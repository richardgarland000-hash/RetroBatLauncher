# launcher.spec
# Build with:  pyinstaller launcher.spec
# Requires:    pip install pyinstaller

import datetime
import ctypes
import glfw
import hashlib
import json
import logging
import os
import pathlib
import platform
import re
import sys
import subprocess
import tempfile
import threading
import time
import tkinter
import uuid
import webbrowser
import winreg
import wmi
import xml.etree.ElementTree

from ctypes import util
from datetime import datetime
from OpenGL.GL import glGetString, GL_VERSION, GL_RENDERER, GL_VENDOR
from packaging.version import Version
from pathlib import Path
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules
from typing import Optional

block_cipher = None

all_binaries = []
all_binaries.extend(collect_dynamic_libs('psutil'))
all_binaries.extend(collect_dynamic_libs('glfw'))

all_hiddenimports = ['cpuinfo']
all_hiddenimports.extend(collect_submodules('psutil'))
all_hiddenimports.extend(collect_submodules('glfw'))

a = Analysis(
    ["launcher.py"],
    pathex=[str(Path(".").resolve())],
    #binaries=collect_dynamic_libs('glfw'),
    binaries=all_binaries,
    datas=[
        # Include an icon if present; remove the tuple if you have none
        # ("assets/icon.ico", "assets"),
    ],
    hiddenimports=all_hiddenimports,
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
