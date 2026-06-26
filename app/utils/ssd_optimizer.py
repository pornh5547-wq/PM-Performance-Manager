import json
from app.utils._pwsh import run, run_admin
from app.config import log

class SSDOptimizer:
    @staticmethod
    def check_trim_status():
        result = run('fsutil behavior query DisableDeleteNotify')
        if result:
            if "DisableDeleteNotify = 0" in result.stdout:
                return {"trim_enabled": True}
            elif "DisableDeleteNotify = 1" in result.stdout:
                return {"trim_enabled": False}
        return {"trim_enabled": None}

    @staticmethod
    def enable_trim():
        result = run_admin('fsutil behavior set DisableDeleteNotify 0')
        ok = result is not None and result.returncode == 0
        log(f"TRIM enabled: {ok}")
        return {"success": ok}

    @staticmethod
    def optimize_all_drives():
        result = run_admin('Optimize-Volume -DriveLetter * -ReTrim -Verbose')
        ok = result is not None and result.returncode == 0
        log(f"All drives optimized: {ok}")
        return {"success": ok, "output": result.stdout if result else ""}

    @staticmethod
    def get_drive_info(drive='C:'):
        result = run(f'Get-PhysicalDisk | Where-Object DeviceId -eq (Get-Partition -DriveLetter {drive} | Get-Disk).Number | Select-Object * | ConvertTo-Json')
        if result and result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except:
                pass
        return {}

    @staticmethod
    def disable_sysmain():
        result = run_admin('Stop-Service SysMain -Force; Set-Service SysMain -StartupType Disabled')
        ok = result is not None and result.returncode == 0
        log(f"SysMain (Superfetch) disabled: {ok}")
        return {"success": ok}

    @staticmethod
    def run_full_optimization():
        trim = SSDOptimizer.check_trim_status()
        optimize = SSDOptimizer.optimize_all_drives()
        sysmain = SSDOptimizer.disable_sysmain()
        if not trim.get("trim_enabled", False):
            SSDOptimizer.enable_trim()
        log("Full SSD optimization completed")
        return {"trim": trim, "optimize": optimize, "sysmain": sysmain}
