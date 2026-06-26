import json
import os

CONFIG_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'PMPerformanceManager')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
LOG_FILE = os.path.join(CONFIG_DIR, 'logs.txt')

DEFAULT_CONFIG = {
    "theme": "Dark",
    "start_minimized": False,
    "minimize_to_tray": True,
    "monitoring_interval": 1000,
    "auto_cleanup_temp": True,
    "auto_cleanup_shader": True,
    "game_detection": True,
    "scheduled_maintenance": False,
    "maintenance_interval_hours": 24,
    "last_maintenance": None,
    "show_cpu_graph": True,
    "show_gpu_graph": True,
    "show_ram_graph": True,
    "show_disk_graph": True,
    "repair_log_path": LOG_FILE,
    "plugins_enabled": True,
    "check_updates": True,
    "gaming_mode_gpu_profile": "performance",
    "gaming_mode_disable_updates": True,
    "gaming_mode_disable_defender": False,
}

class Config:
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except:
                pass

    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get_all(self):
        return self.data.copy()

def log(message):
    timestamp = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f"[{timestamp}] {message}\n"
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(entry)
    except:
        pass

def get_logs():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                return f.read()
        except:
            return ""
    return ""
