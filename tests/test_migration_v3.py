import copy
import json
from pathlib import Path

import pytest

import migration_v3.mysql_target as mysql_target
from migration_v3.mysql_target import (
    _canonical_structure_sha256,
    _plan_sha256,
    _validate_plan,
    connect,
    split_sql,
    validate_server_observation,
    validate_test_schema,
)
from migration_v3.domain import (
    DomainValidationError,
    validate_ac_input,
    validate_battery_groups,
    validate_output_profile,
)
from migration_v3.normalization import collapse_spaces, normalized_key
from migration_v3.reconciliation import load_reconciliation
from migration_v3.transform import UINT64_MAX, build_plan, decode_group


def inverter(identifier, model=None):
    return {
        "ID": identifier, "MODEL": model or f"INV-{identifier}", "MANUFACTURER_ID": 1,
        "DIM_WIDTH": 1, "DIM_HEIGHT": 2, "DIM_DEPTH": 3, "DIM_WEIGHT": 4,
        "MAX_OPERATING_TEMPERATURE": 60, "MIN_OPERATING_TEMPERATURE": -25,
        "COOLING_MODE": "Natural", "PROTECTION_DEGREE": "IP65", "TOPOLOGY": "Sem transformador",
        "RATED_ACTIVE_POWER": 10000, "MAX_ACTIVE_POWER": 11000,
        "RATED_OUTPUT_VOLTAGE": 380, "RATED_OUTPUT_CURRENT": 15.2,
        "MAX_OUTPUT_CURRENT": 16.4, "OVERLOAD": 50,
        "NUMBER_OF_TRACKERS": 1, "NUMBER_OF_INPUTS": 2, "ACTIVE": 1,
    }


def source_for(inverters, modes):
    modules = [{
        "ID": 1, "MODEL": "MOD-1", "MANUFACTURER_ID": 1,
        "DIM_WIDTH": 1, "DIM_HEIGHT": 2, "DIM_DEPTH": 3, "DIM_WEIGHT": 4,
        "WP": 600, "VMPP": 40.1, "IMPP": 14.96, "VOC": 48.2, "ISC": 15.6,
        "SOLAR_CELLS": "MONOCRISTALINO", "CELL_TYPE": "HALF CELL", "SURFACE_TYPE": "BIFACIAL",
        "COEF_PMAX": -0.3528, "COEF_VOC": -0.2769, "COEF_ISC": 0.03528, "ACTIVE": 1,
    }]
    return {
        "integrity": "ok", "foreign_key_issues": [],
        "tables": {
            "manufacturer": [{"ID": 1, "NAME": " WEG ", "CATEGORY": 2}],
            "inverter": inverters,
            "module": modules,
            "mppt": [{
                "ID": n, "INVERTER_ID": item["ID"], "MPPT_INDEX": 0, "NUMBER_OF_INPUTS": 2,
                "MAX_INPUT_VOLTAGE": 1000, "MIN_STARTUP_VOLTAGE": 100,
                "MAX_OPERATING_VOLTAGE": 900, "MIN_OPERATING_VOLTAGE": 120,
                "MAX_FULL_LOAD_VOLTAGE": -1, "MIN_FULL_LOAD_VOLTAGE": -1,
                "RATED_INPUT_VOLTAGE": -1, "MAX_SHORT_CIRCUIT_CURRENT": 30,
                "MAX_OPERATING_CURRENT": 25,
            } for n, item in enumerate(inverters, 1)],
            "inverter_system": [{"ID": n, "INVERTER_ID": item["ID"], "SYSTEM_TYPE": "ON-GRID"}
                                for n, item in enumerate(inverters, 1)],
            "inverter_communication": [],
            "inverter_output_mode": [
                {"ID": n, "INVERTER_ID": inverter_id, "OUTPUT_MODE": mode}
                for n, (inverter_id, mode) in enumerate(modes, 1)
            ],
        },
    }


def build(source, decisions=None):
    return build_plan(source, {
        "source_id": "fixture-source",
        "source_path": "fixture.db", "source_sha256": "a" * 64,
        "snapshot_path": "fixture.snapshot.db", "snapshot_sha256": "b" * 64,
    }, decisions or {}, "c" * 64)


