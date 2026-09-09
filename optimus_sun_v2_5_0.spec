# -*- mode: python ; coding: utf-8 -*-

import shutil
from pathlib import Path


project_root = Path(SPECPATH)
src_dir = project_root / "src"
tools_dir = project_root / "tools"
icon_path = src_dir / "optimus_sun.ico"

common_pathex = [str(project_root), str(src_dir)]

main_analysis = Analysis(
    [str(src_dir / "optimus_sun.py")],
    pathex=common_pathex,
    binaries=[],
    datas=[
        (str(src_dir / "optimus_sun.png"), "."),
        (str(icon_path), "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

cadastros_analysis = Analysis(
    [str(src_dir / "cadastros_db_gui.py")],
    pathex=common_pathex,
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

matrix_analysis = Analysis(
    [str(tools_dir / "compatibility_matrix_gui.py")],
    pathex=common_pathex,
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

MERGE(
    (main_analysis, "optimus_sun", "optimus_sun"),
    (cadastros_analysis, "cadastros", "cadastros"),
    (matrix_analysis, "matriz", "matriz"),
)

main_pyz = PYZ(main_analysis.pure)
cadastros_pyz = PYZ(cadastros_analysis.pure)
matrix_pyz = PYZ(matrix_analysis.pure)

main_exe = EXE(
    main_pyz,
    main_analysis.scripts,
    [],
    exclude_binaries=True,
    name="Optimus Sun",
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

cadastros_exe = EXE(
    cadastros_pyz,
    cadastros_analysis.scripts,
    [],
    exclude_binaries=True,
    name="Optimus Sun Cadastros",
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

matrix_exe = EXE(
    matrix_pyz,
    matrix_analysis.scripts,
    [],
    exclude_binaries=True,
    name="Matriz de Compatibilidade",
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
    name="Optimus-Sun-v2.5.0",
)

distribution_dir = Path(DISTPATH) / "Optimus-Sun-v2.5.0"
shutil.copy2(src_dir / "optimus_sun.db", distribution_dir / "optimus_sun.db")
