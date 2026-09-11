import copy
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
import tkinter as tk

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from catalog import (
    CatalogRepository, CatalogValidationError, decode_mppt_index,
    encode_mppt_index, parse_number, validate_inverter_draft,
)
from catalog.gui import ENUM_LABELS, GroupEditor, InverterEditor, _label


SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE manufacturer(ID INTEGER PRIMARY KEY, NAME TEXT NOT NULL, CATEGORY INTEGER CHECK(CATEGORY IN(0,1,2)));
CREATE TABLE inverter(ID INTEGER PRIMARY KEY, MODEL TEXT NOT NULL, MANUFACTURER_ID INTEGER NOT NULL,
 DIM_WIDTH REAL DEFAULT -1, DIM_HEIGHT REAL DEFAULT -1, DIM_DEPTH REAL DEFAULT -1, DIM_WEIGHT REAL DEFAULT -1,
 MAX_OPERATING_TEMPERATURE INTEGER, MIN_OPERATING_TEMPERATURE INTEGER, COOLING_MODE TEXT NOT NULL,
 PROTECTION_DEGREE TEXT NOT NULL, TOPOLOGY TEXT NOT NULL, RATED_ACTIVE_POWER INTEGER DEFAULT -1,
 MAX_ACTIVE_POWER INTEGER DEFAULT -1, RATED_OUTPUT_VOLTAGE REAL DEFAULT -1, RATED_OUTPUT_CURRENT REAL DEFAULT -1,
 MAX_OUTPUT_CURRENT REAL DEFAULT -1, OVERLOAD INTEGER DEFAULT -1, NUMBER_OF_TRACKERS INTEGER DEFAULT -1,
 NUMBER_OF_INPUTS INTEGER DEFAULT -1, ACTIVE INTEGER NOT NULL CHECK(ACTIVE IN(0,1)),
 FOREIGN KEY(MANUFACTURER_ID) REFERENCES manufacturer(ID));
CREATE TABLE mppt(ID INTEGER PRIMARY KEY, INVERTER_ID INTEGER NOT NULL, MPPT_INDEX INTEGER,
 NUMBER_OF_INPUTS INTEGER, MAX_INPUT_VOLTAGE INTEGER DEFAULT -1, MIN_STARTUP_VOLTAGE INTEGER DEFAULT -1,
 MAX_OPERATING_VOLTAGE INTEGER DEFAULT -1, MIN_OPERATING_VOLTAGE INTEGER DEFAULT -1,
 MAX_FULL_LOAD_VOLTAGE INTEGER DEFAULT -1, MIN_FULL_LOAD_VOLTAGE INTEGER DEFAULT -1,
 RATED_INPUT_VOLTAGE INTEGER DEFAULT -1, MAX_SHORT_CIRCUIT_CURRENT REAL DEFAULT -1,
 MAX_OPERATING_CURRENT REAL DEFAULT -1, FOREIGN KEY(INVERTER_ID) REFERENCES inverter(ID) ON DELETE CASCADE);
CREATE TABLE inverter_system(ID INTEGER PRIMARY KEY, INVERTER_ID INTEGER NOT NULL,
 SYSTEM_TYPE TEXT CHECK(SYSTEM_TYPE IN('ON-GRID','OFF-GRID','GRIDZERO','HYBRID')),
 FOREIGN KEY(INVERTER_ID) REFERENCES inverter(ID) ON DELETE CASCADE);
CREATE TABLE inverter_communication(ID INTEGER PRIMARY KEY, INVERTER_ID INTEGER NOT NULL,
 COMMUNICATION_TYPE TEXT CHECK(COMMUNICATION_TYPE IN('DISPLAY','RS485','WIFI','LED','USB','4G')),
 FOREIGN KEY(INVERTER_ID) REFERENCES inverter(ID) ON DELETE CASCADE);
CREATE TABLE inverter_output_mode(ID INTEGER PRIMARY KEY, INVERTER_ID INTEGER NOT NULL,
 OUTPUT_MODE TEXT CHECK(OUTPUT_MODE IN('THREE_PHASE_FOUR_WIRE','THREE_PHASE_THREE_WIRE','SINGLE_PHASE')),
 FOREIGN KEY(INVERTER_ID) REFERENCES inverter(ID) ON DELETE CASCADE);
