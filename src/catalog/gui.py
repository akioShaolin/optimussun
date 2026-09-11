"""Interface de cadastros v2.6: listas filtráveis e editor unificado."""

from __future__ import annotations

import copy
import itertools
import tkinter as tk
from tkinter import messagebox, ttk

from focus_navigation import prepare_toplevel
from version import APP_VERSION

from .domain import (
    COMMUNICATION_OPTIONS, FUTURE_COMMUNICATION_OPTIONS, FUTURE_OUTPUT_OPTIONS,
    OUTPUT_OPTIONS, SYSTEM_OPTIONS, CatalogValidationError, decode_mppt_index,
    encode_mppt_index, parse_number, validate_inverter_draft,
)

CATEGORY_LABELS = {0: "Inversores", 1: "Módulos", 2: "Módulos e inversores"}
STATUS_LABELS = {0: "Inativo", 1: "Ativo"}
ENTITY_LABELS = {"manufacturer": "Fabricante", "inverter": "Inversor", "module": "Módulo"}
FIELD_LABELS = {
    "ID": "Id", "NAME": "Nome", "CATEGORY": "Categoria", "MODEL": "Modelo",
    "MANUFACTURER_NAME": "Fabricante", "MANUFACTURER_ID": "Fabricante", "ACTIVE": "Situação",
    "DIM_WIDTH": "Largura", "DIM_HEIGHT": "Altura", "DIM_DEPTH": "Profundidade", "DIM_WEIGHT": "Peso",
    "MAX_OPERATING_TEMPERATURE": "Temperatura máxima de operação",
    "MIN_OPERATING_TEMPERATURE": "Temperatura mínima de operação", "COOLING_MODE": "Refrigeração",
    "PROTECTION_DEGREE": "Grau de proteção", "TOPOLOGY": "Topologia",
    "RATED_ACTIVE_POWER": "Potência ativa nominal", "MAX_ACTIVE_POWER": "Potência ativa máxima",
    "RATED_OUTPUT_VOLTAGE": "Tensão nominal de saída", "RATED_OUTPUT_CURRENT": "Corrente nominal de saída",
    "MAX_OUTPUT_CURRENT": "Corrente máxima de saída", "OVERLOAD": "Sobrecarga cadastrada",
    "NUMBER_OF_TRACKERS": "Quantidade de MPPTs", "NUMBER_OF_INPUTS": "Quantidade de entradas",
    "MPPT_INDEX": "Índice de MPPTs", "MAX_INPUT_VOLTAGE": "Tensão máxima de entrada",
    "MIN_STARTUP_VOLTAGE": "Tensão mínima de partida", "MAX_OPERATING_VOLTAGE": "Tensão máxima de operação",
    "MIN_OPERATING_VOLTAGE": "Tensão mínima de operação", "MAX_FULL_LOAD_VOLTAGE": "Tensão máxima em plena carga",
    "MIN_FULL_LOAD_VOLTAGE": "Tensão mínima em plena carga", "RATED_INPUT_VOLTAGE": "Tensão nominal de entrada",
    "MAX_SHORT_CIRCUIT_CURRENT": "Corrente máxima de curto-circuito",
    "MAX_OPERATING_CURRENT": "Corrente máxima de operação", "WP": "Potência do módulo",
    "VMPP": "Vmpp", "IMPP": "Impp", "VOC": "Voc", "ISC": "Isc",
    "SOLAR_CELLS": "Tecnologia das células", "CELL_TYPE": "Tipo de célula",
    "SURFACE_TYPE": "Tipo de superfície", "COEF_PMAX": "Coeficiente térmico Pmax",
    "COEF_VOC": "Coeficiente térmico Voc", "COEF_ISC": "Coeficiente térmico Isc",
    "SYSTEM_TYPE": "Sistema", "COMMUNICATION_TYPE": "Comunicação", "OUTPUT_MODE": "Modo de saída",
}
ENUM_LABELS = {
    "MONOCRISTALINO": "Monocristalino", "POLICRISTALINO": "Policristalino",
    "FULL CELL": "Célula inteira", "HALF CELL": "Meia célula", "MONOFACIAL": "Monofacial",
    "BIFACIAL": "Bifacial", "ON-GRID": "Conectado à rede", "OFF-GRID": "Isolado",
    "GRIDZERO": "Injeção zero", "HYBRID": "Híbrido", "THREE_PHASE_FOUR_WIRE": "Trifásico a quatro fios",
    "THREE_PHASE_THREE_WIRE": "Trifásico a três fios", "SINGLE_PHASE": "Monofásico",
    "SPLIT PHASE": "Fase dividida",
}
UNITS = {
    "DIM_WIDTH": "mm", "DIM_HEIGHT": "mm", "DIM_DEPTH": "mm", "DIM_WEIGHT": "kg",
    "MAX_OPERATING_TEMPERATURE": "°C", "MIN_OPERATING_TEMPERATURE": "°C",
    "RATED_ACTIVE_POWER": "W", "MAX_ACTIVE_POWER": "W", "WP": "W",
    "RATED_OUTPUT_VOLTAGE": "V", "MAX_INPUT_VOLTAGE": "V", "MIN_STARTUP_VOLTAGE": "V",
    "MAX_OPERATING_VOLTAGE": "V", "MIN_OPERATING_VOLTAGE": "V",
    "MAX_FULL_LOAD_VOLTAGE": "V", "MIN_FULL_LOAD_VOLTAGE": "V", "RATED_INPUT_VOLTAGE": "V",
    "VMPP": "V", "VOC": "V", "RATED_OUTPUT_CURRENT": "A", "MAX_OUTPUT_CURRENT": "A",
    "MAX_SHORT_CIRCUIT_CURRENT": "A", "MAX_OPERATING_CURRENT": "A", "IMPP": "A", "ISC": "A",
    "OVERLOAD": "%", "COEF_PMAX": "%/°C", "COEF_VOC": "%/°C", "COEF_ISC": "%/°C",
}
INTEGER_FIELDS = {"WP", "RATED_ACTIVE_POWER", "MAX_ACTIVE_POWER", "MAX_OPERATING_TEMPERATURE",
                  "MIN_OPERATING_TEMPERATURE", "OVERLOAD", "NUMBER_OF_TRACKERS", "NUMBER_OF_INPUTS",
                  "MAX_INPUT_VOLTAGE", "MIN_STARTUP_VOLTAGE", "MAX_OPERATING_VOLTAGE",
                  "MIN_OPERATING_VOLTAGE", "MAX_FULL_LOAD_VOLTAGE", "MIN_FULL_LOAD_VOLTAGE",
                  "RATED_INPUT_VOLTAGE"}
