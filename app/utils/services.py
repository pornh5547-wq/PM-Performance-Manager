import json
from app.utils._pwsh import run, run_admin

SAFE_SERVICES = {
    "XboxGipSvc": "Safe", "XblAuthManager": "Safe", "XblGameSave": "Safe",
    "XboxNetApiSvc": "Safe", "DiagTrack": "Safe", "dmwappushservice": "Safe",
    "WSearch": "Safe", "SysMain": "Safe", "MapsBroker": "Safe",
    "lfsvc": "Safe", "BthAvctpSvc": "Safe", "SessionEnv": "Safe",
    "SharedRealtorSvc": "Safe", "WMPNetworkSvc": "Safe", "stisvc": "Safe",
    "wisvc": "Safe", "WpnService": "Safe", "WpnUserService": "Safe",
    "TabletInputService": "Safe", "RetailDemo": "Safe", "MessagingService": "Safe",
    "PcaSvc": "Safe", "wcncsvc": "Safe", "PhoneSvc": "Safe",
    "PrintNotify": "Safe", "WlanSvc": "Safe",
}

def list_services():
    cmd = 'Get-Service | Select-Object Name, DisplayName, Status, StartType, CanStop, CanPauseAndContinue | ConvertTo-Json'
    result = run(cmd)
    if result and result.stdout.strip():
        try:
            services = json.loads(result.stdout)
            if isinstance(services, dict):
                services = [services]
            for s in services:
                name = s.get("Name", "")
                s["Safety"] = SAFE_SERVICES.get(name, "Unknown")
            return services
        except:
            pass
    return []

def stop_service(name):
    r = run_admin(f'Stop-Service {name} -Force')
    return r is not None and r.returncode == 0

def start_service(name):
    r = run_admin(f'Start-Service {name}')
    return r is not None and r.returncode == 0

def set_startup_type(name, startup_type):
    r = run_admin(f'Set-Service {name} -StartupType {startup_type}')
    return r is not None and r.returncode == 0

def disable_service(name):
    r = run_admin(f'Set-Service {name} -StartupType Disabled; Stop-Service {name} -Force')
    return r is not None and r.returncode == 0

def enable_service(name):
    r = run_admin(f'Set-Service {name} -StartupType Manual')
    return r is not None and r.returncode == 0
