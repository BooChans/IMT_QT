# -*- mode: python ; coding: utf-8 -*-

datas = [
    (r'C:\Users\baoch\Optics\opt-venv\IMT_QT\examples\splashscreen_assets\ops_ss.png', 'splashscreen_assets'),
    (r'C:\Users\baoch\Optics\opt-venv\IMT_QT\examples\icons\arrows.png', 'icons'),
    (r'C:\Users\baoch\Optics\opt-venv\IMT_QT\examples\icons\blue_arrow.png', 'icons'),
    (r'C:\Users\baoch\Optics\opt-venv\IMT_QT\examples\icons\game.png', 'icons'),
]


a = Analysis(
    ['OpticalDiffractionSimulator.py'],
    pathex=[r'C:\Users\baoch\Optics\opt-venv\IMT_QT\examples'],
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
    name='OpticalDiffractionSimulator',
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