POSITIVE_FIELDS = set(UNITS) - {"MAX_OPERATING_TEMPERATURE", "MIN_OPERATING_TEMPERATURE",
                                "COEF_PMAX", "COEF_VOC", "COEF_ISC"}


def _label(field):
    return FIELD_LABELS.get(field, field.replace("_", " ").title()) + (f" ({UNITS[field]})" if field in UNITS else "")


def _display(value):
    return "Não informado" if value in (-1, None, "") else str(value)


class CatalogApp(tk.Tk):
    def __init__(self, repository):
        super().__init__()
        self.repository = repository
        self.title(f"Optimus Sun {APP_VERSION} — Cadastros")
        self.geometry("1240x700")
        self.minsize(960, 620)
        style = ttk.Style(self); style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 11))
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        style.configure("TButton", padding=(10, 6), font=("Segoe UI", 10))
        style.configure("TEntry", padding=(5, 4)); style.configure("TCombobox", padding=(5, 4))
        notebook = ttk.Notebook(self); notebook.pack(fill="both", expand=True, padx=12, pady=12)
        self.manufacturers = ListingFrame(notebook, repository, "manufacturer")
        self.inverters = ListingFrame(notebook, repository, "inverter")
        self.modules = ListingFrame(notebook, repository, "module")
        notebook.add(self.manufacturers, text="Fabricantes")
        notebook.add(self.inverters, text="Inversores")
        notebook.add(self.modules, text="Módulos")

    def refresh_all(self):
        """Atualiza fontes dependentes, preservando os filtros de cada aba."""
        for frame in (self.manufacturers, self.inverters, self.modules):
            frame.load()


