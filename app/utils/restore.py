import json
from app.utils._pwsh import run_admin
from app.config import log

def create_restore_point(description="PM Performance Manager - System Optimization"):
    try:
        result = run_admin(f'Checkpoint-Computer -Description "{description}" -RestorePointType MODIFY_SETTINGS')
        success = result is not None and result.returncode == 0
        log(f"Restore point created: {description} - {'Success' if success else 'Failed'}")
        return {"success": success, "output": result.stdout if result else "Failed"}
    except Exception as e:
        log(f"Restore point creation error: {str(e)}")
        return {"success": False, "output": str(e)}

def list_restore_points():
    result = run_admin('Get-ComputerRestorePoint | Select-Object SequenceNumber, Description, CreationTime, EventType | ConvertTo-Json')
    if result and result.stdout.strip():
        try:
            points = json.loads(result.stdout)
            if not isinstance(points, list):
                points = [points]
            return points
        except:
            pass
    return []

def restore_system(sequence_number):
    result = run_admin(f'Restore-Computer -RestorePoint {sequence_number}')
    return {"success": result is not None, "output": result.stdout if result else "Failed"}

def enable_system_restore(drive='C:'):
    result = run_admin(f'Enable-ComputerRestore -Drive "{drive}"')
    return {"success": result is not None}
