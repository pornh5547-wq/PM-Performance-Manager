import customtkinter as ctk
import threading
import time
from app.utils.speed_test import test_latency, test_download_speed

class SpeedTestPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.build_ui()

    def build_ui(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(self.main, text="Network Speed Test", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(self.main, text="Test your internet download speed and latency",
                      font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        results_card = ctk.CTkFrame(self.main, corner_radius=10, fg_color="#1e293b")
        results_card.pack(fill="x", pady=10)

        speed_frame = ctk.CTkFrame(results_card, fg_color="transparent")
        speed_frame.pack(fill="x", padx=20, pady=20)

        self.speed_label = ctk.CTkLabel(speed_frame, text="---", font=ctk.CTkFont(size=48, weight="bold"),
                                         text_color="#3b82f6")
        self.speed_label.pack()
        ctk.CTkLabel(speed_frame, text="Mbps Download", font=ctk.CTkFont(size=14), text_color="#94a3b8").pack()

        latency_frame = ctk.CTkFrame(results_card, fg_color="transparent")
        latency_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.latency_labels = {}
        for host in ["8.8.8.8", "1.1.1.1", "google.com"]:
            row = ctk.CTkFrame(latency_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=host, font=ctk.CTkFont(size=12), width=100).pack(side="left")
            self.latency_labels[host] = ctk.CTkLabel(row, text="---", font=ctk.CTkFont(size=12, weight="bold"))
            self.latency_labels[host].pack(side="right")

        progress_card = ctk.CTkFrame(self.main, fg_color="#1e293b", corner_radius=10)
        progress_card.pack(fill="x", pady=5)

        self.progress_bar = ctk.CTkProgressBar(progress_card, height=8, corner_radius=4, progress_color="#3b82f6")
        self.progress_bar.pack(fill="x", padx=20, pady=(15, 5))
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(progress_card, text="Click 'Start Test' to measure your speed",
                                            font=ctk.CTkFont(size=12), text_color="#94a3b8")
        self.progress_label.pack(pady=(0, 15))

        self.test_btn = ctk.CTkButton(self.main, text="Start Test", command=self.do_test,
                                       fg_color="#16a34a", hover_color="#15803d",
                                       height=44, font=ctk.CTkFont(size=14, weight="bold"))
        self.test_btn.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.main, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack()

    def do_test(self):
        self.test_btn.configure(state="disabled", text="Testing...")
        self.speed_label.configure(text="...")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Testing latency...")
        for lbl in self.latency_labels.values():
            lbl.configure(text="...")

        def task():
            self.after(0, lambda: self.progress_bar.set(0.15))
            latency_results = test_latency()
            self.after(0, lambda: self._update_latency(latency_results))
            self.after(0, lambda: self.progress_label.configure(text="Testing download speed (100MB file)..."))
            self.after(0, lambda: self.progress_bar.set(0.3))
            dl_result = test_download_speed()
            self.after(0, lambda: self._update_speed(dl_result))
            self.after(0, lambda: self.progress_bar.set(1.0))
            self.after(0, lambda: self.progress_label.configure(text="Test complete"))
            self.after(0, lambda: self.test_btn.configure(state="normal", text="Test Again"))
        threading.Thread(target=task, daemon=True).start()

    def _update_latency(self, results):
        for r in results:
            host = r.get("host", "")
            ms = r.get("latency_ms")
            if host in self.latency_labels:
                if ms is not None:
                    color = "#4ade80" if ms < 50 else ("#fbbf24" if ms < 150 else "#ef4444")
                    self.latency_labels[host].configure(text=f"{ms} ms", text_color=color)
                else:
                    self.latency_labels[host].configure(text="Timeout", text_color="#ef4444")

    def _update_speed(self, result):
        if "error" in result:
            self.speed_label.configure(text="Error", text_color="#ef4444")
            self.status_label.configure(text=f"Speed test failed: {result['error']}", text_color="#ef4444")
        else:
            mbps = result.get("download_mbps", 0)
            self.speed_label.configure(text=f"{mbps:.1f}")
            elapsed = result.get("elapsed_sec", 0)
            self.status_label.configure(text=f"Downloaded {result.get('total_bytes', 0)//(1024*1024)}MB in {elapsed}s",
                                        text_color="#4ade80")