class ListingFrame(ttk.Frame):
    def __init__(self, parent, repository, entity):
        super().__init__(parent, padding=10)
        self.repository, self.entity = repository, entity
        self.rows, self.sort_column, self.descending = {}, "MODEL", False
        filters = ttk.LabelFrame(self, text="Busca e filtros", padding=10)
        filters.pack(fill="x", pady=(0, 8))
        self.search = tk.StringVar(); self.status = tk.StringVar(value="Todos")
        self.manufacturer = tk.StringVar(value="Todos"); self.category = tk.StringVar(value="Todas")
        ttk.Label(filters, text="Busca:").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(filters, textvariable=self.search, width=32); entry.grid(row=1, column=0, padx=(0, 8))
        entry.bind("<Return>", lambda _event: self.load())
        if entity == "manufacturer":
            ttk.Label(filters, text="Categoria:").grid(row=0, column=1, sticky="w")
            ttk.Combobox(filters, textvariable=self.category, state="readonly",
                         values=("Todas", *CATEGORY_LABELS.values()), width=24).grid(row=1, column=1, padx=(0, 8))
        else:
            ttk.Label(filters, text="Fabricante:").grid(row=0, column=1, sticky="w")
            self.manufacturer_combo = ttk.Combobox(filters, textvariable=self.manufacturer,
                                                   state="readonly", width=28)
            self.manufacturer_combo.grid(row=1, column=1, padx=(0, 8))
            ttk.Label(filters, text="Status:").grid(row=0, column=2, sticky="w")
            ttk.Combobox(filters, textvariable=self.status, state="readonly",
                         values=("Todos", "Ativo", "Inativo"), width=14).grid(row=1, column=2, padx=(0, 8))
        ttk.Button(filters, text="Aplicar", command=self.load).grid(row=1, column=3, padx=4)
        ttk.Button(filters, text="Limpar filtros", command=self.clear_filters).grid(row=1, column=4, padx=4)
        columns = ("ID", "NAME", "CATEGORY") if entity == "manufacturer" else (
            "ID", "MODEL", "MANUFACTURER_NAME", "ACTIVE")
        table = ttk.Frame(self); table.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table, columns=columns, show="headings", selectmode="browse")
        for column in columns:
            self.tree.heading(column, text=_label(column), command=lambda value=column: self.sort(value))
            self.tree.column(column, width=90 if column in ("ID", "ACTIVE") else 260, anchor="center" if column in ("ID", "ACTIVE") else "w")
        vs = ttk.Scrollbar(table, command=self.tree.yview); hs = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.tree.grid(row=0, column=0, sticky="nsew"); vs.grid(row=0, column=1, sticky="ns"); hs.grid(row=1, column=0, sticky="ew")
        table.rowconfigure(0, weight=1); table.columnconfigure(0, weight=1)
        actions = ttk.Frame(self); actions.pack(fill="x", pady=(8, 0))
        for text, command in (("Novo", self.new), ("Visualizar", self.view), ("Editar", self.edit), ("Duplicar como rascunho", self.duplicate),
                              ("Excluir", self.delete), ("Copiar dados", self.copy_data)):
            ttk.Button(actions, text=text, command=command).pack(side="left", padx=(0, 6))
        self.load()

    def clear_filters(self):
        self.search.set(""); self.status.set("Todos"); self.manufacturer.set("Todos"); self.category.set("Todas"); self.load()

    def _manufacturer_map(self):
        records = self.repository.list_manufacturers()
        return {f"{row['NAME']} (ID {row['ID']})": row["ID"] for row in records}

    def load(self):
        if self.entity == "manufacturer":
            category = next((key for key, label in CATEGORY_LABELS.items() if label == self.category.get()), None)
            records = self.repository.list_manufacturers(self.search.get(), category)
        else:
            mapping = self._manufacturer_map(); self.manufacturer_combo["values"] = ("Todos", *mapping)
            active = {"Ativo": 1, "Inativo": 0}.get(self.status.get())
            records = self.repository.list_equipment(self.entity, self.search.get(), mapping.get(self.manufacturer.get()), active,
                                                     self.sort_column, self.descending)
        self.rows = {row["ID"]: row for row in records}
        self.tree.delete(*self.tree.get_children())
        for row in records:
            if self.entity == "manufacturer":
                values = (row["ID"], row["NAME"], CATEGORY_LABELS.get(row["CATEGORY"], row["CATEGORY"]))
            else:
                values = (row["ID"], row["MODEL"], row["MANUFACTURER_NAME"], STATUS_LABELS.get(row["ACTIVE"]))
            self.tree.insert("", "end", iid=str(row["ID"]), values=values)

    def sort(self, column):
        if self.entity == "manufacturer":
            items = [(self.tree.set(item, column).casefold(), item) for item in self.tree.get_children()]
            self.descending = self.sort_column == column and not self.descending; self.sort_column = column
            for position, (_value, item) in enumerate(sorted(items, reverse=self.descending)):
                self.tree.move(item, "", position)
        else:
            self.descending = self.sort_column == column and not self.descending; self.sort_column = column; self.load()

    def selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Selecione um cadastro.", parent=self); return None
        return self.rows[int(selection[0])]

    def new(self): self._open(None, False)
    def view(self):
        row = self.selected()
        if row:
            if self.entity == "inverter": InverterEditor(self, self.repository, row, False, lambda: None, readonly=True)
            else: SimpleEditor(self, self.repository, self.entity, row, False, lambda: None, readonly=True)
    def edit(self):
        row = self.selected()
        if row: self._open(row, False)
    def duplicate(self):
        row = self.selected()
        if row: self._open(row, True)

    def _open(self, row, duplicate):
        callback = self.winfo_toplevel().refresh_all
        if self.entity == "inverter": InverterEditor(self, self.repository, row, duplicate, callback)
        else: SimpleEditor(self, self.repository, self.entity, row, duplicate, callback)

    def delete(self):
        row = self.selected()
        if not row: return
        identity = row.get("MODEL", row.get("NAME"))
        if not messagebox.askyesno("Confirmar exclusão", f"Excluir definitivamente {identity}?\nRelacionamentos afetados serão removidos de modo atômico.", parent=self): return
        try: self.repository.delete(self.entity, row["ID"]); self.winfo_toplevel().refresh_all()
        except Exception as exc: messagebox.showerror("Exclusão bloqueada", str(exc), parent=self)

    def copy_data(self):
        row = self.selected()
        if not row: return
        text = "\n".join(f"{_label(key)}: {_display(value)}" for key, value in row.items())
        self.clipboard_clear(); self.clipboard_append(text)


class DraftWindow(tk.Toplevel):
    def __init__(self, parent, title, callback):
        opener = parent.focus_get() or parent
        super().__init__(parent); self.title(title); self.callback = callback; self.dirty = False
        self.geometry("920x660"); self.minsize(760, 560); self.protocol("WM_DELETE_WINDOW", self.cancel)
        prepare_toplevel(self, opener=opener)

    def cancel(self):
        if self.dirty and not messagebox.askyesno("Descartar alterações", "Descartar o rascunho sem salvar?", parent=self): return
        self.destroy()


