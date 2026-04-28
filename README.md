# RetroBat Launcher v2.5.2

A Windows executable launcher for [RetroBat](https://www.retrobat.org/) with:

- 🎮 **Retro-themed splash screen** with animated scanline and progress bar
- 🔍 **Automatic path detection** — searches relative directories so it works from any drive or folder
- 🔍 **Automatic RetroBat requirement validation** — checks for minimum versions of hardware/software
- 📋 **Debug logging** — timestamped log files saved to a `logs/` folder next to the .exe
- ⚠️ **Error dialog** — friendly popup if RetroBat can't be found or requirements are not met

Tested with RetroBat-v8.0.1-stable-win64.

**REQUIREMENTS**
- Windows 10 or newer (64-bit) (Can run on 8.1 but who has that these days)
- 64-bit CPU
- Direct3D 11.1 / OpenGL 4.4 / Vulkan 1.2 compatible GPU 
- Visual C++ 2010/2015-2019 Redistributable Packages
- Base installation of RetroBat only includes ROMs that are not copyrighted, you must add these yourself

Retrobat runs in a standalone folder natively, but the system must meet minimum requirements. This
program was created to validate the requirements and run RetroBat automatically from any drive/folder if 
all validations pass or show a window with pass/fail details for each requirement. This makes a portable
drive RetroBat installation with the ROMs and console BIOS easily movable between systems and checks
the requirements.

**PLEASE NOTE** If you plan on running from a portable drive, it is recommended to use an external SSD 
(preferred) or HDD connected via USB 3.0 or higher for optimal performance, formatted as exFAT to support 
files larger than 4GB. Newer console ROMs are huge.

---

## Project Structure

```
├── 📁 assets
│   ├── 📄 icon.ico
│   └── 🖼️ icon.png
├── ⚙️ .gitignore
├── 📝 CODE_OF_CONDUCT.md
├── 📝 CONTRIBUTING.md
├── 📄 LICENSE
├── 📝 README.md
├── 📝 SECURITY.md
├── 📄 build.bat
├── 📄 changelog.txt
├── 🐍 get_cpu_info.py
├── 🐍 get_directx_version.py
├── 🐍 get_gpu_info.py
├── 🐍 get_opengl_version.py
├── 🐍 get_vcpp_redist_versions.py
├── 🐍 get_vulkan_version.py
├── 🐍 get_windows_info.py
├── 🐍 launcher.py
├── 📄 launcher.spec
└── 📄 version_info.txt

**Other folders created when building or running**

├── 📁 build                         # Scratch folder for builds
├── 📁 dist                          # Folder where compiled executable is saved
└── 📁 logs                          # Diagnostic log store each time it runs
```
---

## Requirements

| Tool | Version |
|------|---------|
| Python | 3.10 or newer |
| PyInstaller | 6.x (auto-installed by `build.bat`) |
| OS | Windows 10 / 11 |

---

## Building

### Option A — double-click

Run **`build.bat`**. It will:
1. Check for Python and PyInstaller (installs if missing)
2. Clean old build artefacts
3. Compile `RetroBatLauncher.exe` into `dist/`

### Option B — manual

```powershell
pip install pyinstaller
python -m PyInstaller launcher.spec --clean --noconfirm
```

The finished executable is at **`dist/RetroBatLauncher.exe`**.

---

## Deployment

Place `RetroBatLauncher.exe` in **any** of these positions relative to your RetroBat installation:

```
# Same folder as retrobat.exe
C:\Games\RetroBat\
├── retrobat.exe
└── RetroBatLauncher.exe     ← here

# One level above
C:\Games\
├── RetroBat\
│   └── retrobat.exe
└── RetroBatLauncher.exe     ← or here

# Subfolder alongside
C:\Games\RetroBat\
├── retrobat.exe
└── Launcher\
    └── RetroBatLauncher.exe ← or here
```

The launcher walks up to four parent directories and checks the `RETROBAT_RELATIVE_CANDIDATES` list (editable in `launcher.py`).

---

## Customisation

### Add a custom icon

1. Place a `icon.ico` file in `assets/`
2. Uncomment the `icon=` lines in `launcher.spec` and `launcher.py`
3. Rebuild

### Change search paths

Edit `RETROBAT_RELATIVE_CANDIDATES` near the top of `launcher.py`:

```python
RETROBAT_RELATIVE_CANDIDATES = [
    ".",
    "RetroBat",
    "..",
    "../RetroBat",
    "../../RetroBat",
    "D:/Emulation/RetroBat",   # ← add an absolute fallback if needed
]
```

### Show a console window for live debugging

In `launcher.spec` flip:
```python
console=True,
```

Then rebuild. You'll see real-time log output in the console while the splash is displayed.

---

## Log Files

Logs are written to `logs/launcher_YYYYMMDD_HHMMSS.log` next to the `.exe`. They contain:

- Python / platform version
- Launcher directory and environment variables
- Every path that was checked during detection
- All output from `retrobat.exe`
- Results of each system validation
- Process exit code

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "RetroBat not found" dialog | `retrobat.exe` not in any candidate path | Move the launcher closer, or add an explicit path to `RETROBAT_RELATIVE_CANDIDATES` |
| Splash flickers / crashes | Tkinter DPI issue on 4K displays | Add `root.tk.call('tk', 'scaling', 2.0)` after `self.root = tk.Tk()` in `SplashScreen.__init__` |
| `.exe` flagged by antivirus | PyInstaller packer heuristic | Whitelist `RetroBatLauncher.exe` or sign it with a code-signing certificate |
| `UPX` warning during build | UPX not on PATH | Install [UPX](https://upx.github.io/) or set `upx=False` in `launcher.spec` |
