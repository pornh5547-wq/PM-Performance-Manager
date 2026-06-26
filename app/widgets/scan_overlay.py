import tkinter as tk
import customtkinter as ctk
import math
import time

class ScanOverlay(ctk.CTkFrame):
    def __init__(self, parent, scan_manager, on_complete=None):
        super().__init__(parent, fg_color="#0f172a")
        self.scan_manager = scan_manager
        self.on_complete = on_complete
        self._angle = 0
        self._pulse = 0
        self._pulse_dir = 1
        self._anim_id = None
        self._build()
        self._animate()

    def _build(self):
        self.canvas = tk.Canvas(self, bg="#0f172a", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Configure>", self._on_resize)

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color="#94a3b8")
        self.status_label.place(relx=0.5, rely=0.65, anchor="center")

        self.scan_label = ctk.CTkLabel(self, text="System Scan", font=ctk.CTkFont(size=22, weight="bold"), text_color="#e2e8f0")
        self.scan_label.place(relx=0.5, rely=0.56, anchor="center")

        self.note_label = ctk.CTkLabel(self, text="Caching system data for instant access...",
                                        font=ctk.CTkFont(size=11), text_color="#64748b")
        self.note_label.place(relx=0.5, rely=0.72, anchor="center")

    def _on_resize(self, event):
        self._draw_triangle()

    def _draw_triangle(self):
        self.canvas.delete("tri")
        w = self.canvas.winfo_width() or 400
        h = self.canvas.winfo_height() or 400
        cx, cy = w // 2, h // 2 - 40

        size = min(w, h) * 0.12
        if size < 30:
            size = 30
        if size > 120:
            size = 120

        angle_rad = math.radians(self._angle)
        glow_intensity = 0.5 + 0.5 * math.sin(self._pulse)
        r = int(59 + 196 * glow_intensity)
        g = int(130 + 125 * glow_intensity)
        b = int(246 + 9 * glow_intensity)
        glow_color = f"#{r:02x}{g:02x}{b:02x}"

        points = []
        for i in range(3):
            a = angle_rad + math.radians(i * 120)
            points.extend([cx + size * math.cos(a), cy + size * math.sin(a)])

        outer_glow = []
        glow_size = size * 1.3
        for i in range(3):
            a = angle_rad + math.radians(i * 120)
            outer_glow.extend([cx + glow_size * math.cos(a), cy + glow_size * math.sin(a)])

        self.canvas.create_polygon(outer_glow, fill="", outline=glow_color, width=1,
                                    stipple="gray25", tags="tri")
        self.canvas.create_polygon(points, fill="", outline=glow_color, width=3, tags="tri")

        inner_size = size * 0.5
        inner_points = []
        for i in range(3):
            a = angle_rad + math.radians(180 + i * 120)
            inner_points.extend([cx + inner_size * math.cos(a), cy + inner_size * math.sin(a)])
        self.canvas.create_polygon(inner_points, fill="", outline=glow_color, width=1, tags="tri")

        for i in range(3):
            a = angle_rad + math.radians(i * 120)
            x1 = cx + size * math.cos(a)
            y1 = cy + size * math.sin(a)
            r_size = size * 0.06
            self.canvas.create_oval(x1 - r_size, y1 - r_size, x1 + r_size, y1 + r_size,
                                     fill=glow_color, outline="", tags="tri")

    def _animate(self):
        if not self.winfo_exists():
            return
        self._angle = (self._angle + 2) % 360
        self._pulse += 0.05 * self._pulse_dir
        if self._pulse > math.pi:
            self._pulse_dir = -1
        elif self._pulse < 0:
            self._pulse_dir = 1

        self._draw_triangle()

        progress = self.scan_manager.get_progress()
        self.status_label.configure(text=progress)

        if not self.scan_manager.is_running():
            self.canvas.after(300, self._fade_out)
            return

        self._anim_id = self.after(40, self._animate)

    def _fade_out(self):
        self.destroy()
        if self.on_complete:
            self.on_complete()