def test_normalization_contract():
    assert collapse_spaces("  WEG   Energia ") == "WEG Energia"
    assert normalized_key(" Árvore  SOLAR ") == normalized_key("arvore solar")


def test_one_mode_creates_ready_default_and_preserves_unclassified_voltage():
    plan = build(source_for([inverter(1)], [(1, "SINGLE_PHASE")]))
    profile = plan["tables"]["inverter_ac_profile"][0]
    assert profile["ACTIVE"] == 1
    assert profile["IS_DEFAULT"] == 1
    assert profile["RATED_LINE_TO_LINE_VOLTAGE"] is None
    assert profile["RATED_LINE_TO_NEUTRAL_VOLTAGE"] is None
    assert any(item["reason_code"] == "VOLTAGE_REFERENCE_UNRESOLVED" for item in plan["issues"])
    mppt = plan["tables"]["mppt"][0]
    assert mppt["MAX_FULL_LOAD_VOLTAGE"] is None
    assert plan["tables"]["module"][0]["COEF_ISC"] == "0.03528"
    assert plan["counts"]["ready_profiles"] == 1


def test_56_pairs_create_112_inactive_nondefault_profiles():
    inverters = [inverter(identifier) for identifier in range(1, 57)]
    modes = [(item["ID"], mode) for item in inverters
             for mode in ("THREE_PHASE_THREE_WIRE", "THREE_PHASE_FOUR_WIRE")]
    plan = build(source_for(inverters, modes))
    profiles = plan["tables"]["inverter_ac_profile"]
    assert len(profiles) == 112
    assert not any(row["ACTIVE"] or row["IS_DEFAULT"] for row in profiles)
    assert sum(item["reason_code"] == "MULTIMODE_PROFILE_REVIEW_REQUIRED"
               for item in plan["issues"]) == 112


def test_multimode_voltage_only_decision_does_not_clear_review_pending():
    source = source_for([inverter(1)], [(1, "THREE_PHASE_THREE_WIRE"),
                                       (1, "THREE_PHASE_FOUR_WIRE")])
    decisions = {(1, "THREE_PHASE_FOUR_WIRE"): {
        "inverter_id": 1, "output_mode": "THREE_PHASE_FOUR_WIRE",
        "voltage_reference": "LINE_TO_LINE", "source": "fixture", "corrections": {},
    }}

    plan = build(source, decisions)

    pending = [issue for issue in plan["issues"]
               if issue["reason_code"] == "MULTIMODE_PROFILE_REVIEW_REQUIRED"]
    assert len(pending) == 2


def test_fully_reviewed_multimode_requires_exactly_one_default():
    source = source_for([inverter(1)], [(1, "THREE_PHASE_THREE_WIRE"),
                                       (1, "THREE_PHASE_FOUR_WIRE")])
    decisions = {
        (1, mode): {"inverter_id": 1, "output_mode": mode, "active": True,
                    "is_default": False, "source": "fixture", "corrections": {}}
        for mode in ("THREE_PHASE_THREE_WIRE", "THREE_PHASE_FOUR_WIRE")
    }

    plan = build(source, decisions)

    assert any(issue["reason_code"] == "MISSING_DEFAULT_PROFILE" for issue in plan["issues"])


def test_reconciliation_can_classify_voltage_and_choose_only_one_default(tmp_path):
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps({"version": 1, "profiles": [{
        "inverter_id": 1, "output_mode": "THREE_PHASE_FOUR_WIRE",
        "active": True, "is_default": True, "voltage_reference": "LINE_TO_LINE",
        "source": "datasheet confirmed", "corrections": {},
    }]}), encoding="utf-8")
    decisions, digest, _ = load_reconciliation(path)
    source = source_for([inverter(1)], [(1, "THREE_PHASE_THREE_WIRE"),
                                       (1, "THREE_PHASE_FOUR_WIRE")])
    plan = build_plan(source, {"source_id": "fixture-source",
                               "source_path": "fixture.db", "source_sha256": "a" * 64,
                               "snapshot_path": "fixture.snapshot.db", "snapshot_sha256": "b" * 64},
                      decisions, digest)
    selected = next(row for row in plan["tables"]["inverter_ac_profile"]
                    if row["OUTPUT_MODE_ID"] == 1)
    assert selected["IS_DEFAULT"] == 1
    assert selected["RATED_LINE_TO_LINE_VOLTAGE"] == "380"
    assert selected["RATED_LINE_TO_NEUTRAL_VOLTAGE"] is None


