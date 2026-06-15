# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox,
    QPushButton, QDoubleSpinBox, QSpinBox, QScrollArea, QColorDialog,
    QFrame, QSizePolicy, QStackedWidget, QGroupBox
)
# pyrefly: ignore [missing-import]
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QLinearGradient
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt, Signal, QSize
from config import load_settings, save_settings, SCRIPTS_DIR
from actions import BUILTIN_ACTIONS, load_custom_actions, CUSTOM_ACTION_PREFIX
from i18n import t
from startup import is_startup_enabled, enable_startup, disable_startup
from action_builder import ActionBuilderDialog
import os

CORNERS = ["TOP_LEFT", "TOP_RIGHT", "BOTTOM_LEFT", "BOTTOM_RIGHT"]
ANIMATIONS = ["arc", "corner_bar", "pulse", "fade_box"]

# ─────────────────────────────────────────────
# STYLESHEET
# ─────────────────────────────────────────────
QSS = """
QWidget {
    background-color: #0f0f17;
    color: #d4d4e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}
QWidget:disabled {
    color: #555577;
}
/* ── Scroll Areas ── */
QScrollArea {
    border: none;
    background-color: transparent;
}
/* ── Sidebar ── */
#sidebar {
    background-color: #0a0a12;
    border-right: 1px solid #1e1e2e;
}
#sidebarContent {
    background-color: #0a0a12;
}
/* ── Right panel ── */
#rightPanel {
    background-color: #0f0f17;
}
/* ── Section labels ── */
QLabel#sectionLabel {
    color: #7c7c9a;
    font-size: 8pt;
    font-weight: bold;
    letter-spacing: 1px;
    padding-bottom: 2px;
}
QLabel#sectionLabel:disabled {
    color: #3f3f56;
}
/* ── Corner areas are painted, not styled via QSS ── */
/* ── ComboBox ── */
QComboBox {
    background-color: #16161f;
    border: 1px solid #2a2a3e;
    border-radius: 6px;
    padding: 6px 10px;
    color: #d4d4e0;
    min-height: 28px;
}
QComboBox:hover { border-color: #a78bfa; }
QComboBox:disabled {
    background-color: #0d0d14;
    border-color: #1a1a26;
    color: #555577;
}
QComboBox::drop-down { border: none; width: 26px; }
QComboBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #a78bfa;
    margin-right: 8px;
}
QComboBox::down-arrow:disabled {
    border-top-color: #3f3f56;
}
QComboBox QAbstractItemView {
    background-color: #16161f;
    border: 1px solid #2a2a3e;
    selection-background-color: #a78bfa;
    selection-color: #0f0f17;
    outline: none;
}
/* ── SpinBox ── */
QSpinBox, QDoubleSpinBox {
    background-color: #16161f;
    border: 1px solid #2a2a3e;
    border-radius: 6px;
    padding: 5px 8px;
    color: #d4d4e0;
    min-height: 28px;
}
QSpinBox:hover, QDoubleSpinBox:hover { border-color: #a78bfa; }
QSpinBox:disabled, QDoubleSpinBox:disabled {
    background-color: #0d0d14;
    border-color: #1a1a26;
    color: #555577;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border; subcontrol-position: top right;
    width: 18px; border-left: 1px solid #2a2a3e;
    border-top-right-radius: 5px; background-color: #1e1e2e;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border; subcontrol-position: bottom right;
    width: 18px; border-left: 1px solid #2a2a3e;
    border-bottom-right-radius: 5px; background-color: #1e1e2e;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #a78bfa;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-bottom: 4px solid #a78bfa; width: 0; height: 0;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-top: 4px solid #a78bfa; width: 0; height: 0;
}
/* ── Checkbox ── */
QCheckBox { spacing: 10px; color: #d4d4e0; }
QCheckBox:disabled {
    color: #555577;
}
QCheckBox::indicator {
    width: 18px; height: 18px; border-radius: 5px;
    border: 2px solid #2a2a3e; background-color: #16161f;
}
QCheckBox::indicator:hover { border-color: #a78bfa; }
QCheckBox::indicator:disabled {
    border-color: #1a1a26;
    background-color: #0d0d14;
}
QCheckBox::indicator:checked {
    background-color: #a78bfa; border-color: #a78bfa;
}
QCheckBox::indicator:checked:disabled {
    background-color: #3f3f56; border-color: #3f3f56;
}
QCheckBox#enableCheck {
    font-size: 11pt;
    font-weight: bold;
    color: #e0e0f0;
}
QCheckBox#enableCheck:disabled {
    color: #555577;
}
QCheckBox#enableCheck::indicator { width: 20px; height: 20px; }
/* ── Buttons ── */
QPushButton {
    background-color: #1e1e2e;
    border: 1px solid #2a2a3e;
    border-radius: 6px;
    padding: 8px 18px;
    color: #d4d4e0;
    font-weight: bold;
    min-height: 32px;
}
QPushButton:hover {
    background-color: #a78bfa;
    color: #ffffff;
    border-color: #a78bfa;
}
QPushButton:pressed { background-color: #8b5cf6; color: #fff; }
QPushButton:disabled {
    background-color: #0d0d14;
    border-color: #1a1a26;
    color: #555577;
}
QPushButton#primaryBtn {
    background-color: #a78bfa;
    color: #ffffff;
    border-color: #a78bfa;
}
QPushButton#primaryBtn:hover { background-color: #8b5cf6; color: #fff; }
QPushButton#primaryBtn:disabled {
    background-color: #3f3f56;
    border-color: #3f3f56;
    color: #77778c;
}
QPushButton#ghostBtn {
    background-color: transparent;
    border-color: #a78bfa;
    color: #a78bfa;
}
QPushButton#ghostBtn:hover {
    background-color: #a78bfa;
    color: #ffffff;
    border-color: #a78bfa;
}
QPushButton#ghostBtn:disabled {
    border-color: #2a2a3e;
    color: #555577;
    background-color: transparent;
}
QPushButton#ghostBtn:checked {
    background-color: rgba(167,139,250,0.15);
    color: #a78bfa;
}
/* ── Scrollbar ── */
QScrollBar:vertical {
    background: #0a0a12; width: 10px; margin: 0;
}
QScrollBar::handle:vertical {
    background: #2a2a3e; min-height: 24px; border-radius: 5px; margin: 2px;
}
QScrollBar::handle:vertical:hover { background: #555577; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
/* ── Divider ── */
QFrame#divider { background-color: #1e1e2e; max-height: 1px; }
QFrame#divider:disabled { background-color: #14141f; }
"""

