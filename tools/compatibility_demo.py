"""Interface provisória para validação manual do motor de compatibilidade."""

import sqlite3
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
DB_PATH = SRC_DIR / "optimus_sun.db"
sys.path.insert(0, str(SRC_DIR))

from compatibility import (  # noqa: E402
    CompatibilityOptions,
    compare_operating_current_modes,
    load_inverter,
    load_module,
)


def open_database():
    """Abre o banco-base sem permitir alterações."""
    return sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True)


def active_equipment(connection, table):
    """Retorna pares modelo/ID ativos, ordenados para os comboboxes."""
    return connection.execute(
        f"SELECT MODEL, ID FROM {table} WHERE ACTIVE = 1 "
        "ORDER BY MODEL COLLATE NOCASE, ID"
    ).fetchall()


def format_result(result):
    """Converte exclusivamente os campos públicos do resultado em texto."""
    lines = [
        f"Quantidade total: {result.quantity}",
        f"Potência DC: {result.dc_power_kw:.2f} kW",
        f"Sobrecarga: {result.overload_percent:.2f}%",
        f"Fator limitante: {result.limiting_factor.value}",
        f"Total de strings: {result.total_strings}",
        "Módulos por string: "
        + (", ".join(map(str, result.modules_per_string)) or "—"),
        "",
        "Distribuição por MPPT:",
    ]
    used = [item for item in result.mppt_results if item.strings]
    if not used:
        lines.append("  Nenhuma string válida")
    else:
        for item in used:
            lines.append(
                f"  MPPT {item.index}, ocorrência {item.occurrence}: "
                f"{item.strings} string(s) × {item.modules_per_string} "
                f"módulo(s) = {item.quantity}"
            )
    return "\n".join(lines)


class CompatibilityDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Optimus Sun — teste do motor de compatibilidade")
        self.geometry("1080x650")
        self.minsize(850, 560)

        with open_database() as connection:
            self.inverters = active_equipment(connection, "inverter")
            self.modules = active_equipment(connection, "module")

        self.inverter_by_label = self._display_map(self.inverters)
        self.module_by_label = self._display_map(self.modules)
        self.overload_mode = tk.StringVar(value="registered")
        self.custom_overload = tk.StringVar(value="50")
        self.difference = tk.StringVar(value="Diferença de quantidade: —")

        self._build_interface()
        self._select_default(self.inverter_combo, "SIW400G K025 W00")
        self._select_default(self.module_combo, "WPV 610 H66MBN3")
        self._update_overload_state()

    @staticmethod
    def _display_map(rows):
        counts = {}
        for model, _ in rows:
            counts[model] = counts.get(model, 0) + 1
        return {
            f"{model} (ID {item_id})" if counts[model] > 1 else model: item_id
            for model, item_id in rows
        }

    @staticmethod
    def _select_default(combo, model):
        match = next((value for value in combo["values"] if value == model), None)
        if match is not None:
            combo.set(match)
        elif combo["values"]:
            combo.current(0)

    def _build_interface(self):
        selection = ttk.LabelFrame(self, text="Equipamentos e sobrecarga", padding=12)
        selection.pack(fill="x", padx=12, pady=(12, 6))
        selection.columnconfigure(1, weight=1)
        selection.columnconfigure(3, weight=1)

        ttk.Label(selection, text="Inversor ativo:").grid(row=0, column=0, sticky="w")
        self.inverter_combo = ttk.Combobox(
            selection,
            state="readonly",
            values=tuple(self.inverter_by_label),
        )
        self.inverter_combo.grid(row=0, column=1, sticky="ew", padx=(6, 18))

        ttk.Label(selection, text="Módulo ativo:").grid(row=0, column=2, sticky="w")
        self.module_combo = ttk.Combobox(
            selection,
            state="readonly",
            values=tuple(self.module_by_label),
        )
        self.module_combo.grid(row=0, column=3, sticky="ew", padx=(6, 0))

        ttk.Radiobutton(
            selection,
            text="Sobrecarga cadastrada",
            variable=self.overload_mode,
            value="registered",
            command=self._update_overload_state,
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Radiobutton(
            selection,
            text="Sobrecarga personalizada",
            variable=self.overload_mode,
            value="custom",
            command=self._update_overload_state,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

        custom_frame = ttk.Frame(selection)
        custom_frame.grid(row=2, column=2, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(custom_frame, text="Percentual:").pack(side="left")
        self.custom_entry = ttk.Entry(
            custom_frame, textvariable=self.custom_overload, width=10
        )
        self.custom_entry.pack(side="left", padx=6)
        ttk.Label(custom_frame, text="%").pack(side="left")

        ttk.Button(selection, text="Calcular", command=self.calculate).grid(
            row=1, column=3, sticky="e", pady=(12, 0)
        )

        results = ttk.Frame(self)
        results.pack(fill="both", expand=True, padx=12, pady=6)
        results.columnconfigure(0, weight=1, uniform="result")
        results.columnconfigure(1, weight=1, uniform="result")
        results.rowconfigure(0, weight=1)

        normal_frame = ttk.LabelFrame(results, text="Modo normal", padding=8)
        normal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ignored_frame = ttk.LabelFrame(
            results, text="Ignorando corrente de operação", padding=8
        )
        ignored_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.normal_text = self._result_text(normal_frame)
        self.ignored_text = self._result_text(ignored_frame)

        ttk.Label(self, textvariable=self.difference, font=("Segoe UI", 11, "bold")).pack(
            pady=(4, 12)
        )

    @staticmethod
    def _result_text(parent):
        text = tk.Text(parent, wrap="word", state="disabled", padx=8, pady=8)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return text

    def _update_overload_state(self):
        state = "normal" if self.overload_mode.get() == "custom" else "disabled"
        self.custom_entry.configure(state=state)

    @staticmethod
    def _show(text_widget, content):
        text_widget.configure(state="normal")
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", content)
        text_widget.configure(state="disabled")

    def _options(self):
        if self.overload_mode.get() == "registered":
            return CompatibilityOptions()
        raw_value = self.custom_overload.get().strip().replace(",", ".")
        try:
            value = float(raw_value)
        except ValueError as error:
            raise ValueError("Informe um percentual de sobrecarga válido.") from error
        if value < 0:
            raise ValueError("O percentual de sobrecarga não pode ser negativo.")
        return CompatibilityOptions(custom_overload_percent=value)

    def calculate(self):
        inverter_id = self.inverter_by_label.get(self.inverter_combo.get())
        module_id = self.module_by_label.get(self.module_combo.get())
        if inverter_id is None or module_id is None:
            messagebox.showwarning("Seleção incompleta", "Selecione um inversor e um módulo.")
            return
        try:
            options = self._options()
            with open_database() as connection:
                inverter = load_inverter(connection, inverter_id)
                module = load_module(connection, module_id)
            normal, ignored = compare_operating_current_modes(
                inverter, module, options
            )
        except (ValueError, LookupError, sqlite3.Error) as error:
            messagebox.showerror("Não foi possível calcular", str(error))
            return

        self._show(self.normal_text, format_result(normal))
        self._show(self.ignored_text, format_result(ignored))
        self.difference.set(
            "Diferença de quantidade (ignorando − normal): "
            f"{ignored.quantity - normal.quantity:+d} módulo(s)"
        )


if __name__ == "__main__":
    CompatibilityDemo().mainloop()
