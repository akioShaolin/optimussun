# -*- mode: python ; coding: utf-8 -*-

import shutil
from pathlib import Path


project_root = Path(SPECPATH)
src_dir = project_root / "src"
tools_dir = project_root / "tools"
icon_path = src_dir / "optimus_sun.ico"
common_pathex = [str(project_root), str(src_dir)]


def application_analysis(entry_point, datas=None, hiddenimports=None, excludes=None, hooksconfig=None):
    return Analysis(
        [str(entry_point)],
        pathex=common_pathex,
        binaries=[],
        datas=datas or [],
        hiddenimports=hiddenimports or [],
        hookspath=[],
        hooksconfig=hooksconfig or {},
        runtime_hooks=[],
        excludes=excludes or [],
        noarchive=False,
        optimize=0,
    )


main_analysis = application_analysis(
    src_dir / "optimus_sun.py",
    [(str(src_dir / "optimus_sun.png"), "."), (str(icon_path), ".")],
    hiddenimports=["matplotlib.backends.backend_tkagg"],
    excludes=["PySide6", "PyQt5", "PyQt6"],
    hooksconfig={"matplotlib": {"backends": ["TkAgg"]}},
)
cadastros_analysis = application_analysis(src_dir / "cadastros_db_gui.py")
matrix_analysis = application_analysis(tools_dir / "compatibility_matrix_gui.py")

MERGE(
    (main_analysis, "optimus_sun", "optimus_sun"),
    (cadastros_analysis, "cadastros", "cadastros"),
    (matrix_analysis, "matriz", "matriz"),
)


def application_exe(analysis, name):
    return EXE(
        PYZ(analysis.pure),
        analysis.scripts,
        [],
        exclude_binaries=True,
        name=name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(icon_path),
        contents_directory="_internal",
    )


main_exe = application_exe(main_analysis, "Optimus Sun")
cadastros_exe = application_exe(cadastros_analysis, "Optimus Sun Cadastros")
matrix_exe = application_exe(matrix_analysis, "Matriz de Compatibilidade")

distribution_name = "Optimus-Sun-v2.6.0"
distribution = COLLECT(
    main_exe,
    cadastros_exe,
    matrix_exe,
    main_analysis.binaries,
    main_analysis.datas,
    cadastros_analysis.binaries,
    cadastros_analysis.datas,
    matrix_analysis.binaries,
    matrix_analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=distribution_name,
)

# O banco é deliberadamente externo e compartilhado pelos três executáveis.
distribution_dir = Path(DISTPATH) / distribution_name
shutil.copy2(src_dir / "optimus_sun.db", distribution_dir / "optimus_sun.db")
