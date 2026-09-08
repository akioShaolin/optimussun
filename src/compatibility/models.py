"""Modelos de dados do motor de compatibilidade."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple


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
class MPPTData:
    index: int
    number_of_inputs: int
    max_input_voltage: float
    min_startup_voltage: float
    max_operating_voltage: float
    min_operating_voltage: float
    max_short_circuit_current: float
    max_operating_current: float
    min_full_load_voltage: Optional[float] = None
    max_full_load_voltage: Optional[float] = None
    count: int = 1


@dataclass(frozen=True)
class InverterData:
    model: str
    rated_active_power_w: float
    overload_percent: float
    mppts: Tuple[MPPTData, ...]
    database_id: Optional[int] = None


@dataclass(frozen=True)
class ModuleData:
    model: str
    nominal_power_w: float
    vmpp_v: float
    impp_a: float
    voc_v: float
    isc_a: float
    coef_voc_percent_c: float
    coef_isc_percent_c: float
    database_id: Optional[int] = None


@dataclass(frozen=True)
class CompatibilityOptions:
    ignore_operating_current: bool = False
    custom_overload_percent: Optional[float] = None
    enforce_full_load: bool = True
    min_cell_temperature_c: float = 10.0
    max_cell_temperature_c: float = 50.0
    operating_current_tolerance: float = 0.0
    power_tolerance: float = 0.005


@dataclass(frozen=True)
class MPPTResult:
    index: int
    occurrence: int
    strings: int
    modules_per_string: int

    @property
    def quantity(self):
        return self.strings * self.modules_per_string


@dataclass(frozen=True)
class CompatibilityResult:
    quantity: int
    dc_power_kw: float
    overload_percent: float
    limiting_factor: LimitingFactor
    operating_current_ignored: bool
    valid: bool
    strings_per_mppt: Tuple[int, ...] = field(default_factory=tuple)
    modules_per_string: Tuple[int, ...] = field(default_factory=tuple)
    total_strings: int = 0
    mppt_results: Tuple[MPPTResult, ...] = field(default_factory=tuple)
    overload_limit: int = 0
