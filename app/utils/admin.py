import subprocess
import sys
import os
from app.utils._pwsh import run, run_admin

def run_dism_command(command):
    return run_admin(f'DISM /Online /Cleanup-Image /{command} /NoRestart')

def run_sfc_command():
    return run_admin('sfc /scannow')

def run_chkdsk_command(drive='C:'):
    return run_admin(f'chkdsk {drive} /f /r')

def run_ipconfig_command(args=''):
    return run(f'ipconfig {args}')

def create_restore_point(description='PM Performance Manager - Before Optimization'):
    cmd = f'Checkpoint-Computer -Description "{description}" -RestorePointType MODIFY_SETTINGS'
    return run_admin(cmd)

def enable_gaming_mode():
    cmd = '''
    $powerScheme = Get-WmiObject -Namespace root\\cimv2\\power -Class Win32_PowerPlan | Where-Object {$_.ElementName -like "*High performance*"}
    if ($powerScheme) { $powerScheme.Activate() }
    Powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    '''
    return run_admin(cmd)

def disable_gaming_mode():
    return run_admin('Powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e')

def disable_windows_updates():
    return run_admin('sc config wuauserv start=disabled; sc stop wuauserv')

def enable_windows_updates():
    return run_admin('sc config wuauserv start=auto; sc start wuauserv')

def set_high_performance_power_plan():
    return run_admin('powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c')

def clear_dns_cache():
    return run_admin('ipconfig /flushdns')

def reset_winsock():
    return run_admin('netsh winsock reset')

def reset_ip_stack():
    return run_admin('netsh int ip reset')

def get_windows_health():
    health = {"dism_health": "Unknown", "sfc_status": "Unknown"}
    result = run('DISM /Online /Cleanup-Image /CheckHealth')
    if result and result.stdout:
        if "No component store corruption detected" in result.stdout:
            health["dism_health"] = "Healthy"
        elif "repairable" in result.stdout.lower():
            health["dism_health"] = "Repairable"
        else:
            health["dism_health"] = "Issues Found"
    result2 = run('sfc /verifyonly')
    if result2 and result2.stdout:
        if "did not find any integrity violations" in result2.stdout:
            health["sfc_status"] = "Healthy"
        else:
            health["sfc_status"] = "Corruption Found"
    return health
