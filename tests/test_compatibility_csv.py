import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from compatibility import (  # noqa: E402
    CSVFormatError,
    CompatibilityMatrix,
    CompatibilityResult,
    EquipmentSummary,
    LimitingFactor,
    MatrixCalculation,
    MatrixCellResult,
    export_matrix_csv,
    import_matrix_csv,
)


def result(quantity, power, overload, factor=LimitingFactor.OVERLOAD_LIMIT):
    return CompatibilityResult(
        quantity=quantity,
        dc_power_kw=power,
        overload_percent=overload,
        limiting_factor=factor,
        operating_current_ignored=False,
        valid=factor != LimitingFactor.MISSING_DATA,
    )


class CompatibilityCSVTests(unittest.TestCase):
    def setUp(self):
        self.inverter = EquipmentSummary(10, "WEG", "INV A", 5000, 50)
        self.module_a = EquipmentSummary(20, "FAB", "MÓDULO Á", 570)
        self.module_b = EquipmentSummary(21, "FAB", "MÓDULO B", 610)

    def calculation(self):
        matrix = CompatibilityMatrix()
        second = matrix.add_inverter(self.inverter, "INV A SEM BATERIAS")
        first = matrix.add_inverter(self.inverter, "INV A COM BATERIAS")
        module_b = matrix.add_module(self.module_b)
        module_a = matrix.add_module(self.module_a)
        cells = {
            (first.key, module_b.key): MatrixCellResult(
                result(10, 6.10, 22.0), result(12, 7.32, 101.25)
            ),
            (first.key, module_a.key): MatrixCellResult(
                result(0, 0, -100, LimitingFactor.MISSING_DATA),
                result(0, 0, -100, LimitingFactor.MISSING_DATA),
            ),
            (second.key, module_b.key): MatrixCellResult(
                result(9, 5.49, -8.0), result(9, 5.49, -8.0)
            ),
            (second.key, module_a.key): MatrixCellResult(
                result(11, 6.27, 25.4), result(11, 6.27, 25.4)
            ),
        }
        return MatrixCalculation(matrix.sorted_inverters(), tuple(matrix.modules), cells)

    def test_round_trip_preserves_display_values_order_repetition_and_bom(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder) / "matriz.csv"
            export_matrix_csv(self.calculation(), path)
            self.assertEqual(path.read_bytes()[:3], b"\xef\xbb\xbf")
            text = path.read_text(encoding="utf-8-sig")
            self.assertIn(";", text)
            self.assertIn("12;7,32;101,25%", text)
            self.assertIn("9;5,49;-8%", text)
            imported = import_matrix_csv(
                path, [self.inverter], [self.module_a, self.module_b]
            )

        self.assertEqual(
            [item.display_label for item in imported.calculation.inverters],
            ["INV A COM BATERIAS", "INV A SEM BATERIAS"],
        )
        self.assertTrue(all(not item.associated for item in imported.matrix.inverters))
        self.assertEqual(
            [item.display_model for item in imported.matrix.modules],
            ["MÓDULO B", "MÓDULO Á"],
        )
        first = imported.calculation.inverters[0]
        first_module = imported.calculation.modules[0]
        value = imported.calculation.cell(first.key, first_module.key).display_result
        self.assertEqual((value.quantity, value.dc_power_kw, value.overload_percent), (12, 7.32, 101.25))
        missing = imported.calculation.cell(first.key, imported.calculation.modules[1].key)
        self.assertFalse(missing.display_result.valid)

    def test_exact_models_associate_but_personalized_text_does_not(self):
        content = (
            "Inversor;MÓDULO B;MÓDULO B;MÓDULO B\n"
            ";610;610;610\n"
            "Inversor;Quantidade de módulos;Potência (kW);Sobrecarga (%)\n"
            "INV A;10;6,1;22%\n"
            "INV A PERSONALIZADO;11;6.71;34,2%\n"
        )
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder) / "manual.csv"
            path.write_text(content, encoding="utf-8")
            imported = import_matrix_csv(path, [self.inverter], [self.module_b])
        self.assertTrue(imported.matrix.inverters[0].associated)
        self.assertFalse(imported.matrix.inverters[1].associated)
        self.assertTrue(imported.matrix.modules[0].associated)

    def test_external_edit_is_loaded_without_recalculation(self):
        content = (
            "Inversor;MÓDULO B;MÓDULO B;MÓDULO B\n"
            ";610;610;610\n"
            "Inversor;Quantidade de módulos;Potência (kW);Sobrecarga (%)\n"
            "INV A;77;46,97;839,4%\n"
        )
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder) / "editado.csv"
            path.write_text(content, encoding="cp1252")
            imported = import_matrix_csv(path, [self.inverter], [self.module_b])
        cell = imported.calculation.cell(
            imported.matrix.inverters[0].key, imported.matrix.modules[0].key
        )
        self.assertEqual(cell.display_result.quantity, 77)
        self.assertEqual(imported.calculation.source, "imported")

    def test_unknown_module_is_preserved_for_manual_association(self):
        content = (
            "Inversor;MODELO EXTERNO;MODELO EXTERNO;MODELO EXTERNO\n"
            ";700;700;700\n"
            "Inversor;Quantidade de módulos;Potência (kW);Sobrecarga (%)\n"
            "INV A;4;2,8;-44%\n"
        )
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder) / "externo.csv"
            path.write_text(content, encoding="utf-8")
            imported = import_matrix_csv(path, [self.inverter], [self.module_b])
        module = imported.matrix.modules[0]
        self.assertFalse(module.associated)
        imported.matrix.associate_module(module.key, self.module_b)
        self.assertTrue(imported.matrix.modules[0].associated)
        self.assertEqual(imported.matrix.modules[0].display_model, "MODELO EXTERNO")

    @patch("compatibility.matrix.load_module", return_value=object())
    @patch("compatibility.matrix.load_inverter", return_value=object())
    @patch("compatibility.matrix.compare_operating_current_modes")
    def test_recalculation_is_explicit_and_replaces_imported_values(
        self, compare, _load_inverter, _load_module
    ):
        compare.return_value = (result(18, 10.98, 119.6), result(18, 10.98, 119.6))
        content = (
            "Inversor;MÓDULO B;MÓDULO B;MÓDULO B\n"
            ";610;610;610\n"
            "Inversor;Quantidade de módulos;Potência (kW);Sobrecarga (%)\n"
            "INV A;17;10,37;107,4%\n"
        )
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder) / "recalcular.csv"
            path.write_text(content, encoding="utf-8")
            imported = import_matrix_csv(path, [self.inverter], [self.module_b])
        before = imported.calculation.cell(
            imported.matrix.inverters[0].key, imported.matrix.modules[0].key
        ).display_result
        self.assertEqual(before.quantity, 17)
        compare.assert_not_called()

        recalculated = imported.matrix.calculate(object())
        self.assertEqual(recalculated.source, "calculated")
        self.assertEqual(
            recalculated.cell(
                recalculated.inverters[0].key, recalculated.modules[0].key
            ).display_result.quantity,
            18,
        )
        compare.assert_called_once()

    def test_invalid_structure_and_non_finite_values_are_rejected(self):
        invalid_documents = (
            "Inversor;X;X\n;;\nInversor;Quantidade;Potência\nA;1;2\n",
            "Inversor;X;X;X\n;500;500;500\nInversor;Quantidade de módulos;Potência (kW);Sobrecarga (%)\nA;1;NaN;0%\n",
            "Inversor;X;X;X\n;-500;-500;-500\nInversor;Quantidade de módulos;Potência (kW);Sobrecarga (%)\nA;1;0,5;0%\n",
        )
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            for index, content in enumerate(invalid_documents):
                path = Path(folder) / f"invalido-{index}.csv"
                path.write_text(content, encoding="utf-8")
                with self.subTest(index=index), self.assertRaises(CSVFormatError):
                    import_matrix_csv(path)


if __name__ == "__main__":
    unittest.main()
