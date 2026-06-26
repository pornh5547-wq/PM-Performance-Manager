import customtkinter as ctk
import threading
from app.utils.repair import NetworkRepair
from app.monitors.system_monitor import SystemMonitor

class NetworkRepairPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.monitor = SystemMonitor()
        self.build_ui()

    def build_ui(self):
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(main, text="🌐 Network Repair", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(main, text="Diagnose and fix network connectivity issues", font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        stats_card = ctk.CTkFrame(main, corner_radius=10, fg_color="#1e293b")
        stats_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(stats_card, text="Network Statistics", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        self.stat_labels = {}
        for label in ["Data Sent", "Data Received", "Packets Sent", "Packets Received"]:
            row = ctk.CTkFrame(stats_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=1)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12), width=130, anchor="w").pack(side="left")
            lbl = ctk.CTkLabel(row, text="...", font=ctk.CTkFont(size=12, weight="bold"))
            lbl.pack(side="left")
            self.stat_labels[label] = lbl

        self._stats_pending = False
        self._net_after_id = None

        tools_card = ctk.CTkFrame(main, corner_radius=10, fg_color="#1e293b")
        tools_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(tools_card, text="Repair Tools", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        tools = [
            ("Flush DNS", "Clear DNS resolver cache", "#0891b2", NetworkRepair.flush_dns),
            ("Reset Winsock", "Reset network catalog", "#7c3aed", NetworkRepair.reset_winsock),
            ("Reset IP Stack", "Reset TCP/IP to default", "#db2777", NetworkRepair.reset_ip),
            ("Renew IP", "Release & renew DHCP lease", "#ca8a04", NetworkRepair.renew_ip),
            ("Full Network Reset", "Run all repairs at once", "#16a34a", NetworkRepair.reset_all),
        ]

        for name, desc, color, func in tools:
            row = ctk.CTkFrame(tools_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=13), width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=desc, font=ctk.CTkFont(size=11), text_color="#94a3b8", anchor="w").pack(side="left", padx=5, fill="x", expand=True)
            btn = ctk.CTkButton(row, text="Run", width=60, height=26,
                                command=lambda f=func, n=name: self._run(f, n),
                                fg_color=color, hover_color=self._darken(color))
            btn.pack(side="right", padx=5)

        self.status_box = ctk.CTkTextbox(main, height=100, wrap="word", state="disabled", font=ctk.CTkFont(size=11))
        self.status_box.pack(fill="x")

    def _darken(self, c):
        r = max(int(c[1:3], 16) - 25, 0)
        g = max(int(c[3:5], 16) - 25, 0)
        b = max(int(c[5:7], 16) - 25, 0)
        return f"#{r:02x}{g:02x}{b:02x}"

    def start_monitoring(self):
        self._stats_pending = True
        self.after(200, self._refresh_stats)

    def stop_monitoring(self):
        self._stats_pending = False
        if self._net_after_id:
            self.after_cancel(self._net_after_id)
            self._net_after_id = None

    def on_activate(self):
        if not self._stats_pending:
            self.start_monitoring()

    def _refresh_stats(self):
        if not self._stats_pending:
            return
        try:
            net = self.monitor.get_network_stats()
            self.stat_labels["Data Sent"].configure(text=self._fmt(net.get("bytes_sent", 0)))
            self.stat_labels["Data Received"].configure(text=self._fmt(net.get("bytes_recv", 0)))
            self.stat_labels["Packets Sent"].configure(text=str(net.get("packets_sent", 0)))
            self.stat_labels["Packets Received"].configure(text=str(net.get("packets_recv", 0)))
        except:
            pass
        if self._stats_pending:
            self._net_after_id = self.after(3000, self._refresh_stats)

    def _fmt(self, b):
        for u in ['B', 'KB', 'MB', 'GB']:
            if b < 1024:
                return f"{b:.1f} {u}"
            b /= 1024
        return f"{b:.1f} TB"

    def _run(self, func, name):
        self._log(f"Running {name}...")
        func(lambda tool, ok, out: self.after(0, lambda: self._log(f"{'✓' if ok else '✗'} {name} completed")))

    def _log(self, msg):
        self.status_box.configure(state="normal")
        self.status_box.insert("end", f"> {msg}\n")
        self.status_box.see("end")
        self.status_box.configure(state="disabled")
