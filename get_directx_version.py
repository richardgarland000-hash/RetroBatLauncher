import ctypes
import subprocess
import os
import platform
import xml.etree.ElementTree as ET
import tempfile
import logging
import json
from pathlib import Path

CACHE_FILE = Path("dx_cache.json")

# ─────────────────────────────────────────────
# Fast: Direct3D Feature Level Detection
# ─────────────────────────────────────────────

def get_directx_feature_level():
    try:
        d3d11 = ctypes.windll.d3d11

        levels = (ctypes.c_uint * 6)(
            0xb000,  # 11_0
            0xa100,  # 10_1
            0xa000,  # 10_0
            0x9300,  # 9_3
            0x9200,  # 9_2
            0x9100   # 9_1
        )

        device = ctypes.c_void_p()
        context = ctypes.c_void_p()
        feature_level = ctypes.c_uint()

        result = d3d11.D3D11CreateDevice(
            None,
            1,  # Hardware driver
            None,
            0,
            levels,
            len(levels),
            7,
            ctypes.byref(device),
            ctypes.byref(feature_level),
            ctypes.byref(context)
        )

        if result != 0:
            return None, f"D3D11CreateDevice failed: {result}"

        return feature_level.value, None

    except Exception as e:
        return None, str(e)

# ─────────────────────────────────────────────
# Slow fallback: dxdiag
# ─────────────────────────────────────────────

def get_directx_version_dxdiag():
    temp_file = os.path.join(tempfile.gettempdir(), "dxdiag_cache.xml")

    try:
        subprocess.run(
            ["dxdiag", "/x", temp_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if not os.path.exists(temp_file):
            return None, "dxdiag output missing"

        tree = ET.parse(temp_file)
        root = tree.getroot()

        version_node = root.find(".//DirectXVersion")
        if version_node is not None:
            return version_node.text, None

        return None, "DirectX version not found"

    except Exception as e:
        return None, str(e)

# ─────────────────────────────────────────────
# Cache helpers
# ─────────────────────────────────────────────

def load_cache():
    try:
        if CACHE_FILE.exists():
            return json.loads(CACHE_FILE.read_text())
    except:
        pass
    return None

def save_cache(data):
    try:
        CACHE_FILE.write_text(json.dumps(data))
    except:
        pass

# ─────────────────────────────────────────────
# Unified DirectX Detection
# ─────────────────────────────────────────────

def get_directx_version():
    if platform.system() != "Windows":
        return None, f"DirectX not supported on {platform.system()}"

    # 1. Cache (fastest)
    cached = load_cache()
    if cached:
        return cached, None

    # 2. Feature level (fast + accurate)
    level, err = get_directx_feature_level()
    if level:
        result = {"type": "feature_level", "value": level}
        save_cache(result)
        return result, None

    # 3. Fallback to dxdiag (slow)
    version, err = get_directx_version_dxdiag()
    if version:
        result = {"type": "dxdiag", "value": version}
        save_cache(result)
        return result, None

    return None, err

# ─────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────

def validate_directx(min_feature_level, logger: logging.Logger):
    """
    Example:
        min_feature_level = 0xb000  # DirectX 11
    """
    result, error = get_directx_version()

    if error or not result:
        logger.error(f"⚠ {error or 'Unknown error'}")
        return False

    if result["type"] == "feature_level":
        level = result["value"]
        logger.info(f"Detected Direct3D Feature Level: {hex(level)}")

        if level >= min_feature_level:
            logger.info(f"  ✓ Pass: {hex(level)} >= {hex(min_feature_level)}")
            return True

        logger.error(f"  ✗ Fail: {hex(level)} < {hex(min_feature_level)}")
        return False

    else:
        # dxdiag fallback parsing
        version_str = result["value"]
        logger.info(f"Detected: {version_str}")

        try:
            current_ver = int(version_str.split()[-1].split('.')[0])
            if current_ver >= 11:  # assume minimum
                logger.info("  ✓ Pass (dxdiag fallback)")
                return True
        except:
            pass

        logger.error("  ✗ Fail: insufficient DirectX version")
        return False