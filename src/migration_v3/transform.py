import hashlib
import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation

from .domain import (
    DomainValidationError,
    UINT64_MAX,
    decode_group,
    output_profile_is_ready,
    validate_output_profile,
)
from .integrity import plan_sha256
from .normalization import normalized_key


KNOWN_NULL_SENTINELS = {
    ("mppt", "MAX_FULL_LOAD_VOLTAGE"),
    ("mppt", "MIN_FULL_LOAD_VOLTAGE"),
    ("mppt", "RATED_INPUT_VOLTAGE"),
}
DECIMAL_SPECS = {
    **{("inverter", field): (10, 2) for field in
       ("DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT")},
    **{("inverter", field): (6, 2) for field in
       ("MAX_OPERATING_TEMPERATURE", "MIN_OPERATING_TEMPERATURE")},
    ("inverter", "OVERLOAD"): (7, 2),
    **{("inverter", field): (12, 2) for field in
       ("RATED_ACTIVE_POWER", "MAX_ACTIVE_POWER")},
    **{("inverter", field): (10, 2) for field in
       ("RATED_OUTPUT_VOLTAGE", "RATED_OUTPUT_CURRENT", "MAX_OUTPUT_CURRENT")},
    **{("module", field): (10, 2) for field in
       ("DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT", "VMPP", "IMPP", "VOC", "ISC")},
    ("module", "WP"): (12, 2),
    **{("module", field): (8, 5) for field in ("COEF_PMAX", "COEF_VOC", "COEF_ISC")},
    **{("mppt", field): (10, 2) for field in (
        "MAX_INPUT_VOLTAGE", "MIN_STARTUP_VOLTAGE", "MAX_OPERATING_VOLTAGE",
        "MIN_OPERATING_VOLTAGE", "MAX_FULL_LOAD_VOLTAGE", "MIN_FULL_LOAD_VOLTAGE",
        "RATED_INPUT_VOLTAGE", "MAX_SHORT_CIRCUIT_CURRENT", "MAX_OPERATING_CURRENT",
    )},
    **{("reconciliation", field): (12, 2) for field in
       ("RATED_ACTIVE_POWER", "MAX_ACTIVE_POWER")},
    **{("reconciliation", field): (10, 2) for field in (
        "RATED_CURRENT", "MAX_CURRENT", "RATED_LINE_TO_LINE_VOLTAGE",
        "RATED_LINE_TO_NEUTRAL_VOLTAGE",
    )},
}


def _decimal(value, table=None, field=None):
    if value is None or ((table, field) in KNOWN_NULL_SENTINELS and value == -1):
        return None
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Valor decimal inválido: {table}.{field}={value!r}")
    if not decimal_value.is_finite():
        raise ValueError(f"Valor decimal não finito: {table}.{field}")
    spec = DECIMAL_SPECS.get((table, field))
    if spec:
        precision, scale = spec
        quantum = Decimal(1).scaleb(-scale)
        try:
            exact = decimal_value.quantize(quantum)
        except InvalidOperation:
            raise ValueError(f"Valor decimal fora do domínio: {table}.{field}") from None
        if exact != decimal_value or abs(decimal_value) >= Decimal(10) ** (precision - scale):
            raise ValueError(f"Valor decimal excede precisão/escala: {table}.{field}")
    return format(decimal_value, "f")


def _issue(severity, entity, key, reason, field=None, details=None):
    return {"severity": severity, "entity_type": entity, "source_key": str(key),
            "field": field, "reason_code": reason, "details": details or {}}


def _safe_decimal(value, table, field, issues, entity, key):
    try:
        return _decimal(value, table, field)
    except ValueError:
        issues.append(_issue("ERROR", entity, key, "INVALID_DECIMAL", field))
        return None


def _copy_decimal_row(row, fields, table, issues, key):
    result = dict(row)
    for field in fields:
        result[field] = _safe_decimal(result.get(field), table, field, issues, table, key)
    return result


