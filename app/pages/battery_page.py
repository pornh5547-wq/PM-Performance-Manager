import customtkinter as ctk
import threading
import os
from app.utils.battery import get_battery_info, get_power_scheme, generate_battery_report, get_battery_history

class BatteryPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.build_ui()

    def build_ui(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(self.main, text="Battery Report", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(self.main, text="View battery health, capacity, and generate detailed reports",
                      font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        info_card = ctk.CTkFrame(self.main, corner_radius=10, fg_color="#1e293b")
        info_card.pack(fill="x", pady=5)

        self.info_labels = {}
        for label, key in [("Battery Name", "Name"), ("Chemistry", "Chemistry"),
                           ("Design Capacity", "DesignCapacity"), ("Full Charge Capacity", "FullChargeCapacity"),
                           ("Charge Remaining", "EstimatedChargeRemaining"), ("Voltage", "DesignVoltage"),
                           ("Power Scheme", "power_scheme")]:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12), width=160, anchor="w").pack(side="left")
            self.info_labels[key] = ctk.CTkLabel(row, text="---", font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
            self.info_labels[key].pack(side="left", padx=10)

        ctrl = ctk.CTkFrame(self.main, fg_color="transparent")
        ctrl.pack(fill="x", pady=10)

        self.refresh_btn = ctk.CTkButton(ctrl, text="Refresh", command=self.refresh, fg_color="#475569", height=36)
        self.refresh_btn.pack(side="left", padx=5)

        self.report_btn = ctk.CTkButton(ctrl, text="Generate Full Report", command=self.do_report,
                                         fg_color="#2563eb", height=36)
        self.report_btn.pack(side="left", padx=5)

        self.open_report_btn = ctk.CTkButton(ctrl, text="Open Report", command=self.do_open_report,
                                              fg_color="#16a34a", height=36)
        self.open_report_btn.pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(self.main, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(fill="x", pady=5)

        health_card = ctk.CTkFrame(self.main, corner_radius=10, fg_color="#1e293b")
        health_card.pack(fill="x", pady=5)

        ctk.CTkLabel(health_card, text="Health Assessment", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 2))

        self.health_bar = ctk.CTkProgressBar(health_card, height=12, corner_radius=6, progress_color="#4ade80")
        self.health_bar.pack(fill="x", padx=15, pady=(5, 5))
        self.health_bar.set(0)

        self.health_text = ctk.CTkLabel(health_card, text="No battery data", font=ctk.CTkFont(size=12), text_color="#94a3b8")
        self.health_text.pack(anchor="w", padx=15, pady=(0, 10))

    def on_activate(self):
        self.refresh()

    def refresh(self):
        def task():
            info = get_battery_info()
            if isinstance(info, dict):
                info["power_scheme"] = get_power_scheme()
            self.after(0, lambda: self._update_info(info))
        threading.Thread(target=task, daemon=True).start()

    def _update_info(self, info):
        for key, label in self.info_labels.items():
            val = info.get(key, "---")
            if val is None or val == "":
                val = "---"
            if key == "EstimatedChargeRemaining":
                label.configure(text=f"{val}%")
            elif key in ("DesignCapacity", "FullChargeCapacity"):
                try:
                    label.configure(text=f"{int(val)} mWh")
                except:
                    label.configure(text=str(val))
            elif key == "DesignVoltage":
                try:
                    label.configure(text=f"{int(val)} mV")
                except:
                    label.configure(text=str(val))
            else:
                label.configure(text=str(val))

        try:
            design = int(info.get("DesignCapacity", 0) or 0)
            full = int(info.get("FullChargeCapacity", 0) or 0)
            if design > 0:
                pct = full / design
                self.health_bar.set(pct)
                color = "#4ade80" if pct > 0.8 else ("#fbbf24" if pct > 0.5 else "#ef4444")
                self.health_bar.configure(progress_color=color)
                self.health_text.configure(text=f"Battery health: {pct*100:.0f}% ({full} / {design} mWh)")
            else:
                self.health_bar.set(0)
                self.health_text.configure(text="No battery detected")
        except:
            pass

    def do_report(self):
        self.report_btn.configure(state="disabled", text="Generating...")
        self.status_label.configure(text="Generating battery report...")
        def task():
            result = generate_battery_report()
            self.after(0, lambda: self._report_done(result))
        threading.Thread(target=task, daemon=True).start()

    def _report_done(self, result):
        self.report_btn.configure(state="normal", text="Generate Full Report")
        if result.get("success"):
            path = result.get("path", "")
            self.status_label.configure(text=f"Report saved to {path}", text_color="#4ade80")
        else:
            self.status_label.configure(text="Failed to generate report", text_color="#ef4444")

    def do_open_report(self):
        history = get_battery_history()
        if history.get("exists"):
            os.startfile(history.get("report_path", ""))
        else:
            self.status_label.configure(text="No report found. Generate one first.", text_color="#fbbf24")
