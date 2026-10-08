"""Adaptador puro entre o contexto v2 da tela principal e o núcleo v3."""

from __future__ import annotations

import math

from calculation_core import (
    CalculationOptions,
    CalculationRequest,
    InverterInput,
    ModuleInput,
    MPPTGroup,
    OutputProfile,
    ProfileType,
    calculate,
)
from optimus_lib import mppt_index_dec, vv


def _optional_legacy(value):
    return None if value == -1 else value


def _group_count(index, tracker_count):
    return tracker_count if index == 0 else len(mppt_index_dec(index))


def _legacy_profile_type(system_types):
    normalized = {str(value).strip().upper() for value in system_types}
    if "OFF-GRID" in normalized and not normalized.intersection({"ON-GRID", "GRIDZERO", "HYBRID"}):
        return ProfileType.EPS_OUTPUT
    return ProfileType.AC_OUTPUT


def build_legacy_main_calculations(
    inverter_data,
    module_data,
    *,
    minimum_cell_temperature_c,
    maximum_cell_temperature_c,
    operating_current_tolerance_fraction,
    power_tolerance_fraction,
    effective_overload_fraction,
    ignore_operating_current=False,
    ignore_full_load=False,
):
    """Produz o dicionário consumido pelos cartões e gráficos históricos.

    O fechamento otimizado do núcleo permanece disponível no resultado interno,
    mas esta projeção conserva a agregação e o arredondamento aprovados na tela
    principal v2, inclusive a semântica particular de ``ignore_full_load``.
    """
    tracker_count = inverter_data["NUMBER_OF_TRACKERS"]
    groups = tuple(
        MPPTGroup(
            group_id=item.get("ID"),
            index=item["MPPT_INDEX"],
            count=_group_count(item["MPPT_INDEX"], tracker_count),
            number_of_inputs=item["NUMBER_OF_INPUTS"],
            max_input_voltage_v=item["MAX_INPUT_VOLTAGE"],
            min_startup_voltage_v=item["MIN_STARTUP_VOLTAGE"],
            max_operating_voltage_v=item["MAX_OPERATING_VOLTAGE"],
            min_operating_voltage_v=item["MIN_OPERATING_VOLTAGE"],
            max_short_circuit_current_per_mppt_a=item["MAX_SHORT_CIRCUIT_CURRENT"],
            max_operating_current_per_mppt_a=_optional_legacy(item["MAX_OPERATING_CURRENT"]),
            min_full_load_voltage_v=_optional_legacy(item["MIN_FULL_LOAD_VOLTAGE"]),
            max_full_load_voltage_v=_optional_legacy(item["MAX_FULL_LOAD_VOLTAGE"]),
            rated_input_voltage_v=_optional_legacy(item.get("RATED_INPUT_VOLTAGE")),
            source="sqlite-v2-main-adapter",
        )
        for item in inverter_data["MPPT"]
    )
    system_types = tuple(inverter_data.get("SYSTEM_TYPE") or ("ON-GRID",))
    inverter = InverterInput(
        inverter_id=inverter_data.get("ID"),
        manufacturer=inverter_data.get("MANUFACTURER_NAME", ""),
        model=inverter_data.get("MODEL", ""),
        overload_percent=effective_overload_fraction * 100,
        mppt_groups=groups,
        system_types=system_types,
        active=bool(inverter_data.get("ACTIVE", True)),
        source="sqlite-v2-main-adapter",
    )
    module = ModuleInput(
        module_id=module_data.get("ID"),
        manufacturer=module_data.get("MANUFACTURER_NAME", ""),
        model=module_data.get("MODEL", ""),
        nominal_power_w=module_data["WP"],
        vmpp_v=module_data["VMPP"],
        impp_a=module_data["IMPP"],
        voc_v=module_data["VOC"],
        isc_a=module_data["ISC"],
        coef_voc_percent_c=module_data["COEF_VOC"],
        coef_isc_percent_c=module_data["COEF_ISC"],
        coef_pmax_percent_c=module_data["COEF_PMAX"],
        active=bool(module_data.get("ACTIVE", True)),
        source="sqlite-v2-main-adapter",
    )
    profile = OutputProfile(
        profile_id=None,
        inverter_id=inverter.inverter_id,
        profile_type=_legacy_profile_type(system_types),
        rated_active_power_w=inverter_data["RATED_ACTIVE_POWER"],
        output_mode="LEGACY_CA_FIELDS",
        active=True,
        is_default=True,
        source="legacy-rated-active-power",
    )
    options = CalculationOptions(
        ignore_operating_current=ignore_operating_current,
        custom_overload_percent=effective_overload_fraction * 100,
        # Os gráficos legados sempre precisam dos limites de plena carga. A flag
        # altera somente a projeção agregada abaixo, como fazia a tela v2.
        enforce_full_load=True,
        min_cell_temperature_c=minimum_cell_temperature_c,
        max_cell_temperature_c=maximum_cell_temperature_c,
        operating_current_tolerance=operating_current_tolerance_fraction,
        power_tolerance=power_tolerance_fraction,
    )
    result = calculate(CalculationRequest(inverter, module, profile, options))
    if result.thermal is None:
        details = "; ".join(issue.field or issue.code.value for issue in result.issues)
        raise ValueError(f"Dados insuficientes para o cálculo: {details}")

    thermal = result.thermal
    module_result = {
        "p_nom": module.nominal_power_w,
        "coef_pmax": module.coef_pmax_percent_c / 100,
        "coef_voc": module.coef_voc_percent_c / 100,
        "coef_isc": module.coef_isc_percent_c / 100,
        "p_min": thermal.power_min_w,
        "p_max": thermal.power_max_w,
        "vmpp_min": thermal.vmpp_min_v,
        "vmpp_max": thermal.vmpp_max_v,
        "voc_min": thermal.voc_min_v,
        "voc_max": thermal.voc_max_v,
        "isc_min": thermal.isc_min_a,
        "isc_max": thermal.isc_max_a,
        "impp_min": thermal.impp_min_a,
        "impp_max": thermal.impp_max_a,
    }

    limits_by_group = {}
    for item in result.mppt_limits:
        limits_by_group.setdefault(item.group_id, item)
    mppt_results = []
    for source, group in zip(inverter_data["MPPT"], groups):
        limits = limits_by_group[group.group_id]
        string_limit = limits.string_limit
        if string_limit > 0:
            input_min, input_max = limits.input_series_minimum, limits.input_series_maximum
            operation_min, operation_max = limits.operating_series_minimum, limits.operating_series_maximum
            full_min = limits.full_load_series_minimum if limits.full_load_series_minimum is not None else -1
            full_max = limits.full_load_series_maximum if limits.full_load_series_maximum is not None else -1
        else:
            input_min = input_max = operation_min = operation_max = full_min = full_max = 0

        if vv(input_min, operation_min, input_max, operation_max):
            operation_series_minimum = max(input_min, operation_min)
            operation_series_maximum = min(input_max, operation_max)
            operation_quantity = operation_series_maximum * string_limit
            operation_power = operation_quantity * module.nominal_power_w / 1000
        else:
            operation_series_minimum = operation_series_maximum = operation_quantity = operation_power = -1
        if vv(operation_series_minimum, operation_series_maximum, full_min, full_max):
            full_series_minimum = max(input_min, operation_min, full_min)
            full_series_maximum = min(input_max, operation_max, full_max)
            full_quantity = full_series_maximum * string_limit
            full_power = full_quantity * module.nominal_power_w / 1000
        else:
            full_series_minimum = full_series_maximum = full_quantity = full_power = -1

        mppt_results.append({
            "mppt_index": source["MPPT_INDEX"], "n_in_mppt": source["NUMBER_OF_INPUTS"],
            "max_i_v": source["MAX_INPUT_VOLTAGE"], "min_i_v": source["MIN_STARTUP_VOLTAGE"],
            "max_o_v": source["MAX_OPERATING_VOLTAGE"], "min_o_v": source["MIN_OPERATING_VOLTAGE"],
            "max_fl_v": source["MAX_FULL_LOAD_VOLTAGE"], "min_fl_v": source["MIN_FULL_LOAD_VOLTAGE"],
            "max_sc_i": source["MAX_SHORT_CIRCUIT_CURRENT"], "max_o_i": source["MAX_OPERATING_CURRENT"],
            "n_min_in": input_min, "n_max_in": input_max,
            "n_min_o": operation_min, "n_max_o": operation_max,
            "n_min_fl": full_min, "n_max_fl": full_max,
            "q_min_o": operation_series_minimum, "q_max_o": operation_series_maximum,
            "q_min_fl": full_series_minimum, "q_max_fl": full_series_maximum,
            "n_max_sc_mppt": limits.short_circuit_limit,
            "n_max_o_mppt": limits.operating_current_limit if limits.operating_current_limit is not None else -1,
            "q_s_mppt": string_limit,
            "n_mod_o_mppt": operation_quantity, "p_mod_o_mppt": operation_power,
            "n_mod_fl_mppt": full_quantity, "p_mod_fl_mppt": full_power,
        })

    inverter_result = {
        "n_tr": tracker_count,
        "sb": effective_overload_fraction,
        "pn": inverter_data["RATED_ACTIVE_POWER"],
        "n_in": inverter_data["NUMBER_OF_INPUTS"],
    }
    for mppt, group in zip(mppt_results, groups):
        multiplier = group.count
        for target, source_key in (("n_max_in", "n_max_in"), ("n_max_o", "n_max_o"), ("n_max_fl", "n_max_fl")):
            value = mppt[source_key]
            if vv(value, mppt["q_s_mppt"]):
                if inverter_result.get(target) != -1:
                    inverter_result[target] = inverter_result.get(target, 0) + value * multiplier * mppt["q_s_mppt"]
            else:
                inverter_result[target] = -1

    inverter_result["n_max_sb"] = result.overload_limit
    operation_candidates = [inverter_result["n_max_in"], inverter_result["n_max_sb"]] if ignore_full_load else [inverter_result["n_max_in"], inverter_result["n_max_o"], inverter_result["n_max_sb"]]
    inverter_result["q_max_o"] = min(operation_candidates) if [value for value in operation_candidates if value != -1 and value is not None] else -1
    if vv(inverter_result["q_max_o"]):
        inverter_result["p_max_sb_o"] = round(module.nominal_power_w * inverter_result["q_max_o"] / 1000, 1)
        inverter_result["p_max_sb_o_per"] = math.trunc((inverter_result["p_max_sb_o"] * 1000 - inverter_result["pn"]) * 100 / inverter_result["pn"])
    else:
        inverter_result["p_max_sb_o"] = inverter_result["p_max_sb_o_per"] = -1
    full_candidates = [inverter_result["n_max_in"], inverter_result["n_max_o"], inverter_result["n_max_fl"], inverter_result["n_max_sb"]]
    inverter_result["q_max_fl"] = min(full_candidates) if [value for value in full_candidates if value != -1 and value is not None] else -1
    if vv(inverter_result["q_max_fl"]):
        inverter_result["p_max_sb_fl"] = round(module.nominal_power_w * inverter_result["q_max_fl"] / 1000, 1)
        inverter_result["p_max_sb_fl_per"] = math.trunc((inverter_result["p_max_sb_fl"] * 1000 - inverter_result["pn"]) * 100 / inverter_result["pn"])
    else:
        inverter_result["p_max_sb_fl"] = inverter_result["p_max_sb_fl_per"] = -1
    return {"mod": module_result, "mppt": mppt_results, "inv": inverter_result}