def _validate_target_constraints(tables, issues):
    nonnegative = {
        "inverter": ("DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT", "OVERLOAD",
                     "MAX_EFFICIENCY", "EURO_EFFICIENCY"),
        "module": ("DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT", "WP", "VMPP",
                   "IMPP", "VOC", "ISC"),
        "mppt": ("MAX_INPUT_VOLTAGE", "MIN_STARTUP_VOLTAGE", "MAX_OPERATING_VOLTAGE",
                 "MIN_OPERATING_VOLTAGE", "MAX_FULL_LOAD_VOLTAGE", "MIN_FULL_LOAD_VOLTAGE",
                 "RATED_INPUT_VOLTAGE", "MAX_SHORT_CIRCUIT_CURRENT_PER_MPPT",
                 "MAX_SHORT_CIRCUIT_CURRENT_PER_STRING", "MAX_OPERATING_CURRENT_PER_MPPT",
                 "MAX_OPERATING_CURRENT_PER_STRING"),
        "inverter_ac_profile": ("RATED_ACTIVE_POWER", "MAX_ACTIVE_POWER", "MAX_PEAK_ACTIVE_POWER",
                                "RATED_LINE_TO_LINE_VOLTAGE", "RATED_LINE_TO_NEUTRAL_VOLTAGE",
                                "RATED_CURRENT", "MAX_CURRENT", "SWITCHING_TIME"),
        "inverter_battery": ("BATTERY_VOLTAGE_MIN", "BATTERY_VOLTAGE_MAX", "MAX_CHARGE_CURRENT",
                             "MAX_DISCHARGE_CURRENT"),
    }
    for table, fields in nonnegative.items():
        for row in tables[table]:
            for field in fields:
                value = row.get(field)
                if value is not None and Decimal(str(value)) < 0:
                    issues.append(_issue("ERROR", table, row["ID"], "NEGATIVE_VALUE", field))

    boolean_fields = {
        "inverter": ("ACTIVE",), "module": ("ACTIVE",),
        "inverter_output_mode": ("ACTIVE",),
        "inverter_ac_profile": ("ACTIVE", "IS_DEFAULT"),
        "inverter_battery": ("ACTIVE",),
    }
    for table, fields in boolean_fields.items():
        for row in tables[table]:
            for field in fields:
                if row.get(field) not in (0, 1, False, True):
                    issues.append(_issue("ERROR", table, row["ID"], "INVALID_BOOLEAN", field))

    for row in tables["manufacturer"]:
        if row["CATEGORY"] not in (0, 1, 2):
            issues.append(_issue("ERROR", "manufacturer", row["ID"], "INVALID_CATEGORY", "CATEGORY"))
    for row in tables["inverter"]:
        minimum = row.get("MIN_OPERATING_TEMPERATURE")
        maximum = row.get("MAX_OPERATING_TEMPERATURE")
        if minimum is not None and maximum is not None and Decimal(minimum) > Decimal(maximum):
            issues.append(_issue("ERROR", "inverter", row["ID"], "INVALID_TEMPERATURE_RANGE"))
        for field in ("NUMBER_OF_TRACKERS", "NUMBER_OF_INPUTS", "NUMBER_OF_BATTERY_INPUTS"):
            value = row.get(field)
            if value is not None and (type(value) is not int or not 0 <= value <= 65535):
                issues.append(_issue("ERROR", "inverter", row["ID"], "UNSIGNED_RANGE_ERROR", field))
    for row in tables["mppt"]:
        inputs = row.get("NUMBER_OF_INPUTS")
        if inputs is not None and (type(inputs) is not int or not 0 <= inputs <= 65535):
            issues.append(_issue("ERROR", "mppt", row["ID"], "UNSIGNED_RANGE_ERROR",
                                 "NUMBER_OF_INPUTS"))
        for minimum_field, maximum_field in (
            ("MIN_OPERATING_VOLTAGE", "MAX_OPERATING_VOLTAGE"),
            ("MIN_FULL_LOAD_VOLTAGE", "MAX_FULL_LOAD_VOLTAGE"),
        ):
            minimum = row.get(minimum_field)
            maximum = row.get(maximum_field)
            if minimum is not None and maximum is not None and Decimal(minimum) > Decimal(maximum):
                issues.append(_issue("ERROR", "mppt", row["ID"], "INVALID_VOLTAGE_RANGE",
                                     minimum_field))
    for row in tables["inverter_ac_profile"]:
        if row["IS_DEFAULT"] and (not row["ACTIVE"] or row["PROFILE_TYPE"] == "AC_INPUT"):
            issues.append(_issue("ERROR", "ac_profile", row["ID"], "INVALID_DEFAULT_PROFILE"))
        if row["PROFILE_TYPE"] == "AC_INPUT":
            if row["OUTPUT_MODE_ID"] is not None or row["IS_DEFAULT"]:
                issues.append(_issue("ERROR", "ac_profile", row["ID"], "INVALID_AC_INPUT_MODE"))
        elif row["ACTIVE"] and row["OUTPUT_MODE_ID"] is None:
            issues.append(_issue("ERROR", "ac_profile", row["ID"], "ACTIVE_OUTPUT_WITHOUT_MODE"))

    systems_by_inverter = defaultdict(set)
    for row in tables["inverter_system"]:
        systems_by_inverter[row["INVERTER_ID"]].add(
            str(row["SYSTEM_TYPE"]).strip().upper()
        )
    active_modes = {row["ID"] for row in tables["inverter_output_mode"] if row["ACTIVE"]}
    for row in tables["inverter_ac_profile"]:
        if not row["ACTIVE"] or row["PROFILE_TYPE"] not in {"AC_OUTPUT", "EPS_OUTPUT"}:
            continue
        systems = systems_by_inverter[row["INVERTER_ID"]]
        try:
            validate_output_profile(row, systems)
        except DomainValidationError:
            if not systems:
                reason = "ACTIVE_OUTPUT_MISSING_SYSTEM_CLASSIFICATION"
            elif ((row["PROFILE_TYPE"] == "AC_OUTPUT"
                   and not systems.intersection({"ON-GRID", "GRIDZERO", "HYBRID"}))
                  or (row["PROFILE_TYPE"] == "EPS_OUTPUT"
                      and not systems.intersection({"OFF-GRID", "HYBRID"}))):
                reason = "ACTIVE_OUTPUT_SYSTEM_INCOMPATIBLE"
            else:
                continue
            issues.append(_issue("ERROR", "ac_profile", row["ID"], reason,
                                 details={"inverter_id": row["INVERTER_ID"]}))
        if row["OUTPUT_MODE_ID"] is not None and row["OUTPUT_MODE_ID"] not in active_modes:
            issues.append(_issue("ERROR", "ac_profile", row["ID"],
                                 "ACTIVE_OUTPUT_WITH_INACTIVE_MODE"))


