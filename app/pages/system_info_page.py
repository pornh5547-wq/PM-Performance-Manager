import customtkinter as ctk
import threading
from app.utils.system_info import SystemInfo
from app.utils.cleanup import format_size

class SystemInfoPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.sysinfo = SystemInfo()
        self.build_ui()

    def build_ui(self):
        title = ctk.CTkLabel(self, text="System Information", font=ctk.CTkFont(size=24, weight="bold"), anchor="w")
        title.pack(pady=(20, 10), padx=20, fill="x")

        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.content_frame = ctk.CTkFrame(main, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        self.loading = ctk.CTkLabel(self.content_frame, text="Loading system information...", font=ctk.CTkFont(size=14))
        self.loading.pack(pady=40)

    def on_activate(self):
        self.after(200, self._load_info)

    def _load_info(self):
        info = self.sysinfo.get_all()
        self._display_info(info)

    def _display_info(self, info):
        self.loading.destroy()

        sections = [
            ("Operating System", info.get("os", {}), [
                ("Name", "name"), ("Version", "version"), ("Architecture", "architecture"),
                ("Computer Name", "computername"), ("User", "username"),
            ]),
            ("CPU", info.get("cpu", {}), [
                ("Processor", "name"), ("Cores", "cores"), ("Logical Cores", "logical_cores"),
                ("Max Clock", "max_clock"), ("L2 Cache", "l2_cache"), ("L3 Cache", "l3_cache"),
            ]),
            ("Memory", info.get("ram", {}), [
                ("Total RAM", "total"), ("Module Count", "module_count"),
            ]),
            ("Graphics", info.get("gpu", [{}])[0] if info.get("gpu") else {}, [
                ("GPU", "name"), ("VRAM", "vram"), ("Driver", "driver"), ("Resolution", "resolution"),
            ]),
            ("Motherboard", info.get("motherboard", {}), [
                ("Manufacturer", "manufacturer"), ("Model", "product"),
                ("Version", "version"), ("Serial", "serial"),
            ]),
        ]

        for section_title, data, fields in sections:
            section = ctk.CTkFrame(self.content_frame, corner_radius=10)
            section.pack(fill="x", pady=(0, 10))

            ctk.CTkLabel(section, text=section_title, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

            for label, key in fields:
                val = data.get(key, "Unknown")
                if val is None or val == "":
                    val = "Unknown"
                row = ctk.CTkFrame(section, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=1)
                ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12), width=130, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=str(val), font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(side="left", padx=10)

            ram_modules = info.get("ram", {}).get("modules", [])
            if ram_modules and section_title == "Memory":
                mod_label = ctk.CTkLabel(section, text="RAM Modules:", font=ctk.CTkFont(size=12), anchor="w")
                mod_label.pack(anchor="w", padx=15, pady=(5, 0))
                for mod in ram_modules:
                    mod_text = f"  {mod.get('manufacturer', '')} {mod.get('capacity', '')} {mod.get('speed', '')} {mod.get('type', '')}"
                    ctk.CTkLabel(section, text=mod_text.strip(), font=ctk.CTkFont(size=11), text_color="gray", anchor="w").pack(anchor="w", padx=20)

        drives = info.get("drives", [])
        if drives:
            section = ctk.CTkFrame(self.content_frame, corner_radius=10)
            section.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(section, text="Drives", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
            for drive in drives:
                text = f"  {drive.get('model', '')} - {drive.get('size', '')} ({drive.get('interface', '')})"
                ctk.CTkLabel(section, text=text.strip(), font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=15, pady=1)

        adapters = info.get("network", [])
        if adapters:
            section = ctk.CTkFrame(self.content_frame, corner_radius=10)
            section.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(section, text="Network Adapters", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
            for adapter in adapters:
                text = f"  {adapter.get('name', '')} - IP: {adapter.get('ip', '')} MAC: {adapter.get('mac', '')}"
                ctk.CTkLabel(section, text=text.strip(), font=ctk.CTkFont(size=11), anchor="w").pack(anchor="w", padx=15, pady=1)

        battery = info.get("battery", {})
        if battery:
            section = ctk.CTkFrame(self.content_frame, corner_radius=10)
            section.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(section, text="Battery", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
            for key, label in [("name", "Name"), ("charge", "Charge"), ("status", "Status")]:
                val = battery.get(key, "Unknown")
                if val:
                    row = ctk.CTkFrame(section, fg_color="transparent")
                    row.pack(fill="x", padx=15, pady=1)
                    ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12), width=130, anchor="w").pack(side="left")
                    ctk.CTkLabel(row, text=str(val), font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(side="left", padx=10)
