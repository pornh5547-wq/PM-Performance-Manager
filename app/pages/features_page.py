import customtkinter as ctk
import threading
from app.utils.windows_features import list_features, enable_feature, disable_feature, COMMON_FEATURES

class FeaturesPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.features = []
        self.build_ui()

    def build_ui(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(self.main, text="Windows Features", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(self.main, text="Enable or disable optional Windows features (requires admin)",
                      font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        ctrl = ctk.CTkFrame(self.main, fg_color="transparent")
        ctrl.pack(fill="x", pady=5)

        self.refresh_btn = ctk.CTkButton(ctrl, text="Refresh", command=self.refresh, fg_color="#475569", height=36)
        self.refresh_btn.pack(side="right", padx=5)

        self.status_label = ctk.CTkLabel(self.main, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(fill="x", pady=5)

        header = ctk.CTkFrame(self.main, fg_color="#1a2332")
        header.pack(fill="x")
        for i, t in enumerate(["Feature", "State", "Action"]):
            ctk.CTkLabel(header, text=t, font=ctk.CTkFont(size=11, weight="bold"),
                         width=300 if i == 0 else 120).pack(side="left", padx=4, pady=4)

        self.list_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.list_frame, text="Click Refresh to load Windows features", text_color="#64748b").pack(pady=20)

    def refresh(self):
        self.refresh_btn.configure(state="disabled", text="Loading...")
        for w in self.list_frame.winfo_children():
            w.destroy()
        def task():
            all_features = list_features()
            self.features = [f for f in all_features if f.get("FeatureName") in dict(COMMON_FEATURES)]
            self.after(0, self._display)
            self.after(0, lambda: self.refresh_btn.configure(state="normal", text="Refresh"))
        threading.Thread(target=task, daemon=True).start()

    def _display(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        if not self.features:
            ctk.CTkLabel(self.list_frame, text="No features loaded or not running as admin", text_color="#64748b").pack(pady=20)
            return
        names = dict(COMMON_FEATURES)
        for feat in self.features:
            fname = feat.get("FeatureName", "")
            display = names.get(fname, fname)
            state = feat.get("State", "Unknown")
            enabled = state in ("Enabled", "EnablePending")

            row = ctk.CTkFrame(self.list_frame, fg_color="#1e293b")
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=display, font=ctk.CTkFont(size=11), anchor="w", width=300).pack(side="left", padx=4, pady=3)
            state_color = "#4ade80" if enabled else "#94a3b8"
            ctk.CTkLabel(row, text=state, font=ctk.CTkFont(size=11), text_color=state_color, width=120).pack(side="left", padx=4, pady=3)

            btn = ctk.CTkButton(row, text="Disable" if enabled else "Enable", width=80, height=24,
                                command=lambda n=fname, e=enabled: self._toggle(n, e),
                                fg_color="#dc2626" if enabled else "#16a34a",
                                font=ctk.CTkFont(size=10))
            btn.pack(side="left", padx=4)

    def _toggle(self, name, enabled):
        self.status_label.configure(text=f"Toggling {name}...")
        def task():
            if enabled:
                ok = disable_feature(name)
            else:
                ok = enable_feature(name)
            msg = f"{'Disabled' if ok else 'Failed'} {name}" if enabled else f"{'Enabled' if ok else 'Failed'} {name}"
            self.after(0, lambda: self.status_label.configure(text=msg, text_color="#4ade80" if ok else "#ef4444"))
            self.after(1000, self.refresh)
        threading.Thread(target=task, daemon=True).start()
