import sqlite3
import sys
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from equipment_search import (  # noqa: E402
    EquipmentSearchRepository,
    SearchCriteria,
    parse_optional_number,
    parse_range,
)
from equipment_search_gui import EquipmentSearchPanel, SearchVisibilityController, format_selection_summary  # noqa: E402
from test_catalog import SCHEMA


class EquipmentSearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "search.db"
        with closing(sqlite3.connect(self.path)) as connection:
            connection.executescript(SCHEMA)
            connection.executemany("INSERT INTO manufacturer VALUES(?,?,?)", (
                (1, "Fabricante A", 2), (2, "Fabricante B", 2),
            ))
            inverter_sql = ("INSERT INTO inverter(ID,MODEL,MANUFACTURER_ID,COOLING_MODE,PROTECTION_DEGREE,TOPOLOGY,"
                            "RATED_ACTIVE_POWER,MAX_ACTIVE_POWER,RATED_OUTPUT_VOLTAGE,RATED_OUTPUT_CURRENT,MAX_OUTPUT_CURRENT,"
                            "NUMBER_OF_TRACKERS,NUMBER_OF_INPUTS,ACTIVE) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)")
            connection.executemany(inverter_sql, (
                (2, "Modelo igual", 1, "Livre", "IP65", "TRANSFORMERLESS", 5000, 5500, 220, 20, 25, 2, 2, 1),
                (10, "Modelo igual", 2, "Livre", "IP65", "TRANSFORMERLESS", 6000, 6600, 380, 15, 18, 2, 2, 0),
                (105, "Sem dados", 1, "Livre", "IP65", "TRANSFORMERLESS", -1, -1, -1, -1, -1, 2, 2, 1),
                (200, "Sem grupos", 1, "Livre", "IP65", "TRANSFORMERLESS", 7000, 7500, 380, 16, 20, 2, 2, 1),
                (220, "Modelo 127 V", 1, "Livre", "IP65", "TRANSFORMERLESS", 5000, 5500, 127, 30, 35, 1, 1, 1),
            ))
            mppt_sql = ("INSERT INTO mppt(INVERTER_ID,MPPT_INDEX,NUMBER_OF_INPUTS,MAX_INPUT_VOLTAGE,MIN_STARTUP_VOLTAGE,"
                        "MAX_OPERATING_VOLTAGE,MIN_OPERATING_VOLTAGE,MAX_SHORT_CIRCUIT_CURRENT,MAX_OPERATING_CURRENT) "
                        "VALUES(?,?,?,?,?,?,?,?,?)")
            connection.executemany(mppt_sql, (
                # No inversor 2, tensão e corrente passam em grupos diferentes.
                (2, 2, 1, 700, 100, 650, 120, 10, 5),
                (2, 3, 1, 500, 100, 450, 120, 30, 20),
                # Sentinela homogênea no inversor 10.
                (10, 0, 1, 900, 150, 800, 120, 35, 25),
                (105, 0, 1, -1, -1, -1, -1, -1, -1),
            ))
            connection.executemany("INSERT INTO inverter_system(INVERTER_ID,SYSTEM_TYPE) VALUES(?,?)", ((2, "ON-GRID"), (2, "HYBRID")))
            connection.executemany("INSERT INTO inverter_communication(INVERTER_ID,COMMUNICATION_TYPE) VALUES(?,?)", ((2, "RS485"), (2, "WIFI")))
            connection.executemany("INSERT INTO module(ID,MODEL,MANUFACTURER_ID,WP,VMPP,IMPP,VOC,ISC,SOLAR_CELLS,CELL_TYPE,SURFACE_TYPE,ACTIVE) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (
                (3, "Painel X", 1, 550, 40, 13, 49, 14, "MONOCRISTALINO", "HALF CELL", "BIFACIAL", 1),
                (20, "Painel X", 2, 600, 42, 14, 51, 15, "POLICRISTALINO", "FULL CELL", "MONOFACIAL", 0),
                (30, "Desconhecido", 1, -1, -1, -1, -1, -1, None, None, None, 1),
                (40, "Painel 620", 1, 620, 42, 14, 51, 15, "MONOCRISTALINO", "HALF CELL", "MONOFACIAL", 1),
                (41, "Painel 625", 1, 625, 42, 14, 51, 15, "MONOCRISTALINO", "HALF CELL", "MONOFACIAL", 1),
                (42, "Painel 630", 1, 630, 42, 14, 51, 15, "MONOCRISTALINO", "HALF CELL", "MONOFACIAL", 1),
            ))
            connection.commit()
        self.repository = EquipmentSearchRepository(self.path)

    def tearDown(self): self.temp.cleanup()

    def test_default_lists_active_and_inactive_without_manufacturer(self):
        self.assertEqual([row["ID"] for row in self.repository.search("inverter", order="ID")], [2, 10, 105, 200, 220])
        self.assertEqual([row["ID"] for row in self.repository.search("module", order="ID")], [3, 20, 30, 40, 41, 42])

    def test_id_text_manufacturer_power_status_are_cumulative(self):
        criteria = SearchCriteria(text="10", manufacturer_ids=(2,), model="igual", active=0, ranges={"power": (6000, 6000)})
        self.assertEqual([row["ID"] for row in self.repository.search("inverter", criteria)], [10])
        self.assertEqual(self.repository.search("inverter", SearchCriteria(text=" 105 "))[0]["ID"], 105)

    def test_inclusive_ranges_decimal_parser_and_unknown_values(self):
        self.assertEqual(parse_optional_number(" 12,5 ", "teste"), 12.5)
        self.assertEqual(parse_range("550", "600", "Potência"), (550, 600))
        ids = [row["ID"] for row in self.repository.search("module", SearchCriteria(ranges={"power": (550, 600)}), order="ID")]
        self.assertEqual(ids, [3, 20])
        for low, high in (("NaN", ""), ("10", "5"), ("1.000,5", "")):
            with self.subTest(low=low, high=high), self.assertRaises(ValueError): parse_range(low, high, "Faixa")

    def test_equal_minimum_and_maximum_apply_exact_filters(self):
        ac = self.repository.search("inverter", SearchCriteria(ranges={"ac_voltage": (220, 220)}), order="ID")
        self.assertEqual([row["ID"] for row in ac], [2])

        dc = self.repository.search("inverter", SearchCriteria(ranges={"min_operating_voltage": (120, 120)}), order="ID")
        self.assertEqual([row["ID"] for row in dc], [2, 10])
        self.assertEqual({row["AC_VOLTAGE"] for row in dc}, {220, 380})

        modules = self.repository.search("module", SearchCriteria(ranges={"power": (625, 625)}), order="ID")
        self.assertEqual([row["ID"] for row in modules], [41])

    def test_selection_summary_uses_selected_record_and_handles_unknowns(self):
        inverter = {"ID": 2, "MANUFACTURER": "Fabricante A", "MODEL": "Modelo igual", "NOMINAL_POWER": 5000, "AC_VOLTAGE": 220}
        self.assertIn("Id 2 | Potência: 5000 W | Saída CA: 220 V", format_selection_summary("inverter", inverter))
        module = {"ID": 30, "MANUFACTURER": "Fabricante A", "MODEL": "Desconhecido", "NOMINAL_POWER": -1}
        self.assertIn("Potência: Não informado", format_selection_summary("module", module))
        self.assertEqual(format_selection_summary("module", None), "Nenhum módulo selecionado")

    def test_duplicate_models_remain_distinct_and_numeric_sorting(self):
        rows = self.repository.search("inverter", SearchCriteria(model="modelo igual"), order="ID", descending=True)
        self.assertEqual([(row["ID"], row["MANUFACTURER"]) for row in rows], [(10, "Fabricante B"), (2, "Fabricante A")])

    def test_relations_do_not_duplicate_results_and_options_are_or(self):
        criteria = SearchCriteria(options={"systems": ("ON-GRID", "HYBRID"), "communications": ("RS485", "WIFI")})
        self.assertEqual([row["ID"] for row in self.repository.search("inverter", criteria)], [2])

    def test_same_mppt_group_must_meet_all_active_dc_filters(self):
        criteria = SearchCriteria(ranges={"max_input_voltage": (600, None), "max_operating_current": (15, None)})
        self.assertEqual([row["ID"] for row in self.repository.search("inverter", criteria)], [10])

    def test_any_all_homogeneous_unknown_and_no_groups(self):
        ranges = {"max_input_voltage": (600, None)}
        any_ids = {row["ID"] for row in self.repository.search("inverter", SearchCriteria(ranges=ranges, mppt_mode="any"))}
        all_ids = {row["ID"] for row in self.repository.search("inverter", SearchCriteria(ranges=ranges, mppt_mode="all"))}
        self.assertEqual(any_ids, {2, 10})
        self.assertEqual(all_ids, {10})
        self.assertNotIn(105, any_ids); self.assertNotIn(200, all_ids)

    def test_module_categories_use_or_within_field_and_and_between_fields(self):
        criteria = SearchCriteria(options={"solar_cells": ("MONOCRISTALINO", "POLICRISTALINO"), "surface_type": ("BIFACIAL",)})
        self.assertEqual([row["ID"] for row in self.repository.search("module", criteria)], [3])

    def test_advanced_dialog_draft_cancel_apply_and_validation(self):
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk indisponível neste ambiente: {error}")
        root.withdraw(); selections = []

        def descendants(widget):
            result = []
            for child in widget.winfo_children(): result.extend((child, *descendants(child)))
            return result

        try:
            panel = EquipmentSearchPanel(root, self.repository, "inverter", selections.append)
            panel.pack(); root.update_idletasks()
            self.assertEqual(int(panel.tree.cget("height")), 5)
            labels = [widget.cget("text") for widget in descendants(panel) if widget.winfo_class() == "TLabel"]
            self.assertNotIn("Modelo contém:", labels)
            self.assertEqual(panel.criteria().model, "")
            panel.tree.selection_set("2"); panel._selected()

            panel.open_advanced_dialog(); root.update_idletasks()
            dialog = panel.advanced_dialog
            first_entry = next(widget for widget in descendants(dialog) if widget.winfo_class() == "TEntry")
            first_entry.insert(0, "5000")
            cancel = next(widget for widget in descendants(dialog) if widget.winfo_class() == "TButton" and widget.cget("text") == "Cancelar")
            cancel.invoke(); root.update_idletasks()
            self.assertEqual(panel.range_vars["power"][0].get(), "")
            self.assertIsNone(panel.selected_id)
            self.assertIsNone(selections[-1])

            panel.open_advanced_dialog(); root.update_idletasks(); dialog = panel.advanced_dialog
            first_entry = next(widget for widget in descendants(dialog) if widget.winfo_class() == "TEntry")
            first_entry.insert(0, "5000")
            apply_button = next(widget for widget in descendants(dialog) if widget.winfo_class() == "TButton" and widget.cget("text") == "Aplicar filtros")
            apply_button.invoke(); root.update_idletasks()
            self.assertEqual(panel.range_vars["power"][0].get(), "5000")
            self.assertIn("(1)", panel.advanced_button.cget("text"))
            self.assertIsNone(panel.selected_id)

            panel.open_advanced_dialog(); root.update_idletasks(); dialog = panel.advanced_dialog
            first_entry = next(widget for widget in descendants(dialog) if widget.winfo_class() == "TEntry")
            first_entry.delete(0, "end"); first_entry.insert(0, "inválido")
            apply_button = next(widget for widget in descendants(dialog) if widget.winfo_class() == "TButton" and widget.cget("text") == "Aplicar filtros")
            apply_button.invoke(); root.update_idletasks()
            self.assertTrue(dialog.winfo_exists())
            self.assertEqual(panel.range_vars["power"][0].get(), "5000")
        finally:
            if root.winfo_exists(): root.destroy()

    def test_search_navigation_requires_explicit_confirmation(self):
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk indisponível neste ambiente: {error}")
        root.withdraw(); selections = []
        try:
            panel = EquipmentSearchPanel(root, self.repository, "inverter", selections.append)
            panel.pack(); root.update_idletasks()

            panel.tree.selection_set("2")
            panel.tree.focus("2")
            root.update_idletasks()
            self.assertEqual(selections, [])
            self.assertIsNone(panel.selected_id)

            panel._confirm_from_keyboard()
            self.assertEqual(panel.selected_id, 2)
            self.assertEqual(selections[-1]["ID"], 2)

            panel._invalidate_selection()
            self.assertIsNone(panel.selected_id)
            self.assertEqual(panel.tree.selection(), ())
            self.assertIsNone(selections[-1])

            panel.tree.selection_set("10")
            root.update_idletasks()
            self.assertIsNone(panel.selected_id)
            self.assertIsNone(selections[-1])

            panel.tree.identify_region = lambda _x, _y: "cell"
            panel.tree.identify_row = lambda _y: "10"
            panel._tree_clicked(SimpleNamespace(x=10, y=10))
            self.assertEqual(panel.selected_id, 10)
            self.assertEqual(selections[-1]["ID"], 10)

            panel.sort("MANUFACTURER")
            self.assertIsNone(panel.selected_id)
            self.assertEqual(panel.tree.selection(), ())
        finally:
            root.destroy()

    def test_search_visibility_has_only_full_or_collapsed_states(self):
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk indisponível neste ambiente: {error}")
        root.withdraw()
        try:
            button = ttk.Button(root); hint = ttk.Label(root)
            notebook = ttk.Notebook(root); first = ttk.Frame(notebook); second = ttk.Frame(notebook)
            notebook.add(first, text="Inversores"); notebook.add(second, text="Módulos")
            controller = SearchVisibilityController(notebook, button, hint)
            preserved = tk.StringVar(value="filtro preservado")

            controller.after_selection(False, True)
            self.assertTrue(controller.expanded)
            controller.after_selection(True, True)
            self.assertFalse(controller.expanded)
            self.assertEqual(int(notebook.cget("height")), 1)
            self.assertEqual((notebook.nametowidget(notebook.tabs()[0]), notebook.nametowidget(notebook.tabs()[1])), (first, second))

            controller.activate_tab(1)
            self.assertTrue(controller.expanded)
            self.assertEqual(notebook.index("current"), 1)
            self.assertEqual(int(notebook.cget("height")), 0)
            self.assertEqual(preserved.get(), "filtro preservado")
            controller.toggle()
            self.assertFalse(controller.expanded)
        finally:
            root.destroy()


if __name__ == "__main__": unittest.main()
