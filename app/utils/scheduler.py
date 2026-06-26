import threading
import time
import schedule
from datetime import datetime
from app.config import Config, log
from app.utils.cleanup import run_full_cleanup
from app.utils._pwsh import run_admin

class MaintenanceScheduler:
    def __init__(self, config: Config):
        self.config = config
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        log("Maintenance scheduler started")

    def stop(self):
        self.running = False
        log("Maintenance scheduler stopped")

    def _run_loop(self):
        interval = self.config.get("maintenance_interval_hours", 24)
        schedule.every(interval).hours.do(self._run_maintenance)
        while self.running:
            schedule.run_pending()
            time.sleep(60)

    def _run_maintenance(self):
        log("Running scheduled maintenance...")
        try:
            run_full_cleanup()
        except Exception as e:
            log(f"Scheduled cleanup error: {str(e)}")
        try:
            run_admin('DISM /Online /Cleanup-Image /ScanHealth')
        except Exception as e:
            log(f"Scheduled DISM error: {str(e)}")
        try:
            run_admin('sfc /scannow')
        except Exception as e:
            log(f"Scheduled SFC error: {str(e)}")
        self.config.set("last_maintenance", datetime.now().isoformat())
        log("Scheduled maintenance completed")

    def run_once(self):
        threading.Thread(target=self._run_maintenance, daemon=True).start()

    def get_status(self):
        last = self.config.get("last_maintenance")
        return {
            "running": self.running,
            "interval_hours": self.config.get("maintenance_interval_hours", 24),
            "last_maintenance": last,
            "next_maintenance": None,
        }
