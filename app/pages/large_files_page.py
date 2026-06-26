import customtkinter as ctk
import threading
import os
from app.utils.large_files import scan_directory, scan_multiple, COMMON_SCAN_PATHS, format_size

class LargeFilesPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.files = []
        self.scanning = False
        self.build_ui()

    def build_ui(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(self.main, text="Large File Finder", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(self.main, text="Find large files taking up disk space",
                      font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        ctrl = ctk.CTkFrame(self.main, fg_color="transparent")
        ctrl.pack(fill="x", pady=5)

        self.scan_btn = ctk.CTkButton(ctrl, text="Scan Now", command=self.do_scan,
                                       fg_color="#2563eb", height=36, font=ctk.CTkFont(size=13, weight="bold"))
        self.scan_btn.pack(side="left", padx=5)

        size_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        size_frame.pack(side="left", padx=10)

        ctk.CTkLabel(size_frame, text="Min size:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.size_var = ctk.StringVar(value="100")
        size_entry = ctk.CTkEntry(size_frame, width=60, textvariable=self.size_var)
        size_entry.pack(side="left", padx=5)
        ctk.CTkLabel(size_frame, text="MB", font=ctk.CTkFont(size=12)).pack(side="left")

        path_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        path_frame.pack(side="right")

        self.path_var = ctk.StringVar(value=";".join(p for p in COMMON_SCAN_PATHS if p))
        path_entry = ctk.CTkEntry(path_frame, width=250, textvariable=self.path_var, placeholder_text="Paths (semicolon separated)")
        path_entry.pack(side="left", padx=5)

        self.progress_label = ctk.CTkLabel(self.main, text="", font=ctk.CTkFont(size=12), text_color="#94a3b8")
        self.progress_label.pack(fill="x", pady=2)

        header = ctk.CTkFrame(self.main, fg_color="#1a2332")
        header.pack(fill="x")
        for i, t in enumerate(["File Name", "Size", "Location", "Action"]):
            ctk.CTkLabel(header, text=t, font=ctk.CTkFont(size=11, weight="bold"),
                         width=200 if i == 0 else (120 if i == 1 else 300)).pack(side="left", padx=4, pady=4)

        self.list_frame = ctk.CTkScrollableFrame(self.main, fg_color="transparent", height=350)
        self.list_frame.pack(fill="both", expand=True, pady=5)

        ctk.CTkLabel(self.list_frame, text="Click 'Scan Now' to find large files", text_color="#64748b").pack(pady=30)

    def do_scan(self):
        if self.scanning:
            return
        self.scanning = True
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.progress_label.configure(text="Scanning...")
        for w in self.list_frame.winfo_children():
            w.destroy()

        try:
            min_size = int(self.size_var.get())
        except:
            min_size = 100
        paths = [p.strip() for p in self.path_var.get().split(";") if p.strip() and os.path.exists(p.strip())]
        if not paths:
            paths = [p for p in COMMON_SCAN_PATHS if p and os.path.exists(p)]

        def task():
            all_files = []
            scanned = [0]
            def cb(scanned_count, found_count):
                self.after(0, lambda: self.progress_label.configure(
                    text=f"Scanned {scanned_count} files... found {found_count}"))
            for path in paths:
                if not self.scanning:
                    break
                self.after(0, lambda p=path: self.progress_label.configure(text=f"Scanning {p}..."))
                results = scan_directory(path, min_size, cb)
                all_files.extend(results)
            all_files.sort(key=lambda x: x["size"], reverse=True)
            self.files = all_files
            self.after(0, self._display_results)
            self.after(0, lambda: self.scan_btn.configure(state="normal", text="Scan Now"))
            self.after(0, lambda: self.progress_label.configure(text=f"Found {len(all_files)} files over {min_size} MB"))
            self.scanning = False

        threading.Thread(target=task, daemon=True).start()

    def _display_results(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        if not self.files:
            ctk.CTkLabel(self.list_frame, text="No large files found", text_color="#64748b").pack(pady=20)
            return
        for f in self.files[:200]:
            row = ctk.CTkFrame(self.list_frame, fg_color="#1e293b")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f.get("name", ""), font=ctk.CTkFont(size=11), anchor="w", width=200).pack(side="left", padx=4, pady=2)
            ctk.CTkLabel(row, text=format_size(f.get("size", 0)), font=ctk.CTkFont(size=11), width=120).pack(side="left", padx=4)
            dir_path = f.get("dir", "")
            disp = dir_path if len(dir_path) <= 50 else "..." + dir_path[-47:]
            ctk.CTkLabel(row, text=disp, font=ctk.CTkFont(size=10), text_color="#94a3b8", anchor="w", width=300).pack(side="left", padx=4)
            open_btn = ctk.CTkButton(row, text="Open Folder", width=80, height=22,
                                     command=lambda p=dir_path: os.startfile(p),
                                     fg_color="#1f538d", font=ctk.CTkFont(size=10))
            open_btn.pack(side="left", padx=4)
