"""
RetroBat Launcher
-----------------
A Windows executable launcher for RetroBat that is pre-installed 
on an external drive. Features splash screen, path detection, 
dependency checks, and debug logging.

RetroBat requirements (all validated):

- Windows 10 or newer (64-bit) (Can run on 8.1 but who has that these days)
- 64-bit CPU
- Direct3D 11.1 / OpenGL 4.4 / Vulkan 1.2 compatible GPU 
- Visual C++ 2010/2015-2019 Redistributable Packages

Be sure to update self.version_text in SplashScreen.__init__  to display the
current version of the launcher. You can also implement dynamic reading from
a file if you want to get fancy, but both executable and valid version_info.txt
must exists in the same directory.

Build with: pyinstaller & launcher.spec

"""

# ─────────────────────────────────────────────
#  Imports
# ─────────────────────────────────────────────

import sys
import os
import subprocess
import logging
import tkinter as tk
import re

from tkinter import messagebox
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import validation functions from external scripts
from get_cpu_info import get_cpu_arch # get_cpu_info.py
from get_directx_version import validate_directx # get_directx_version.py
from get_gpu_info import get_gpu_info # get_gpu_info.py
from get_opengl_version import validate_opengl # get_opengl_version.py
from get_vcpp_redist_versions import get_vcredist_versions # get_vcpp_redist_versions.py
from get_vulkan_version import validate_requirement as validate_vulkan # get_vulkan_version.py
from get_windows_info import get_windows_info # get_windows_info.py

# ─────────────────────────────────────────────
#  Logging setup
# ─────────────────────────────────────────────

