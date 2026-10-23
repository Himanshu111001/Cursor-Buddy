"""
Windows Autostart manager.
Configures Animated Cursor Buddy to launch automatically on Windows login
via the CurrentVersion\\Run registry key.
"""

import os
import sys
import winreg

REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "AnimatedCursorBuddy"


def _get_launch_command() -> str:
    """Returns the appropriate command to launch silently on boot."""
    if getattr(sys, "frozen", False):
        # Compiled PyInstaller executable
        return f'"{sys.executable}"'
    else:
        # Python script: use pythonw.exe to avoid console window
        python_exe = sys.executable
        pythonw_exe = os.path.join(os.path.dirname(python_exe), "pythonw.exe")
        if not os.path.exists(pythonw_exe):
            pythonw_exe = python_exe

        main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
        return f'"{pythonw_exe}" "{main_py}"'


def is_autostart_enabled() -> bool:
    """Checks if the app is registered in Windows Startup."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"[Autostart] Query error: {e}")
        return False


def set_autostart(enable: bool) -> bool:
    """Enables or disables launch on Windows startup."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_ALL_ACCESS) as key:
            if enable:
                cmd = _get_launch_command()
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                print(f"[Autostart] Enabled: {cmd}")
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    print("[Autostart] Disabled")
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        print(f"[Autostart] Set error: {e}")
        return False