def test_confirmed_power_correction_makes_single_mode_profile_ready():
    item = inverter(1)
    item["RATED_ACTIVE_POWER"] = None
    decisions = {(1, "SINGLE_PHASE"): {
        "inverter_id": 1, "output_mode": "SINGLE_PHASE", "source": "fixture",
        "corrections": {"RATED_ACTIVE_POWER": "10000"},
    }}

    plan = build(source_for([item], [(1, "SINGLE_PHASE")]), decisions)

    profile = plan["tables"]["inverter_ac_profile"][0]
    assert profile["RATED_ACTIVE_POWER"] == "10000"
    assert profile["ACTIVE"] == 1
    assert profile["IS_DEFAULT"] == 1
    assert not any(issue["reason_code"] == "MISSING_NOMINAL_OUTPUT_POWER"
                   for issue in plan["issues"])


def test_reconciliation_rejects_promoted_profile_without_source(tmp_path):
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps({"version": 1, "profiles": [{
        "inverter_id": 1, "output_mode": "SINGLE_PHASE", "active": True,
    }]}), encoding="utf-8")
    with pytest.raises(ValueError, match="source"):
        load_reconciliation(path)


@pytest.mark.parametrize("correction", [-1, "NaN", "Infinity", None])
def test_reconciliation_rejects_invalid_correction_without_echoing_value(tmp_path, correction):
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps({"version": 1, "profiles": [{
        "inverter_id": 1, "output_mode": "SINGLE_PHASE", "source": "fixture",
        "corrections": {"RATED_ACTIVE_POWER": correction},
    }]}), encoding="utf-8")

    with pytest.raises(ValueError) as caught:
        load_reconciliation(path)

    assert "RATED_ACTIVE_POWER" in str(caught.value)
    assert str(correction) not in str(caught.value)


@pytest.mark.parametrize("field,value", [("inverter_id", "1"), ("active", "true"),
                                           ("is_default", 1)])
def test_reconciliation_rejects_wrong_scalar_types(tmp_path, field, value):
    decision = {"inverter_id": 1, "output_mode": "SINGLE_PHASE", "source": "fixture"}
    decision[field] = value
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps({"version": 1, "profiles": [decision]}), encoding="utf-8")

    with pytest.raises(ValueError, match=field):
        load_reconciliation(path)


@pytest.mark.parametrize("bad_document", [
    {"version": True, "profiles": []},
    {"version": 1, "profiles": [{"inverter_id": 1, "output_mode": "SINGLE_PHASE",
                                   "source": "fixture", "voltage_reference": []}]},
    {"version": 1, "profiles": [{"inverter_id": 1, "output_mode": "SINGLE_PHASE",
                                   "source": "fixture", "active": False,
                                   "is_default": True}]},
])
def test_reconciliation_rejects_ambiguous_or_contradictory_values(tmp_path, bad_document):
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps(bad_document), encoding="utf-8")

    with pytest.raises(ValueError):
        load_reconciliation(path)


def test_reconciliation_hash_is_independent_of_profile_list_order(tmp_path):
    profiles = [
        {"inverter_id": 2, "output_mode": "MODE_B", "source": "fixture",
         "active": False, "is_default": False},
        {"inverter_id": 1, "output_mode": "MODE_A", "source": "fixture",
         "active": True, "is_default": True},
    ]
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"
    first_path.write_text(json.dumps({"version": 1, "profiles": profiles}), encoding="utf-8")
    second_path.write_text(json.dumps({"version": 1, "profiles": list(reversed(profiles))}),
                           encoding="utf-8")

    first_index, first_hash, _ = load_reconciliation(first_path)
    second_index, second_hash, _ = load_reconciliation(second_path)

    assert first_index == second_index
    assert first_hash == second_hash


