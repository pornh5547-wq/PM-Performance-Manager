import os
import json
from app.utils._pwsh import run as _run_pwsh

class StartupManager:
    def get_startup_items(self):
        items = []
        result = _run_pwsh('Get-CimInstance -ClassName Win32_StartupCommand | Select-Object Name, Command, Location, User | ConvertTo-Json', timeout=15)
        if result and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                if not isinstance(data, list):
                    data = [data]
                for item in data:
                    items.append({
                        "name": item.get("Name", "Unknown"),
                        "command": item.get("Command", ""),
                        "location": item.get("Location", ""),
                        "user": item.get("User", ""),
                    })
            except:
                pass
        registry_paths = [
            ("HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "HKLM"),
            ("HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", "HKCU"),
            ("HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Run", "HKLM (32-bit)"),
        ]
        for reg_path, source in registry_paths:
            result = _run_pwsh(f'Get-ItemProperty -Path "{reg_path}" | Select-Object * | ConvertTo-Json', timeout=10)
            if result and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if key.startswith("PS") or key == "":
                                continue
                            if key == key.upper() or "(" in key:
                                continue
                            if not any(i["name"] == key for i in items):
                                items.append({
                                    "name": key,
                                    "command": str(value),
                                    "location": reg_path,
                                    "user": source,
                                })
                except:
                    pass
        items.sort(key=lambda x: x["name"].lower())
        return items

    def disable_startup_item(self, name, location):
        try:
            if "HKLM" in location:
                path = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
            elif "HKCU" in location:
                path = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
            else:
                path = location
            result = _run_pwsh(f'Remove-ItemProperty -Path "{path}" -Name "{name}" -ErrorAction SilentlyContinue')
            return result is not None and result.returncode == 0
        except:
            return False

    def enable_startup_item(self, name, command, location):
        try:
            if "HKLM" in location:
                path = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
            elif "HKCU" in location:
                path = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
            else:
                path = location
            result = _run_pwsh(f'Set-ItemProperty -Path "{path}" -Name "{name}" -Value "{command}"')
            return result is not None and result.returncode == 0
        except:
            return False
