"""Regressões de navegação, cancelamento e encerramento da matriz."""
import sqlite3
import csv
import sys
import tempfile
import time
import tkinter as tk
import unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from compatibility import CompatibilityMatrix, EquipmentSummary  # noqa: E402
from compatibility import export_matrix_csv  # noqa: E402
from compatibility.matrix import (  # noqa: E402
    ImportedCellResult, ImportedCellValue, MatrixCalculation,
    MatrixCalculationCancelled,
)
from tools import compatibility_matrix_gui as gui  # noqa: E402


class MatrixGuiResponsivenessTests(unittest.TestCase):
    def setUp(self):
        try:
            self.app = self._make_app()
        except tk.TclError as error:
            self.skipTest(f"Tk indisponível: {error}")

    def tearDown(self):
        try:
            if self.app.winfo_exists():
                self.app._close_window()
        except tk.TclError:
            pass

    @staticmethod
    def _make_app():
        inverter = EquipmentSummary(10, "Fabricante", "Inversor", 5000)
        module = EquipmentSummary(20, "Fabricante", "Módulo", 500)
        with (patch.object(gui, "open_database", side_effect=lambda: closing(sqlite3.connect(":memory:"))),
              patch.object(gui, "list_active_inverters", return_value=[inverter]),
              patch.object(gui, "list_active_modules", return_value=[module])):
            app = gui.CompatibilityMatrixGUI()
        app.geometry("1200x800+2500+1500")
        app.update()
        return app

    def _populate(self, rows, columns):
        self.app.state_model = CompatibilityMatrix()
        inverters = [self.app.state_model.add_inverter(self.app.available_inverters[0], f"Inversor {i:03d}") for i in range(rows)]
        modules = [self.app.state_model.add_module(self.app.available_modules[0]) for _ in range(columns)]
        cell = ImportedCellResult(ImportedCellValue(10, 5.0, 0.0, True))
        calculation = MatrixCalculation(
            tuple(inverters), tuple(modules),
            {(inverter.key, module.key): cell for inverter in inverters for module in modules},
            "imported",
        )
        self.app.calculation = calculation
        return calculation

    def test_virtual_view_keeps_all_cells_but_draws_only_viewport(self):
        calculation = self._populate(100, 100)
        self.app._render_matrix()
        self.app.update_idletasks()
        self.assertEqual(len(calculation.cells), 10000)
        self.assertLess(len(self.app.matrix_canvas.find_all()), 1000)
        self.app._xview("moveto", 1)
        self.app._yview("moveto", 1)
        self.app.update_idletasks()
        x, y = 400, 160
        column = int((self.app.matrix_canvas.canvasx(x) - 280) // 360)
        row = int((self.app.matrix_canvas.canvasy(y) - 84) // 32)
        details = Mock()
        self.app._show_details = details
        self.app._matrix_click(SimpleNamespace(x=x, y=y))
        self.assertEqual(details.call_count, 1)
        self.assertIs(details.call_args.args[2], calculation.cell(
            calculation.inverters[row].key, calculation.modules[column].key
        ))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "large.csv"
            export_matrix_csv(calculation, path)
            with path.open(encoding="utf-8-sig", newline="") as handle:
                exported = list(csv.reader(handle, delimiter=";"))
            self.assertEqual(len(exported), 101)
            self.assertEqual(len(exported[0]), 301)

    def test_cancel_and_close_leave_no_matrix_callbacks(self):
        previous = self._populate(1, 1)

        def slow_calculation(_matrix, _connection, _options, progress, is_cancelled):
            while not is_cancelled():
                time.sleep(.005)
            raise MatrixCalculationCancelled()

        with (patch.object(gui, "open_database", side_effect=lambda: closing(sqlite3.connect(":memory:"))),
              patch.object(CompatibilityMatrix, "calculate", slow_calculation)):
            self.app.start_calculation()
            self.app.cancel_calculation()
            deadline = time.monotonic() + 3
            while self.app.calculating and time.monotonic() < deadline:
                self.app.update()
                time.sleep(.01)
            self.assertFalse(self.app.calculating)
            self.assertIs(self.app.calculation, previous)
            self.assertIsNone(self.app._poll_after)
            self.app.start_calculation()
            worker = self.app._worker_thread
            self.app._close_window()
            worker.join(timeout=2)
            self.assertFalse(worker.is_alive())
            self.assertIsNone(self.app._poll_after)
            self.assertIsNone(self.app._paint_after)


if __name__ == "__main__":
    unittest.main()
