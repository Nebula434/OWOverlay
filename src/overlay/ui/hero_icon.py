"""Framed hero portrait drawn as the Overwatch shield/badge silhouette.

The frame is a shield: a rectangle with rounded top corners whose bottom edges
angle inward to a centered point. It carries a glowing cyan edge plus a darker
inner bevel line (mirroring the win-rate ring's double rim). The portrait is
clipped to the shield path. When a portrait is missing, loading or unknown, the
same shield + frame + glow are kept and the hero's initial (or ``?``) is centred
instead, so the card layout never shifts. All visual values come from
:mod:`overlay.ui.theme`.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QWidget

from . import theme

_HALF_DIVISOR = 2.0
# Each glow layer is one device pixel wider per side than the last.
_GLOW_LAYER_WIDTH_STEP = 2.0
_FALLBACK_PLACEHOLDER = "?"
_GEOMETRY_FLOOR = 0.0
# Glow pulse shape — mirrors winrate_ring so the badge and ring breathe in sync
# (DESIGN.md -> Motion: "the cyan ring/icon glow breathes on a slow loop with
# period GLOW_PULSE_PERIOD_MS"). The glow alpha eases between a dim floor and
# full strength, peaking halfway through the period.
_GLOW_PULSE_PEAK_AT = 0.5
_GLOW_PULSE_MIN_FACTOR = 0.5
_GLOW_PULSE_FULL_FACTOR = 1.0
_GLOW_PHASE_EMPTY = 0.0


def _build_shield_path(rect: QRectF, top_radius: float, point_depth: float) -> QPainterPath:
    """Build a shield silhouette: rounded-top rect tapering to a bottom point.

    The straight sides drop to ``point_depth`` above ``rect.bottom()`` and then
    angle inward to a centred point at the very bottom.
    """
    left = rect.left()
    right = rect.right()
    top = rect.top()
    bottom = rect.bottom()
    center_x = rect.center().x()
    sides_bottom = bottom - point_depth

    path = QPainterPath()
    path.moveTo(left + top_radius, top)
    path.lineTo(right - top_radius, top)
    path.quadTo(right, top, right, top + top_radius)
    path.lineTo(right, sides_bottom)
    path.lineTo(center_x, bottom)
    path.lineTo(left, sides_bottom)
    path.lineTo(left, top + top_radius)
    path.quadTo(left, top, left + top_radius, top)
    path.closeSubpath()
    return path


class HeroIcon(QWidget):
    """Shield-shaped hero icon that shows a portrait or a fallback glyph."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(theme.ICON_BADGE_WIDTH_PX, theme.ICON_BADGE_HEIGHT_PX)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._pixmap: QPixmap | None = None
        self._fallback_text = _FALLBACK_PLACEHOLDER
        self._glow_phase = _GLOW_PHASE_EMPTY

        # Looping idle "breathing" of the frame glow, mirroring winrate_ring's
        # _glow_anim / _glow_phase so the icon badge and the ring pulse together.
        self._glow_anim = QVariantAnimation(self)
        self._glow_anim.setStartValue(_GLOW_PHASE_EMPTY)
        self._glow_anim.setKeyValueAt(_GLOW_PULSE_PEAK_AT, _GLOW_PULSE_FULL_FACTOR)
        self._glow_anim.setEndValue(_GLOW_PHASE_EMPTY)
        self._glow_anim.setDuration(theme.GLOW_PULSE_PERIOD_MS)
        self._glow_anim.setLoopCount(-1)
        self._glow_anim.valueChanged.connect(self._on_glow_value)
        self._glow_anim.start()

    def _on_glow_value(self, value: object) -> None:
        self._glow_phase = float(value)
        self.update()

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
        outer_path = _build_shield_path(
            frame_rect, theme.ICON_TOP_CORNER_RADIUS_PX, theme.ICON_BOTTOM_POINT_DEPTH_PX
        )

        self._paint_glow(painter, outer_path)
        if self._pixmap is not None:
            self._paint_portrait(painter, outer_path, frame_rect)
        else:
            self._paint_fallback(painter, outer_path, frame_rect)
        self._paint_inner_bevel(painter, frame_rect)
        self._paint_frame(painter, outer_path)

    def _paint_glow(self, painter: QPainter, path: QPainterPath) -> None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pulse = _GLOW_PULSE_MIN_FACTOR + (
            _GLOW_PULSE_FULL_FACTOR - _GLOW_PULSE_MIN_FACTOR
        ) * self._glow_phase
        for layer in range(theme.ICON_FRAME_GLOW_BLUR_PX):
            fade = (theme.ICON_FRAME_GLOW_BLUR_PX - layer) / theme.ICON_FRAME_GLOW_BLUR_PX
            alpha = int(theme.COLOR_ICON_FRAME_GLOW_ALPHA * fade * pulse)
            width = theme.ICON_FRAME_WIDTH_PX + (layer + 1) * _GLOW_LAYER_WIDTH_STEP
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
            theme.build_font(
                theme.FONT_ICON_FALLBACK_SIZE_PT, theme.FONT_ICON_FALLBACK_WEIGHT
            )
        )
        painter.setPen(theme.qcolor(theme.COLOR_ICON_FALLBACK_TEXT))
        painter.drawText(frame_rect, Qt.AlignmentFlag.AlignCenter, self._fallback_text)

    def _paint_inner_bevel(self, painter: QPainter, frame_rect: QRectF) -> None:
        inset = theme.ICON_FRAME_WIDTH_PX
        inner_rect = frame_rect.adjusted(inset, inset, -inset, -inset)
        inner_path = _build_shield_path(
            inner_rect,
            max(_GEOMETRY_FLOOR, theme.ICON_TOP_CORNER_RADIUS_PX - inset),
            max(_GEOMETRY_FLOOR, theme.ICON_BOTTOM_POINT_DEPTH_PX - inset),
        )
        pen = QPen(theme.qcolor(theme.COLOR_ICON_FRAME_INNER))
        pen.setWidthF(theme.ICON_FRAME_INNER_WIDTH_PX)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(inner_path)

    def _paint_frame(self, painter: QPainter, path: QPainterPath) -> None:
        pen = QPen(theme.qcolor(theme.COLOR_ICON_FRAME))
        pen.setWidthF(theme.ICON_FRAME_WIDTH_PX)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
