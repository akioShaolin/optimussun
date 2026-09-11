"""API reutilizável dos cadastros do Optimus Sun."""

from .domain import (
    COMMUNICATION_OPTIONS,
    FUTURE_COMMUNICATION_OPTIONS,
    FUTURE_OUTPUT_OPTIONS,
    OUTPUT_OPTIONS,
    SYSTEM_OPTIONS,
    CatalogValidationError,
    decode_mppt_index,
    encode_mppt_index,
    parse_number,
    validate_inverter_draft,
)
from .repository import CatalogRepository

__all__ = [
    "COMMUNICATION_OPTIONS", "FUTURE_COMMUNICATION_OPTIONS",
    "FUTURE_OUTPUT_OPTIONS", "OUTPUT_OPTIONS", "SYSTEM_OPTIONS",
    "CatalogRepository", "CatalogValidationError", "decode_mppt_index",
    "encode_mppt_index", "parse_number", "validate_inverter_draft",
]
