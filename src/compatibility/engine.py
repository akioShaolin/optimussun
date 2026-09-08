"""Busca de configurações fisicamente possíveis para inversor e módulo."""

from dataclasses import dataclass, replace
from functools import lru_cache
import math
from optimus_lib import (
    compensacao_termica,
    limite_modulos_sobrecarga,
    limite_strings_curto_circuito,
    limite_strings_operacao,
    limites_modulos_serie,
    vv,
)

from .models import (
    CompatibilityOptions,
    CompatibilityResult,
    InverterData,
    LimitingFactor,
    ModuleData,
    MPPTData,
    MPPTResult,
)


@dataclass(frozen=True)
class _Candidate:
    strings: int
    modules_per_string: int

    @property
    def quantity(self):
        return self.strings * self.modules_per_string


@dataclass(frozen=True)
class _MPPTLimits:
    candidates: tuple[_Candidate, ...]
    string_limit: int
    input_limit: int
    short_circuit_limit: int
    operating_current_limit: int
    series_minimum: int
    series_maximum: int
    series_factor: LimitingFactor
    zero_quantity_factor: LimitingFactor | None


def _present_number(value):
    return vv(value) and isinstance(value, (int, float)) and math.isfinite(value)


def _present_positive(value):
    return _present_number(value) and value > 0


def _missing_required_data(inverter, module, options):
    if not _present_positive(inverter.rated_active_power_w):
        return True
    configured_overload = (
        inverter.overload_percent
        if options.custom_overload_percent is None
        else options.custom_overload_percent
    )
    if not _present_number(configured_overload) or configured_overload < 0:
        return True
    module_values = [
        module.nominal_power_w,
        module.vmpp_v,
        module.impp_a,
        module.voc_v,
        module.isc_a,
        module.coef_voc_percent_c,
        module.coef_isc_percent_c,
    ]
    if not inverter.mppts:
        return True
    if not all(_present_number(v) for v in module_values) or not all(
        _present_positive(v) for v in module_values[:5]
    ):
        return True
    option_values = [
        options.min_cell_temperature_c,
        options.max_cell_temperature_c,
        options.operating_current_tolerance,
        options.power_tolerance,
    ]
    if not all(_present_number(v) for v in option_values):
        return True
    if (
        options.min_cell_temperature_c > options.max_cell_temperature_c
        or options.operating_current_tolerance < 0
        or options.power_tolerance < 0
    ):
        return True
    for mppt in inverter.mppts:
        required = [
            mppt.max_input_voltage,
            mppt.min_startup_voltage,
            mppt.max_operating_voltage,
            mppt.min_operating_voltage,
            mppt.max_short_circuit_current,
            mppt.max_operating_current,
            mppt.count,
        ]
        if not all(_present_positive(v) for v in required):
            return True
        if not _present_number(mppt.number_of_inputs) or mppt.number_of_inputs < 0:
            return True
    return False


@lru_cache(maxsize=1024)
def _thermal_values(module, options):
    coef_voc = module.coef_voc_percent_c / 100
    coef_isc = module.coef_isc_percent_c / 100
    vmpp_min, vmpp_max = compensacao_termica(
        coef_voc, options.min_cell_temperature_c, options.max_cell_temperature_c, module.vmpp_v
    )
    voc_min, voc_max = compensacao_termica(
        coef_voc, options.min_cell_temperature_c, options.max_cell_temperature_c, module.voc_v
    )
    _, isc_max = compensacao_termica(
        coef_isc, options.min_cell_temperature_c, options.max_cell_temperature_c, module.isc_a
    )
    _, impp_max = compensacao_termica(
        coef_isc, options.min_cell_temperature_c, options.max_cell_temperature_c, module.impp_a
    )
    return vmpp_min, vmpp_max, voc_min, voc_max, isc_max, impp_max


