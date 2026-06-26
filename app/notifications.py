import customtkinter as ctk
import threading
import time

TOAST_DURATION = 3.0

class ToastManager:
    def __init__(self, parent):
        self.parent = parent
        self.toasts = []

    def show(self, message, type="info", duration=TOAST_DURATION):
        colors = {"info": "#2563eb", "success": "#16a34a", "warning": "#f59e0b", "error": "#dc2626"}
        bg = colors.get(type, "#2563eb")
        toast = ctk.CTkToplevel(self.parent)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(fg_color=bg)
        toast.geometry("380x50")
        toast.resizable(False, False)
        label = ctk.CTkLabel(toast, text=message, font=ctk.CTkFont(size=13), text_color="white")
        label.pack(fill="both", expand=True, padx=15, pady=5)
        toast.update_idletasks()
        x = self.parent.winfo_x() + self.parent.winfo_width() - 400
        y = self.parent.winfo_y() + self.parent.winfo_height() - 70
        toast.geometry(f"+{x}+{y}")
        toast.focus_force()
        self.toasts.append(toast)
        def close():
            time.sleep(duration)
            try:
                toast.destroy()
            except:
                pass
        threading.Thread(target=close, daemon=True).start()
