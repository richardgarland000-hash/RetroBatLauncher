# RetroBat Launcher

A Windows executable launcher for [RetroBat](https://www.retrobat.org/) with:

- 🎮 **Retro-themed splash screen** with animated scanline and progress bar
- 🔍 **Automatic path detection** — searches relative directories so it works from any drive or folder
- 📋 **Debug logging** — timestamped log files saved to a `logs/` folder next to the .exe
- ⚠️ **Error dialogs** — friendly popup if RetroBat can't be found

---

## Project Structure

```
retrobat_launcher/
├── launcher.py          # Main source file
├── launcher.spec        # PyInstaller build spec
├── version_info.txt     # Windows executable metadata
├── build.bat            # One-click build script (Windows)
├── README.md
└── assets/
    └── icon.ico         # (optional) custom window icon
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
- Process exit code

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "RetroBat not found" dialog | `retrobat.exe` not in any candidate path | Move the launcher closer, or add an explicit path to `RETROBAT_RELATIVE_CANDIDATES` |
| Splash flickers / crashes | Tkinter DPI issue on 4K displays | Add `root.tk.call('tk', 'scaling', 2.0)` after `self.root = tk.Tk()` in `SplashScreen.__init__` |
| `.exe` flagged by antivirus | PyInstaller packer heuristic | Whitelist `RetroBatLauncher.exe` or sign it with a code-signing certificate |
| `UPX` warning during build | UPX not on PATH | Install [UPX](https://upx.github.io/) or set `upx=False` in `launcher.spec` |
