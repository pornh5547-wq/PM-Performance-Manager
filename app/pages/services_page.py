import customtkinter as ctk
import threading
from app.utils.services import list_services, disable_service, enable_service, set_startup_type

class ServicesPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.services = []
        self.buttons = {}
        self.build_ui()

    def build_ui(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(self.main, text="Windows Services Manager", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(self.main, text="View and manage Windows services. Safe services can be disabled to free resources.",
                      font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        controls = ctk.CTkFrame(self.main, fg_color="transparent")
        controls.pack(fill="x", pady=5)
        self.refresh_btn = ctk.CTkButton(controls, text="Refresh", command=self.refresh, fg_color="#475569", width=100)
        self.refresh_btn.pack(side="right")
        self.status_label = ctk.CTkLabel(controls, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left")

        self.list_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, pady=5)

    def on_activate(self):
        self.refresh()

    def refresh(self):
        self.refresh_btn.configure(state="disabled", text="Loading...")
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.buttons = {}
        def task():
            svcs = list_services()
            self.services = svcs
            self.after(0, self._display)
        threading.Thread(target=task, daemon=True).start()

    def _display(self):
        self.refresh_btn.configure(state="normal", text="Refresh")
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.services:
            ctk.CTkLabel(self.list_frame, text="No services found or not running as admin", text_color="#64748b").pack(pady=20)
            return

        header = ctk.CTkFrame(self.list_frame, fg_color="#1a2332")
        header.pack(fill="x", pady=(0, 2))
        for i, text in enumerate(["Service", "Status", "Start Type", "Safety", "Action"]):
            ctk.CTkLabel(header, text=text, font=ctk.CTkFont(size=11, weight="bold"),
                         width=120 if i < 4 else 80).pack(side="left", padx=4)

        for svc in self.services:
            name = svc.get("Name", "")
            display = svc.get("DisplayName", name)[:35]
            status = svc.get("Status", "Unknown")
            start_type = svc.get("StartType", "Unknown")
            safety = svc.get("Safety", "Unknown")

            row = ctk.CTkFrame(self.list_frame, fg_color="#1e293b", height=30)
            row.pack(fill="x", pady=1)

            status_color = "#4ade80" if status == "Running" else "#94a3b8"
            safety_color = {"Safe": "#4ade80", "Unknown": "#fbbf24", "Critical": "#ef4444"}.get(safety, "#94a3b8")

            ctk.CTkLabel(row, text=display, font=ctk.CTkFont(size=11), anchor="w", width=120).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=status, font=ctk.CTkFont(size=11), text_color=status_color, width=120).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=start_type, font=ctk.CTkFont(size=11), width=120).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=safety, font=ctk.CTkFont(size=11), text_color=safety_color, width=120).pack(side="left", padx=4)

            if safety == "Safe":
                is_running = status == "Running"
                txt = "Disable" if is_running else "Enable"
                btn = ctk.CTkButton(row, text=txt, width=70, height=24,
                                    command=lambda n=name, r=is_running: self._toggle(n, r),
                                    fg_color="#dc2626" if is_running else "#16a34a",
                                    hover_color="#b91c1c" if is_running else "#15803d",
                                    font=ctk.CTkFont(size=10))
                btn.pack(side="right", padx=4)
                self.buttons[name] = {"btn": btn, "row": row, "running": is_running}

    def _toggle(self, name, is_running):
        if name in self.buttons:
            self.buttons[name]["btn"].configure(state="disabled", text="...")
        self.status_label.configure(text=f"Toggling {name}...")
        def task():
            if is_running:
                ok = disable_service(name)
            else:
                ok = enable_service(name)
            msg = f"{'Disabled' if ok else 'Failed'} {name}"
            self.after(0, lambda: self.status_label.configure(text=msg))
            self.after(1000, self.refresh)
        threading.Thread(target=task, daemon=True).start()