CREATE TABLE module(ID INTEGER PRIMARY KEY, MODEL TEXT NOT NULL, MANUFACTURER_ID INTEGER NOT NULL,
 DIM_WIDTH REAL DEFAULT -1, DIM_HEIGHT REAL DEFAULT -1, DIM_DEPTH REAL DEFAULT -1, DIM_WEIGHT REAL DEFAULT -1,
 WP INTEGER DEFAULT -1, VMPP REAL DEFAULT -1, IMPP REAL DEFAULT -1, VOC REAL DEFAULT -1, ISC REAL DEFAULT -1,
 SOLAR_CELLS TEXT CHECK(SOLAR_CELLS IN('MONOCRISTALINO','POLICRISTALINO')),
 CELL_TYPE TEXT CHECK(CELL_TYPE IN('FULL CELL','HALF CELL')),
 SURFACE_TYPE TEXT CHECK(SURFACE_TYPE IN('MONOFACIAL','BIFACIAL')),
 COEF_PMAX REAL DEFAULT -.35, COEF_VOC REAL DEFAULT -.3, COEF_ISC REAL DEFAULT .05,
 ACTIVE INTEGER NOT NULL CHECK(ACTIVE IN(0,1)), FOREIGN KEY(MANUFACTURER_ID) REFERENCES manufacturer(ID));
