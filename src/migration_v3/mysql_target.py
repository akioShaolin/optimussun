import hashlib
import json
import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from functools import wraps
from pathlib import Path

from . import MAPPING_VERSION, SCHEMA_VERSION
from .domain import (
    DomainValidationError,
    decode_group,
    output_profile_is_ready,
    validate_ac_input,
    validate_battery_groups,
    validate_output_profile,
)
from .integrity import plan_sha256 as _plan_sha256
from .normalization import normalized_key


SAFE_TEST_SCHEMA = re.compile(r"^[A-Za-z0-9_]*(?:_ensaio|_test)$", re.IGNORECASE)
LOAD_ORDER = (
    "manufacturer", "inverter", "module", "mppt", "inverter_output_mode",
    "inverter_ac_profile", "inverter_battery", "inverter_system", "inverter_communication",
)
EXPECTED_TABLES = frozenset((*LOAD_ORDER, "schema_version", "migration_run",
                             "migration_id_map", "migration_pending"))
OFFICIAL_DDL_PATH = Path(__file__).resolve().parents[2] / "migrations" / "mysql" / "0001_initial.sql"
TABLE_COLUMNS = {
    "manufacturer": ("ID", "NAME", "CATEGORY"),
    "inverter": (
        "ID", "MODEL", "MANUFACTURER_ID", "DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH",
        "DIM_WEIGHT", "MAX_OPERATING_TEMPERATURE", "MIN_OPERATING_TEMPERATURE",
        "COOLING_MODE", "PROTECTION_DEGREE", "TOPOLOGY", "OVERLOAD",
        "NUMBER_OF_TRACKERS", "NUMBER_OF_INPUTS", "ACTIVE",
        "NUMBER_OF_BATTERY_INPUTS", "MAX_EFFICIENCY", "EURO_EFFICIENCY", "ROW_VERSION",
    ),
    "module": (
        "ID", "MODEL", "MANUFACTURER_ID", "DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH",
        "DIM_WEIGHT", "WP", "VMPP", "IMPP", "VOC", "ISC", "SOLAR_CELLS", "CELL_TYPE",
        "SURFACE_TYPE", "COEF_PMAX", "COEF_VOC", "COEF_ISC", "ACTIVE", "ROW_VERSION",
    ),
    "mppt": (
        "ID", "INVERTER_ID", "MPPT_INDEX", "NUMBER_OF_INPUTS", "MAX_INPUT_VOLTAGE",
        "MIN_STARTUP_VOLTAGE", "MAX_OPERATING_VOLTAGE", "MIN_OPERATING_VOLTAGE",
        "MAX_FULL_LOAD_VOLTAGE", "MIN_FULL_LOAD_VOLTAGE", "RATED_INPUT_VOLTAGE",
        "MAX_SHORT_CIRCUIT_CURRENT_PER_MPPT", "MAX_SHORT_CIRCUIT_CURRENT_PER_STRING",
        "MAX_OPERATING_CURRENT_PER_MPPT", "MAX_OPERATING_CURRENT_PER_STRING",
    ),
    "inverter_output_mode": ("ID", "OUTPUT_MODE", "ACTIVE"),
    "inverter_ac_profile": (
        "ID", "INVERTER_ID", "PROFILE_TYPE", "OUTPUT_MODE_ID", "RATED_ACTIVE_POWER",
        "MAX_ACTIVE_POWER", "MAX_PEAK_ACTIVE_POWER", "RATED_LINE_TO_LINE_VOLTAGE",
        "RATED_LINE_TO_NEUTRAL_VOLTAGE", "RATED_CURRENT", "MAX_CURRENT", "SWITCHING_TIME",
        "ACTIVE", "IS_DEFAULT", "ROW_VERSION",
    ),
    "inverter_battery": (
        "ID", "INVERTER_ID", "BATTERY_INDEX", "BATTERY_TYPE", "BATTERY_VOLTAGE_MIN",
        "BATTERY_VOLTAGE_MAX", "MAX_CHARGE_CURRENT", "MAX_DISCHARGE_CURRENT",
        "BATTERY_COM", "ACTIVE", "ROW_VERSION",
    ),
    "inverter_system": ("ID", "INVERTER_ID", "SYSTEM_TYPE"),
    "inverter_communication": ("ID", "INVERTER_ID", "COMMUNICATION_TYPE"),
}
TARGET_DECIMAL_SPECS = {
    "inverter": {
        **{field: (10, 2) for field in ("DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT")},
        "MAX_OPERATING_TEMPERATURE": (6, 2), "MIN_OPERATING_TEMPERATURE": (6, 2),
        "OVERLOAD": (7, 2), "MAX_EFFICIENCY": (6, 2), "EURO_EFFICIENCY": (6, 2),
    },
    "module": {
        **{field: (10, 2) for field in
           ("DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT", "VMPP", "IMPP", "VOC", "ISC")},
        "WP": (12, 2), "COEF_PMAX": (8, 5), "COEF_VOC": (8, 5), "COEF_ISC": (8, 5),
    },
    "mppt": {field: (10, 2) for field in (
        "MAX_INPUT_VOLTAGE", "MIN_STARTUP_VOLTAGE", "MAX_OPERATING_VOLTAGE",
        "MIN_OPERATING_VOLTAGE", "MAX_FULL_LOAD_VOLTAGE", "MIN_FULL_LOAD_VOLTAGE",
        "RATED_INPUT_VOLTAGE", "MAX_SHORT_CIRCUIT_CURRENT_PER_MPPT",
        "MAX_SHORT_CIRCUIT_CURRENT_PER_STRING", "MAX_OPERATING_CURRENT_PER_MPPT",
        "MAX_OPERATING_CURRENT_PER_STRING",
    )},
    "inverter_ac_profile": {
        **{field: (12, 2) for field in
           ("RATED_ACTIVE_POWER", "MAX_ACTIVE_POWER", "MAX_PEAK_ACTIVE_POWER")},
        **{field: (10, 2) for field in (
            "RATED_LINE_TO_LINE_VOLTAGE", "RATED_LINE_TO_NEUTRAL_VOLTAGE",
            "RATED_CURRENT", "MAX_CURRENT", "SWITCHING_TIME",
        )},
    },
    "inverter_battery": {field: (10, 2) for field in (
        "BATTERY_VOLTAGE_MIN", "BATTERY_VOLTAGE_MAX", "MAX_CHARGE_CURRENT",
        "MAX_DISCHARGE_CURRENT",
    )},
}


def _sanitize_database_errors(message):
    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except (ValueError, RuntimeError):
                raise
            except Exception:
                raise RuntimeError(message) from None
        return wrapped
    return decorator


def _driver():
    try:
        import pymysql
    except ImportError as error:
        raise RuntimeError("PyMySQL não instalado; use requirements-v3-migration.txt.") from error
    return pymysql


def connect(config, include_database=True):
    if include_database:
        validate_test_schema(config["database"])
    pymysql = _driver()
    args = {"host": config["host"], "port": int(config.get("port", 3306)),
            "user": config["user"], "password": config["password"],
            "charset": "utf8mb4", "autocommit": False}
    if config.get("ssl_ca"):
        args.update({"ssl_ca": config["ssl_ca"], "ssl_verify_cert": True,
                     "ssl_verify_identity": True})
    if include_database:
        args["database"] = config["database"]
    try:
        return pymysql.connect(**args)
    except Exception:
        raise RuntimeError(
            "Falha ao conectar ao MySQL; confira host, porta, usuário, senha e permissões no .env local."
        ) from None


