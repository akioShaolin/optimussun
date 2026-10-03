import math
from decimal import Decimal, InvalidOperation
from functools import lru_cache


UINT64_MAX = 18_446_744_073_709_551_615


class DomainValidationError(ValueError):
    pass


@lru_cache(maxsize=32)
def _primes(count):
    if count < 1:
        return ()
    limit = 15 if count < 6 else int(count * (math.log(count) + math.log(math.log(count)))) + 10
    while True:
        sieve = bytearray(b"\x01") * (limit + 1)
        sieve[0:2] = b"\x00\x00"
        for prime in range(2, math.isqrt(limit) + 1):
            if sieve[prime]:
                start = prime * prime
                sieve[start:limit + 1:prime] = b"\x00" * (((limit - start) // prime) + 1)
        result = tuple(index for index, is_prime in enumerate(sieve) if is_prime)
        if len(result) >= count:
            return result[:count]
        limit *= 2


def decode_group(code, count):
    if type(code) is not int or type(count) is not int or count < 1:
        raise ValueError("Código ou quantidade de posições inválida.")
    if code == 0:
        return set(range(1, count + 1))
    if code == 1 or code < 0 or code > UINT64_MAX:
        raise ValueError("Código fora do domínio BIGINT UNSIGNED ou igual a 1.")
    remaining = code
    positions = set()
    for position, prime in enumerate(_primes(count), 1):
        occurrences = 0
        while remaining % prime == 0:
            remaining //= prime
            occurrences += 1
        if occurrences > 1:
            raise ValueError(f"Fator repetido para a posição {position}.")
        if occurrences:
            positions.add(position)
        if remaining == 1:
            break
    if remaining != 1 or not positions:
        raise ValueError("Código contém posição inexistente ou fator residual.")
    return positions


def validate_battery_groups(groups, input_count):
    """Validate the set of active battery-input groups for one inverter."""
    active = [row for row in groups if row.get("ACTIVE") in (1, True)]
    if not active:
        return True
    if type(input_count) is not int or not 1 <= input_count <= 65535:
        raise DomainValidationError(["Grupos ativos exigem quantidade de entradas de bateria válida."])
    occupied = set()
    errors = []
    for row in active:
        try:
            positions = decode_group(row.get("BATTERY_INDEX"), input_count)
        except (TypeError, ValueError):
            errors.append(f"Grupo de bateria {row.get('ID')} possui índice inválido.")
            continue
        if occupied & positions:
            errors.append(f"Grupo de bateria {row.get('ID')} sobrepõe outro grupo ativo.")
        occupied |= positions
    if errors:
        raise DomainValidationError(errors)
    return True


def _positive(value):
    if value is None:
        return False
    try:
        return Decimal(str(value)) > 0
    except (InvalidOperation, ValueError):
        return False


def validate_ac_input(profile, system_types):
    errors = []
    systems = {str(value).strip().upper() for value in system_types}
    if profile.get("PROFILE_TYPE") != "AC_INPUT":
        errors.append("PROFILE_TYPE deve ser AC_INPUT.")
    if "HYBRID" not in systems:
        errors.append("AC_INPUT ativo exige inversor classificado como HYBRID.")
    if profile.get("ACTIVE") not in (1, True):
        errors.append("AC_INPUT disponível exige ACTIVE=TRUE.")
    if profile.get("IS_DEFAULT") not in (0, False):
        errors.append("AC_INPUT nunca pode ser perfil padrão.")
    if profile.get("OUTPUT_MODE_ID") is not None:
        errors.append("AC_INPUT não aceita OUTPUT_MODE_ID.")
    nominal = ("RATED_ACTIVE_POWER", "RATED_CURRENT", "RATED_LINE_TO_LINE_VOLTAGE",
               "RATED_LINE_TO_NEUTRAL_VOLTAGE")
    if not any(_positive(profile.get(field)) for field in nominal):
        errors.append("AC_INPUT exige ao menos uma grandeza nominal positiva.")
    if errors:
        raise DomainValidationError(errors)
    return True


def validate_output_profile(profile, system_types):
    errors = []
    profile_type = profile.get("PROFILE_TYPE")
    systems = {str(value).strip().upper() for value in system_types}
    if profile_type not in {"AC_OUTPUT", "EPS_OUTPUT"}:
        errors.append("Perfil de saída deve ser AC_OUTPUT ou EPS_OUTPUT.")
    if profile.get("ACTIVE") not in (1, True):
        errors.append("Perfil de saída disponível exige ACTIVE=TRUE.")
    if profile.get("OUTPUT_MODE_ID") is None:
        errors.append("Perfil de saída ativo exige OUTPUT_MODE_ID.")
    if not _positive(profile.get("RATED_ACTIVE_POWER")):
        errors.append("Perfil de saída ativo exige potência nominal positiva.")
    if profile_type == "AC_OUTPUT" and not systems.intersection({"ON-GRID", "GRIDZERO", "HYBRID"}):
        errors.append("AC_OUTPUT ativo exige classificação ON-GRID, GRIDZERO ou HYBRID.")
    if profile_type == "EPS_OUTPUT" and not systems.intersection({"OFF-GRID", "HYBRID"}):
        errors.append("EPS_OUTPUT ativo exige classificação OFF-GRID ou HYBRID.")
    if errors:
        raise DomainValidationError(errors)
    return True


def output_profile_is_ready(profile, system_types, active_output_mode_ids):
    if profile.get("IS_DEFAULT") not in (1, True):
        return False
    if profile.get("OUTPUT_MODE_ID") not in set(active_output_mode_ids):
        return False
    try:
        validate_output_profile(profile, system_types)
    except DomainValidationError:
        return False
    return True

