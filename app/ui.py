import customtkinter as ctk
import threading
import time
from app.config import Config, log
from app.notifications import ToastManager
from app.pages.dashboard import DashboardPage
from app.pages.gaming_mode import GamingModePage
from app.pages.performance_mode import PerformanceModePage
from app.pages.health_check import HealthCheckPage
from app.pages.network_repair import NetworkRepairPage
from app.pages.logs_page import LogsPage
from app.pages.settings_page import SettingsPage
from app.pages.startup_manager import StartupManagerPage
from app.pages.system_info_page import SystemInfoPage
from app.pages.drives_page import DrivesPage
from app.pages.privacy_page import PrivacyPage
from app.pages.services_page import ServicesPage
from app.pages.bloatware_page import BloatwarePage
from app.pages.hosts_page import HostsPage
from app.pages.ram_optimizer_page import RamOptimizerPage
from app.pages.large_files_page import LargeFilesPage
from app.pages.battery_page import BatteryPage
from app.pages.features_page import FeaturesPage
from app.pages.visual_toggles_page import VisualTogglesPage
from app.pages.speed_test_page import SpeedTestPage
from app.utils.scheduler import MaintenanceScheduler
from app.utils.update_checker import UpdateChecker
from app.utils.scan_manager import ScanManager
from app.widgets.scan_overlay import ScanOverlay
from app.plugins.loader import PluginLoader
from app.config import theme_path

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme(theme_path("purple"))

NAV_CATEGORIES = [
    ("\U0001f4ca", "Dashboard", [
        ("dashboard", "Dashboard"),
    ]),
    ("\u2139\ufe0f", "System Info", [
        ("sysinfo", "System Info"),
        ("battery", "Battery"),
        ("drives", "Drives"),
    ]),
    ("\u26a1", "Performance", [
        ("performance", "Performance"),
        ("ram", "RAM Optimizer"),
        ("privacy", "Privacy"),
        ("visual", "Visual Effects"),
        ("bloatware", "Bloatware"),
    ]),
    ("\U0001f3ae", "Gaming", [
        ("gaming", "Gaming Mode"),
    ]),
    ("\U0001f310", "Network", [
        ("network", "Network"),
        ("speedtest", "Speed Test"),
        ("hosts", "Hosts Editor"),
    ]),
    ("\U0001f527", "System Tools", [
        ("health", "Health Check"),
        ("services", "Services"),
        ("features", "Windows Features"),
        ("startup", "Startup Manager"),
        ("largefiles", "Large Files"),
    ]),
    ("\U0001f4cb", "Logs & Settings", [
        ("logs", "Logs"),
        ("settings", "Settings"),
    ]),
]

NAV_ITEMS = []
for _icon, _cat, items in NAV_CATEGORIES:
    for key, label in items:
        NAV_ITEMS.append((key, label))

NAV_BG = "#1a0a2e"
NAV_ACCENT = "#a855f7"
NAV_HOVER = "#2e1065"
NAV_ACTIVE = "#7c3aed"
NAV_TEXT = "#eab308"
CONTENT_BG = "#1a0a2e"
TOPBAR_BG = "#2d0d5e"

COLOR_THEMES = {
    "purple": lambda: theme_path("purple"),
    "dark-blue": lambda: theme_path("purple"),
    "blue": lambda: theme_path("purple"),
    "green": lambda: theme_path("purple"),
}

PAGE_CLASSES = {
    "dashboard": DashboardPage, "privacy": PrivacyPage, "gaming": GamingModePage,
    "performance": PerformanceModePage, "ram": RamOptimizerPage, "health": HealthCheckPage,
    "services": ServicesPage, "network": NetworkRepairPage, "speedtest": SpeedTestPage,
    "hosts": HostsPage, "drives": DrivesPage, "largefiles": LargeFilesPage,
    "startup": StartupManagerPage, "sysinfo": SystemInfoPage, "battery": BatteryPage,
    "features": FeaturesPage, "visual": VisualTogglesPage, "bloatware": BloatwarePage,
    "logs": LogsPage, "settings": SettingsPage,
}

class PerformanceManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.current_page = None
        self.nav_buttons = {}
        self.page_frames = {}
        self.scheduler = MaintenanceScheduler(self.config)
        self.plugin_loader = PluginLoader()
        self.toast = None
        self._slide_after_id = None
        self.scan_manager = ScanManager()
        self.config.scan_manager = self.scan_manager

        self._apply_theme()

        self.title("PM Performance Manager")
        self.geometry("1200x780")
        self.minsize(960, 640)

        self._build_layout()
        self._show_startup_overlay()
        self._bind_events()
        self._post_init()

    def _apply_theme(self):
        mode = self.config.get("appearance_mode", "Dark")
        ctk.set_appearance_mode(mode)
        theme = self.config.get("color_theme", "purple")
        path_fn = COLOR_THEMES.get(theme, COLOR_THEMES["purple"])
        ctk.set_default_color_theme(path_fn())

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=240)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.nav_frame = ctk.CTkFrame(self, fg_color=NAV_BG, corner_radius=0, width=240)
        self.nav_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.nav_frame.grid_propagate(False)

        self.top_bar = ctk.CTkFrame(self, fg_color=TOPBAR_BG, corner_radius=0, height=48)
        self.top_bar.grid(row=0, column=1, sticky="nsew")
        self.top_bar.grid_propagate(False)

        self.content_frame = ctk.CTkFrame(self, fg_color=CONTENT_BG, corner_radius=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        self.content_frame.grid_propagate(False)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self._build_topbar()
        self._build_navbar()
        self._build_pages()

    def _build_topbar(self):
        self.page_title = ctk.CTkLabel(self.top_bar, text="Dashboard", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        self.page_title.pack(side="left", padx=20)

        right = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        right.pack(side="right", padx=15)

        self.update_indicator = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=11))
        self.update_indicator.pack(side="left", padx=5)

        self.status_dot = ctk.CTkLabel(right, text="\u25cf", font=ctk.CTkFont(size=10), text_color="#4ade80")
        self.status_dot.pack(side="left", padx=2)
        self.status_text = ctk.CTkLabel(right, text="Starting...", font=ctk.CTkFont(size=11), text_color="gray")
        self.status_text.pack(side="left", padx=2)

        self.scan_status = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=10), text_color="#475569")
        self.scan_status.pack(side="left", padx=5)

    def _build_navbar(self):
        logo_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent", height=60)
        logo_frame.pack(fill="x", pady=(0, 15))
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="\u26a1 PM", font=ctk.CTkFont(size=24, weight="bold"), text_color=NAV_TEXT).pack(pady=(12, 0))

        nav_container = ctk.CTkScrollableFrame(self.nav_frame, fg_color="transparent")
        nav_container.pack(fill="both", expand=True, padx=8)

        self._cat_items = {}
        self._cat_arrows = {}
        self._expanded_cat = "Dashboard"

        for icon, cat_name, items in NAV_CATEGORIES:
            cat_frame = ctk.CTkFrame(nav_container, fg_color="transparent")
            cat_frame.pack(fill="x", pady=(1, 0))

            hdr_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
            hdr_frame.pack(fill="x")

            arrow = ctk.CTkLabel(hdr_frame, text="\u25b6", font=ctk.CTkFont(size=10), text_color="#a78bfa")
            arrow.pack(side="right", padx=(0, 4))

            hdr = ctk.CTkButton(
                hdr_frame, text=f"{icon}  {cat_name}", anchor="w",
                fg_color="transparent", hover_color=NAV_HOVER,
                text_color="#e2e8f0", font=ctk.CTkFont(size=13, weight="bold"),
                height=36, corner_radius=6,
                command=lambda name=cat_name: self._toggle_cat(name),
            )
            hdr.pack(fill="x", side="left", expand=True)

            self._cat_arrows[cat_name] = arrow
            container = ctk.CTkFrame(cat_frame, fg_color="transparent")
            self._cat_items[cat_name] = container

            for page_key, label in items:
                btn = ctk.CTkButton(
                    container, text=f"    {label}", anchor="w",
                    fg_color="transparent", hover_color=NAV_HOVER,
                    text_color="#a1a1aa", font=ctk.CTkFont(size=12),
                    height=30, corner_radius=6,
                    command=lambda k=page_key: self._switch_page(k),
                )
                btn.pack(fill="x", pady=1, padx=(12, 0))
                self.nav_buttons[page_key] = btn

        dash_ctn = self._cat_items.get("Dashboard")
        if dash_ctn:
            dash_ctn.pack(fill="x", pady=(0, 4))
            arr = self._cat_arrows.get("Dashboard")
            if arr:
                arr.configure(text="\u25bc")

        bottom = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=(0, 12))
        ctk.CTkLabel(bottom, text="v1.0.0", font=ctk.CTkFont(size=10), text_color="#6b21a8").pack()

    def _toggle_cat(self, name):
        if self._expanded_cat == name:
            return
        if self._expanded_cat:
            old = self._cat_items.get(self._expanded_cat)
            if old:
                old.pack_forget()
                arr = self._cat_arrows.get(self._expanded_cat)
                if arr:
                    arr.configure(text="\u25b6")
        container = self._cat_items.get(name)
        if container:
            container.pack(fill="x", pady=(0, 4))
            arr = self._cat_arrows.get(name)
            if arr:
                arr.configure(text="\u25bc")
        self._expanded_cat = name

    def _build_pages(self):
        self._page_titles = {k: v for k, v in NAV_ITEMS}
        for page_key, cls in PAGE_CLASSES.items():
            frame = cls(self.content_frame, self.config, self.scheduler) if page_key == "settings" else cls(self.content_frame, self.config)
            self.page_frames[page_key] = frame

    def _switch_page(self, page_key):
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.configure(fg_color=NAV_ACTIVE, text_color=NAV_TEXT)
            else:
                btn.configure(fg_color="transparent", text_color="#a1a1aa")

        if self.current_page == page_key:
            return

        old = self.page_frames.get(self.current_page) if self.current_page else None
        new_page = self.page_frames.get(page_key)
        if not new_page:
            return

        # Cancel any in-progress slide animation immediately
        if hasattr(self, '_slide_after_id') and self._slide_after_id:
            self.after_cancel(self._slide_after_id)
            self._slide_after_id = None

        # Remove old page from display
        if old:
            if hasattr(old, 'stop_monitoring'):
                old.stop_monitoring()
            old.place_forget()

        if hasattr(new_page, 'start_monitoring'):
            new_page.start_monitoring()
        if hasattr(new_page, 'on_activate'):
            new_page.on_activate()

        self.current_page = page_key
        self.page_title.configure(text=self._page_titles.get(page_key, page_key.capitalize()))

        # Animate new page: slide in from the right
        cw = self.content_frame.winfo_width()
        if cw < 20:
            cw = max(self.content_frame.winfo_reqwidth(), 900)
        ch = self.content_frame.winfo_height()
        if ch < 20:
            ch = 500

        new_page.configure(width=cw, height=ch)
        new_page.place(x=cw, y=0)
        new_page.lift()

        steps = 10
        interval = 15

        def slide(step):
            if not self.winfo_exists():
                return
            if step >= steps:
                new_page.place(x=0, y=0, relwidth=1, relheight=1)
                self._slide_after_id = None
                return
            new_x = int(cw * (steps - step - 1) / steps)
            new_page.place_configure(x=new_x)
            self._slide_after_id = new_page.after(interval, lambda: slide(step + 1))

        slide(0)

    def _bind_events(self):
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _show_startup_overlay(self):
        self._overlay_start_time = time.time()
        self._scan_is_done = False
        self.overlay = ScanOverlay(self, on_complete=self._on_startup_done)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()
        self.scan_manager.start_scan()
        self._poll_scan_and_overlay()

    def _poll_scan_and_overlay(self):
        if not self.overlay:
            return
        if not self.overlay.winfo_exists():
            return
        self._scan_is_done = not self.scan_manager.is_running()
        self.overlay.set_status(self.scan_manager.get_progress())
        if self._scan_is_done:
            self._finish_overlay_if_ready()
        else:
            self.after(200, self._poll_scan_and_overlay)

    def _post_init(self):
        self.toast = ToastManager(self)
        self._switch_page("dashboard")
        self.update()

    def _finish_overlay_if_ready(self):
        elapsed = time.time() - getattr(self, '_overlay_start_time', 0)
        if elapsed < 8.0:
            self.after(int((8.0 - elapsed) * 1000) + 50, self._finish_overlay_if_ready)
            return
        if self.overlay and self.overlay.winfo_exists():
            self.overlay.finish()

    def _on_startup_done(self):
        self.overlay = None
        self.update_idletasks()
        self.after(50, self._post_startup)

    def _post_startup(self):
        self.status_text.configure(text="Ready")
        self._update_scan_status()
        self._finish_init()
        self._schedule_periodic_scan()

    def _schedule_periodic_scan(self):
        self.after(300000, self._do_periodic_scan)

    def _do_periodic_scan(self):
        self.status_text.configure(text="Scanning...")
        log("Starting periodic 5-minute scan")
        self.scan_manager.start_scan()
        self._poll_periodic_scan()
        self.after(300000, self._do_periodic_scan)

    def _poll_periodic_scan(self):
        if self.scan_manager.is_running():
            self.after(500, self._poll_periodic_scan)
        else:
            self.status_text.configure(text="Ready")
            self._update_scan_status()
            log("Periodic scan complete")

    def _update_scan_status(self):
        ago = self.scan_manager.last_scan_ago()
        self.scan_status.configure(text=f"Scan: {ago}")

    def _finish_init(self):
        try:
            if self.config.get("scheduled_maintenance", False):
                self.scheduler.start()
            if self.config.get("plugins_enabled", True):
                loaded = self.plugin_loader.load_all()
                log(f"Loaded {len(loaded)} plugins")
            if self.config.get("check_updates", True):
                UpdateChecker().check(lambda r: self.after(0, lambda: self._on_update_check(r)))
            log("Application started")
        except Exception as e:
            log(f"_finish_init error: {e}")

    def _on_update_check(self, result):
        if result.get("has_update"):
            self.update_indicator.configure(text="Update available", text_color="#f59e0b")

    def show_toast(self, message, type="info", duration=3.0):
        if self.toast:
            self.toast.show(message, type, duration)

    def _on_close(self):
        log("Application shutting down")
        self.scheduler.stop()
        self.plugin_loader.unload_all()
        for frame in self.page_frames.values():
            if hasattr(frame, 'stop_monitoring'):
                frame.stop_monitoring()
        self.destroy()

    def run(self):
        self.mainloop()
