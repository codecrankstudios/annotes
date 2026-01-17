# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
import sys
import os

block_cipher = None

# Define data files to include
# Format: (source_path, dest_path)
datas = [
    ('src/templates', 'templates'),
    ('src/static', 'static'),
    ('src/config.default.yaml', '.'),
    ('src/logo.png', '.'), 
    ('src/app_icon.png', '.')
]

# Add hidden imports that might not be detected automatically
hiddenimports = [
    'pystray', 
    'PIL', 
    'PIL._tkinter_finder',
    'uvicorn',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols', 
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'jinja2'
]

a = Analysis(
    ['src/tray_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='annotes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app (no terminal)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/app_icon.png' if os.path.exists('src/app_icon.png') else None
)

# Configuration for macOS .app bundle
app = BUNDLE(
    exe,
    name='Annotes.app',
    icon='src/app_icon.png' if os.path.exists('src/app_icon.png') else None,
    bundle_identifier='com.codecrankstudios.annotes'
)
