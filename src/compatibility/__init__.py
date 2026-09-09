"""Motor reutilizável de compatibilidade elétrica do Optimus Sun."""

from .engine import analyze_compatibility, compare_operating_current_modes
from .csv_io import CSVFormatError, ImportedMatrix, export_matrix_csv, import_matrix_csv
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
    ImportedCellResult,
    ImportedCellValue,
    ModuleSelection,
)
from .repository import (
    list_active_inverters,
    list_active_modules,
    list_inverters,
    list_modules,
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
    "ImportedCellResult",
    "ImportedCellValue",
    "ModuleSelection",
    "list_active_inverters",
    "list_active_modules",
    "list_inverters",
    "list_modules",
    "load_inverter",
    "load_module",
    "CSVFormatError",
    "ImportedMatrix",
    "export_matrix_csv",
    "import_matrix_csv",
]
