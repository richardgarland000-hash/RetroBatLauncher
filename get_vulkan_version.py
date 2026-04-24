import ctypes
from ctypes import util
import logging

def get_vulkan_version():
    """
    Dynamically finds the Vulkan loader and extracts the version.
    Returns (tuple, error_string). Tuple is (major, minor, patch).
    """
    # 1. Search for the library based on common OS naming conventions
    lib_names = ['vulkan-1', 'vulkan', 'libvulkan.so.1', 'libvulkan.1.dylib']
    lib_path = None
    for name in lib_names:
        lib_path = util.find_library(name)
        if lib_path:
            break
    
    if not lib_path:
        return None, "Vulkan Loader not found. Ensure Vulkan drivers are installed."

    try:
        # 2. Load the library
        vk_lib = ctypes.CDLL(lib_path)
        
        # 3. Check for vkEnumerateInstanceVersion (introduced in Vulkan 1.1)
        if hasattr(vk_lib, 'vkEnumerateInstanceVersion'):
            vk_version = ctypes.c_uint32()
            # Success code in Vulkan is 0 (VK_SUCCESS)
            if vk_lib.vkEnumerateInstanceVersion(ctypes.byref(vk_version)) == 0:
                v = vk_version.value
                # Standard Vulkan bit-masking for version parts
                major = v >> 22
                minor = (v >> 12) & 0x3FF
                patch = v & 0xFFF
                return (major, minor, patch), None
        
        # 4. Fallback: If function doesn't exist, it's a 1.0 loader
        return (1, 0, 0), None

    except Exception as e:
        return None, f"⚠ Failed to communicate with Vulkan library: {str(e)}"

def validate_requirement(min_major, min_minor, logger: logging.Logger):
    """Prints status and returns True/False based on requirements."""
    version, error = get_vulkan_version()

    if error:
        logger.error(f"⚠ Validation Failed: {error}")
        return False

    major, minor, patch = version
    logger.info(f"Detected Vulkan {major}.{minor}.{patch}")

    # Logic check: (Major > Required) OR (Major == Required AND Minor >= Required)
    if (major > min_major) or (major == min_major and minor >= min_minor):
        logger.info(f"  ✓ Pass: Minimum {min_major}.{min_minor} is met.")

        return True
    
    logger.error(f"  ✗ Fail: Version {major}.{minor} is below required {min_major}.{min_minor}.")
    return False
