import customtkinter as ctk
import threading
from app.utils.privacy import get_privacy_status, block_telemetry, unblock_telemetry

class PrivacyPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.build_ui()

    def build_ui(self):
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(main, text="Privacy & Telemetry Blocker", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(main, text="Block telemetry, disable tracking services, and protect your privacy", font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        self.status_box = ctk.CTkTextbox(main, height=120, wrap="word", state="disabled", font=ctk.CTkFont(size=12))
        self.status_box.pack(fill="x", pady=(0, 10))

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)

        self.block_btn = ctk.CTkButton(btn_frame, text="Block Telemetry", command=self.do_block,
                                        fg_color="#dc2626", hover_color="#b91c1c", height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.block_btn.pack(side="left", padx=5)

        self.unblock_btn = ctk.CTkButton(btn_frame, text="Unblock Telemetry", command=self.do_unblock,
                                          fg_color="#2563eb", hover_color="#1d4ed8", height=40)
        self.unblock_btn.pack(side="left", padx=5)

        self.refresh_btn = ctk.CTkButton(btn_frame, text="Refresh Status", command=self.refresh,
                                          fg_color="#475569", hover_color="#334155", height=40)
        self.refresh_btn.pack(side="right", padx=5)

        info_card = ctk.CTkFrame(main, corner_radius=10, fg_color="#1e293b")
        info_card.pack(fill="x", pady=5)

        self.status_labels = {}
        items = [("telemetry_service", "Telemetry Service"), ("push_service", "Push Service"),
                 ("telemetry_level", "Telemetry Level"), ("hosts_blocked", "Hosts Blocked")]
        for key, label in items:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=4)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=13)).pack(side="left")
            self.status_labels[key] = ctk.CTkLabel(row, text="---", font=ctk.CTkFont(size=13, weight="bold"))
            self.status_labels[key].pack(side="right")

    def on_activate(self):
        self.refresh()

    def _log(self, msg):
        self.status_box.configure(state="normal")
        self.status_box.insert("end", f"> {msg}\n")
        self.status_box.see("end")
        self.status_box.configure(state="disabled")

    def refresh(self):
        def task():
            status = get_privacy_status()
            self.after(0, lambda: self._update_status(status))
        threading.Thread(target=task, daemon=True).start()

    def _update_status(self, status):
        colors = {"telemetry_service": "#4ade80" if status.get("telemetry_service","") != "Running" else "#fbbf24",
                  "push_service": "#4ade80" if status.get("push_service","") != "Running" else "#fbbf24",
                  "telemetry_level": "#4ade80" if status.get("telemetry_level","") in ("0","Not Set") else "#fbbf24",
                  "hosts_blocked": "#4ade80" if status.get("hosts_blocked") else "#94a3b8"}
        for key, label in self.status_labels.items():
            val = status.get(key, "---")
            label.configure(text=str(val), text_color=colors.get(key, "#94a3b8"))

    def do_block(self):
        self.block_btn.configure(state="disabled", text="Blocking...")
        self._log("Blocking telemetry...")
        def task():
            results = block_telemetry()
            self.after(0, lambda: self._done(results))
        threading.Thread(target=task, daemon=True).start()

    def do_unblock(self):
        self.unblock_btn.configure(state="disabled", text="Unblocking...")
        self._log("Unblocking telemetry...")
        def task():
            results = unblock_telemetry()
            self.after(0, lambda: self._done(results, False))
        threading.Thread(target=task, daemon=True).start()

    def _done(self, results, blocked=True):
        for item, status in results:
            self._log(f"{item}: {status}")
        self.block_btn.configure(state="normal", text="Block Telemetry")
        self.unblock_btn.configure(state="normal", text="Unblock Telemetry")
        self.refresh()
