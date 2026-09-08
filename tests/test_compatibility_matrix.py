import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from compatibility import (  # noqa: E402
    CompatibilityMatrix,
    CompatibilityResult,
    EquipmentSummary,
    LimitingFactor,
    MatrixCellResult,
)


def result(quantity, power, overload, valid=True):
    return CompatibilityResult(
        quantity=quantity,
        dc_power_kw=power,
        overload_percent=overload,
        limiting_factor=LimitingFactor.OVERLOAD_LIMIT,
        operating_current_ignored=False,
        valid=valid,
    )


class MatrixSelectionTests(unittest.TestCase):
    def setUp(self):
        self.matrix = CompatibilityMatrix()
        self.inverter = EquipmentSummary(10, "WEG", "MODELO", 5000)
        self.modules = [
            EquipmentSummary(20, "A", "MÓDULO A", 500),
            EquipmentSummary(21, "B", "MÓDULO B", 550),
            EquipmentSummary(22, "C", "MÓDULO C", 600),
        ]

    def test_repeated_inverter_keeps_database_id_and_independent_labels(self):
        first = self.matrix.add_inverter(self.inverter)
        second = self.matrix.add_inverter(self.inverter)
        self.matrix.rename_inverter(first.key, "MODELO COM BATERIAS")
        self.matrix.rename_inverter(second.key, "MODELO SEM BATERIAS")

        self.assertNotEqual(first.key, second.key)
        self.assertEqual(
            [item.equipment.database_id for item in self.matrix.inverters],
            [10, 10],
        )
        self.assertEqual(
            [item.display_label for item in self.matrix.inverters],
            ["MODELO COM BATERIAS", "MODELO SEM BATERIAS"],
        )

        self.matrix.remove_inverter(first.key)
        self.assertEqual(len(self.matrix.inverters), 1)
        self.assertEqual(self.matrix.inverters[0].key, second.key)

    def test_inverters_are_sorted_by_custom_display_label(self):
        first = self.matrix.add_inverter(self.inverter, "Zulu")
        second = self.matrix.add_inverter(self.inverter, "alfa")
        self.assertEqual(
            [item.key for item in self.matrix.sorted_inverters()],
            [second.key, first.key],
        )

    def test_module_manual_order_is_preserved_and_reorderable(self):
        selected = [self.matrix.add_module(item) for item in self.modules]
        self.matrix.move_module(selected[2].key, "start")
        self.assertEqual(
            [item.equipment.model for item in self.matrix.modules],
            ["MÓDULO C", "MÓDULO A", "MÓDULO B"],
        )
        self.matrix.move_module(selected[0].key, "end")
        self.assertEqual(
            [item.equipment.model for item in self.matrix.modules],
            ["MÓDULO C", "MÓDULO B", "MÓDULO A"],
        )
        self.matrix.move_module(selected[1].key, "left")
        self.assertEqual(
            [item.equipment.model for item in self.matrix.modules],
            ["MÓDULO B", "MÓDULO C", "MÓDULO A"],
        )
        self.matrix.remove_module(selected[2].key)
        self.assertEqual(
            [item.equipment.model for item in self.matrix.modules],
            ["MÓDULO B", "MÓDULO A"],
        )

    def test_empty_custom_label_is_rejected(self):
        selected = self.matrix.add_inverter(self.inverter)
        with self.assertRaises(ValueError):
            self.matrix.rename_inverter(selected.key, "   ")

    def test_three_repeated_inverters_keep_independent_overloads_after_sorting(self):
        registered = self.matrix.add_inverter(self.inverter, "Cadastrada")
        eighty = self.matrix.add_inverter(self.inverter, "Oitenta")
        hundred = self.matrix.add_inverter(self.inverter, "Cem")
        self.matrix.configure_inverter_overload(eighty.key, "custom", 80)
        self.matrix.configure_inverter_overload(hundred.key, "custom", 100)

        ordered = self.matrix.sorted_inverters()
        by_key = {item.key: item for item in ordered}
        self.assertEqual(by_key[registered.key].overload_mode, "registered")
        self.assertIsNone(by_key[registered.key].custom_overload_percent)
        self.assertEqual(by_key[eighty.key].custom_overload_percent, 80)
        self.assertEqual(by_key[hundred.key].custom_overload_percent, 100)
        self.assertEqual({item.equipment.database_id for item in ordered}, {10})

    @patch("compatibility.matrix.load_module", return_value=object())
    @patch("compatibility.matrix.load_inverter", return_value=object())
    @patch("compatibility.matrix.compare_operating_current_modes")
    def test_calculation_uses_each_occurrence_overload_in_cache_key(
        self, compare, _load_inverter, _load_module
    ):
        compare.return_value = (result(1, 0.5, 0), result(1, 0.5, 0))
        registered = self.matrix.add_inverter(self.inverter, "A")
        custom = self.matrix.add_inverter(self.inverter, "B")
        self.matrix.configure_inverter_overload(custom.key, "custom", 100)
        self.matrix.add_module(self.modules[0])

        self.matrix.calculate(object())

        percentages = [
            call.args[2].custom_overload_percent for call in compare.call_args_list
        ]
        self.assertEqual(percentages, [None, 100])
        self.assertEqual(registered.equipment.database_id, custom.equipment.database_id)


class MatrixDisplayResultTests(unittest.TestCase):
    def test_ignored_gain_is_the_consistent_display_result(self):
        normal = result(0, 0.0, -100)
        ignored = result(15, 9.53, 90.50)
        cell = MatrixCellResult(normal, ignored)
        self.assertTrue(cell.uses_ignored_result)
        self.assertIs(cell.display_result, ignored)
        self.assertEqual(
            (
                cell.display_result.quantity,
                cell.display_result.dc_power_kw,
                cell.display_result.overload_percent,
            ),
            (15, 9.53, 90.50),
        )

    def test_equal_quantities_keep_normal_as_display_result(self):
        normal = result(14, 10.01, 100.20)
        ignored = result(14, 10.01, 100.20)
        cell = MatrixCellResult(normal, ignored)
        self.assertFalse(cell.uses_ignored_result)
        self.assertIs(cell.display_result, normal)

    def test_invalid_ignored_result_never_replaces_normal(self):
        normal = result(0, 0.0, -100)
        ignored = result(15, 9.53, 90.50, valid=False)
        cell = MatrixCellResult(normal, ignored)
        self.assertIs(cell.display_result, normal)


if __name__ == "__main__":
    unittest.main()
