# -*- mode: python ; coding: utf-8 -*-

datas = [
    (r'c:/Users/baoch/Optics/opt-venv/IMT_QT/examples/icons/arrows.png', 'icons'),
    (r'c:/Users/baoch/Optics/opt-venv/IMT_QT/examples/icons/blue_arrow.png', 'icons'),
    (r'c:/Users/baoch/Optics/opt-venv/IMT_QT/examples/icons/floppy-disk.png', 'icons'),
    (r'c:/Users/baoch/Optics/opt-venv/IMT_QT/examples/icons\game.png', 'icons')
]

a = Analysis(
    ['DOEDesignSimulation.py'],
    pathex=[],
    binaries=[],
    datas=datas,
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
    name='DOEDesignSimulation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
