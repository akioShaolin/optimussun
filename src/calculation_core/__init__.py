"""API pública do núcleo compartilhado de cálculos do Optimus Sun."""

from .engine import calculate
from .models import (
    CalculationIssue,
    CalculationOptions,
    CalculationRequest,
    CalculationResult,
    InverterInput,
    IssueCode,
    IssueSeverity,
    LimitingFactor,
    ModuleInput,
    MPPTCalculation,
    MPPTGroup,
    MPPTLimits,
    OutputProfile,
    ProfileResolution,
    ProfileType,
    ThermalValues,
    TotalLimits,
)
from .profiles import profile_is_eligible, resolve_output_profile, validate_output_profile

__all__ = [
    "CalculationIssue", "CalculationOptions", "CalculationRequest", "CalculationResult",
    "InverterInput", "IssueCode", "IssueSeverity", "LimitingFactor", "ModuleInput",
    "MPPTCalculation", "MPPTGroup", "MPPTLimits", "OutputProfile", "ProfileResolution",
    "ProfileType", "ThermalValues", "TotalLimits", "calculate", "profile_is_eligible",
    "resolve_output_profile", "validate_output_profile",
]
