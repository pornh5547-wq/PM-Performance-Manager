import os
import importlib
import inspect
import json
from app.config import CONFIG_DIR, log

PLUGINS_DIR = os.path.join(CONFIG_DIR, 'plugins')
PLUGIN_MANIFEST = 'plugin.json'

class PluginBase:
    name = "Base Plugin"
    version = "1.0.0"
    author = "Unknown"
    description = ""

    def on_load(self, app):
        pass

    def on_unload(self, app):
        pass

    def get_ui_elements(self):
        return []

class PluginLoader:
    def __init__(self):
        self.plugins = []
        self.plugin_modules = {}
        os.makedirs(PLUGINS_DIR, exist_ok=True)

    def discover_plugins(self):
        self.plugins = []
        if not os.path.exists(PLUGINS_DIR):
            return self.plugins
        for item in os.listdir(PLUGINS_DIR):
            plugin_dir = os.path.join(PLUGINS_DIR, item)
            if os.path.isdir(plugin_dir):
                manifest_path = os.path.join(plugin_dir, PLUGIN_MANIFEST)
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                        self.plugins.append({
                            "name": manifest.get("name", item),
                            "version": manifest.get("version", "1.0.0"),
                            "author": manifest.get("author", "Unknown"),
                            "description": manifest.get("description", ""),
                            "entry": manifest.get("entry", "main.py"),
                            "dir": plugin_dir,
                            "enabled": manifest.get("enabled", True),
                        })
                    except:
                        pass
        return self.plugins

    def load_plugin(self, plugin_info):
        if not plugin_info.get("enabled", True):
            return None
        entry = plugin_info.get("entry", "main.py")
        entry_path = os.path.join(plugin_info["dir"], entry)
        if not os.path.exists(entry_path):
            log(f"Plugin entry not found: {entry_path}")
            return None
        try:
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_info['name']}",
                entry_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj != PluginBase:
                        instance = obj()
                        instance.on_load(None)
                        self.plugin_modules[plugin_info["name"]] = instance
                        log(f"Plugin loaded: {plugin_info['name']} v{plugin_info['version']}")
                        return instance
        except Exception as e:
            log(f"Plugin load error ({plugin_info['name']}): {str(e)}")
        return None

    def load_all(self):
        self.discover_plugins()
        loaded = []
        for plugin in self.plugins:
            instance = self.load_plugin(plugin)
            if instance:
                loaded.append(instance)
        return loaded

    def unload_all(self):
        for name, instance in self.plugin_modules.items():
            try:
                instance.on_unload(None)
            except:
                pass
        self.plugin_modules.clear()
        log("All plugins unloaded")
