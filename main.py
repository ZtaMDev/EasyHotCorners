import sys
import os
import winreg
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
# pyrefly: ignore [missing-import]
from PySide6.QtGui import QIcon, QImage, QPainter, QColor, QPixmap, QAction
from engine import HotCornerEngine
from overlay_ui import OverlayUI
from settings_ui import SettingsUI
from actions import execute_action
from config import init_appdata, SCRIPTS_DIR
from i18n import t
from startup import is_startup_enabled, toggle_startup

def get_icon():
    """Load icon.ico if available (bundled or next to script), else generate it."""
    # PyInstaller bundle path
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    ico_path = os.path.join(base, 'icon.ico')
    if os.path.exists(ico_path):
        return QIcon(ico_path)
    # Fallback: generate programmatically
    return QIcon(create_icon_pixmap())

def is_dark_mode():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except Exception:
        return False

def get_stylesheet(is_dark):
    if is_dark:
        return """
            QWidget { background-color: #2b2b2b; color: #ffffff; }
            QComboBox, QSpinBox, QDoubleSpinBox { background-color: #3b3b3b; border: 1px solid #555; padding: 2px; }
            QPushButton { background-color: #444; border: 1px solid #666; padding: 5px; }
            QPushButton:hover { background-color: #555; }
            QGroupBox { border: 1px solid #555; margin-top: 10px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
            QScrollArea { border: none; }
        """
    else:
        return """
            QWidget { background-color: #f0f0f0; color: #000000; }
            QComboBox, QSpinBox, QDoubleSpinBox { background-color: #ffffff; border: 1px solid #ccc; padding: 2px; }
            QPushButton { background-color: #e0e0e0; border: 1px solid #bbb; padding: 5px; }
            QPushButton:hover { background-color: #d0d0d0; }
            QGroupBox { border: 1px solid #ccc; margin-top: 10px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
            QScrollArea { border: none; }
        """

def create_icon_pixmap():
    image = QImage(64, 64, QImage.Format_RGB32)
    image.fill(QColor("black"))
    painter = QPainter(image)
    painter.fillRect(16, 16, 32, 32, QColor("white"))
    painter.fillRect(24, 24, 16, 16, QColor("black"))
    painter.end()
    return QPixmap.fromImage(image)

class EasyHotCornersApp:
    def __init__(self):
        init_appdata()
        
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Engine
        self.engine = HotCornerEngine()
        self.engine.app_instance = self
        
        self.apply_theme()
        
        # App icon (tray + windows)
        self.app_icon = get_icon()
        self.app.setWindowIcon(self.app_icon)
        
        # Overlays (one per corner, or reuse one)
        self.overlay = OverlayUI()
        
        # Settings UI
        self.settings_ui = None
        
        # Tray Icon
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.app_icon)
        self.tray.setToolTip("EasyHotCorners")
        
        self.update_tray_menu()
        self.tray.show()
        
        # Connect engine signals
        self.engine.corner_entered.connect(self.on_corner_entered)
        self.engine.corner_progress.connect(self.on_corner_progress)
        self.engine.corner_triggered.connect(self.on_corner_triggered)
        self.engine.corner_exited.connect(self.on_corner_exited)
        
    def update_tray_menu(self):
        menu = QMenu()
        lang = self.engine.settings.get("language", "en")
        
        settings_action = QAction(t("tray_settings", lang), menu)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        scripts_action = QAction(t("tray_scripts", lang), menu)
        scripts_action.triggered.connect(self.open_scripts_dir)
        menu.addAction(scripts_action)
        
        menu.addSeparator()
        
        startup_action = QAction(t("tray_startup", lang), menu)
        startup_action.setCheckable(True)
        startup_action.setChecked(is_startup_enabled())
        startup_action.triggered.connect(self.toggle_startup)
        menu.addAction(startup_action)
        self._startup_action = startup_action
        
        menu.addSeparator()
        
        quit_action = QAction(t("tray_quit", lang), menu)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray.setContextMenu(menu)

    def show_settings(self):
        if self.settings_ui:
            self.settings_ui.close()
        self.settings_ui = SettingsUI(self.engine)
        self.settings_ui.setWindowIcon(self.app_icon)
        self.apply_theme()
        self.settings_ui.show()
        self.settings_ui.activateWindow()

    def apply_theme(self):
        theme = self.engine.settings.get("theme", "system")
        if theme == "system":
            is_dark = is_dark_mode()
        else:
            is_dark = (theme == "dark")
        self.app.setStyleSheet(get_stylesheet(is_dark))

    def toggle_startup(self):
        new_state = toggle_startup()
        self._startup_action.setChecked(new_state)

    def open_scripts_dir(self):
        os.startfile(SCRIPTS_DIR)

    def quit_app(self):
        self.app.quit()

    def on_corner_entered(self, corner_id):
        anim = self.engine.settings["corners"][corner_id].get("animation", "pulse")
        color = self.engine.settings["corners"][corner_id].get("color", "#ffffff")
        self.overlay.show_corner(corner_id, anim, color)

    def on_corner_progress(self, corner_id, progress):
        self.overlay.set_progress(progress)

    def on_corner_triggered(self, corner_id):
        action_id = self.engine.settings["corners"][corner_id].get("action_id", "none")
        execute_action(action_id, SCRIPTS_DIR)
        self.overlay.trigger_complete()  # Keep animation visible, then fade out

    def on_corner_exited(self, corner_id):
        self.overlay.hide_corner()  # Smooth fade-out

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = EasyHotCornersApp()
    app.run()
