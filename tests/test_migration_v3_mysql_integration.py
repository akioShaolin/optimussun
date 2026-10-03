"""Integration checks. They run only against an explicitly enabled test schema."""
import copy
import os
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest

from migration_v3.config import load_mysql_config
from migration_v3.mysql_target import (
    _plan_sha256,
    apply_schema,
    connect,
    inspect_server,
    LOAD_ORDER,
    load_plan,
    switch_default_profile,
    verify_plan,
)


ROOT = Path(__file__).resolve().parents[1]
DDL_PATH = ROOT / "migrations" / "mysql" / "0001_initial.sql"


pytestmark = pytest.mark.skipif(
    os.environ.get("OPTIMUS_RUN_MYSQL_TESTS") != "1",
    reason="Defina OPTIMUS_RUN_MYSQL_TESTS=1 somente para o schema MySQL isolado de ensaio.",
)


@pytest.fixture(scope="module")
def mysql_config():
    return load_mysql_config()


def test_server_is_expected_mysql_8046_and_schema_is_selected(mysql_config):
    observed = inspect_server(mysql_config)
    assert observed["version"].startswith("8.0.46")
    assert "MySQL" in observed["product"]
    assert observed["innodb_page_size"] >= 8192
    assert observed["schema_exists"]


def test_physical_schema_engine_collation_and_tables(mysql_config):
    expected = {
        "manufacturer", "inverter", "mppt", "module", "inverter_ac_profile",
        "inverter_battery", "inverter_system", "inverter_communication",
        "inverter_output_mode", "schema_version", "migration_run",
        "migration_id_map", "migration_pending",
    }
    with connect(mysql_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT DEFAULT_CHARACTER_SET_NAME,DEFAULT_COLLATION_NAME "
                "FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s",
                (mysql_config["database"],),
            )
            schema = cursor.fetchone()
            cursor.execute("SELECT TABLE_NAME, ENGINE, TABLE_COLLATION, ROW_FORMAT FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s",
                           (mysql_config["database"],))
            rows = cursor.fetchall()
    assert schema == ("utf8mb4", "utf8mb4_0900_ai_ci")
    assert {row[0] for row in rows} == expected
    assert all(row[1] == "InnoDB" for row in rows)
    assert all(row[2] == "utf8mb4_0900_ai_ci" for row in rows)
    assert all(row[3].casefold() == "dynamic" for row in rows)


def test_schema_reapplication_is_recognized_without_running_ddl_again(mysql_config):
    result = apply_schema(mysql_config, DDL_PATH)
    assert result["created"] is False
    assert result["already_initialized"] is True
    assert len(result["ddl_sha256"]) == 64
    assert len(result["structure_sha256"]) == 64


def test_normalized_manufacturer_and_conditional_default_constraints(mysql_config):
    with connect(mysql_config) as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO manufacturer (ID,NAME,CATEGORY) VALUES (900000001,' Teste  Único ',2)")
                with pytest.raises(Exception):
                    cursor.execute("INSERT INTO manufacturer (ID,NAME,CATEGORY) VALUES (900000002,'teste único',2)")
                connection.rollback()

                cursor.execute("INSERT INTO manufacturer (ID,NAME,CATEGORY) VALUES (900000001,'Teste Migração',2)")
                cursor.execute("INSERT INTO inverter (ID,MODEL,MANUFACTURER_ID,ACTIVE) VALUES (900000001,'INV TESTE',900000001,1)")
                with pytest.raises(Exception):
                    cursor.execute("INSERT INTO inverter (ID,MODEL,MANUFACTURER_ID,ACTIVE) VALUES (900000002,'  inv   teste ',900000001,1)")
                cursor.execute("INSERT INTO inverter_output_mode (ID,OUTPUT_MODE,ACTIVE) VALUES (900000001,'TEST_MODE',1)")
                base = (900000001, 900000001, "AC_OUTPUT", 900000001, 1000, 1, 1)
                cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,OUTPUT_MODE_ID,RATED_ACTIVE_POWER,ACTIVE,IS_DEFAULT) VALUES (%s,%s,%s,%s,%s,%s,%s)", base)
                cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,OUTPUT_MODE_ID,RATED_ACTIVE_POWER,ACTIVE,IS_DEFAULT) VALUES (900000003,900000001,'AC_OUTPUT',900000001,1000,1,0)")
                cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,OUTPUT_MODE_ID,RATED_ACTIVE_POWER,ACTIVE,IS_DEFAULT) VALUES (900000004,900000001,'AC_OUTPUT',900000001,1000,1,0)")
                with pytest.raises(Exception):
                    cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,OUTPUT_MODE_ID,RATED_ACTIVE_POWER,ACTIVE,IS_DEFAULT) VALUES (900000002,900000001,'AC_OUTPUT',900000001,1000,1,1)")
                connection.rollback()
        finally:
            connection.rollback()


