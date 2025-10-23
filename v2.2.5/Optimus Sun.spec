# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['inv_vs_mod_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('optimus_sun.db', '.'), ('logo.png', '.'), ('optimus_sun.png', '.'), ('optimus_sun.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Optimus Sun',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['optimus_sun.ico'],
)
