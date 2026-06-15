# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QCheckBox, QPushButton, QDoubleSpinBox, QSpinBox, QGroupBox, QScrollArea, QColorDialog, QFrame, QSizePolicy)
# pyrefly: ignore [missing-import]
from PySide6.QtGui import QColor, QFont
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
# pyrefly: ignore [missing-import]
from PySide6.QtSvgWidgets import QSvgWidget
from config import load_settings, save_settings, SCRIPTS_DIR
from actions import BUILTIN_ACTIONS
from i18n import t
from startup import is_startup_enabled, enable_startup, disable_startup
import os

GLOBAL_QSS = """
QWidget {
    background-color: #121218;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background: #1a1a24;
    width: 12px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #333344;
    min-height: 20px;
    border-radius: 6px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background: #555577;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QGroupBox {
    border: 1px solid #333344;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 15px;
    background-color: #1a1a24;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 10px;
    color: #a78bfa;
    font-weight: bold;
}
QPushButton {
    background-color: #2a2a3a;
    border: 1px solid #444455;
    border-radius: 5px;
    padding: 8px 16px;
    color: #ffffff;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #a78bfa;
    color: #050508;
    border-color: #a78bfa;
}
QPushButton:pressed {
    background-color: #8b5cf6;
}
QPushButton#applyBtn {
    background-color: transparent;
    border: 1px solid #a78bfa;
    color: #a78bfa;
}
QPushButton#applyBtn:hover {
    background-color: rgba(167, 139, 250, 0.1);
}
QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #0d0d14;
    border: 1px solid #333344;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
}
QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #a78bfa;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #a78bfa;
    margin-right: 8px;
}
QCheckBox {
    spacing: 10px;
    font-size: 10pt;
    color: #e0e0e0;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 2px solid #333344;
    background-color: #0d0d14;
}
QCheckBox::indicator:hover {
    border-color: #a78bfa;
}
QCheckBox::indicator:checked {
    background-color: #a78bfa;
    border-color: #a78bfa;
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23121218' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>");
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #333344;
    border-bottom: 1px solid #333344;
    border-top-right-radius: 3px;
    background-color: #1a1a24;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #333344;
    border-bottom-right-radius: 3px;
    background-color: #1a1a24;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover, QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #a78bfa;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    width: 0; height: 0;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-bottom: 4px solid #a78bfa;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    width: 0; height: 0;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-top: 4px solid #a78bfa;
}
"""

SVG_MONITOR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
    <line x1="8" y1="21" x2="16" y2="21"></line>
    <line x1="12" y1="17" x2="12" y2="21"></line>
