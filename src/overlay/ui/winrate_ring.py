"""The win-rate donut: an Overwatch ult-charge ring re-themed as a win/loss split.

The ring paints, back to front: a soft cyan glow, a dark recessed track, the
green-win / red-loss band rendered as ``RING_TICK_COUNT`` short radial tick
segments (each tick = 2% of win rate) with a dark seam where the two arcs meet,
a beveled double rim, a cyan accent hairline, and the bold italic percentage in
the hole (the number large, the trailing ``%`` smaller). All colours, sizes and
timings come from :mod:`overlay.ui.theme`; this module contains only layout
maths, never design values.
"""
from __future__ import annotations

from PySide6.QtCore import Property, QPointF, QPropertyAnimation, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPen
from PySide6.QtWidgets import QWidget

from . import theme

# Qt expresses arc angles in 1/16th of a degree.
_QT_ANGLE_UNITS_PER_DEGREE = 16
# Win rate is a 0-100 percentage; the ring works in a 0..1 fraction internally.
_PERCENT_MAX = 100.0
_PERCENT_MIN = 0.0
_FRACTION_EMPTY = 0.0
# Geometry helpers.
_HALF_DIVISOR = 2.0
_SPAN_NONE = 0.0
_TICK_NONE = 0
# Glow pulse shape: peak halfway through the period, breathing between a dim
# floor and full strength.
_GLOW_PULSE_PEAK_AT = 0.5
_GLOW_PULSE_MIN_FACTOR = 0.5
_GLOW_PULSE_FULL_FACTOR = 1.0
# Center text. A single dash marks the no-data state.
_EMPTY_CENTER_TEXT = "\u2013"
_PERCENT_SUFFIX = "%"


def _clamp_percent(percent: float) -> float:
    return max(_PERCENT_MIN, min(_PERCENT_MAX, percent))


class _TextRun:
    """One run of text drawn with its own font (the number vs the ``%``)."""

    def __init__(self, text: str, font: QFont) -> None:
        self.text = text
        self.font = font
        self.advance = QFontMetricsF(font).horizontalAdvance(text)


