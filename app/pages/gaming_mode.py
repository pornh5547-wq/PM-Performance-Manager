import customtkinter as ctk
import threading
from app.utils.game_detector import GameDetector
from app.utils.admin import enable_gaming_mode, disable_gaming_mode, disable_windows_updates, enable_windows_updates, set_high_performance_power_plan
from app.utils.cleanup import run_full_cleanup, format_size
from app.config import log

class GamingModePage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.detector = GameDetector()
        self.games = []
        self.active = False
        self.build_ui()

    def on_activate(self):
        saved = self.config.get("gaming_mode_active", False)
        if saved != self.active:
            self.active = saved
            self._update_toggle_ui()

    def build_ui(self):
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(main, text="Gaming Mode", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(main, text="Auto-detect games and optimize your system for gaming", font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        controls = ctk.CTkFrame(main, corner_radius=10, fg_color="#1e293b")
        controls.pack(fill="x", pady=(0, 10))

        inner = ctk.CTkFrame(controls, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)

        self.toggle_btn = ctk.CTkButton(inner, text="ACTIVATE GAMING MODE", command=self.toggle,
                                         fg_color="#16a34a", hover_color="#15803d", height=40, font=ctk.CTkFont(size=13, weight="bold"))
        self.toggle_btn.pack(side="left", padx=(0, 10))

        self.status_badge = ctk.CTkLabel(inner, text="Inactive", font=ctk.CTkFont(size=12),
                                          fg_color="#334155", corner_radius=4, padx=10, pady=4)
        self.status_badge.pack(side="left", padx=5)

        self.detect_btn = ctk.CTkButton(inner, text="Scan Games", command=self.scan,
                                         fg_color="#1f538d", hover_color="#1a4173", width=110)
        self.detect_btn.pack(side="right", padx=(5, 0))

        self.optimize_btn = ctk.CTkButton(inner, text="Pre-Game Optimize", command=self.optimize,
                                           fg_color="#7c3aed", hover_color="#6d28d9", width=140)
        self.optimize_btn.pack(side="right", padx=5)

        games_section = ctk.CTkFrame(main, corner_radius=10, fg_color="#1e293b")
        games_section.pack(fill="both", expand=True, pady=(0, 10))

        ctk.CTkLabel(games_section, text="Detected Games", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        self.games_container = ctk.CTkScrollableFrame(games_section, fg_color="transparent")
        self.games_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ctk.CTkLabel(self.games_container, text="Click 'Scan Games' to search for installed games", text_color="#64748b").pack(pady=20)

        status_section = ctk.CTkFrame(main, corner_radius=10, fg_color="#1e293b")
        status_section.pack(fill="x")

        self.status_text = ctk.CTkTextbox(status_section, height=80, wrap="word", state="disabled", font=ctk.CTkFont(size=11))
        self.status_text.pack(fill="x", padx=15, pady=10)

    def _update_toggle_ui(self):
        if self.active:
            self.toggle_btn.configure(text="DEACTIVATE GAMING MODE", fg_color="#dc2626", hover_color="#b91c1c")
            self.status_badge.configure(text="Active", fg_color="#16a34a", text_color="white")
        else:
            self.toggle_btn.configure(text="ACTIVATE GAMING MODE", fg_color="#16a34a", hover_color="#15803d")
            self.status_badge.configure(text="Inactive", fg_color="#334155", text_color="#94a3b8")

    def scan(self):
        self.detect_btn.configure(state="disabled", text="Scanning...")
        self._log("Scanning for games...")

        def task():
            games = self.detector.detect_all()
            self.games = games
            self.after(0, self._display)
            self.after(0, lambda: self.detect_btn.configure(state="normal", text="Scan Games"))
        threading.Thread(target=task, daemon=True).start()

    def _display(self):
        for w in self.games_container.winfo_children():
            w.destroy()
        if not self.games:
            ctk.CTkLabel(self.games_container, text="No games found. Try running as admin.", text_color="#64748b").pack(pady=20)
            return
        platforms = {}
        for g in self.games:
            p = g.get("platform", "Other")
            platforms.setdefault(p, []).append(g)
        for plat, glist in sorted(platforms.items()):
            ctk.CTkLabel(self.games_container, text=f"  {plat} ({len(glist)})", font=ctk.CTkFont(size=12, weight="bold"),
                         anchor="w").pack(fill="x", padx=5, pady=(5, 2))
            for g in glist:
                row = ctk.CTkFrame(self.games_container, fg_color=("gray90", "#1a2332"), height=28)
                row.pack(fill="x", padx=10, pady=1)
                ctk.CTkLabel(row, text=f"  {g['name']}", font=ctk.CTkFont(size=12), anchor="w").pack(side="left", padx=5)
                btn = ctk.CTkButton(row, text="Launch", width=70, height=22,
                                    command=lambda gg=g: self._launch(gg),
                                    fg_color="#16a34a", hover_color="#15803d", font=ctk.CTkFont(size=10))
                btn.pack(side="right", padx=5, pady=2)

    def toggle(self):
        self.active = not self.active
        self.config.set("gaming_mode_active", self.active)
        self._update_toggle_ui()
        if self.active:
            self._log("Activating gaming mode...")
            threading.Thread(target=lambda: [enable_gaming_mode(), disable_windows_updates(),
                                             self.after(0, lambda: self._log("Gaming mode active - High performance"))], daemon=True).start()
        else:
            self._log("Deactivating gaming mode...")
            threading.Thread(target=lambda: [disable_gaming_mode(), enable_windows_updates(),
                                             self.after(0, lambda: self._log("Gaming mode deactivated"))], daemon=True).start()

    def optimize(self):
        self.optimize_btn.configure(state="disabled", text="Working...")
        self._log("Running pre-game optimization...")

        def task():
            results, freed = run_full_cleanup()
            self.after(0, lambda: self._log(f"Freed {format_size(freed)}"))
            self.after(0, lambda: self.optimize_btn.configure(state="normal", text="Pre-Game Optimize"))
        threading.Thread(target=task, daemon=True).start()

    def _launch(self, game):
        self._log(f"Launching {game['name']}...")
        threading.Thread(target=lambda: self.detector.launch_game(game), daemon=True).start()

    def _log(self, msg):
        self.status_text.configure(state="normal")
        self.status_text.insert("end", f"> {msg}\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")
