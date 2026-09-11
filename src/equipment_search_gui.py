"""Widgets de busca de equipamentos usados apenas pela GUI principal."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from equipment_search import SearchCriteria, parse_range
from focus_navigation import prepare_toplevel


RANGE_LABELS = {
    "power": "Potência nominal (W)", "max_power": "Potência ativa máxima (W)",
    "ac_voltage": "Tensão nominal de saída CA (V)", "rated_current": "Corrente CA nominal (A)",
    "max_current": "Corrente CA máxima (A)", "trackers": "Quantidade de MPPTs",
    "inputs": "Quantidade total de entradas", "max_input_voltage": "Tensão máxima de entrada CC (V)",
    "min_startup_voltage": "Tensão mínima de partida CC (V)",
    "min_operating_voltage": "Tensão mínima de operação CC (V)",
    "max_operating_voltage": "Tensão máxima de operação CC (V)",
    "max_operating_current": "Corrente máxima de operação CC (A)",
    "max_short_circuit_current": "Corrente máxima de curto-circuito CC (A)",
    "vmpp": "Vmpp (V)", "voc": "Voc (V)", "impp": "Impp (A)", "isc": "Isc (A)",
}


def format_selection_summary(entity, row):
    """Cria o resumo visível a partir do mesmo registro que controla a seleção."""
    if row is None:
        return "Nenhum inversor selecionado" if entity == "inverter" else "Nenhum módulo selecionado"

    def shown(value, suffix=""):
        return "Não informado" if value in (None, -1, "-1") else f"{value}{suffix}"

    identity = f"{row['MANUFACTURER']} — {row['MODEL']} — Id {row['ID']}"
    power = shown(row.get("NOMINAL_POWER"), " W")
    if entity == "inverter":
        return f"Inversor selecionado: {identity} | Potência: {power} | Saída CA: {shown(row.get('AC_VOLTAGE'), ' V')}"
    return f"Módulo selecionado: {identity} | Potência: {power}"


def format_selection_card(entity, row):
    """Retorna título e detalhes para os cartões persistentes de seleção."""
    if row is None:
        noun = "Inversor" if entity == "inverter" else "Módulo"
        return f"{noun}: nenhum selecionado", "Selecione um equipamento na lista acima."
    title = f"{row['MANUFACTURER']} — {row['MODEL']}"
    power = "Não informado" if row.get("NOMINAL_POWER") in (None, -1, "-1") else f"{row['NOMINAL_POWER']} W"
    details = f"Id {row['ID']}  •  Potência nominal: {power}"
    if entity == "inverter":
        voltage = "Não informada" if row.get("AC_VOLTAGE") in (None, -1, "-1") else f"{row['AC_VOLTAGE']} V"
        details += f"  •  Saída CA: {voltage}"
    return title, details
OPTION_VALUES = {
    "systems": (("Conectado à rede", "ON-GRID"), ("Isolado", "OFF-GRID"), ("Injeção zero", "GRIDZERO"), ("Híbrido", "HYBRID")),
    "communications": tuple((value, value) for value in ("DISPLAY", "RS485", "WIFI", "LED", "USB", "4G")),
    "output_modes": (("Trifásico a quatro fios", "THREE_PHASE_FOUR_WIRE"),
                     ("Trifásico a três fios", "THREE_PHASE_THREE_WIRE"), ("Monofásico", "SINGLE_PHASE")),
    "solar_cells": (("Monocristalino", "MONOCRISTALINO"), ("Policristalino", "POLICRISTALINO")),
    "cell_type": (("Célula inteira", "FULL CELL"), ("Meia célula", "HALF CELL")),
    "surface_type": (("Monofacial", "MONOFACIAL"), ("Bifacial", "BIFACIAL")),
}


class SearchVisibilityController:
    """Recolhe somente o corpo do Notebook, preservando abas e painéis vivos."""
    def __init__(self, notebook, button, hint, on_change=None):
        self.notebook, self.button, self.hint = notebook, button, hint
        self.on_change = on_change
        self.expanded = True
        button.configure(command=self.toggle)
        notebook.bind("<Button-1>", self._tab_clicked, add="+")

    def set_expanded(self, expanded, selected_index=None):
        if selected_index is not None:
            self.notebook.select(selected_index)
        if self.expanded == expanded:
            return False
        self.expanded = expanded
        self.notebook.configure(height=0 if expanded else 1)
        self.button.configure(text="Recolher pesquisa" if expanded else "Expandir pesquisa")
        self.hint.configure(text=("Pesquisa expandida — filtros e listas preservam seu estado." if expanded
                                  else "Pesquisa recolhida — clique em qualquer aba para reabrir."))
        if self.on_change is not None: self.on_change(expanded)
        return True

    def toggle(self):
        self.set_expanded(not self.expanded)

    def after_selection(self, calculated, has_pair):
        if calculated and has_pair:
            self.set_expanded(False)

    def activate_tab(self, index):
        self.set_expanded(True, index)

    def _tab_clicked(self, event):
        if self.expanded or event.y > 45:
            return
        try:
            index = self.notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        self.activate_tab(index)
        return "break"


class EquipmentSearchPanel(ttk.Frame):
    def __init__(self, parent, repository, entity, on_selection):
        super().__init__(parent, padding=7)
        self.repository, self.entity, self.on_selection = repository, entity, on_selection
        self.selected_id = None; self.order = "MODEL"; self.descending = False; self._debounce = None
        self.rows = {}; self.advanced_dialog = None
        self.text = tk.StringVar(); self.manufacturer = tk.StringVar(value="Todos")
        self.active = tk.StringVar(value="Todos"); self.message = tk.StringVar()
        self.range_vars = {}; self.option_vars = {}
        self.mppt_mode = tk.StringVar(value="any")
        self._advanced_range_keys = (
            ("power", "max_power", "ac_voltage", "rated_current", "max_current",
             "max_input_voltage", "min_startup_voltage", "min_operating_voltage",
             "max_operating_voltage", "max_operating_current", "max_short_circuit_current",
             "trackers", "inputs") if entity == "inverter" else ("vmpp", "voc", "impp", "isc")
        )
        self._advanced_option_keys = (
            ("systems", "communications", "output_modes") if entity == "inverter"
            else ("solar_cells", "cell_type", "surface_type")
        )
        for key in self._advanced_range_keys: self.range_vars[key] = (tk.StringVar(), tk.StringVar())
        for key in self._advanced_option_keys:
            self.option_vars[key] = {value: tk.BooleanVar() for _label, value in OPTION_VALUES[key]}
        self.manufacturers = repository.manufacturers(entity)
        self.manufacturer_map = {f"{row['NAME']} (Id {row['ID']})": row["ID"] for row in self.manufacturers}
        self._build(); self.refresh()

    def _build(self):
        basic = ttk.Frame(self); basic.pack(fill="x")
        ttk.Label(basic, text="Busca por Id, modelo ou fabricante:").grid(row=0, column=0, sticky="w")
        self.search_entry = ttk.Entry(basic, textvariable=self.text, width=31)
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        self.search_entry.bind("<Button-1>", self._invalidate_selection)
        self.search_entry.bind("<FocusIn>", self._invalidate_selection)
        self.search_entry.bind("<KeyRelease>", self._schedule_refresh)
        self.search_entry.bind("<Return>", self._search_enter)
        ttk.Label(basic, text="Fabricante:").grid(row=0, column=1, sticky="w")
        manufacturer = ttk.Combobox(basic, textvariable=self.manufacturer, state="readonly",
                                    values=("Todos", *self.manufacturer_map), width=27)
        manufacturer.grid(row=1, column=1, sticky="ew", padx=(0, 6))
        manufacturer.bind("<<ComboboxSelected>>", self._filter_changed)
        status_column = 0
        second_row = 3
        if self.entity == "module":
            power_box = ttk.Frame(basic)
            power_box.grid(row=3, column=0, sticky="w", pady=(6, 0), padx=(0, 6))
            low, high = tk.StringVar(), tk.StringVar(); self.range_vars["power"] = (low, high)
            ttk.Label(power_box, text="Potência do módulo (W):").grid(row=0, column=0, padx=(0, 5))
            for column, (caption, var) in enumerate((("Mín.", low), ("Máx.", high)), start=1):
                ttk.Label(power_box, text=caption).grid(row=0, column=column * 2 - 1)
                entry = ttk.Entry(power_box, textvariable=var, width=8); entry.grid(row=0, column=column * 2, padx=(2, 6))
                entry.bind("<Button-1>", self._invalidate_selection)
                entry.bind("<FocusIn>", self._invalidate_selection)
                entry.bind("<KeyRelease>", self._schedule_refresh)
                entry.bind("<Return>", self._search_enter)
            status_column = 1
        ttk.Label(basic, text="Situação:").grid(row=second_row, column=status_column, sticky="w", padx=(0, 4), pady=(6, 0))
        status = ttk.Combobox(basic, textvariable=self.active, state="readonly", values=("Todos", "Ativos", "Inativos"), width=12)
        status.grid(row=second_row, column=status_column + 1, sticky="w", padx=(0, 10), pady=(6, 0))
        status.bind("<<ComboboxSelected>>", self._filter_changed)
        self.advanced_button = ttk.Button(basic, text="Filtros avançados…", command=self.open_advanced_dialog)
        self.advanced_button.grid(row=second_row, column=status_column + 2, padx=4, pady=(6, 0), sticky="w")
        ttk.Button(basic, text="Limpar filtros", command=self.clear).grid(row=second_row, column=status_column + 3, padx=4, pady=(6, 0), sticky="w")
        basic.columnconfigure(0, weight=3); basic.columnconfigure(1, weight=2)

        columns = ("ID", "MANUFACTURER", "MODEL", "NOMINAL_POWER", "ACTIVE") + (("AC_VOLTAGE",) if self.entity == "inverter" else ())
        table = ttk.Frame(self); table.pack(fill="x", pady=(6, 0))
        style = ttk.Style(self); style.configure("Search.Treeview", rowheight=26)
        style.map("Search.Treeview", background=[("selected", "#1F4E78")], foreground=[("selected", "#FFFFFF")])
        self.tree = ttk.Treeview(table, columns=columns, show="headings", selectmode="browse", height=5, style="Search.Treeview")
        labels = {"ID":"Id", "MANUFACTURER":"Fabricante", "MODEL":"Modelo", "NOMINAL_POWER":"Potência nominal (W)", "ACTIVE":"Situação", "AC_VOLTAGE":"Tensão CA nominal (V)"}
        for column in columns:
            self.tree.heading(column, text=labels[column], command=lambda value=column: self.sort(value))
            self.tree.column(column, width=65 if column in ("ID", "ACTIVE") else 145, anchor="center" if column != "MODEL" and column != "MANUFACTURER" else "w")
        scrollbar = ttk.Scrollbar(table, command=self.tree.yview); self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew"); scrollbar.grid(row=0, column=1, sticky="ns")
        table.rowconfigure(0, weight=1); table.columnconfigure(0, weight=1)
        self.tree.bind("<ButtonRelease-1>", self._tree_clicked)
        self.tree.bind("<Return>", self._confirm_from_keyboard)
        ttk.Label(self, textvariable=self.message).pack(fill="x", pady=(3, 0))

    def _add_range(self, parent, key, row, variables):
        ttk.Label(parent, text=RANGE_LABELS[key], wraplength=210).grid(row=row, column=0, sticky="w", padx=(2, 5), pady=2)
        low, high = variables[key]
        for column, (caption, var) in enumerate((("Mín.", low), ("Máx.", high)), start=1):
            box = ttk.Frame(parent); box.grid(row=row, column=column, padx=2)
            ttk.Label(box, text=caption).pack(side="left")
            ttk.Entry(box, textvariable=var, width=9).pack(side="left", padx=(2, 0))

    def _add_options(self, parent, keys, start_row, variables):
        titles = {"systems":"Sistemas", "communications":"Comunicação", "output_modes":"Modo de saída", "solar_cells":"Tecnologia", "cell_type":"Tipo de célula", "surface_type":"Superfície"}
        for offset, key in enumerate(keys):
            box = ttk.LabelFrame(parent, text=titles[key]); box.grid(row=start_row + offset, column=0, columnspan=3, sticky="ew", pady=2)
            max_columns = 3
            for pos, (label, value) in enumerate(OPTION_VALUES[key]):
                ttk.Checkbutton(box, text=label, variable=variables[key][value]).grid(row=pos // max_columns, column=pos % max_columns, sticky="w", padx=3)

    def _advanced_count(self):
        count = sum(bool(low.get().strip() or high.get().strip()) for key, (low, high) in self.range_vars.items() if key in self._advanced_range_keys)
        count += sum(var.get() for key in self._advanced_option_keys for var in self.option_vars[key].values())
        if self.entity == "inverter" and self.mppt_mode.get() != "any": count += 1
        return count

    def _update_advanced_button(self):
        count = self._advanced_count()
        self.advanced_button.configure(text=f"Filtros avançados… ({count})" if count else "Filtros avançados…")

    def open_advanced_dialog(self):
        self._invalidate_selection()
        if self.advanced_dialog is not None and self.advanced_dialog.winfo_exists():
            self.advanced_dialog.deiconify(); self.advanced_dialog.lift(); self.advanced_dialog.focus_set(); return
        opener = self.focus_get() or self.advanced_button
        owner = self.winfo_toplevel(); dialog = tk.Toplevel(owner); self.advanced_dialog = dialog
        noun = "Inversores" if self.entity == "inverter" else "Módulos"
        dialog.title(f"Filtros avançados — {noun}"); dialog.transient(owner); dialog.resizable(True, True)
        screen_w, screen_h = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
        width, height = min(1040, screen_w - 80), min(650, screen_h - 120)
        owner.update_idletasks(); x = max(20, owner.winfo_rootx() + (owner.winfo_width() - width) // 2); y = max(20, owner.winfo_rooty() + (owner.winfo_height() - height) // 2)
        dialog.geometry(f"{width}x{height}+{min(x, screen_w-width-20)}+{min(y, screen_h-height-60)}")

        draft_ranges = {key: (tk.StringVar(value=low.get()), tk.StringVar(value=high.get())) for key, (low, high) in self.range_vars.items() if key in self._advanced_range_keys}
        draft_options = {key: {value: tk.BooleanVar(value=var.get()) for value, var in self.option_vars[key].items()} for key in self._advanced_option_keys}
        draft_mppt = tk.StringVar(value=self.mppt_mode.get())
        error_text = tk.StringVar()

        shell = ttk.Frame(dialog, padding=8); shell.pack(fill="both", expand=True)
        shell.rowconfigure(0, weight=1); shell.columnconfigure(0, weight=1)
        canvas = tk.Canvas(shell, highlightthickness=0); scroll = ttk.Scrollbar(shell, orient="vertical", command=canvas.yview)
        body = ttk.Frame(canvas, padding=(4, 2)); window = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set); canvas.grid(row=0, column=0, sticky="nsew"); scroll.grid(row=0, column=1, sticky="ns")
        body.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))

        if self.entity == "inverter":
            ac = ttk.LabelFrame(body, text="Saída CA — rede/carga", padding=6); dc = ttk.LabelFrame(body, text="Entrada CC — grupos de MPPTs", padding=6); general = ttk.LabelFrame(body, text="Características gerais", padding=6)
            ac.grid(row=0, column=0, sticky="nsew", padx=4); dc.grid(row=0, column=1, sticky="nsew", padx=4); general.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(8, 0))
            for row, key in enumerate(("power", "max_power", "ac_voltage", "rated_current", "max_current")): self._add_range(ac, key, row, draft_ranges)
            for row, key in enumerate(("max_input_voltage", "min_startup_voltage", "min_operating_voltage", "max_operating_voltage", "max_operating_current", "max_short_circuit_current")): self._add_range(dc, key, row, draft_ranges)
            ttk.Label(dc, text="Aplicação dos critérios CC:").grid(row=6, column=0, columnspan=3, sticky="w", pady=(5, 0))
            ttk.Radiobutton(dc, text="Ao menos um grupo atende todos", variable=draft_mppt, value="any").grid(row=7, column=0, columnspan=3, sticky="w")
            ttk.Radiobutton(dc, text="Todos os grupos atendem todos", variable=draft_mppt, value="all").grid(row=8, column=0, columnspan=3, sticky="w")
            for row, key in enumerate(("trackers", "inputs")): self._add_range(general, key, row, draft_ranges)
            self._add_options(general, self._advanced_option_keys, 2, draft_options); body.columnconfigure(0, weight=1); body.columnconfigure(1, weight=1)
        else:
            electrical = ttk.LabelFrame(body, text="Características elétricas do módulo", padding=6); general = ttk.LabelFrame(body, text="Características gerais", padding=6)
            electrical.grid(row=0, column=0, sticky="nsew", padx=4); general.grid(row=0, column=1, sticky="nsew", padx=4)
            for row, key in enumerate(self._advanced_range_keys): self._add_range(electrical, key, row, draft_ranges)
            self._add_options(general, self._advanced_option_keys, 0, draft_options); body.columnconfigure(0, weight=1); body.columnconfigure(1, weight=1)

        footer = ttk.Frame(shell); footer.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Label(footer, textvariable=error_text, foreground="#C62828").pack(side="left", fill="x", expand=True)

        def close():
            if dialog.grab_current() == dialog: dialog.grab_release()
            self.advanced_dialog = None; dialog.destroy()

        def clear_draft():
            for low, high in draft_ranges.values(): low.set(""); high.set("")
            for mapping in draft_options.values():
                for var in mapping.values(): var.set(False)
            draft_mppt.set("any"); error_text.set("")

        def apply():
            try:
                for key, (low, high) in draft_ranges.items(): parse_range(low.get(), high.get(), RANGE_LABELS[key])
            except ValueError as error:
                error_text.set(str(error)); return
            for key, (low, high) in draft_ranges.items(): self.range_vars[key][0].set(low.get()); self.range_vars[key][1].set(high.get())
            for key, mapping in draft_options.items():
                for value, var in mapping.items(): self.option_vars[key][value].set(var.get())
            self.mppt_mode.set(draft_mppt.get()); self._update_advanced_button(); close(); self.refresh()

        ttk.Button(footer, text="Aplicar filtros", command=apply).pack(side="right", padx=(5, 0))
        ttk.Button(footer, text="Cancelar", command=close).pack(side="right", padx=(5, 0))
        ttk.Button(footer, text="Limpar avançados", command=clear_draft).pack(side="right")

        def wheel(event):
            if event.widget.winfo_class() in ("TCombobox", "Treeview"): return
            delta = -1 if getattr(event, "delta", 0) > 0 else 1
            if getattr(event, "num", None) in (4, 5): delta = -1 if event.num == 4 else 1
            canvas.yview_scroll(delta, "units"); return "break"

        def bind_scroll(widget):
            for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"): widget.bind(sequence, wheel, add="+")
            for child in widget.winfo_children(): bind_scroll(child)

        bind_scroll(body); dialog.protocol("WM_DELETE_WINDOW", close); dialog.bind("<Escape>", lambda _e: close())

        def initialize_dialog():
            def first_entry(widget):
                for child in widget.winfo_children():
                    if child.winfo_class() == "TEntry": return child
                    found = first_entry(child)
                    if found is not None: return found
                return None
            target = first_entry(body)
            canvas.yview_moveto(0)
            dialog.after(30, lambda: canvas.yview_moveto(0))
            prepare_toplevel(dialog, opener=opener, initial=target, canvas=canvas)

        dialog.grab_set(); dialog.after_idle(initialize_dialog)

    @staticmethod
    def _reveal_widget(canvas, widget):
        canvas.update_idletasks(); top = widget.winfo_rooty() - canvas.winfo_rooty(); bottom = top + widget.winfo_height()
        if top < 0: canvas.yview_scroll(-1, "units")
        elif bottom > canvas.winfo_height(): canvas.yview_scroll(1, "units")

    def _schedule_refresh(self, _event=None):
        self._invalidate_selection(cancel_debounce=False)
        if self._debounce is not None: self.after_cancel(self._debounce)
        self._debounce = self.after(300, self.refresh)

    def _search_enter(self, _event=None):
        if self._debounce is not None:
            self.after_cancel(self._debounce)
            self._debounce = None
        self.refresh()
        return "break"

    def _filter_changed(self, _event=None):
        self._invalidate_selection()
        self.refresh()

    def _invalidate_selection(self, _event=None, cancel_debounce=True):
        """Descarta a escolha confirmada sem afetar a outra aba da aplicação."""
        if cancel_debounce and self._debounce is not None:
            self.after_cancel(self._debounce)
            self._debounce = None
        had_selection = self.selected_id is not None
        self.selected_id = None
        if self.tree.selection():
            self.tree.selection_remove(*self.tree.selection())
        if had_selection:
            self.on_selection(None)
        self.message.set(f"{len(self.tree.get_children())} resultado(s)" if self.tree.get_children() else "Nenhum equipamento encontrado")

    def criteria(self):
        ranges = {key: parse_range(low.get(), high.get(), RANGE_LABELS[key]) for key, (low, high) in self.range_vars.items()}
        return SearchCriteria(
            text=self.text.get(), manufacturer_ids=((self.manufacturer_map[self.manufacturer.get()],) if self.manufacturer.get() in self.manufacturer_map else ()),
            model="", active={"Ativos":1, "Inativos":0}.get(self.active.get()), ranges=ranges,
            options={key: tuple(value for value, var in mapping.items() if var.get()) for key, mapping in self.option_vars.items()},
            mppt_mode=self.mppt_mode.get() if self.entity == "inverter" else "any",
        )

    def refresh(self):
        try:
            rows = self.repository.search(self.entity, self.criteria(), self.order, self.descending)
        except ValueError as error:
            self.message.set(str(error)); return
        self._debounce = None
        self.rows = {row["ID"]: row for row in rows}
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            values = (row["ID"], row["MANUFACTURER"], row["MODEL"], row["NOMINAL_POWER"], "Ativo" if row["ACTIVE"] else "Inativo")
            if self.entity == "inverter": values += (row["AC_VOLTAGE"],)
            self.tree.insert("", "end", iid=str(row["ID"]), values=values)
        self.message.set(f"{len(rows)} resultado(s)" if rows else "Nenhum equipamento encontrado")

    def _selected(self, _event=None):
        """Compatibilidade interna: confirma explicitamente a linha destacada."""
        selection = self.tree.selection()
        if not selection: return
        self._confirm_iid(selection[0])

    def _confirm_iid(self, iid):
        if self._debounce is not None:
            self.after_cancel(self._debounce)
            self._debounce = None
        self.selected_id = int(iid); values = self.tree.item(iid, "values")
        row = self.rows[self.selected_id]
        self.message.set(f"{len(self.tree.get_children())} resultado(s) — selecionado: Id {self.selected_id}, {values[2]}")
        self.on_selection(row)

    def _tree_clicked(self, event):
        if self.tree.identify_region(event.x, event.y) not in ("cell", "tree"):
            return
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        self.tree.focus(iid)
        self._confirm_iid(iid)

    def _confirm_from_keyboard(self, _event=None):
        iid = self.tree.focus()
        if not iid:
            selection = self.tree.selection()
            iid = selection[0] if selection else ""
        if iid and iid in self.tree.get_children():
            self._confirm_iid(iid)
        return "break"

    def sort(self, column):
        self._invalidate_selection()
        self.descending = not self.descending if self.order == column else False; self.order = column; self.refresh()

    def clear(self):
        self._invalidate_selection()
        self.text.set(""); self.manufacturer.set("Todos"); self.active.set("Todos")
        for low, high in self.range_vars.values(): low.set(""); high.set("")
        for mapping in self.option_vars.values():
            for var in mapping.values(): var.set(False)
        if self.entity == "inverter": self.mppt_mode.set("any")
        self._update_advanced_button()
        self.refresh()
