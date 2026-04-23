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
