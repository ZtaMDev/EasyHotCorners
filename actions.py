import win32gui
import win32con
import win32api
import ctypes
import subprocess
import os
import sys
import json
import time
import webbrowser

from config import APPDATA_DIR

CUSTOM_ACTIONS_FILE = os.path.join(APPDATA_DIR, "custom_actions.json")

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
        win32api.SendMessage(hwnd, win32con.WM_APPCOMMAND, 0, 8 * 65536)

def show_desktop():
    win32api.keybd_event(0x5B, 0, 0, 0)
    win32api.keybd_event(0x44, 0, 0, 0)
    win32api.keybd_event(0x44, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def show_task_view():
    win32api.keybd_event(0x5B, 0, 0, 0) # Win
    win32api.keybd_event(0x09, 0, 0, 0) # Tab
    win32api.keybd_event(0x09, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def toggle_start_menu():
    win32api.keybd_event(0x5B, 0, 0, 0) # Win
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def open_quick_settings():
    win32api.keybd_event(0x5B, 0, 0, 0) # Win
    win32api.keybd_event(0x41, 0, 0, 0) # A
    win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def open_notifications():
    win32api.keybd_event(0x5B, 0, 0, 0) # Win
    win32api.keybd_event(0x4E, 0, 0, 0) # N
    win32api.keybd_event(0x4E, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def open_widgets():
    win32api.keybd_event(0x5B, 0, 0, 0) # Win
    win32api.keybd_event(0x57, 0, 0, 0) # W
    win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def next_virtual_desktop():
    win32api.keybd_event(0x5B, 0, 0, 0) # Win
    win32api.keybd_event(0x11, 0, 0, 0) # Ctrl
    win32api.keybd_event(0x27, 0, 0, 0) # Right Arrow
    win32api.keybd_event(0x27, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def prev_virtual_desktop():
    win32api.keybd_event(0x5B, 0, 0, 0) # Win
    win32api.keybd_event(0x11, 0, 0, 0) # Ctrl
    win32api.keybd_event(0x25, 0, 0, 0) # Left Arrow
    win32api.keybd_event(0x25, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def open_task_manager():
    win32api.keybd_event(0x11, 0, 0, 0) # Ctrl
    win32api.keybd_event(0x10, 0, 0, 0) # Shift
    win32api.keybd_event(0x1B, 0, 0, 0) # Esc
    win32api.keybd_event(0x1B, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x10, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)

def open_explorer():
    subprocess.Popen(["explorer.exe"], creationflags=subprocess.CREATE_NO_WINDOW)

def sleep_display():
    # Send SC_MONITORPOWER with -1=on, 1=low, 2=off
    ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)

def open_run_dialog():
    win32api.keybd_event(0x5B, 0, 0, 0) # Win
    win32api.keybd_event(0x52, 0, 0, 0) # R
    win32api.keybd_event(0x52, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def snip_sketch():
    win32api.keybd_event(0x5B, 0, 0, 0)  # Win
    win32api.keybd_event(0x10, 0, 0, 0)  # Shift
    win32api.keybd_event(0x53, 0, 0, 0)  # S
    win32api.keybd_event(0x53, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x10, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def open_clipboard_history():
    win32api.keybd_event(0x5B, 0, 0, 0)  # Win
    win32api.keybd_event(0x56, 0, 0, 0)  # V
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def open_emoji_panel():
    win32api.keybd_event(0x5B, 0, 0, 0)  # Win
    win32api.keybd_event(0xBE, 0, 0, 0)  # . (period)
    win32api.keybd_event(0xBE, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)

def open_magnifier():
    subprocess.Popen(["magnify.exe"], creationflags=subprocess.CREATE_NO_WINDOW)

def open_narrator():
    subprocess.Popen(["narrator.exe"], creationflags=subprocess.CREATE_NO_WINDOW)

def volume_up():
    VK_VOLUME_UP = 0xAF
    win32api.keybd_event(VK_VOLUME_UP, 0, 0, 0)
    win32api.keybd_event(VK_VOLUME_UP, 0, win32con.KEYEVENTF_KEYUP, 0)

def volume_down():
    VK_VOLUME_DOWN = 0xAE
    win32api.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
    win32api.keybd_event(VK_VOLUME_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)

def media_play_pause():
    VK_MEDIA_PLAY_PAUSE = 0xB3
    win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
    win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)

def media_next():
    VK_MEDIA_NEXT_TRACK = 0xB0
    win32api.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 0, 0)
    win32api.keybd_event(VK_MEDIA_NEXT_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)

def media_prev():
    VK_MEDIA_PREV_TRACK = 0xB1
    win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, 0, 0)
    win32api.keybd_event(VK_MEDIA_PREV_TRACK, 0, win32con.KEYEVENTF_KEYUP, 0)

BUILTIN_ACTIONS = {
    "none":                {"t_key": "action_none",             "func": lambda: None},
    "show_task_view":      {"t_key": "action_task_view",        "func": show_task_view},
    "show_desktop":        {"t_key": "action_show_desktop",     "func": show_desktop},
    "toggle_start_menu":   {"t_key": "action_start_menu",       "func": toggle_start_menu},
    "toggle_desktop_icons":{"t_key": "action_toggle_icons",     "func": toggle_desktop_icons},
    "lock_screen":         {"t_key": "action_lock",             "func": lock_screen},
    "open_quick_settings": {"t_key": "action_quick_settings",   "func": open_quick_settings},
    "open_notifications":  {"t_key": "action_notifications",    "func": open_notifications},
    "open_widgets":        {"t_key": "action_widgets",          "func": open_widgets},
    "next_desktop":        {"t_key": "action_next_desktop",     "func": next_virtual_desktop},
    "prev_desktop":        {"t_key": "action_prev_desktop",     "func": prev_virtual_desktop},
    "open_task_manager":   {"t_key": "action_task_manager",     "func": open_task_manager},
    "open_explorer":       {"t_key": "action_explorer",         "func": open_explorer},
    "sleep_display":       {"t_key": "action_sleep_display",    "func": sleep_display},
    "open_run_dialog":     {"t_key": "action_run_dialog",       "func": open_run_dialog},
    "snip_sketch":         {"t_key": "action_snip_sketch",      "func": snip_sketch},
    "open_clipboard":      {"t_key": "action_clipboard",        "func": open_clipboard_history},
    "open_emoji":          {"t_key": "action_emoji",            "func": open_emoji_panel},
    "mute_volume":         {"t_key": "action_mute",             "func": mute_volume},
    "volume_up":           {"t_key": "action_volume_up",        "func": volume_up},
    "volume_down":         {"t_key": "action_volume_down",      "func": volume_down},
    "media_play_pause":    {"t_key": "action_media_play",       "func": media_play_pause},
    "media_next":          {"t_key": "action_media_next",       "func": media_next},
    "media_prev":          {"t_key": "action_media_prev",       "func": media_prev},
}

def load_custom_actions():
    """Load custom actions from JSON file."""
    if os.path.exists(CUSTOM_ACTIONS_FILE):
        try:
            with open(CUSTOM_ACTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_custom_actions(actions_dict):
    """Save custom actions to JSON file."""
    os.makedirs(APPDATA_DIR, exist_ok=True)
    with open(CUSTOM_ACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(actions_dict, f, indent=4)

def execute_custom_action(action_data):
    """Execute a custom built action."""
    action_type = action_data.get("type", "")
    if action_type == "launch":
        path = action_data.get("path", "")
        if path and os.path.exists(path):
            subprocess.Popen([path], creationflags=subprocess.CREATE_NO_WINDOW)
    elif action_type == "url":
        url = action_data.get("url", "")
        if url:
            webbrowser.open(url)
    elif action_type == "hotkey":
        mods = action_data.get("modifiers", [])
        key_vk = action_data.get("key_vk", 0)
        if not key_vk:
            return
        # Press modifiers
        mod_map = {"win": 0x5B, "ctrl": 0x11, "shift": 0x10, "alt": 0x12}
        pressed = []
        for mod in mods:
            vk = mod_map.get(mod)
            if vk:
                win32api.keybd_event(vk, 0, 0, 0)
                pressed.append(vk)
        time.sleep(0.05)
        win32api.keybd_event(key_vk, 0, 0, 0)
        win32api.keybd_event(key_vk, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        for vk in reversed(pressed):
            win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)

CUSTOM_ACTION_PREFIX = "__custom__:"

def execute_action(action_id, scripts_dir):
    if action_id in BUILTIN_ACTIONS:
        BUILTIN_ACTIONS[action_id]["func"]()
    elif action_id.startswith(CUSTOM_ACTION_PREFIX):
        name = action_id[len(CUSTOM_ACTION_PREFIX):]
        custom_actions = load_custom_actions()
        if name in custom_actions:
            execute_custom_action(custom_actions[name])
    else:
        script_path = os.path.join(scripts_dir, action_id)
        if os.path.exists(script_path) and script_path.endswith('.py'):
            python_exe = "python" if getattr(sys, 'frozen', False) else sys.executable
            try:
                subprocess.Popen([python_exe, script_path], creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as e:
                print(f"Failed to execute script {script_path}: {e}")
