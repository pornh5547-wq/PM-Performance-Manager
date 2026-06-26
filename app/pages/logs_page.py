import customtkinter as ctk
from app.config import get_logs, LOG_FILE, log
import datetime

class LogsPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.build_ui()

    def build_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(main, text="📋 Activity Logs", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(main, text="Application and diagnostic activity record", font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        controls = ctk.CTkFrame(main, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(controls, text="🔄 Refresh", command=self.refresh, width=100, fg_color="#1f538d").pack(side="left", padx=(0, 5))
        ctk.CTkButton(controls, text="🗑️ Clear", command=self.clear, width=100, fg_color="#dc2626", hover_color="#b91c1c").pack(side="left")
        ctk.CTkButton(controls, text="📝 Log Test Entry", command=self.log_test, width=120, fg_color="#334155").pack(side="left", padx=5)

        self.log_text = ctk.CTkTextbox(main, wrap="word", state="disabled", font=ctk.CTkFont(size=11, family="Consolas"))
        self.log_text.pack(fill="both", expand=True)

    def on_activate(self):
        self.refresh()

    def refresh(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        logs = get_logs()
        if logs:
            self.log_text.insert("1.0", logs)
        else:
            self.log_text.insert("1.0", "No logs recorded yet.\nActivities will appear here as you use the application.")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear(self):
        try:
            open(LOG_FILE, 'w').close()
        except:
            pass
        self.refresh()

    def log_test(self):
        log("Manual test entry logged")
        self.refresh()
