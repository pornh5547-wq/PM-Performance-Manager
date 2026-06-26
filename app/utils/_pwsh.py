import subprocess

SI = subprocess.STARTUPINFO()
SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW
SI.wShowWindow = subprocess.SW_HIDE
NO_WINDOW = subprocess.CREATE_NO_WINDOW

def run(cmd, timeout=30, shell=False):
    try:
        if shell:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                                  startupinfo=SI, creationflags=NO_WINDOW, shell=True)
        return subprocess.run(['powershell', '-NoProfile', '-Command', cmd],
                              capture_output=True, text=True, timeout=timeout,
                              startupinfo=SI, creationflags=NO_WINDOW)
    except:
        return None

def run_admin(cmd, timeout=60):
    try:
        full = f'Start-Process PowerShell -Verb RunAs -WindowStyle Hidden -ArgumentList \'-NoProfile -ExecutionPolicy Bypass -Command "{cmd}"\''
        return subprocess.run(['powershell', '-NoProfile', '-Command', full],
                              capture_output=True, text=True, timeout=timeout,
                              startupinfo=SI, creationflags=NO_WINDOW)
    except:
        return None
