import win32api
import win32con
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import QWidget
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt, QRectF, QTimer
# pyrefly: ignore [missing-import]
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

FADE_OUT_DURATION_MS = 400
FLASH_DURATION_MS = 500

class OverlayUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.size = 100
        self.resize(self.size, self.size)
        
        self.progress = 0.0
        self.fade_alpha = 1.0   # multiplier applied on top of progress-based alpha
        self.fading_out = False
        self.corner_id = None
        self.animation_style = "pulse"
        self.animation_color = "#ffffff"
        
        self.screen_w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        
        # Fade-out timer runs at 60fps
        self._fade_timer = QTimer()
        self._fade_timer.setInterval(16)
        self._fade_timer.timeout.connect(self._fade_step)

        self._flash_timer = QTimer()
        self._flash_timer.setInterval(30)
        self._flash_timer.timeout.connect(self._flash_tick)

    def show_corner(self, corner_id, animation_style="pulse", color="#ffffff"):
        # Cancel any ongoing fade or flash
        self._fade_timer.stop()
        self._flash_timer.stop()
        self.fading_out = False
        self.fade_alpha = 1.0
        
        self.corner_id = corner_id
        self.animation_style = animation_style
        self.animation_color = color
        self.progress = 0.0
        
        # Position the window
        if corner_id == "TOP_LEFT":
            self.move(0, 0)
        elif corner_id == "TOP_RIGHT":
            self.move(self.screen_w - self.size, 0)
        elif corner_id == "BOTTOM_LEFT":
            self.move(0, self.screen_h - self.size)
        elif corner_id == "BOTTOM_RIGHT":
            self.move(self.screen_w - self.size, self.screen_h - self.size)
            
        self.show()
        self.update()

    def set_progress(self, progress):
        if not self.fading_out:
            self.progress = progress
            self.update()

    def hide_corner(self):
        """Called when mouse leaves corner — start fade-out instead of hiding instantly."""
        if not self.fading_out and self.isVisible():
            self.fading_out = True
            self._fade_timer.start()
        elif not self.isVisible():
            self._do_hide()

    def trigger_complete(self):
        """Called when action fires — keep showing at full for a beat then fade out."""
        self.progress = 1.0
        self.fading_out = True
        self._fade_timer.start()

    def _fade_step(self):
        step = 16 / FADE_OUT_DURATION_MS
        self.fade_alpha = max(0.0, self.fade_alpha - step)
        self.update()
        if self.fade_alpha <= 0.0:
            self._fade_timer.stop()
            self._do_hide()

    def _do_hide(self):
        self.fading_out = False
        self.fade_alpha = 1.0
        self.progress = 0.0
        self.hide()

    def flash_corner(self, corner_id, animation_style="pulse", color="#ffffff"):
        """Animated flash for profile switch — grows then fades."""
        self._fade_timer.stop()
        self.fading_out = False
        self.fade_alpha = 1.0
        self.corner_id = corner_id
        self.animation_style = animation_style
        self.animation_color = color
        self.progress = 0.0

        if corner_id == "TOP_LEFT":
            self.move(0, 0)
        elif corner_id == "TOP_RIGHT":
            self.move(self.screen_w - self.size, 0)
        elif corner_id == "BOTTOM_LEFT":
            self.move(0, self.screen_h - self.size)
        elif corner_id == "BOTTOM_RIGHT":
            self.move(self.screen_w - self.size, self.screen_h - self.size)

        self.show()
        self._flash_step = 0
        self._flash_timer.start()

    def _flash_tick(self):
        self._flash_step += 1
        self.progress = min(1.0, self._flash_step / 12)
        self.update()
        if self._flash_step >= 24:  # ~720ms grow
            self._flash_timer.stop()
            self.progress = 1.0
            self.update()
            QTimer.singleShot(FLASH_DURATION_MS, self._trigger_flash_fade)

    def _trigger_flash_fade(self):
        if self.isVisible():
            self.fading_out = True
            self._fade_timer.start()

    def paintEvent(self, event):
        if not self.isVisible() or self.progress <= 0:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.fade_alpha)
        
        if self.animation_style == "arc":
            self._draw_arc(painter)
        elif self.animation_style == "corner_bar":
            self._draw_corner_bar(painter)
        elif self.animation_style == "pulse":
            self._draw_pulse(painter)
        elif self.animation_style == "fade_box":
            self._draw_fade_box(painter)
        elif self.animation_style == "ripple":
            self._draw_ripple(painter)
        elif self.animation_style == "halo":
            self._draw_halo(painter)
            
        painter.end()

    def _draw_arc(self, painter):
        padding = 20
        rect = QRectF(padding, padding, self.size - 2*padding, self.size - 2*padding)
        c = QColor(self.animation_color)
        c.setAlpha(50)
        pen_bg = QPen(c)
        pen_bg.setWidth(6)
        painter.setPen(pen_bg)
        painter.drawArc(rect, 0, 360 * 16)
        
        c_fg = QColor(self.animation_color)
        pen_fg = QPen(c_fg)
        pen_fg.setWidth(6)
        painter.setPen(pen_fg)
        
        start_angle = 90 * 16
        span_angle = -int(self.progress * 360 * 16)
        painter.drawArc(rect, start_angle, span_angle)

    def _draw_corner_bar(self, painter):
        thickness = 8
        length = int((self.size - 20) * self.progress)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(self.animation_color)))
        
        if self.corner_id == "TOP_LEFT":
            painter.drawRect(0, 0, length, thickness)
            painter.drawRect(0, 0, thickness, length)
        elif self.corner_id == "TOP_RIGHT":
            painter.drawRect(self.size - length, 0, length, thickness)
            painter.drawRect(self.size - thickness, 0, thickness, length)
        elif self.corner_id == "BOTTOM_LEFT":
            painter.drawRect(0, self.size - thickness, length, thickness)
            painter.drawRect(0, self.size - length, thickness, length)
        elif self.corner_id == "BOTTOM_RIGHT":
            painter.drawRect(self.size - length, self.size - thickness, length, thickness)
            painter.drawRect(self.size - thickness, self.size - length, thickness, length)

    def _draw_pulse(self, painter):
        radius = self.size * self.progress
        opacity = max(0, int(255 * (1.0 - self.progress)))
        
        painter.setPen(Qt.PenStyle.NoPen)
        c = QColor(self.animation_color)
        c.setAlpha(opacity)
        painter.setBrush(QBrush(c))
        
        cx, cy = 0, 0
        if self.corner_id == "TOP_LEFT": cx, cy = 0, 0
        elif self.corner_id == "TOP_RIGHT": cx, cy = self.size, 0
        elif self.corner_id == "BOTTOM_LEFT": cx, cy = 0, self.size
        elif self.corner_id == "BOTTOM_RIGHT": cx, cy = self.size, self.size
            
        painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

    def _draw_fade_box(self, painter):
        opacity = int(255 * self.progress)
        padding = 10
        rect = QRectF(padding, padding, self.size - 2*padding, self.size - 2*padding)
        
        painter.setPen(Qt.PenStyle.NoPen)
        c = QColor(self.animation_color)
        c.setAlpha(opacity)
        painter.setBrush(QBrush(c))
        painter.drawRoundedRect(rect, 10, 10)

    def _draw_ripple(self, painter):
        for i in range(3):
            radius = (self.size * 0.45) * (self.progress - i * 0.15)
            if radius <= 0:
                continue
            alpha = int(180 * (1.0 - i * 0.35) * (1.0 - abs(self.progress - 0.5) * 1.4))
            alpha = max(0, min(255, alpha))
            painter.setPen(Qt.PenStyle.NoPen)
            c = QColor(self.animation_color)
            c.setAlpha(alpha)
            painter.setBrush(QBrush(c))
            self._draw_quarter_circle(painter, radius)

    def _draw_halo(self, painter):
        progress = min(1.0, self.progress * 1.5)
        radii = [
            (self.size * 0.5 * progress, 80),
            (self.size * 0.35 * progress, 120),
            (self.size * 0.2 * progress, 200),
        ]
        for radius, base_alpha in radii:
            painter.setPen(Qt.PenStyle.NoPen)
            c = QColor(self.animation_color)
            c.setAlpha(int(base_alpha * (1.0 - abs(self.progress - 0.5) * 1.2)))
            c.setAlpha(max(0, min(255, c.alpha())))
            painter.setBrush(QBrush(c))
            self._draw_quarter_circle(painter, radius)

    def _draw_quarter_circle(self, painter, radius):
        if radius <= 0:
            return
        if self.corner_id == "TOP_LEFT":
            painter.drawEllipse(QRectF(0, 0, radius * 2, radius * 2))
        elif self.corner_id == "TOP_RIGHT":
            painter.drawEllipse(QRectF(self.size - radius * 2, 0, radius * 2, radius * 2))
        elif self.corner_id == "BOTTOM_LEFT":
            painter.drawEllipse(QRectF(0, self.size - radius * 2, radius * 2, radius * 2))
        elif self.corner_id == "BOTTOM_RIGHT":
            painter.drawEllipse(QRectF(self.size - radius * 2, self.size - radius * 2, radius * 2, radius * 2))