def setup_logging(log_dir: Path) -> logging.Logger:
    """
    Configure file + console logging.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"launcher_{datetime.now():%Y%m%d_%H%M%S}.log"
    logger = logging.getLogger("RetroBatLauncher")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)-8s] %(message)s",
        datefmt="%H:%M:%S",
    )

    # File handler (always verbose)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # Console handler (only when a console is attached)
    if sys.stdout and getattr(sys.stdout, "isatty", lambda: False)():
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    logger.info("=" * 60)
    logger.info("RetroBat Launcher started")
    logger.info("=" * 60)
    logger.info(f"Log file: {log_file}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Executable: {sys.executable}")
    return logger

# ─────────────────────────────────────────────
#  Locate RetroBat executable by searching 
#  candidate directories relative to the launcher.
# ─────────────────────────────────────────────

"""
Candidates to search for the RetroBat executable, relative to the launcher location. 
Reorder as needed.
"""
RETROBAT_RELATIVE_CANDIDATES = [
    ".",
    "RetroBat",
    "..",
    "../RetroBat",
    "../../RetroBat",
]

RETROBAT_EXE_NAME = "retrobat.exe"

def get_launcher_dir() -> Path:
    """
    Return the directory that contains the launcher itself.
    Works both when running as a .py and as a PyInstaller bundle.
    """
    if getattr(sys, "frozen", False):          # PyInstaller bundle
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

def find_retrobat(base: Path, logger: logging.Logger) -> Optional[Path] | None:
    """
    Walk candidate directories relative to *base* looking for retrobat.exe.
    Returns the absolute path to the executable, or None.
    """
    logger.info(f"Searching for {RETROBAT_EXE_NAME} relative to: {base}")

    for rel in RETROBAT_RELATIVE_CANDIDATES:
        candidate = (base / rel).resolve()
        exe = candidate / RETROBAT_EXE_NAME
        logger.debug(f"  Checking: {exe}")
        if exe.is_file():
            logger.info(f"  ✓ Found: {exe}")
            return exe

    # Fallback: walk up to 4 parent levels
    current = base
    for level in range(4):
        exe = current / RETROBAT_EXE_NAME
        logger.debug(f"  Parent walk [{level}]: {exe}")
        if exe.is_file():
            logger.info(f"  ✓ Found via parent walk: {exe}")
            return exe
        parent = current.parent
        if parent == current:
            break
        current = parent

    logger.warning(f"  ✗ {RETROBAT_EXE_NAME} not found in any candidate locations.")
    return None

# ─────────────────────────────────────────────
#  Results window with summary of checks and 
#  "Start" button if all passed, or "Exit" if not.
# ─────────────────────────────────────────────

def show_results_window(results, launch_callback=None):
        root = tk.Tk()
        root.title("RetroBat System Check")
        root.geometry("520x400")

        frame = tk.Frame(root)
        frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Populate results
        all_passed = True

        for r in results:
            row = tk.Frame(scroll_frame, pady=4)
            row.pack(fill="x", padx=10)

            icon = "✅" if r["passed"] else "❌"
            if not r["passed"]:
                all_passed = False

            label = tk.Label(
                row,
                text=f"{icon} {r['name']} — {r['message']}",
                anchor="w"
            )
            label.pack(side="left", fill="x", expand=True)

            if not r["passed"] and r.get("fix"):
                btn = tk.Button(
                    row,
                    text="Fix",
                    command=r["fix"],
                    bg="#ff6b35",
                    fg="white"
                )
                btn.pack(side="right")

        # Bottom buttons
        bottom = tk.Frame(root, pady=10)
        bottom.pack()

        if all_passed and launch_callback:
            launch_callback()
            root.destroy()
        else:
            tk.Button(
                bottom,
                text="EXIT",
                width=20,
                command=root.destroy,
                bg="#ff6b35"
            ).pack()

        root.mainloop()

# ─────────────────────────────────────────────
#  Log environment info for troubleshooting 
#  (paths, etc.)
# ─────────────────────────────────────────────

def collect_environment_info(logger: logging.Logger) -> dict:
    """
    Gather and log relevant environment details.
    """
    info = {
        "cwd": Path.cwd(),
        "launcher_dir": get_launcher_dir(),
        "user_profile": os.environ.get("USERPROFILE", "N/A"),
        "program_files": os.environ.get("ProgramFiles", "N/A"),
        "program_files_x86": os.environ.get("ProgramFiles(x86)", "N/A"),
        "path_entries": os.environ.get("PATH", "").split(os.pathsep),
    }
    logger.info("Current Environment:")
    for k, v in info.items():
        if k == "path_entries":
            logger.info(f"  PATH has {len(v)} entries")
        else:
            logger.info(f"  {k}: {v}")
    return info

# ─────────────────────────────────────────────
#  Download links, unused for now.
# ─────────────────────────────────────────────

#DX_LINK = "https://www.microsoft.com/en-us/download/details.aspx?id=35"
#VC_LINK = "https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist"

# ─────────────────────────────────────────────
#  Splash screen parameters and functions.
# ─────────────────────────────────────────────

class SplashScreen:
    """
    A retro-themed splash screen rendered with tkinter.
    Closes itself after `duration_ms` or when .close() is called.

    StringVar / DoubleVar are created *after* tk.Tk() and exposed as:
        self.status_var    (tk.StringVar)
        self.progress_var  (tk.DoubleVar)
    """

    W, H = 540, 300

    # Retro palette
    BG       = "#0d0d1a"
    ACCENT   = "#ff6b35"
    ACCENT2  = "#00d4ff"
    TEXT     = "#e8e8f0"
    DIM      = "#5a5a7a"
    BAR_BG   = "#1a1a2e"
    BAR_FG   = "#ff6b35"

    def __init__(self, logger: logging.Logger = None):
        self.root = tk.Tk()
        self.root.overrideredirect(True)          # borderless
        self.root.attributes("-topmost", True)
        self.root.configure(bg=self.BG)
        self.logger = logger

        # Create variables AFTER root exists
        self.status_var   = tk.StringVar(master=self.root, value="Initialising…")
        self.progress_var = tk.DoubleVar(master=self.root, value=0.0)
        # self.version_text = None
        self.version_text = "Version 2.5.1" # Update this as needed, or change value 
                                            # to "Unknown" and read from version_info.txt
                                            # file if you want to get fancy

        # Center on screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - self.W) // 2
        y = (sh - self.H) // 2
        self.root.geometry(f"{self.W}x{self.H}+{x}+{y}")

        self._build_ui(self.status_var, self.progress_var, self.version_text)
        self._animate_scan(0)

    # ── UI construction ──────────────────────

    def _build_ui(self, status_var, progress_var, version_text):
        c = tk.Canvas(
            self.root, width=self.W, height=self.H,
            bg=self.BG, highlightthickness=0,
        )
        c.pack()
        self._canvas = c

        # Outer border
        c.create_rectangle(2, 2, self.W-2, self.H-2,
                            outline=self.ACCENT, width=2)
        # Inner border (corner-nicked)
        c.create_rectangle(8, 8, self.W-8, self.H-8,
                            outline=self.DIM, width=1)

        # Corner decorations
        for cx, cy, start in [
            (8, 8, 180), (self.W-8, 8, 270),
            (8, self.H-8, 90), (self.W-8, self.H-8, 0),
        ]:
            c.create_arc(cx-12, cy-12, cx+12, cy+12,
                         start=start, extent=90,
                         outline=self.ACCENT2, width=1, style="arc")

        # Logo / title
        c.create_text(self.W//2, 80,
                      text="⟨ RETROBAT ⟩",
                      fill=self.ACCENT, font=("Courier New", 28, "bold"))
        c.create_text(self.W//2, 112,
                      text="L  A  U  N  C  H  E  R",
                      fill=self.ACCENT2, font=("Courier New", 11))

        # Horizontal rule
        c.create_line(40, 130, self.W-40, 130, fill=self.DIM)

        # Status label — Canvas.create_text has no textvariable; use trace+itemconfigure
        self._status_item = c.create_text(self.W//2, 158,
                      text=status_var.get(),
                      fill=self.TEXT, font=("Courier New", 10),
                      anchor="center")
        status_var.trace_add("write",
            lambda *_: c.itemconfigure(self._status_item, text=status_var.get()))

        # Progress bar background
        c.create_rectangle(40, 178, self.W-40, 194,
                            fill=self.BAR_BG, outline=self.DIM)
        self._bar_rect = c.create_rectangle(
            40, 178, 40, 194,
            fill=self.BAR_FG, outline="",
        )

        # Assign self.version_text is assigned "Unknown" above to use version from 
        # ProductVersion value in version_info.txt, otherwise fallback to "Unknown"
        if version_text == "":
            pattern = re.compile(r'StringStruct\("([^"]+)",\s*"([^"]+)"\)')

            def get_stringstruct_value(file_path, key):
                remove_chars = '"\' )'
                table = str.maketrans('', '', remove_chars)

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            match = pattern.search(line)
                            if match and match.group(1) == key:
                                return match.group(2).translate(table)
                except:
                    pass

                return "Unknown"
            
            if not get_stringstruct_value("version_info.txt", "ProductVersion") == "":
                version_text = f"Version {get_stringstruct_value("version_info.txt", "ProductVersion")}"
            else:
                version_text = "Version Unknown"

        c.create_text(self.W//2, 240,
                      #text=f"v1.2  ·  {datetime.now():%Y-%m-%d}",
                      text=f"{version_text}  ·  {datetime.now():%Y-%m-%d}",
                      fill=self.DIM, font=("Courier New", 8))

        # Scanline overlay placeholder id (updated by animation)
        self._scan_id = None

        # Hook progress variable to update bar
        progress_var.trace_add("write", lambda *_: self._update_bar(progress_var.get()))

        # Button support
        self._buttons = []

    def _update_bar(self, pct: float):
        """
        Redraw progress bar to reflect 0–100 percent.
        """
        pct = max(0.0, min(1.0, pct))
        x1 = 40
        x2 = 40 + int((self.W - 80) * pct)
        self._canvas.coords(self._bar_rect, x1, 178, x2, 194)

    def _animate_scan(self, y: int):
        """
        Draw a moving scanline for retro atmosphere.
        """
        c = self._canvas
        if self._scan_id:
            c.delete(self._scan_id)
        self._scan_id = c.create_line(
            40, y, self.W-40, y,
            fill="#ffffff", stipple="gray12",
        )
        next_y = (y + 3) % self.H
        self._after_id = self.root.after(40, self._animate_scan, next_y)

    def add_button(self, text, command, x, y, width=120, height=28):
        """
        Add a button to the splash screen. Returns the button instance.
        """
        btn = tk.Button(
            self.root,
            text=text,
            command=command,
            bg=self.ACCENT,
            fg="white",
            activebackground=self.ACCENT2,
            relief="flat",
            font=("Courier New", 9, "bold")
        )
        btn.place(x=x, y=y, width=width, height=height)
        self._buttons.append(btn)
        return btn
    
    def clear_buttons(self):
        """
        Removes all buttons from the splash screen.
        """
        for b in self._buttons:
            try:
                b.destroy()
            except:
                pass
        self._buttons.clear()

    # ── Public API ───────────────────────────

    def update(self):
        self.root.update()

    def close(self):
        if self.root:
            try:
                self.root.after_cancel(self._after_id)
                self.root.destroy()
            except Exception:
                pass
            self.root = None

# ─────────────────────────────────────────────
#  Launch logic
# ─────────────────────────────────────────────

def launch_retrobat(exe: Path, logger: logging.Logger) -> int:
    cwd = exe.parent  # i.e. D:\RetroBat
    # Point home one level deeper so ES resolves .emulationstation correctly
    es_home = cwd / "emulationstation"  # i.e. D:\RetroBat\emulationstation
    if not es_home.is_dir():
        logger.warning(f"Expected ES home not found: {es_home} — falling back to {cwd}")
        es_home = cwd

    logger.info(f"Launching: {exe}")
    logger.debug(f"Working dir: {cwd}")
    logger.debug(f"EmulationStation dir: {es_home}")

    # Copy current environment and modify for EmulationStation folder.
    env = os.environ.copy()

    # Set related environment variables to the emulationstation folder
    # inside the RetroBat installation.
    env["HOME"]         = str(es_home)
    env["USERPROFILE"]  = str(es_home)
    env["HOMEDRIVE"]    = es_home.drive
    env["HOMEPATH"]     = str(es_home)[len(es_home.drive):]
    env["APPDATA"]      = str(es_home / "AppData" / "Roaming")
    env["LOCALAPPDATA"] = str(es_home / "AppData" / "Local")

    # Log the environment variables we're setting for troubleshooting.
    for k in ("HOME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "APPDATA", "LOCALAPPDATA"):
        logger.debug(f"  {k}={env[k]}")

    try:
        proc = subprocess.Popen(
        [str(exe)],
            cwd=str(cwd),   # ← still D:\RetroBat, where retrobat.exe lives
            env=env,        # ← but with HOME and related vars pointing to \RetroBat\emulationstation
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info(f"Process started (PID {proc.pid})")
        rc = proc.wait()
        logger.info(f"Process exited (rc={rc})")
        return rc

    except Exception as e:
        logger.error(f"Launch failed: {e}")
        return -1

# ─────────────────────────────────────────────
#  Main function and loading sequence with 
#  splash screen.
# ─────────────────────────────────────────────

def main():
    # ── Bootstrap paths & logging ────────────
    launcher_dir = get_launcher_dir()
    log_dir = launcher_dir / "logs"
    #log_dir = Path(os.environ.get("LOCALAPPDATA", launcher_dir)) / "RetroBatLauncher" / "logs"
    logger = setup_logging(log_dir)

    # ── Shared tkinter variables ─────────────
    # We create the Tk root inside SplashScreen; status & progress
    # need to be StringVar / DoubleVar bound to that root.
    status_var   = None
    progress_var = None
    version_text = None

    # ── Version variable - update this ───────
    #version_text = "2.5.0"

    # ── Create splash ────────────────────────
    # We need the Tk instance first to make StringVar / DoubleVar
    # Trick: create them after SplashScreen.__init__ builds root.
    splash = None

    def run_with_splash():
        nonlocal splash, status_var, progress_var, version_text

        # Build splash — Tk root is created inside __init__,
        # then StringVar/DoubleVar are created bound to that root.
        splash = SplashScreen(logger=logger)
        status_var   = splash.status_var
        progress_var = splash.progress_var
        version_text = splash.version_text

        # Drive the loading steps on the Tk main thread via after()
        splash.root.after(100, loading_sequence)
        splash.root.mainloop()

    # Initialize validation variables
    retrobat_exe = None
    #launch_error = None
    results = []

    def add_result(name, passed, message):
        results.append({
            "name": name,
            "passed": passed,
            "message": message
        })

    def loading_sequence():
        """
        Define the sequential loading steps with status updates and progress increments.
        """
        nonlocal retrobat_exe

        steps = [
            (0.05, "Initializing Launcher…"),           # step 0
            (0.10, "Detecting RetroBat Installation…"), # step 1
            (0.15, "Checking CPU Architecture…"),       # step 2
            (0.20, "Checking GPU Info…"),               # step 3
            (0.25, "Getting OS Info…"),                 # step 4
            (0.30, "Get DirectX Version…"),             # step 5
            (0.55, "Get OpenGL Version…"),              # step 6
            (0.80, "Get Vulkan Version…"),              # step 7
            (0.90, "Get VCPP Version…"),                # step 8
            (1.00, "Ready to start RetroBat…"),         # step 9
        ]

        """
        Function for looping through sequential loading steps.
        """
        def do_step(i):
            nonlocal retrobat_exe

            # If all validation steps are done, close splash screen and 
            # show results window.
            if i >= len(steps):
                splash.close()
                return

            pct, msg = steps[i]
            logger.info(f"=> Step {i+1}/{len(steps)}: {msg}")
            status_var.set(msg)
            progress_var.set(pct)

            # Step 0: Log initial environment info for troubleshooting (paths, etc.).
            if i == 0:
                collect_environment_info(logger) # returns dict of environment info

            # Step 1: Locate RetroBat executable relative to launcher
            elif i == 1:
                retrobat_exe = find_retrobat(launcher_dir, logger) # returns executable path or None
                exe_ok = True if retrobat_exe else False

                add_result(
                    "RetroBat Executable",
                    exe_ok,
                    f"Found {retrobat_exe}" if retrobat_exe else f"{RETROBAT_EXE_NAME} missing"
                )
                
            # Step 2: Check CPU architecture (64-bit required).
            elif i == 2:
                cpu = get_cpu_arch(logger) # returns array of strings

                for key, value in cpu.items():
                    logger.info(f"{key}: {value}")
                cpu_is_64bit = cpu.get("Hardware Arch") in ['AMD64', 'x86_64']

                add_result(
                    "CPU Architecture",
                    cpu_is_64bit,
                    "64-bit CPU detected" if cpu_is_64bit else "64-bit CPU REQUIRED"
                )

            # Step 3: Check GPU info for troubleshooting and logging.
            elif i == 3:
                logger.info(f"Detected Hardware: {', '.join(get_gpu_info())}") # returns GPU info strings

            # Step 4: Check Windows version and architecture details for minimum version.
            elif i == 4:
                # We log all the Windows version details we can get for troubleshooting, but for 
                # validation we check if it's Windows 10 or 11 and 64-bit.
                win_info = get_windows_info(logger)

                for key, value in win_info.items():
                    logger.info(f"{key}: {value}")

                os_release = str(win_info.get("OS Release", "")).strip()
                arch = str(win_info.get("OS Architecture", "")).strip()
                # Normalize architecture
                is_64bit = arch in ("AMD64", "X86_64", "ARM64", "AARCH64", "64-BIT")

                win_ok = (
                    ("10" in os_release or "11" in os_release)
                    and is_64bit
                )
                
                add_result(
                    "Windows Version",
                    win_ok,
                    "Compatible Windows version 10+ detected" if win_ok else "Incompatible Windows version"
                )

            # Step 5: Check DirectX for minimum version.
            elif i == 5:
                # Check for Direct3D 11.1 feature level (fallback to dxdiag version string if feature 
                # level check fails)
                min_feature_level = 11 #"0xb000"
                dx_ok = validate_directx(min_feature_level, logger) # returns boolean

                add_result(
                    "DirectX Version",
                    dx_ok,
                    "Compatible DirectX version 11.1 detected" if dx_ok else "Incompatible DirectX version"
                )
            
            # Step 6: Check OpenGL for minimum version.
            elif i == 6:
                # Check for OpenGL 4.4
                gl_ok = validate_opengl(4, 4, logger) # returns boolean

                add_result(
                    "OpenGL Version",
                    gl_ok,
                    "Compatible OpenGL version 4.4 detected" if gl_ok else "Incompatible OpenGL version"
                )

            # Step 7: Check Vulkan for minimum version.
            elif i == 7:
                # Check for Vulkan 1.2
                vk_ok = validate_vulkan(1, 2, logger) # returns boolean

                add_result(
                    "Vulkan",
                    vk_ok,
                    "Vulkan 1.2 detected" if vk_ok else "Vulkan 1.2 REQUIRED"
                )

            # Step 8: Check Visual C++ Redistributable for 2010/2015-2019 installations.
            elif i == 8:
                def check_vcredist_detailed():
                    required = {
                        "VC++ 2010": False,
                        "VC++ 2015-2022": False
                    }

                    try:
                        redists = get_vcredist_versions() # returns array of dicts for valid redistributables

                        # Log the list of detected Visual C++ Redistributables for troubleshooting.
                        logger.info(f"{'Installed Redistributable':<60} | {'Version'}")
                        logger.info("-" * 80)
                        for r in sorted(redists, key=lambda x: x['Name']):
                            logger.info(f"{r['Name']:<60} | {r['Version']}")

                        for r in redists:
                            name = r.get("Name", "")

                            if "2010" in name:
                                required["VC++ 2010"] = True

                            #if any(v in name for v in ["2015", "2017", "2019", "2022"]):
                            if "2015-2022" in name:
                                required["VC++ 2015-2022"] = True

                    except Exception:
                        pass

                    return required
                
                vcredist_status = check_vcredist_detailed() # returns dict of required redistributables

                add_result(
                    "VC++ 2010",
                    vcredist_status["VC++ 2010"],
                    "Installed" if vcredist_status["VC++ 2010"] else "Missing"
                )
                logger.error("✓ Pass: VC++ 2010 installed" if vcredist_status["VC++ 2010"] \
                             else "❌ Fail: VC++ 2010 missing")

                add_result(
                    "VC++ 2015-2022",
                    vcredist_status["VC++ 2015-2022"],
                    "Installed" if vcredist_status["VC++ 2015-2022"] else "Missing"
                )
                logger.error("✓ Pass: VC++ 2015-2022 installed" if vcredist_status["VC++ 2015-2022"] \
                             else "❌ Fail: VC++ 2015-2022 missing")

            """
            Increment the do_step integer to proceed to the next step with a delay between 
            each to show progress until the end of the array is reached.
            """
            splash.root.after(350, do_step, i + 1)

        """
        Start the loading sequence with the first step.
        """
        do_step(0) # Start with the first step (index 0)

    # Run splash on main thread
    run_with_splash()

    # ── After splash closes ──────────────────

    # Create the show_results_window, which will stay open if any check fails 
    # and add an exit button. Otherwise it will callback launch(), close the results 
    # window and Retrobat will immediately launch.
    def launch():
        rc = launch_retrobat(retrobat_exe, logger)
        sys.exit(rc)

    show_results_window(results, launch_callback=launch)
    sys.exit()

if __name__ == "__main__":
    main()
