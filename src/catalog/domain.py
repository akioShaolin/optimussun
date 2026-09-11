"""Regras puras de validação usadas pela GUI e pela persistência."""

from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation

SYSTEM_OPTIONS = ("ON-GRID", "OFF-GRID", "GRIDZERO", "HYBRID")
COMMUNICATION_OPTIONS = ("DISPLAY", "RS485", "WIFI", "LED", "USB", "4G")
OUTPUT_OPTIONS = ("THREE_PHASE_FOUR_WIRE", "THREE_PHASE_THREE_WIRE", "SINGLE_PHASE")
FUTURE_COMMUNICATION_OPTIONS = ("RS232", "CAN", "ETHERNET", "GPRS")
FUTURE_OUTPUT_OPTIONS = ("SPLIT PHASE",)


class CatalogValidationError(ValueError):
    """Agrupa erros de validação sem depender de widgets Tk."""

    def __init__(self, errors):
        self.errors = tuple(str(item) for item in errors)
        super().__init__("\n".join(self.errors))


def parse_number(value, *, integer=False, required=False, unknown=-1,
                 positive=False, field="Valor"):
    """Converte número decimal pt-BR/en-US, rejeitando formatos ambíguos."""
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise ValueError(f"{field} é obrigatório.")
        return unknown
    if isinstance(value, bool):
        raise ValueError(f"{field} deve ser numérico.")
    text = str(value).strip()
    if any(ch.isspace() for ch in text) or ("," in text and "." in text):
        raise ValueError(f"{field} usa ponto ou vírgula apenas como separador decimal.")
    text = text.replace(",", ".")
    try:
        number = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"{field} deve ser numérico.") from exc
    if not number.is_finite():
        raise ValueError(f"{field} não aceita NaN ou infinito.")
    if integer and number != number.to_integral_value():
        raise ValueError(f"{field} deve ser inteiro; o valor não será arredondado.")
    result = int(number) if integer else float(number)
    if positive and result != unknown and result <= 0:
        raise ValueError(f"{field} deve ser positivo.")
    return result


def primes(count):
    result, candidate = [], 2
    while len(result) < count:
        if all(candidate % prime for prime in result if prime * prime <= candidate):
            result.append(candidate)
        candidate += 1
    return tuple(result)


def encode_mppt_index(positions):
    positions = tuple(int(item) for item in positions)
    if not positions or len(set(positions)) != len(positions) or min(positions) < 1:
        raise ValueError("Selecione ao menos um MPPT físico, sem repetições.")
    available = primes(max(positions))
    product = math.prod(available[position - 1] for position in positions)
    if product > 2_147_483_647:
        raise ValueError("O índice dos MPPTs excede a capacidade INTEGER do SQLite.")
    return product


def decode_mppt_index(index, tracker_count):
    """Decodifica índices; zero é a sentinela legada para todos os MPPTs."""
    if tracker_count < 1:
        raise ValueError("Quantidade de MPPTs inválida.")
    if index == 0:
        return tuple(range(1, tracker_count + 1))
    if not isinstance(index, int) or index <= 1:
        raise ValueError("Índice MPPT inválido.")
    remaining, positions = index, []
    for position, prime in enumerate(primes(tracker_count), 1):
        if remaining % prime == 0:
            remaining //= prime
            if remaining % prime == 0:
                raise ValueError("Índice MPPT contém fator primo repetido.")
            positions.append(position)
    if remaining != 1:
        raise ValueError("Índice MPPT contém MPPT fora da faixa ou resíduo inválido.")
    if not positions:
        raise ValueError("Grupo MPPT vazio.")
    return tuple(positions)


def _known(value):
    return value is not None and value != -1


def validate_inverter_draft(draft):
    errors = []
    inverter = draft.get("inverter", draft)
    groups = draft.get("mppts", ())
    for name, label in (("MODEL", "Modelo"), ("MANUFACTURER_ID", "Fabricante"),
                        ("COOLING_MODE", "Refrigeração"),
                        ("PROTECTION_DEGREE", "Grau de proteção"),
                        ("TOPOLOGY", "Topologia")):
        if inverter.get(name) in (None, "", -1):
            errors.append(f"{label} é obrigatório.")
    if inverter.get("ACTIVE") not in (0, 1):
        errors.append("Status deve ser Ativo ou Inativo.")
    try:
        trackers = parse_number(inverter.get("NUMBER_OF_TRACKERS"), integer=True,
                                required=True, positive=True, field="Total de MPPTs")
        inputs = parse_number(inverter.get("NUMBER_OF_INPUTS"), integer=True,
                              required=True, positive=True, field="Total de entradas")
    except ValueError as exc:
        errors.append(str(exc)); trackers = inputs = 0
    seen, weighted_inputs = set(), 0
    for number, group in enumerate(groups, 1):
        try:
            positions = tuple(group.get("positions") or
                              decode_mppt_index(group.get("MPPT_INDEX"), trackers))
            index = encode_mppt_index(positions)
            if decode_mppt_index(index, trackers) != tuple(sorted(positions)):
                raise ValueError("Atribuição MPPT inválida.")
            overlap = seen.intersection(positions)
            if overlap:
                errors.append(f"Grupo {number}: MPPT(s) repetido(s): {sorted(overlap)}.")
            seen.update(positions)
        except (TypeError, ValueError) as exc:
            errors.append(f"Grupo {number}: {exc}"); positions = ()
        try:
            per_mppt = parse_number(group.get("NUMBER_OF_INPUTS"), integer=True,
                                    required=True, positive=True,
                                    field=f"Entradas do grupo {number}")
            weighted_inputs += per_mppt * len(positions)
        except ValueError as exc:
            errors.append(str(exc))
    if trackers:
        missing = set(range(1, trackers + 1)) - seen
        outside = seen - set(range(1, trackers + 1))
        if missing:
            errors.append(f"MPPTs sem grupo: {sorted(missing)}.")
        if outside:
            errors.append(f"MPPTs fora da faixa: {sorted(outside)}.")
    if inputs and weighted_inputs != inputs:
        errors.append(f"Total ponderado de entradas é {weighted_inputs}, mas o inversor declara {inputs}.")
    for key, allowed, label in (("systems", SYSTEM_OPTIONS, "Sistema"),
                                ("communications", COMMUNICATION_OPTIONS, "Comunicação"),
                                ("output_modes", OUTPUT_OPTIONS, "Modo de saída")):
        values = tuple(draft.get(key, ()))
        if len(values) != len(set(values)):
            errors.append(f"{label}: relacionamentos duplicados.")
        invalid = set(values) - set(allowed)
        if invalid:
            errors.append(f"{label}: opção indisponível no schema: {sorted(invalid)}.")
    if errors:
        raise CatalogValidationError(errors)
    return {"trackers": trackers, "inputs": inputs, "weighted_inputs": weighted_inputs}
