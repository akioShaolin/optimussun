"""Interface provisória da matriz de compatibilidade do Optimus Sun."""

import queue
import math
import sqlite3
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
DB_PATH = SRC_DIR / "optimus_sun.db"
sys.path.insert(0, str(SRC_DIR))

from compatibility import (  # noqa: E402
    CompatibilityMatrix,
    CompatibilityOptions,
    LimitingFactor,
    list_active_inverters,
    list_active_modules,
)


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
    return sqlite3.connect(f"file:{DB_PATH.resolve()}?mode=ro", uri=True)


def equipment_label(equipment):
    return f"{equipment.manufacturer} — {equipment.model} [ID {equipment.database_id}]"


def decimal_pt(value, places=2):
    return f"{value:.{places}f}".replace(".", ",")


def matrix_values(cell):
    result = cell.display_result
    if result.limiting_factor == LimitingFactor.MISSING_DATA:
        return "N/D", "N/D", "N/D"
    if cell.uses_ignored_result:
        quantity = f"{cell.normal.quantity} → {cell.ignored.quantity} ↗"
    else:
        quantity = str(result.quantity)
    return (
        quantity,
        decimal_pt(result.dc_power_kw),
        f"{decimal_pt(result.overload_percent)}%",
    )


def result_details(result):
    if result.limiting_factor == LimitingFactor.MISSING_DATA:
        quantity = power = overload = "N/D"
    else:
        quantity = str(result.quantity)
        power = f"{decimal_pt(result.dc_power_kw)} kW"
        overload = f"{decimal_pt(result.overload_percent)}%"
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
        return f"Personalizada ({decimal_pt(selection.custom_overload_percent)}%)"
    registered = selection.equipment.overload_percent
    return f"Cadastrada ({decimal_pt(registered)}%)"