class WinRateRing(QWidget):
    """A donut widget driven by a single :meth:`set_win_rate` call."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(theme.RING_DIAMETER_PX, theme.RING_DIAMETER_PX)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self._display_fraction = _FRACTION_EMPTY
        self._display_percent = _PERCENT_MIN
        self._has_data = False
        self._glow_phase = _GLOW_PULSE_MIN_FACTOR

        # The ticks sweep (fraction) and the centre number counts up (percent)
        # together so they land in sync, per DESIGN.md → Motion.
        self._fill_anim = QPropertyAnimation(self, b"displayFraction", self)
        self._fill_anim.setDuration(theme.RING_FILL_ANIM_MS)
        self._fill_anim.setEasingCurve(theme.easing_type(theme.RING_FILL_EASING))

        self._value_anim = QPropertyAnimation(self, b"displayPercent", self)
        self._value_anim.setDuration(theme.VALUE_TWEEN_MS)
        self._value_anim.setEasingCurve(theme.easing_type(theme.RING_FILL_EASING))

        self._glow_anim = QVariantAnimation(self)
        self._glow_anim.setStartValue(_FRACTION_EMPTY)
        self._glow_anim.setKeyValueAt(_GLOW_PULSE_PEAK_AT, _GLOW_PULSE_FULL_FACTOR)
        self._glow_anim.setEndValue(_FRACTION_EMPTY)
        self._glow_anim.setDuration(theme.GLOW_PULSE_PERIOD_MS)
        self._glow_anim.setLoopCount(-1)
        self._glow_anim.valueChanged.connect(self._on_glow_value)
        self._glow_anim.start()

    def set_win_rate(self, percent: float | None) -> None:
        """Animate the ring to ``percent`` (0-100), or clear it when ``None``.

        ``None`` represents no games / unresolved data and renders the neutral
        empty ring (track + rim only, no coloured ticks) with a dash in the
        centre.
        """
        self._fill_anim.stop()
        self._value_anim.stop()
        if percent is None:
            self._has_data = False
            self._animate_to(_FRACTION_EMPTY, _PERCENT_MIN)
            return
        self._has_data = True
        clamped = _clamp_percent(percent)
        self._animate_to(clamped / _PERCENT_MAX, clamped)

    def _animate_to(self, fraction: float, percent: float) -> None:
        self._fill_anim.setStartValue(self._display_fraction)
        self._fill_anim.setEndValue(fraction)
        self._value_anim.setStartValue(self._display_percent)
        self._value_anim.setEndValue(percent)
        self._fill_anim.start()
        self._value_anim.start()

    def _get_display_fraction(self) -> float:
        return self._display_fraction

    def _set_display_fraction(self, value: float) -> None:
        self._display_fraction = value
        self.update()

    displayFraction = Property(float, _get_display_fraction, _set_display_fraction)

    def _get_display_percent(self) -> float:
        return self._display_percent

    def _set_display_percent(self, value: float) -> None:
        self._display_percent = value
        self.update()

    displayPercent = Property(float, _get_display_percent, _set_display_percent)

    def _on_glow_value(self, value: object) -> None:
        self._glow_phase = float(value)
        self.update()

    # -- painting ----------------------------------------------------------
    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override name
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        base_rect = QRectF(self.rect())

        self._paint_glow(painter, base_rect)
        self._paint_track(painter, base_rect)
        if self._has_data:
            self._paint_ticks(painter, base_rect)
        self._paint_rims(painter, base_rect)
        self._paint_center_text(painter, base_rect)

    def _paint_glow(self, painter: QPainter, base_rect: QRectF) -> None:
        thickness = float(theme.RING_THICKNESS_PX)
        pulse = _GLOW_PULSE_MIN_FACTOR + (
            _GLOW_PULSE_FULL_FACTOR - _GLOW_PULSE_MIN_FACTOR
        ) * self._glow_phase
        for layer in range(theme.RING_GLOW_BLUR_PX):
            fade = (theme.RING_GLOW_BLUR_PX - layer) / theme.RING_GLOW_BLUR_PX
            alpha = int(theme.COLOR_RING_GLOW_ALPHA * fade * pulse)
            width = thickness + (theme.RING_GLOW_SPREAD_PX + layer) * _HALF_DIVISOR
            self._stroke_ellipse(
                painter, base_rect, thickness / _HALF_DIVISOR, width,
                theme.qcolor(theme.COLOR_RING_GLOW, alpha),
            )

    def _paint_track(self, painter: QPainter, base_rect: QRectF) -> None:
        thickness = float(theme.RING_THICKNESS_PX)
        # Recessed channel: inset from the outer edge by RING_TRACK_INSET_PX so
        # it reads as a recessed track and shows through the tick/seam gaps.
        track_width = thickness - theme.RING_TRACK_INSET_PX
        center_inset = (theme.RING_TRACK_INSET_PX + thickness) / _HALF_DIVISOR
        self._stroke_ellipse(
            painter, base_rect, center_inset, track_width,
            theme.qcolor(theme.COLOR_RING_TRACK),
        )

    def _paint_ticks(self, painter: QPainter, base_rect: QRectF) -> None:
        thickness = float(theme.RING_THICKNESS_PX)
        tick_center_inset = (theme.RING_TRACK_INSET_PX + thickness) / _HALF_DIVISOR
        sweep_sign = (
            -1.0
            if theme.RING_SWEEP_DIRECTION == theme.SWEEP_DIRECTION_CLOCKWISE
            else 1.0
        )
        slot_span = theme.RING_FULL_SWEEP_DEG / theme.RING_TICK_COUNT
        half_gap = theme.RING_TICK_GAP_DEG / _HALF_DIVISOR
        # Widen the normal tick gap into the dark seam at the colour boundaries.
        seam_extra = (theme.RING_ARC_GAP_DEG - theme.RING_TICK_GAP_DEG) / _HALF_DIVISOR

        green_count = round(self._display_fraction * theme.RING_TICK_COUNT)
        green_count = max(_TICK_NONE, min(theme.RING_TICK_COUNT, green_count))
        has_seam = _TICK_NONE < green_count < theme.RING_TICK_COUNT
        leading_seam = {0, green_count} if has_seam else set()
        trailing_seam = (
            {green_count - 1, theme.RING_TICK_COUNT - 1} if has_seam else set()
        )

        win_color = theme.qcolor(theme.COLOR_WIN_ARC)
        loss_color = theme.qcolor(theme.COLOR_LOSS_ARC)
        win_glow = theme.qcolor(theme.COLOR_WIN_ARC, theme.COLOR_ARC_GLOW_ALPHA)
        loss_glow = theme.qcolor(theme.COLOR_LOSS_ARC, theme.COLOR_ARC_GLOW_ALPHA)
        glow_width = theme.RING_TICK_LENGTH_PX + theme.RING_GLOW_SPREAD_PX * _HALF_DIVISOR

        for index in range(theme.RING_TICK_COUNT):
            is_win = index < green_count
            leading = half_gap + (seam_extra if index in leading_seam else _SPAN_NONE)
            trailing = half_gap + (seam_extra if index in trailing_seam else _SPAN_NONE)
            drawn_span = slot_span - leading - trailing
            if drawn_span <= _SPAN_NONE:
                continue
            slot_start = theme.RING_START_ANGLE_DEG + sweep_sign * index * slot_span
            draw_start = slot_start + sweep_sign * leading
            span = sweep_sign * drawn_span
            self._stroke_arc(
                painter, base_rect, tick_center_inset, glow_width,
                win_glow if is_win else loss_glow, draw_start, span,
            )
            self._stroke_arc(
                painter, base_rect, tick_center_inset, theme.RING_TICK_LENGTH_PX,
                win_color if is_win else loss_color, draw_start, span,
            )

    def _paint_rims(self, painter: QPainter, base_rect: QRectF) -> None:
        thickness = float(theme.RING_THICKNESS_PX)
        outer_inset = theme.RING_BEVEL_OUTER_WIDTH_PX / _HALF_DIVISOR
        self._stroke_ellipse(
            painter, base_rect, outer_inset, theme.RING_BEVEL_OUTER_WIDTH_PX,
            theme.qcolor(theme.COLOR_RING_BEVEL_OUTER),
        )
        inner_inset = thickness - theme.RING_BEVEL_INNER_WIDTH_PX / _HALF_DIVISOR
        self._stroke_ellipse(
            painter, base_rect, inner_inset, theme.RING_BEVEL_INNER_WIDTH_PX,
            theme.qcolor(theme.COLOR_RING_BEVEL_INNER),
        )
        accent_inset = (
            thickness
            - theme.RING_BEVEL_INNER_WIDTH_PX
            - theme.RING_ACCENT_WIDTH_PX / _HALF_DIVISOR
        )
        self._stroke_ellipse(
            painter, base_rect, accent_inset, theme.RING_ACCENT_WIDTH_PX,
            theme.qcolor(theme.COLOR_RING_ACCENT_CYAN),
        )

    def _paint_center_text(self, painter: QPainter, base_rect: QRectF) -> None:
        thickness = float(theme.RING_THICKNESS_PX)
        hole_rect = base_rect.adjusted(thickness, thickness, -thickness, -thickness)
        runs = self._build_text_runs()
        total_advance = sum(run.advance for run in runs)
        primary_metrics = QFontMetricsF(runs[0].font)
        center = hole_rect.center()
        baseline_y = center.y() + (
            primary_metrics.ascent() - primary_metrics.descent()
        ) / _HALF_DIVISOR
        start_x = center.x() - total_advance / _HALF_DIVISOR

        self._draw_runs(
            painter, runs, start_x,
            baseline_y + theme.CENTER_TEXT_SHADOW_OFFSET_PX,
            x_shift=theme.CENTER_TEXT_SHADOW_OFFSET_PX,
            color=theme.qcolor(
                theme.COLOR_CENTER_TEXT_SHADOW, theme.COLOR_CENTER_TEXT_SHADOW_ALPHA
            ),
        )
        self._draw_runs(
            painter, runs, start_x, baseline_y,
            x_shift=_SPAN_NONE, color=theme.qcolor(theme.COLOR_CENTER_TEXT),
        )

    def _build_text_runs(self) -> list[_TextRun]:
        center_font = theme.build_font(
            theme.FONT_RING_CENTER_SIZE_PT,
            theme.FONT_RING_CENTER_WEIGHT,
            italic=theme.FONT_RING_CENTER_ITALIC,
            letter_spacing_pct=theme.FONT_HUD_LETTER_SPACING_PCT,
        )
        if not self._has_data:
            return [_TextRun(_EMPTY_CENTER_TEXT, center_font)]
        suffix_font = theme.build_font(
            theme.FONT_RING_SUFFIX_SIZE_PT,
            theme.FONT_RING_CENTER_WEIGHT,
            italic=theme.FONT_RING_CENTER_ITALIC,
            letter_spacing_pct=theme.FONT_HUD_LETTER_SPACING_PCT,
        )
        number = str(round(self._display_percent))
        return [_TextRun(number, center_font), _TextRun(_PERCENT_SUFFIX, suffix_font)]

    def _draw_runs(
        self,
        painter: QPainter,
        runs: list[_TextRun],
        start_x: float,
        baseline_y: float,
        *,
        x_shift: float,
        color: QColor,
    ) -> None:
        painter.setPen(color)
        pen_x = start_x + x_shift
        for run in runs:
            painter.setFont(run.font)
            painter.drawText(QPointF(pen_x, baseline_y), run.text)
            pen_x += run.advance

    # -- low-level stroking ------------------------------------------------
    def _stroke_ellipse(
        self,
        painter: QPainter,
        base_rect: QRectF,
        center_inset: float,
        width: float,
        color: QColor,
    ) -> None:
        pen = self._make_pen(color, width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(
            base_rect.adjusted(center_inset, center_inset, -center_inset, -center_inset)
        )

    def _stroke_arc(
        self,
        painter: QPainter,
        base_rect: QRectF,
        center_inset: float,
        width: float,
        color: QColor,
        start_deg: float,
        span_deg: float,
    ) -> None:
        pen = self._make_pen(color, width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(
            base_rect.adjusted(center_inset, center_inset, -center_inset, -center_inset),
            int(round(start_deg * _QT_ANGLE_UNITS_PER_DEGREE)),
            int(round(span_deg * _QT_ANGLE_UNITS_PER_DEGREE)),
        )

    @staticmethod
    def _make_pen(color: QColor, width: float) -> QPen:
        pen = QPen(color)
        pen.setWidthF(width)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        return pen
