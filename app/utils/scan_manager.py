import threading
import time
from app.monitors.system_monitor import SystemMonitor

class ScanManager:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.cache = {}
        self.running = False
        self._callbacks = []
        self._last_scan = 0
        self._progress = ""
        self._status = "idle"

    def start_scan(self, callback=None):
        if callback:
            self._callbacks.append(callback)
        if self.running:
            return
        self.running = True
        self._status = "scanning"
        threading.Thread(target=self._scan, daemon=True).start()

    def _scan(self):
        data = {}
        try:
            self._progress = "Collecting CPU info..."
            self.cache["cpu"] = self.monitor.get_cpu_usage()
            self.cache["cpu_info"] = self.monitor.get_cpu_info()

            self._progress = "Collecting memory info..."
            self.cache["ram"] = self.monitor.get_ram_usage()

            self._progress = "Collecting GPU info..."
            self.cache["gpus"] = self.monitor.get_gpu_usage()

            self._progress = "Collecting disk info..."
            self.cache["disks"] = self.monitor.get_disk_usage()

            self._progress = "Collecting processes..."
            self.cache["top_processes"] = self.monitor.get_top_processes(12)

            self._progress = "Collecting network info..."
            self.cache["network"] = self.monitor.get_network_stats()

            self._progress = "Done"
        except:
            import traceback; traceback.print_exc()
        self.running = False
        self._status = "done"
        self._last_scan = time.time()
        for cb in self._callbacks:
            try:
                cb()
            except:
                pass
        self._callbacks = []

    def get(self, key, default=None):
        return self.cache.get(key, default)

    def get_all(self):
        return dict(self.cache)

    def last_scan_ago(self):
        if not self._last_scan:
            return "Never"
        s = int(time.time() - self._last_scan)
        if s < 60:
            return f"{s}s ago"
        m = s // 60
        return f"{m}m ago"

    def is_running(self):
        return self.running

    def get_progress(self):
        return self._progress

    def get_status(self):
        return self._status