def test_ac_input_database_checks(mysql_config):
    with connect(mysql_config) as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO manufacturer (ID,NAME,CATEGORY) VALUES (900000011,'Teste AC Input',0)")
                cursor.execute("INSERT INTO inverter (ID,MODEL,MANUFACTURER_ID,ACTIVE) VALUES (900000011,'INV AC INPUT',900000011,1)")
                cursor.execute("INSERT INTO inverter_output_mode (ID,OUTPUT_MODE,ACTIVE) VALUES (900000011,'TEST_AC_MODE',1)")
                cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,RATED_CURRENT,ACTIVE,IS_DEFAULT) VALUES (900000011,900000011,'AC_INPUT',1,1,0)")
                with pytest.raises(Exception):
                    cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,ACTIVE,IS_DEFAULT) VALUES (900000012,900000011,'AC_INPUT',1,0)")
                with pytest.raises(Exception):
                    cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,RATED_CURRENT,ACTIVE,IS_DEFAULT) VALUES (900000013,900000011,'AC_INPUT',1,1,1)")
                with pytest.raises(Exception):
                    cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,OUTPUT_MODE_ID,RATED_ACTIVE_POWER,ACTIVE,IS_DEFAULT) VALUES (900000014,900000011,'AC_OUTPUT',900000011,1000,0,1)")
                with pytest.raises(Exception):
                    cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,RATED_CURRENT,ACTIVE,IS_DEFAULT) VALUES (900000015,900000011,'ac_input',1,1,0)")
                connection.rollback()
        finally:
            connection.rollback()


def test_default_switch_rolls_back_on_failure(mysql_config):
    with connect(mysql_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO manufacturer (ID,NAME,CATEGORY) VALUES (900000021,'Teste Troca Padrão',0)")
            cursor.execute("INSERT INTO inverter (ID,MODEL,MANUFACTURER_ID,ACTIVE) VALUES (900000021,'INV TROCA',900000021,1)")
            cursor.execute("INSERT INTO inverter_system (ID,INVERTER_ID,SYSTEM_TYPE) VALUES (900000021,900000021,'ON-GRID')")
            cursor.execute("INSERT INTO inverter_output_mode (ID,OUTPUT_MODE,ACTIVE) VALUES (900000021,'TEST_SWITCH_MODE',1)")
            cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,OUTPUT_MODE_ID,RATED_ACTIVE_POWER,ACTIVE,IS_DEFAULT) VALUES (900000021,900000021,'AC_OUTPUT',900000021,1000,1,1)")
            cursor.execute("INSERT INTO inverter_ac_profile (ID,INVERTER_ID,PROFILE_TYPE,OUTPUT_MODE_ID,RATED_ACTIVE_POWER,ACTIVE,IS_DEFAULT) VALUES (900000022,900000021,'AC_OUTPUT',900000021,1000,1,0)")
        connection.commit()
    try:
        with pytest.raises(RuntimeError, match="Falha injetada"):
            switch_default_profile(mysql_config, 900000021, 900000022, 1, inject_failure=True)
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT ID FROM inverter_ac_profile WHERE INVERTER_ID=900000021 AND IS_DEFAULT=1")
                assert cursor.fetchone()[0] == 900000021
    finally:
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM inverter WHERE ID=900000021")
                cursor.execute("DELETE FROM inverter_output_mode WHERE ID=900000021")
                cursor.execute("DELETE FROM manufacturer WHERE ID=900000021")
            connection.commit()


def test_concurrent_default_attempts_leave_only_one_default(mysql_config):
    fixture_id = random.randint(700_000_000, 799_000_000)
    with connect(mysql_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO manufacturer (ID,NAME,CATEGORY) VALUES (%s,%s,0)",
                           (fixture_id, f"Teste Concorrência {fixture_id}"))
            cursor.execute("INSERT INTO inverter (ID,MODEL,MANUFACTURER_ID,ACTIVE) VALUES (%s,%s,%s,1)",
                           (fixture_id, f"INV CONCORRENTE {fixture_id}", fixture_id))
            cursor.execute("INSERT INTO inverter_output_mode (ID,OUTPUT_MODE,ACTIVE) VALUES (%s,%s,1)",
                           (fixture_id, f"TEST_CONCURRENT_{fixture_id}"))
        connection.commit()
    barrier = Barrier(2)

    def attempt(offset):
        connection = connect(mysql_config)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET SESSION innodb_lock_wait_timeout=5")
                barrier.wait(timeout=5)
                cursor.execute(
                    "INSERT INTO inverter_ac_profile "
                    "(ID,INVERTER_ID,PROFILE_TYPE,OUTPUT_MODE_ID,RATED_ACTIVE_POWER,ACTIVE,IS_DEFAULT) "
                    "VALUES (%s,%s,'AC_OUTPUT',%s,1000,1,1)",
                    (fixture_id + offset, fixture_id, fixture_id),
                )
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            return False
        finally:
            connection.close()

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, (1, 2)))
        assert sorted(results) == [False, True]
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM inverter_ac_profile WHERE INVERTER_ID=%s AND IS_DEFAULT=1",
                               (fixture_id,))
                assert cursor.fetchone()[0] == 1
    finally:
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM inverter WHERE ID=%s", (fixture_id,))
                cursor.execute("DELETE FROM inverter_output_mode WHERE ID=%s", (fixture_id,))
                cursor.execute("DELETE FROM manufacturer WHERE ID=%s", (fixture_id,))
            connection.commit()


