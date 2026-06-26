import subprocess
from app.utils._pwsh import run, run_admin

SI = subprocess.STARTUPINFO()
SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW
SI.wShowWindow = subprocess.SW_HIDE
NO_WINDOW = subprocess.CREATE_NO_WINDOW

def get_visual_status():
    status = {}
    try:
        r = run('(Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name TaskbarAnimations -ErrorAction SilentlyContinue).TaskbarAnimations')
        if r and r.stdout.strip():
            status["animations"] = r.stdout.strip() == "1"
        else:
            status["animations"] = None
    except:
        status["animations"] = None
    try:
        r = run_admin('(Get-ItemProperty -Path "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI\\BootAnimation" -Name DisableStartupSound -ErrorAction SilentlyContinue).DisableStartupSound')
        if r and r.stdout.strip():
            status["startup_sound"] = r.stdout.strip() != "1"
        else:
            status["startup_sound"] = None
    except:
        status["startup_sound"] = None
    try:
        r = run('(Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name EnableTransparency -ErrorAction SilentlyContinue).EnableTransparency')
        if r and r.stdout.strip():
            status["transparency"] = r.stdout.strip() == "1"
        else:
            status["transparency"] = None
    except:
        status["transparency"] = None
    return status

def toggle_animations(enable):
    val = "1" if enable else "0"
    r = run(f'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name TaskbarAnimations -Value {val}')
    return r is not None and r.returncode == 0

def toggle_startup_sound(enable):
    if enable:
        cmd = 'Remove-ItemProperty -Path "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI\\BootAnimation" -Name DisableStartupSound -ErrorAction SilentlyContinue'
    else:
        cmd = 'New-ItemProperty -Path "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Authentication\\LogonUI\\BootAnimation" -Name DisableStartupSound -Value 1 -PropertyType DWord -Force'
    r = run_admin(cmd)
    return r is not None and r.returncode == 0

def toggle_transparency(enable):
    val = "1" if enable else "0"
    r = run(f'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name EnableTransparency -Value {val}')
    return r is not None and r.returncode == 0

def toggle_performance_mode(max_performance):
    if max_performance:
        cmd = 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Name VisualFXSetting -Value 2'
    else:
        cmd = 'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" -Name VisualFXSetting -Value 1'
    r = run(cmd)
    return r is not None and r.returncode == 0
