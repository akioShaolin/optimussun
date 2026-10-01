"""Interface da Matriz de Compatibilidade do Optimus Sun."""

import queue
import math
import sqlite3
import sys
import threading
import tkinter as tk
import time
from contextlib import closing
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"


def external_path(filename):
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / filename
    return SRC_DIR / filename


DB_PATH = external_path("optimus_sun.db")
sys.path.insert(0, str(SRC_DIR))

from version import APP_VERSION  # noqa: E402

from compatibility import (  # noqa: E402
    CompatibilityMatrix,
    CompatibilityOptions,
    CSVFormatError,
    ImportedCellResult,
    LimitingFactor,
    export_matrix_csv,
    import_matrix_csv,
    list_active_inverters,
    list_active_modules,
)
from focus_navigation import prepare_toplevel  # noqa: E402
from compatibility.matrix import MatrixCalculationCancelled  # noqa: E402


COLORS = {
    "background": "#F4F7FA",
    "surface": "#FFFFFF",
    "surface_alt": "#E8EEF5",
    "primary": "#1F4E78",
    "text": "#17212B",
    "muted": "#5D6B78",
    "border": "#CBD5E1",
    "success": "#2E7D32",
    "warning": "#D97706",
    "error": "#C62828",
    "ignored": "#8A94A3",
}


FACTOR_LABELS = {
    LimitingFactor.OVERLOAD_LIMIT: "Limite de sobrecarga",
    LimitingFactor.OPERATING_CURRENT: "Corrente de operação",
    LimitingFactor.SHORT_CIRCUIT_CURRENT: "Corrente de curto-circuito",
    LimitingFactor.INPUT_COUNT: "Quantidade de entradas",
    LimitingFactor.ALL_STRINGS_OCCUPIED: "Entradas/strings totalmente ocupadas",
    LimitingFactor.MAX_SERIES_VOLTAGE: "Tensão máxima em série",
    LimitingFactor.MPPT_VOLTAGE_RANGE: "Faixa de tensão do MPPT",
    LimitingFactor.FULL_LOAD_RANGE: "Faixa de carga máxima (Full Load)",
    LimitingFactor.INSUFFICIENT_SERIES_VOLTAGE: "Tensão insuficiente para nova string",
    LimitingFactor.MISSING_DATA: "Dados insuficientes",
}


def open_database():
    return closing(sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True))


def equipment_label(equipment):
    return f"{equipment.manufacturer} — {equipment.model}"


def selected_equipment(combobox, equipment):
    index = combobox.current()
    return equipment[index] if 0 <= index < len(equipment) else None


def decimal_pt(value, places=2):
    return f"{value:.{places}f}".replace(".", ",")


def overload_ratio(percent):
    """Converte uma única vez o percentual interno para razão de exibição."""
    return decimal_pt(percent / 100, 2)


def overload_percent_from_ratio(ratio):
    """Converte a entrada visível para a unidade interna do motor."""
    return ratio * 100


def overload_percent_label(percent):
    return f"{decimal_pt(percent, 2)}%"


def matrix_values(cell):
    result = cell.display_result
    invalid = (
        not result.valid
        if isinstance(cell, ImportedCellResult)
        else result.limiting_factor == LimitingFactor.MISSING_DATA
    )
    if invalid:
        return "N/D", "N/D", "N/D"
    if result.quantity == 0:
        return "Não suporta", "0", "-"
    if cell.uses_ignored_result:
        quantity = f"{cell.normal.quantity} → {cell.ignored.quantity} ↗"
    else:
        quantity = str(result.quantity)
    return (
        quantity,
        decimal_pt(result.dc_power_kw),
        overload_percent_label(result.overload_percent),
    )


