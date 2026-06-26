import customtkinter as ctk
import threading
from app.utils.cleanup import run_full_cleanup, get_total_cleanable_size, format_size, clean_temp_files, clean_shader_cache, clean_prefetch
from app.utils.ssd_optimizer import SSDOptimizer
from app.utils.restore import create_restore_point

class PerformanceModePage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.build_ui()

    def build_ui(self):
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(main, text="⚡ Performance Mode", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(main, text="Optimize your system with one click", font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        self.status_box = ctk.CTkTextbox(main, height=140, wrap="word", state="disabled", font=ctk.CTkFont(size=12))
        self.status_box.pack(fill="x", pady=(0, 10))

        cards = [
            ("🛡️  Create Restore Point", "Backup system state before making changes", "#2563eb",
             lambda cb: self._run_task("Creating restore point...", create_restore_point, cb)),
            ("🧹  Temp File Cleanup", f"Estimated: {format_size(get_total_cleanable_size())} can be freed", "#7c3aed",
             lambda cb: self._run_task("Cleaning temp files...", self._do_cleanup, cb)),
            ("🎮  Clear Shader Cache", "Remove GPU shader compilation cache", "#db2777",
             lambda cb: self._run_task("Clearing shader cache...", clean_shader_cache, cb)),
            ("💿  SSD Optimization", "Enable TRIM and optimize all drives", "#0891b2",
             lambda cb: self._run_task("Optimizing SSDs...", SSDOptimizer().run_full_optimization, cb)),
            ("🚀  Full Performance Boost", "Run all optimizations in sequence", "#16a34a",
             lambda cb: self._run_task("Running full optimization...", self._full_boost, cb)),
        ]

        for title, desc, color, action in cards:
            self._card(main, title, desc, color, action)

    def _card(self, parent, title, desc, color, action):
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1e293b")
        card.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(anchor="w")
        ctk.CTkLabel(inner, text=desc, font=ctk.CTkFont(size=11), text_color="#94a3b8", anchor="w").pack(anchor="w", pady=(2, 8))

        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.pack(fill="x")

        result = ctk.CTkLabel(row2, text="", font=ctk.CTkFont(size=12), text_color="#4ade80")
        result.pack(side="left")

        btn = ctk.CTkButton(row2, text="Run", fg_color=color, hover_color=self._darken(color),
                            width=100, height=30, corner_radius=6)
        btn.configure(command=lambda b=btn, r=result, a=action: self._click(b, r, a))
        btn.pack(side="right")

    def _darken(self, c):
        r = max(int(c[1:3], 16) - 25, 0)
        g = max(int(c[3:5], 16) - 25, 0)
        b = max(int(c[5:7], 16) - 25, 0)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _click(self, btn, result, action):
        btn.configure(state="disabled", text="Running...")
        result.configure(text="")
        action(lambda ok, msg: self._done(btn, result, ok, msg))

    def _done(self, btn, result, ok, msg):
        btn.configure(state="normal", text="Run")
        result.configure(text=msg if ok else f"Failed: {msg}")

    def _run_task(self, start_msg, func, callback):
        self._add_status(start_msg)
        threading.Thread(target=lambda: self._execute(func, callback), daemon=True).start()

    def _execute(self, func, callback):
        try:
            result = func() if callable(func) else func
            if isinstance(result, dict):
                if "freed_bytes" in result:
                    msg = f"Freed {format_size(result['freed_bytes'])}"
                elif "success" in result:
                    msg = "Completed" if result["success"] else str(result.get("error", "Failed"))
                else:
                    msg = "Completed"
            else:
                msg = "Completed"
            self.after(0, lambda: self._add_status(f"✓ {msg}"))
            self.after(0, lambda: callback(True, msg))
        except Exception as e:
            self.after(0, lambda: self._add_status(f"✗ Error: {str(e)}"))
            self.after(0, lambda: callback(False, str(e)))

    def _do_cleanup(self):
        return run_full_cleanup()[0]

    def _full_boost(self):
        create_restore_point()
        run_full_cleanup()
        clean_shader_cache()
        SSDOptimizer().run_full_optimization()
        return {"success": True}

    def _add_status(self, msg):
        self.status_box.configure(state="normal")
        import datetime
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_box.insert("end", f"[{ts}] {msg}\n")
        self.status_box.see("end")
        self.status_box.configure(state="disabled")