MONITOR_SVG = b"""<svg viewBox="0 0 260 180" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="240" height="148" rx="14" ry="14"
        fill="#1a1a2e" stroke="#3a3a5e" stroke-width="3"/>
  <rect x="20" y="20" width="220" height="128" rx="8" ry="8"
        fill="#0d0d18"/>
  <rect x="105" y="158" width="50" height="12" rx="3" ry="3" fill="#1a1a2e"/>
  <rect x="80" y="169" width="100" height="5" rx="2" ry="2" fill="#141424"/>
</svg>"""


class ColorButton(QPushButton):
    def __init__(self, color_hex="#ffffff"):
        super().__init__()
        self.color_hex = color_hex
        self.setObjectName("colorBtn")
        self.setFixedSize(90, 32)
        self._refresh()
        self.clicked.connect(self._pick)

    def _refresh(self):
        qc = QColor(self.color_hex)
        lum = 0.299 * qc.red() + 0.587 * qc.green() + 0.114 * qc.blue()
        fg = "#000" if lum > 128 else "#fff"
        self.setStyleSheet(
            f"QPushButton#colorBtn {{ background-color:{self.color_hex}; color:{fg};"
            f" border:1px solid #555; border-radius:6px; font-size:8pt; font-weight:bold; }}"
            f"QPushButton#colorBtn:hover {{ background-color:{self.color_hex}; color:{fg};"
            f" border:1.5px solid #a78bfa; }}"
        )
        self.setText(self.color_hex.upper())

    def _pick(self):
        c = QColorDialog.getColor(QColor(self.color_hex), self)
        if c.isValid():
            self.color_hex = c.name()
            self._refresh()


