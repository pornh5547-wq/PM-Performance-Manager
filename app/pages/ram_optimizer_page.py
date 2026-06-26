import customtkinter as ctk
import threading
from app.utils.ram_optimizer import get_memory_stats, get_top_memory_processes, empty_working_set, kill_process

class RamOptimizerPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.processes = []
        self.build_ui()

    def build_ui(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(self.main, text="RAM & Process Optimizer", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(self.main, text="Free up memory and manage running processes",
                      font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        stats_card = ctk.CTkFrame(self.main, corner_radius=10, fg_color="#1e293b")
        stats_card.pack(fill="x", pady=5)

        self.stats_labels = {}
        for label, key in [("Total RAM", "total_gb"), ("Available", "available_gb"), ("Used", "used_gb"),
                           ("Usage", "percent"), ("Swap Used", "swap_used_gb")]:
            row = ctk.CTkFrame(stats_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12)).pack(side="left")
            self.stats_labels[key] = ctk.CTkLabel(row, text="---", font=ctk.CTkFont(size=12, weight="bold"))
            self.stats_labels[key].pack(side="right")

        ctrl = ctk.CTkFrame(self.main, fg_color="transparent")
        ctrl.pack(fill="x", pady=5)

        self.empty_btn = ctk.CTkButton(ctrl, text="Free Up Memory", command=self.do_empty,
                                        fg_color="#7c3aed", hover_color="#6d28d9", height=36)
        self.empty_btn.pack(side="left", padx=5)

        self.refresh_btn = ctk.CTkButton(ctrl, text="Refresh", command=self.refresh, fg_color="#475569", height=36)
        self.refresh_btn.pack(side="right", padx=5)

        self.status_label = ctk.CTkLabel(self.main, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(fill="x", pady=5)

        header = ctk.CTkFrame(self.main, fg_color="#1a2332")
        header.pack(fill="x")
        for i, t in enumerate(["Process", "Memory", "CPU", "Status", "Action"]):
            ctk.CTkLabel(header, text=t, font=ctk.CTkFont(size=11, weight="bold"),
                         width=180 if i == 0 else 100).pack(side="left", padx=4, pady=4)

        self.list_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

    def on_activate(self):
        self.refresh()

    def refresh(self):
        def task():
            stats = get_memory_stats()
            procs = get_top_memory_processes(20)
            self.processes = procs
            self.after(0, lambda: self._update_stats(stats))
            self.after(0, self._display_procs)
        threading.Thread(target=task, daemon=True).start()

    def _update_stats(self, stats):
        for key, label in self.stats_labels.items():
            val = stats.get(key, 0)
            if key == "percent":
                label.configure(text=f"{val:.0f}%")
            elif isinstance(val, float):
                label.configure(text=f"{val:.1f} GB")

    def _display_procs(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        for proc in self.processes:
            name = (proc.get("name", "Unknown") or "Unknown")[:35]
            mem_mb = proc.get("memory_mb", 0)
            cpu = proc.get("cpu_percent", 0) or 0
            status = proc.get("status", "")
            pid = proc.get("pid", 0)

            row = ctk.CTkFrame(self.list_frame, fg_color="#1e293b")
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=11), anchor="w", width=180).pack(side="left", padx=4, pady=2)
            ctk.CTkLabel(row, text=f"{mem_mb:.0f} MB", font=ctk.CTkFont(size=11), width=100).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"{cpu:.1f}%", font=ctk.CTkFont(size=11), width=100).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=status, font=ctk.CTkFont(size=11), width=100).pack(side="left", padx=4)

            kill_btn = ctk.CTkButton(row, text="Kill", width=60, height=24,
                                     command=lambda p=pid: self.do_kill(p),
                                     fg_color="#dc2626", font=ctk.CTkFont(size=10))
            kill_btn.pack(side="left", padx=4)

    def do_empty(self):
        self.empty_btn.configure(state="disabled", text="Working...")
        def task():
            result = empty_working_set()
            self.after(0, lambda: self.status_label.configure(
                text=f"Freed ~{result.get('freed_mb', 0)} MB across {result.get('count', 0)} processes",
                text_color="#4ade80"))
            self.after(0, lambda: self.empty_btn.configure(state="normal", text="Free Up Memory"))
            self.after(500, self.refresh)
        threading.Thread(target=task, daemon=True).start()

    def do_kill(self, pid):
        if kill_process(pid):
            self.status_label.configure(text=f"Killed process {pid}", text_color="#ef4444")
            self.refresh()
        else:
            self.status_label.configure(text=f"Failed to kill process {pid}", text_color="#fbbf24")
