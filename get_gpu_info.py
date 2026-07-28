"""
Graphics Processing Unit (GPU) Detection - imported by launcher.py.
get_gpu_info.py Version: 2.5.3

This module retrieves the names of the graphics processing units (GPUs)
installed in the system. It uses operating system-specific methods to
query the graphics hardware and returns a list of detected GPU names.

The module provides functions to:

    • Detect installed GPU hardware on Windows, Linux, and macOS.
    • Retrieve the display name of each detected graphics adapter.
    • Return a fallback value if GPU detection is unsuccessful.

Platform-specific detection methods include:

    • Windows: Windows Management Instrumentation (WMI).
    • Linux: The lspci command.
    • macOS: The system_profiler utility.

This is intended for use during application startup to identify the
system's graphics hardware for logging, diagnostics, or compatibility
verification.
"""

import platform
import wmi
import subprocess

def get_gpu_info():
    """Retrieves basic GPU hardware name."""
    system = platform.system()
    try:
        if system == "Windows":
            # Requires 'wmi' library: pip install wmi
            #import wmi
            c = wmi.WMI()
            return [gpu.Name for gpu in c.Win32_VideoController()]
        elif system == "Linux":
            result = subprocess.run(["lspci"], capture_output=True, text=True)
            return [line.split(':')[-1].strip() for line in result.stdout.splitlines() if "VGA" in line]
        elif system == "Darwin":
            result = subprocess.run(["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True)
            return [line.strip() for line in result.stdout.splitlines() if "Chipset Model" in line]
    except Exception:
        return ["⚠ Unknown GPU"]
