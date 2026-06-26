import customtkinter as ctk
import threading
from app.utils.bloatware import list_installed_bloatware, uninstall_package, uninstall_all

class BloatwarePage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.packages = []
        self.checkboxes = {}
        self.var_map = {}
        self.build_ui()

    def build_ui(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(self.main, text="Bloatware Uninstaller", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(self.main, text="Remove unwanted pre-installed Windows apps and third-party software",
                      font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        ctrl = ctk.CTkFrame(self.main, fg_color="transparent")
        ctrl.pack(fill="x", pady=5)

        self.refresh_btn = ctk.CTkButton(ctrl, text="Scan Installed", command=self.refresh, fg_color="#475569")
        self.refresh_btn.pack(side="left", padx=5)

        self.select_all_btn = ctk.CTkButton(ctrl, text="Select All", command=self.select_all, fg_color="#1f538d")
        self.select_all_btn.pack(side="left", padx=5)

        self.uninstall_btn = ctk.CTkButton(ctrl, text="Uninstall Selected", command=self.do_uninstall_selected,
                                            fg_color="#dc2626", hover_color="#b91c1c")
        self.uninstall_btn.pack(side="right", padx=5)

        self.batch_uninstall_btn = ctk.CTkButton(ctrl, text="Uninstall All", command=self.do_uninstall_all,
                                                  fg_color="#991b1b", hover_color="#7f1d1d")
        self.batch_uninstall_btn.pack(side="right", padx=5)

        self.status_label = ctk.CTkLabel(self.main, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(fill="x", pady=5)

        self.list_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

    def on_activate(self):
        self.refresh()

    def refresh(self):
        self.refresh_btn.configure(state="disabled", text="Scanning...")
        self.status_label.configure(text="Scanning for bloatware...")
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.checkboxes = {}
        self.var_map = {}
        def task():
            pkgs = list_installed_bloatware()
            self.packages = pkgs
            self.after(0, self._display)
        threading.Thread(target=task, daemon=True).start()

    def _display(self):
        self.refresh_btn.configure(state="normal", text="Scan Installed")
        self.status_label.configure(text=f"Found {len(self.packages)} bloatware packages")
        for w in self.list_frame.winfo_children():
            w.destroy()
        if not self.packages:
            ctk.CTkLabel(self.list_frame, text="No bloatware found or not running as admin", text_color="#64748b").pack(pady=20)
            return
        for pkg in self.packages:
            name = pkg.get("Name", "Unknown")
            row = ctk.CTkFrame(self.list_frame, fg_color="#1e293b")
            row.pack(fill="x", pady=1)
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(row, text=name, variable=var, font=ctk.CTkFont(size=12))
            cb.pack(side="left", padx=10, pady=4)
            self.checkboxes[name] = cb
            self.var_map[name] = var

    def select_all(self):
        all_selected = all(v.get() for v in self.var_map.values())
        for var in self.var_map.values():
            var.set(not all_selected)
        self.select_all_btn.configure(text="Deselect All" if not all_selected else "Select All")

    def do_uninstall_selected(self):
        selected = [name for name, var in self.var_map.items() if var.get()]
        if not selected:
            self.status_label.configure(text="No packages selected", text_color="#fbbf24")
            return
        self.status_label.configure(text=f"Uninstalling {len(selected)} packages...")
        self._uninstall_list(selected)

    def do_uninstall_all(self):
        self.status_label.configure(text=f"Uninstalling all {len(self.packages)} packages...")
        self._uninstall_list([p.get("Name", "") for p in self.packages])

    def _uninstall_list(self, names):
        self.uninstall_btn.configure(state="disabled")
        self.batch_uninstall_btn.configure(state="disabled")
        self.refresh_btn.configure(state="disabled")
        def task():
            for name in names:
                pkg = next((p for p in self.packages if p.get("Name") == name), None)
                if pkg:
                    full = pkg.get("PackageFullName", "")
                    if full:
                        ok = uninstall_package(full)
                        result = "OK" if ok else "Failed"
                    else:
                        result = "No full name"
                else:
                    result = "Not found"
                self.after(0, lambda n=name, r=result: self.status_label.configure(text=f"{n}: {r}"))
            self.after(500, lambda: [self.uninstall_btn.configure(state="normal"),
                                     self.batch_uninstall_btn.configure(state="normal"),
                                     self.refresh_btn.configure(state="normal"),
                                     self.refresh()])
        threading.Thread(target=task, daemon=True).start()