def test_group_decoder_rejects_repetition_missing_position_and_overflow():
    assert decode_group(0, 3) == {1, 2, 3}
    assert decode_group(15, 3) == {2, 3}
    with pytest.raises(ValueError):
        decode_group(4, 3)
    with pytest.raises(ValueError):
        decode_group(5, 2)
    with pytest.raises(ValueError):
        decode_group(UINT64_MAX + 1, 64)


def test_mysql_schema_has_conditional_default_and_no_generic_voltage():
    ddl = (Path(__file__).parents[1] / "migrations" / "mysql" / "0001_initial.sql").read_text(encoding="utf-8")
    assert "CASE WHEN IS_DEFAULT = TRUE THEN 1 ELSE NULL END" in ddl
    assert "UNIQUE KEY uq_ac_profile_one_default (INVERTER_ID, DEFAULT_SLOT)" in ddl
    assert "RATED_LINE_TO_LINE_VOLTAGE" in ddl
    assert "RATED_LINE_TO_NEUTRAL_VOLTAGE" in ddl
    assert " RATED_VOLTAGE " not in ddl
    assert "CONSTRAINT chk_ac_profile_booleans" in ddl
    assert "PLAN_SHA256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL" in ddl
    assert "STRUCTURE_SHA256 CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL" in ddl
    assert "SNAPSHOT_SHA256, MAPPING_VERSION" in ddl
    assert ddl.count("ROW_FORMAT=DYNAMIC") == 13
    assert len(split_sql(ddl)) >= 13


def test_only_explicit_test_schema_names_are_accepted():
    validate_test_schema("optimus_sun_v3_ensaio")
    validate_test_schema("catalog_test")
    for unsafe in ("optimus_sun", "mysql", "", "test;drop"):
        with pytest.raises(ValueError):
            validate_test_schema(unsafe)


def test_connect_rejects_unsafe_schema_before_loading_driver():
    with pytest.raises(ValueError, match="_ensaio ou _test"):
        connect({"database": "optimus_sun_producao"})


def test_connection_failure_never_echoes_fictitious_credentials(monkeypatch):
    secret = "fictitious-do-not-echo"

    class FailingDriver:
        @staticmethod
        def connect(**kwargs):
            assert kwargs["password"] == secret
            raise Exception(f"driver included {secret}")

    monkeypatch.setattr(mysql_target, "_driver", lambda: FailingDriver)
    config = {"host": "127.0.0.1", "port": 3306, "database": "catalog_test",
              "user": "fake-user", "password": secret, "ssl_ca": None}

    with pytest.raises(RuntimeError) as caught:
        connect(config)

    assert secret not in str(caught.value)
    assert "fake-user" not in str(caught.value)


def test_server_preflight_requires_mysql_8046_and_strict_mode():
    valid = {"version": "8.0.46", "product": "MySQL Community Server - GPL",
             "sql_mode": "STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION",
             "innodb_page_size": 16384, "innodb_default_row_format": "dynamic"}
    assert validate_server_observation(valid)

    for field, value in (("version", "8.0.45"), ("product", "MariaDB Server"),
                         ("sql_mode", "NO_ENGINE_SUBSTITUTION"),
                         ("innodb_page_size", 4096)):
        invalid = dict(valid)
        invalid[field] = value
        with pytest.raises(RuntimeError):
            validate_server_observation(invalid)


def test_ac_input_minimum_and_hybrid_eligibility():
    profile = {"PROFILE_TYPE": "AC_INPUT", "ACTIVE": 1, "IS_DEFAULT": 0,
               "OUTPUT_MODE_ID": None, "RATED_CURRENT": "1.00"}
    assert validate_ac_input(profile, {"HYBRID", "ON-GRID"})
    assert validate_ac_input(profile, {" hybrid "})
    with pytest.raises(DomainValidationError, match="HYBRID"):
        validate_ac_input(profile, {"ON-GRID"})
    profile["RATED_CURRENT"] = 0
    with pytest.raises(DomainValidationError, match="grandeza nominal positiva"):
        validate_ac_input(profile, {"HYBRID"})


