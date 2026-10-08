"""Motor puro para compatibilidade elétrica e fechamento de strings."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .math import (
    operating_string_limit,
    overload_module_limit,
    series_module_limits,
    short_circuit_string_limit,
    thermal_compensation,
)
from .models import (
    CalculationIssue,
    CalculationRequest,
    CalculationResult,
    IssueCode,
    LimitingFactor,
    MPPTCalculation,
    MPPTGroup,
    MPPTLimits,
    ThermalValues,
    TotalLimits,
)
from .profiles import validate_output_profile


@dataclass(frozen=True)
class _Candidate:
    strings: int
    modules_per_string: int

    @property
    def quantity(self):
        return self.strings * self.modules_per_string


@dataclass(frozen=True)
class _PreparedMPPT:
    group: MPPTGroup
    occurrence: int
    limits: MPPTLimits
    candidates: tuple[_Candidate, ...]
    zero_quantity_factor: LimitingFactor | None


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _positive(value) -> bool:
    return _number(value) and value > 0


def _issue(field, message, code=IssueCode.MISSING_DATA):
    return CalculationIssue(code, message, field)


def _validate(request: CalculationRequest) -> tuple[CalculationIssue, ...]:
    inverter, module, options = request.inverter, request.module, request.options
    issues = list(validate_output_profile(inverter, request.output_profile))
    overload = inverter.overload_percent if options.custom_overload_percent is None else options.custom_overload_percent
    if not _number(overload) or overload < 0:
        issues.append(_issue("options.custom_overload_percent", "A sobrecarga efetiva deve ser um percentual adicional não negativo.", IssueCode.INVALID_VALUE))
    required_module = {
        "module.nominal_power_w": module.nominal_power_w,
        "module.vmpp_v": module.vmpp_v,
        "module.impp_a": module.impp_a,
        "module.voc_v": module.voc_v,
        "module.isc_a": module.isc_a,
    }
    for field, value in required_module.items():
        if not _positive(value):
            issues.append(_issue(field, "Grandeza elétrica positiva obrigatória ausente ou inválida."))
    for field, value in {
        "module.coef_voc_percent_c": module.coef_voc_percent_c,
        "module.coef_isc_percent_c": module.coef_isc_percent_c,
    }.items():
        if not _number(value):
            issues.append(_issue(field, "Coeficiente térmico obrigatório ausente ou inválido."))
    if not request.inverter.mppt_groups:
        issues.append(_issue("inverter.mppt_groups", "O inversor não possui grupos MPPT calculáveis."))
    if not all(_number(value) for value in (options.min_cell_temperature_c, options.max_cell_temperature_c, options.operating_current_tolerance, options.power_tolerance)):
        issues.append(_issue("options", "As opções numéricas devem ser finitas.", IssueCode.INVALID_VALUE))
    elif options.min_cell_temperature_c > options.max_cell_temperature_c:
        issues.append(_issue("options.min_cell_temperature_c", "A temperatura mínima não pode superar a máxima.", IssueCode.INVALID_VALUE))
    elif options.operating_current_tolerance < 0 or options.power_tolerance < 0:
        issues.append(_issue("options", "Tolerâncias não podem ser negativas.", IssueCode.INVALID_VALUE))

    for position, group in enumerate(inverter.mppt_groups):
        prefix = f"inverter.mppt_groups[{position}]"
        if not isinstance(group.count, int) or isinstance(group.count, bool) or group.count <= 0:
            issues.append(_issue(f"{prefix}.count", "A quantidade física representada deve ser inteira e positiva.", IssueCode.INVALID_VALUE))
        if not isinstance(group.number_of_inputs, int) or isinstance(group.number_of_inputs, bool) or group.number_of_inputs < 0:
            issues.append(_issue(f"{prefix}.number_of_inputs", "A quantidade de entradas deve ser inteira e não negativa.", IssueCode.INVALID_VALUE))
        required = {
            "max_input_voltage_v": group.max_input_voltage_v,
            "min_startup_voltage_v": group.min_startup_voltage_v,
            "max_operating_voltage_v": group.max_operating_voltage_v,
            "min_operating_voltage_v": group.min_operating_voltage_v,
            "max_short_circuit_current_per_mppt_a": group.max_short_circuit_current_per_mppt_a,
        }
        if not options.ignore_operating_current:
            required["max_operating_current_per_mppt_a"] = group.max_operating_current_per_mppt_a
        for name, value in required.items():
            if not _positive(value):
                issues.append(_issue(f"{prefix}.{name}", "Limite MPPT positivo obrigatório ausente ou inválido."))
        for name, value in (
            ("min_full_load_voltage_v", group.min_full_load_voltage_v),
            ("max_full_load_voltage_v", group.max_full_load_voltage_v),
        ):
            if value is not None and not _positive(value):
                issues.append(_issue(f"{prefix}.{name}", "Faixa de plena carga informada deve ser positiva.", IssueCode.INVALID_VALUE))
    return tuple(issues)


def _thermal(request: CalculationRequest) -> ThermalValues:
    module, options = request.module, request.options
    coef_voc = module.coef_voc_percent_c / 100
    coef_isc = module.coef_isc_percent_c / 100
    vmpp_min, vmpp_max = thermal_compensation(coef_voc, options.min_cell_temperature_c, options.max_cell_temperature_c, module.vmpp_v)
    voc_min, voc_max = thermal_compensation(coef_voc, options.min_cell_temperature_c, options.max_cell_temperature_c, module.voc_v)
    isc_min, isc_max = thermal_compensation(coef_isc, options.min_cell_temperature_c, options.max_cell_temperature_c, module.isc_a)
    impp_min, impp_max = thermal_compensation(coef_isc, options.min_cell_temperature_c, options.max_cell_temperature_c, module.impp_a)
    power_min = power_max = None
    if _number(module.coef_pmax_percent_c):
        power_min, power_max = thermal_compensation(module.coef_pmax_percent_c / 100, options.min_cell_temperature_c, options.max_cell_temperature_c, module.nominal_power_w)
    return ThermalValues(power_min, power_max, vmpp_min, vmpp_max, voc_min, voc_max, isc_min, isc_max, impp_min, impp_max)


def _prepare_group(group, occurrence, thermal, options):
    input_min, input_max = series_module_limits(group.min_startup_voltage_v, group.max_input_voltage_v, thermal.voc_min_v, thermal.voc_max_v)
    operation_min, operation_max = series_module_limits(group.min_operating_voltage_v, group.max_operating_voltage_v, thermal.vmpp_min_v, thermal.vmpp_max_v)
    full_available = group.min_full_load_voltage_v is not None and group.max_full_load_voltage_v is not None
    full_min = full_max = None
    minima = [input_min, operation_min]
    maxima = [input_max, operation_max]
    factors = [LimitingFactor.MAX_SERIES_VOLTAGE, LimitingFactor.MPPT_VOLTAGE_RANGE]
    if options.enforce_full_load and full_available:
        full_min, full_max = series_module_limits(group.min_full_load_voltage_v, group.max_full_load_voltage_v, thermal.vmpp_min_v, thermal.vmpp_max_v)
        minima.append(full_min); maxima.append(full_max); factors.append(LimitingFactor.FULL_LOAD_RANGE)
    series_minimum, series_maximum = max(minima), min(maxima)
    series_factor = factors[maxima.index(series_maximum)]
    short_limit = short_circuit_string_limit(group.max_short_circuit_current_per_mppt_a, thermal.isc_max_a)
    operating_limit = None
    if group.max_operating_current_per_mppt_a is not None:
        operating_limit = operating_string_limit(group.max_operating_current_per_mppt_a, thermal.impp_max_a, options.operating_current_tolerance)
    applicable = [group.number_of_inputs, short_limit]
    if not options.ignore_operating_current:
        applicable.append(operating_limit)
    string_limit = min(applicable)
    zero = None
    if group.number_of_inputs == 0: zero = LimitingFactor.INPUT_COUNT
    elif short_limit <= 0: zero = LimitingFactor.SHORT_CIRCUIT_CURRENT
    elif not options.ignore_operating_current and operating_limit <= 0: zero = LimitingFactor.OPERATING_CURRENT
    elif input_min > input_max: zero = LimitingFactor.INSUFFICIENT_SERIES_VOLTAGE
    elif operation_min > operation_max: zero = LimitingFactor.MPPT_VOLTAGE_RANGE
    elif options.enforce_full_load and full_available and full_min > full_max: zero = LimitingFactor.FULL_LOAD_RANGE
    elif series_minimum > series_maximum: zero = series_factor
    candidates = [_Candidate(0, 0)]
    if string_limit > 0 and series_minimum <= series_maximum:
        candidates.extend(_Candidate(strings, modules) for strings in range(1, string_limit + 1) for modules in range(series_minimum, series_maximum + 1))
    limits = MPPTLimits(group.group_id, group.index, occurrence, group.number_of_inputs, short_limit, operating_limit, string_limit, input_min, input_max, operation_min, operation_max, full_min, full_max, series_minimum, series_maximum, series_factor)
    return _PreparedMPPT(group, occurrence, limits, tuple(candidates), zero)


def _rank(configuration):
    quantities = [candidate.quantity for _, candidate in configuration]
    return (max(quantities) - min(quantities) if quantities else 0, sum(candidate.strings for _, candidate in configuration))


def _optimize(prepared, cap):
    states = {0: tuple()}
    for item in prepared:
        next_states = {}
        for accumulated, configuration in states.items():
            for candidate in item.candidates:
                quantity = accumulated + candidate.quantity
                if quantity > cap: continue
                proposal = configuration + ((item, candidate),)
                current = next_states.get(quantity)
                if current is None or _rank(proposal) < _rank(current): next_states[quantity] = proposal
        states = next_states
    quantity = max(states, default=0)
    return quantity, states.get(quantity, tuple())


def _zero_factor(prepared, overload_limit):
    positive = [candidate.quantity for item in prepared for candidate in item.candidates if candidate.quantity > 0]
    if positive and min(positive) > overload_limit: return LimitingFactor.OVERLOAD_LIMIT
    factors = [item.zero_quantity_factor for item in prepared if item.zero_quantity_factor]
    if LimitingFactor.OPERATING_CURRENT in factors: return LimitingFactor.OPERATING_CURRENT
    return factors[0] if factors else LimitingFactor.INSUFFICIENT_SERIES_VOLTAGE


def _factor(overload_limit, physical_capacity, prepared, configuration, options):
    if overload_limit < physical_capacity: return LimitingFactor.OVERLOAD_LIMIT
    if any(item.limits.series_minimum > item.limits.series_maximum for item in prepared): return LimitingFactor.INSUFFICIENT_SERIES_VOLTAGE
    saturated = [item for (item, candidate) in configuration if candidate.strings == item.limits.string_limit and candidate.strings > 0]
    inspected = saturated or list(prepared)
    if any(not options.ignore_operating_current and item.limits.operating_current_limit <= item.limits.short_circuit_limit and item.limits.operating_current_limit <= item.limits.input_limit for item in inspected): return LimitingFactor.OPERATING_CURRENT
    if any(item.limits.short_circuit_limit <= item.limits.input_limit and (options.ignore_operating_current or item.limits.short_circuit_limit <= item.limits.operating_current_limit) for item in inspected): return LimitingFactor.SHORT_CIRCUIT_CURRENT
    if any(item.limits.input_limit <= item.limits.short_circuit_limit for item in inspected): return LimitingFactor.ALL_STRINGS_OCCUPIED
    return min(inspected, key=lambda item: item.limits.series_maximum).limits.series_factor


def _base_result(request, **values):
    inverter, module, profile = request.inverter, request.module, request.output_profile
    return CalculationResult(
        inverter_id=inverter.inverter_id, inverter_model=inverter.model, inverter_row_version=inverter.row_version, inverter_source=inverter.source,
        module_id=module.module_id, module_model=module.model, module_row_version=module.row_version, module_source=module.source,
        profile_id=profile.profile_id, profile_type=profile.profile_type, profile_row_version=profile.row_version, profile_source=profile.source,
        output_mode_id=profile.output_mode_id, output_mode=profile.output_mode, rated_active_power_w=profile.rated_active_power_w,
        max_active_power_w=profile.max_active_power_w, max_peak_active_power_w=profile.max_peak_active_power_w,
        rated_line_to_line_voltage_v=profile.rated_line_to_line_voltage_v,
        rated_line_to_neutral_voltage_v=profile.rated_line_to_neutral_voltage_v,
        options=request.options, **values,
    )


def calculate(request: CalculationRequest) -> CalculationResult:
    """Calcula uma configuração máxima sem consultar infraestrutura externa."""
    issues = _validate(request)
    overload = request.inverter.overload_percent if request.options.custom_overload_percent is None else request.options.custom_overload_percent
    if issues:
        return _base_result(request, effective_overload_percent=overload if _number(overload) else None, valid=False, quantity=None, dc_power_kw=None, overload_percent=None, limiting_factor=LimitingFactor.MISSING_DATA, overload_limit=None, physical_capacity=None, total_strings=None, total_limits=None, thermal=None, issues=issues)
    thermal = _thermal(request)
    overload_limit = overload_module_limit(request.output_profile.rated_active_power_w, overload / 100, request.options.power_tolerance, request.module.nominal_power_w)
    prepared = tuple(_prepare_group(group, occurrence, thermal, request.options) for group in request.inverter.mppt_groups for occurrence in range(1, group.count + 1))
    physical_capacity = sum(max(candidate.quantity for candidate in item.candidates) for item in prepared)
    total_limits = TotalLimits(
        max_modules_by_input_voltage=sum(item.limits.input_series_maximum * item.limits.string_limit for item in prepared),
        max_modules_by_operating_voltage=sum(item.limits.operating_series_maximum * item.limits.string_limit for item in prepared),
        max_modules_by_full_load_voltage=(
            sum(item.limits.full_load_series_maximum * item.limits.string_limit for item in prepared)
            if all(item.limits.full_load_series_maximum is not None for item in prepared)
            else None
        ),
        max_modules_by_overload=overload_limit,
        max_modules_physical=physical_capacity,
    )
    quantity, configuration = _optimize(prepared, overload_limit)
    all_limits = tuple(item.limits for item in prepared)
    if quantity <= 0:
        factor = _zero_factor(prepared, overload_limit)
        reason = CalculationIssue(IssueCode.NO_FEASIBLE_CONFIGURATION, "Nenhuma configuração positiva satisfaz simultaneamente os limites informados.")
        return _base_result(request, effective_overload_percent=overload, valid=False, quantity=0, dc_power_kw=0.0, overload_percent=-100.0, limiting_factor=factor, overload_limit=overload_limit, physical_capacity=physical_capacity, total_strings=0, total_limits=total_limits, thermal=thermal, mppt_limits=all_limits, issues=(reason,))
    mppt_results = tuple(MPPTCalculation(item.group.group_id, item.group.index, item.occurrence, candidate.strings, candidate.modules_per_string, item.limits) for item, candidate in configuration)
    dc_power = quantity * request.module.nominal_power_w / 1000
    actual_overload = (dc_power * 1000 / request.output_profile.rated_active_power_w - 1) * 100
    factor = _factor(overload_limit, physical_capacity, prepared, configuration, request.options)
    return _base_result(request, effective_overload_percent=overload, valid=True, quantity=quantity, dc_power_kw=dc_power, overload_percent=actual_overload, limiting_factor=factor, overload_limit=overload_limit, physical_capacity=physical_capacity, total_strings=sum(item.strings for item in mppt_results), total_limits=total_limits, thermal=thermal, mppt_limits=all_limits, mppt_results=mppt_results, issues=tuple())
