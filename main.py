import sys
import os
import subprocess
import threading
import winreg
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox, QDialog
# pyrefly: ignore [missing-import]
from PySide6.QtCore import QObject, Signal, QTimer
# pyrefly: ignore [missing-import]
from PySide6.QtGui import QIcon, QImage, QPainter, QColor, QPixmap, QAction
from engine import HotCornerEngine
from overlay_ui import OverlayUI
from settings_ui import SettingsUI, ProfileManagerDialog, QSS, QSS_LIGHT
from actions import execute_action
from config import init_appdata, APPDATA_DIR, SCRIPTS_DIR, load_settings, save_settings, list_profiles, switch_profile, save_profile, load_profile, effective_is_dark
from i18n import t
from startup import is_startup_enabled, toggle_startup
from version import VERSION
from update_manager import check_update
from download_dialog import DownloadDialog

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

class _BgNotifier(QObject):
    update_found = Signal(object)


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
        
        self._pending_update = None
        self._cleanup_old_setups()
        self._bg_notifier = _BgNotifier()
        self._build_tray_menu()
        self.tray.show()
        self.tray.messageClicked.connect(self._on_notification_clicked)
        
        # Connect engine signals
        self.engine.corner_entered.connect(self.on_corner_entered)
        self.engine.corner_progress.connect(self.on_corner_progress)
        self.engine.corner_triggered.connect(self.on_corner_triggered)
        self.engine.corner_exited.connect(self.on_corner_exited)

        # Background update check at startup (deferred so event loop is running)
        QTimer.singleShot(0, self._run_bg_update_check)
        
    def _build_tray_menu(self):
        self._tray_menu = QMenu()
        lang = self.engine.settings.get("language", "en")

        self._settings_action = QAction(t("tray_settings", lang), self._tray_menu)
        self._settings_action.triggered.connect(self.show_settings)
        self._tray_menu.addAction(self._settings_action)

        self._scripts_action = QAction(t("tray_scripts", lang), self._tray_menu)
        self._scripts_action.triggered.connect(self.open_scripts_dir)
        self._tray_menu.addAction(self._scripts_action)

        self._tray_menu.addSeparator()

        self._startup_action = QAction(t("tray_startup", lang), self._tray_menu)
        self._startup_action.setCheckable(True)
        self._startup_action.setChecked(is_startup_enabled())
        self._startup_action.triggered.connect(self.toggle_startup)
        self._tray_menu.addAction(self._startup_action)

        self._tray_menu.addSeparator()

        # Profiles submenu
        self._profile_menu = QMenu(t("tray_profiles", lang), self._tray_menu)
        self._profile_menu.setObjectName("profileMenu")
        self._populate_profile_menu()
        self._tray_menu.addMenu(self._profile_menu)

        self._manage_profiles_action = QAction(t("tray_manage_profiles", lang), self._tray_menu)
        self._manage_profiles_action.triggered.connect(self.show_profile_manager)
        self._tray_menu.addAction(self._manage_profiles_action)

        self._tray_menu.addSeparator()

        self._version_action = QAction(t("version", lang).format(v=VERSION), self._tray_menu)
        self._version_action.setEnabled(False)
        self._tray_menu.addAction(self._version_action)

        self._update_action = QAction(t("check_updates", lang), self._tray_menu)
        self._update_action.triggered.connect(self._on_check_updates)
        self._tray_menu.addAction(self._update_action)

        self._tray_menu.addSeparator()

        self._quit_action = QAction(t("tray_quit", lang), self._tray_menu)
        self._quit_action.triggered.connect(self.quit_app)
        self._tray_menu.addAction(self._quit_action)

        self.tray.setContextMenu(self._tray_menu)

    def update_tray_menu(self):
        if not hasattr(self, '_tray_menu'):
            self._build_tray_menu()
            return
        lang = self.engine.settings.get("language", "en")
        self._settings_action.setText(t("tray_settings", lang))
        self._scripts_action.setText(t("tray_scripts", lang))
        self._startup_action.setText(t("tray_startup", lang))
        self._startup_action.setChecked(is_startup_enabled())
        self._version_action.setText(t("version", lang).format(v=VERSION))
        update_text = t("check_updates", lang)
        if self._pending_update:
            update_text = f"⬇ {t('update_available', lang).format(latest=self._pending_update['latest'])}"
        self._update_action.setText(update_text)
        self._quit_action.setText(t("tray_quit", lang))
        self._profile_menu.setTitle(t("tray_profiles", lang))
        self._manage_profiles_action.setText(t("tray_manage_profiles", lang))
        self._populate_profile_menu()

    def _populate_profile_menu(self):
        self._profile_menu.clear()
        current = self.engine.settings.get("current_profile", "Default")
        profiles = list_profiles()
        for p in profiles:
            action = QAction(p, self._profile_menu)
            action.setCheckable(True)
            action.setChecked(p == current)
            action.setData(p)
            action.triggered.connect(lambda checked, name=p: self._on_tray_profile_switch(name))
            self._profile_menu.addAction(action)

    def _on_tray_profile_switch(self, name):
        if name == self.engine.settings.get("current_profile", "Default"):
            return
        if switch_profile(name):
            self.engine.settings = load_settings()
            # Update tray
            self._populate_profile_menu()
            self.update_tray_menu()
            self.engine.reload_settings()
            # Animate profile corners
            self._animate_profile_switch(name)

    def _animate_profile_switch(self, name):
        profile_data = load_profile(name)
        if profile_data is None:
            return
        corners = profile_data.get("corners", {})
        enabled = [(cid, c) for cid, c in corners.items() if c.get("enabled", False)]
        for i, (cid, c) in enumerate(enabled):
            color = c.get("color", "#ffffff")
            anim = c.get("animation", "pulse")
            QTimer.singleShot(200 * i, lambda cid=cid, a=anim, cl=color: self.overlay.flash_corner(cid, a, cl))

    def show_settings(self):
        if self.settings_ui:
            self.settings_ui.close()
        self.settings_ui = SettingsUI(self.engine)
        self.settings_ui.setWindowIcon(self.app_icon)
        self.apply_theme()
        self.settings_ui.show()
        self.settings_ui.activateWindow()

    def show_profile_manager(self):
        lang = self.engine.settings.get("language", "en")
        is_dark = effective_is_dark(self.engine.settings)
        dlg = ProfileManagerDialog(self.engine.settings, lang, is_dark, None)
        dlg.setStyleSheet(QSS if is_dark else QSS_LIGHT)
        dlg.exec()
        self.engine.settings = load_settings()
        self._populate_profile_menu()
        self.update_tray_menu()
        self.engine.reload_settings()

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

    def _cleanup_old_setups(self):
        for f in os.listdir(APPDATA_DIR):
            if f.startswith("EasyHotCorners_v") and f.endswith(".exe"):
                path = os.path.join(APPDATA_DIR, f)
                try:
                    os.remove(path)
                except Exception:
                    pass

    def _run_bg_update_check(self):
        def worker(notifier):
            result = check_update()
            if result:
                notifier.update_found.emit(result)
        self._bg_notifier.update_found.connect(self._on_background_update)
        threading.Thread(target=worker, args=(self._bg_notifier,), daemon=True).start()

    def _on_background_update(self, result):
        if not result:
            return
        self._pending_update = result
        self.update_tray_menu()
        lang = self.engine.settings.get("language", "en")
        self.tray.showMessage(
            t("update_available", lang).format(latest=result["latest"]),
            t("update_new_found", lang).format(latest=result["latest"]),
            QSystemTrayIcon.Information,
            5000
        )

    def _on_notification_clicked(self):
        if self._pending_update:
            self._ask_download_and_install(
                self._pending_update["latest"],
                self._pending_update["download_url"]
            )

    def _ask_download_and_install(self, version, url):
        lang = self.engine.settings.get("language", "en")
        reply = QMessageBox.question(
            None,
            t("update_available", lang).format(latest=version),
            t("update_ask_download", lang).format(latest=version, current=VERSION),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self._pending_update = None
        self.update_tray_menu()
        dest = os.path.join(APPDATA_DIR, f"EasyHotCorners_v{version}.exe")
        for f in os.listdir(APPDATA_DIR):
            if f.startswith("EasyHotCorners_v") and f.endswith(".exe") and f != os.path.basename(dest):
                try:
                    os.remove(os.path.join(APPDATA_DIR, f))
                except Exception:
                    pass
        dlg = DownloadDialog(url, dest, version, lang)
        if dlg.exec() != QDialog.Accepted:
            return
        subprocess.Popen([dest], shell=True)
        self.app.quit()

    def _on_check_updates(self):
        lang = self.engine.settings.get("language", "en")
        if self._pending_update:
            self._ask_download_and_install(
                self._pending_update["latest"],
                self._pending_update["download_url"]
            )
            return

        self._update_action.setText(t("check_updates", lang) + " …")
        self._update_action.setEnabled(False)
        result = check_update()
        self._on_check_done(result)

    def _on_check_done(self, result):
        lang = self.engine.settings.get("language", "en")
        title = t("settings_title", lang)
        self._update_action.setEnabled(True)
        self._update_action.setText(t("check_updates", lang))
        if result is None:
            QMessageBox.warning(None, title, t("update_error", lang))
        elif result == {}:
            QMessageBox.information(None, title, t("update_up_to_date", lang))
        else:
            self._ask_download_and_install(result["latest"], result["download_url"])

    def quit_app(self):
        self.app.quit()

    def on_corner_entered(self, corner_id):
        anim = self.engine.settings["corners"][corner_id].get("animation", "pulse")
        color = self.engine.settings["corners"][corner_id].get("color", "#ffffff")
        self.overlay.show_corner(corner_id, anim, color)

    def on_corner_progress(self, corner_id, progress):
        self.overlay.set_progress(progress)

    def on_corner_triggered(self, corner_id):
        corner_cfg = self.engine.settings["corners"].get(corner_id, {})
        action_id = corner_cfg.get("action_id", "none")

        if action_id.startswith("switch_to_profile__"):
            sw_profile = action_id[len("switch_to_profile__"):]
            if sw_profile and sw_profile != self.engine.settings.get("current_profile", "Default"):
                if switch_profile(sw_profile):
                    self.engine.settings = load_settings()
                    self._populate_profile_menu()
                    self.update_tray_menu()
                    self.engine.reload_settings()
                    self._animate_profile_switch(sw_profile)
        elif action_id != "none":
            execute_action(action_id, SCRIPTS_DIR)

        self.overlay.trigger_complete()

    def on_corner_exited(self, corner_id):
        self.overlay.hide_corner()  # Smooth fade-out

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = EasyHotCornersApp()
    app.run()
