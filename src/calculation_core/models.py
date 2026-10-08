"""Contratos imutáveis do núcleo de cálculo fotovoltaico.

Os contratos desta camada não conhecem banco de dados, widgets ou componentes
gráficos. Adaptadores são responsáveis por converter sentinelas legadas para
``None`` somente nos campos em que essa conversão foi aprovada.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


class ProfileType(str, Enum):
    AC_OUTPUT = "AC_OUTPUT"
    AC_INPUT = "AC_INPUT"
    EPS_OUTPUT = "EPS_OUTPUT"


class IssueSeverity(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"


class IssueCode(str, Enum):
    MISSING_DATA = "MISSING_DATA"
    INVALID_VALUE = "INVALID_VALUE"
    PROFILE_SELECTION_REQUIRED = "PROFILE_SELECTION_REQUIRED"
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"
    PROFILE_WRONG_INVERTER = "PROFILE_WRONG_INVERTER"
    PROFILE_INACTIVE = "PROFILE_INACTIVE"
    PROFILE_TYPE_NOT_ELIGIBLE = "PROFILE_TYPE_NOT_ELIGIBLE"
    PROFILE_OUTPUT_MODE_MISSING = "PROFILE_OUTPUT_MODE_MISSING"
    PROFILE_POWER_MISSING = "PROFILE_POWER_MISSING"
    MULTIPLE_DEFAULT_PROFILES = "MULTIPLE_DEFAULT_PROFILES"
    NO_FEASIBLE_CONFIGURATION = "NO_FEASIBLE_CONFIGURATION"


class LimitingFactor(str, Enum):
    OVERLOAD_LIMIT = "OVERLOAD_LIMIT"
    OPERATING_CURRENT = "OPERATING_CURRENT"
    SHORT_CIRCUIT_CURRENT = "SHORT_CIRCUIT_CURRENT"
    INPUT_COUNT = "INPUT_COUNT"
    ALL_STRINGS_OCCUPIED = "ALL_STRINGS_OCCUPIED"
    MAX_SERIES_VOLTAGE = "MAX_SERIES_VOLTAGE"
    MPPT_VOLTAGE_RANGE = "MPPT_VOLTAGE_RANGE"
    FULL_LOAD_RANGE = "FULL_LOAD_RANGE"
    INSUFFICIENT_SERIES_VOLTAGE = "INSUFFICIENT_SERIES_VOLTAGE"
    MISSING_DATA = "MISSING_DATA"


@dataclass(frozen=True)
class CalculationIssue:
    code: IssueCode
    message: str
    field: Optional[str] = None
    severity: IssueSeverity = IssueSeverity.ERROR


@dataclass(frozen=True)
class OutputProfile:
    profile_id: Optional[int]
    inverter_id: Optional[int]
    profile_type: ProfileType
    rated_active_power_w: Optional[float]
    output_mode_id: Optional[int] = None
    output_mode: Optional[str] = None
    max_active_power_w: Optional[float] = None
    max_peak_active_power_w: Optional[float] = None
    rated_line_to_line_voltage_v: Optional[float] = None
    rated_line_to_neutral_voltage_v: Optional[float] = None
    rated_current_a: Optional[float] = None
    max_current_a: Optional[float] = None
    active: bool = True
    is_default: bool = False
    row_version: Optional[int] = None
    source: Optional[str] = None


@dataclass(frozen=True)
class MPPTGroup:
    group_id: Optional[int]
    index: int
    count: int
    number_of_inputs: Optional[int]
    max_input_voltage_v: Optional[float]
    min_startup_voltage_v: Optional[float]
    max_operating_voltage_v: Optional[float]
    min_operating_voltage_v: Optional[float]
    max_short_circuit_current_per_mppt_a: Optional[float]
    max_operating_current_per_mppt_a: Optional[float]
    min_full_load_voltage_v: Optional[float] = None
    max_full_load_voltage_v: Optional[float] = None
    rated_input_voltage_v: Optional[float] = None
    max_short_circuit_current_per_string_a: Optional[float] = None
    max_operating_current_per_string_a: Optional[float] = None
    row_version: Optional[int] = None
    source: Optional[str] = None


@dataclass(frozen=True)
class InverterInput:
    inverter_id: Optional[int]
    manufacturer: str
    model: str
    overload_percent: Optional[float]
    mppt_groups: Tuple[MPPTGroup, ...]
    system_types: Tuple[str, ...] = field(default_factory=tuple)
    active: bool = True
    row_version: Optional[int] = None
    source: Optional[str] = None


@dataclass(frozen=True)
class ModuleInput:
    module_id: Optional[int]
    manufacturer: str
    model: str
    nominal_power_w: Optional[float]
    vmpp_v: Optional[float]
    impp_a: Optional[float]
    voc_v: Optional[float]
    isc_a: Optional[float]
    coef_voc_percent_c: Optional[float]
    coef_isc_percent_c: Optional[float]
    coef_pmax_percent_c: Optional[float] = None
    active: bool = True
    row_version: Optional[int] = None
    source: Optional[str] = None


@dataclass(frozen=True)
class CalculationOptions:
    ignore_operating_current: bool = False
    custom_overload_percent: Optional[float] = None
    enforce_full_load: bool = True
    min_cell_temperature_c: float = 10.0
    max_cell_temperature_c: float = 50.0
    operating_current_tolerance: float = 0.0
    power_tolerance: float = 0.005


@dataclass(frozen=True)
class CalculationRequest:
    inverter: InverterInput
    module: ModuleInput
    output_profile: OutputProfile
    options: CalculationOptions = field(default_factory=CalculationOptions)


@dataclass(frozen=True)
class ThermalValues:
    power_min_w: Optional[float]
    power_max_w: Optional[float]
    vmpp_min_v: float
    vmpp_max_v: float
    voc_min_v: float
    voc_max_v: float
    isc_min_a: float
    isc_max_a: float
    impp_min_a: float
    impp_max_a: float


@dataclass(frozen=True)
class MPPTLimits:
    group_id: Optional[int]
    index: int
    occurrence: int
    input_limit: int
    short_circuit_limit: int
    operating_current_limit: Optional[int]
    string_limit: int
    input_series_minimum: int
    input_series_maximum: int
    operating_series_minimum: int
    operating_series_maximum: int
    full_load_series_minimum: Optional[int]
    full_load_series_maximum: Optional[int]
    series_minimum: int
    series_maximum: int
    series_factor: LimitingFactor


@dataclass(frozen=True)
class MPPTCalculation:
    group_id: Optional[int]
    index: int
    occurrence: int
    strings: int
    modules_per_string: int
    limits: MPPTLimits

    @property
    def quantity(self) -> int:
        return self.strings * self.modules_per_string


@dataclass(frozen=True)
class TotalLimits:
    max_modules_by_input_voltage: int
    max_modules_by_operating_voltage: int
    max_modules_by_full_load_voltage: Optional[int]
    max_modules_by_overload: int
    max_modules_physical: int


@dataclass(frozen=True)
class CalculationResult:
    inverter_id: Optional[int]
    inverter_model: str
    inverter_row_version: Optional[int]
    inverter_source: Optional[str]
    module_id: Optional[int]
    module_model: str
    module_row_version: Optional[int]
    module_source: Optional[str]
    profile_id: Optional[int]
    profile_type: ProfileType
    profile_row_version: Optional[int]
    profile_source: Optional[str]
    output_mode_id: Optional[int]
    output_mode: Optional[str]
    rated_active_power_w: Optional[float]
    max_active_power_w: Optional[float]
    max_peak_active_power_w: Optional[float]
    rated_line_to_line_voltage_v: Optional[float]
    rated_line_to_neutral_voltage_v: Optional[float]
    options: CalculationOptions
    effective_overload_percent: Optional[float]
    valid: bool
    quantity: Optional[int]
    dc_power_kw: Optional[float]
    overload_percent: Optional[float]
    limiting_factor: LimitingFactor
    overload_limit: Optional[int]
    physical_capacity: Optional[int]
    total_strings: Optional[int]
    total_limits: Optional[TotalLimits]
    thermal: Optional[ThermalValues]
    mppt_limits: Tuple[MPPTLimits, ...] = field(default_factory=tuple)
    mppt_results: Tuple[MPPTCalculation, ...] = field(default_factory=tuple)
    issues: Tuple[CalculationIssue, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ProfileResolution:
    profile: Optional[OutputProfile]
    issues: Tuple[CalculationIssue, ...] = field(default_factory=tuple)

    @property
    def valid(self) -> bool:
        return self.profile is not None and not any(
            issue.severity is IssueSeverity.ERROR for issue in self.issues
        )

    @property
    def selection_required(self) -> bool:
        return any(
            issue.code is IssueCode.PROFILE_SELECTION_REQUIRED for issue in self.issues
        )