@lru_cache(maxsize=8192)
def _limits_for_mppt(mppt, thermal, options):
    vmpp_min, vmpp_max, voc_min, voc_max, isc_max, impp_max = thermal
    input_min, input_max = limites_modulos_serie(
        mppt.min_startup_voltage, mppt.max_input_voltage, voc_min, voc_max
    )
    operation_min, operation_max = limites_modulos_serie(
        mppt.min_operating_voltage, mppt.max_operating_voltage, vmpp_min, vmpp_max
    )
    minima = [input_min, operation_min]
    maxima = [input_max, operation_max]
    max_factors = [LimitingFactor.MAX_SERIES_VOLTAGE, LimitingFactor.MPPT_VOLTAGE_RANGE]

    full_load_available = all(
        _present_positive(v) for v in (mppt.min_full_load_voltage, mppt.max_full_load_voltage)
    )
    if options.enforce_full_load and full_load_available:
        full_min, full_max = limites_modulos_serie(
            mppt.min_full_load_voltage, mppt.max_full_load_voltage, vmpp_min, vmpp_max
        )
        minima.append(full_min)
        maxima.append(full_max)
        max_factors.append(LimitingFactor.FULL_LOAD_RANGE)

    series_minimum = max(minima)
    series_maximum = min(maxima)
    series_factor = max_factors[maxima.index(series_maximum)]
    short_limit = limite_strings_curto_circuito(mppt.max_short_circuit_current, isc_max)
    operating_limit = limite_strings_operacao(
        mppt.max_operating_current, impp_max, options.operating_current_tolerance
    )
    applicable = [mppt.number_of_inputs, short_limit]
    if not options.ignore_operating_current:
        applicable.append(operating_limit)
    string_limit = min(applicable)

    zero_quantity_factor = None
    if mppt.number_of_inputs == 0:
        zero_quantity_factor = LimitingFactor.INPUT_COUNT
    elif short_limit <= 0:
        zero_quantity_factor = LimitingFactor.SHORT_CIRCUIT_CURRENT
    elif not options.ignore_operating_current and operating_limit <= 0:
        zero_quantity_factor = LimitingFactor.OPERATING_CURRENT
    elif input_min > input_max:
        zero_quantity_factor = LimitingFactor.INSUFFICIENT_SERIES_VOLTAGE
    elif operation_min > operation_max:
        zero_quantity_factor = LimitingFactor.MPPT_VOLTAGE_RANGE
    elif options.enforce_full_load and full_load_available and full_min > full_max:
        zero_quantity_factor = LimitingFactor.FULL_LOAD_RANGE
    elif series_minimum > series_maximum:
        zero_quantity_factor = series_factor

    candidates = [_Candidate(0, 0)]
    if string_limit > 0 and series_minimum <= series_maximum:
        for strings in range(1, string_limit + 1):
            for modules_per_string in range(series_minimum, series_maximum + 1):
                candidates.append(_Candidate(strings, modules_per_string))

    return _MPPTLimits(
        candidates=tuple(candidates),
        string_limit=string_limit,
        input_limit=mppt.number_of_inputs,
        short_circuit_limit=short_limit,
        operating_current_limit=operating_limit,
        series_minimum=series_minimum,
        series_maximum=series_maximum,
        series_factor=series_factor,
        zero_quantity_factor=zero_quantity_factor,
    )


def _physical_mppts(inverter):
    return tuple((mppt, occurrence) for mppt in inverter.mppts for occurrence in range(1, mppt.count + 1))


def _distribution_rank(configuration):
    quantities = [candidate.quantity for _, _, candidate in configuration]
    imbalance = max(quantities) - min(quantities) if quantities else 0
    strings = sum(candidate.strings for _, _, candidate in configuration)
    return imbalance, strings


def _optimize(physical_limits, quantity_cap):
    states = {0: tuple()}
    for mppt, occurrence, limits in physical_limits:
        next_states = {}
        for accumulated, configuration in states.items():
            for candidate in limits.candidates:
                quantity = accumulated + candidate.quantity
                if quantity > quantity_cap:
                    continue
                proposal = configuration + ((mppt, occurrence, candidate),)
                current = next_states.get(quantity)
                if current is None or _distribution_rank(proposal) < _distribution_rank(current):
                    next_states[quantity] = proposal
        states = next_states
    best_quantity = max(states, default=0)
    return best_quantity, states.get(best_quantity, tuple())


def _limiting_factor(
    quantity, overload_limit, physical_capacity, limits, configuration, options
):
    if overload_limit < physical_capacity:
        return LimitingFactor.OVERLOAD_LIMIT
    if any(limit.series_minimum > limit.series_maximum for limit in limits):
        return LimitingFactor.INSUFFICIENT_SERIES_VOLTAGE

    saturated = []
    for (_, _, candidate), limit in zip(configuration, limits):
        if candidate.strings == limit.string_limit and candidate.strings > 0:
            saturated.append(limit)
    inspected = saturated or list(limits)
    if any(
        not options.ignore_operating_current
        and limit.operating_current_limit <= limit.short_circuit_limit
        and limit.operating_current_limit <= limit.input_limit
        for limit in inspected
    ):
        return LimitingFactor.OPERATING_CURRENT
    if any(
        limit.short_circuit_limit <= limit.input_limit
        and (options.ignore_operating_current or limit.short_circuit_limit <= limit.operating_current_limit)
        for limit in inspected
    ):
        return LimitingFactor.SHORT_CIRCUIT_CURRENT
    if any(limit.input_limit <= limit.short_circuit_limit for limit in inspected):
        return LimitingFactor.ALL_STRINGS_OCCUPIED
    return min(limits, key=lambda item: item.series_maximum).series_factor


