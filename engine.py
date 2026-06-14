import time
import win32api
import win32con
import win32gui
# pyrefly: ignore [missing-import]
from PySide6.QtCore import QObject, QTimer, Signal
from config import load_settings

def is_fullscreen_or_maximized_active():
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd: return False
    class_name = win32gui.GetClassName(hwnd)
    if class_name in ("Progman", "WorkerW", "Qt5QWindowIcon", "Qt6QWindowIcon"):
        return False
    rect = win32gui.GetWindowRect(hwnd)
    win_w = rect[2] - rect[0]
    win_h = rect[3] - rect[1]
    screen_w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screen_h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    if win_w >= screen_w and win_h >= screen_h:
        return True
    try:
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] == win32con.SW_SHOWMAXIMIZED:
            return True
    except: pass
    return False

class HotCornerEngine(QObject):
    # Emit (corner_id) when entered, (corner_id, progress) while in it, (corner_id) when triggered, (corner_id) when exited
    corner_entered = Signal(str)
    corner_progress = Signal(str, float)
    corner_triggered = Signal(str)
    corner_exited = Signal(str)

    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.screen_w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        self.active_corner = None
        self.timer_val = 0.0
        self.last_toggle_time = 0
        
        # We run check at ~60fps (16ms)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_loop)
        self.timer.start(16)

    def reload_settings(self):
        self.settings = load_settings()

    def check_loop(self):
        x, y = win32api.GetCursorPos()
        
        corners = self.settings.get("corners", {})
        
        current_corner = None
        if x <= 0 and y <= 0: current_corner = "TOP_LEFT"
        elif x >= self.screen_w - 1 and y <= 0: current_corner = "TOP_RIGHT"
        elif x <= 0 and y >= self.screen_h - 1: current_corner = "BOTTOM_LEFT"
        elif x >= self.screen_w - 1 and y >= self.screen_h - 1: current_corner = "BOTTOM_RIGHT"

        # Check if corner is enabled
        if current_corner and not corners.get(current_corner, {}).get("enabled", False):
            current_corner = None

        if current_corner:
            # We are in a corner
            if self.active_corner != current_corner:
                # Switched to a new corner
                if self.active_corner:
                    self.corner_exited.emit(self.active_corner)
                self.active_corner = current_corner
                self.timer_val = 0.0
                
                # Prevent triggers if full screen is active or cooldown
                if time.time() - self.last_toggle_time > 1.5 and not is_fullscreen_or_maximized_active():
                    self.corner_entered.emit(self.active_corner)
                else:
                    self.active_corner = None # Blocked
                    
            if self.active_corner:
                delay = float(corners[self.active_corner].get("delay", 0.6))
                self.timer_val += 0.016 # 16ms
                progress = min(self.timer_val / delay, 1.0)
                
                self.corner_progress.emit(self.active_corner, progress)
                
                if progress >= 1.0:
                    self.corner_triggered.emit(self.active_corner)
                    self.last_toggle_time = time.time()
                    self.corner_exited.emit(self.active_corner)
                    self.active_corner = None
                    self.timer_val = 0.0
        else:
            # Exited corner
            if self.active_corner:
                self.corner_exited.emit(self.active_corner)
                self.active_corner = None
                self.timer_val = 0.0
