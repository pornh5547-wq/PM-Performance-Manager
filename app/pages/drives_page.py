import customtkinter as ctk
import threading
import psutil
import os
from app.utils.cleanup import format_size
from app.monitors.system_monitor import SystemMonitor

class DrivesPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.monitor = SystemMonitor()
        self.build_ui()

    def build_ui(self):
        title = ctk.CTkLabel(self, text="Drives & Storage", font=ctk.CTkFont(size=24, weight="bold"), anchor="w")
        title.pack(pady=(20, 10), padx=20, fill="x")

        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.refresh_btn = ctk.CTkButton(main, text="🔄 Refresh", command=self.refresh, fg_color="#1f538d", width=120)
        self.refresh_btn.pack(anchor="w", pady=(0, 10))

        self.drives_container = ctk.CTkFrame(main, fg_color="transparent")
        self.drives_container.pack(fill="x")

        smart_frame = ctk.CTkFrame(main)
        smart_frame.pack(fill="x", pady=(15, 0))

        ctk.CTkLabel(smart_frame, text="Drive Health (SMART)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))
        self.smart_text = ctk.CTkTextbox(smart_frame, height=100, wrap="word", state="disabled")
        self.smart_text.pack(fill="x", padx=15, pady=(0, 10))

    def on_activate(self):
        self.refresh()

    def refresh(self):
        self.refresh_btn.configure(state="disabled", text="Refreshing...")

        def task():
            disks = self.monitor.get_disk_usage()
            smart = self.monitor.get_smart_status()
            self.after(0, lambda: self._display_disks(disks))
            self.after(0, lambda: self._display_smart(smart))
            self.after(0, lambda: self.refresh_btn.configure(state="normal", text="🔄 Refresh"))

        threading.Thread(target=task, daemon=True).start()

    def _display_disks(self, disks):
        for w in self.drives_container.winfo_children():
            w.destroy()

        if not disks:
            ctk.CTkLabel(self.drives_container, text="No drives detected", text_color="gray").pack(pady=20)
            return

        for disk in disks:
            card = ctk.CTkFrame(self.drives_container, corner_radius=10)
            card.pack(fill="x", pady=4)

            total_gb = disk["total"] / (1024**3)
            used_gb = disk["used"] / (1024**3)
            free_gb = disk["free"] / (1024**3)
            percent = disk["percent"]

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=10)

            header = ctk.CTkFrame(inner, fg_color="transparent")
            header.pack(fill="x")
            ctk.CTkLabel(header, text=f"{disk['device']} ({disk['mountpoint']})", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(side="left")
            ctk.CTkLabel(header, text=f"{used_gb:.1f}GB / {total_gb:.1f}GB used", font=ctk.CTkFont(size=12), anchor="w").pack(side="right")

            bar_frame = ctk.CTkFrame(inner, fg_color="transparent")
            bar_frame.pack(fill="x", pady=(8, 0))
            progress = ctk.CTkProgressBar(bar_frame, height=12, corner_radius=6)
            progress.pack(side="left", fill="x", expand=True, padx=(0, 10))
            progress.set(percent / 100)
            if percent > 90:
                progress.configure(progress_color="#dc2626")
            elif percent > 75:
                progress.configure(progress_color="#f59e0b")
            else:
                progress.configure(progress_color="#16a34a")

            ctk.CTkLabel(bar_frame, text=f"{percent:.0f}%", font=ctk.CTkFont(size=12, weight="bold"), width=45, anchor="w").pack(side="right")

            info = ctk.CTkFrame(inner, fg_color="transparent")
            info.pack(fill="x", pady=(5, 0))
            ctk.CTkLabel(info, text=f"Free: {format_size(disk['free'])}", font=ctk.CTkFont(size=11), text_color="gray").pack(side="left", padx=(0, 15))
            ctk.CTkLabel(info, text=f"File System: {disk['fstype']}", font=ctk.CTkFont(size=11), text_color="gray").pack(side="left")

    def _display_smart(self, drives):
        self.smart_text.configure(state="normal")
        self.smart_text.delete("1.0", "end")
        if not drives:
            self.smart_text.insert("1.0", "No SMART data available (admin rights may help)")
        else:
            for drive in drives:
                status = drive.get("status", "Unknown")
                status_icon = "✅" if status.lower() == "ok" else "⚠️"
                self.smart_text.insert("end", f"{status_icon} {drive.get('model', '')} - {drive.get('size_gb', '')}GB - Status: {status} ({drive.get('interface', '')})\n")
        self.smart_text.configure(state="disabled")