def _zero_quantity_factor(limits, overload_limit):
    """Explica por que nenhuma configuração positiva pôde ser escolhida."""
    positive_candidates = [
        candidate.quantity
        for limit in limits
        for candidate in limit.candidates
        if candidate.quantity > 0
    ]
    if positive_candidates:
        # Há configuração elétrica, mas até a menor delas excede o teto DC.
        if min(positive_candidates) > overload_limit:
            return LimitingFactor.OVERLOAD_LIMIT

    factors = [limit.zero_quantity_factor for limit in limits if limit.zero_quantity_factor]
    if factors:
        # OPERATING_CURRENT é causal quando é a única restrição removida no
        # segundo modo; os demais empates mantêm a ordem física do cadastro.
        if LimitingFactor.OPERATING_CURRENT in factors:
            return LimitingFactor.OPERATING_CURRENT
        return factors[0]
    return LimitingFactor.INSUFFICIENT_SERIES_VOLTAGE


@lru_cache(maxsize=8192)
def analyze_compatibility(inverter, module, options=None):
    """Calcula a maior configuração válida para uma combinação de equipamentos."""
    options = options or CompatibilityOptions()
    if _missing_required_data(inverter, module, options):
        return CompatibilityResult(
            quantity=0,
            dc_power_kw=0.0,
            overload_percent=0.0,
            limiting_factor=LimitingFactor.MISSING_DATA,
            operating_current_ignored=options.ignore_operating_current,
            valid=False,
        )

    overload_percent = (
        options.custom_overload_percent
        if options.custom_overload_percent is not None
        else inverter.overload_percent
    )
    if overload_percent < 0:
        return CompatibilityResult(
            quantity=0,
            dc_power_kw=0.0,
            overload_percent=0.0,
            limiting_factor=LimitingFactor.MISSING_DATA,
            operating_current_ignored=options.ignore_operating_current,
            valid=False,
        )
    overload_limit = limite_modulos_sobrecarga(
        inverter.rated_active_power_w,
        overload_percent / 100,
        options.power_tolerance,
        module.nominal_power_w,
    )
    thermal = _thermal_values(module, options)
    physical = _physical_mppts(inverter)
    limits = tuple(_limits_for_mppt(mppt, thermal, options) for mppt, _ in physical)
    physical_limits = tuple(
        (mppt, occurrence, limit)
        for (mppt, occurrence), limit in zip(physical, limits)
    )
    physical_capacity = sum(max(c.quantity for c in limit.candidates) for limit in limits)
    quantity, configuration = _optimize(physical_limits, overload_limit)
    if quantity <= 0:
        factor = _zero_quantity_factor(limits, overload_limit)
        return CompatibilityResult(
            quantity=0,
            dc_power_kw=0.0,
            overload_percent=-100.0,
            limiting_factor=factor,
            operating_current_ignored=options.ignore_operating_current,
            valid=False,
            overload_limit=overload_limit,
        )

    dc_power_kw = quantity * module.nominal_power_w / 1000
    actual_overload = (dc_power_kw * 1000 / inverter.rated_active_power_w - 1) * 100
    mppt_results = tuple(
        MPPTResult(mppt.index, occurrence, candidate.strings, candidate.modules_per_string)
        for mppt, occurrence, candidate in configuration
    )
    factor = _limiting_factor(
        quantity, overload_limit, physical_capacity, limits, configuration, options
    )
    return CompatibilityResult(
        quantity=quantity,
        dc_power_kw=dc_power_kw,
        overload_percent=actual_overload,
        limiting_factor=factor,
        operating_current_ignored=options.ignore_operating_current,
        valid=True,
        strings_per_mppt=tuple(item.strings for item in mppt_results),
        modules_per_string=tuple(item.modules_per_string for item in mppt_results),
        total_strings=sum(item.strings for item in mppt_results),
        mppt_results=mppt_results,
        overload_limit=overload_limit,
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
    normal = analyze_compatibility(
        inverter, module, CompatibilityOptions(False, **common)
    )
    ignored = analyze_compatibility(
        inverter, module, CompatibilityOptions(True, **common)
    )
    if ignored.quantity > normal.quantity:
        normal = replace(normal, limiting_factor=LimitingFactor.OPERATING_CURRENT)
    return normal, ignored
