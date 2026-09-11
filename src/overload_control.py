"""Estado de sessão e validação da sobrecarga usada pela GUI principal."""

from __future__ import annotations

import math
from dataclasses import dataclass


def parse_overload_percent(value):
    """Interpreta uma entrada percentual; 50 representa acréscimo de 50%."""
    if value is None or not str(value).strip():
        raise ValueError("Informe a sobrecarga personalizada em percentual.")
    text = str(value).strip()
    if "," in text and "." in text:
        raise ValueError("Use ponto ou vírgula somente como separador decimal.")
    try:
        percent = float(text.replace(",", "."))
    except ValueError as error:
        raise ValueError("A sobrecarga deve ser um número.") from error
    if not math.isfinite(percent):
        raise ValueError("NaN e infinito não são aceitos.")
    if percent < 0:
        raise ValueError("A sobrecarga não pode ser negativa.")
    return percent


def valid_registered_percent(value):
    return value not in (None, -1, "-1") and isinstance(value, (int, float)) and math.isfinite(value) and value >= 0


@dataclass
class OverloadSession:
    inverter_id: int | None = None
    registered_percent: float | None = None
    mode: str = "registered"
    custom_text: str = ""

    def select_inverter(self, inverter_id, registered_percent):
        """Novo inversor sempre restaura o modo cadastrado e limpa heranças."""
        self.inverter_id = inverter_id
        self.registered_percent = registered_percent
        self.mode = "registered"
        self.custom_text = ""

    def clear(self):
        self.select_inverter(None, None)

    def effective_percent(self):
        if self.mode == "custom":
            return parse_overload_percent(self.custom_text)
        if not valid_registered_percent(self.registered_percent):
            raise ValueError("Este inversor não possui sobrecarga cadastrada. Informe um valor personalizado.")
        return float(self.registered_percent)

    def effective_fraction(self):
        return self.effective_percent() / 100


def bind_overload_entry(entry, on_edit, on_apply):
    """Liga edição/Enter sem invalidar o resultado após o KeyRelease do Enter."""
    def key_released(event):
        if event.keysym in ("Return", "KP_Enter"):
            return "break"
        return on_edit(event)

    def enter_pressed(event):
        on_apply(event)
        return "break"

    entry.bind("<KeyRelease>", key_released)
    entry.bind("<Return>", enter_pressed)
    entry.bind("<KP_Enter>", enter_pressed)
    return key_released, enter_pressed
