import customtkinter as ctk
import threading
from app.config import Config
from app.utils.admin import disable_windows_updates, enable_windows_updates, clear_dns_cache, set_high_performance_power_plan
from app.utils.cleanup import clean_temp_files, clean_shader_cache
from app.utils.update_checker import UpdateChecker

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, config: Config, scheduler=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.scheduler = scheduler
        self.switches = {}
        self.build_ui()

    def build_ui(self):
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(main, text="Settings", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(main, text="Configure application behavior", font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        self._section(main, "Appearance", [])
        theme_frame = ctk.CTkFrame(main, corner_radius=10, fg_color="#1e293b")
        theme_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(theme_frame, text="Appearance Mode", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=15, pady=(8, 0))
        self.appearance_var = ctk.StringVar(value=self.config.get("appearance_mode", "Dark"))
        appearance_dd = ctk.CTkOptionMenu(theme_frame, values=["Dark", "Light", "System"],
                                           variable=self.appearance_var)
        appearance_dd.pack(anchor="w", padx=15, pady=(0, 8))

        ctk.CTkLabel(theme_frame, text="Color Theme", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=15, pady=(0, 0))
        self.theme_var = ctk.StringVar(value=self.config.get("color_theme", "dark-blue"))
        theme_dd = ctk.CTkOptionMenu(theme_frame, values=["dark-blue", "blue", "green"],
                                      variable=self.theme_var)
        theme_dd.pack(anchor="w", padx=15, pady=(0, 10))

        self._section(main, "General", [
            ("check_updates", "Check for Updates", "Auto-check for new versions on startup"),
            ("minimize_to_tray", "Minimize to Tray", "Minimize to system tray instead of taskbar"),
        ])

        self._section(main, "Monitoring", [
            ("show_cpu_graph", "Show CPU Graph", "Display real-time CPU chart"),
            ("show_gpu_graph", "Show GPU Graph", "Display real-time GPU chart"),
            ("show_ram_graph", "Show RAM Graph", "Display real-time RAM chart"),
            ("show_disk_graph", "Show Disk Graph", "Display real-time Disk chart"),
        ])

        interval = ctk.CTkFrame(main, corner_radius=10, fg_color="#1e293b")
        interval.pack(fill="x", pady=5)
        ctk.CTkLabel(interval, text="Update Interval", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 0))
        ctk.CTkLabel(interval, text="How often to refresh monitoring data", font=ctk.CTkFont(size=11), text_color="#94a3b8", anchor="w").pack(anchor="w", padx=15)

        row = ctk.CTkFrame(interval, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=10)

        self.interval_var = ctk.IntVar(value=self.config.get("monitoring_interval", 1000))
        slider = ctk.CTkSlider(row, from_=200, to=5000, number_of_steps=24,
                                command=lambda v: self.interval_var.set(int(v)))
        slider.set(self.config.get("monitoring_interval", 1000))
        slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(row, textvariable=self.interval_var, width=50, font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")

        self._section(main, "Gaming Mode", [
            ("gaming_mode_disable_updates", "Disable Windows Updates", "Pause updates during gaming sessions"),
        ])

        self._section(main, "Maintenance", [
            ("scheduled_maintenance", "Scheduled Maintenance", "Run optimization on a regular schedule"),
            ("auto_cleanup_temp", "Auto Clean Temp", "Include temp file cleanup in maintenance"),
            ("auto_cleanup_shader", "Auto Clean Shader Cache", "Include shader cache cleanup"),
            ("plugins_enabled", "Enable Plugins", "Load third-party plugins on startup"),
        ])

        self.status_label = ctk.CTkLabel(main, text="", font=ctk.CTkFont(size=12), text_color="#4ade80")
        self.status_label.pack(pady=(10, 0))

        save = ctk.CTkButton(main, text="Save All Settings", command=self.save,
                             fg_color="#16a34a", hover_color="#15803d", height=40)
        save.pack(pady=(10, 5))

        ctk.CTkLabel(main, text="PM Performance Manager v1.0.0", font=ctk.CTkFont(size=11), text_color="#475569").pack()

    def _section(self, parent, title, items):
        section = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1e293b")
        section.pack(fill="x", pady=5)

        ctk.CTkLabel(section, text=title, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(10, 2))

        for key, label, desc in items:
            row = ctk.CTkFrame(section, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info, text=label, font=ctk.CTkFont(size=13), anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=desc, font=ctk.CTkFont(size=10), text_color="#94a3b8", anchor="w").pack(anchor="w")

            switch = ctk.CTkSwitch(row, text="")
            if self.config.get(key, False):
                switch.select()
            else:
                switch.deselect()
            switch.pack(side="right", padx=5)
            self.switches[key] = switch

    def save(self):
        self.status_label.configure(text="Applying settings...", text_color="#fbbf24")
        for key, switch in self.switches.items():
            self.config.set(key, bool(switch.get()))
        self.config.set("monitoring_interval", self.interval_var.get())
        self.config.set("appearance_mode", self.appearance_var.get())
        self.config.set("color_theme", self.theme_var.get())
        self.config.save()
        ctk.set_appearance_mode(self.appearance_var.get())
        threading.Thread(target=self._apply_settings, daemon=True).start()

    def _apply_settings(self):
        results = []
        try:
            if self.config.get("gaming_mode_disable_updates", False):
                r = disable_windows_updates()
                results.append(("Windows Updates", "Disabled" if (r and r.returncode == 0) else "Failed"))
            else:
                r = enable_windows_updates()
                results.append(("Windows Updates", "Enabled" if (r and r.returncode == 0) else "Failed"))
        except:
            results.append(("Windows Updates", "Error"))

        try:
            if self.scheduler:
                if self.config.get("scheduled_maintenance", False):
                    self.scheduler.start()
                    results.append(("Scheduled Maintenance", "Started"))
                else:
                    self.scheduler.stop()
                    results.append(("Scheduled Maintenance", "Stopped"))
        except:
            results.append(("Scheduled Maintenance", "Error"))

        try:
            if self.config.get("auto_cleanup_temp", True):
                r = clean_temp_files()
                freed = r.get("freed_bytes", 0)
                results.append(("Temp Cleanup", f"Freed {freed // (1024*1024)}MB" if freed else "Done"))
        except:
            results.append(("Temp Cleanup", "Error"))

        try:
            if self.config.get("auto_cleanup_shader", True):
                r = clean_shader_cache()
                freed = r.get("freed_bytes", 0)
                results.append(("Shader Cache", f"Freed {freed // (1024*1024)}MB" if freed else "Done"))
        except:
            results.append(("Shader Cache", "Error"))

        try:
            if self.config.get("check_updates", True):
                checker = UpdateChecker()
                r = checker.check_now()
                if r and r.get("has_update"):
                    results.append(("Updates", f"v{r.get('latest_version','?')} available"))
                else:
                    results.append(("Updates", "Up to date"))
        except:
            results.append(("Updates", "Error"))

        summary = " | ".join(f"{k}: {v}" for k, v in results)
        self.after(0, lambda: self.status_label.configure(text=f"Applied: {summary}", text_color="#4ade80"))