def test_output_profile_and_battery_group_domain_rules():
    output = {"PROFILE_TYPE": "AC_OUTPUT", "ACTIVE": 1, "IS_DEFAULT": 0,
              "OUTPUT_MODE_ID": 1, "RATED_ACTIVE_POWER": "1000.00"}
    assert validate_output_profile(output, {"ON-GRID"})
    assert validate_output_profile(output, {" on-grid "})
    with pytest.raises(DomainValidationError, match="classifica"):
        validate_output_profile(output, set())
    eps = dict(output, PROFILE_TYPE="EPS_OUTPUT")
    with pytest.raises(DomainValidationError, match="OFF-GRID"):
        validate_output_profile(eps, {"ON-GRID"})

    homogeneous = {"ID": 1, "BATTERY_INDEX": 0, "ACTIVE": 1}
    overlapping = {"ID": 2, "BATTERY_INDEX": 2, "ACTIVE": 1}
    with pytest.raises(DomainValidationError, match="sobrep"):
        validate_battery_groups([homogeneous, overlapping], 2)
    overlapping["ACTIVE"] = 0
    assert validate_battery_groups([homogeneous, overlapping], 2)


def test_same_input_builds_identical_plan():
    source = source_for([inverter(1)], [(1, "SINGLE_PHASE")])
    first = build(source)
    second = build(source)
    assert first == second
    assert _plan_sha256(first) == _plan_sha256(second)


def test_plan_preflight_rejects_tampered_counts_columns_and_profile_content():
    plan = build(source_for([inverter(1)], [(1, "SINGLE_PHASE")]))
    assert _validate_plan(plan)

    bad_counts = copy.deepcopy(plan)
    bad_counts["counts"]["errors"] = 0 if plan["counts"]["errors"] else 1
    with pytest.raises(ValueError, match="Contagens"):
        _validate_plan(bad_counts)

    bad_columns = copy.deepcopy(plan)
    bad_columns["tables"]["manufacturer"][0]["UNSAFE_COLUMN"] = "x"
    with pytest.raises(ValueError, match="colunas inválidas"):
        _validate_plan(bad_columns)

    bad_profile = copy.deepcopy(plan)
    bad_profile["tables"]["inverter_ac_profile"][0]["RATED_ACTIVE_POWER"] = None
    with pytest.raises(ValueError, match="perfil de saída ativo inválido"):
        _validate_plan(bad_profile)

    bad_scale = copy.deepcopy(plan)
    bad_scale["tables"]["inverter_ac_profile"][0]["RATED_ACTIVE_POWER"] = "0.001"
    with pytest.raises(ValueError, match="decimal fora da precisão"):
        _validate_plan(bad_scale)

    bad_classification = copy.deepcopy(plan)
    bad_classification["tables"]["inverter_ac_profile"][0]["PROFILE_TYPE"] = "EPS_OUTPUT"
    with pytest.raises(ValueError, match="perfil de saída ativo inválido"):
        _validate_plan(bad_classification)

    removed_pending = copy.deepcopy(plan)
    pending_index = next(index for index, issue in enumerate(removed_pending["issues"])
                         if issue["severity"] == "PENDING")
    removed_pending["issues"].pop(pending_index)
    removed_pending["counts"]["pending"] -= 1
    with pytest.raises(ValueError, match="Checksum"):
        _validate_plan(removed_pending)


def test_active_output_without_system_is_reported_and_plan_remains_auditable():
    source = source_for([inverter(1)], [(1, "SINGLE_PHASE")])
    source["tables"]["inverter_system"] = []

    plan = build(source)

    assert plan["counts"]["errors"] == 1
    assert plan["counts"]["ready_profiles"] == 0
    assert any(issue["reason_code"] == "ACTIVE_OUTPUT_MISSING_SYSTEM_CLASSIFICATION"
               for issue in plan["issues"])
    assert _validate_plan(plan)


