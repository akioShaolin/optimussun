"""Motor reutilizável de compatibilidade elétrica do Optimus Sun."""

from .engine import analyze_compatibility, compare_operating_current_modes
from .models import (
    CompatibilityOptions,
    CompatibilityResult,
    EquipmentSummary,
    InverterData,
    LimitingFactor,
    ModuleData,
    MPPTData,
    MPPTResult,
)
from .matrix import (
    CompatibilityMatrix,
    InverterSelection,
    MatrixCalculation,
    MatrixCellResult,
    ModuleSelection,
)
from .repository import (
    list_active_inverters,
    list_active_modules,
    load_inverter,
    load_module,
)

__all__ = [
    "analyze_compatibility",
    "compare_operating_current_modes",
    "CompatibilityOptions",
    "CompatibilityResult",
    "EquipmentSummary",
    "InverterData",
    "LimitingFactor",
    "ModuleData",
    "MPPTData",
    "MPPTResult",
    "CompatibilityMatrix",
    "InverterSelection",
    "MatrixCalculation",
    "MatrixCellResult",
    "ModuleSelection",
    "list_active_inverters",
    "list_active_modules",
    "load_inverter",
    "load_module",
]
