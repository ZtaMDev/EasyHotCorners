import win32gui
import win32con
import ctypes
import subprocess
import os
import sys

def get_desktop_listview_hwnd():
    hwnd = win32gui.FindWindow("Progman", "Program Manager")
    shelldll = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
    if shelldll:
        listview = win32gui.FindWindowEx(shelldll, 0, "SysListView32", None)
        if listview: return listview

    workerw_hwnds = []
    def enum_windows_callback(h, lParam):
        if win32gui.GetClassName(h) == "WorkerW":
            workerw_hwnds.append(h)
        return True
    win32gui.EnumWindows(enum_windows_callback, 0)
    for worker_hwnd in workerw_hwnds:
        shelldll = win32gui.FindWindowEx(worker_hwnd, 0, "SHELLDLL_DefView", None)
        if shelldll:
            listview = win32gui.FindWindowEx(shelldll, 0, "SysListView32", None)
            if listview: return listview
    return None

def toggle_desktop_icons():
    listview_hwnd = get_desktop_listview_hwnd()
    if listview_hwnd:
        if win32gui.IsWindowVisible(listview_hwnd):
            win32gui.ShowWindow(listview_hwnd, win32con.SW_HIDE)
        else:
            win32gui.ShowWindow(listview_hwnd, win32con.SW_SHOW)

def lock_screen():
    ctypes.windll.user32.LockWorkStation()

def mute_volume():
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        win32api = __import__("win32api")
        win32api.SendMessage(hwnd, win32con.WM_APPCOMMAND, 0, 8 * 65536)

def show_desktop():
    import win32api
    win32api.keybd_event(0x5B, 0, 0, 0)
    win32api.keybd_event(0x44, 0, 0, 0)
    win32api.keybd_event(0x44, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

BUILTIN_ACTIONS = {
    "none": {"t_key": "action_none", "func": lambda: None},
    "toggle_desktop_icons": {"t_key": "action_toggle_icons", "func": toggle_desktop_icons},
    "lock_screen": {"t_key": "action_lock", "func": lock_screen},
    "show_desktop": {"t_key": "action_show_desktop", "func": show_desktop},
    "mute_volume": {"t_key": "action_mute", "func": mute_volume},
}

def execute_action(action_id, scripts_dir):
    if action_id in BUILTIN_ACTIONS:
        BUILTIN_ACTIONS[action_id]["func"]()
    else:
        script_path = os.path.join(scripts_dir, action_id)
        if os.path.exists(script_path) and script_path.endswith('.py'):
            subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NO_WINDOW)