class SimpleEditor(DraftWindow):
    MODULE_FIELDS = ("MODEL", "MANUFACTURER_ID", "DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT",
                     "WP", "VMPP", "IMPP", "VOC", "ISC", "SOLAR_CELLS", "CELL_TYPE", "SURFACE_TYPE",
                     "COEF_PMAX", "COEF_VOC", "COEF_ISC", "ACTIVE")
    def __init__(self, parent, repository, entity, row, duplicate, callback, readonly=False):
        super().__init__(parent, f"{'Visualizar' if readonly else 'Duplicar' if duplicate else 'Editar' if row else 'Novo'} {ENTITY_LABELS[entity]}", callback)
        self.readonly = readonly
        self.repository, self.entity = repository, entity; self.record_id = None if duplicate or not row else row["ID"]
        self.vars = {}; body = ttk.Frame(self, padding=14); body.pack(fill="both", expand=True)
        data = dict(row or {})
        fields = ("NAME", "CATEGORY") if entity == "manufacturer" else self.MODULE_FIELDS
        manufacturers = repository.manufacturer_choices("module") if entity == "module" else []
        self.manufacturer_map = {f"{item['NAME']} (ID {item['ID']})": item["ID"] for item in manufacturers}
        for index, field in enumerate(fields):
            row = index if entity == "manufacturer" else index // 2
            column = 0 if entity == "manufacturer" else (index % 2) * 2
            ttk.Label(body, text=_label(field), wraplength=260).grid(row=row, column=column, sticky="w", padx=5, pady=5)
            var = tk.StringVar(); self.vars[field] = var
            if field == "CATEGORY": widget = ttk.Combobox(body, textvariable=var, state="readonly", values=tuple(CATEGORY_LABELS.values()))
            elif field == "MANUFACTURER_ID": widget = ttk.Combobox(body, textvariable=var, state="readonly", values=tuple(self.manufacturer_map))
            elif field == "ACTIVE": widget = ttk.Combobox(body, textvariable=var, state="readonly", values=("Ativo", "Inativo"))
            elif field == "SOLAR_CELLS": widget = ttk.Combobox(body, textvariable=var, state="readonly", values=tuple(ENUM_LABELS[x] for x in ("MONOCRISTALINO", "POLICRISTALINO")))
            elif field == "CELL_TYPE": widget = ttk.Combobox(body, textvariable=var, state="readonly", values=tuple(ENUM_LABELS[x] for x in ("FULL CELL", "HALF CELL")))
            elif field == "SURFACE_TYPE": widget = ttk.Combobox(body, textvariable=var, state="readonly", values=tuple(ENUM_LABELS[x] for x in ("MONOFACIAL", "BIFACIAL")))
            else: widget = ttk.Entry(body, textvariable=var, width=42 if field == "MODEL" else 22)
            widget.grid(row=row, column=column + 1, sticky="w", padx=5, pady=5); var.trace_add("write", lambda *_: setattr(self, "dirty", True))
            value = data.get(field, "")
            if field == "CATEGORY": value = CATEGORY_LABELS.get(value, "")
            elif field == "ACTIVE": value = STATUS_LABELS.get(value, "Ativo")
            elif field == "MANUFACTURER_ID": value = next((label for label, key in self.manufacturer_map.items() if key == value), "")
            elif field in ("SOLAR_CELLS", "CELL_TYPE", "SURFACE_TYPE"): value = ENUM_LABELS.get(value, value)
            elif value == -1: value = ""
            var.set(value)
            if readonly:
                widget.configure(state="readonly")
        body.columnconfigure(1, weight=1); body.columnconfigure(3, weight=1)
        button_row = len(fields) if entity == "manufacturer" else (len(fields) + 1) // 2
        ttk.Button(body, text="Fechar" if readonly else "Salvar", command=self.cancel if readonly else self.save).grid(row=button_row, column=0, columnspan=4, sticky="e", pady=12)
        self.dirty = False

    def save(self):
        try:
            if self.entity == "manufacturer":
                if not self.vars["NAME"].get().strip(): raise ValueError("Nome é obrigatório.")
                data = {"NAME": self.vars["NAME"].get().strip(),
                        "CATEGORY": next(key for key, label in CATEGORY_LABELS.items() if label == self.vars["CATEGORY"].get())}
            else:
                data = {}
                for field, var in self.vars.items():
                    value = var.get()
                    if field == "MODEL":
                        if not value.strip(): raise ValueError("Modelo é obrigatório.")
                        data[field] = value.strip()
                    elif field == "MANUFACTURER_ID": data[field] = self.manufacturer_map.get(value) or (_ for _ in ()).throw(ValueError("Fabricante é obrigatório."))
                    elif field == "ACTIVE": data[field] = {"Ativo": 1, "Inativo": 0}[value]
                    elif field in ("SOLAR_CELLS", "CELL_TYPE", "SURFACE_TYPE"):
                        data[field] = next((key for key, label in ENUM_LABELS.items() if label == value), None)
                    else: data[field] = parse_number(value, integer=field in INTEGER_FIELDS, positive=field in POSITIVE_FIELDS, field=_label(field))
            action = "alterar" if self.record_id else "criar"
            if not messagebox.askyesno("Confirmar", f"Confirma {action} este cadastro?", parent=self): return
            self.repository.save_equipment(self.entity, data, self.record_id); self.dirty = False; self.destroy(); self.callback()
        except Exception as exc: messagebox.showerror("Dados inválidos", str(exc), parent=self)


