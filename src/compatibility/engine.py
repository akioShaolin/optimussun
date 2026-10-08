"""Adaptador da API v2 para o núcleo compartilhado de cálculo."""

from dataclasses import replace
from functools import lru_cache

from calculation_core import (
    CalculationOptions as CoreOptions,
    CalculationRequest,
    InverterInput,
    ModuleInput,
    MPPTGroup,
    OutputProfile,
    ProfileType,
    calculate,
)

from .models import CompatibilityOptions, CompatibilityResult, LimitingFactor, MPPTResult


def _optional_legacy(value):
    """Converte apenas a sentinela aprovada nos campos opcionais do legado."""
    return None if value == -1 else value


def _request(inverter, module, options):
    groups = tuple(
        MPPTGroup(
            group_id=None,
            index=item.index,
            count=item.count,
            number_of_inputs=item.number_of_inputs,
            max_input_voltage_v=item.max_input_voltage,
            min_startup_voltage_v=item.min_startup_voltage,
            max_operating_voltage_v=item.max_operating_voltage,
            min_operating_voltage_v=item.min_operating_voltage,
            max_short_circuit_current_per_mppt_a=item.max_short_circuit_current,
            max_operating_current_per_mppt_a=_optional_legacy(item.max_operating_current),
            min_full_load_voltage_v=_optional_legacy(item.min_full_load_voltage),
            max_full_load_voltage_v=_optional_legacy(item.max_full_load_voltage),
            source="sqlite-v2-adapter",
        )
        for item in inverter.mppts
    )
    core_inverter = InverterInput(
        inverter_id=inverter.database_id,
        manufacturer="",
        model=inverter.model,
        overload_percent=inverter.overload_percent,
        mppt_groups=groups,
        system_types=("ON-GRID",),
        source="sqlite-v2-adapter",
    )
    core_module = ModuleInput(
        module_id=module.database_id,
        manufacturer="",
        model=module.model,
        nominal_power_w=module.nominal_power_w,
        vmpp_v=module.vmpp_v,
        impp_a=module.impp_a,
        voc_v=module.voc_v,
        isc_a=module.isc_a,
        coef_voc_percent_c=module.coef_voc_percent_c,
        coef_isc_percent_c=module.coef_isc_percent_c,
        source="sqlite-v2-adapter",
    )
    profile = OutputProfile(
        profile_id=None,
        inverter_id=inverter.database_id,
        profile_type=ProfileType.AC_OUTPUT,
        rated_active_power_w=inverter.rated_active_power_w,
        output_mode="LEGACY_CA_FIELDS",
        active=True,
        is_default=True,
        source="legacy-rated-active-power",
    )
    core_options = CoreOptions(
        ignore_operating_current=options.ignore_operating_current,
        custom_overload_percent=options.custom_overload_percent,
        enforce_full_load=options.enforce_full_load,
        min_cell_temperature_c=options.min_cell_temperature_c,
        max_cell_temperature_c=options.max_cell_temperature_c,
        operating_current_tolerance=options.operating_current_tolerance,
        power_tolerance=options.power_tolerance,
    )
    return CalculationRequest(core_inverter, core_module, profile, core_options)


@lru_cache(maxsize=8192)
def analyze_compatibility(inverter, module, options=None):
    """Mantém o contrato público v2 enquanto delega as fórmulas ao núcleo v3."""
    options = options or CompatibilityOptions()
    result = calculate(_request(inverter, module, options))
    mppt_results = tuple(
        MPPTResult(item.index, item.occurrence, item.strings, item.modules_per_string)
        for item in result.mppt_results
    )
    missing_data = result.limiting_factor.value == LimitingFactor.MISSING_DATA.value
    return CompatibilityResult(
        quantity=result.quantity or 0,
        dc_power_kw=result.dc_power_kw or 0.0,
        overload_percent=0.0 if missing_data else (result.overload_percent or 0.0),
        limiting_factor=LimitingFactor(result.limiting_factor.value),
        operating_current_ignored=options.ignore_operating_current,
        valid=result.valid,
        strings_per_mppt=tuple(item.strings for item in mppt_results),
        modules_per_string=tuple(item.modules_per_string for item in mppt_results),
        total_strings=result.total_strings or 0,
        mppt_results=mppt_results,
        overload_limit=result.overload_limit or 0,
    )


def compare_operating_current_modes(inverter, module, options=None):
    """Retorna lado a lado os resultados normal e sem o limite de Impp."""
    options = options or CompatibilityOptions()
    common = dict(
        custom_overload_percent=options.custom_overload_percent,
        enforce_full_load=options.enforce_full_load,
        min_cell_temperature_c=options.min_cell_temperature_c,
        max_cell_temperature_c=options.max_cell_temperature_c,
        operating_current_tolerance=options.operating_current_tolerance,
        power_tolerance=options.power_tolerance,
    )
    normal = analyze_compatibility(inverter, module, CompatibilityOptions(False, **common))
    ignored = analyze_compatibility(inverter, module, CompatibilityOptions(True, **common))
    if ignored.quantity > normal.quantity:
        normal = replace(normal, limiting_factor=LimitingFactor.OPERATING_CURRENT)
    return normal, ignored
