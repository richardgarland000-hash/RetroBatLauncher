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
        return ["Unknown GPU"]