class InverterEditor(DraftWindow):
    PARENT_FIELDS = ("MODEL", "MANUFACTURER_ID", "ACTIVE", "DIM_WIDTH", "DIM_HEIGHT", "DIM_DEPTH", "DIM_WEIGHT",
                     "MAX_OPERATING_TEMPERATURE", "MIN_OPERATING_TEMPERATURE", "COOLING_MODE", "PROTECTION_DEGREE",
                     "TOPOLOGY", "RATED_ACTIVE_POWER", "MAX_ACTIVE_POWER", "RATED_OUTPUT_VOLTAGE",
                     "RATED_OUTPUT_CURRENT", "MAX_OUTPUT_CURRENT", "OVERLOAD", "NUMBER_OF_TRACKERS", "NUMBER_OF_INPUTS")
    MPPT_FIELDS = ("NUMBER_OF_INPUTS", "MAX_INPUT_VOLTAGE", "MIN_STARTUP_VOLTAGE", "MAX_OPERATING_VOLTAGE",
                   "MIN_OPERATING_VOLTAGE", "MAX_FULL_LOAD_VOLTAGE", "MIN_FULL_LOAD_VOLTAGE", "RATED_INPUT_VOLTAGE",
                   "MAX_SHORT_CIRCUIT_CURRENT", "MAX_OPERATING_CURRENT")
    _draft_keys = itertools.count(1)
    def __init__(self, parent, repository, row, duplicate, callback, readonly=False):
        super().__init__(parent, "Cadastro unificado de inversor", callback)
        self.readonly = readonly
        self.repository = repository; self.record_id = None if duplicate or not row else row["ID"]
        loaded = repository.load_inverter_draft(row["ID"]) if row else {"inverter": {}, "mppts": [], "systems": [], "communications": [], "output_modes": []}
        self.draft = copy.deepcopy(loaded); self.draft["inverter"].pop("ID", None)
        for group in self.draft["mppts"]:
            if duplicate:
                group.pop("ID", None)
            try:
                group["positions"] = decode_mppt_index(group["MPPT_INDEX"], int(loaded["inverter"].get("NUMBER_OF_TRACKERS", -1)))
            except (TypeError, ValueError) as error:
                group["positions"] = ()
                group["_load_error"] = str(error)
            group["_draft_key"] = f"db-{group.get('ID')}" if group.get("ID") is not None else f"draft-{next(self._draft_keys)}"
        self.vars = {}; notebook = ttk.Notebook(self); self.notebook = notebook; notebook.pack(fill="both", expand=True, padx=10, pady=10)
        sections = (("Identificação", self.PARENT_FIELDS[:3]), ("Características", self.PARENT_FIELDS[3:12]),
                    ("Saída e entrada", self.PARENT_FIELDS[12:]))
        choices = repository.manufacturer_choices("inverter"); self.manufacturer_map = {f"{x['NAME']} (ID {x['ID']})": x["ID"] for x in choices}
        for title, fields in sections:
            tab = ttk.Frame(notebook, padding=12); notebook.add(tab, text=title); self._parent_fields(tab, fields)
        self.mppt_tab = ttk.Frame(notebook, padding=10); notebook.add(self.mppt_tab, text="Grupos de MPPTs"); self._mppt_ui()
        relations = ttk.Frame(notebook, padding=12); notebook.add(relations, text="Sistemas, comunicação e saída"); self._relations_ui(relations)
        footer = ttk.Frame(self, padding=(10, 0, 10, 10)); footer.pack(fill="x")
        ttk.Button(footer, text="Fechar" if readonly else "Cancelar", command=self.cancel).pack(side="right")
        if not readonly:
            ttk.Button(footer, text="Salvar conjunto", command=self.save).pack(side="right", padx=8)
        else:
            self._set_readonly()
        self.dirty = False; self.refresh_groups()

    def _set_readonly(self):
        self._disable_editing(self.notebook)
        self.view_group_button.configure(state="normal")

    def _disable_editing(self, widget):
        for child in widget.winfo_children():
            self._disable_editing(child)
        if isinstance(widget, (ttk.Entry, ttk.Combobox)):
            widget.configure(state="readonly")
        elif isinstance(widget, (ttk.Checkbutton, ttk.Button)):
            widget.configure(state="disabled")

    def _parent_fields(self, tab, fields):
        parent = self.draft["inverter"]
        for i, field in enumerate(fields):
            ttk.Label(tab, text=_label(field)).grid(row=i, column=0, sticky="w", padx=5, pady=5)
            var = tk.StringVar(); self.vars[field] = var
            if field == "MANUFACTURER_ID": widget = ttk.Combobox(tab, textvariable=var, state="readonly", values=tuple(self.manufacturer_map))
            elif field == "ACTIVE": widget = ttk.Combobox(tab, textvariable=var, state="readonly", values=("Ativo", "Inativo"))
            else: widget = ttk.Entry(tab, textvariable=var, width=46 if field in ("MODEL", "COOLING_MODE", "PROTECTION_DEGREE", "TOPOLOGY") else 22)
            widget.grid(row=i, column=1, sticky="w", padx=5, pady=5); var.trace_add("write", lambda *_: setattr(self, "dirty", True))
            value = parent.get(field, "")
            if field == "MANUFACTURER_ID": value = next((x for x, key in self.manufacturer_map.items() if key == value), "")
            elif field == "ACTIVE": value = STATUS_LABELS.get(value, "Ativo")
            elif value == -1: value = ""
            var.set(value)
        tab.columnconfigure(1, weight=1)

    def _mppt_ui(self):
        self.progress = ttk.Label(self.mppt_tab); self.progress.pack(anchor="w", pady=(0, 6))
        self.group_tree = ttk.Treeview(self.mppt_tab, columns=("mppts", "inputs", "subtotal", "index", "status"), show="headings", height=12)
        for col, title in (("mppts", "MPPTs físicos"), ("inputs", "Entradas por MPPT"), ("subtotal", "Subtotal"), ("index", "Índice técnico"), ("status", "Validação")):
            self.group_tree.heading(col, text=title); self.group_tree.column(col, width=150)
        self.group_tree.pack(fill="both", expand=True)
        bar = ttk.Frame(self.mppt_tab); bar.pack(fill="x", pady=7)
        for text, command in (("Adicionar grupo", lambda: self.edit_group(None)), ("Editar grupo", self.edit_selected_group),
                              ("Visualizar grupo", self.view_selected_group), ("Duplicar características", self.duplicate_group), ("Remover do rascunho", self.remove_group),
                              ("Copiar de outro inversor", self.copy_groups)):
            button = ttk.Button(bar, text=text, command=command)
            button.pack(side="left", padx=(0, 5))
            if text == "Visualizar grupo":
                self.view_group_button = button

    def _relations_ui(self, tab):
        self.relation_vars = {}
        groups = (("systems", "Sistemas", SYSTEM_OPTIONS, ()), ("communications", "Comunicação", COMMUNICATION_OPTIONS, FUTURE_COMMUNICATION_OPTIONS),
                  ("output_modes", "Modos de saída", OUTPUT_OPTIONS, FUTURE_OUTPUT_OPTIONS))
        for col, (key, title, options, future) in enumerate(groups):
            frame = ttk.LabelFrame(tab, text=title, padding=10); frame.grid(row=0, column=col, sticky="nsew", padx=6)
            self.relation_vars[key] = {}
            for row, option in enumerate(options):
                var = tk.BooleanVar(value=option in self.draft[key]); self.relation_vars[key][option] = var
                ttk.Checkbutton(frame, text=ENUM_LABELS.get(option, option), variable=var).grid(row=row, column=0, sticky="w", pady=3)
                var.trace_add("write", lambda *_: setattr(self, "dirty", True))
            for offset, option in enumerate(future, len(options)):
                ttk.Checkbutton(frame, text=f"{ENUM_LABELS.get(option, option)} — indisponível nesta versão", state="disabled").grid(row=offset, column=0, sticky="w", pady=3)
            tab.columnconfigure(col, weight=1)

    def _tracker_count(self):
        return parse_number(self.vars["NUMBER_OF_TRACKERS"].get(), integer=True, required=True, positive=True, field="Total de MPPTs")

    def refresh_groups(self):
        self.group_tree.delete(*self.group_tree.get_children()); covered = inputs = 0
        self.group_rows = {}
        expected_mppts = self.vars["NUMBER_OF_TRACKERS"].get() or "?"
        expected_inputs = self.vars["NUMBER_OF_INPUTS"].get() or "?"
        for index, group in enumerate(self.draft["mppts"]):
            key = group.setdefault("_draft_key", f"draft-{next(self._draft_keys)}")
            self.group_rows[key] = index
            positions = tuple(group.get("positions", ()))
            row_errors = [group["_load_error"]] if group.get("_load_error") else []
            try:
                per_mppt = int(group.get("NUMBER_OF_INPUTS"))
                subtotal = len(positions) * per_mppt
                inputs += subtotal
            except (TypeError, ValueError):
                subtotal = "—"; row_errors.append("quantidade de entradas inválida")
            covered += len(positions)
            homogeneous = len(self.draft["mppts"]) == 1 and positions == tuple(range(1, int(expected_mppts) + 1)) if str(expected_mppts).isdigit() else False
            try:
                technical = group.get("MPPT_INDEX", "inválido") if group.get("_load_error") else 0 if homogeneous else encode_mppt_index(positions)
            except ValueError as error:
                technical = group.get("MPPT_INDEX", "inválido"); row_errors.append(str(error))
            status = "Erro: " + "; ".join(row_errors) if row_errors else "OK"
            self.group_tree.insert("", "end", iid=key, values=(", ".join(map(str, positions)) or "—", group.get("NUMBER_OF_INPUTS"), subtotal, technical, status))
        self.progress.config(text=f"MPPTs: {covered}/{expected_mppts} — Entradas: {inputs}/{expected_inputs}")

    def edit_selected_group(self):
        selection = self.group_tree.selection()
        if selection: self.edit_group(self.group_rows[selection[0]])
    def view_selected_group(self):
        selection = self.group_tree.selection()
        if selection: GroupEditor(self, self.group_rows[selection[0]], readonly=True)
    def edit_group(self, index, characteristics=None, on_applied=None):
        GroupEditor(self, index, characteristics, on_applied=on_applied)
    def duplicate_group(self):
        selection = self.group_tree.selection()
        if selection:
            source = copy.deepcopy(self.draft["mppts"][self.group_rows[selection[0]]]); source["positions"] = (); source.pop("ID", None); source.pop("_draft_key", None); source.pop("_load_error", None); self.edit_group(None, source)
    def remove_group(self):
        selection = self.group_tree.selection()
        if selection: self.draft["mppts"].pop(self.group_rows[selection[0]]); self.dirty = True; self.refresh_groups()

    def copy_groups(self):
        rows = self.repository.list_equipment("inverter")
        labels = {f"{row['MANUFACTURER_NAME']} — {row['MODEL']} (ID {row['ID']})": row["ID"] for row in rows if row["ID"] != self.record_id}
        chooser = ChoiceDialog(self, "Copiar características", labels)
        self.wait_window(chooser)
        if chooser.result:
            source = self.repository.load_inverter_draft(chooser.result)
            selector = SourceGroupsDialog(self, source["mppts"])
            self.wait_window(selector)
            if selector.result:
                self._copy_group_queue(selector.result)

    def _copy_group_queue(self, groups):
        pending = list(groups)
        if not pending:
            return
        group = pending.pop(0)
        item = {key: value for key, value in group.items() if key not in ("ID", "INVERTER_ID", "MPPT_INDEX")}
        item["positions"] = ()
        self.edit_group(None, item, on_applied=lambda: self._copy_group_queue(pending))

    def _collect_parent(self):
        result = {}
        required_text = {"MODEL", "COOLING_MODE", "PROTECTION_DEGREE", "TOPOLOGY"}
        for field, var in self.vars.items():
            value = var.get()
            if field in required_text:
                if not value.strip(): raise ValueError(f"{_label(field)} é obrigatório.")
                result[field] = value.strip()
            elif field == "MANUFACTURER_ID": result[field] = self.manufacturer_map.get(value) or (_ for _ in ()).throw(ValueError("Fabricante é obrigatório."))
            elif field == "ACTIVE": result[field] = {"Ativo": 1, "Inativo": 0}[value]
            else: result[field] = parse_number(value, integer=field in INTEGER_FIELDS,
                                               required=field in ("NUMBER_OF_TRACKERS", "NUMBER_OF_INPUTS"),
                                               positive=field in POSITIVE_FIELDS, field=_label(field))
        return result

    def save(self):
        try:
            self.draft["inverter"] = self._collect_parent()
            for key, mapping in self.relation_vars.items(): self.draft[key] = [option for option, var in mapping.items() if var.get()]
            summary = validate_inverter_draft(self.draft)
            model = self.draft["inverter"]["MODEL"]
            if not messagebox.askyesno("Confirmar conjunto", f"Salvar {model}?\n{len(self.draft['mppts'])} grupo(s), {summary['trackers']} MPPTs e {summary['inputs']} entradas.", parent=self): return
            self.repository.save_inverter(self.draft, self.record_id); self.dirty = False; self.destroy(); self.callback()
        except Exception as exc: messagebox.showerror("Não foi possível salvar", str(exc), parent=self)


