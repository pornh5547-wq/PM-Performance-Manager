import sys
import os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = " ".join(f'"{a}"' if " " in a else a for a in sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    sys.exit()

if __name__ == "__main__":
    if "--no-admin" in sys.argv:
        pass
    elif not is_admin():
        run_as_admin()

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from app.ui import PerformanceManagerApp
    app = PerformanceManagerApp()
    app.run()
