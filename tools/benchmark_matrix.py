"""Benchmark da matriz com SQLite somente leitura e células sintéticas na renderização.

Uso: py -3 -X utf8 -B tools/benchmark_matrix.py LINHAS COLUNAS SNAPSHOT [calc] [baseline]
baseline carrega a GUI da tag v2.6.0 sem alterar o checkout.
"""
import ctypes
import importlib.util
import os
import subprocess
import sys
import time
import tkinter as tk
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
BASELINE = "baseline" in sys.argv[4:]
if BASELINE:
    gui = ModuleType("matrix_gui_baseline")
    gui.__file__ = str(ROOT / "tools" / "compatibility_matrix_gui.py")
    source = subprocess.check_output(["git", "show", "v2.6.0:tools/compatibility_matrix_gui.py"], cwd=ROOT).decode("utf-8")
    exec(compile(source, gui.__file__, "exec"), gui.__dict__)
else:
    spec = importlib.util.spec_from_file_location("matrix_gui", ROOT / "tools" / "compatibility_matrix_gui.py")
    gui = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gui)
from compatibility.matrix import MatrixCalculation, ImportedCellResult, ImportedCellValue

class Counters(ctypes.Structure):
    _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong)] + [
        (name, ctypes.c_size_t) for name in (
            "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
            "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage",
            "PagefileUsage", "PeakPagefileUsage",
        )
    ]

def memory_mb():
    result = Counters()
    result.cb = ctypes.sizeof(result)
    current = ctypes.windll.kernel32.GetCurrentProcess
    current.restype = ctypes.c_void_p
    read_memory = ctypes.windll.psapi.GetProcessMemoryInfo
    read_memory.argtypes = (ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong)
    read_memory.restype = ctypes.c_int
    if not read_memory(current(), ctypes.byref(result), result.cb):
        raise ctypes.WinError()
    return round(result.WorkingSetSize / 1048576, 1), round(result.PeakWorkingSetSize / 1048576, 1)

rows, columns = map(int, sys.argv[1:3])
gui.DB_PATH = Path(sys.argv[3])
app = gui.CompatibilityMatrixGUI()
app.geometry("1200x800+2500+1500")
app.update()
inverters = [app.state_model.add_inverter(app.available_inverters[i % len(app.available_inverters)], f"Inversor {i:04d}") for i in range(rows)]
modules = [app.state_model.add_module(app.available_modules[i % len(app.available_modules)]) for i in range(columns)]
cell = ImportedCellResult(ImportedCellValue(12, 7.2, 44.0, True))
app.calculation = MatrixCalculation(tuple(inverters), tuple(modules), {(i.key, m.key): cell for i in inverters for m in modules}, "imported")
app.update()
if len(sys.argv) > 4 and sys.argv[4] == "calc":
    app.state_model = gui.CompatibilityMatrix()
    for i in range(rows):
        app.state_model.add_inverter(app.available_inverters[i % len(app.available_inverters)], f"Inversor {i:04d}")
    for i in range(columns):
        app.state_model.add_module(app.available_modules[i % len(app.available_modules)])
    calc_delays = []
    visual_delays = []
    done = False
    render_started = None
    original_render = app._render_matrix
    def timed_render(*args, **kwargs):
        global render_started
        render_started = time.perf_counter()
        return original_render(*args, **kwargs)
    app._render_matrix = timed_render
    def pulse(expected=None):
        if done:
            return
        now = time.perf_counter()
        if expected is not None:
            (visual_delays if render_started is not None else calc_delays).append(max(0, (now - expected) * 1000))
        app.after(20, pulse, now + .020)
    pulse()
    starts = time.perf_counter()
    app.start_calculation()
    while app.calculating and time.perf_counter() - starts < 300:
        app.update()
        time.sleep(.005)
    done = True
    end = time.perf_counter()
    calc_delays.sort()
    visual_delays.sort()
    p95 = lambda values: values[int(.95 * (len(values) - 1))] if values else None
    print(
        f"CALC {rows}x{columns} compute_s={render_started-starts if render_started else None:.3f} "
        f"visual_s={end-render_started if render_started else None:.3f} total_s={end-starts:.3f} "
        f"compute_p95_ms={p95(calc_delays)} compute_max_ms={max(calc_delays) if calc_delays else None} "
        f"visual_p95_ms={p95(visual_delays)} visual_max_ms={max(visual_delays) if visual_delays else None} "
        f"rss_mb={memory_mb()} status={app.status_text.get()}", flush=True
    )
else:
    starts = time.perf_counter()
    app._render_matrix()
    render_return = time.perf_counter()
    app.update_idletasks()
    end = time.perf_counter()
    print(f"RENDER {rows}x{columns} call_s={render_return-starts:.3f} settled_s={end-starts:.3f} rss_mb={memory_mb()}", flush=True)
if BASELINE:
    os._exit(0)  # o processo isolado evita minutos para destruir 30 mil widgets legados
app._close_window()
