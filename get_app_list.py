"""
Installed Applications Detection - imported by launcher.py.
get_cpu_info.py Version: 2.6.5.1

Get installed Windows applications and their versions
    from the Windows Uninstall registry keys.

    Returns:
        list: Sorted list of dictionaries containing:
              - name
              - version
"""

import winreg

def get_installed_programs():
    # Paths to the Windows Uninstall registry keys
    registry_paths = [
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            winreg.KEY_WOW64_64KEY
        ),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            winreg.KEY_WOW64_32KEY
        ),
        (
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            0
        )
    ]

    programs = {}

    for hive, path, flag in registry_paths:
        try:
            # Open the registry key
            key = winreg.OpenKey(
                hive,
                path,
                0,
                winreg.KEY_READ | flag
            )

            # Count the number of subkeys
            num_subkeys = winreg.QueryInfoKey(key)[0]

            for i in range(num_subkeys):
                try:
                    # Get the name of each subkey
                    subkey_name = winreg.EnumKey(key, i)

                    subkey = winreg.OpenKey(key, subkey_name)

                    try:
                        # Get application name
                        display_name, _ = winreg.QueryValueEx(
                            subkey,
                            "DisplayName"
                        )

                        if not display_name:
                            continue

                        # Get application version
                        try:
                            display_version, _ = winreg.QueryValueEx(
                                subkey,
                                "DisplayVersion"
                            )
                        except OSError:
                            display_version = "Unknown"

                        # Store name and version
                        programs[display_name] = display_version

                    finally:
                        subkey.Close()

                except OSError:
                    # Skip entries that cannot be read
                    continue

            key.Close()

        except OSError:
            continue

    # Return sorted list
    return [
        {
            "name": name,
            "version": version
        }
        for name, version in sorted(
            programs.items(),
            key=lambda item: item[0].lower()
        )
    ]