def _info(tip):
    lbl = QLabel("?")
    lbl.setFixedSize(16, 16)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(
        "background:#1e1e2e; color:#a78bfa; border-radius:8px; "
        "font-weight:bold; font-size:8pt;"
    )
    lbl.setToolTip(tip)
    return lbl


def _divider():
    f = QFrame()
    f.setObjectName("divider")
    f.setFixedHeight(1)
    return f


def _section(text):
    lbl = QLabel(text.upper())
    lbl.setObjectName("sectionLabel")
    return lbl


# ─────────────────────────────────────────────
# Monitor widget — fully painted, no SVG overlay
# ─────────────────────────────────────────────
class MonitorWidget(QWidget):
    corner_clicked = Signal(str)

    CORNERS = ["TOP_LEFT", "TOP_RIGHT", "BOTTOM_LEFT", "BOTTOM_RIGHT"]
    CORNER_LABELS = {
        "TOP_LEFT": "TL", "TOP_RIGHT": "TR",
        "BOTTOM_LEFT": "BL", "BOTTOM_RIGHT": "BR",
    }

    # ── colours
    C_BG      = QColor("#0a0a12")
    C_BEZEL   = QColor("#1e1e2e")
    C_SCREEN  = QColor("#0d0d18")
    C_IDLE    = QColor(160, 160, 200, 30)
    C_IDLE_BD = QColor("#2a2a44")
    C_HOV     = QColor(167, 139, 250, 55)
    C_HOV_BD  = QColor("#a78bfa")
    C_ACT     = QColor(167, 139, 250, 90)
    C_ACT_BD  = QColor("#a78bfa")
    C_ENA     = QColor(74, 222, 128, 45)
    C_ENA_BD  = QColor("#4ade80")
    C_TEXT_IDLE = QColor("#55557a")
    C_TEXT_HOV  = QColor("#a78bfa")
    C_TEXT_ACT  = QColor("#c4b5fd")
    C_TEXT_ENA  = QColor("#4ade80")

    ZONE = 54   # corner zone size in px (within screen area)

    def __init__(self, settings, lang="en"):
        super().__init__()
        self.settings = settings
        self.lang = lang
        self.active = "TOP_LEFT"
        self._hover = None
        self.setFixedSize(280, 200)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

    # ── geometry helpers ──────────────────────
    def _screen_rect(self):
        """The inner screen area rectangle."""
        w, h = self.width(), self.height()
        bz = 16   # bezel thickness
        stand_h = 22
        sx = bz
        sy = bz
        sw = w - 2*bz
        sh = h - 2*bz - stand_h
        return sx, sy, sw, sh

    def _corner_rect(self, corner_id):
        sx, sy, sw, sh = self._screen_rect()
        z = self.ZONE
        if corner_id == "TOP_LEFT":     return (sx,        sy,        z, z)
        if corner_id == "TOP_RIGHT":    return (sx+sw-z,   sy,        z, z)
        if corner_id == "BOTTOM_LEFT":  return (sx,        sy+sh-z,   z, z)
        if corner_id == "BOTTOM_RIGHT": return (sx+sw-z,   sy+sh-z,   z, z)
        return (0, 0, 0, 0)

    def _corner_at(self, px, py):
        for cid in self.CORNERS:
            x, y, w, h = self._corner_rect(cid)
            if x <= px <= x+w and y <= py <= y+h:
                return cid
        return None

    # ── events ───────────────────────────────
    def mouseMoveEvent(self, event):
        h = self._corner_at(event.x(), event.y())
        if h != self._hover:
            self._hover = h
            self.update()

    def leaveEvent(self, event):
        self._hover = None
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            cid = self._corner_at(event.x(), event.y())
            if cid:
                self.active = cid
                self.update()
                self.corner_clicked.emit(cid)

    # ── painting ─────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        bz = 16
        stand_h = 22
        sx, sy, sw, sh = self._screen_rect()
        z = self.ZONE
        corners_cfg = self.settings.get("corners", {})

        # ── Bezel ──
        p.setBrush(QBrush(self.C_BEZEL))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(sx-bz, sy-bz, sw+2*bz, sh+2*bz, 12, 12)

        # ── Screen background ──
        p.setBrush(QBrush(self.C_SCREEN))
        p.drawRoundedRect(sx, sy, sw, sh, 6, 6)

        # ── Subtle desktop wallpaper gradient ──
        grad = QLinearGradient(sx, sy, sx+sw, sy+sh)
        grad.setColorAt(0, QColor(20, 18, 40, 120))
        grad.setColorAt(1, QColor(10, 10, 20, 120))
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(sx, sy, sw, sh, 6, 6)

        # ── Corner zones ──
        font = QFont("Segoe UI", 8, QFont.Bold)
        p.setFont(font)

        for cid in self.CORNERS:
            cx, cy, cw, ch = self._corner_rect(cid)
            enabled = corners_cfg.get(cid, {}).get("enabled", False)
            is_active = (cid == self.active)
            is_hov = (cid == self._hover)

            # Pick colours
            if is_active:
                fill, bd, tc = self.C_ACT, self.C_ACT_BD, self.C_TEXT_ACT
            elif is_hov:
                fill, bd, tc = self.C_HOV, self.C_HOV_BD, self.C_TEXT_HOV
            elif enabled:
                fill, bd, tc = self.C_ENA, self.C_ENA_BD, self.C_TEXT_ENA
            else:
                fill, bd, tc = self.C_IDLE, self.C_IDLE_BD, self.C_TEXT_IDLE

            # Rounded zone
            p.setBrush(QBrush(fill))
            pen = QPen(bd, 1.5 if is_active else 1)
            p.setPen(pen)
            r = 5
            p.drawRoundedRect(cx, cy, cw, ch, r, r)

            # Glow ring for active
            if is_active:
                glow = QPen(self.C_ACT_BD, 2)
                glow.setStyle(Qt.DotLine)
                p.setPen(glow)
                p.setBrush(Qt.NoBrush)
                p.drawRoundedRect(cx-2, cy-2, cw+4, ch+4, r+2, r+2)

            # Label
            p.setPen(tc)
            label = self.CORNER_LABELS[cid]
            p.drawText(cx, cy, cw, ch, Qt.AlignCenter, label)

        # ── Stand ──
        stand_x = sx + sw//2 - 30
        stand_y = sy + sh + 2
        p.setBrush(QBrush(self.C_BEZEL))
        p.setPen(Qt.NoPen)
        p.drawRect(stand_x, stand_y, 60, stand_h - 6)
        p.drawRect(stand_x - 20, stand_y + stand_h - 8, 100, 6)

        p.end()

    def _refresh_chips(self):
        """Keep API compatibility — just repaint."""
        self.update()

    def mark_enabled(self, corner_id, enabled):
        cfg = self.settings.get("corners", {})
        if corner_id in cfg:
            cfg[corner_id]["enabled"] = enabled
        self.update()