def validate_test_schema(name):
    if not SAFE_TEST_SCHEMA.fullmatch(name or ""):
        raise ValueError("O schema de destino deve terminar em _ensaio ou _test.")


def split_sql(text):
    statements, current = [], []
    for line in text.splitlines():
        if line.lstrip().startswith("--"):
            continue
        current.append(line)
        if line.rstrip().endswith(";"):
            statement = "\n".join(current).strip().rstrip(";")
            if statement:
                statements.append(statement)
            current = []
    if "".join(current).strip():
        raise ValueError("DDL termina sem ponto e vírgula.")
    return statements


def _ddl_sha256(path=OFFICIAL_DDL_PATH):
    text = Path(path).read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest(), text


def _canonical_structure_sha256(sections):
    canonical = json.dumps(sections, ensure_ascii=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _schema_structure_sha256(cursor, database):
    queries = (
        ("schema", "SELECT DEFAULT_CHARACTER_SET_NAME,DEFAULT_COLLATION_NAME "
         "FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s", (database,)),
        ("tables", "SELECT TABLE_NAME,ENGINE,TABLE_COLLATION,ROW_FORMAT "
         "FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s AND TABLE_TYPE='BASE TABLE' "
         "ORDER BY TABLE_NAME", (database,)),
        ("columns", "SELECT TABLE_NAME,ORDINAL_POSITION,COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,"
         "COLUMN_DEFAULT,EXTRA,GENERATION_EXPRESSION,CHARACTER_SET_NAME,COLLATION_NAME "
         "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s "
         "ORDER BY TABLE_NAME,ORDINAL_POSITION", (database,)),
        ("indexes", "SELECT TABLE_NAME,INDEX_NAME,NON_UNIQUE,SEQ_IN_INDEX,COLUMN_NAME,"
         "COLLATION,SUB_PART,INDEX_TYPE,IS_VISIBLE,EXPRESSION FROM information_schema.STATISTICS "
         "WHERE TABLE_SCHEMA=%s ORDER BY TABLE_NAME,INDEX_NAME,SEQ_IN_INDEX", (database,)),
        ("constraints", "SELECT TABLE_NAME,CONSTRAINT_NAME,CONSTRAINT_TYPE,ENFORCED "
         "FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA=%s "
         "ORDER BY TABLE_NAME,CONSTRAINT_NAME", (database,)),
        ("keys", "SELECT TABLE_NAME,CONSTRAINT_NAME,COLUMN_NAME,ORDINAL_POSITION,"
         "POSITION_IN_UNIQUE_CONSTRAINT,REFERENCED_TABLE_SCHEMA,REFERENCED_TABLE_NAME,"
         "REFERENCED_COLUMN_NAME "
         "FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=%s "
         "ORDER BY TABLE_NAME,CONSTRAINT_NAME,ORDINAL_POSITION", (database,)),
        ("foreign_keys", "SELECT TABLE_NAME,CONSTRAINT_NAME,UNIQUE_CONSTRAINT_SCHEMA,"
         "UNIQUE_CONSTRAINT_NAME,MATCH_OPTION,UPDATE_RULE,DELETE_RULE "
         "FROM information_schema.REFERENTIAL_CONSTRAINTS "
         "WHERE CONSTRAINT_SCHEMA=%s ORDER BY TABLE_NAME,CONSTRAINT_NAME", (database,)),
        ("checks", "SELECT CONSTRAINT_NAME,CHECK_CLAUSE FROM information_schema.CHECK_CONSTRAINTS "
         "WHERE CONSTRAINT_SCHEMA=%s ORDER BY CONSTRAINT_NAME", (database,)),
        ("triggers", "SELECT EVENT_OBJECT_TABLE,TRIGGER_NAME,ACTION_TIMING,"
         "EVENT_MANIPULATION,ACTION_ORIENTATION,ACTION_STATEMENT "
         "FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=%s "
         "ORDER BY EVENT_OBJECT_TABLE,TRIGGER_NAME", (database,)),
        ("partitions", "SELECT TABLE_NAME,PARTITION_NAME,SUBPARTITION_NAME,"
         "PARTITION_METHOD,SUBPARTITION_METHOD,PARTITION_EXPRESSION,SUBPARTITION_EXPRESSION "
         "FROM information_schema.PARTITIONS WHERE TABLE_SCHEMA=%s "
         "ORDER BY TABLE_NAME,PARTITION_ORDINAL_POSITION,SUBPARTITION_ORDINAL_POSITION",
         (database,)),
    )
    sections = []
    for name, query, parameters in queries:
        cursor.execute(query, parameters)
        sections.append((name, list(cursor.fetchall())))
    return _canonical_structure_sha256(sections)


def _assert_physical_envelope(cursor, database):
    cursor.execute(
        "SELECT DEFAULT_CHARACTER_SET_NAME,DEFAULT_COLLATION_NAME "
        "FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s",
        (database,),
    )
    schema = cursor.fetchone()
    if schema != ("utf8mb4", "utf8mb4_0900_ai_ci"):
        raise RuntimeError(
            "Schema existente possui charset/collation incompatível; nenhuma alteração foi feita."
        )
    cursor.execute(
        "SELECT TABLE_NAME,ENGINE,TABLE_COLLATION,ROW_FORMAT "
        "FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s AND TABLE_TYPE='BASE TABLE'",
        (database,),
    )
    for _, engine, collation, row_format in cursor.fetchall():
        if (engine != "InnoDB" or collation != "utf8mb4_0900_ai_ci"
                or str(row_format).casefold() != "dynamic"):
            raise RuntimeError(
                "Schema existente possui engine, collation ou row format incompatível; "
                "nenhuma alteração foi feita."
            )


def _assert_schema_compatible(cursor, database, expected_ddl_sha256=None):
    _assert_physical_envelope(cursor, database)
    cursor.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s", (database,))
    tables = {row[0] for row in cursor.fetchall()}
    if tables != EXPECTED_TABLES:
        raise RuntimeError("Schema existente está incompleto ou possui estrutura desconhecida; nenhuma alteração foi feita.")
    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA=%s AND TABLE_NAME='schema_version'",
        (database,),
    )
    version_columns = {row[0] for row in cursor.fetchall()}
    if not {"DDL_SHA256", "STRUCTURE_SHA256"}.issubset(version_columns):
        raise RuntimeError("Schema reconhecido, mas sem assinatura física compatível; nenhuma alteração foi feita.")
    cursor.execute(f"SELECT VERSION,DDL_SHA256,STRUCTURE_SHA256 FROM `{database}`.schema_version")
    versions = list(cursor.fetchall())
    if len(versions) != 1 or versions[0][0] != SCHEMA_VERSION:
        raise RuntimeError("Schema reconhecido, mas com versão incompatível; nenhuma alteração foi feita.")
    _, stored_ddl_sha256, stored_structure_sha256 = versions[0]
    if expected_ddl_sha256 is not None and stored_ddl_sha256 != expected_ddl_sha256:
        raise RuntimeError("Schema reconhecido, mas com assinatura de DDL incompatível; nenhuma alteração foi feita.")
    actual_structure_sha256 = _schema_structure_sha256(cursor, database)
    if stored_structure_sha256 != actual_structure_sha256:
        raise RuntimeError("Schema reconhecido, mas sua estrutura física foi alterada; nenhuma operação foi feita.")
    return {"ddl_sha256": stored_ddl_sha256,
            "structure_sha256": actual_structure_sha256}


