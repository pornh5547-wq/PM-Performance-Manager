import os
import json
import subprocess
from datetime import datetime
from app.utils._pwsh import run

SI = subprocess.STARTUPINFO()
SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW
SI.wShowWindow = subprocess.SW_HIDE
NO_WINDOW = subprocess.CREATE_NO_WINDOW

BATTERY_REPORT_DIR = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'PMPerformanceManager')

def generate_battery_report():
    os.makedirs(BATTERY_REPORT_DIR, exist_ok=True)
    path = os.path.join(BATTERY_REPORT_DIR, 'battery-report.html')
    try:
        subprocess.run(['powercfg', '/batteryreport', '/output', path],
                       capture_output=True, timeout=30,
                       startupinfo=SI, creationflags=NO_WINDOW)
        if os.path.exists(path):
            return {"success": True, "path": path}
    except:
        pass
    return {"success": False}

def get_battery_info():
    cmd = 'Get-WmiObject Win32_Battery | Select-Object Name, EstimatedChargeRemaining, EstimatedRunTime, BatteryStatus, Chemistry, DesignCapacity, FullChargeCapacity, DesignVoltage | ConvertTo-Json'
    result = run(cmd)
    battery = {}
    if result and result.stdout.strip():
        try:
            data = json.loads(result.stdout)
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            battery = data
        except:
            pass
    return battery

def get_power_scheme():
    result = run('powercfg /getactivescheme')
    if result and result.stdout:
        text = result.stdout.strip()
        if "High performance" in text or "8c5e7fda" in text:
            return "High Performance"
        elif "Balanced" in text or "381b4222" in text:
            return "Balanced"
        elif "Power saver" in text:
            return "Power Saver"
    return "Unknown"

def get_battery_history():
    try:
        path = os.path.join(BATTERY_REPORT_DIR, 'battery-report.html')
        if os.path.exists(path):
            return {"report_path": path, "exists": True}
    except:
        pass
    return {"exists": False}
