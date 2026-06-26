import threading
import requests
from packaging import version as pkg_version
from app.config import log

APP_VERSION = "1.0.0"
UPDATE_URL = "https://api.github.com/repos/user/pm-performance-manager/releases/latest"

class UpdateChecker:
    def __init__(self):
        self.latest_version = None
        self.download_url = None
        self.release_notes = ""

    def check(self, callback=None):
        def task():
            try:
                log("Checking for updates...")
                response = requests.get(UPDATE_URL, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.latest_version = data.get("tag_name", "").lstrip("v")
                    self.download_url = data.get("html_url", "")
                    assets = data.get("assets", [])
                    if assets:
                        for asset in assets:
                            if asset.get("name", "").endswith(".exe"):
                                self.download_url = asset.get("browser_download_url", self.download_url)
                                break
                    self.release_notes = data.get("body", "")
                    has_update = False
                    if self.latest_version:
                        try:
                            has_update = pkg_version.parse(self.latest_version) > pkg_version.parse(APP_VERSION)
                        except:
                            has_update = self.latest_version != APP_VERSION
                    log(f"Update check: current={APP_VERSION}, latest={self.latest_version}, has_update={has_update}")
                    if callback:
                        callback({
                            "has_update": has_update,
                            "current_version": APP_VERSION,
                            "latest_version": self.latest_version,
                            "download_url": self.download_url,
                            "release_notes": self.release_notes,
                        })
                else:
                    log(f"Update check failed: HTTP {response.status_code}")
                    if callback:
                        callback({"has_update": False, "error": f"HTTP {response.status_code}"})
            except Exception as e:
                log(f"Update check error: {str(e)}")
                if callback:
                    callback({"has_update": False, "error": str(e)})
        threading.Thread(target=task, daemon=True).start()

    def check_now(self):
        try:
            response = requests.get(UPDATE_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.latest_version = data.get("tag_name", "").lstrip("v")
                self.download_url = data.get("html_url", "")
                assets = data.get("assets", [])
                if assets:
                    for asset in assets:
                        if asset.get("name", "").endswith(".exe"):
                            self.download_url = asset.get("browser_download_url", self.download_url)
                            break
                self.release_notes = data.get("body", "")
                has_update = False
                if self.latest_version:
                    try:
                        has_update = pkg_version.parse(self.latest_version) > pkg_version.parse(APP_VERSION)
                    except:
                        has_update = self.latest_version != APP_VERSION
                return {
                    "has_update": has_update,
                    "current_version": APP_VERSION,
                    "latest_version": self.latest_version,
                    "download_url": self.download_url,
                    "release_notes": self.release_notes,
                }
        except:
            pass
        return {"has_update": False}
