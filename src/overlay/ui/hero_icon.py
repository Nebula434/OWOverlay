"""Framed hero portrait with a glowing cyan edge and a graceful fallback.

The frame is a rounded rectangle (the v1 shape; see DESIGN.md Open Question 3
for the deferred shield silhouette). When a portrait is missing, loading or
unknown, the same frame and glow are kept and the hero's initial (or ``?``) is
centred instead, so the card layout never shifts.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QWidget

from . import theme

_HALF_DIVISOR = 2.0
_FALLBACK_PLACEHOLDER = "?"


class HeroIcon(QWidget):
    """Square hero icon that shows a portrait or a fallback glyph."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(theme.ICON_SIZE_PX, theme.ICON_SIZE_PX)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._pixmap: QPixmap | None = None
        self._fallback_text = _FALLBACK_PLACEHOLDER

    def set_portrait(self, path: str | None) -> None:
        """Set the portrait from a cached file path, or clear it when ``None``."""
        if not path:
            self._pixmap = None
            self.update()
            return
        pixmap = QPixmap(path)
        self._pixmap = None if pixmap.isNull() else pixmap
        self.update()

    def set_fallback_text(self, text: str | None) -> None:
        """Set the glyph shown when no portrait is available (e.g. an initial)."""
        cleaned = (text or "").strip()
        self._fallback_text = cleaned[:1].upper() if cleaned else _FALLBACK_PLACEHOLDER
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override name
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        frame_inset = theme.ICON_FRAME_WIDTH_PX / _HALF_DIVISOR
        frame_rect = QRectF(self.rect()).adjusted(
            frame_inset, frame_inset, -frame_inset, -frame_inset
        )
        path = QPainterPath()
        path.addRoundedRect(
            frame_rect, theme.ICON_CORNER_RADIUS_PX, theme.ICON_CORNER_RADIUS_PX
        )

        self._paint_glow(painter, path)
        if self._pixmap is not None:
            self._paint_portrait(painter, path, frame_rect)
        else:
            self._paint_fallback(painter, path, frame_rect)
        self._paint_frame(painter, path)

    def _paint_glow(self, painter: QPainter, path: QPainterPath) -> None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for layer in range(theme.ICON_FRAME_GLOW_BLUR_PX):
            fade = (theme.ICON_FRAME_GLOW_BLUR_PX - layer) / theme.ICON_FRAME_GLOW_BLUR_PX
            alpha = int(theme.COLOR_ICON_FRAME_GLOW_ALPHA * fade)
            width = theme.ICON_FRAME_WIDTH_PX + (layer + 1) * _HALF_DIVISOR
            pen = QPen(theme.qcolor(theme.COLOR_ICON_FRAME_GLOW, alpha))
            pen.setWidthF(width)
            painter.setPen(pen)
            painter.drawPath(path)

    def _paint_portrait(
        self, painter: QPainter, path: QPainterPath, frame_rect: QRectF
    ) -> None:
        assert self._pixmap is not None
        painter.save()
        painter.setClipPath(path)
        target_size = frame_rect.toRect().size()
        scaled = self._pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        top_left = QPointF(
            frame_rect.center().x() - scaled.width() / _HALF_DIVISOR,
            frame_rect.center().y() - scaled.height() / _HALF_DIVISOR,
        )
        painter.drawPixmap(top_left, scaled)
        painter.restore()

    def _paint_fallback(
        self, painter: QPainter, path: QPainterPath, frame_rect: QRectF
    ) -> None:
        painter.fillPath(path, theme.qcolor(theme.COLOR_ICON_BG_FALLBACK))
        painter.setFont(
            theme.build_font(theme.FONT_ICON_FALLBACK_SIZE_PT, theme.FONT_LABEL_NAME_WEIGHT)
        )
        painter.setPen(theme.qcolor(theme.COLOR_ICON_FALLBACK_TEXT))
        painter.drawText(frame_rect, Qt.AlignmentFlag.AlignCenter, self._fallback_text)

    def _paint_frame(self, painter: QPainter, path: QPainterPath) -> None:
        pen = QPen(theme.qcolor(theme.COLOR_ICON_FRAME))
        pen.setWidthF(theme.ICON_FRAME_WIDTH_PX)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