# ─────────────────────────────────────────────
# Corner editor panel (right side)
# ─────────────────────────────────────────────
class CornerPanel(QWidget):
    def __init__(self, lang="en"):
        super().__init__()
        self.setObjectName("rightPanel")
        self.lang = lang
        self.corner_id = None
        self._on_enabled_change = None  # callback

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(16)

        # Corner title
        self.lbl_title = QLabel("—")
        self.lbl_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #a78bfa;")
        root.addWidget(self.lbl_title)

        root.addWidget(_divider())

        # Enable
        self.chk_enable = QCheckBox(t("enable", lang))
        self.chk_enable.setObjectName("enableCheck")
        root.addWidget(self.chk_enable)

        root.addWidget(_divider())

        # Action row
        root.addWidget(_section(t("action", lang).replace(":", "")))
        action_row = QHBoxLayout()
        self.combo_action = QComboBox()
        self.combo_action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_build = QPushButton(t("action_builder_btn", lang))
        btn_build.setObjectName("ghostBtn")
        btn_build.setFixedHeight(32)
        btn_build.setToolTip(t("build_custom_action", lang))
        btn_build.clicked.connect(self._open_builder)
        action_row.addWidget(self.combo_action)
        action_row.addWidget(btn_build)
        root.addLayout(action_row)

        # Animation + Color row
        anim_color_row = QHBoxLayout()
        anim_col = QVBoxLayout()
        anim_col.addWidget(_section(t("animation", lang).replace(":", "")))
        self.combo_anim = QComboBox()
        for anim_id in ANIMATIONS:
            self.combo_anim.addItem(t(f"anim_{anim_id}", lang), anim_id)
        anim_col.addWidget(self.combo_anim)

        color_col = QVBoxLayout()
        color_col.addWidget(_section(t("color", lang).replace(":", "")))
        self.btn_color = ColorButton()
        color_col.addWidget(self.btn_color)

        anim_color_row.addLayout(anim_col, 2)
        anim_color_row.addSpacing(12)
        anim_color_row.addLayout(color_col, 1)
        root.addLayout(anim_color_row)

        # Delay row
        delay_row = QHBoxLayout()
        delay_lbl = _section(t("delay", lang).replace(":", ""))
        delay_row.addWidget(delay_lbl)
        delay_row.addWidget(_info(t("info_delay", lang)))
        delay_row.addStretch()
        self.spin_delay = QDoubleSpinBox()
        self.spin_delay.setRange(0.05, 5.0)
        self.spin_delay.setSingleStep(0.05)
        self.spin_delay.setFixedWidth(90)
        delay_row.addWidget(self.spin_delay)
        root.addLayout(delay_row)

        # Allow maximized
        self.chk_maximized = QCheckBox(t("allow_maximized", lang))
        root.addWidget(self.chk_maximized)

        root.addStretch()
        self.setEnabled(False)

    def _open_builder(self):
        dlg = ActionBuilderDialog(self, self.lang)
        if dlg.exec():
            # Refresh action combobox after builder closes
            if hasattr(self, '_refresh_action_combo'):
                self._refresh_action_combo()

    def load(self, corner_id, corner_data, settings, lang="en"):
        self.corner_id = corner_id
        self.lang = lang
        self.lbl_title.setText(t(corner_id, lang))
        self.chk_enable.setChecked(corner_data.get("enabled", False))
        self._rebuild_actions(corner_data.get("action_id", "none"), settings)
        curr_anim = corner_data.get("animation", "pulse")
        idx = self.combo_anim.findData(curr_anim)
        if idx >= 0: self.combo_anim.setCurrentIndex(idx)
        self.btn_color = ColorButton(corner_data.get("color", "#ffffff"))
        self.spin_delay.setValue(corner_data.get("delay", 0.4))
        self.chk_maximized.setChecked(corner_data.get("allow_maximized", False))
        self.setEnabled(True)

    def _rebuild_actions(self, current_action, settings):
        self.combo_action.clear()
        for action_id, info in BUILTIN_ACTIONS.items():
            self.combo_action.addItem(t(info["t_key"], self.lang), action_id)
        # Custom built actions
        custom = load_custom_actions()
        for name in sorted(custom.keys()):
            uid = CUSTOM_ACTION_PREFIX + name
            self.combo_action.addItem(f"{t('custom_prefix', self.lang)}{name}", uid)
        # Python scripts
        if os.path.exists(SCRIPTS_DIR):
            for f in sorted(os.listdir(SCRIPTS_DIR)):
                if f.endswith('.py'):
                    self.combo_action.addItem(f"{t('script_prefix', self.lang)}{f}", f)
        # Separator + builder
        self.combo_action.insertSeparator(self.combo_action.count())
        self.combo_action.addItem(t("build_custom_action", self.lang), "__open_builder__")
        # Set current
        idx = self.combo_action.findData(current_action)
        if idx >= 0:
            self.combo_action.setCurrentIndex(idx)
        self.combo_action.currentIndexChanged.connect(self._on_action_changed)

    def _on_action_changed(self, idx):
        if self.combo_action.currentData() == "__open_builder__":
            dlg = ActionBuilderDialog(self, self.lang)
            dlg.exec()
            # Refresh and restore to none
            prev = self.combo_action.currentIndex()
            self._rebuild_actions("none", {})

    def _refresh_action_combo(self):
        current = self.combo_action.currentData()
        self._rebuild_actions(current, {})

    def collect(self):
        action_id = self.combo_action.currentData() or "none"
        if action_id == "__open_builder__":
            action_id = "none"
        return {
            "enabled": self.chk_enable.isChecked(),
            "allow_maximized": self.chk_maximized.isChecked(),
            "action_id": action_id,
            "animation": self.combo_anim.currentData() or "pulse",
            "color": self.btn_color.color_hex,
            "delay": self.spin_delay.value(),
        }