class OverloadDialog(tk.Toplevel):
    def __init__(self, parent, selection):
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
        self.percent = tk.StringVar(value=decimal_pt(initial))

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text=f"Inversor: {selection.equipment.model}").grid(
            row=0, column=0, columnspan=3, sticky="w"
        )
        ttk.Label(body, text=f"Texto: {selection.display_label}").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(2, 12)
        )
        ttk.Radiobutton(
            body,
            text=f"Usar cadastrada: {decimal_pt(selection.equipment.overload_percent)}%",
            variable=self.mode,
            value="registered",
            command=self._update_state,
        ).grid(row=2, column=0, columnspan=3, sticky="w")
        ttk.Radiobutton(
            body,
            text="Personalizada:",
            variable=self.mode,
            value="custom",
            command=self._update_state,
        ).grid(row=3, column=0, sticky="w", pady=(8, 0))
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
        self.title("Optimus Sun — matriz de compatibilidade (provisória)")
        self.geometry("1380x820")
        self.minsize(960, 640)
        self.state_model = CompatibilityMatrix()
        self.calculation = None
        self.calculating = False
        self.worker_queue = queue.Queue()

        with open_database() as connection:
            self.available_inverters = list_active_inverters(connection)
            self.available_modules = list_active_modules(connection)
        self.inverter_lookup = {
            equipment_label(item): item for item in self.available_inverters
        }
        self.module_lookup = {
            equipment_label(item): item for item in self.available_modules
        }

        self.status_text = tk.StringVar(value="Monte a seleção e clique em Calcular matriz.")
        self._build_interface()

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
            frame, state="readonly", values=tuple(self.inverter_lookup)
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
        ttk.Button(buttons, text="Remover", command=self.remove_inverter).pack(
            side="left", padx=6
        )

    def _build_module_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Módulos da matriz", padding=8)
        frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        frame.columnconfigure(0, weight=1)
        self.module_combo = ttk.Combobox(
            frame, state="readonly", values=tuple(self.module_lookup)
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

    def _build_calculation_controls(self, parent):
        frame = ttk.Frame(parent)
        frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.calculate_button = ttk.Button(
            frame, text="Calcular matriz", command=self.start_calculation
        )
        self.calculate_button.pack(side="left")
        self.progress = ttk.Progressbar(frame, mode="indeterminate", length=150)
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
        self.matrix_canvas = tk.Canvas(outer, highlightthickness=0, background="#f5f7fa")
        x_scroll = ttk.Scrollbar(outer, orient="horizontal", command=self.matrix_canvas.xview)
        y_scroll = ttk.Scrollbar(outer, orient="vertical", command=self.matrix_canvas.yview)
        self.matrix_canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        self.matrix_canvas.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.matrix_frame = tk.Frame(self.matrix_canvas, background="#f5f7fa")
        self.matrix_window = self.matrix_canvas.create_window(
            (0, 0), window=self.matrix_frame, anchor="nw"
        )
        self.matrix_frame.bind("<Configure>", self._update_scroll_region)
        self.matrix_canvas.bind("<Configure>", self._expand_matrix_view)
        ttk.Label(
            self.matrix_frame,
            text="Adicione inversores e módulos para gerar a matriz.",
        ).grid(padx=20, pady=20)

    def _update_scroll_region(self, _event=None):
        self.matrix_canvas.configure(scrollregion=self.matrix_canvas.bbox("all"))

    def _expand_matrix_view(self, event):
        requested = self.matrix_frame.winfo_reqwidth()
        self.matrix_canvas.itemconfigure(self.matrix_window, width=max(event.width, requested))

    def _guard_busy(self):
        if self.calculating:
            messagebox.showinfo("Cálculo em andamento", "Aguarde o cálculo da matriz.")
            return False
        return True

    def add_inverter(self):
        if not self._guard_busy():
            return
        equipment = self.inverter_lookup.get(self.inverter_combo.get())
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

    def configure_overload(self):
        if not self._guard_busy():
            return
        key = self._selected_key(self.inverter_tree)
        if key is None:
            return
        selection = next(item for item in self.state_model.inverters if item.key == key)
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

    def remove_inverter(self):
        if not self._guard_busy():
            return
        key = self._selected_key(self.inverter_tree)
        if key is not None:
            self.state_model.remove_inverter(key)
            self.inverter_tree.delete(str(key))

    def add_module(self):
        if not self._guard_busy():
            return
        equipment = self.module_lookup.get(self.module_combo.get())
        if equipment is None:
            return
        item = self.state_model.add_module(equipment)
        self.module_tree.insert(
            "",
            "end",
            iid=str(item.key),
            values=(equipment.manufacturer, equipment.model),
        )

    def remove_module(self):
        if not self._guard_busy():
            return
        key = self._selected_key(self.module_tree)
        if key is not None:
            self.state_model.remove_module(key)
            self.module_tree.delete(str(key))

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

    def start_calculation(self):
        if self.calculating:
            return
        try:
            if not self.state_model.inverters or not self.state_model.modules:
                raise ValueError("Adicione ao menos um inversor e um módulo.")
        except ValueError as error:
            messagebox.showerror("Não foi possível calcular", str(error))
            return
        self.calculating = True
        self.calculate_button.configure(state="disabled")
        self.progress.start(12)
        total = len(self.state_model.inverters) * len(self.state_model.modules)
        self.status_text.set(f"Calculando {total} combinação(ões)…")
        threading.Thread(
            target=self._calculate_worker, daemon=True
        ).start()
        self.after(100, self._poll_worker)

    def _calculate_worker(self):
        try:
            with open_database() as connection:
                calculation = self.state_model.calculate(
                    connection, CompatibilityOptions()
                )
            self.worker_queue.put(("ok", calculation))
        except Exception as error:
            self.worker_queue.put(("error", error))

    def _poll_worker(self):
        try:
            status, payload = self.worker_queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_worker)
            return
        self.calculating = False
        self.calculate_button.configure(state="normal")
        self.progress.stop()
        if status == "error":
            self.status_text.set("Falha no cálculo.")
            messagebox.showerror("Não foi possível calcular", str(payload))
            return
        self.calculation = payload
        self._render_matrix()
        self.status_text.set(
            f"Matriz pronta: {len(payload.inverters)} × {len(payload.modules)}."
        )

    def _clear_matrix(self):
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

    def _header_label(self, text, row, column, columnspan=1, **options):
        label = tk.Label(
            self.matrix_frame,
            text=text,
            background=options.pop("background", "#dce6f1"),
            foreground="#163a5f",
            font=options.pop("font", ("Segoe UI", 9, "bold")),
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=4,
            **options,
        )
        label.grid(row=row, column=column, columnspan=columnspan, sticky="nsew")
        return label

    def _render_matrix(self):
        self._clear_matrix()
        calculation = self.calculation
        self._header_label("Inversor", 0, 0, 1, font=("Segoe UI", 10, "bold"))
        self._header_label("Texto exibido", 1, 0)
        self._header_label("Fabricante / modelo real", 2, 0)
        for module_position, module in enumerate(calculation.modules):
            column = 1 + module_position * 3
            equipment = module.equipment
            self._header_label(equipment.model, 0, column, 3)
            self._header_label(
                f"{equipment.manufacturer} — potência nominal: "
                f"{equipment.nominal_power_w:.0f} W",
                1,
                column,
                3,
                font=("Segoe UI", 8),
            )
            for offset, title in enumerate(("Qtd.", "Potência (kW)", "Sobrecarga")):
                self._header_label(title, 2, column + offset)

        for row_position, inverter in enumerate(calculation.inverters, start=3):
            equipment = inverter.equipment
            self._body_label(
                f"{inverter.display_label}\n{equipment.manufacturer} — {equipment.model}",
                row_position,
                0,
                width=34,
                anchor="w",
            )
            for module_position, module in enumerate(calculation.modules):
                cell = calculation.cell(inverter.key, module.key)
                values = matrix_values(cell)
                for offset, value in enumerate(values):
                    label = self._body_label(
                        value,
                        row_position,
                        1 + module_position * 3 + offset,
                        width=13,
                        cursor="hand2",
                    )
                    label.bind(
                        "<Button-1>",
                        lambda _event, inv=inverter, mod=module, result=cell: (
                            self._show_details(inv, mod, result)
                        ),
                    )
        self._update_scroll_region()

    def _body_label(self, text, row, column, **options):
        label = tk.Label(
            self.matrix_frame,
            text=text,
            background="#ffffff" if row % 2 else "#f2f6fa",
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=6,
            **options,
        )
        label.grid(row=row, column=column, sticky="nsew")
        return label

    def _show_details(self, inverter, module, cell):
        window = tk.Toplevel(self)
        window.title(f"Detalhes — {inverter.display_label} × {module.equipment.model}")
        window.geometry("1000x620")
        window.minsize(760, 480)
        heading = (
            f"Modelo real: {inverter.equipment.model}\n"
            f"Texto da linha: {inverter.display_label}\n"
            f"Sobrecarga da linha: {overload_label(inverter)}\n"
            f"Módulo: {module.equipment.manufacturer} — {module.equipment.model}"
        )
        ttk.Label(window, text=heading, font=("Segoe UI", 11, "bold")).pack(
            fill="x", padx=12, pady=12
        )
        content = ttk.Frame(window)
        content.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        content.columnconfigure(0, weight=1, uniform="details")
        content.columnconfigure(1, weight=1, uniform="details")
        content.rowconfigure(0, weight=1)
        for column, title, result in (
            (0, "Modo normal", cell.normal),
            (1, "Ignorando corrente de operação", cell.ignored),
        ):
            frame = ttk.LabelFrame(content, text=title, padding=8)
            frame.grid(row=0, column=column, sticky="nsew", padx=(0, 6) if column == 0 else (6, 0))
            text = tk.Text(frame, wrap="word", padx=8, pady=8)
            text.insert("1.0", result_details(result))
            text.configure(state="disabled")
            text.pack(fill="both", expand=True)
        difference = cell.ignored.quantity - cell.normal.quantity
        ttk.Label(
            window,
            text=f"Diferença de quantidade: {difference:+d} módulo(s)",
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(0, 12))


if __name__ == "__main__":
    CompatibilityMatrixGUI().mainloop()