@_sanitize_database_errors("Falha ao inspecionar o MySQL; detalhes do servidor foram omitidos.")
def inspect_server(config):
    validate_test_schema(config["database"])
    with connect(config, include_database=False) as connection:
        with connection.cursor() as cursor:
            observed = _observe_connected_server(cursor)
            cursor.execute("SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s",
                           (config["database"],))
            exists = cursor.fetchone() is not None
    return {**observed, "database": config["database"], "schema_exists": exists}


def _observe_connected_server(cursor):
    cursor.execute(
        "SELECT VERSION(),@@version_comment,@@collation_server,@@sql_mode,"
        "@@innodb_page_size,@@innodb_default_row_format"
    )
    version, product, collation, sql_mode, page_size, row_format = cursor.fetchone()
    return {"version": version, "product": product, "server_collation": collation,
            "sql_mode": sql_mode, "innodb_page_size": int(page_size),
            "innodb_default_row_format": row_format}


def validate_server_observation(observed):
    if not re.match(r"^8\.0\.46(?:$|[-+])", str(observed.get("version", ""))):
        raise RuntimeError("Servidor incompatível: a etapa exige MySQL 8.0.46.")
    if "mysql" not in str(observed.get("product", "")).casefold():
        raise RuntimeError("Produto incompatível: a etapa exige MySQL, não um substituto compatível.")
    modes = {mode.strip().upper() for mode in str(observed.get("sql_mode", "")).split(",")}
    if not modes.intersection({"STRICT_TRANS_TABLES", "STRICT_ALL_TABLES"}):
        raise RuntimeError("SQL mode incompatível: habilite um modo STRICT antes do ensaio.")
    try:
        page_size = int(observed.get("innodb_page_size"))
    except (TypeError, ValueError):
        raise RuntimeError("Configuração InnoDB incompatível: innodb_page_size não observado.") from None
    if page_size < 8192:
        raise RuntimeError("Configuração InnoDB incompatível: innodb_page_size deve ser ao menos 8192.")
    return True


def _validate_connected_server(cursor):
    observed = _observe_connected_server(cursor)
    validate_server_observation(observed)
    return observed