</svg>"""

class ColorButton(QPushButton):
    def __init__(self, color_hex):
        super().__init__()
        self.color_hex = color_hex
        self.setObjectName("colorButton")
        self.setFixedSize(80, 28)
        self.update_style()
        self.clicked.connect(self.choose_color)
        
    def update_style(self):
        qc = QColor(self.color_hex)
        luminance = 0.299 * qc.red() + 0.587 * qc.green() + 0.114 * qc.blue()
        text_color = "#000000" if luminance > 128 else "#ffffff"
        self.setStyleSheet(
            f"QPushButton#colorButton {{"
            f"  background-color: {self.color_hex};"
            f"  color: {text_color};"
            f"  border: 1px solid #555;"
            f"  border-radius: 4px;"
            f"  font-size: 8pt;"
            f"}}"
        )
        self.setText(self.color_hex)
        
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.color_hex), self, "Select Color")
        if color.isValid():
            self.color_hex = color.name()
            self.update_style()

def create_info_label(tooltip_text):
    lbl = QLabel("?")
    lbl.setFixedSize(16, 16)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet("background: #333344; color: #a78bfa; border-radius: 8px; font-weight: bold; font-size: 8pt;")
    lbl.setToolTip(tooltip_text)
    return lbl

class SettingsUI(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.settings = load_settings()
        self.lang = self.settings.get("language", "en")
        
        self.setWindowTitle(t("settings_title", self.lang))
        self.resize(600, 650)
        self.setMinimumHeight(300)
        self.setStyleSheet(GLOBAL_QSS)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header Graphic
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        svg_widget = QSvgWidget()
        svg_widget.load(SVG_MONITOR.encode('utf-8'))
        svg_widget.setFixedSize(64, 64)
        header_layout.addWidget(svg_widget)
        layout.addLayout(header_layout)
        
        # General Settings
        gen_group = QGroupBox("General")
        gen_layout = QVBoxLayout(gen_group)
        
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(t("language", self.lang)))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Español", "es")
        idx = self.lang_combo.findData(self.lang)
        if idx >= 0: self.lang_combo.setCurrentIndex(idx)
        lang_layout.addWidget(self.lang_combo)
        gen_layout.addLayout(lang_layout)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel(t("theme", self.lang)))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["system", "dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "system"))
        theme_layout.addWidget(self.theme_combo)
        gen_layout.addLayout(theme_layout)
        
        self.chk_startup = QCheckBox(t("tray_startup", self.lang))
        self.chk_startup.setChecked(is_startup_enabled())
        gen_layout.addWidget(self.chk_startup)
        
        layout.addWidget(gen_group)
        
        # Advanced Options
        self.btn_advanced = QPushButton(t("advanced_options", self.lang))
        self.btn_advanced.setCheckable(True)
        self.btn_advanced.setStyleSheet("QPushButton { background-color: transparent; border: 1px dashed #555; color: #aaa; } QPushButton:checked { border-color: #a78bfa; color: #a78bfa; }")
        self.btn_advanced.toggled.connect(self.toggle_advanced)
        layout.addWidget(self.btn_advanced)
        
        self.advanced_container = QWidget()
        adv_layout = QVBoxLayout(self.advanced_container)
        adv_layout.setContentsMargins(0, 0, 0, 0)
        
        # Radius
        rad_layout = QHBoxLayout()
        rad_layout.addWidget(QLabel(t("radius", self.lang)))
        rad_layout.addWidget(create_info_label(t("info_radius", self.lang)))
        rad_layout.addStretch()
        self.spin_radius = QSpinBox()
        self.spin_radius.setRange(1, 100)
        self.spin_radius.setValue(self.settings.get("radius", 10))
        rad_layout.addWidget(self.spin_radius)
        adv_layout.addLayout(rad_layout)
        
        # Polling
        poll_layout = QHBoxLayout()
        poll_layout.addWidget(QLabel(t("polling_interval", self.lang)))
        poll_layout.addWidget(create_info_label(t("info_polling", self.lang)))
        poll_layout.addStretch()
        self.spin_polling = QSpinBox()
        self.spin_polling.setRange(1, 1000)
        self.spin_polling.setValue(self.settings.get("polling_interval", 16))
        poll_layout.addWidget(self.spin_polling)
        adv_layout.addLayout(poll_layout)
        
        # Multi monitor
        mmon_layout = QHBoxLayout()
        self.chk_multi_monitor = QCheckBox(t("multi_monitor", self.lang))
        self.chk_multi_monitor.setChecked(self.settings.get("multi_monitor", True))
        mmon_layout.addWidget(self.chk_multi_monitor)
        mmon_layout.addWidget(create_info_label(t("info_multi_monitor", self.lang)))
        mmon_layout.addStretch()
        adv_layout.addLayout(mmon_layout)
        
        self.advanced_container.setVisible(False)
        layout.addWidget(self.advanced_container)
        
        # Corners
        self.corner_widgets = {}
        corners = ["TOP_LEFT", "TOP_RIGHT", "BOTTOM_LEFT", "BOTTOM_RIGHT"]
        ANIMATIONS = ["arc", "corner_bar", "pulse", "fade_box"]
        
        for corner in corners:
            group = QGroupBox(t(corner, self.lang))
            glayout = QVBoxLayout()
            
            corner_data = self.settings["corners"].get(corner, {})
            
            chk_enabled = QCheckBox(t("enable", self.lang))
            chk_enabled.setChecked(corner_data.get("enabled", False))
            chk_enabled.setStyleSheet("font-weight: bold; color: #a78bfa;")

            chk_maximized = QCheckBox(t("allow_maximized", self.lang))
            chk_maximized.setChecked(corner_data.get("allow_maximized", False))
            
            # Action
            action_layout = QHBoxLayout()
            action_layout.addWidget(QLabel(t("action", self.lang)))
            combo_action = QComboBox()
            for action_id, info in BUILTIN_ACTIONS.items():
                combo_action.addItem(t(info["t_key"], self.lang), action_id)
            if os.path.exists(SCRIPTS_DIR):
                for f in os.listdir(SCRIPTS_DIR):
                    if f.endswith('.py'):
                        combo_action.addItem(f"{t('script_prefix', self.lang)}{f}", f)
            curr_action = corner_data.get("action_id", "none")
            idx = combo_action.findData(curr_action)
            if idx >= 0: combo_action.setCurrentIndex(idx)
            action_layout.addWidget(combo_action)
            
            # Animation
            anim_layout = QHBoxLayout()
            anim_layout.addWidget(QLabel(t("animation", self.lang)))
            combo_anim = QComboBox()
            for anim_id in ANIMATIONS:
                combo_anim.addItem(t(f"anim_{anim_id}", self.lang), anim_id)
            curr_anim = corner_data.get("animation", "pulse")
            idx_anim = combo_anim.findData(curr_anim)
            if idx_anim >= 0: combo_anim.setCurrentIndex(idx_anim)
            anim_layout.addWidget(combo_anim)
            
            # Color
            color_layout = QHBoxLayout()
            color_layout.addWidget(QLabel(t("color", self.lang)))
            btn_color = ColorButton(corner_data.get("color", "#ffffff"))
            color_layout.addWidget(btn_color)
            color_layout.addStretch()
            
            # Delay
            delay_layout = QHBoxLayout()
            delay_layout.addWidget(QLabel(t("delay", self.lang)))
            delay_layout.addWidget(create_info_label(t("info_delay", self.lang)))
            delay_layout.addStretch()
            spin_delay = QDoubleSpinBox()
            spin_delay.setRange(0.1, 5.0)
            spin_delay.setSingleStep(0.1)
            spin_delay.setValue(corner_data.get("delay", 0.4))
            delay_layout.addWidget(spin_delay)
            
            glayout.addWidget(chk_enabled)
            glayout.addWidget(chk_maximized)
            glayout.addLayout(action_layout)
            glayout.addLayout(anim_layout)
            glayout.addLayout(color_layout)
            glayout.addLayout(delay_layout)
            group.setLayout(glayout)
            
            layout.addWidget(group)
            
            self.corner_widgets[corner] = {
                "enabled": chk_enabled,
                "allow_maximized": chk_maximized,
                "action": combo_action,
                "animation": combo_anim,
                "color": btn_color,
                "delay": spin_delay
            }
            
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # Bottom Buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(20, 10, 20, 20)
        
        btn_apply = QPushButton(t("apply", self.lang))
        btn_apply.setObjectName("applyBtn")
        btn_apply.clicked.connect(self.apply_changes)
        
        btn_save = QPushButton(t("save_settings", self.lang))
        btn_save.clicked.connect(self.save_and_close)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_apply)
        bottom_layout.addWidget(btn_save)
        
        main_layout.addLayout(bottom_layout)
        
    def toggle_advanced(self, checked):
        self.advanced_container.setVisible(checked)

    def gather_settings(self):
        self.lang = self.lang_combo.currentData()
        self.settings["language"] = self.lang
        self.settings["theme"] = self.theme_combo.currentText()
        self.settings["radius"] = self.spin_radius.value()
        self.settings["polling_interval"] = self.spin_polling.value()
        self.settings["multi_monitor"] = self.chk_multi_monitor.isChecked()
        
        for corner, widgets in self.corner_widgets.items():
            self.settings["corners"][corner] = {
                "enabled": widgets["enabled"].isChecked(),
                "allow_maximized": widgets["allow_maximized"].isChecked(),
                "action_id": widgets["action"].currentData(),
                "animation": widgets["animation"].currentData(),
                "color": widgets["color"].color_hex,
                "delay": widgets["delay"].value()
            }
            
    def apply_changes(self):
        self.gather_settings()
        save_settings(self.settings)
        self.engine.reload_settings()
        
        if self.chk_startup.isChecked():
            enable_startup()
        else:
            disable_startup()
            
        if hasattr(self.engine, 'app_instance'):
            self.engine.app_instance.update_tray_menu()
            
    def save_and_close(self):
        self.apply_changes()
        self.hide()
