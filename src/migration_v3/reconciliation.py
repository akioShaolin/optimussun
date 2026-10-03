import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


ALLOWED_VOLTAGE_REFERENCES = {"LINE_TO_LINE", "LINE_TO_NEUTRAL", "UNRESOLVED"}
ALLOWED_CORRECTIONS = {
    "RATED_ACTIVE_POWER", "MAX_ACTIVE_POWER", "RATED_CURRENT", "MAX_CURRENT",
    "RATED_LINE_TO_LINE_VOLTAGE", "RATED_LINE_TO_NEUTRAL_VOLTAGE",
}


def empty_reconciliation():
    return {"version": 1, "profiles": []}


def load_reconciliation(path=None):
    data = empty_reconciliation() if path is None else json.loads(Path(path).read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or type(data.get("version")) is not int
            or data.get("version") != 1 or not isinstance(data.get("profiles"), list)):
        raise ValueError("Reconciliação deve conter version=1 e uma lista profiles.")
    if set(data) != {"version", "profiles"}:
        raise ValueError("Reconciliação contém campos de topo desconhecidos.")
    indexed = {}
    defaults = {}
    for item in data["profiles"]:
        if not isinstance(item, dict):
            raise ValueError("Cada decisão de perfil deve ser um objeto.")
        allowed = {"inverter_id", "output_mode", "active", "is_default",
                   "voltage_reference", "source", "corrections"}
        required = {"inverter_id", "output_mode", "source"}
        unknown_item = set(item) - allowed
        if unknown_item:
            raise ValueError(f"Campos desconhecidos na decisão: {sorted(unknown_item)}")
        missing_item = required - set(item)
        if missing_item:
            raise ValueError(f"Campos obrigatórios ausentes na decisão: {sorted(missing_item)}")
        if type(item["inverter_id"]) is not int or item["inverter_id"] < 1:
            raise ValueError("inverter_id deve ser um inteiro positivo.")
        inverter_id = item["inverter_id"]
        if not isinstance(item["output_mode"], str) or not item["output_mode"].strip():
            raise ValueError(f"output_mode deve ser texto não vazio para inversor {inverter_id}.")
        output_mode = item["output_mode"].strip()
        key = (inverter_id, output_mode)
        if key in indexed:
            raise ValueError(f"Decisão duplicada para inversor/modo {key}.")
        for boolean_field in ("active", "is_default"):
            if boolean_field in item and type(item[boolean_field]) is not bool:
                raise ValueError(f"{boolean_field} deve ser booleano em {key}.")
        if item.get("is_default") is True and item.get("active") is False:
            raise ValueError(f"is_default=true exige active=true em {key}.")
        reference = item.get("voltage_reference", "UNRESOLVED")
        if not isinstance(reference, str) or reference not in ALLOWED_VOLTAGE_REFERENCES:
            raise ValueError(f"Referência de tensão inválida em {key}: {reference}")
        corrections = item.get("corrections", {})
        if not isinstance(corrections, dict):
            raise ValueError(f"corrections deve ser um objeto em {key}.")
        unknown = set(corrections) - ALLOWED_CORRECTIONS
        if unknown:
            raise ValueError(f"Correções desconhecidas em {key}: {sorted(unknown)}")
        for field, value in corrections.items():
            try:
                decimal_value = Decimal(str(value))
            except (InvalidOperation, ValueError):
                raise ValueError(f"Correção decimal inválida para {field} em {key}.") from None
            if not decimal_value.is_finite() or decimal_value < 0:
                raise ValueError(f"Correção decimal inválida para {field} em {key}.")
        if not isinstance(item["source"], str) or not item["source"].strip():
            raise ValueError(f"Decisão de perfil exige source em {key}.")
        if item.get("is_default"):
            if defaults.get(inverter_id):
                raise ValueError(f"Mais de um padrão informado para inversor {inverter_id}.")
            defaults[inverter_id] = key
        indexed[key] = item
    canonical_data = {
        "version": 1,
        "profiles": sorted(data["profiles"],
                           key=lambda profile: (int(profile["inverter_id"]),
                                                str(profile["output_mode"]).strip())),
    }
    canonical = json.dumps(canonical_data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return indexed, hashlib.sha256(canonical.encode("utf-8")).hexdigest(), data