def build_plan(source, source_meta, decisions, decisions_sha256):
    tables = source["tables"]
    issues = []
    if source["integrity"] != "ok":
        issues.append(_issue("ERROR", "database", "sqlite", "INTEGRITY_CHECK_FAILED",
                             details={"result": source["integrity"]}))
    for item in source["foreign_key_issues"]:
        issues.append(_issue("ERROR", "database", "sqlite", "FOREIGN_KEY_VIOLATION", details=item))

    manufacturers = []
    seen_manufacturers = {}
    for row in tables["manufacturer"]:
        key = normalized_key(row["NAME"])
        if key in seen_manufacturers:
            issues.append(_issue("ERROR", "manufacturer", row["ID"], "NORMALIZED_NAME_COLLISION",
                                 "NAME", {"other_id": seen_manufacturers[key]}))
        seen_manufacturers[key] = row["ID"]
        manufacturers.append({"ID": row["ID"], "NAME": row["NAME"], "CATEGORY": row["CATEGORY"]})

    inverter_decimal = (
        "DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT", "OVERLOAD",
        "MAX_OPERATING_TEMPERATURE", "MIN_OPERATING_TEMPERATURE",
    )
    inverters = []
    seen_equipment = {}
    for row in tables["inverter"]:
        key = (row["MANUFACTURER_ID"], normalized_key(row["MODEL"]))
        if key in seen_equipment:
            issues.append(_issue("ERROR", "inverter", row["ID"], "NORMALIZED_MODEL_COLLISION",
                                 "MODEL", {"other_id": seen_equipment[key]}))
        seen_equipment[key] = row["ID"]
        item = {field: row.get(field) for field in (
            "ID", "MODEL", "MANUFACTURER_ID", "DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH",
            "DIM_WEIGHT", "MAX_OPERATING_TEMPERATURE", "MIN_OPERATING_TEMPERATURE",
            "COOLING_MODE", "PROTECTION_DEGREE", "TOPOLOGY", "OVERLOAD",
            "NUMBER_OF_TRACKERS", "NUMBER_OF_INPUTS", "ACTIVE",
        )}
        item = _copy_decimal_row(item, inverter_decimal, "inverter", issues, row["ID"])
        item.update({"NUMBER_OF_BATTERY_INPUTS": None, "MAX_EFFICIENCY": None,
                     "EURO_EFFICIENCY": None, "ROW_VERSION": 1})
        inverters.append(item)

    module_decimal = ("DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT", "WP", "VMPP",
                      "IMPP", "VOC", "ISC", "COEF_PMAX", "COEF_VOC", "COEF_ISC")
    modules = []
    seen_equipment = {}
    for row in tables["module"]:
        key = (row["MANUFACTURER_ID"], normalized_key(row["MODEL"]))
        if key in seen_equipment:
            issues.append(_issue("ERROR", "module", row["ID"], "NORMALIZED_MODEL_COLLISION",
                                 "MODEL", {"other_id": seen_equipment[key]}))
        seen_equipment[key] = row["ID"]
        item = dict(row)
        item = _copy_decimal_row(item, module_decimal, "module", issues, row["ID"])
        item["ROW_VERSION"] = 1
        modules.append(item)

    inverter_by_id = {row["ID"]: row for row in tables["inverter"]}
    groups_by_inverter = defaultdict(list)
    mppts = []
    for row in tables["mppt"]:
        groups_by_inverter[row["INVERTER_ID"]].append(row)
        fields = ("MAX_INPUT_VOLTAGE", "MIN_STARTUP_VOLTAGE", "MAX_OPERATING_VOLTAGE",
                  "MIN_OPERATING_VOLTAGE", "MAX_FULL_LOAD_VOLTAGE", "MIN_FULL_LOAD_VOLTAGE",
                  "RATED_INPUT_VOLTAGE", "MAX_SHORT_CIRCUIT_CURRENT", "MAX_OPERATING_CURRENT")
        values = _copy_decimal_row(row, fields, "mppt", issues, row["ID"])
        mppts.append({
            "ID": values["ID"], "INVERTER_ID": values["INVERTER_ID"],
            "MPPT_INDEX": values["MPPT_INDEX"], "NUMBER_OF_INPUTS": values["NUMBER_OF_INPUTS"],
            "MAX_INPUT_VOLTAGE": values["MAX_INPUT_VOLTAGE"],
            "MIN_STARTUP_VOLTAGE": values["MIN_STARTUP_VOLTAGE"],
            "MAX_OPERATING_VOLTAGE": values["MAX_OPERATING_VOLTAGE"],
            "MIN_OPERATING_VOLTAGE": values["MIN_OPERATING_VOLTAGE"],
            "MAX_FULL_LOAD_VOLTAGE": values["MAX_FULL_LOAD_VOLTAGE"],
            "MIN_FULL_LOAD_VOLTAGE": values["MIN_FULL_LOAD_VOLTAGE"],
            "RATED_INPUT_VOLTAGE": values["RATED_INPUT_VOLTAGE"],
            "MAX_SHORT_CIRCUIT_CURRENT_PER_MPPT": values["MAX_SHORT_CIRCUIT_CURRENT"],
            "MAX_SHORT_CIRCUIT_CURRENT_PER_STRING": None,
            "MAX_OPERATING_CURRENT_PER_MPPT": values["MAX_OPERATING_CURRENT"],
            "MAX_OPERATING_CURRENT_PER_STRING": None,
        })
    for inverter_id, groups in groups_by_inverter.items():
        parent = inverter_by_id.get(inverter_id)
        if parent is None:
            for group in groups:
                issues.append(_issue("ERROR", "mppt", group["ID"], "ORPHAN_INVERTER_REFERENCE",
                                     "INVERTER_ID"))
            continue
        try:
            tracker_count = int(parent["NUMBER_OF_TRACKERS"])
            declared_inputs = int(parent["NUMBER_OF_INPUTS"])
        except (TypeError, ValueError):
            issues.append(_issue("ERROR", "inverter", inverter_id, "INVALID_MPPT_TOTALS"))
            continue
        if tracker_count < 1 or declared_inputs < 0:
            issues.append(_issue("ERROR", "inverter", inverter_id, "INVALID_MPPT_TOTALS"))
            continue
        occupied = set()
        seen_codes = set()
        all_valid = True
        weighted_inputs = 0
        for group in groups:
            try:
                code = int(group["MPPT_INDEX"])
            except (TypeError, ValueError, OverflowError):
                all_valid = False
                issues.append(_issue("ERROR", "mppt", group["ID"], "INVALID_GROUP_INDEX",
                                     "MPPT_INDEX", {"value": group["MPPT_INDEX"],
                                                    "declared_tracker_count": tracker_count}))
                continue
            if code in seen_codes:
                issues.append(_issue("ERROR", "mppt", group["ID"], "DUPLICATE_GROUP_INDEX"))
            seen_codes.add(code)
            try:
                positions = decode_group(code, tracker_count)
            except ValueError as error:
                all_valid = False
                issues.append(_issue("ERROR", "mppt", group["ID"], "INVALID_GROUP_INDEX",
                                     "MPPT_INDEX", {"message": str(error), "value": code,
                                                    "declared_tracker_count": tracker_count}))
                continue
            overlap = occupied & positions
            if overlap:
                issues.append(_issue("ERROR", "mppt", group["ID"], "OVERLAPPING_GROUPS",
                                     "MPPT_INDEX", {"positions": sorted(overlap)}))
            occupied |= positions
            try:
                weighted_inputs += len(positions) * int(group["NUMBER_OF_INPUTS"])
            except (TypeError, ValueError, OverflowError):
                all_valid = False
                issues.append(_issue("ERROR", "mppt", group["ID"], "INVALID_INPUT_COUNT",
                                     "NUMBER_OF_INPUTS"))
        if all_valid and occupied != set(range(1, tracker_count + 1)):
            issues.append(_issue("ERROR", "inverter", inverter_id, "INCOMPLETE_MPPT_COVERAGE",
                                 "NUMBER_OF_TRACKERS", {"covered": sorted(occupied),
                                                        "declared_tracker_count": tracker_count}))
        if all_valid and weighted_inputs != declared_inputs:
            issues.append(_issue("ERROR", "inverter", inverter_id, "MPPT_INPUT_TOTAL_MISMATCH",
                                 "NUMBER_OF_INPUTS", {"computed": weighted_inputs,
                                                      "declared": declared_inputs}))
    for inverter_id in sorted(set(inverter_by_id) - set(groups_by_inverter)):
        issues.append(_issue("PENDING", "inverter", inverter_id, "MISSING_MPPT_GROUPS"))

    modes_by_inverter = defaultdict(list)
    all_modes = set()
    seen_mode_pairs = set()
    for row in tables["inverter_output_mode"]:
        mode = row["OUTPUT_MODE"]
        pair = (row["INVERTER_ID"], mode)
        if pair in seen_mode_pairs:
            issues.append(_issue("ERROR", "inverter_output_mode", row["ID"],
                                 "DUPLICATE_INVERTER_OUTPUT_MODE"))
        seen_mode_pairs.add(pair)
        modes_by_inverter[row["INVERTER_ID"]].append(mode)
        all_modes.add(mode)
    output_modes = [{"ID": index, "OUTPUT_MODE": mode, "ACTIVE": 1}
                    for index, mode in enumerate(sorted(all_modes), 1)]
    normalized_modes = {}
    for row in output_modes:
        normalized = normalized_key(row["OUTPUT_MODE"])
        if normalized in normalized_modes:
            issues.append(_issue("ERROR", "inverter_output_mode", row["ID"],
                                 "NORMALIZED_OUTPUT_MODE_COLLISION", "OUTPUT_MODE",
                                 {"other_id": normalized_modes[normalized]}))
        normalized_modes[normalized] = row["ID"]
    output_mode_ids = {row["OUTPUT_MODE"]: row["ID"] for row in output_modes}

    profiles = []
    mappings = []
    profile_id = 1
    for legacy in tables["inverter"]:
        modes = sorted(set(modes_by_inverter[legacy["ID"]]))
        if not modes:
            issues.append(_issue("ERROR", "inverter", legacy["ID"], "MISSING_OUTPUT_MODE"))
        multi = len(modes) > 1
        chosen_defaults = 0
        active_outputs = 0
        for mode in modes:
            source_key = f"{legacy['ID']}:{mode}"
            decision = decisions.get((legacy["ID"], mode), {})
            corrections = decision.get("corrections", {})
            reference = decision.get("voltage_reference", "UNRESOLVED")
            voltage = _safe_decimal(legacy.get("RATED_OUTPUT_VOLTAGE"), "inverter",
                                    "RATED_OUTPUT_VOLTAGE", issues, "ac_profile", source_key)
            line_line = voltage if reference == "LINE_TO_LINE" else None
            line_neutral = voltage if reference == "LINE_TO_NEUTRAL" else None
            rated_power = _safe_decimal(legacy.get("RATED_ACTIVE_POWER"), "inverter",
                                        "RATED_ACTIVE_POWER", issues, "ac_profile", source_key)
            minimum_ok = rated_power is not None and Decimal(rated_power) > 0
            active = bool(decision.get("active", not multi and minimum_ok))
            is_default = bool(decision.get("is_default", not multi and active))
            if is_default:
                active = True
            profile = {
                "ID": profile_id, "INVERTER_ID": legacy["ID"], "PROFILE_TYPE": "AC_OUTPUT",
                "OUTPUT_MODE_ID": output_mode_ids[mode],
                "RATED_ACTIVE_POWER": rated_power,
                "MAX_ACTIVE_POWER": _safe_decimal(legacy.get("MAX_ACTIVE_POWER"), "inverter",
                                                   "MAX_ACTIVE_POWER", issues, "ac_profile", source_key),
                "MAX_PEAK_ACTIVE_POWER": None,
                "RATED_LINE_TO_LINE_VOLTAGE": line_line,
                "RATED_LINE_TO_NEUTRAL_VOLTAGE": line_neutral,
                "RATED_CURRENT": _safe_decimal(legacy.get("RATED_OUTPUT_CURRENT"), "inverter",
                                                "RATED_OUTPUT_CURRENT", issues, "ac_profile", source_key),
                "MAX_CURRENT": _safe_decimal(legacy.get("MAX_OUTPUT_CURRENT"), "inverter",
                                              "MAX_OUTPUT_CURRENT", issues, "ac_profile", source_key),
                "SWITCHING_TIME": None, "ACTIVE": int(active), "IS_DEFAULT": int(is_default),
                "ROW_VERSION": 1,
            }
            for field, value in corrections.items():
                profile[field] = _safe_decimal(value, "reconciliation", field, issues,
                                               "ac_profile", source_key)
            minimum_ok = (
                profile["RATED_ACTIVE_POWER"] is not None
                and Decimal(profile["RATED_ACTIVE_POWER"]) > 0
            )
            if not multi and "active" not in decision:
                profile["ACTIVE"] = int(minimum_ok)
            if not multi and "is_default" not in decision:
                profile["IS_DEFAULT"] = int(bool(profile["ACTIVE"]))
            if profile["IS_DEFAULT"]:
                profile["ACTIVE"] = 1
                chosen_defaults += 1
            if profile["ACTIVE"]:
                active_outputs += 1
            review_complete = "active" in decision and "is_default" in decision
            profiles.append(profile)
            content_hash = hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest()
            mappings.append({"ENTITY_TYPE": "ac_profile", "SOURCE_KEY": source_key,
                             "TARGET_ID": profile_id, "CONTENT_SHA256": content_hash})
            if reference == "UNRESOLVED" and voltage is not None:
                issues.append(_issue("PENDING", "ac_profile", source_key,
                                     "VOLTAGE_REFERENCE_UNRESOLVED", "RATED_OUTPUT_VOLTAGE",
                                     {"legacy_value": voltage, "legacy_unit": "V",
                                      "legacy_column": "inverter.RATED_OUTPUT_VOLTAGE"}))
            if multi and not review_complete:
                issues.append(_issue("PENDING", "ac_profile", source_key,
                                     "MULTIMODE_PROFILE_REVIEW_REQUIRED"))
            if profile["ACTIVE"] and not minimum_ok:
                issues.append(_issue("ERROR", "ac_profile", source_key,
                                     "ACTIVE_PROFILE_MISSING_NOMINAL_OUTPUT_POWER",
                                     "RATED_ACTIVE_POWER"))
            elif not minimum_ok:
                issues.append(_issue("PENDING", "ac_profile", source_key,
                                     "MISSING_NOMINAL_OUTPUT_POWER", "RATED_ACTIVE_POWER"))
            profile_id += 1
        if chosen_defaults > 1:
            issues.append(_issue("ERROR", "inverter", legacy["ID"], "MULTIPLE_DEFAULT_PROFILES"))
        elif active_outputs and chosen_defaults == 0:
            issues.append(_issue("PENDING", "inverter", legacy["ID"], "MISSING_DEFAULT_PROFILE"))

    systems_by_inverter = defaultdict(set)
    for row in tables["inverter_system"]:
        systems_by_inverter[row["INVERTER_ID"]].add(
            str(row["SYSTEM_TYPE"]).strip().upper()
        )
    for (inverter_id, mode), decision in decisions.items():
        if (inverter_id not in inverter_by_id or mode not in modes_by_inverter[inverter_id]):
            issues.append(_issue("ERROR", "reconciliation", f"{inverter_id}:{mode}",
                                 "UNKNOWN_PROFILE_REFERENCE"))

    plan_tables = {
        "manufacturer": manufacturers,
        "inverter": inverters,
        "module": modules,
        "mppt": mppts,
        "inverter_output_mode": output_modes,
        "inverter_ac_profile": profiles,
        "inverter_battery": [],
        "inverter_system": tables["inverter_system"],
        "inverter_communication": tables["inverter_communication"],
    }
    _validate_target_constraints(plan_tables, issues)
    counts = {name: len(rows) for name, rows in plan_tables.items()}
    systems_by_inverter = defaultdict(set)
    for row in plan_tables["inverter_system"]:
        systems_by_inverter[row["INVERTER_ID"]].add(
            str(row["SYSTEM_TYPE"]).strip().upper()
        )
    active_output_modes = {
        row["ID"] for row in plan_tables["inverter_output_mode"] if row["ACTIVE"]
    }
    counts["ready_profiles"] = sum(
        output_profile_is_ready(row, systems_by_inverter.get(row["INVERTER_ID"], set()),
                                active_output_modes)
        for row in profiles
    )
    counts["pending"] = sum(item["severity"] == "PENDING" for item in issues)
    counts["errors"] = sum(item["severity"] == "ERROR" for item in issues)
    plan = {
        "format_version": 1, "mapping_version": "0001", "source": source_meta,
        "decisions_sha256": decisions_sha256, "counts": counts,
        "tables": plan_tables, "mappings": mappings, "issues": issues,
    }
    plan["plan_sha256"] = plan_sha256(plan)
    return plan