class GroupEditor(tk.Toplevel):
    def __init__(self, owner, index, characteristics=None, on_applied=None, readonly=False):
        opener = owner.focus_get() or owner.group_tree
        super().__init__(owner); self.owner, self.index = owner, index; self.title("Grupo de MPPTs")
        self.on_applied, self.readonly = on_applied, readonly
        current = copy.deepcopy(owner.draft["mppts"][index] if index is not None else characteristics or {})
        self.original_id = current.get("ID")
        try: total = owner._tracker_count()
        except ValueError as exc: messagebox.showerror("Total de MPPTs", str(exc), parent=owner); self.destroy(); return
        occupied = set().union(*(set(group.get("positions", ())) for number, group in enumerate(owner.draft["mppts"]) if number != index))
        selected = set(current.get("positions", ())); self.position_vars = {}; self.position_buttons = {}
        legend = ttk.Label(self, text="Selecionado: verde/✓  •  Disponível: vermelho/○  •  Ocupado: cinza/—"); legend.pack(anchor="w", padx=12, pady=8)
        buttons = ttk.Frame(self); buttons.pack(fill="x", padx=12)
        for position in range(1, total + 1):
            var = tk.BooleanVar(value=position in selected); self.position_vars[position] = var
            occupied_here = position in occupied
            button = tk.Checkbutton(buttons, text=f"{'—' if occupied_here else '✓' if var.get() else '○'} MPPT {position}", variable=var,
                                    state="disabled" if occupied_here else "normal", indicatoron=False,
                                    selectcolor="#86EFAC", background="#CBD5E1" if occupied_here else "#FCA5A5", width=12,
                                    takefocus=not occupied_here and not readonly, highlightthickness=2)
            button.grid(row=(position - 1)//6, column=(position - 1)%6, padx=4, pady=4)
            self.position_buttons[position] = button
            if readonly:
                button.configure(state="disabled")
        self.vars = {}; form = ttk.Frame(self, padding=12); form.pack(fill="both", expand=True)
        first_entry = None
        for row, field in enumerate(owner.MPPT_FIELDS):
            ttk.Label(form, text=_label(field)).grid(row=row, column=0, sticky="w", pady=3)
            var = tk.StringVar(value="" if current.get(field, -1) == -1 else current.get(field, "")); self.vars[field] = var
            entry = ttk.Entry(form, textvariable=var, width=22)
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=3)
            if first_entry is None:
                first_entry = entry
            if readonly:
                entry.configure(state="readonly")
        form.columnconfigure(1, weight=1)
        close_button = ttk.Button(form, text="Fechar" if readonly else "Aplicar ao rascunho", command=self.destroy if readonly else self.apply)
        close_button.grid(row=len(owner.MPPT_FIELDS), column=1, sticky="e", pady=8)
        initial = first_entry if readonly else next((button for button in self.position_buttons.values() if str(button.cget("state")) != "disabled"), first_entry)
        prepare_toplevel(self, opener=opener, initial=initial)

    def apply(self):
        try:
            positions = tuple(position for position, var in self.position_vars.items() if var.get()); encode_mppt_index(positions)
            group = {"positions": positions}
            if self.original_id is not None:
                group["ID"] = self.original_id
            if self.index is not None:
                group["_draft_key"] = self.owner.draft["mppts"][self.index].get("_draft_key")
            for field, var in self.vars.items():
                group[field] = parse_number(var.get(), integer=field in INTEGER_FIELDS,
                                            required=field == "NUMBER_OF_INPUTS", positive=field in POSITIVE_FIELDS,
                                            field=_label(field))
            if self.index is None: self.owner.draft["mppts"].append(group)
            else: self.owner.draft["mppts"][self.index] = group
            self.owner.dirty = True; self.owner.refresh_groups(); self.destroy()
            if self.on_applied:
                self.on_applied()
        except Exception as exc: messagebox.showerror("Grupo inválido", str(exc), parent=self)


