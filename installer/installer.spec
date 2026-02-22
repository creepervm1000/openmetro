# installer.spec — PyInstaller build spec for OpenMetro Setup
# Build openmetro.exe first, then run: pyinstaller installer.spec

block_cipher = None

a = Analysis(
    ['installer.py'],
    pathex=['.'],
    binaries=[],
    datas=[('../dist/openmetro.exe', '.')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='openmetro-setup',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='../openmetro.ico',
)
