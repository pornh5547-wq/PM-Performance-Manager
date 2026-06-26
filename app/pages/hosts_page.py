import customtkinter as ctk
import threading
from app.utils.hosts_editor import read_hosts, add_entry, remove_entry, toggle_entry, restore_defaults

class HostsPage(ctk.CTkFrame):
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.entries = []
        self.rows = []
        self.build_ui()

    def build_ui(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(self.main, text="Hosts File Editor", font=ctk.CTkFont(size=22, weight="bold"), anchor="w").pack(fill="x")
        ctk.CTkLabel(self.main, text="Manage the Windows HOSTS file for domain blocking and redirection",
                      font=ctk.CTkFont(size=12), text_color="#94a3b8", anchor="w").pack(fill="x", pady=(0, 10))

        add_frame = ctk.CTkFrame(self.main, corner_radius=10, fg_color="#1e293b")
        add_frame.pack(fill="x", pady=5)

        inner = ctk.CTkFrame(add_frame, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(inner, text="IP:", font=ctk.CTkFont(size=12)).pack(side="left")
        self.ip_entry = ctk.CTkEntry(inner, width=120, placeholder_text="127.0.0.1")
        self.ip_entry.pack(side="left", padx=5)
        self.ip_entry.insert(0, "127.0.0.1")

        ctk.CTkLabel(inner, text="Domain:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(10, 0))
        self.domain_entry = ctk.CTkEntry(inner, width=250, placeholder_text="example.com")
        self.domain_entry.pack(side="left", padx=5)

        ctk.CTkButton(inner, text="Add", command=self.do_add, fg_color="#16a34a", width=70, height=30).pack(side="left", padx=5)

        ctrl = ctk.CTkFrame(self.main, fg_color="transparent")
        ctrl.pack(fill="x", pady=5)

        self.refresh_btn = ctk.CTkButton(ctrl, text="Refresh", command=self.refresh, fg_color="#475569")
        self.refresh_btn.pack(side="left", padx=5)
        self.restore_btn = ctk.CTkButton(ctrl, text="Restore Defaults", command=self.do_restore, fg_color="#dc2626")
        self.restore_btn.pack(side="right", padx=5)

        self.status_label = ctk.CTkLabel(self.main, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(fill="x", pady=5)

        header = ctk.CTkFrame(self.main, fg_color="#1a2332")
        header.pack(fill="x")
        for i, t in enumerate(["IP Address", "Domain", "Status", "Action"]):
            ctk.CTkLabel(header, text=t, font=ctk.CTkFont(size=11, weight="bold"),
                         width=150 if i < 3 else 120).pack(side="left", padx=4, pady=4)

        self.list_frame = ctk.CTkFrame(self.main, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True)

    def on_activate(self):
        self.refresh()

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.rows = []
        def task():
            entries = read_hosts()
            self.entries = entries
            self.after(0, self._display)
        threading.Thread(target=task, daemon=True).start()

    def _display(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.rows = []
        for entry in self.entries:
            if entry.get("comment"):
                continue
            row = ctk.CTkFrame(self.list_frame, fg_color="#1e293b")
            row.pack(fill="x", pady=1)

            ip = entry.get("ip", "")
            domain = entry.get("domain", "")
            enabled = not entry.get("raw", "").startswith('#')

            ctk.CTkLabel(row, text=ip, font=ctk.CTkFont(size=11), width=150).pack(side="left", padx=4, pady=3)
            ctk.CTkLabel(row, text=domain, font=ctk.CTkFont(size=11), width=150).pack(side="left", padx=4, pady=3)

            status_txt = "Active" if enabled else "Disabled"
            status_color = "#4ade80" if enabled else "#ef4444"
            ctk.CTkLabel(row, text=status_txt, font=ctk.CTkFont(size=11), text_color=status_color, width=150).pack(side="left", padx=4, pady=3)

            toggle_btn = ctk.CTkButton(row, text="Toggle", width=60, height=24,
                                       command=lambda e=entry: self.do_toggle(e),
                                       fg_color="#2563eb", font=ctk.CTkFont(size=10))
            toggle_btn.pack(side="left", padx=2)

            del_btn = ctk.CTkButton(row, text="Delete", width=60, height=24,
                                    command=lambda d=domain: self.do_remove(d),
                                    fg_color="#dc2626", font=ctk.CTkFont(size=10))
            del_btn.pack(side="left", padx=2)
            self.rows.append(row)

    def do_add(self):
        ip = self.ip_entry.get().strip()
        domain = self.domain_entry.get().strip()
        if not ip or not domain:
            self.status_label.configure(text="Enter both IP and domain", text_color="#fbbf24")
            return
        if add_entry(ip, domain):
            self.status_label.configure(text=f"Added {ip} {domain}", text_color="#4ade80")
            self.domain_entry.delete(0, "end")
            self.refresh()
        else:
            self.status_label.configure(text="Failed to add entry (try running as admin)", text_color="#ef4444")

    def do_remove(self, domain):
        if remove_entry(domain):
            self.status_label.configure(text=f"Removed {domain}", text_color="#4ade80")
            self.refresh()
        else:
            self.status_label.configure(text="Failed to remove", text_color="#ef4444")

    def do_toggle(self, entry):
        if toggle_entry(entry):
            self.refresh()
        else:
            self.status_label.configure(text="Failed to toggle (try running as admin)", text_color="#ef4444")

    def do_restore(self):
        if restore_defaults():
            self.status_label.configure(text="Hosts file restored to defaults", text_color="#4ade80")
            self.refresh()
        else:
            self.status_label.configure(text="Failed to restore (try running as admin)", text_color="#ef4444")