@_sanitize_database_errors("Falha ao aplicar o DDL no schema de ensaio; detalhes foram omitidos.")
def apply_schema(config, ddl_path):
    validate_test_schema(config["database"])
    database = config["database"]
    resolved_ddl = Path(ddl_path).resolve()
    if resolved_ddl != OFFICIAL_DDL_PATH.resolve():
        raise ValueError("Somente o DDL versionado oficial 0001 pode ser aplicado nesta etapa.")
    ddl_sha256, ddl = _ddl_sha256(resolved_ddl)
    with connect(config, include_database=False) as connection:
        with connection.cursor() as cursor:
            _validate_connected_server(cursor)
            cursor.execute("SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s", (database,))
            exists = cursor.fetchone() is not None
            if exists:
                cursor.execute("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s",
                               (database,))
                tables = {row[0] for row in cursor.fetchall()}
                if tables:
                    signature = _assert_schema_compatible(cursor, database, ddl_sha256)
                    return {"created": False, "already_initialized": True,
                            **signature}
                _assert_physical_envelope(cursor, database)
            else:
                cursor.execute(f"CREATE DATABASE `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
        connection.commit()
    with connect(config) as connection:
        with connection.cursor() as cursor:
            _validate_connected_server(cursor)
            _assert_physical_envelope(cursor, database)
            for statement in split_sql(ddl):
                cursor.execute(statement)
            _assert_physical_envelope(cursor, database)
            structure_sha256 = _schema_structure_sha256(cursor, database)
            cursor.execute(
                "INSERT INTO schema_version (VERSION,DDL_SHA256,STRUCTURE_SHA256,DESCRIPTION) "
                "VALUES (%s,%s,%s,%s)",
                (SCHEMA_VERSION, ddl_sha256, structure_sha256,
                 "Initial Optimus Sun v3 catalog and migration metadata"),
            )
            if cursor.rowcount != 1:
                raise RuntimeError("Não foi possível registrar a assinatura física do schema.")
        connection.commit()
    return {"created": not exists, "already_initialized": False,
            "ddl_sha256": ddl_sha256, "structure_sha256": structure_sha256}


def _exact_decimal(value, precision, scale):
    if isinstance(value, bool):
        raise ValueError
    decimal_value = Decimal(str(value))
    if not decimal_value.is_finite():
        raise ValueError
    quantum = Decimal(1).scaleb(-scale)
    if decimal_value.quantize(quantum) != decimal_value:
        raise ValueError
    if abs(decimal_value) >= Decimal(10) ** (precision - scale):
        raise ValueError
    return decimal_value


def _ensure_unique(rows, key_function, message, *, reported_issues=None,
                   reason_code=None, entity_type=None):
    """Validate uniqueness, permitting only collisions already reported as errors.

    A simulation plan may intentionally contain rows that cannot be loaded so its
    audit report remains complete.  Such a plan is still rejected by ``load_plan``
    because its error count is non-zero; this exception only lets preflight verify
    that every impossible collision has an explicit, row-specific occurrence.
    """
    seen = set()
    for row in rows:
        key = key_function(row)
        if key in seen:
            signature = (reason_code, entity_type, str(row["ID"]))
            if reported_issues is None or signature not in reported_issues:
                raise ValueError(message)
        seen.add(key)


def _validate_required_text(rows, field, maximum, table):
    for row in rows:
        value = row[field]
        if not isinstance(value, str) or not value.strip() or len(value) > maximum:
            raise ValueError(f"Plano de importação possui texto inválido em {table}.{field}.")


def _validate_plan(plan):
    required_top = {"format_version", "mapping_version", "source", "decisions_sha256",
                    "counts", "tables", "mappings", "issues", "plan_sha256"}
    if not isinstance(plan, dict) or set(plan) != required_top:
        raise ValueError("Plano de importação possui estrutura de topo inválida.")
    if plan["format_version"] != 1 or plan["mapping_version"] != MAPPING_VERSION:
        raise ValueError("Plano de importação possui versão incompatível.")
    source = plan["source"]
    required_source = {"source_id", "source_sha256", "snapshot_sha256"}
    if not isinstance(source, dict) or not required_source.issubset(source):
        raise ValueError("Plano de importação não identifica a origem completa.")
    if not isinstance(source["source_id"], str) or not source["source_id"].strip():
        raise ValueError("Plano de importação possui source_id inválido.")
    for field in ("source_sha256", "snapshot_sha256"):
        if (not isinstance(source[field], str)
                or not re.fullmatch(r"[0-9a-f]{64}", source[field])):
            raise ValueError(f"Plano de importação possui {field} inválido.")
    if (not isinstance(plan["decisions_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", plan["decisions_sha256"])):
        raise ValueError("Plano de importação possui decisions_sha256 inválido.")
    if (not isinstance(plan["plan_sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", plan["plan_sha256"])):
        raise ValueError("Plano de importação possui plan_sha256 inválido.")
    if not isinstance(plan["tables"], dict) or set(plan["tables"]) != set(LOAD_ORDER):
        raise ValueError("Plano de importação possui conjunto de tabelas inválido.")
    for table in LOAD_ORDER:
        rows = plan["tables"][table]
        if not isinstance(rows, list):
            raise ValueError(f"Plano de importação possui linhas inválidas em {table}.")
        expected_columns = set(TABLE_COLUMNS[table])
        if any(not isinstance(row, dict) or set(row) != expected_columns for row in rows):
            raise ValueError(f"Plano de importação possui colunas inválidas em {table}.")
        identifiers = [row["ID"] for row in rows]
        if any(type(identifier) is not int or identifier < 1 for identifier in identifiers):
            raise ValueError(f"Plano de importação possui ID inválido em {table}.")
        if len(identifiers) != len(set(identifiers)):
            raise ValueError(f"Plano de importação possui ID duplicado em {table}.")
    issue_columns = {"severity", "entity_type", "source_key", "field", "reason_code", "details"}
    if not isinstance(plan["issues"], list) or any(
        not isinstance(row, dict) or set(row) != issue_columns
        or row["severity"] not in {"ERROR", "PENDING", "WARNING", "INFO"}
        or not isinstance(row["entity_type"], str)
        or not isinstance(row["source_key"], str)
        or not isinstance(row["reason_code"], str)
        or not isinstance(row["details"], dict)
        for row in plan["issues"]
    ):
        raise ValueError("Plano de importação possui ocorrências inválidas.")
    if not isinstance(plan["mappings"], list) or any(
        not isinstance(row, dict)
        or set(row) != {"ENTITY_TYPE", "SOURCE_KEY", "TARGET_ID", "CONTENT_SHA256"}
        or not isinstance(row["ENTITY_TYPE"], str)
        or not isinstance(row["SOURCE_KEY"], str)
        or type(row["TARGET_ID"]) is not int or row["TARGET_ID"] < 1
        or not isinstance(row["CONTENT_SHA256"], str)
        or not re.fullmatch(r"[0-9a-f]{64}", row["CONTENT_SHA256"])
        for row in plan["mappings"]
    ):
        raise ValueError("Plano de importação possui mapeamentos inválidos.")
    reported_issues = {(row["reason_code"], row["entity_type"], row["source_key"])
                       for row in plan["issues"] if row["severity"] == "ERROR"}
    reported_issue_fields = {
        (row["reason_code"], row["entity_type"], row["source_key"], row["field"])
        for row in plan["issues"] if row["severity"] == "ERROR"
    }

    _validate_required_text(plan["tables"]["manufacturer"], "NAME", 150, "manufacturer")
    _validate_required_text(plan["tables"]["inverter"], "MODEL", 255, "inverter")
    _validate_required_text(plan["tables"]["module"], "MODEL", 255, "module")
    _validate_required_text(plan["tables"]["inverter_output_mode"], "OUTPUT_MODE", 100,
                            "inverter_output_mode")
    _validate_required_text(plan["tables"]["inverter_system"], "SYSTEM_TYPE", 100,
                            "inverter_system")
    _validate_required_text(plan["tables"]["inverter_communication"],
                            "COMMUNICATION_TYPE", 100, "inverter_communication")
    _ensure_unique(plan["tables"]["manufacturer"],
                   lambda row: normalized_key(row["NAME"]),
                   "Plano de importação possui fabricante normalizado duplicado.",
                   reported_issues=reported_issues,
                   reason_code="NORMALIZED_NAME_COLLISION", entity_type="manufacturer")
    _ensure_unique(plan["tables"]["inverter"],
                   lambda row: (row["MANUFACTURER_ID"], normalized_key(row["MODEL"])),
                   "Plano de importação possui inversor normalizado duplicado.",
                   reported_issues=reported_issues,
                   reason_code="NORMALIZED_MODEL_COLLISION", entity_type="inverter")
    _ensure_unique(plan["tables"]["module"],
                   lambda row: (row["MANUFACTURER_ID"], normalized_key(row["MODEL"])),
                   "Plano de importação possui módulo normalizado duplicado.",
                   reported_issues=reported_issues,
                   reason_code="NORMALIZED_MODEL_COLLISION", entity_type="module")
    _ensure_unique(plan["tables"]["inverter_output_mode"],
                   lambda row: normalized_key(row["OUTPUT_MODE"]),
                   "Plano de importação possui modo normalizado duplicado.",
                   reported_issues=reported_issues,
                   reason_code="NORMALIZED_OUTPUT_MODE_COLLISION",
                   entity_type="inverter_output_mode")
    _ensure_unique(plan["tables"]["mppt"],
                   lambda row: (row["INVERTER_ID"], row["MPPT_INDEX"]),
                   "Plano de importação possui grupo MPPT duplicado.",
                   reported_issues=reported_issues,
                   reason_code="DUPLICATE_GROUP_INDEX", entity_type="mppt")
    _ensure_unique(plan["tables"]["inverter_system"],
                   lambda row: (row["INVERTER_ID"], normalized_key(row["SYSTEM_TYPE"])),
                   "Plano de importação possui classificação de sistema duplicada.")
    _ensure_unique(plan["tables"]["inverter_communication"],
                   lambda row: (row["INVERTER_ID"], normalized_key(row["COMMUNICATION_TYPE"])),
                   "Plano de importação possui comunicação duplicada.")
    defaults = set()
    inverter_ids = {row["ID"] for row in plan["tables"]["inverter"]}
    manufacturer_ids = {row["ID"] for row in plan["tables"]["manufacturer"]}
    output_modes_by_id = {row["ID"]: row
                         for row in plan["tables"]["inverter_output_mode"]}
    output_mode_by_id = {identifier: row["OUTPUT_MODE"]
                         for identifier, row in output_modes_by_id.items()}
    generic_fk_error = ("FOREIGN_KEY_VIOLATION", "database", "sqlite") in reported_issues
    if (any(row["MANUFACTURER_ID"] not in manufacturer_ids
            for table in ("inverter", "module") for row in plan["tables"][table])
            and not generic_fk_error):
        raise ValueError("Plano de importação possui referência de fabricante inválida.")
    for table in ("mppt", "inverter_ac_profile", "inverter_battery",
                  "inverter_system", "inverter_communication"):
        orphan_rows = [row for row in plan["tables"][table]
                       if row["INVERTER_ID"] not in inverter_ids]
        if orphan_rows:
            specific_mppt_errors = (
                table == "mppt"
                and all(("ORPHAN_INVERTER_REFERENCE", "mppt", str(row["ID"]))
                        in reported_issues for row in orphan_rows)
            )
            if not generic_fk_error and not specific_mppt_errors:
                raise ValueError(
                    f"Plano de importação possui referência de inversor inválida em {table}."
                )
    systems_by_inverter = {}
    for row in plan["tables"]["inverter_system"]:
        systems_by_inverter.setdefault(row["INVERTER_ID"], set()).add(
            str(row["SYSTEM_TYPE"]).strip().upper()
        )
    for profile in plan["tables"]["inverter_ac_profile"]:
        if profile["PROFILE_TYPE"] not in {"AC_OUTPUT", "AC_INPUT", "EPS_OUTPUT"}:
            raise ValueError("Plano de importação possui PROFILE_TYPE inválido.")
        if (type(profile["ACTIVE"]) is not int or profile["ACTIVE"] not in (0, 1)
                or type(profile["IS_DEFAULT"]) is not int or profile["IS_DEFAULT"] not in (0, 1)):
            raise ValueError("Plano de importação possui booleano de perfil inválido.")
        if profile["IS_DEFAULT"]:
            if not profile["ACTIVE"] or profile["PROFILE_TYPE"] == "AC_INPUT":
                raise ValueError("Plano de importação possui perfil padrão inválido.")
            if profile["INVERTER_ID"] in defaults:
                raise ValueError("Plano de importação possui mais de um padrão por inversor.")
            defaults.add(profile["INVERTER_ID"])
        if profile["PROFILE_TYPE"] == "AC_INPUT":
            if profile["OUTPUT_MODE_ID"] is not None or profile["IS_DEFAULT"]:
                raise ValueError("Plano de importação possui AC_INPUT com modo/padrão inválido.")
            if profile["ACTIVE"]:
                try:
                    validate_ac_input(profile, systems_by_inverter.get(profile["INVERTER_ID"], set()))
                except DomainValidationError as error:
                    raise ValueError("Plano de importação possui AC_INPUT ativo inválido.") from error
        else:
            if (profile["OUTPUT_MODE_ID"] is not None
                    and profile["OUTPUT_MODE_ID"] not in output_mode_by_id):
                raise ValueError("Plano de importação possui referência de modo inválida.")
        if profile["ACTIVE"] and profile["PROFILE_TYPE"] in {"AC_OUTPUT", "EPS_OUTPUT"}:
            systems = systems_by_inverter.get(profile["INVERTER_ID"], set())
            source_key = f"{profile['INVERTER_ID']}:{output_mode_by_id.get(profile['OUTPUT_MODE_ID'], '')}"
            required_profile_issues = set()
            if profile["OUTPUT_MODE_ID"] is None:
                required_profile_issues.add(("ACTIVE_OUTPUT_WITHOUT_MODE", "ac_profile",
                                             str(profile["ID"])))
            else:
                mode = output_modes_by_id[profile["OUTPUT_MODE_ID"]]
                if mode["ACTIVE"] not in (1, True):
                    required_profile_issues.add(("ACTIVE_OUTPUT_WITH_INACTIVE_MODE", "ac_profile",
                                                 str(profile["ID"])))
            try:
                nominal_power = Decimal(str(profile["RATED_ACTIVE_POWER"]))
                nominal_power_ok = nominal_power.is_finite() and nominal_power > 0
            except (InvalidOperation, TypeError, ValueError):
                nominal_power_ok = False
            if not nominal_power_ok:
                required_profile_issues.add(("ACTIVE_PROFILE_MISSING_NOMINAL_OUTPUT_POWER",
                                             "ac_profile", source_key))
            if not systems:
                required_profile_issues.add(("ACTIVE_OUTPUT_MISSING_SYSTEM_CLASSIFICATION",
                                             "ac_profile", str(profile["ID"])))
            elif ((profile["PROFILE_TYPE"] == "AC_OUTPUT"
                   and not systems.intersection({"ON-GRID", "GRIDZERO", "HYBRID"}))
                  or (profile["PROFILE_TYPE"] == "EPS_OUTPUT"
                      and not systems.intersection({"OFF-GRID", "HYBRID"}))):
                required_profile_issues.add(("ACTIVE_OUTPUT_SYSTEM_INCOMPATIBLE", "ac_profile",
                                             str(profile["ID"])))
            try:
                validate_output_profile(profile, systems)
            except DomainValidationError:
                if not required_profile_issues.issubset(reported_issues):
                    raise ValueError("Plano de importação possui perfil de saída ativo inválido sem ocorrência correspondente.") from None
            if not required_profile_issues.issubset(reported_issues):
                raise ValueError("Plano de importação possui perfil de saída ativo inválido sem ocorrência correspondente.")
    boolean_columns = {
        "inverter": ("ACTIVE",), "module": ("ACTIVE",),
        "inverter_output_mode": ("ACTIVE",), "inverter_battery": ("ACTIVE",),
    }
    for table, fields in boolean_columns.items():
        for row in plan["tables"][table]:
            for field in fields:
                if (type(row[field]) is not int or row[field] not in (0, 1)):
                    signature = ("INVALID_BOOLEAN", table, str(row["ID"]), field)
                    if signature not in reported_issue_fields:
                        raise ValueError(
                            f"Plano de importação possui booleano inválido em {table}."
                        )
    for row in plan["tables"]["mppt"]:
        if (type(row["MPPT_INDEX"]) is not int or row["MPPT_INDEX"] == 1
                or not 0 <= row["MPPT_INDEX"] <= 18_446_744_073_709_551_615):
            signature = ("INVALID_GROUP_INDEX", "mppt", str(row["ID"]))
            if signature not in reported_issues:
                raise ValueError("Plano de importação possui MPPT_INDEX inválido.")
    groups_by_inverter = defaultdict(list)
    for row in plan["tables"]["mppt"]:
        groups_by_inverter[row["INVERTER_ID"]].append(row)
    inverter_by_id = {row["ID"]: row for row in plan["tables"]["inverter"]}
    required_mppt_issues = set()
    required_mppt_issue_fields = set()
    for inverter_id, groups in groups_by_inverter.items():
        if inverter_id not in inverter_by_id:
            continue
        parent = inverter_by_id[inverter_id]
        trackers = parent["NUMBER_OF_TRACKERS"]
        total_inputs = parent["NUMBER_OF_INPUTS"]
        if (type(trackers) is not int or not 1 <= trackers <= 65535
                or type(total_inputs) is not int or not 0 <= total_inputs <= 65535):
            signature = ("INVALID_MPPT_TOTALS", "inverter", str(inverter_id))
            if signature not in reported_issues:
                raise ValueError("Plano de importação possui totais MPPT inválidos.")
            continue
        occupied = set()
        seen_codes = set()
        weighted_inputs = 0
        all_valid = True
        for group in groups:
            code = group["MPPT_INDEX"]
            inputs = group["NUMBER_OF_INPUTS"]
            if type(inputs) is not int or not 0 <= inputs <= 65535:
                signatures = {
                    ("INVALID_INPUT_COUNT", "mppt", str(group["ID"])),
                    ("UNSIGNED_RANGE_ERROR", "mppt", str(group["ID"])),
                }
                if not signatures.intersection(reported_issues):
                    raise ValueError(
                        "Plano de importação possui quantidade de entradas MPPT inválida."
                    )
                all_valid = False
                continue
            for minimum_field, maximum_field in (
                ("MIN_OPERATING_VOLTAGE", "MAX_OPERATING_VOLTAGE"),
                ("MIN_FULL_LOAD_VOLTAGE", "MAX_FULL_LOAD_VOLTAGE"),
            ):
                minimum = group[minimum_field]
                maximum = group[maximum_field]
                try:
                    inverted = (minimum is not None and maximum is not None
                                and Decimal(str(minimum)) > Decimal(str(maximum)))
                except (InvalidOperation, TypeError, ValueError):
                    inverted = False
                if inverted:
                    required_mppt_issue_fields.add(
                        ("INVALID_VOLTAGE_RANGE", "mppt", str(group["ID"]), minimum_field)
                    )
            if code in seen_codes:
                required_mppt_issues.add(("DUPLICATE_GROUP_INDEX", "mppt", str(group["ID"])))
            seen_codes.add(code)
            try:
                positions = decode_group(code, trackers)
            except ValueError:
                all_valid = False
                required_mppt_issues.add(("INVALID_GROUP_INDEX", "mppt", str(group["ID"])))
                continue
            if occupied & positions:
                required_mppt_issues.add(("OVERLAPPING_GROUPS", "mppt", str(group["ID"])))
            occupied |= positions
            weighted_inputs += len(positions) * inputs
        if all_valid and occupied != set(range(1, trackers + 1)):
            required_mppt_issues.add(("INCOMPLETE_MPPT_COVERAGE", "inverter", str(inverter_id)))
        if all_valid and weighted_inputs != total_inputs:
            required_mppt_issues.add(("MPPT_INPUT_TOTAL_MISMATCH", "inverter", str(inverter_id)))
    if not required_mppt_issues.issubset(reported_issues):
        raise ValueError("Plano de importação omite inconsistência estrutural de MPPT.")
    if not required_mppt_issue_fields.issubset(reported_issue_fields):
        raise ValueError("Plano de importação omite faixa de tensão MPPT inválida.")
    signed_decimal_fields = {
        ("inverter", "MAX_OPERATING_TEMPERATURE"),
        ("inverter", "MIN_OPERATING_TEMPERATURE"),
        ("module", "COEF_PMAX"), ("module", "COEF_VOC"), ("module", "COEF_ISC"),
    }
    for table, specs in TARGET_DECIMAL_SPECS.items():
        for row in plan["tables"][table]:
            for field, (precision, scale) in specs.items():
                value = row[field]
                if value is None:
                    continue
                try:
                    decimal_value = _exact_decimal(value, precision, scale)
                except (InvalidOperation, ValueError):
                    raise ValueError(f"Plano de importação possui decimal fora da precisão em {table}.{field}.") from None
                if decimal_value < 0 and (table, field) not in signed_decimal_fields:
                    signature = ("NEGATIVE_VALUE", table, str(row["ID"]), field)
                    if signature not in reported_issue_fields:
                        raise ValueError(f"Plano de importação omite valor negativo em {table}.{field}.")
    for row in plan["tables"]["manufacturer"]:
        if type(row["CATEGORY"]) is not int or row["CATEGORY"] not in (0, 1, 2):
            signature = ("INVALID_CATEGORY", "manufacturer", str(row["ID"]), "CATEGORY")
            if signature not in reported_issue_fields:
                raise ValueError("Plano de importação possui categoria de fabricante inválida.")
    for row in plan["tables"]["inverter"]:
        for field in ("NUMBER_OF_TRACKERS", "NUMBER_OF_INPUTS", "NUMBER_OF_BATTERY_INPUTS"):
            value = row[field]
            if value is not None and (type(value) is not int or not 0 <= value <= 65535):
                field_signature = ("UNSIGNED_RANGE_ERROR", "inverter", str(row["ID"]), field)
                total_signature = ("INVALID_MPPT_TOTALS", "inverter", str(row["ID"]))
                if (field_signature not in reported_issue_fields
                        and total_signature not in reported_issues):
                    raise ValueError(
                        f"Plano de importação possui inteiro fora da faixa em inverter.{field}."
                    )
        minimum = row["MIN_OPERATING_TEMPERATURE"]
        maximum = row["MAX_OPERATING_TEMPERATURE"]
        if minimum is not None and maximum is not None and Decimal(str(minimum)) > Decimal(str(maximum)):
            raise ValueError("Plano de importação possui faixa de temperatura invertida.")
        for field in ("MAX_EFFICIENCY", "EURO_EFFICIENCY"):
            value = row[field]
            if value is not None and Decimal(str(value)) > 100:
                raise ValueError(f"Plano de importação possui percentual inválido em inverter.{field}.")
    for table in LOAD_ORDER:
        if any(row["ID"] > 4_294_967_295 for row in plan["tables"][table]):
            raise ValueError(f"Plano de importação possui ID fora de INT UNSIGNED em {table}.")
    for table in ("inverter", "module", "inverter_ac_profile", "inverter_battery"):
        for row in plan["tables"][table]:
            if type(row["ROW_VERSION"]) is not int or not 1 <= row["ROW_VERSION"] <= 4_294_967_295:
                raise ValueError(f"Plano de importação possui ROW_VERSION inválido em {table}.")
    for row in plan["tables"]["inverter_battery"]:
        if (type(row["BATTERY_INDEX"]) is not int or row["BATTERY_INDEX"] == 1
                or not 0 <= row["BATTERY_INDEX"] <= 18_446_744_073_709_551_615):
            raise ValueError("Plano de importação possui BATTERY_INDEX inválido.")
        minimum = row["BATTERY_VOLTAGE_MIN"]
        maximum = row["BATTERY_VOLTAGE_MAX"]
        if minimum is not None and maximum is not None and Decimal(str(minimum)) > Decimal(str(maximum)):
            raise ValueError("Plano de importação possui faixa de bateria invertida.")
    battery_groups = defaultdict(list)
    for row in plan["tables"]["inverter_battery"]:
        battery_groups[row["INVERTER_ID"]].append(row)
    for inverter_id, groups in battery_groups.items():
        try:
            validate_battery_groups(groups, inverter_by_id[inverter_id]["NUMBER_OF_BATTERY_INPUTS"])
        except DomainValidationError as error:
            raise ValueError("Plano de importação possui grupos ativos de bateria inválidos.") from error
    profile_by_id = {row["ID"]: row for row in plan["tables"]["inverter_ac_profile"]}
    mapping_keys = set()
    mapped_profiles = set()
    for mapping in plan["mappings"]:
        key = (mapping["ENTITY_TYPE"], mapping["SOURCE_KEY"])
        if key in mapping_keys:
            raise ValueError("Plano de importação possui mapeamento duplicado.")
        mapping_keys.add(key)
        if mapping["ENTITY_TYPE"] != "ac_profile" or mapping["TARGET_ID"] not in profile_by_id:
            raise ValueError("Plano de importação possui alvo de mapeamento inválido.")
        profile = profile_by_id[mapping["TARGET_ID"]]
        expected_key = f"{profile['INVERTER_ID']}:{output_mode_by_id.get(profile['OUTPUT_MODE_ID'], '')}"
        expected_hash = hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest()
        if mapping["SOURCE_KEY"] != expected_key or mapping["CONTENT_SHA256"] != expected_hash:
            raise ValueError("Plano de importação possui conteúdo de mapeamento divergente.")
        mapped_profiles.add(profile["ID"])
    if mapped_profiles != set(profile_by_id):
        raise ValueError("Plano de importação não mapeia todos os perfis CA.")
    calculated_counts = {table: len(plan["tables"][table]) for table in LOAD_ORDER}
    active_output_modes = {
        row["ID"] for row in plan["tables"]["inverter_output_mode"] if row["ACTIVE"] in (1, True)
    }
    calculated_counts["ready_profiles"] = sum(
        output_profile_is_ready(
            row, systems_by_inverter.get(row["INVERTER_ID"], set()), active_output_modes
        )
        for row in plan["tables"]["inverter_ac_profile"]
    )
    calculated_counts["pending"] = sum(row.get("severity") == "PENDING" for row in plan["issues"])
    calculated_counts["errors"] = sum(row.get("severity") == "ERROR" for row in plan["issues"])
    if plan["counts"] != calculated_counts:
        raise ValueError("Contagens do plano não correspondem ao conteúdo; carga recusada.")
    if plan["plan_sha256"] != _plan_sha256(plan):
        raise ValueError("Checksum do plano de importação divergente; carga recusada.")
    return True


def _insert_rows(cursor, table, rows):
    if not rows:
        return
    columns = TABLE_COLUMNS[table]
    placeholders = ",".join(["%s"] * len(columns))
    names = ",".join(f"`{column}`" for column in columns)
    sql = f"INSERT INTO `{table}` ({names}) VALUES ({placeholders})"
    cursor.executemany(sql, [tuple(row.get(column) for column in columns) for row in rows])


@_sanitize_database_errors("Falha na carga transacional; rollback executado e detalhes omitidos.")
def load_plan(config, plan, *, inject_failure_after_table=None):
    validate_test_schema(config["database"])
    if inject_failure_after_table is not None and inject_failure_after_table not in LOAD_ORDER:
        raise ValueError("Tabela de injeção de falha inválida.")
    _validate_plan(plan)
    if plan["counts"]["errors"]:
        raise RuntimeError("Plano contém erros estruturais; carga recusada.")
    source = plan["source"]
    plan_sha256 = _plan_sha256(plan)
    with connect(config) as connection:
        lock_name = f"optimus_sun_v3_migration:{config['database'].casefold()}"[:64]
        lock_acquired = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT GET_LOCK(%s,10)", (lock_name,))
                lock_acquired = cursor.fetchone()[0] == 1
                if not lock_acquired:
                    raise RuntimeError("Outra carga de migração está em andamento neste destino.")
                # GET_LOCK is connection-scoped and survives COMMIT. End any
                # transaction snapshot before inspecting state protected by it.
                connection.commit()
                _validate_connected_server(cursor)
                expected_ddl_sha256, _ = _ddl_sha256()
                _assert_schema_compatible(cursor, config["database"], expected_ddl_sha256)
                cursor.execute("SELECT VERSION FROM schema_version WHERE VERSION=%s", (SCHEMA_VERSION,))
                if not cursor.fetchone():
                    raise RuntimeError("Versão de schema não reconhecida.")
                cursor.execute("SELECT ID, SNAPSHOT_SHA256, DECISIONS_SHA256, PLAN_SHA256, STATUS FROM migration_run WHERE SOURCE_ID=%s AND SOURCE_SHA256=%s AND MAPPING_VERSION=%s",
                               (source["source_id"], source["source_sha256"], plan["mapping_version"]))
                previous = cursor.fetchall()
                for run_id, snapshot_hash, decision_hash, previous_plan_hash, status in previous:
                    same_input = (snapshot_hash == source["snapshot_sha256"]
                                  and decision_hash == plan["decisions_sha256"])
                    if same_input and status == "COMPLETED" and previous_plan_hash == plan_sha256:
                        verification = verify_plan(config, plan)
                        if not verification["matches"]:
                            raise RuntimeError("Carga anterior diverge do plano atual; ALREADY_COMPLETED recusado.")
                        return {"status": "ALREADY_COMPLETED", "migration_run_id": run_id,
                                "plan_sha256": plan_sha256}
                    if same_input and status == "COMPLETED":
                        raise RuntimeError("A mesma entrada produziu plano diferente; carga recusada para revisão manual.")
                    if status == "COMPLETED":
                        raise RuntimeError("A origem já foi carregada com snapshot ou decisões diferentes; revisão manual protegida.")
                cursor.execute("SELECT COUNT(*),COALESCE(SUM(STATUS='COMPLETED'),0) FROM migration_run")
                run_count, completed_count = cursor.fetchone()
                if completed_count:
                    raise RuntimeError("Destino já contém outra carga concluída; sincronização incremental não pertence a esta etapa.")
                if run_count:
                    raise RuntimeError("Destino contém execução incompleta; inspeção manual necessária.")
                for table in (*LOAD_ORDER, "migration_id_map", "migration_pending"):
                    cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                    if cursor.fetchone()[0]:
                        raise RuntimeError("Destino de ensaio não está vazio; carga inicial recusada.")
                cursor.execute("INSERT INTO migration_run (SOURCE_ID,SOURCE_SHA256,SNAPSHOT_SHA256,MAPPING_VERSION,DECISIONS_SHA256,PLAN_SHA256,STATUS) VALUES (%s,%s,%s,%s,%s,%s,'RUNNING')",
                               (source["source_id"], source["source_sha256"], source["snapshot_sha256"],
                                plan["mapping_version"], plan["decisions_sha256"], plan_sha256))
                run_id = cursor.lastrowid
                for table in LOAD_ORDER:
                    _insert_rows(cursor, table, plan["tables"][table])
                    if table == inject_failure_after_table:
                        raise RuntimeError("Falha injetada durante carga transacional.")
                for row in plan["mappings"]:
                    cursor.execute("INSERT INTO migration_id_map (MIGRATION_RUN_ID,ENTITY_TYPE,SOURCE_KEY,TARGET_ID,CONTENT_SHA256) VALUES (%s,%s,%s,%s,%s)",
                                   (run_id, row["ENTITY_TYPE"], row["SOURCE_KEY"], row["TARGET_ID"], row["CONTENT_SHA256"]))
                for issue in plan["issues"]:
                    cursor.execute("INSERT INTO migration_pending (MIGRATION_RUN_ID,SEVERITY,ENTITY_TYPE,SOURCE_KEY,FIELD_NAME,REASON_CODE,DETAILS_JSON) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                   (run_id, issue["severity"], issue["entity_type"], issue["source_key"],
                                    issue.get("field"), issue["reason_code"], json.dumps(issue.get("details", {}), ensure_ascii=False)))
                cursor.execute("UPDATE migration_run SET STATUS='COMPLETED', COMPLETED_AT=CURRENT_TIMESTAMP(6) WHERE ID=%s", (run_id,))
            connection.commit()
            return {"status": "COMPLETED", "migration_run_id": run_id,
                    "plan_sha256": plan_sha256}
        except Exception:
            connection.rollback()
            raise
        finally:
            if lock_acquired:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT RELEASE_LOCK(%s)", (lock_name,))
                except Exception:
                    pass


def _values_equal(actual, expected):
    if actual is None or expected is None:
        return actual is expected
    if isinstance(actual, Decimal):
        try:
            return actual == Decimal(str(expected))
        except (InvalidOperation, ValueError):
            return False
    return actual == expected


def _table_mismatches(cursor, table, expected_rows):
    if not expected_rows:
        return []
    columns = TABLE_COLUMNS[table]
    names = ",".join(f"`{column}`" for column in columns)
    cursor.execute(f"SELECT {names} FROM `{table}` ORDER BY `ID`")
    actual_rows = cursor.fetchall()
    expected_rows = sorted(expected_rows, key=lambda row: row["ID"])
    mismatches = []
    if len(actual_rows) != len(expected_rows):
        return [{"table": table, "reason": "ROW_COUNT"}]
    for actual, expected in zip(actual_rows, expected_rows):
        for index, column in enumerate(columns):
            if not _values_equal(actual[index], expected.get(column)):
                mismatches.append({"table": table, "id": expected.get("ID"), "field": column})
    return mismatches


@_sanitize_database_errors("Falha ao verificar o schema de ensaio; detalhes foram omitidos.")
def verify_plan(config, plan):
    validate_test_schema(config["database"])
    _validate_plan(plan)
    with connect(config) as connection:
        with connection.cursor() as cursor:
            _validate_connected_server(cursor)
            expected_ddl_sha256, _ = _ddl_sha256()
            _assert_schema_compatible(cursor, config["database"], expected_ddl_sha256)
            actual = {}
            mismatches = []
            for table in LOAD_ORDER:
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                actual[table] = cursor.fetchone()[0]
                mismatches.extend(_table_mismatches(cursor, table, plan["tables"][table]))
            cursor.execute(
                "SELECT COUNT(*) FROM inverter_ac_profile p "
                "JOIN inverter_output_mode m ON m.ID=p.OUTPUT_MODE_ID AND m.ACTIVE=1 "
                "WHERE p.ACTIVE=1 AND p.IS_DEFAULT=1 AND p.RATED_ACTIVE_POWER>0 AND ("
                "(p.PROFILE_TYPE='AC_OUTPUT' AND EXISTS (SELECT 1 FROM inverter_system s "
                "WHERE s.INVERTER_ID=p.INVERTER_ID AND UPPER(TRIM(s.SYSTEM_TYPE)) IN ('ON-GRID','GRIDZERO','HYBRID'))) OR "
                "(p.PROFILE_TYPE='EPS_OUTPUT' AND EXISTS (SELECT 1 FROM inverter_system s "
                "WHERE s.INVERTER_ID=p.INVERTER_ID AND UPPER(TRIM(s.SYSTEM_TYPE)) IN ('OFF-GRID','HYBRID'))))"
            )
            actual["ready_profiles"] = cursor.fetchone()[0]
            source = plan["source"]
            plan_sha256 = _plan_sha256(plan)
            cursor.execute(
                "SELECT ID,STATUS,PLAN_SHA256 FROM migration_run "
                "WHERE SOURCE_ID=%s AND SOURCE_SHA256=%s AND SNAPSHOT_SHA256=%s "
                "AND MAPPING_VERSION=%s AND DECISIONS_SHA256=%s",
                (source["source_id"], source["source_sha256"], source["snapshot_sha256"],
                 plan["mapping_version"], plan["decisions_sha256"]),
            )
            run = cursor.fetchone()
            if run is None or run[1] != "COMPLETED" or run[2] != plan_sha256:
                mismatches.append({"table": "migration_run", "reason": "IDENTITY_OR_PLAN_HASH"})
            else:
                run_id = run[0]
                cursor.execute(
                    "SELECT ENTITY_TYPE,SOURCE_KEY,TARGET_ID,CONTENT_SHA256 "
                    "FROM migration_id_map WHERE MIGRATION_RUN_ID=%s "
                    "ORDER BY ENTITY_TYPE,SOURCE_KEY",
                    (run_id,),
                )
                actual_mappings = list(cursor.fetchall())
                expected_mappings = sorted(
                    [(row["ENTITY_TYPE"], row["SOURCE_KEY"], row["TARGET_ID"], row["CONTENT_SHA256"])
                     for row in plan["mappings"]]
                )
                if actual_mappings != expected_mappings:
                    mismatches.append({"table": "migration_id_map", "reason": "CONTENT"})
                cursor.execute(
                    "SELECT SEVERITY,ENTITY_TYPE,SOURCE_KEY,FIELD_NAME,REASON_CODE,DETAILS_JSON "
                    "FROM migration_pending WHERE MIGRATION_RUN_ID=%s ORDER BY ID",
                    (run_id,),
                )
                actual_issues = []
                for severity, entity, source_key, field, reason, details in cursor.fetchall():
                    parsed = json.loads(details) if isinstance(details, str) else details
                    actual_issues.append((severity, entity, source_key, field, reason,
                                          json.dumps(parsed or {}, ensure_ascii=False, sort_keys=True,
                                                     separators=(",", ":"))))
                expected_issues = [
                    (row["severity"], row["entity_type"], row["source_key"], row.get("field"),
                     row["reason_code"],
                     json.dumps(row.get("details", {}), ensure_ascii=False, sort_keys=True,
                                separators=(",", ":")))
                    for row in plan["issues"]
                ]
                if actual_issues != expected_issues:
                    mismatches.append({"table": "migration_pending", "reason": "CONTENT"})
    expected = {key: plan["counts"][key] for key in LOAD_ORDER}
    expected["ready_profiles"] = plan["counts"]["ready_profiles"]
    return {"expected": expected, "actual": actual, "content_mismatches": mismatches,
            "matches": expected == actual and not mismatches}


@_sanitize_database_errors("Falha na troca transacional de perfil; detalhes foram omitidos.")
def switch_default_profile(config, inverter_id, new_profile_id, expected_row_version,
                           *, inject_failure=False):
    """Atomically replace the default output profile with optimistic locking."""
    validate_test_schema(config["database"])
    try:
        expected_version = int(expected_row_version)
    except (TypeError, ValueError):
        raise ValueError("expected_row_version deve ser inteiro.") from None
    with connect(config) as connection:
        try:
            with connection.cursor() as cursor:
                _validate_connected_server(cursor)
                expected_ddl_sha256, _ = _ddl_sha256()
                _assert_schema_compatible(cursor, config["database"], expected_ddl_sha256)
                cursor.execute("SELECT ROW_VERSION FROM inverter WHERE ID=%s FOR UPDATE", (inverter_id,))
                row = cursor.fetchone()
                if row is None:
                    raise RuntimeError("Inversor não encontrado para troca de padrão.")
                if int(row[0]) != expected_version:
                    raise RuntimeError("Conflito de revisão do inversor; nenhuma alteração foi aplicada.")
                cursor.execute(
                    "SELECT p.ACTIVE,p.PROFILE_TYPE,p.RATED_ACTIVE_POWER,p.OUTPUT_MODE_ID,m.ACTIVE "
                    "FROM inverter_ac_profile p "
                    "LEFT JOIN inverter_output_mode m ON m.ID=p.OUTPUT_MODE_ID "
                    "WHERE p.ID=%s AND p.INVERTER_ID=%s FOR UPDATE",
                    (new_profile_id, inverter_id),
                )
                candidate = cursor.fetchone()
                cursor.execute(
                    "SELECT SYSTEM_TYPE FROM inverter_system WHERE INVERTER_ID=%s FOR UPDATE",
                    (inverter_id,),
                )
                system_types = {item[0] for item in cursor.fetchall()}
                if candidate is None or candidate[4] not in (1, True):
                    raise RuntimeError("Perfil substituto não é uma saída ativa válida.")
                profile = {
                    "PROFILE_TYPE": candidate[1], "ACTIVE": candidate[0],
                    "RATED_ACTIVE_POWER": candidate[2], "OUTPUT_MODE_ID": candidate[3],
                }
                try:
                    validate_output_profile(profile, system_types)
                except DomainValidationError:
                    raise RuntimeError("Perfil substituto não é uma saída ativa válida.") from None
                cursor.execute("UPDATE inverter_ac_profile SET IS_DEFAULT=0,ROW_VERSION=ROW_VERSION+1 WHERE INVERTER_ID=%s AND IS_DEFAULT=1",
                               (inverter_id,))
                if inject_failure:
                    raise RuntimeError("Falha injetada durante troca de padrão.")
                cursor.execute("UPDATE inverter_ac_profile SET IS_DEFAULT=1,ROW_VERSION=ROW_VERSION+1 WHERE ID=%s",
                               (new_profile_id,))
                cursor.execute("UPDATE inverter SET ROW_VERSION=ROW_VERSION+1 WHERE ID=%s AND ROW_VERSION=%s",
                               (inverter_id, expected_version))
                if cursor.rowcount != 1:
                    raise RuntimeError("Conflito de revisão do inversor; nenhuma alteração foi aplicada.")
            connection.commit()
            return expected_version + 1
        except Exception:
            connection.rollback()
            raise