def test_concurrent_default_switches_use_optimistic_row_version(mysql_config):
    fixture_id = random.randint(800_000_000, 849_000_000)
    with connect(mysql_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO manufacturer (ID,NAME,CATEGORY) VALUES (%s,%s,0)",
                           (fixture_id, f"Teste Switch Concorrente {fixture_id}"))
            cursor.execute("INSERT INTO inverter (ID,MODEL,MANUFACTURER_ID,ACTIVE) VALUES (%s,%s,%s,1)",
                           (fixture_id, f"INV SWITCH {fixture_id}", fixture_id))
            cursor.execute("INSERT INTO inverter_system (ID,INVERTER_ID,SYSTEM_TYPE) VALUES (%s,%s,'ON-GRID')",
                           (fixture_id, fixture_id))
            cursor.execute("INSERT INTO inverter_output_mode (ID,OUTPUT_MODE,ACTIVE) VALUES (%s,%s,1)",
                           (fixture_id, f"TEST_SWITCH_CONCURRENT_{fixture_id}"))
            for offset, is_default in ((1, 1), (2, 0), (3, 0)):
                cursor.execute(
                    "INSERT INTO inverter_ac_profile "
                    "(ID,INVERTER_ID,PROFILE_TYPE,OUTPUT_MODE_ID,RATED_ACTIVE_POWER,ACTIVE,IS_DEFAULT) "
                    "VALUES (%s,%s,'AC_OUTPUT',%s,1000,1,%s)",
                    (fixture_id + offset, fixture_id, fixture_id, is_default),
                )
        connection.commit()
    barrier = Barrier(2)

    def attempt(profile_id):
        barrier.wait(timeout=5)
        try:
            switch_default_profile(mysql_config, fixture_id, profile_id, 1)
            return True
        except RuntimeError:
            return False

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, (fixture_id + 2, fixture_id + 3)))
        assert sorted(results) == [False, True]
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT ROW_VERSION FROM inverter WHERE ID=%s", (fixture_id,))
                assert cursor.fetchone()[0] == 2
                cursor.execute("SELECT COUNT(*) FROM inverter_ac_profile WHERE INVERTER_ID=%s AND IS_DEFAULT=1",
                               (fixture_id,))
                assert cursor.fetchone()[0] == 1
    finally:
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM inverter WHERE ID=%s", (fixture_id,))
                cursor.execute("DELETE FROM inverter_output_mode WHERE ID=%s", (fixture_id,))
                cursor.execute("DELETE FROM manufacturer WHERE ID=%s", (fixture_id,))
            connection.commit()


