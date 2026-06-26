import tkinter as tk
import time

BG = "#050510"
ACCENT = "#3b82f6"
TITLE_CLR = "#f1f5f9"
DOTS_CLR = "#94a3b8"
STATUS_CLR = "#64748b"

class ScanOverlay(tk.Frame):
    def __init__(self, parent, on_complete=None):
        super().__init__(parent, bg=BG)
        self.on_complete = on_complete
        self._done = False
        self._last_frame = 0.0
        self._status_text = "Starting scan..."
        self._phase = 0

        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")

        self._logo = self.canvas.create_text(0, 0, text="\u26a1",
            font=("Segoe UI", 64), fill=ACCENT, anchor="center")
        self._title = self.canvas.create_text(0, 0, text="PM Performance Manager",
            font=("Segoe UI", 20, "bold"), fill=TITLE_CLR, anchor="center")
        self._loading = self.canvas.create_text(0, 0, text="Loading",
            font=("Segoe UI", 13), fill=DOTS_CLR, anchor="center")
        self._status = self.canvas.create_text(0, 0, text=self._status_text,
            font=("Segoe UI", 11), fill=STATUS_CLR, anchor="center")

        self.after(50, self._animate)

    def set_status(self, text):
        self._status_text = text

    def finish(self):
        self._done = True

    def _update(self):
        w, h = self.master.winfo_width(), self.master.winfo_height()
        if w < 50 or h < 50:
            w, h = 1200, 780

        cx, cy = w // 2, h // 2 - 20
        self.canvas.coords(self._logo, cx, cy - 60)
        self.canvas.coords(self._title, cx, cy + 10)
        self.canvas.coords(self._loading, cx, cy + 45)
        self.canvas.coords(self._status, cx, cy + 70)

        self._phase = (self._phase + 1) % 12
        self.canvas.itemconfig(self._loading, text=f"Loading{'.' * (self._phase // 4 + 1)}")
        self.canvas.itemconfig(self._status, text=self._status_text)

        if self._phase % 4 == 0:
            shade = 0.85 + 0.15 * (1 if self._phase % 8 < 4 else 0)
            r = int(59 * shade)
            g = int(130 * shade)
            b = int(246 * shade)
            self.canvas.itemconfig(self._logo, fill=f"#{r:02x}{g:02x}{b:02x}")

    def _animate(self):
        if not self.winfo_exists():
            return
        now = time.monotonic()
        if self._last_frame == 0:
            self._last_frame = now
        dt = now - self._last_frame
        self._last_frame = now
        self._update()
        if self._done:
            self._done = False
            cb = self.on_complete
            self.destroy()
            if cb:
                cb()
            return
        self.after(150, self._animate)
