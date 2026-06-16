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
from config import load_settings, save_settings, SCRIPTS_DIR, effective_is_dark
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
/* ── Corner panel title ── */
QLabel#cornerTitle {
    font-size: 14pt;
    font-weight: bold;
    color: #a78bfa;
    padding: 0;
    margin: 0;
}
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
/* ── Bottom bar ── */
#bottomBar {
    background-color: #0a0a12;
    border-top: 1px solid #1e1e2e;
}
/* ── Divider ── */
QFrame#divider { background-color: #1e1e2e; max-height: 1px; }
QFrame#divider:disabled { background-color: #14141f; }
"""

QSS_LIGHT = """
QWidget {
    background-color: #f5f5f7;
    color: #2c2c3a;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}
QWidget:disabled {
    color: #a0a0b0;
}
/* ── Scroll Areas ── */
QScrollArea {
    border: none;
    background-color: transparent;
}
/* ── Sidebar ── */
#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e0e0e8;
}
#sidebarContent {
    background-color: #ffffff;
}
/* ── Right panel ── */
#rightPanel {
    background-color: #f5f5f7;
}
/* ── Section labels ── */
QLabel#sectionLabel {
    color: #88889a;
    font-size: 8pt;
    font-weight: bold;
    letter-spacing: 1px;
    padding-bottom: 2px;
}
QLabel#sectionLabel:disabled {
    color: #c0c0ce;
}
/* ── ComboBox ── */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #c8c8d0;
    border-radius: 6px;
    padding: 6px 10px;
    color: #2c2c3a;
    min-height: 28px;
}
QComboBox:hover { border-color: #7c3aed; }
QComboBox:disabled {
    background-color: #e8e8ec;
    border-color: #d0d0d8;
    color: #a0a0b0;
}
QComboBox::drop-down { border: none; width: 26px; }
QComboBox::down-arrow {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #7c3aed;
    margin-right: 8px;
}
QComboBox::down-arrow:disabled {
    border-top-color: #c0c0ce;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #c8c8d0;
    selection-background-color: #7c3aed;
    selection-color: #ffffff;
    outline: none;
}
/* ── SpinBox ── */
QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #c8c8d0;
    border-radius: 6px;
    padding: 5px 8px;
    color: #2c2c3a;
    min-height: 28px;
}
QSpinBox:hover, QDoubleSpinBox:hover { border-color: #7c3aed; }
QSpinBox:disabled, QDoubleSpinBox:disabled {
    background-color: #e8e8ec;
    border-color: #d0d0d8;
    color: #a0a0b0;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border; subcontrol-position: top right;
    width: 18px; border-left: 1px solid #c8c8d0;
    border-top-right-radius: 5px; background-color: #ececf0;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border; subcontrol-position: bottom right;
    width: 18px; border-left: 1px solid #c8c8d0;
    border-bottom-right-radius: 5px; background-color: #ececf0;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #7c3aed;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-bottom: 4px solid #7c3aed; width: 0; height: 0;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    border-left: 3px solid transparent; border-right: 3px solid transparent;
    border-top: 4px solid #7c3aed; width: 0; height: 0;
}
/* ── Checkbox ── */
QCheckBox { spacing: 10px; color: #2c2c3a; }
QCheckBox:disabled {
    color: #a0a0b0;
}
QCheckBox::indicator {
    width: 18px; height: 18px; border-radius: 5px;
    border: 2px solid #c8c8d0; background-color: #ffffff;
}
QCheckBox::indicator:hover { border-color: #7c3aed; }
QCheckBox::indicator:disabled {
    border-color: #d0d0d8;
    background-color: #e8e8ec;
}
QCheckBox::indicator:checked {
    background-color: #7c3aed; border-color: #7c3aed;
}
QCheckBox::indicator:checked:disabled {
    background-color: #c0c0ce; border-color: #c0c0ce;
}
QCheckBox#enableCheck {
    font-size: 11pt;
    font-weight: bold;
    color: #1a1a2a;
}
QCheckBox#enableCheck:disabled {
    color: #a0a0b0;
}
QCheckBox#enableCheck::indicator { width: 20px; height: 20px; }
/* ── Buttons ── */
QPushButton {
    background-color: #e8e8ec;
    border: 1px solid #c8c8d0;
    border-radius: 6px;
    padding: 8px 18px;
    color: #2c2c3a;
    font-weight: bold;
    min-height: 32px;
}
QPushButton:hover {
    background-color: #7c3aed;
    color: #ffffff;
    border-color: #7c3aed;
}
QPushButton:pressed { background-color: #6d28d9; color: #fff; }
QPushButton:disabled {
    background-color: #e8e8ec;
    border-color: #d0d0d8;
    color: #a0a0b0;
}
QPushButton#primaryBtn {
    background-color: #7c3aed;
    color: #ffffff;
    border-color: #7c3aed;
}
QPushButton#primaryBtn:hover { background-color: #6d28d9; color: #fff; }
QPushButton#primaryBtn:disabled {
    background-color: #c0c0ce;
    border-color: #c0c0ce;
    color: #e0e0e8;
}
QPushButton#ghostBtn {
    background-color: transparent;
    border-color: #7c3aed;
    color: #7c3aed;
}
QPushButton#ghostBtn:hover {
    background-color: #7c3aed;
    color: #ffffff;
    border-color: #7c3aed;
}
QPushButton#ghostBtn:disabled {
    border-color: #c8c8d0;
    color: #a0a0b0;
    background-color: transparent;
}
QPushButton#ghostBtn:checked {
    background-color: rgba(124,58,237,0.12);
    color: #7c3aed;
}
/* ── Corner panel title ── */
QLabel#cornerTitle {
    font-size: 14pt;
    font-weight: bold;
    color: #7c3aed;
    padding: 0;
    margin: 0;
}
/* ── Scrollbar ── */
QScrollBar:vertical {
    background: #ffffff; width: 10px; margin: 0;
}
QScrollBar::handle:vertical {
    background: #c8c8d0; min-height: 24px; border-radius: 5px; margin: 2px;
}
QScrollBar::handle:vertical:hover { background: #a0a0b0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
/* ── Bottom bar ── */
#bottomBar {
    background-color: #ffffff;
    border-top: 1px solid #e0e0e8;
}
/* ── Divider ── */
QFrame#divider { background-color: #e0e0e8; max-height: 1px; }
QFrame#divider:disabled { background-color: #e8e8ec; }
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
        "color:#a78bfa; border:1px solid #a78bfa; border-radius:8px; "
        "font-weight:bold; font-size:8pt; background:transparent;"
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

    ZONE = 54   # corner zone size in px (within screen area)

    def __init__(self, settings, lang="en", is_dark=True):
        super().__init__()
        self.settings = settings
        self.lang = lang
        self._is_dark = is_dark
        self._init_colors()
        self.active = "TOP_LEFT"
        self._hover = None
        self.setFixedSize(280, 200)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

    def _init_colors(self):
        if self._is_dark:
            self.C_BG      = QColor("#0a0a12")
            self.C_BEZEL   = QColor("#1e1e2e")
            self.C_SCREEN  = QColor("#0d0d18")
            self.C_IDLE    = QColor(160, 160, 200, 30)
            self.C_IDLE_BD = QColor("#2a2a44")
            self.C_HOV     = QColor(167, 139, 250, 55)
            self.C_HOV_BD  = QColor("#a78bfa")
            self.C_ACT     = QColor(167, 139, 250, 90)
            self.C_ACT_BD  = QColor("#a78bfa")
            self.C_ENA     = QColor(74, 222, 128, 45)
            self.C_ENA_BD  = QColor("#4ade80")
            self.C_TEXT_IDLE = QColor("#55557a")
            self.C_TEXT_HOV  = QColor("#a78bfa")
            self.C_TEXT_ACT  = QColor("#c4b5fd")
            self.C_TEXT_ENA  = QColor("#4ade80")
            self._wallpaper_grad = [(20, 18, 40, 120), (10, 10, 20, 120)]
        else:
            self.C_BG      = QColor("#f0f0f2")
            self.C_BEZEL   = QColor("#d4d4dc")
            self.C_SCREEN  = QColor("#ffffff")
            self.C_IDLE    = QColor(180, 180, 210, 40)
            self.C_IDLE_BD = QColor("#c8c8d0")
            self.C_HOV     = QColor(124, 58, 237, 50)
            self.C_HOV_BD  = QColor("#7c3aed")
            self.C_ACT     = QColor(124, 58, 237, 85)
            self.C_ACT_BD  = QColor("#7c3aed")
            self.C_ENA     = QColor(34, 197, 94, 45)
            self.C_ENA_BD  = QColor("#22c55e")
            self.C_TEXT_IDLE = QColor("#a0a0b0")
            self.C_TEXT_HOV  = QColor("#7c3aed")
            self.C_TEXT_ACT  = QColor("#6d28d9")
            self.C_TEXT_ENA  = QColor("#22c55e")
            self._wallpaper_grad = [(200, 200, 220, 80), (220, 220, 240, 60)]

    def set_theme(self, is_dark):
        self._is_dark = is_dark
        self._init_colors()
        self.update()

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
        c0, c1 = self._wallpaper_grad
        grad.setColorAt(0, QColor(*c0))
        grad.setColorAt(1, QColor(*c1))
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
    def __init__(self, lang="en", is_dark=True):
        super().__init__()
        self.setObjectName("rightPanel")
        self.lang = lang
        self._is_dark = is_dark
        self.corner_id = None
        self._on_enabled_change = None  # callback

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(16)

        # Corner title
        self.lbl_title = QLabel("—")
        self.lbl_title.setObjectName("cornerTitle")
        root.addWidget(self.lbl_title)

        root.addWidget(_divider())

        # Enable
        self.chk_enable = QCheckBox(t("enable", lang))
        self.chk_enable.setObjectName("enableCheck")
        root.addWidget(self.chk_enable)

        root.addWidget(_divider())

        # Action row
        self._sec_action = _section(t("action", lang).replace(":", ""))
        root.addWidget(self._sec_action)
        self.combo_action = QComboBox()
        self.combo_action.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_action.currentIndexChanged.connect(self._on_action_changed)
        root.addWidget(self.combo_action)

        self.btn_build = QPushButton(t("action_builder_btn", lang))
        self.btn_build.setObjectName("ghostBtn")
        self.btn_build.setFixedHeight(32)
        self.btn_build.setToolTip(t("build_custom_action", lang))
        self.btn_build.clicked.connect(self._open_builder)
        root.addSpacing(4)
        build_row = QHBoxLayout()
        build_row.addStretch()
        build_row.addWidget(self.btn_build)
        build_row.addStretch()
        root.addLayout(build_row)

        # Animation + Color row
        anim_color_row = QHBoxLayout()
        anim_col = QVBoxLayout()
        self._sec_anim = _section(t("animation", lang).replace(":", ""))
        anim_col.addWidget(self._sec_anim)
        self.combo_anim = QComboBox()
        for anim_id in ANIMATIONS:
            self.combo_anim.addItem(t(f"anim_{anim_id}", lang), anim_id)
        anim_col.addWidget(self.combo_anim)

        color_col = QVBoxLayout()
        self._sec_color = _section(t("color", lang).replace(":", ""))
        color_col.addWidget(self._sec_color)
        self.btn_color = ColorButton()
        color_col.addWidget(self.btn_color)

        anim_color_row.addLayout(anim_col, 2)
        anim_color_row.addSpacing(12)
        anim_color_row.addLayout(color_col, 1)
        root.addLayout(anim_color_row)

        # Delay row
        delay_row = QHBoxLayout()
        self._sec_delay = _section(t("delay", lang).replace(":", ""))
        delay_row.addWidget(self._sec_delay)
        self._info_delay = _info(t("info_delay", lang))
        delay_row.addWidget(self._info_delay)
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

    def retranslate(self, lang):
        self.lang = lang
        self.lbl_title.setText(t(self.corner_id, lang) if self.corner_id else "—")
        self.chk_enable.setText(t("enable", lang))
        self._sec_action.setText(t("action", lang).replace(":", "").upper())
        self._sec_anim.setText(t("animation", lang).replace(":", "").upper())
        self._sec_color.setText(t("color", lang).replace(":", "").upper())
        self._sec_delay.setText(t("delay", lang).replace(":", "").upper())
        self.btn_build.setText(t("action_builder_btn", lang))
        self.btn_build.setToolTip(t("build_custom_action", lang))
        self._info_delay.setToolTip(t("info_delay", lang))
        self.chk_maximized.setText(t("allow_maximized", lang))
        # Rebuild action combo items (keep current selection)
        current_data = self.combo_action.currentData()
        self._rebuild_actions(current_data if current_data != "__open_builder__" else "none", {})
        # Rebuild animation combo items
        current_anim = self.combo_anim.currentData() or "pulse"
        self.combo_anim.blockSignals(True)
        self.combo_anim.clear()
        for anim_id in ANIMATIONS:
            self.combo_anim.addItem(t(f"anim_{anim_id}", lang), anim_id)
        idx = self.combo_anim.findData(current_anim)
        if idx >= 0: self.combo_anim.setCurrentIndex(idx)
        self.combo_anim.blockSignals(False)

    def _open_builder(self):
        dlg = ActionBuilderDialog(self, self.lang, self._is_dark)
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
        self.btn_color.color_hex = corner_data.get("color", "#ffffff")
        self.btn_color._refresh()
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
        # Set current (block signals to avoid triggering _on_action_changed)
        self.combo_action.blockSignals(True)
        idx = self.combo_action.findData(current_action)
        if idx >= 0:
            self.combo_action.setCurrentIndex(idx)
        self.combo_action.blockSignals(False)

    def _on_action_changed(self, idx):
        if self.combo_action.currentData() == "__open_builder__":
            dlg = ActionBuilderDialog(self, self.lang, self._is_dark)
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

        self._is_dark = effective_is_dark(self.settings)
        self.apply_qss()

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
        self.monitor = MonitorWidget(self.settings, self.lang, self._is_dark)
        self.monitor.corner_clicked.connect(self._on_corner_clicked)
        sb.addWidget(self.monitor, 0, Qt.AlignHCenter)

        sb.addWidget(_divider())

        # Global settings
        sb.addWidget(_section("General"))

        lang_row = QHBoxLayout()
        self.lbl_lang = QLabel(t("language", self.lang))
        lang_row.addWidget(self.lbl_lang)
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Español", "es")
        idx = self.lang_combo.findData(self.lang)
        if idx >= 0: self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.lang_combo)
        sb.addLayout(lang_row)

        theme_row = QHBoxLayout()
        self.lbl_theme = QLabel(t("theme", self.lang))
        theme_row.addWidget(self.lbl_theme)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["system", "dark", "light"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "system"))
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
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
        self.lbl_radius = QLabel(t("radius", self.lang))
        radius_row.addWidget(self.lbl_radius)
        self._info_radius = _info(t("info_radius", self.lang))
        radius_row.addWidget(self._info_radius)
        radius_row.addStretch()
        self.spin_radius = QSpinBox()
        self.spin_radius.setRange(1, 100)
        self.spin_radius.setValue(self.settings.get("radius", 10))
        self.spin_radius.setFixedWidth(70)
        radius_row.addWidget(self.spin_radius)
        adv_l.addLayout(radius_row)

        poll_row = QHBoxLayout()
        self.lbl_poll = QLabel(t("polling_interval", self.lang))
        poll_row.addWidget(self.lbl_poll)
        self._info_poll = _info(t("info_polling", self.lang))
        poll_row.addWidget(self._info_poll)
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
        self._info_mm = _info(t("info_multi_monitor", self.lang))
        mm_row.addWidget(self._info_mm)
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

        self.corner_panel = CornerPanel(self.lang, self._is_dark)
        panel_scroll.setWidget(self.corner_panel)
        rw_layout.addWidget(panel_scroll)

        # Bottom bar
        bar = QWidget()
        bar.setObjectName("bottomBar")
        bar.setFixedHeight(58)
        bar_l = QHBoxLayout(bar)
        bar_l.setContentsMargins(20, 10, 20, 10)
        bar_l.setSpacing(10)

        self.btn_scripts = QPushButton(t("tray_scripts", self.lang))
        self.btn_scripts.setObjectName("ghostBtn")
        self.btn_scripts.clicked.connect(self._open_scripts)

        self.btn_cancel = QPushButton(t("cancel", self.lang))
        self.btn_cancel.clicked.connect(self.hide)

        self.btn_save = QPushButton(t("save_settings", self.lang))
        self.btn_save.setObjectName("primaryBtn")
        self.btn_save.clicked.connect(self._save_close)

        bar_l.addWidget(self.btn_scripts)
        bar_l.addStretch()
        bar_l.addWidget(self.btn_cancel)
        bar_l.addWidget(self.btn_save)
        rw_layout.addWidget(bar)

        root.addWidget(right_wrap)

        # Load first corner by default
        self._on_corner_clicked("TOP_LEFT")
        # Connect enable checkbox to monitor refresh
        self.corner_panel.chk_enable.stateChanged.connect(self._on_enable_change)

    def apply_qss(self):
        self.setStyleSheet(QSS_LIGHT if not self._is_dark else QSS)

    def _on_theme_changed(self, theme_text):
        self._is_dark = effective_is_dark({**self.settings, "theme": theme_text})
        self.apply_qss()
        self.monitor.set_theme(self._is_dark)
        self.corner_panel._is_dark = self._is_dark
        self.settings["theme"] = theme_text
        save_settings(self.settings)
        self.engine.reload_settings()
        if hasattr(self.engine, 'app_instance'):
            self.engine.app_instance.apply_theme()
            self.engine.app_instance.update_tray_menu()

    def _retranslate_ui(self):
        lang = self.lang
        self.setWindowTitle(t("settings_title", lang))
        self.lbl_lang.setText(t("language", lang))
        self.lbl_theme.setText(t("theme", lang))
        self.chk_startup.setText(t("tray_startup", lang))
        self.btn_adv.setText(t("advanced_options", lang) + (" ▾" if self.btn_adv.isChecked() else " ▸"))
        self.lbl_radius.setText(t("radius", lang))
        self.lbl_poll.setText(t("polling_interval", lang))
        self.chk_mm.setText(t("multi_monitor", lang))
        self._info_radius.setToolTip(t("info_radius", lang))
        self._info_poll.setToolTip(t("info_polling", lang))
        self._info_mm.setToolTip(t("info_multi_monitor", lang))
        self.btn_scripts.setText(t("tray_scripts", lang))
        self.btn_cancel.setText(t("cancel", lang))
        self.btn_save.setText(t("save_settings", lang))
        self.corner_panel.retranslate(lang)

    def _on_lang_changed(self, idx):
        self.lang = self.lang_combo.currentData()
        self.settings["language"] = self.lang
        save_settings(self.settings)
        self.engine.reload_settings()
        if hasattr(self.engine, 'app_instance'):
            self.engine.app_instance.update_tray_menu()
        self._retranslate_ui()

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
            self.engine.app_instance.apply_theme()

    def _save_close(self):
        self._apply()
        self.hide()
