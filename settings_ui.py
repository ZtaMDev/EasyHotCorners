# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QCheckBox, QPushButton, QDoubleSpinBox, QGroupBox, QScrollArea, QColorDialog)
# pyrefly: ignore [missing-import]
from PySide6.QtGui import QColor
from config import load_settings, save_settings, SCRIPTS_DIR
from actions import BUILTIN_ACTIONS
from i18n import t
from startup import is_startup_enabled, enable_startup, disable_startup
import os

class ColorButton(QPushButton):
    def __init__(self, color_hex):
        super().__init__()
        self.color_hex = color_hex
        self.setObjectName("colorButton")
        self.setFixedSize(80, 28)
        self.update_style()
        self.clicked.connect(self.choose_color)
        
    def update_style(self):
        # Use a contrasting text color so it's readable on any background
        qc = QColor(self.color_hex)
        luminance = 0.299 * qc.red() + 0.587 * qc.green() + 0.114 * qc.blue()
        text_color = "#000000" if luminance > 128 else "#ffffff"
        # !important-style: use the objectName to beat global stylesheet
        self.setStyleSheet(
            f"QPushButton#colorButton {{"
            f"  background-color: {self.color_hex};"
            f"  color: {text_color};"
            f"  border: 2px solid #888;"
            f"  border-radius: 4px;"
            f"  font-size: 10px;"
            f"}}"
        )
        self.setText(self.color_hex)
        
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.color_hex), self, "Select Color")
        if color.isValid():
            self.color_hex = color.name()
            self.update_style()

class SettingsUI(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.settings = load_settings()
        self.lang = self.settings.get("language", "en")
        
        self.setWindowTitle(t("settings_title", self.lang))
        self.resize(550, 480)
        self.setMinimumHeight(200)
        
        main_layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(t("language", self.lang)))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Español", "es")
        idx = self.lang_combo.findData(self.lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel(t("theme", self.lang)))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["system", "dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "system"))
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)
        
        self.chk_startup = QCheckBox(t("tray_startup", self.lang))
        self.chk_startup.setChecked(is_startup_enabled())
        layout.addWidget(self.chk_startup)
        
        self.corner_widgets = {}
        corners = ["TOP_LEFT", "TOP_RIGHT", "BOTTOM_LEFT", "BOTTOM_RIGHT"]
        ANIMATIONS = ["arc", "corner_bar", "pulse", "fade_box"]
        
        for corner in corners:
            group = QGroupBox(t(corner, self.lang))
            glayout = QVBoxLayout()
            
            corner_data = self.settings["corners"].get(corner, {})
            
            chk_enabled = QCheckBox(t("enable", self.lang))
            chk_enabled.setChecked(corner_data.get("enabled", False))

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
            index = combo_action.findData(curr_action)
            if index >= 0:
                combo_action.setCurrentIndex(index)
            action_layout.addWidget(combo_action)
            
            # Animation
            anim_layout = QHBoxLayout()
            anim_layout.addWidget(QLabel(t("animation", self.lang)))
            combo_anim = QComboBox()
            for anim_id in ANIMATIONS:
                combo_anim.addItem(t(f"anim_{anim_id}", self.lang), anim_id)
            curr_anim = corner_data.get("animation", "pulse")
            index_anim = combo_anim.findData(curr_anim)
            if index_anim >= 0:
                combo_anim.setCurrentIndex(index_anim)
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
            spin_delay = QDoubleSpinBox()
            spin_delay.setRange(0.1, 5.0)
            spin_delay.setSingleStep(0.1)
            spin_delay.setValue(corner_data.get("delay", 0.6))
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
        
        btn_save = QPushButton(t("save_settings", self.lang))
        btn_save.clicked.connect(self.save)
        main_layout.addWidget(btn_save)
        
    def save(self):
        old_lang = self.lang
        self.lang = self.lang_combo.currentData()
        self.settings["language"] = self.lang
        self.settings["theme"] = self.theme_combo.currentText()
        for corner, widgets in self.corner_widgets.items():
            self.settings["corners"][corner] = {
                "enabled": widgets["enabled"].isChecked(),
                "allow_maximized": widgets["allow_maximized"].isChecked(),
                "action_id": widgets["action"].currentData(),
                "animation": widgets["animation"].currentData(),
                "color": widgets["color"].color_hex,
                "delay": widgets["delay"].value()
            }
        save_settings(self.settings)
        self.engine.reload_settings()
        # Apply startup preference
        if self.chk_startup.isChecked():
            enable_startup()
        else:
            disable_startup()
        self.hide()
