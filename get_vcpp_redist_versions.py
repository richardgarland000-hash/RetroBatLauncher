"""
Microsoft Visual C++ Redistributable Detection - imported by launcher.py.
get_vcpp_redist_versions.py Version: 2.5.3

This module scans the Windows Registry to identify installed Microsoft
Visual C++ Redistributable packages. It searches the standard uninstall
registry locations for both 64-bit and 32-bit applications and returns
information about each detected redistributable.

The module provides functions to:

    • Search the Windows Registry for installed Microsoft Visual C++
      Redistributables.
    • Retrieve the display name and installed version of each package.
    • Detect both native 64-bit and WOW6432Node (32-bit) installations.

The returned information can be used to verify that the required Visual C++
runtime libraries are installed before launching an application that
depends on them.
"""

import winreg

def get_vcredist_versions():
    """
    Scans the Windows Registry for installed Visual C++ Redistributables.
    Returns a list of dictionaries with Name, Version, and Architecture.
    """
    vcredist_list = []
    
    # Common registry paths for installed software
    paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for path in paths:
        try:
            # Open the parent key
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            
            # Iterate through all subkeys (each represents an installed program)
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                try:
                    subkey_name = winreg.EnumKey(reg_key, i)
                    subkey = winreg.OpenKey(reg_key, subkey_name)
                    
                    # Get the display name and version
                    display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    
                    # Filter for Visual C++ Redistributables
                    if "Microsoft Visual C++" in display_name and "Redistributable" in display_name:
                        display_version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                        vcredist_list.append({
                            "Name": display_name,
                            "Version": display_version
                        })
                    winreg.CloseKey(subkey)
                except (OSError, FileNotFoundError):
                    continue
            winreg.CloseKey(reg_key)
        except OSError:
            continue

    return vcredist_list