def test_structure_fingerprint_changes_when_physical_metadata_changes():
    original = [("columns", [("inverter", 1, "ID", "int unsigned")])]
    changed = [("columns", [("inverter", 1, "ID", "bigint unsigned")])]

    assert _canonical_structure_sha256(original) == _canonical_structure_sha256(original)
    assert _canonical_structure_sha256(original) != _canonical_structure_sha256(changed)


def test_normalized_equipment_collision_is_reported_before_load():
    first = inverter(1, "INV DUPLICADO")
    second = inverter(2, "  inv   duplicado ")
    plan = build(source_for([first, second], [(1, "SINGLE_PHASE"), (2, "SINGLE_PHASE")]))

    assert any(issue["reason_code"] == "NORMALIZED_MODEL_COLLISION"
               for issue in plan["issues"])
    assert plan["counts"]["errors"] >= 1
    assert _validate_plan(plan)


def test_invalid_mppt_input_count_is_reported_and_plan_remains_auditable():
    source = source_for([inverter(1)], [(1, "SINGLE_PHASE")])
    source["tables"]["mppt"][0]["NUMBER_OF_INPUTS"] = "invalid"

    plan = build(source)

    assert any(issue["reason_code"] == "INVALID_INPUT_COUNT"
               for issue in plan["issues"])
    assert _validate_plan(plan)


def test_invalid_mppt_group_index_is_reported_without_aborting_simulation():
    source = source_for([inverter(1)], [(1, "SINGLE_PHASE")])
    source["tables"]["mppt"][0]["MPPT_INDEX"] = "invalid"

    plan = build(source)

    assert any(issue["reason_code"] == "INVALID_GROUP_INDEX"
               for issue in plan["issues"])
    assert _validate_plan(plan)


def test_overlapping_mppt_groups_are_reported_before_load():
    item = inverter(1)
    item["NUMBER_OF_TRACKERS"] = 2
    item["NUMBER_OF_INPUTS"] = 3
    source = source_for([item], [(1, "SINGLE_PHASE")])
    base = source["tables"]["mppt"][0]
    source["tables"]["mppt"] = [dict(base, ID=1, MPPT_INDEX=0, NUMBER_OF_INPUTS=1),
                                     dict(base, ID=2, MPPT_INDEX=2, NUMBER_OF_INPUTS=1)]

    plan = build(source)

    assert any(issue["reason_code"] == "OVERLAPPING_GROUPS" for issue in plan["issues"])

    tampered = copy.deepcopy(plan)
    tampered["issues"] = [issue for issue in tampered["issues"] if issue["severity"] != "ERROR"]
    tampered["counts"]["errors"] = 0
    with pytest.raises(ValueError, match="omite inconsistência estrutural de MPPT"):
        _validate_plan(tampered)


@pytest.mark.parametrize("wp", ["1.001", "10000000000"])
def test_decimal_values_that_would_round_or_overflow_are_reported(wp):
    source = source_for([inverter(1)], [(1, "SINGLE_PHASE")])
    source["tables"]["module"][0]["WP"] = wp

    plan = build(source)

    assert plan["tables"]["module"][0]["WP"] is None
    assert plan["counts"]["errors"] == 1
    assert any(issue["reason_code"] == "INVALID_DECIMAL" and issue["field"] == "WP"
               for issue in plan["issues"])


def test_explicit_active_profile_without_nominal_power_blocks_load_plan():
    item = inverter(1)
    item["RATED_ACTIVE_POWER"] = None
    decisions = {(1, "SINGLE_PHASE"): {
        "inverter_id": 1, "output_mode": "SINGLE_PHASE", "source": "fixture",
        "active": True, "is_default": True, "corrections": {},
    }}

    plan = build(source_for([item], [(1, "SINGLE_PHASE")]), decisions)

    assert plan["counts"]["errors"] == 1
    assert any(issue["reason_code"] == "ACTIVE_PROFILE_MISSING_NOMINAL_OUTPUT_POWER"
               for issue in plan["issues"])

