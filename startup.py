"""
startup.py — Manage the Windows registry Run key for EasyHotCorners.
Uses HKCU so no admin rights are required.
"""
import sys
import os
import winreg

APP_NAME = "EasyHotCorners"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _get_exe_path() -> str:
    """Return the path that should be written to the registry."""
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        return sys.executable
    # Running as a plain Python script
    script = os.path.abspath(__file__.replace("startup.py", "main.py"))
    return f'"{sys.executable}" "{script}"'


def is_startup_enabled() -> bool:
    """Return True if the registry Run entry exists for this app."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


def enable_startup() -> None:
    """Add the registry Run entry so the app launches at login."""
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _get_exe_path())
    winreg.CloseKey(key)


def disable_startup() -> None:
    """Remove the registry Run entry."""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass


def toggle_startup() -> bool:
    """Toggle the startup entry and return the new state (True = enabled)."""
    if is_startup_enabled():
        disable_startup()
        return False
    else:
        enable_startup()
        return True
