import customtkinter as ctk
import threading
from app.utils.visual_toggles import get_visual_status, toggle_animations, toggle_startup_sound, toggle_transparency, toggle_performance_mode

class VisualTogglesPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.status = {}
        self.build_ui()

    def build_ui(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(self.main, text="Visual Effects & Sounds", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(self.main, text="Toggle Windows visual effects, animations, and startup sound",
                      font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        self.cards = {}
        toggles = [
            ("animations", "Taskbar Animations", "Animate taskbar, start menu, and window minimize/maximize", ""),
            ("startup_sound", "Startup Sound", "Play Windows startup sound on boot", ""),
            ("transparency", "Transparency Effects", "Enable acrylic/transparency effects in UI", ""),
            ("performance_mode", "Performance Mode", "Disable all visual effects for maximum performance", ""),
        ]

        for key, title, desc, _ in toggles:
            card = ctk.CTkFrame(self.main, corner_radius=10, fg_color="#1e293b")
            card.pack(fill="x", pady=4)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=10)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info, text=title, font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(anchor="w")
            ctk.CTkLabel(info, text=desc, font=ctk.CTkFont(size=11), text_color="#94a3b8", anchor="w").pack(anchor="w")

            switch = ctk.CTkSwitch(row, text="", command=lambda k=key: self._on_toggle(k))
            switch.pack(side="right", padx=5)

            status_lbl = ctk.CTkLabel(row, text="---", font=ctk.CTkFont(size=11), width=30)
            status_lbl.pack(side="right", padx=5)

            self.cards[key] = {"switch": switch, "status": status_lbl, "title": title}

        ctk.CTkLabel(self.main, text="Note: Some changes may require a restart to take effect",
                      font=ctk.CTkFont(size=11), text_color="#64748b", anchor="w").pack(pady=5)

        self.refresh_btn = ctk.CTkButton(self.main, text="Refresh Status", command=self.refresh, fg_color="#475569")
        self.refresh_btn.pack(pady=5)

        self.status_label = ctk.CTkLabel(self.main, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack()

    def on_activate(self):
        self.refresh()

    def refresh(self):
        def task():
            status = get_visual_status()
            self.status = status
            self.after(0, self._update_ui)
        threading.Thread(target=task, daemon=True).start()

    def _update_ui(self):
        for key, card in self.cards.items():
            if key == "performance_mode":
                continue
            val = self.status.get(key)
            if val is True:
                card["switch"].select()
                card["status"].configure(text="On", text_color="#4ade80")
            elif val is False:
                card["switch"].deselect()
                card["status"].configure(text="Off", text_color="#ef4444")
            else:
                card["switch"].deselect()
                card["status"].configure(text="?", text_color="#94a3b8")

    def _on_toggle(self, key):
        enabled = self.cards[key]["switch"].get()
        self.status_label.configure(text=f"Applying {self.cards[key]['title']}...")
        def task():
            ok = False
            if key == "animations":
                ok = toggle_animations(enabled)
            elif key == "startup_sound":
                ok = toggle_startup_sound(enabled)
            elif key == "transparency":
                ok = toggle_transparency(enabled)
            elif key == "performance_mode":
                ok = toggle_performance_mode(enabled)
            msg = f"{'Enabled' if ok else 'Failed'} {self.cards[key]['title']}"
            self.after(0, lambda: self.status_label.configure(text=msg, text_color="#4ade80" if ok else "#ef4444"))
            self.after(500, self.refresh)
        threading.Thread(target=task, daemon=True).start()