"""


def inverter_draft():
    return {
        "inverter": {
            "MODEL": "Teste", "MANUFACTURER_ID": 1, "COOLING_MODE": "Natural",
            "PROTECTION_DEGREE": "IP65", "TOPOLOGY": "Sem transformador",
            "NUMBER_OF_TRACKERS": 6, "NUMBER_OF_INPUTS": 10, "ACTIVE": 1,
        },
        "mppts": [
            {"positions": (1, 4), "NUMBER_OF_INPUTS": 1},
            {"positions": (2, 3, 5, 6), "NUMBER_OF_INPUTS": 2},
        ],
        "systems": ["ON-GRID"], "communications": ["RS485"],
        "output_modes": ["THREE_PHASE_FOUR_WIRE"],
    }


class NumberParserTests(unittest.TestCase):
    def test_decimal_comma_point_integer_and_unknown(self):
        self.assertEqual(parse_number(" 12,5 "), 12.5)
        self.assertEqual(parse_number("12.5"), 12.5)
        self.assertEqual(parse_number("6,0", integer=True), 6)
        self.assertEqual(parse_number(""), -1)
        self.assertEqual(parse_number("-0,35"), -0.35)

    def test_rejects_ambiguous_fractional_integer_nan_units(self):
        for value, kwargs in (("1.234,56", {}), ("6,5", {"integer": True}),
                              ("NaN", {}), ("inf", {}), ("12 V", {})):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_number(value, **kwargs)

    def test_portuguese_labels_do_not_change_internal_enums(self):
        self.assertEqual(_label("ID"), "Id")
        self.assertEqual(_label("MAX_OPERATING_CURRENT"), "Corrente máxima de operação (A)")
        self.assertEqual(ENUM_LABELS["TRANSFORMERLESS"] if "TRANSFORMERLESS" in ENUM_LABELS else "TRANSFORMERLESS", "TRANSFORMERLESS")
        reverse = {label: value for value, label in ENUM_LABELS.items()}
        self.assertEqual(reverse["Meia célula"], "HALF CELL")


class MpptDomainTests(unittest.TestCase):
    def test_prime_examples_and_weighted_total(self):
        self.assertEqual(encode_mppt_index((1, 4)), 14)
        self.assertEqual(encode_mppt_index((2, 3, 5, 6)), 2145)
        self.assertEqual(decode_mppt_index(14, 6), (1, 4))
        self.assertEqual(decode_mppt_index(2145, 6), (2, 3, 5, 6))
        self.assertEqual(validate_inverter_draft(inverter_draft())["weighted_inputs"], 10)

    def test_zero_sentinel_expands_to_all_mppts(self):
        self.assertEqual(decode_mppt_index(0, 6), (1, 2, 3, 4, 5, 6))
        draft = inverter_draft()
        draft["mppts"] = [{"MPPT_INDEX": 0, "NUMBER_OF_INPUTS": 2}]
        draft["inverter"]["NUMBER_OF_INPUTS"] = 12
        self.assertEqual(validate_inverter_draft(draft)["weighted_inputs"], 12)

    def test_homogeneous_and_heterogeneous_round_trip(self):
        draft = inverter_draft()
        draft["mppts"] = [{"positions": (1, 2, 3, 4, 5, 6), "NUMBER_OF_INPUTS": 2}]
        draft["inverter"]["NUMBER_OF_INPUTS"] = 12
        self.assertEqual(validate_inverter_draft(draft)["trackers"], 6)

    def test_rejects_gap_overlap_empty_repeated_and_outside(self):
        variants = []
        draft = inverter_draft(); draft["mppts"][1]["positions"] = (2, 3, 5); variants.append(draft)
        draft = inverter_draft(); draft["mppts"][1]["positions"] = (1, 2, 3, 5, 6); variants.append(draft)
        draft = inverter_draft(); draft["mppts"][0]["positions"] = (); variants.append(draft)
        draft = inverter_draft(); draft["mppts"][0]["positions"] = (1, 1); variants.append(draft)
        draft = inverter_draft(); draft["mppts"][1]["positions"] = (2, 3, 5, 7); variants.append(draft)
        for draft in variants:
            with self.subTest(draft=draft), self.assertRaises(CatalogValidationError):
                validate_inverter_draft(draft)
        with self.assertRaises(ValueError): decode_mppt_index(4, 6)

    def test_rejects_future_options_and_missing_totals(self):
        for unavailable in ("CAN", "GPRS"):
            draft = inverter_draft(); draft["communications"].append(unavailable)
            with self.subTest(unavailable=unavailable), self.assertRaises(CatalogValidationError):
                validate_inverter_draft(draft)
        draft = inverter_draft(); draft["inverter"]["NUMBER_OF_TRACKERS"] = -1
        with self.assertRaises(CatalogValidationError): validate_inverter_draft(draft)


class CatalogRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "catalog.db"
        with closing(sqlite3.connect(self.path)) as connection:
            connection.executescript(SCHEMA)
            connection.executemany("INSERT INTO manufacturer VALUES(?,?,?)", ((1, "Ambos", 2), (2, "Módulos", 1)))
            connection.commit()
        self.repository = CatalogRepository(self.path)

    def tearDown(self): self.temp.cleanup()

    def test_atomic_create_and_duplicate_have_new_ids(self):
        first = self.repository.save_inverter(inverter_draft())
        duplicate = inverter_draft(); duplicate["inverter"]["MODEL"] = "Cópia"
        second = self.repository.save_inverter(duplicate)
        self.assertNotEqual(first, second)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM mppt").fetchone()[0], 4)

    def test_homogeneous_group_is_persisted_with_zero_sentinel(self):
        draft = inverter_draft()
        draft["mppts"] = [{"positions": (1, 2, 3, 4, 5, 6), "NUMBER_OF_INPUTS": 2}]
        draft["inverter"]["NUMBER_OF_INPUTS"] = 12
        identifier = self.repository.save_inverter(draft)
        loaded = self.repository.load_inverter_draft(identifier)
        self.assertEqual(loaded["mppts"][0]["MPPT_INDEX"], 0)

    def test_induced_child_failure_rolls_back_parent(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.save_inverter(inverter_draft(), fail_after_child=True)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM inverter").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM mppt").fetchone()[0], 0)

    def test_edit_failure_preserves_existing_parent_and_children(self):
        identifier = self.repository.save_inverter(inverter_draft())
        changed = inverter_draft(); changed["inverter"]["MODEL"] = "Não deve ficar"
        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.save_inverter(changed, identifier, fail_after_child=True)
        loaded = self.repository.load_inverter_draft(identifier)
        self.assertEqual(loaded["inverter"]["MODEL"], "Teste")
        self.assertEqual(len(loaded["mppts"]), 2)

    def test_edit_preserves_existing_mppt_ids(self):
        identifier = self.repository.save_inverter(inverter_draft())
        loaded = self.repository.load_inverter_draft(identifier)
        original_ids = [group["ID"] for group in loaded["mppts"]]
        loaded["mppts"][0]["positions"] = (1, 4)
        loaded["mppts"][1]["positions"] = (2, 3, 5, 6)
        loaded["mppts"][0]["MAX_INPUT_VOLTAGE"] = 1100
        self.repository.save_inverter(loaded, identifier)
        edited = self.repository.load_inverter_draft(identifier)
        self.assertEqual([group["ID"] for group in edited["mppts"]], original_ids)
        self.assertEqual(edited["mppts"][0]["MAX_INPUT_VOLTAGE"], 1100)

    def test_optional_module_numbers_are_explicit_minus_one(self):
        identifier = self.repository.save_equipment("module", {
            "MODEL": "M", "MANUFACTURER_ID": 2, "WP": -1, "VMPP": -1,
            "IMPP": -1, "VOC": -1, "ISC": -1, "COEF_PMAX": -1,
            "COEF_VOC": -1, "COEF_ISC": -1, "ACTIVE": 1,
        })
        with closing(sqlite3.connect(self.path)) as connection:
            row = connection.execute("SELECT WP,COEF_PMAX,COEF_VOC,COEF_ISC FROM module WHERE ID=?", (identifier,)).fetchone()
        self.assertEqual(row, (-1, -1.0, -1.0, -1.0))

    def test_category_rules_and_referenced_manufacturer_delete(self):
        with self.assertRaises(CatalogValidationError):
            self.repository.save_equipment(
                "module", {"MODEL": "M", "MANUFACTURER_ID": 99, "ACTIVE": 1}
            )
        self.repository.save_inverter(inverter_draft())
        with self.assertRaises(CatalogValidationError): self.repository.delete("manufacturer", 1)
        with self.assertRaises(CatalogValidationError):
            self.repository.save_equipment("manufacturer", {"NAME": "Ambos", "CATEGORY": 1}, 1)

    def test_listing_includes_inactive_and_filters(self):
        for model, active in (("Zeta", 0), ("Alfa", 1)):
            draft = inverter_draft(); draft["inverter"]["MODEL"] = model; draft["inverter"]["ACTIVE"] = active
            self.repository.save_inverter(draft)
        self.assertEqual([row["MODEL"] for row in self.repository.list_equipment("inverter")], ["Alfa", "Zeta"])
        self.assertEqual([row["MODEL"] for row in self.repository.list_equipment("inverter", active=0)], ["Zeta"])

    def test_id_search_combines_with_filters(self):
        identifier = self.repository.save_inverter(inverter_draft())
        self.assertEqual(self.repository.list_equipment("inverter", str(identifier), active=1)[0]["ID"], identifier)
        self.assertEqual(self.repository.list_equipment("inverter", str(identifier), active=0), [])
        self.assertEqual(self.repository.list_manufacturers("1")[0]["ID"], 1)

    def test_delete_inverter_cascades_children(self):
        identifier = self.repository.save_inverter(inverter_draft())
        self.repository.delete("inverter", identifier)
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM mppt").fetchone()[0], 0)


class CatalogGuiGroupTests(CatalogRepositoryTests):
    def setUp(self):
        super().setUp()
        try:
            self.root = tk.Tk(); self.root.withdraw()
        except tk.TclError as error:
            self.temp.cleanup()
            self.skipTest(f"Tk indisponível: {error}")

    def tearDown(self):
        if hasattr(self, "root"):
            self.root.destroy()
        super().tearDown()

    def _editor(self, identifier, readonly=False):
        editor = InverterEditor(
            self.root, self.repository, {"ID": identifier}, False, lambda: None,
            readonly=readonly,
        )
        editor.withdraw(); editor.update_idletasks()
        return editor

    def test_homogeneous_and_heterogeneous_rows_reach_treeview(self):
        homogeneous = inverter_draft()
        homogeneous["mppts"] = [{"positions": (1, 2, 3, 4, 5, 6), "NUMBER_OF_INPUTS": 2}]
        homogeneous["inverter"]["NUMBER_OF_INPUTS"] = 12
        homogeneous_id = self.repository.save_inverter(homogeneous)
        heterogeneous_id = self.repository.save_inverter(inverter_draft())
        first = self._editor(homogeneous_id)
        second = self._editor(heterogeneous_id)
        self.assertEqual(len(first.group_tree.get_children()), 1)
        self.assertEqual(first.group_tree.item(first.group_tree.get_children()[0], "values")[3], "0")
        self.assertEqual(len(second.group_tree.get_children()), 2)
        self.assertEqual(
            [second.group_tree.item(item, "values")[3] for item in second.group_tree.get_children()],
            ["14", "2145"],
        )
        first.destroy(); second.destroy()

    def test_inconsistent_group_is_visible_with_error(self):
        identifier = self.repository.save_inverter(inverter_draft())
        with closing(sqlite3.connect(self.path)) as connection:
            connection.execute("UPDATE mppt SET MPPT_INDEX=4 WHERE ID=(SELECT MIN(ID) FROM mppt WHERE INVERTER_ID=?)", (identifier,))
            connection.commit()
        editor = self._editor(identifier)
        item = editor.group_tree.get_children()[0]
        self.assertIn("Erro:", editor.group_tree.item(item, "values")[4])
        editor.destroy()

    def test_apply_new_group_creates_visible_stable_row_without_sql_write(self):
        editor = InverterEditor(self.root, self.repository, None, False, lambda: None)
        editor.withdraw(); editor.vars["NUMBER_OF_TRACKERS"].set("2")
        dialog = GroupEditor(editor, None); dialog.withdraw()
        dialog.position_vars[1].set(True)
        dialog.vars["NUMBER_OF_INPUTS"].set("1")
        dialog.apply(); editor.update_idletasks()
        children = editor.group_tree.get_children()
        self.assertEqual(len(children), 1)
        self.assertTrue(children[0].startswith("draft-"))
        with closing(sqlite3.connect(self.path)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM inverter").fetchone()[0], 0)
        editor.destroy()

    def test_own_positions_are_editable_and_other_groups_are_blocked(self):
        identifier = self.repository.save_inverter(inverter_draft())
        editor = self._editor(identifier)
        dialog = GroupEditor(editor, 0); dialog.withdraw()
        self.assertEqual(str(dialog.position_buttons[1]["state"]), "normal")
        self.assertEqual(str(dialog.position_buttons[4]["state"]), "normal")
        self.assertEqual(str(dialog.position_buttons[2]["state"]), "disabled")
        before = copy.deepcopy(editor.draft["mppts"])
        dialog.destroy()
        self.assertEqual(editor.draft["mppts"], before)
        editor.destroy()

    def test_copy_prepares_characteristics_but_does_not_insert_before_apply(self):
        identifier = self.repository.save_inverter(inverter_draft())
        editor = self._editor(identifier)
        before = copy.deepcopy(editor.draft["mppts"])
        captured = []
        editor.edit_group = lambda index, characteristics=None, on_applied=None: captured.append(
            (index, characteristics, on_applied)
        )
        source_group = self.repository.load_inverter_draft(identifier)["mppts"][0]
        editor._copy_group_queue([source_group])
        self.assertEqual(editor.draft["mppts"], before)
        self.assertEqual(captured[0][0], None)
        self.assertEqual(captured[0][1]["positions"], ())
        self.assertNotIn("ID", captured[0][1])
        self.assertNotIn("INVERTER_ID", captured[0][1])
        editor.destroy()

    def test_readonly_view_does_not_change_database(self):
        identifier = self.repository.save_inverter(inverter_draft())
        with closing(sqlite3.connect(self.path)) as connection:
            before = connection.total_changes, connection.execute("SELECT COUNT(*) FROM mppt").fetchone()[0]
        editor = self._editor(identifier, readonly=True)
        self.assertEqual(len(editor.group_tree.get_children()), 2)
        editor.destroy()
        with closing(sqlite3.connect(self.path)) as connection:
            after = connection.total_changes, connection.execute("SELECT COUNT(*) FROM mppt").fetchone()[0]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
