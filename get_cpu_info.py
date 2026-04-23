import platform
import logging

def get_cpu_arch(logger: logging.Logger):
    # Returns the actual hardware architecture
    machine = platform.machine()
    
    # Returns the architecture the Python interpreter was built for
    # (e.g., '32bit' or '64bit')
    python_bits = platform.architecture()[0]

    if machine in ['AMD64', 'x86_64']:
        logger.info("✓ Pass: 64-bit CPU architecture detected.")
    else:
        logger.error(f"❌ Fail: Unsupported CPU architecture detected: {machine}")
    
    return {
        "Hardware Arch": machine,
        "Python Bitness": python_bits,
        "Processor": platform.processor()
    }