class SourceGroupsDialog(tk.Toplevel):
    """Pré-visualiza e seleciona características, sem modificar o destino."""
    def __init__(self, parent, groups):
        opener = parent.focus_get() or parent.group_tree
        super().__init__(parent); self.title("Selecionar grupos de origem"); self.groups = groups; self.result = None
        self.tree = ttk.Treeview(self, columns=("indice", "entradas", "tensao", "corrente"), show="headings", selectmode="extended", height=10)
        headings = (("indice", "Índice de MPPTs"), ("entradas", "Entradas por MPPT"),
                    ("tensao", "Faixa de operação (V)"), ("corrente", "Corrente de operação (A)"))
        for column, title in headings:
            self.tree.heading(column, text=title); self.tree.column(column, width=175)
        for index, group in enumerate(groups):
            self.tree.insert("", "end", iid=str(index), values=(
                group.get("MPPT_INDEX"), group.get("NUMBER_OF_INPUTS"),
                f"{_display(group.get('MIN_OPERATING_VOLTAGE'))} – {_display(group.get('MAX_OPERATING_VOLTAGE'))}",
                _display(group.get("MAX_OPERATING_CURRENT")),
            ))
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        buttons = ttk.Frame(self); buttons.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(buttons, text="Cancelar", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Usar características selecionadas", command=self.accept).pack(side="right", padx=6)
        self.transient(parent); self.grab_set(); prepare_toplevel(self, opener=opener, initial=self.tree)

    def accept(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Seleção", "Selecione ao menos um grupo de origem.", parent=self); return
        self.result = [copy.deepcopy(self.groups[int(item)]) for item in selection]
        self.destroy()


class ChoiceDialog(tk.Toplevel):
    def __init__(self, parent, title, choices):
        opener = parent.focus_get() or parent.group_tree
        super().__init__(parent); self.title(title); self.result = None; self.choices = choices; self.var = tk.StringVar()
        ttk.Label(self, text="Inversor de origem:").pack(anchor="w", padx=12, pady=(12, 4))
        combo = ttk.Combobox(self, textvariable=self.var, values=tuple(choices), width=70); combo.pack(padx=12, pady=4)
        ttk.Button(self, text="Copiar grupos", command=self.accept).pack(pady=12)
        self.transient(parent); self.grab_set(); prepare_toplevel(self, opener=opener, initial=combo)
    def accept(self):
        self.result = self.choices.get(self.var.get())
        if self.result: self.destroy()
