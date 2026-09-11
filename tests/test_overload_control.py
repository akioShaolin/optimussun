import sys
import tkinter as tk
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from overload_control import OverloadSession, bind_overload_entry, parse_overload_percent  # noqa: E402
from optimus_lib import limite_modulos_sobrecarga  # noqa: E402


class OverloadControlTests(unittest.TestCase):
    def test_registered_and_custom_are_converted_once(self):
        session = OverloadSession()
        session.select_inverter(1, 50)
        self.assertEqual(session.effective_percent(), 50)
        self.assertEqual(session.effective_fraction(), 0.5)
        session.mode = "custom"; session.custom_text = "80,5"
        self.assertEqual(session.effective_percent(), 80.5)
        self.assertEqual(session.effective_fraction(), 0.805)

    def test_effective_fraction_drives_existing_overload_formula(self):
        session = OverloadSession()
        session.select_inverter(1, 50)
        registered = limite_modulos_sobrecarga(5000, session.effective_fraction(), 0, 500)
        self.assertEqual(registered, limite_modulos_sobrecarga(5000, 0.5, 0, 500))
        session.mode = "custom"; session.custom_text = "80"
        custom = limite_modulos_sobrecarga(5000, session.effective_fraction(), 0, 500)
        self.assertEqual(custom, 18)

    def test_zero_decimal_formats_and_invalid_values(self):
        self.assertEqual(parse_overload_percent("0"), 0)
        self.assertEqual(parse_overload_percent("50.0"), 50)
        self.assertEqual(parse_overload_percent("50,0"), 50)
        for value in ("", "texto", "NaN", "inf", "-1", "1.000,5"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_overload_percent(value)

    def test_switching_inverter_resets_but_module_change_does_not(self):
        session = OverloadSession()
        session.select_inverter(1, 30)
        session.mode = "custom"; session.custom_text = "75"
        # Trocar o módulo não chama select_inverter e preserva a sessão.
        self.assertEqual(session.effective_percent(), 75)
        session.select_inverter(2, 40)
        self.assertEqual(session.mode, "registered")
        self.assertEqual(session.custom_text, "")
        self.assertEqual(session.effective_percent(), 40)

    def test_unknown_registered_requires_custom_without_mutating_source(self):
        inverter = {"ID": 3, "OVERLOAD": -1}
        session = OverloadSession()
        session.select_inverter(inverter["ID"], inverter["OVERLOAD"])
        with self.assertRaises(ValueError): session.effective_percent()
        session.mode = "custom"; session.custom_text = "25"
        self.assertEqual(session.effective_fraction(), 0.25)
        self.assertEqual(inverter["OVERLOAD"], -1)

    def test_real_entry_enter_does_not_trigger_late_edit_invalidation(self):
        try:
            root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk indisponível neste ambiente: {error}")
        calls = {"apply": 0, "edit": 0}
        try:
            entry = tk.Entry(root); entry.pack(); root.update(); entry.focus_force()
            bind_overload_entry(
                entry,
                lambda _event: calls.__setitem__("edit", calls["edit"] + 1),
                lambda _event: calls.__setitem__("apply", calls["apply"] + 1),
            )
            entry.event_generate("<KeyPress-Return>"); entry.event_generate("<KeyRelease-Return>"); root.update()
            self.assertEqual(calls, {"apply": 1, "edit": 0})
            entry.event_generate("<KeyPress-Return>"); entry.event_generate("<KeyRelease-Return>"); root.update()
            self.assertEqual(calls, {"apply": 2, "edit": 0})
            entry.event_generate("<KeyRelease>", keysym="5"); root.update()
            self.assertEqual(calls["edit"], 1)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
