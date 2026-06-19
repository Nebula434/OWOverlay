"""The win-rate donut: an Overwatch ult-charge ring re-themed as a win/loss split.

The ring paints, from back to front: a soft cyan glow, a dark recessed track,
the green win / red loss tick segments, a beveled double rim, a cyan accent
hairline, and the bold italic percentage in the hole. All colours, sizes and
timings come from :mod:`overlay.ui.theme`.
"""
from __future__ import annotations

from PySide6.QtCore import Property, QPropertyAnimation, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from . import theme

# Qt expresses arc angles in 1/16th of a degree.
_QT_ANGLE_UNITS_PER_DEGREE = 16
# Win rate is a 0-100 percentage; the ring works in a 0..1 fraction internally.
_PERCENT_MAX = 100.0
_PERCENT_MIN = 0.0
_FRACTION_FULL = 1.0
_FRACTION_EMPTY = 0.0
# Geometry helpers.
_HALF_DIVISOR = 2.0
# Sample each tick at its midpoint when deciding win vs loss colour.
_TICK_CENTER_OFFSET = 0.5
# Glow pulse shape: peak halfway through the period, breathing between a dim
# floor and full strength.
_GLOW_PULSE_PEAK_AT = 0.5
_GLOW_PULSE_MIN_FACTOR = 0.5
_GLOW_PULSE_FULL_FACTOR = 1.0
# Center text.
_EMPTY_CENTER_TEXT = "--"
_PERCENT_SUFFIX = "%"
# NOTE: DESIGN.md specifies the center-text shadow colour/alpha but no offset
# token; a 1px diagonal offset is used so the drop shadow reads as a shadow.
_CENTER_TEXT_SHADOW_OFFSET_PX = 1


def _clamp_percent(percent: float) -> float:
    return max(_PERCENT_MIN, min(_PERCENT_MAX, percent))


