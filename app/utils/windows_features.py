import json
from app.utils._pwsh import run, run_admin

def list_features():
    cmd = 'Get-WindowsOptionalFeature -Online | Select-Object FeatureName, DisplayName, State, Description | ConvertTo-Json'
    result = run(cmd)
    features = []
    if result and result.stdout.strip():
        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            features = data
        except:
            pass
    features.sort(key=lambda x: x.get("DisplayName", "") or "")
    return features

def enable_feature(name):
    r = run_admin(f'Enable-WindowsOptionalFeature -Online -FeatureName "{name}" -All -NoRestart')
    return r is not None and r.returncode == 0

def disable_feature(name):
    r = run_admin(f'Disable-WindowsOptionalFeature -Online -FeatureName "{name}" -NoRestart')
    return r is not None and r.returncode == 0

COMMON_FEATURES = [
    ("Microsoft-Hyper-V", "Hyper-V"),
    ("VirtualMachinePlatform", "Virtual Machine Platform"),
    ("Microsoft-Windows-Subsystem-Linux", "Windows Subsystem for Linux"),
    ("NetFx3", ".NET Framework 3.5"),
    ("NetFx4-AdvSrvs", ".NET Framework 4.8 Advanced Services"),
    ("Containers-DisposableClientVM", "Windows Sandbox"),
    ("Microsoft-Windows-Holographic", "Windows Mixed Reality"),
    ("Printing-XPSServices-Features", "XPS Services"),
    ("TelnetClient", "Telnet Client"),
    ("TFTP", "TFTP Client"),
    ("SMB1Protocol", "SMB 1.0/CIFS File Sharing"),
    ("Internet-Explorer-Optional-amd64", "Internet Explorer 11"),
    ("WorkFolders-Client", "Work Folders Client"),
    ("MediaPlayback", "Media Features (Windows Media Player)"),
    ("Windows-Defender-ApplicationGuard", "Windows Defender Application Guard"),
    ("SmbDirect", "SMB Direct"),
]