def _require_empty_catalog(mysql_config):
    with connect(mysql_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM migration_run WHERE STATUS='COMPLETED'")
            completed = cursor.fetchone()[0]
            domain_rows = 0
            for table in LOAD_ORDER:
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                domain_rows += cursor.fetchone()[0]
    if completed or domain_rows:
        pytest.skip("Teste de carga exige schema de ensaio recém-inicializado e vazio.")


def _minimal_plan(fixture_id, *, duplicate_manufacturer=False):
    source_hash = f"{fixture_id:064x}"[-64:]
    snapshot_hash = f"{fixture_id + 1:064x}"[-64:]
    manufacturers = [{"ID": fixture_id, "NAME": f"Teste Carga {fixture_id}", "CATEGORY": 0}]
    if duplicate_manufacturer:
        manufacturers.append({"ID": fixture_id + 1,
                              "NAME": f"  teste   carga {fixture_id}  ", "CATEGORY": 0})
    tables = {
        "manufacturer": manufacturers,
        "inverter": [],
        "module": [], "mppt": [], "inverter_output_mode": [],
        "inverter_ac_profile": [], "inverter_battery": [],
        "inverter_system": [], "inverter_communication": [],
    }
    counts = {name: len(rows) for name, rows in tables.items()}
    counts.update({"ready_profiles": 0, "pending": 0, "errors": 0})
    plan = {
        "format_version": 1, "mapping_version": "0001",
        "source": {"source_id": f"pytest-{fixture_id}", "source_sha256": source_hash,
                   "snapshot_sha256": snapshot_hash},
        "decisions_sha256": "d" * 64, "counts": counts,
        "tables": tables, "mappings": [], "issues": [],
    }
    plan["plan_sha256"] = _plan_sha256(plan)
    return plan


def test_initial_load_refuses_preexisting_domain_rows(mysql_config):
    _require_empty_catalog(mysql_config)
    fixture_id = random.randint(550_000_000, 599_000_000)
    plan = _minimal_plan(fixture_id + 1)
    with connect(mysql_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO manufacturer (ID,NAME,CATEGORY) VALUES (%s,%s,0)",
                           (fixture_id, f"Linha preexistente {fixture_id}"))
        connection.commit()
    try:
        with pytest.raises(RuntimeError, match="não está vazio"):
            load_plan(mysql_config, plan)
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM migration_run WHERE SOURCE_ID=%s",
                               (f"pytest-{fixture_id + 1}",))
                assert cursor.fetchone()[0] == 0
    finally:
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM manufacturer WHERE ID=%s", (fixture_id,))
            connection.commit()


def test_load_verify_and_identical_rerun_are_idempotent(mysql_config):
    _require_empty_catalog(mysql_config)
    fixture_id = random.randint(600_000_000, 649_000_000)
    plan = _minimal_plan(fixture_id)
    try:
        first = load_plan(mysql_config, plan)
        assert first["status"] == "COMPLETED"
        assert verify_plan(mysql_config, plan)["matches"]
        second = load_plan(mysql_config, plan)
        assert second["status"] == "ALREADY_COMPLETED"
        assert second["migration_run_id"] == first["migration_run_id"]
        assert second["plan_sha256"] == first["plan_sha256"]

        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE manufacturer SET NAME=%s WHERE ID=%s",
                               (f"Conteúdo alterado {fixture_id}", fixture_id))
            connection.commit()
        with pytest.raises(RuntimeError, match="ALREADY_COMPLETED recusado"):
            load_plan(mysql_config, plan)
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE manufacturer SET NAME=%s WHERE ID=%s",
                               (f"Teste Carga {fixture_id}", fixture_id))
            connection.commit()
        assert verify_plan(mysql_config, plan)["matches"]

        changed_decisions = copy.deepcopy(plan)
        changed_decisions["decisions_sha256"] = "e" * 64
        changed_decisions["plan_sha256"] = _plan_sha256(changed_decisions)
        with pytest.raises(RuntimeError, match="snapshot ou decisões diferentes"):
            load_plan(mysql_config, changed_decisions)
    finally:
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM manufacturer WHERE ID=%s", (fixture_id,))
                cursor.execute("DELETE FROM migration_run WHERE SOURCE_ID=%s", (f"pytest-{fixture_id}",))
            connection.commit()


def test_load_failure_rolls_back_domain_rows_and_run(mysql_config):
    _require_empty_catalog(mysql_config)
    fixture_id = random.randint(650_000_000, 699_000_000)
    plan = _minimal_plan(fixture_id)
    plan["tables"]["manufacturer"].append(
        {"ID": fixture_id + 1, "NAME": f"Segundo Fabricante {fixture_id}", "CATEGORY": 1}
    )
    plan["counts"]["manufacturer"] = 2
    plan["plan_sha256"] = _plan_sha256(plan)
    try:
        with pytest.raises(RuntimeError, match="Falha injetada"):
            load_plan(mysql_config, plan, inject_failure_after_table="manufacturer")

        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM manufacturer WHERE ID=%s", (fixture_id,))
                assert cursor.fetchone()[0] == 0
                cursor.execute("SELECT COUNT(*) FROM manufacturer WHERE ID=%s", (fixture_id + 1,))
                assert cursor.fetchone()[0] == 0
                cursor.execute("SELECT COUNT(*) FROM migration_run WHERE SOURCE_ID=%s",
                               (f"pytest-{fixture_id}",))
                assert cursor.fetchone()[0] == 0

        recovered = load_plan(mysql_config, plan)
        assert recovered["status"] == "COMPLETED"
        assert verify_plan(mysql_config, plan)["matches"]
    finally:
        with connect(mysql_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM manufacturer WHERE ID IN (%s,%s)",
                               (fixture_id, fixture_id + 1))
                cursor.execute("DELETE FROM migration_run WHERE SOURCE_ID=%s",
                               (f"pytest-{fixture_id}",))
            connection.commit()
