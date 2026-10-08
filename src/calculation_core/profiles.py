"""Resolução pura e explícita de perfis de saída."""

from __future__ import annotations

from .models import (
    CalculationIssue,
    InverterInput,
    IssueCode,
    OutputProfile,
    ProfileResolution,
    ProfileType,
)


_HYBRID = {"HYBRID", "HÍBRIDO", "HIBRIDO"}
_ON_GRID = {"ON-GRID", "ON_GRID", "ONGRID"}
_GRID_ZERO = {"GRIDZERO", "GRID-ZERO", "GRID_ZERO"}
_OFF_GRID = {"OFF-GRID", "OFF_GRID", "OFFGRID"}


def _normal_systems(inverter: InverterInput) -> set[str]:
    return {value.strip().upper() for value in inverter.system_types}


def profile_is_eligible(inverter: InverterInput, profile: OutputProfile) -> bool:
    systems = _normal_systems(inverter)
    if profile.profile_type is ProfileType.AC_OUTPUT:
        return bool(systems & (_ON_GRID | _GRID_ZERO | _HYBRID))
    if profile.profile_type is ProfileType.EPS_OUTPUT:
        return bool(systems & (_OFF_GRID | _HYBRID))
    return False


def validate_output_profile(
    inverter: InverterInput, profile: OutputProfile
) -> tuple[CalculationIssue, ...]:
    issues = []
    if profile.inverter_id != inverter.inverter_id:
        issues.append(CalculationIssue(IssueCode.PROFILE_WRONG_INVERTER, "O perfil não pertence ao inversor informado.", "output_profile.inverter_id"))
    if not profile.active:
        issues.append(CalculationIssue(IssueCode.PROFILE_INACTIVE, "O perfil de saída está inativo.", "output_profile.active"))
    if profile.profile_type is ProfileType.AC_INPUT or not profile_is_eligible(inverter, profile):
        issues.append(CalculationIssue(IssueCode.PROFILE_TYPE_NOT_ELIGIBLE, "O tipo do perfil não é elegível como saída para a classificação do inversor.", "output_profile.profile_type"))
    if profile.profile_type in (ProfileType.AC_OUTPUT, ProfileType.EPS_OUTPUT) and profile.output_mode_id is None and not profile.output_mode:
        issues.append(CalculationIssue(IssueCode.PROFILE_OUTPUT_MODE_MISSING, "O perfil de saída deve identificar seu modo de saída.", "output_profile.output_mode_id"))
    if profile.rated_active_power_w is None or profile.rated_active_power_w <= 0:
        issues.append(CalculationIssue(IssueCode.PROFILE_POWER_MISSING, "A potência ativa nominal do perfil de saída é necessária.", "output_profile.rated_active_power_w"))
    return tuple(issues)


def resolve_output_profile(
    inverter: InverterInput,
    profiles: tuple[OutputProfile, ...],
    selected_profile_id: int | None = None,
) -> ProfileResolution:
    """Resolve seleção explícita ou um único padrão válido, sem heurísticas."""
    if selected_profile_id is not None:
        selected = next((item for item in profiles if item.profile_id == selected_profile_id), None)
        if selected is None:
            return ProfileResolution(None, (CalculationIssue(IssueCode.PROFILE_NOT_FOUND, "O perfil selecionado não foi encontrado.", "selected_profile_id"),))
        issues = validate_output_profile(inverter, selected)
        return ProfileResolution(selected if not issues else None, issues)

    defaults = [item for item in profiles if item.is_default]
    valid_defaults = [item for item in defaults if not validate_output_profile(inverter, item)]
    if len(valid_defaults) == 1:
        return ProfileResolution(valid_defaults[0])
    if len(valid_defaults) > 1:
        return ProfileResolution(None, (CalculationIssue(IssueCode.MULTIPLE_DEFAULT_PROFILES, "Há mais de um perfil padrão válido; a escolha deve ser explícita.", "output_profiles"),))
    return ProfileResolution(None, (CalculationIssue(IssueCode.PROFILE_SELECTION_REQUIRED, "Selecione explicitamente um perfil de saída válido.", "selected_profile_id"),))