class WinRateRing(QWidget):
    """A donut widget driven by a single :meth:`set_win_rate` call."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(theme.RING_DIAMETER_PX, theme.RING_DIAMETER_PX)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self._display_fraction = _FRACTION_EMPTY
        self._has_data = False
        self._glow_phase = _GLOW_PULSE_MIN_FACTOR

        self._fill_anim = QPropertyAnimation(self, b"displayFraction", self)
        self._fill_anim.setDuration(theme.RING_FILL_ANIM_MS)
        self._fill_anim.setEasingCurve(theme.easing_type(theme.RING_FILL_EASING))

        self._glow_anim = QVariantAnimation(self)
        self._glow_anim.setStartValue(_FRACTION_EMPTY)
        self._glow_anim.setKeyValueAt(_GLOW_PULSE_PEAK_AT, _FRACTION_FULL)
        self._glow_anim.setEndValue(_FRACTION_EMPTY)
        self._glow_anim.setDuration(theme.GLOW_PULSE_PERIOD_MS)
        self._glow_anim.setLoopCount(-1)
        self._glow_anim.valueChanged.connect(self._on_glow_value)
        self._glow_anim.start()

    def set_win_rate(self, percent: float | None) -> None:
        """Animate the ring to ``percent`` (0-100), or clear it when ``None``.

        ``None`` represents no games / unresolved data and renders the neutral
        empty ring (track + rim only, no coloured arcs).
        """
        self._fill_anim.stop()
        if percent is None:
            self._has_data = False
            self._fill_anim.setStartValue(self._display_fraction)
            self._fill_anim.setEndValue(_FRACTION_EMPTY)
            self._fill_anim.start()
            return
        self._has_data = True
        target = _clamp_percent(percent) / _PERCENT_MAX
        self._fill_anim.setStartValue(self._display_fraction)
        self._fill_anim.setEndValue(target)
        self._fill_anim.start()

    def _get_display_fraction(self) -> float:
        return self._display_fraction

    def _set_display_fraction(self, value: float) -> None:
        self._display_fraction = value
        self.update()

    displayFraction = Property(float, _get_display_fraction, _set_display_fraction)

    def _on_glow_value(self, value: object) -> None:
        self._glow_phase = float(value)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override name
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        base_rect = QRectF(self.rect())
        thickness = float(theme.RING_THICKNESS_PX)
        half_thickness = thickness / _HALF_DIVISOR
        donut_rect = base_rect.adjusted(
            half_thickness, half_thickness, -half_thickness, -half_thickness
        )

        self._paint_glow(painter, donut_rect, thickness)
        self._stroke_ellipse(painter, donut_rect, thickness, theme.qcolor(theme.COLOR_RING_TRACK))
        if self._has_data:
            self._paint_ticks(painter, donut_rect, thickness)
        self._paint_rims(painter, base_rect, thickness)
        self._paint_center_text(painter, base_rect, thickness)

    def _paint_glow(self, painter: QPainter, donut_rect: QRectF, thickness: float) -> None:
        pulse = _GLOW_PULSE_MIN_FACTOR + (
            _GLOW_PULSE_FULL_FACTOR - _GLOW_PULSE_MIN_FACTOR
        ) * self._glow_phase
        for layer in range(theme.RING_GLOW_BLUR_PX):
            fade = (theme.RING_GLOW_BLUR_PX - layer) / theme.RING_GLOW_BLUR_PX
            alpha = int(theme.COLOR_RING_GLOW_ALPHA * fade * pulse)
            spread = theme.RING_GLOW_SPREAD_PX + layer
            width = thickness + spread * _HALF_DIVISOR
            self._stroke_ellipse(
                painter, donut_rect, width, theme.qcolor(theme.COLOR_RING_GLOW, alpha)
            )

    def _paint_ticks(self, painter: QPainter, donut_rect: QRectF, thickness: float) -> None:
        sweep_sign = (
            -1.0
            if theme.RING_SWEEP_DIRECTION == theme.SWEEP_DIRECTION_CLOCKWISE
            else 1.0
        )
        segment_span = theme.RING_FULL_SWEEP_DEG / theme.RING_TICK_COUNT
        half_gap = theme.RING_TICK_GAP_DEG / _HALF_DIVISOR
        drawn_span = segment_span - theme.RING_TICK_GAP_DEG
        win_color = theme.qcolor(theme.COLOR_WIN_ARC)
        loss_color = theme.qcolor(theme.COLOR_LOSS_ARC)

        for index in range(theme.RING_TICK_COUNT):
            tick_fraction = (index + _TICK_CENTER_OFFSET) / theme.RING_TICK_COUNT
            color = win_color if tick_fraction <= self._display_fraction else loss_color
            slot_start = theme.RING_START_ANGLE_DEG + sweep_sign * index * segment_span
            draw_start = slot_start + sweep_sign * half_gap
            span = sweep_sign * drawn_span
            self._draw_arc(painter, donut_rect, thickness, color, draw_start, span)

    def _paint_rims(self, painter: QPainter, base_rect: QRectF, thickness: float) -> None:
        outer_inset = theme.RING_BEVEL_OUTER_WIDTH_PX / _HALF_DIVISOR
        self._stroke_inset(
            painter,
            base_rect,
            outer_inset,
            theme.RING_BEVEL_OUTER_WIDTH_PX,
            theme.qcolor(theme.COLOR_RING_BEVEL_OUTER),
        )
        inner_inset = thickness - theme.RING_BEVEL_INNER_WIDTH_PX / _HALF_DIVISOR
        self._stroke_inset(
            painter,
            base_rect,
            inner_inset,
            theme.RING_BEVEL_INNER_WIDTH_PX,
            theme.qcolor(theme.COLOR_RING_BEVEL_INNER),
        )
        accent_inset = thickness - theme.RING_TRACK_INSET_PX
        self._stroke_inset(
            painter,
            base_rect,
            accent_inset,
            theme.RING_ACCENT_WIDTH_PX,
            theme.qcolor(theme.COLOR_RING_ACCENT_CYAN),
        )

    def _paint_center_text(self, painter: QPainter, base_rect: QRectF, thickness: float) -> None:
        hole_rect = base_rect.adjusted(thickness, thickness, -thickness, -thickness)
        painter.setFont(
            theme.build_font(
                theme.FONT_RING_CENTER_SIZE_PT,
                theme.FONT_RING_CENTER_WEIGHT,
                italic=theme.FONT_RING_CENTER_ITALIC,
                letter_spacing_pct=theme.FONT_HUD_LETTER_SPACING_PCT,
            )
        )
        text = self._center_text()
        align = Qt.AlignmentFlag.AlignCenter

        shadow_rect = hole_rect.translated(
            _CENTER_TEXT_SHADOW_OFFSET_PX, _CENTER_TEXT_SHADOW_OFFSET_PX
        )
        painter.setPen(
            theme.qcolor(theme.COLOR_CENTER_TEXT_SHADOW, theme.COLOR_CENTER_TEXT_SHADOW_ALPHA)
        )
        painter.drawText(shadow_rect, align, text)

        painter.setPen(theme.qcolor(theme.COLOR_CENTER_TEXT))
        painter.drawText(hole_rect, align, text)

    def _center_text(self) -> str:
        if not self._has_data:
            return _EMPTY_CENTER_TEXT
        percent = round(self._display_fraction * _PERCENT_MAX)
        return f"{percent}{_PERCENT_SUFFIX}"

    def _draw_arc(
        self,
        painter: QPainter,
        rect: QRectF,
        width: float,
        color: QColor,
        start_deg: float,
        span_deg: float,
    ) -> None:
        pen = QPen(color)
        pen.setWidthF(width)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(
            rect,
            int(round(start_deg * _QT_ANGLE_UNITS_PER_DEGREE)),
            int(round(span_deg * _QT_ANGLE_UNITS_PER_DEGREE)),
        )

    def _stroke_ellipse(
        self, painter: QPainter, rect: QRectF, width: float, color: QColor
    ) -> None:
        pen = QPen(color)
        pen.setWidthF(width)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)

    def _stroke_inset(
        self, painter: QPainter, base_rect: QRectF, inset: float, width: float, color: QColor
    ) -> None:
        self._stroke_ellipse(
            painter, base_rect.adjusted(inset, inset, -inset, -inset), width, color
        )