def result_details(result):
    if result.limiting_factor == LimitingFactor.MISSING_DATA:
        quantity = power = overload = "N/D"
    elif result.quantity == 0:
        quantity, power, overload = "Não suporta", "0 kW", "—"
    else:
        quantity = str(result.quantity)
        power = f"{decimal_pt(result.dc_power_kw)} kW"
        overload = overload_percent_label(result.overload_percent)
    lines = [
        f"Quantidade: {quantity}",
        f"Potência DC: {power}",
        f"Sobrecarga: {overload}",
        f"Fator limitante: {FACTOR_LABELS[result.limiting_factor]}",
        f"Código: {result.limiting_factor.value}",
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


def overload_label(selection):
    if selection.overload_mode == "custom":
        return f"Personalizada ({overload_percent_label(selection.custom_overload_percent)})"
    if not selection.associated:
        return "Pendente de associação"
    registered = selection.equipment.overload_percent
    return (
        f"Cadastrada ({overload_percent_label(registered)})"
        if registered is not None
        else "Cadastrada (N/D)"
    )


def imported_details(cell):
    value = cell.imported_value
    if not value.valid:
        values = "Quantidade: N/D\nPotência DC: N/D\nSobrecarga: N/D"
    elif value.quantity == 0:
        values = "Quantidade: Não suporta\nPotência DC: 0 kW\nSobrecarga: —"
    else:
        values = (
            f"Quantidade: {value.quantity}\n"
            f"Potência DC: {decimal_pt(value.dc_power_kw)} kW\n"
            f"Sobrecarga: {overload_percent_label(value.overload_percent)}"
        )
    return (
        "Valor importado de CSV.\n\n"
        f"{values}\n\n"
        "Detalhes técnicos completos estarão disponíveis após recalcular a matriz."
    )


class OverloadScaleDialog(tk.Toplevel):
    """Escolha inequívoca para CSV sem unidade no cabeçalho/valor."""
    def __init__(self, parent):
        opener = parent.focus_get() or parent
        super().__init__(parent); self.result = None
        self.title("Escala da sobrecarga no CSV"); self.transient(parent); self.resizable(False, False)
        body = ttk.Frame(self, padding=16); body.pack(fill="both", expand=True)
        ttk.Label(body, text="O arquivo não identifica a escala da sobrecarga.", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(body, text="Escolha como interpretar os valores numéricos sem %:").pack(anchor="w", pady=(4, 14))
        first_button = ttk.Button(body, text="Decimal — exemplo: 0,50 = 50%", command=lambda: self._finish("ratio"), width=38)
        first_button.pack(fill="x", pady=3)
        ttk.Button(body, text="Percentual — exemplo: 50 = 50%", command=lambda: self._finish("percent"), width=38).pack(fill="x", pady=3)
        ttk.Button(body, text="Cancelar — não importar", command=self._cancel, width=38).pack(fill="x", pady=(10, 3))
        self.protocol("WM_DELETE_WINDOW", self._cancel); self.bind("<Escape>", lambda _event: self._cancel())
        self.grab_set(); prepare_toplevel(self, opener=opener, initial=first_button)

    def _finish(self, scale):
        self.result = scale; self.destroy()

    def _cancel(self):
        self.result = None; self.destroy()


class OverloadDialog(tk.Toplevel):
    def __init__(self, parent, selection):
        opener = parent.focus_get() or parent.inverter_tree
        super().__init__(parent)
        self.title("Configurar sobrecarga da ocorrência")
        self.resizable(False, False)
        self.transient(parent)
        self.result = None
        self.mode = tk.StringVar(value=selection.overload_mode)
        initial = (
            selection.custom_overload_percent
            if selection.custom_overload_percent is not None
            else selection.equipment.overload_percent
        )
        if initial is None:
            initial = 0
        self.percent = tk.StringVar(value=decimal_pt(initial, 2))

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"Inversor: {selection.equipment.model}").grid(
            row=0, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(body, text=f"Texto: {selection.display_label}").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(2, 12)
        )
        registered_radio = ttk.Radiobutton(
            body,
            text=(
                f"Usar cadastrada: {overload_percent_label(selection.equipment.overload_percent)}"
                if selection.equipment.overload_percent is not None
                else "Usar cadastrada: N/D"
            ),
            variable=self.mode,
            value="registered",
            command=self._update_state,
        )
        registered_radio.grid(row=2, column=0, columnspan=3, sticky="w")
        custom_radio = ttk.Radiobutton(
            body,
            text="Personalizada:",
            variable=self.mode,
            value="custom",
            command=self._update_state,
        )
        custom_radio.grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.entry = ttk.Entry(body, textvariable=self.percent, width=12)
        self.entry.grid(row=3, column=1, padx=5, pady=(8, 0))
        ttk.Label(body, text="%").grid(row=3, column=2, pady=(8, 0))
        buttons = ttk.Frame(body)
        buttons.grid(row=4, column=0, columnspan=3, sticky="e", pady=(16, 0))
        ttk.Button(buttons, text="Cancelar", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Confirmar", command=self._confirm).pack(
            side="right", padx=(0, 6)
        )
        self._update_state()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()
        self.update_idletasks()
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - self.winfo_width()) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - self.winfo_height()) // 2)
        self.geometry(f"+{x}+{y}")
        prepare_toplevel(
            self,
            opener=opener,
            initial=custom_radio if self.mode.get() == "custom" else registered_radio,
        )

    def _update_state(self):
        self.entry.configure(state="normal" if self.mode.get() == "custom" else "disabled")

    def _confirm(self):
        if self.mode.get() == "registered":
            self.result = ("registered", None)
            self.destroy()
            return
        try:
            value = float(self.percent.get().strip().replace(",", "."))
        except ValueError:
            messagebox.showerror("Valor inválido", "Informe um percentual válido.", parent=self)
            return
        if not math.isfinite(value) or value < 0:
            messagebox.showerror(
                "Valor inválido", "O percentual deve ser um número não negativo.", parent=self
            )
            return
        self.result = ("custom", value)
        self.destroy()


class CompatibilityMatrixGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Optimus Sun {APP_VERSION} — Matriz de Compatibilidade")
        self.geometry("1380x820")
        self.minsize(960, 640)
        self.configure(background=COLORS["background"])
        self._configure_styles()
        self.state_model = CompatibilityMatrix()
        self.calculation = None
        self.calculating = False
        self._closing = False
        self.worker_queue = queue.Queue(maxsize=32)
        self._job_id = 0
        self._cancel_event = None
        self._poll_after = None
        self._paint_after = None
        self._viewport_generation = 0
        self._previous_calculation = None
        self._worker_thread = None

        with open_database() as connection:
            self.available_inverters = list_active_inverters(connection)
            self.available_modules = list_active_modules(connection)

        self.status_text = tk.StringVar(value="Monte a seleção e clique em Calcular matriz.")
        self._build_interface()
        self._update_action_states()
        self.protocol("WM_DELETE_WINDOW", self._close_window)

    def _close_window(self):
        self._closing = True
        if self._cancel_event is not None:
            self._cancel_event.set()
        for callback in (self._poll_after, self._paint_after):
            if callback is not None:
                try:
                    self.after_cancel(callback)
                except tk.TclError:
                    pass
        self._poll_after = None
        self._paint_after = None
        self.destroy()

    def _configure_styles(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure(".", font=("Segoe UI", 9), foreground=COLORS["text"])
        style.configure("TFrame", background=COLORS["background"])
        style.configure("TLabelframe", background=COLORS["surface"], padding=8)
        style.configure(
            "TLabelframe.Label",
            background=COLORS["surface"],
            foreground=COLORS["primary"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure("TButton", padding=(9, 5), font=("Segoe UI", 9))
        style.configure("TCombobox", padding=3, font=("Segoe UI", 9))
        style.configure(
            "Treeview", rowheight=24, font=("Segoe UI", 9), background=COLORS["surface"]
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            foreground=COLORS["primary"],
        )

    def _build_interface(self):
        controls = ttk.Frame(self, padding=(10, 10, 10, 4))
        controls.pack(fill="x")
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)

        self._build_inverter_controls(controls)
        self._build_module_controls(controls)
        self._build_calculation_controls(controls)
        self._build_matrix_area()

    def _build_inverter_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Inversores da matriz", padding=8)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        frame.columnconfigure(0, weight=1)
        self.inverter_combo = ttk.Combobox(
            frame,
            state="readonly",
            width=48,
            values=tuple(equipment_label(item) for item in self.available_inverters),
        )
        self.inverter_combo.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        if self.inverter_combo["values"]:
            self.inverter_combo.current(0)
        ttk.Button(frame, text="Adicionar", command=self.add_inverter).grid(
            row=0, column=1
        )

        self.inverter_tree = ttk.Treeview(
            frame,
            columns=("manufacturer", "model", "label", "overload"),
            show="headings",
            height=5,
            selectmode="browse",
        )
        self.inverter_tree.heading("manufacturer", text="Fabricante")
        self.inverter_tree.heading("model", text="Modelo real")
        self.inverter_tree.heading("label", text="Texto exibido")
        self.inverter_tree.heading("overload", text="Sobrecarga")
        self.inverter_tree.column("manufacturer", width=100, stretch=False)
        self.inverter_tree.column("model", width=180)
        self.inverter_tree.column("label", width=190)
        self.inverter_tree.column("overload", width=150, stretch=False)
        self.inverter_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=6)

        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Button(buttons, text="Editar texto", command=self.rename_inverter).pack(
            side="left"
        )
        ttk.Button(buttons, text="Sobrecarga", command=self.configure_overload).pack(
            side="left", padx=(6, 0)
        )
        ttk.Button(buttons, text="Associar", command=self.associate_inverter).pack(
            side="left", padx=(6, 0)
        )
        ttk.Button(buttons, text="Remover", command=self.remove_inverter).pack(
            side="left", padx=6
        )

    def _build_module_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Módulos da matriz", padding=8)
        frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        frame.columnconfigure(0, weight=1)
        self.module_combo = ttk.Combobox(
            frame,
            state="readonly",
            width=48,
            values=tuple(equipment_label(item) for item in self.available_modules),
        )
        self.module_combo.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        if self.module_combo["values"]:
            self.module_combo.current(0)
        ttk.Button(frame, text="Adicionar", command=self.add_module).grid(row=0, column=1)

        self.module_tree = ttk.Treeview(
            frame,
            columns=("manufacturer", "model"),
            show="headings",
            height=5,
            selectmode="browse",
        )
        self.module_tree.heading("manufacturer", text="Fabricante")
        self.module_tree.heading("model", text="Modelo — ordem das colunas")
        self.module_tree.column("manufacturer", width=120, stretch=False)
        self.module_tree.column("model", width=300)
        self.module_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=6)

        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=2, sticky="w")
        for text, destination in (
            ("Início", "start"),
            ("←", "left"),
            ("→", "right"),
            ("Fim", "end"),
        ):
            ttk.Button(
                buttons,
                text=text,
                command=lambda target=destination: self.move_module(target),
            ).pack(side="left", padx=(0, 4))
        ttk.Button(buttons, text="Remover", command=self.remove_module).pack(
            side="left", padx=(4, 0)
        )
        ttk.Button(buttons, text="Associar", command=self.associate_module).pack(
            side="left", padx=(6, 0)
        )

    def _build_calculation_controls(self, parent):
        frame = ttk.Frame(parent)
        frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(frame, text="Importar CSV", command=self.import_csv).pack(side="left")
        self.export_button = ttk.Button(
            frame, text="Exportar CSV", command=self.export_csv
        )
        self.export_button.pack(side="left", padx=6)
        self.calculate_button = ttk.Button(
            frame, text="Calcular matriz", command=self.start_calculation
        )
        self.calculate_button.pack(side="left")
        self.cancel_button = ttk.Button(frame, text="Cancelar", command=self.cancel_calculation, state="disabled")
        self.cancel_button.pack(side="left", padx=(6, 0))
        self.progress = ttk.Progressbar(frame, mode="determinate", maximum=100, length=150)
        self.progress.pack(side="left", padx=10)
        ttk.Label(frame, textvariable=self.status_text).pack(side="left", fill="x")

    def _build_matrix_area(self):
        outer = ttk.LabelFrame(
            self,
            text="Matriz — ↗ resultado obtido ignorando corrente de operação",
            padding=4,
        )
        outer.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        self.matrix_canvas = tk.Canvas(
            outer, highlightthickness=0, background=COLORS["background"]
        )
        x_scroll = ttk.Scrollbar(outer, orient="horizontal", command=self._xview)
        y_scroll = ttk.Scrollbar(outer, orient="vertical", command=self._yview)
        self.matrix_canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        self.matrix_canvas.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.matrix_canvas.bind("<Configure>", lambda _event: self._schedule_paint())
        self.matrix_canvas.bind("<Button-1>", self._matrix_click)
        self.matrix_canvas.create_text(20, 20, text="Adicione inversores e módulos para gerar a matriz.", anchor="nw")

    def _xview(self, *args):
        self.matrix_canvas.xview(*args)
        self._schedule_paint()

    def _yview(self, *args):
        self.matrix_canvas.yview(*args)
        self._schedule_paint()

    def _guard_busy(self):
        if self.calculating:
            messagebox.showinfo("Cálculo em andamento", "Aguarde o cálculo da matriz.")
            return False
        return True

    def add_inverter(self):
        if not self._guard_busy():
            return
        equipment = selected_equipment(self.inverter_combo, self.available_inverters)
        if equipment is None:
            return
        item = self.state_model.add_inverter(equipment)
        self.inverter_tree.insert(
            "",
            "end",
            iid=str(item.key),
            values=(
                equipment.manufacturer,
                equipment.model,
                item.display_label,
                overload_label(item),
            ),
        )
        self._selection_changed()

    def _selected_key(self, tree):
        selection = tree.selection()
        return int(selection[0]) if selection else None

    def rename_inverter(self):
        if not self._guard_busy():
            return
        key = self._selected_key(self.inverter_tree)
        if key is None:
            return
        current = next(item for item in self.state_model.inverters if item.key == key)
        label = simpledialog.askstring(
            "Editar texto do inversor",
            "Texto exibido na matriz:",
            initialvalue=current.display_label,
            parent=self,
        )
        if label is None:
            return
        try:
            self.state_model.rename_inverter(key, label)
        except ValueError as error:
            messagebox.showerror("Texto inválido", str(error))
            return
        values = list(self.inverter_tree.item(str(key), "values"))
        values[2] = label.strip()
        self.inverter_tree.item(str(key), values=values)
        self._selection_changed(preserve_imported=True)

    def configure_overload(self):
        if not self._guard_busy():
            return
        key = self._selected_key(self.inverter_tree)
        if key is None:
            return
        selection = next(item for item in self.state_model.inverters if item.key == key)
        if not selection.associated:
            messagebox.showinfo(
                "Associação necessária",
                "Associe esta linha a um inversor ativo antes de configurar a sobrecarga.",
                parent=self,
            )
            return
        dialog = OverloadDialog(self, selection)
        self.wait_window(dialog)
        if dialog.result is None:
            return
        mode, percent = dialog.result
        self.state_model.configure_inverter_overload(key, mode, percent)
        updated = next(item for item in self.state_model.inverters if item.key == key)
        values = list(self.inverter_tree.item(str(key), "values"))
        values[3] = overload_label(updated)
        self.inverter_tree.item(str(key), values=values)
        self._selection_changed(preserve_imported=True)

    def remove_inverter(self):
        if not self._guard_busy():
            return
        key = self._selected_key(self.inverter_tree)
        if key is not None:
            self.state_model.remove_inverter(key)
            self.inverter_tree.delete(str(key))
            self._selection_changed(preserve_imported=True)

    def add_module(self):
        if not self._guard_busy():
            return
        equipment = selected_equipment(self.module_combo, self.available_modules)
        if equipment is None:
            return
        item = self.state_model.add_module(equipment)
        self.module_tree.insert(
            "",
            "end",
            iid=str(item.key),
            values=(equipment.manufacturer, equipment.model),
        )
        self._selection_changed()

    def remove_module(self):
        if not self._guard_busy():
            return
        key = self._selected_key(self.module_tree)
        if key is not None:
            self.state_model.remove_module(key)
            self.module_tree.delete(str(key))
            self._selection_changed(preserve_imported=True)

    def move_module(self, destination):
        if not self._guard_busy():
            return
        key = self._selected_key(self.module_tree)
        if key is None:
            return
        self.state_model.move_module(key, destination)
        ordered_keys = [str(item.key) for item in self.state_model.modules]
        for position, item_id in enumerate(ordered_keys):
            self.module_tree.move(item_id, "", position)
        self.module_tree.selection_set(str(key))
        self._selection_changed(preserve_imported=True)

    def associate_inverter(self):
        if not self._guard_busy():
            return
        key = self._selected_key(self.inverter_tree)
        equipment = selected_equipment(self.inverter_combo, self.available_inverters)
        if key is None or equipment is None:
            return
        self.state_model.associate_inverter(key, equipment)
        self._refresh_selection_trees()
        self.inverter_tree.selection_set(str(key))
        self._selection_changed(preserve_imported=True)

    def associate_module(self):
        if not self._guard_busy():
            return
        key = self._selected_key(self.module_tree)
        equipment = selected_equipment(self.module_combo, self.available_modules)
        if key is None or equipment is None:
            return
        self.state_model.associate_module(key, equipment)
        self._refresh_selection_trees()
        self.module_tree.selection_set(str(key))
        self._selection_changed(preserve_imported=True)

    def _selection_changed(self, preserve_imported=False):
        if preserve_imported and self.calculation and self.calculation.source == "imported":
            try:
                self.calculation = self.state_model.snapshot_with_cells(self.calculation)
                self._render_matrix(lambda: self.status_text.set("Matriz importada — valores ainda não recalculados."))
                self._update_action_states()
                return
            except ValueError:
                pass
        self.calculation = None
        self._clear_matrix()
        self.matrix_canvas.create_text(20, 20, text="Seleção alterada. Calcule novamente a matriz.", anchor="nw")
        self.status_text.set("Seleção alterada — cálculo necessário.")
        self._update_action_states()

    def _refresh_selection_trees(self):
        self.inverter_tree.delete(*self.inverter_tree.get_children())
        for item in self.state_model.inverters:
            equipment = item.equipment
            self.inverter_tree.insert(
                "", "end", iid=str(item.key), values=(
                    equipment.manufacturer if equipment else "Não associado",
                    equipment.model if equipment else "—",
                    item.display_label,
                    overload_label(item),
                )
            )
        self.module_tree.delete(*self.module_tree.get_children())
        for item in self.state_model.modules:
            equipment = item.equipment
            self.module_tree.insert(
                "", "end", iid=str(item.key), values=(
                    equipment.manufacturer if equipment else "Não associado",
                    item.display_model,
                )
            )

    def import_csv(self):
        if not self._guard_busy():
            return
        path = filedialog.askopenfilename(
            parent=self,
            title="Importar matriz CSV",
            filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")),
        )
        if not path:
            return
        try:
            imported = import_matrix_csv(
                path, self.available_inverters, self.available_modules
            )
        except CSVFormatError as error:
            if "sobrecarga sem % é ambígua" not in str(error):
                messagebox.showerror("CSV inválido", str(error), parent=self)
                return
            dialog = OverloadScaleDialog(self)
            self.wait_window(dialog)
            if dialog.result is None:
                return
            try:
                imported = import_matrix_csv(
                    path, self.available_inverters, self.available_modules,
                    overload_scale=dialog.result,
                )
            except (OSError, CSVFormatError) as retry_error:
                messagebox.showerror("CSV inválido", str(retry_error), parent=self)
                return
        except OSError as error:
            messagebox.showerror("CSV inválido", str(error), parent=self)
            return
        self.state_model = imported.matrix
        self.calculation = imported.calculation
        self._refresh_selection_trees()
        self.status_text.set("Preparando visualização da matriz importada…")
        self._render_matrix(self._finish_import)
        pending_inverters = sum(not item.associated for item in self.state_model.inverters)
        pending_modules = sum(not item.associated for item in self.state_model.modules)
        self._import_status = (
            "Matriz importada — valores ainda não recalculados. "
            f"Pendências: {pending_inverters} inversor(es), {pending_modules} módulo(s)."
        )
        self._update_action_states()

    def _finish_import(self):
        self.progress["value"] = 100
        self.status_text.set(self._import_status)

    def export_csv(self):
        if self.calculation is None:
            return
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar matriz CSV",
            defaultextension=".csv",
            initialfile="compatibilidade_optimus_sun.csv",
            filetypes=(("Arquivos CSV", "*.csv"),),
        )
        if not path:
            return
        try:
            export_matrix_csv(self.calculation, path)
        except OSError as error:
            messagebox.showerror("Falha ao exportar", str(error), parent=self)
            return
        self.status_text.set(f"CSV exportado: {Path(path).name}")

    def _update_action_states(self):
        self.export_button.configure(
            state="normal" if self.calculation is not None else "disabled"
        )
        self.calculate_button.configure(
            text="Recalcular matriz"
            if self.calculation and self.calculation.source == "imported"
            else "Calcular matriz",
            state="disabled" if self.calculating else "normal",
        )

    def start_calculation(self):
        if self.calculating:
            return
        try:
            if not self.state_model.inverters or not self.state_model.modules:
                raise ValueError("Adicione ao menos um inversor e um módulo.")
            pending_inverters = [
                item.display_label
                for item in self.state_model.inverters
                if not item.associated
            ]
            pending_modules = [
                item.display_model for item in self.state_model.modules if not item.associated
            ]
            if pending_inverters or pending_modules:
                details = []
                if pending_inverters:
                    details.append("Inversores: " + ", ".join(pending_inverters))
                if pending_modules:
                    details.append("Módulos: " + ", ".join(pending_modules))
                raise ValueError(
                    "Associe os equipamentos antes de recalcular.\n" + "\n".join(details)
                )
        except ValueError as error:
            messagebox.showerror("Não foi possível calcular", str(error))
            return
        self.calculating = True
        self._previous_calculation = self.calculation
        self.calculate_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.progress["value"] = 0
        total = len(self.state_model.inverters) * len(self.state_model.modules)
        self.status_text.set(f"Preparando dados para {total} combinação(ões)…")
        self._job_id += 1
        job_id = self._job_id
        self._cancel_event = threading.Event()
        self.worker_queue = queue.Queue(maxsize=32)
        self._worker_thread = threading.Thread(
            target=self._calculate_worker, args=(job_id, self.state_model, self._cancel_event), daemon=True
        )
        self._worker_thread.start()
        self._poll_after = self.after(40, self._poll_worker)

    def cancel_calculation(self):
        if not self.calculating or self._cancel_event is None:
            return
        self._cancel_event.set()
        self.cancel_button.configure(state="disabled")
        self.status_text.set("Cancelando cálculo…")
        if self._poll_after is None:
            self._clear_matrix()
            self.calculation = self._previous_calculation
            if self.calculation is not None:
                self._render_matrix()
            self._finish_cancelled()

    def _calculate_worker(self, job_id, state_model, cancel_event):
        try:
            with open_database() as connection:
                calculation = state_model.calculate(
                    connection, CompatibilityOptions(),
                    progress=lambda done, total: self._queue_progress(job_id, done, total),
                    is_cancelled=cancel_event.is_set,
                )
            self._queue_terminal(job_id, "cancelled" if cancel_event.is_set() else "ok", calculation)
        except MatrixCalculationCancelled:
            self._queue_terminal(job_id, "cancelled", None)
        except Exception as error:
            self._queue_terminal(job_id, "error", error)

    def _queue_progress(self, job_id, done, total):
        try:
            self.worker_queue.put_nowait((job_id, "progress", (done, total)))
        except queue.Full:
            pass
        time.sleep(0.001)  # cede a vez ao event loop; nunca dorme na thread Tk

    def _queue_terminal(self, job_id, status, payload):
        item = (job_id, status, payload)
        while True:
            try:
                self.worker_queue.put_nowait(item)
                return
            except queue.Full:
                try:
                    self.worker_queue.get_nowait()  # descarta somente progresso antigo
                except queue.Empty:
                    pass

    def _poll_worker(self):
        self._poll_after = None
        if self._closing or not self.winfo_exists():
            return
        for _ in range(32):
            try:
                job_id, status, payload = self.worker_queue.get_nowait()
            except queue.Empty:
                break
            if job_id != self._job_id:
                continue
            if status == "progress":
                if not self._cancel_event.is_set():
                    done, total = payload
                    self.progress["value"] = 100 * done / total
                    self.status_text.set(f"Calculando {done} de {total} combinações…")
            elif status == "cancelled":
                self._finish_cancelled()
                return
            elif status == "error":
                self._finish_cancelled("Falha no cálculo.")
                messagebox.showerror("Não foi possível calcular", str(payload), parent=self)
                return
            else:
                if self._cancel_event.is_set():
                    self._finish_cancelled()
                    return
                self.calculation = payload
                self.status_text.set("Preparando visualização…")
                self.progress["value"] = 0
                self._render_matrix(self._finish_calculation)
                return
        self._poll_after = self.after(40, self._poll_worker)

    def _finish_cancelled(self, status="Cálculo cancelado; resultado anterior preservado."):
        self.calculating = False
        self._previous_calculation = None
        self.cancel_button.configure(state="disabled")
        self.progress["value"] = 0
        self.status_text.set(status)
        self._update_action_states()

    def _finish_calculation(self):
        if self._closing:
            return
        self.calculating = False
        self._previous_calculation = None
        self.cancel_button.configure(state="disabled")
        self.progress["value"] = 100
        self._update_action_states()
        self.status_text.set(
            f"Matriz pronta: {len(self.calculation.inverters)} × {len(self.calculation.modules)}."
        )

    def _clear_matrix(self):
        self._viewport_generation += 1
        if self._paint_after is not None:
            self.after_cancel(self._paint_after)
            self._paint_after = None
        self.matrix_canvas.delete("all")
        self.matrix_canvas.configure(scrollregion=(0, 0, 1, 1))

    def _render_matrix(self, on_complete=None):
        self._clear_matrix()
        calculation = self.calculation
        if calculation is None:
            return
        width = 280 + len(calculation.modules) * 360
        height = 84 + len(calculation.inverters) * 32
        self.matrix_canvas.configure(scrollregion=(0, 0, width, height))
        self._schedule_paint(on_complete)

    def _schedule_paint(self, on_complete=None):
        if self._closing or self._paint_after is not None or self.calculation is None:
            return
        generation = self._viewport_generation

        def paint():
            self._paint_after = None
            if self._closing or generation != self._viewport_generation:
                return
            self._paint_viewport()
            if on_complete is not None:
                on_complete()

        self._paint_after = self.after_idle(paint)

    def _draw_cell(self, x, y, width, height, value, *, header=False, stripe=False, anchor="center"):
        canvas = self.matrix_canvas
        canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=COLORS["surface_alt"] if header else COLORS["background"] if stripe else COLORS["surface"],
            outline=COLORS["border"], tags="matrix",
        )
        canvas.create_text(
            x + (8 if anchor == "w" else width / 2), y + height / 2,
            text=value, anchor="w" if anchor == "w" else "center",
            width=width - 12, fill=COLORS["primary"] if header else COLORS["text"],
            font=("Segoe UI", 9, "bold" if header else "normal"), tags="matrix",
        )

    def _paint_viewport(self):
        calculation = self.calculation
        if calculation is None:
            return
        canvas = self.matrix_canvas
        left = canvas.canvasx(0)
        top = canvas.canvasy(0)
        right = left + max(1, canvas.winfo_width())
        bottom = top + max(1, canvas.winfo_height())
        first_module = max(0, int((left - 280) // 360))
        last_module = min(len(calculation.modules), int((right - 280) // 360) + 1)
        first_row = max(0, int((top - 84) // 32))
        last_row = min(len(calculation.inverters), int((bottom - 84) // 32) + 1)
        canvas.delete("matrix")
        if left < 280 and top < 84:
            self._draw_cell(0, 0, 280, 84, "Modelo", header=True)
        if top < 84:
            for module_position in range(first_module, last_module):
                module = calculation.modules[module_position]
                x = 280 + module_position * 360
                equipment = module.equipment
                power = f"{module.nominal_power_w:.0f} W" if module.nominal_power_w is not None else "N/D"
                self._draw_cell(x, 0, 360, 28, module.display_model, header=True)
                self._draw_cell(x, 28, 360, 28, f"{equipment.manufacturer if equipment else 'Não associado'} — potência nominal: {power}", header=True)
                for offset, title in enumerate(("Qtd.", "Potência (kW)", "Sobrecarga")):
                    self._draw_cell(x + offset * 120, 56, 120, 28, title, header=True)
        for row_position in range(first_row, last_row):
            inverter = calculation.inverters[row_position]
            y = 84 + row_position * 32
            if left < 280:
                self._draw_cell(0, y, 280, 32, inverter.display_label, stripe=row_position % 2 == 1, anchor="w")
            for module_position in range(first_module, last_module):
                module = calculation.modules[module_position]
                values = matrix_values(calculation.cell(inverter.key, module.key))
                x = 280 + module_position * 360
                for offset, value in enumerate(values):
                    self._draw_cell(x + offset * 120, y, 120, 32, value, stripe=row_position % 2 == 1)

    def _matrix_click(self, event):
        if self.calculation is None:
            return
        x = self.matrix_canvas.canvasx(event.x)
        y = self.matrix_canvas.canvasy(event.y)
        if x < 280 or y < 84:
            return
        row = int((y - 84) // 32)
        column = int((x - 280) // 360)
        if row >= len(self.calculation.inverters) or column >= len(self.calculation.modules):
            return
        inverter = self.calculation.inverters[row]
        module = self.calculation.modules[column]
        self._show_details(inverter, module, self.calculation.cell(inverter.key, module.key))

    def _show_details(self, inverter, module, cell):
        opener = self.focus_get() or self.matrix_canvas
        window = tk.Toplevel(self)
        window.title(f"Detalhes — {inverter.display_label} × {module.display_model}")
        window.geometry("1000x620")
        window.minsize(760, 480)
        heading = (
            f"Modelo real: {inverter.equipment.model if inverter.equipment else 'Não associado'}\n"
            f"Texto da linha: {inverter.display_label}\n"
            f"Sobrecarga da linha: {overload_label(inverter)}\n"
            f"Módulo: {module.display_model}"
        )
        ttk.Label(window, text=heading, font=("Segoe UI", 11, "bold")).pack(
            fill="x", padx=12, pady=12
        )
        content = ttk.Frame(window)
        content.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        content.columnconfigure(0, weight=1, uniform="details")
        content.columnconfigure(1, weight=1, uniform="details")
        content.rowconfigure(0, weight=1)
        first_text = None
        if isinstance(cell, ImportedCellResult):
            frame = ttk.LabelFrame(content, text="Valor importado", padding=8)
            frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
            text = tk.Text(frame, wrap="word", padx=8, pady=8)
            text.insert("1.0", imported_details(cell))
            text.configure(state="disabled")
            text.configure(takefocus=True)
            text.pack(fill="both", expand=True)
            first_text = text
            difference_text = "Diferença de quantidade: disponível após recalcular"
        else:
            for column, title, result in (
                (0, "Modo normal", cell.normal),
                (1, "Ignorando corrente de operação", cell.ignored),
            ):
                frame = ttk.LabelFrame(content, text=title, padding=8)
                frame.grid(
                    row=0,
                    column=column,
                    sticky="nsew",
                    padx=(0, 6) if column == 0 else (6, 0),
                )
                text = tk.Text(frame, wrap="word", padx=8, pady=8)
                text.insert("1.0", result_details(result))
                text.configure(state="disabled")
                text.configure(takefocus=True)
                text.pack(fill="both", expand=True)
                if first_text is None:
                    first_text = text
            difference = cell.ignored.quantity - cell.normal.quantity
            difference_text = f"Diferença de quantidade: {difference:+d} módulo(s)"
        ttk.Label(
            window,
            text=difference_text,
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(0, 12))
        prepare_toplevel(window, opener=opener, initial=first_text)


if __name__ == "__main__":
    CompatibilityMatrixGUI().mainloop()
