"""Motor reutilizável de compatibilidade elétrica do Optimus Sun."""

from .engine import analyze_compatibility, compare_operating_current_modes
from .models import (
    CompatibilityOptions,
    CompatibilityResult,
    InverterData,
    LimitingFactor,
    ModuleData,
    MPPTData,
    MPPTResult,
)
from .repository import load_inverter, load_module

__all__ = [
    "analyze_compatibility",
    "compare_operating_current_modes",
    "CompatibilityOptions",
    "CompatibilityResult",
    "InverterData",
    "LimitingFactor",
    "ModuleData",
    "MPPTData",
    "MPPTResult",
    "load_inverter",
    "load_module",
]