# ─────────────────────────────────────────────
# Main Settings Window
# ─────────────────────────────────────────────
class SettingsUI(QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.settings = load_settings()
        self.lang = self.settings.get("language", "en")

        self.setWindowTitle(t("settings_title", self.lang))
        self.setMinimumSize(820, 540)
        self.setStyleSheet(QSS)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ══════════════════════════════
        # LEFT SIDEBAR
        # ══════════════════════════════
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setObjectName("sidebar")
        sidebar_scroll.setFixedWidth(320)
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setFrameShape(QFrame.NoFrame)
        sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        sidebar = QWidget()
        sidebar.setObjectName("sidebarContent")
        sidebar.setStyleSheet("background-color: transparent;")
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(20, 20, 20, 16)
        sb.setSpacing(14)

        # Monitor widget
        self.monitor = MonitorWidget(self.settings, self.lang)
        self.monitor.corner_clicked.connect(self._on_corner_clicked)
        sb.addWidget(self.monitor, 0, Qt.AlignHCenter)

        sb.addWidget(_divider())

        # Global settings
        sb.addWidget(_section("General"))

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel(t("language", self.lang)))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Español", "es")
        idx = self.lang_combo.findData(self.lang)
        if idx >= 0: self.lang_combo.setCurrentIndex(idx)
        lang_row.addWidget(self.lang_combo)
        sb.addLayout(lang_row)

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel(t("theme", self.lang)))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["system", "dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "system"))
        theme_row.addWidget(self.theme_combo)
        sb.addLayout(theme_row)

        self.chk_startup = QCheckBox(t("tray_startup", self.lang))
        self.chk_startup.setChecked(is_startup_enabled())
        sb.addWidget(self.chk_startup)

        sb.addWidget(_divider())

        # Advanced toggle
        self.btn_adv = QPushButton(t("advanced_options", self.lang))
        self.btn_adv.setObjectName("ghostBtn")
        self.btn_adv.setCheckable(True)
        self.btn_adv.toggled.connect(self._toggle_adv)
        sb.addWidget(self.btn_adv)

        self.adv_widget = QWidget()
        adv_l = QVBoxLayout(self.adv_widget)
        adv_l.setContentsMargins(0, 0, 0, 0)
        adv_l.setSpacing(10)

        radius_row = QHBoxLayout()
        radius_row.addWidget(QLabel(t("radius", self.lang)))
        radius_row.addWidget(_info(t("info_radius", self.lang)))
        radius_row.addStretch()
        self.spin_radius = QSpinBox()
        self.spin_radius.setRange(1, 100)
        self.spin_radius.setValue(self.settings.get("radius", 10))
        self.spin_radius.setFixedWidth(70)
        radius_row.addWidget(self.spin_radius)
        adv_l.addLayout(radius_row)

        poll_row = QHBoxLayout()
        poll_row.addWidget(QLabel(t("polling_interval", self.lang)))
        poll_row.addWidget(_info(t("info_polling", self.lang)))
        poll_row.addStretch()
        self.spin_poll = QSpinBox()
        self.spin_poll.setRange(1, 500)
        self.spin_poll.setValue(self.settings.get("polling_interval", 16))
        self.spin_poll.setFixedWidth(70)
        poll_row.addWidget(self.spin_poll)
        adv_l.addLayout(poll_row)

        mm_row = QHBoxLayout()
        self.chk_mm = QCheckBox(t("multi_monitor", self.lang))
        self.chk_mm.setChecked(self.settings.get("multi_monitor", True))
        mm_row.addWidget(self.chk_mm)
        mm_row.addWidget(_info(t("info_multi_monitor", self.lang)))
        mm_row.addStretch()
        adv_l.addLayout(mm_row)

        self.adv_widget.setVisible(False)
        sb.addWidget(self.adv_widget)

        sb.addStretch()
        sidebar_scroll.setWidget(sidebar)
        root.addWidget(sidebar_scroll)

        # ══════════════════════════════
        # RIGHT PANEL
        # ══════════════════════════════
        right_wrap = QWidget()
        right_wrap.setObjectName("rightPanel")
        rw_layout = QVBoxLayout(right_wrap)
        rw_layout.setContentsMargins(0, 0, 0, 0)
        rw_layout.setSpacing(0)

        panel_scroll = QScrollArea()
        panel_scroll.setWidgetResizable(True)
        panel_scroll.setFrameShape(QFrame.NoFrame)

        self.corner_panel = CornerPanel(self.lang)
        panel_scroll.setWidget(self.corner_panel)
        rw_layout.addWidget(panel_scroll)

        # Bottom bar
        bar = QWidget()
        bar.setStyleSheet("background-color: #0a0a12; border-top: 1px solid #1e1e2e;")
        bar.setFixedHeight(58)
        bar_l = QHBoxLayout(bar)
        bar_l.setContentsMargins(20, 10, 20, 10)
        bar_l.setSpacing(10)

        btn_scripts = QPushButton(t("tray_scripts", self.lang))
        btn_scripts.setObjectName("ghostBtn")
        btn_scripts.clicked.connect(self._open_scripts)

        btn_cancel = QPushButton(t("cancel", self.lang))
        btn_cancel.clicked.connect(self.hide)

        btn_apply = QPushButton(t("apply", self.lang))
        btn_apply.setObjectName("ghostBtn")
        btn_apply.clicked.connect(self._apply)

        btn_save = QPushButton(t("save_settings", self.lang))
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self._save_close)

        bar_l.addWidget(btn_scripts)
        bar_l.addStretch()
        bar_l.addWidget(btn_cancel)
        bar_l.addWidget(btn_apply)
        bar_l.addWidget(btn_save)
        rw_layout.addWidget(bar)

        root.addWidget(right_wrap)

        # Load first corner by default
        self._on_corner_clicked("TOP_LEFT")
        # Connect enable checkbox to monitor refresh
        self.corner_panel.chk_enable.stateChanged.connect(self._on_enable_change)

    def _on_corner_clicked(self, corner_id):
        # Save current before switching
        if self.corner_panel.corner_id and self.corner_panel.isEnabled():
            self._save_panel_to_settings(self.corner_panel.corner_id)

        self.monitor.active = corner_id
        self.monitor._refresh_chips()
        corner_data = self.settings["corners"].get(corner_id, {})
        self.corner_panel.load(corner_id, corner_data, self.settings, self.lang)

    def _on_enable_change(self, state):
        corner_id = self.corner_panel.corner_id
        if corner_id:
            enabled = state == Qt.Checked.value if hasattr(Qt.Checked, 'value') else bool(state)
            self.monitor.mark_enabled(corner_id, bool(state))

    def _save_panel_to_settings(self, corner_id):
        self.settings["corners"][corner_id] = self.corner_panel.collect()

    def _toggle_adv(self, checked):
        self.adv_widget.setVisible(checked)
        self.btn_adv.setText(
            t("advanced_options", self.lang).replace("▸", "▾") if checked
            else t("advanced_options", self.lang)
        )

    def _open_scripts(self):
        import subprocess
        subprocess.Popen(["explorer.exe", SCRIPTS_DIR])

    def _gather(self):
        # Save current corner
        if self.corner_panel.corner_id:
            self._save_panel_to_settings(self.corner_panel.corner_id)
        self.lang = self.lang_combo.currentData()
        self.settings["language"] = self.lang
        self.settings["theme"] = self.theme_combo.currentText()
        self.settings["radius"] = self.spin_radius.value()
        self.settings["polling_interval"] = self.spin_poll.value()
        self.settings["multi_monitor"] = self.chk_mm.isChecked()

    def _apply(self):
        self._gather()
        save_settings(self.settings)
        self.engine.reload_settings()
        if self.chk_startup.isChecked():
            enable_startup()
        else:
            disable_startup()
        if hasattr(self.engine, 'app_instance'):
            self.engine.app_instance.update_tray_menu()

    def _save_close(self):
        self._apply()
        self.hide()
