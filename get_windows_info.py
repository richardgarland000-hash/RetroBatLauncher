import platform
import sys
import logging

def get_windows_info(logger: logging.Logger):
    info = {}
    
    # 1. Check if we are actually on Windows
    if platform.system() != "Windows":
        return {"error": f"Detected {platform.system()}, not Windows."}

    # 2. Get OS Version Details
    # platform.win32_ver() returns (release, version, csd, ptype)
    release, version, csd, ptype = platform.win32_ver()
    #logger.debug(f"platform.win32_ver() returned: release={release}, version={version}, csd={csd}, ptype={ptype}")
    info['OS Release'] = release  # e.g., "10" or "11"
    info['OS Version'] = version  # e.g., "10.0.22631"

     # sys.getwindowsversion() provides build-level details
    win_ver = sys.getwindowsversion()
    info['Build Number'] = win_ver.build

    # 3. Get Architecture (Accurate OS check)
    # platform.machine() is more reliable than platform.architecture() 
    # as the latter may return '32bit' if running 32-bit Python on 64-bit OS.
    info['OS Architecture'] = platform.machine() # e.g., 'AMD64' (64-bit) or 'x86' (32-bit)
    
    # 4. Get Python Interpreter Architecture
    # Useful for debugging compatibility issues
    info['Python Arch'] = "64-bit" if sys.maxsize > 2**32 else "32-bit"

    if (int(release) >= 10):
        logger.info(f"✓ Pass: Minimum Windows 10 is met.")
    else:
        logger.error(f"❌ Fail: Minimum Windows 10 is not met. Detected: {release}")
    
    if (platform.machine() == "AMD64"):
        logger.info(f"✓ Pass: 64-bit architecture is met.")
    else:
        logger.error(f"❌ Fail: 64-bit architecture is not met. Detected: {platform.machine()}")

    return info
