# launcher.spec
# Build with:  pyinstaller launcher.spec
# Requires:    pip install pyinstaller

import sys
from pathlib import Path
from typing import Optional
from OpenGL.GL import glGetString, GL_VERSION, GL_RENDERER, GL_VENDOR
from ctypes import util
from PyInstaller.utils.hooks import collect_dynamic_libs

block_cipher = None

a = Analysis(
    ["launcher.py"],
    pathex=[str(Path(".").resolve())],
    binaries=collect_dynamic_libs('glfw'),
    datas=[
        # Include an icon if present; remove the tuple if you have none
        # ("assets/icon.ico", "assets"),
    ],
    hiddenimports=[
        "tkinter",
        "tkinter.messagebox",
        "logging",
        "subprocess",
        "threading",
        "pathlib",
        "datetime",
        "sys",
        "os",
        "time",
        "re",
        "winreg",
        "datetime"
        "platform",
        "xml.etree.ElementTree",
        "tempfile",
        "wmi",
        "glfw",
        "winreg",
        "ctypes",
        "json",
        "datetimeplatform",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib", "numpy", "scipy", "pandas",
        "PIL", "cv2", "PyQt5", "wx",
    ],
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
    name="RetroBatLauncher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                       # compress with UPX if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                  # no console window (GUI app)
    # console=True,                 # ← flip this while debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico",         # ← add your .ico path here
    version="version_info.txt",     # optional; see version_info.txt
)
