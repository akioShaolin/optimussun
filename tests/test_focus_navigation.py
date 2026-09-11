import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk
import unittest


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

from focus_navigation import prepare_toplevel  # noqa: E402


class FocusNavigationTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk indisponível neste ambiente: {error}")
        self.root.geometry("320x200+10000+10000")

    def tearDown(self):
        if hasattr(self, "root") and self.root.winfo_exists():
            self.root.destroy()

    def test_dialog_skips_decorations_and_disabled_control(self):
        opener = ttk.Button(self.root, text="Abrir")
        opener.pack()
        dialog = tk.Toplevel(self.root)
        ttk.Label(dialog, text="Título decorativo").pack()
        first = ttk.Entry(dialog)
        first.pack()
        disabled = ttk.Button(dialog, text="Indisponível", state="disabled")
        disabled.pack()
        last = ttk.Button(dialog, text="Confirmar")
        last.pack()
        prepare_toplevel(dialog, opener=opener, initial=first)
        self.root.update()

        self.assertEqual(str(dialog.tk.call("tk_focusNext", first._w)), str(last))
        self.assertEqual(str(dialog.tk.call("tk_focusPrev", last._w)), str(first))
        restored = []
        opener.focus_set = lambda: restored.append(True)
        dialog.destroy()
        self.root.update()
        self.assertEqual(restored, [True])


if __name__ == "__main__":
    unittest.main()
