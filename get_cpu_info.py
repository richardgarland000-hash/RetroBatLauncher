"""
CPU Architecture Detection - imported by launcher.py.
get_cpu_info.py Version: 2.5.3

This module retrieves basic information about the system's processor
architecture and the Python interpreter being used. It determines whether
the system is running on a supported 64-bit CPU and logs the results.

The module provides functions to:

    • Detect the hardware CPU architecture.
    • Determine whether the Python interpreter is 32-bit or 64-bit.
    • Retrieve the processor identifier reported by the operating system.
    • Validate that the system is running on a supported 64-bit
      architecture.
    • Log the detection results using a supplied logger.

This is intended for use during application startup to verify that the
system meets the minimum processor architecture requirements before
launching the application.
"""

import platform
import logging

def get_cpu_arch(logger: logging.Logger):
    # Returns the actual hardware architecture
    machine = platform.machine()
    
    # Returns the architecture the Python interpreter was built for
    # (e.g., '32bit' or '64bit')
    python_bits = platform.architecture()[0]

    if machine in ['AMD64', 'x86_64']:
        logger.info("  ✓ Pass: 64-bit CPU architecture detected.")
    else:
        logger.error(f"  ✗ Fail: Unsupported CPU architecture detected: {machine}")
    
    return {
        "Hardware Arch": machine,
        "Python Bitness": python_bits,
        "Processor": platform.processor()
    }
