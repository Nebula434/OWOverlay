"""A single teammate card: hero shield icon, win-rate ring, and stacked labels.

The card owns the rounded navy panel (with its cyan left accent bar and border),
the three vertically-centred row elements, and the logic that maps a
:class:`PlayerStats` into what each child shows for every card state (loading /
ok / private-or-not-found / network error). All visual values come from
:mod:`overlay.ui.theme`.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..data.models import CardState, PlayerStats
from . import theme
from .hero_icon import HeroIcon
from .winrate_ring import WinRateRing

_HALF_DIVISOR = 2.0
_LAYOUT_ZERO = 0

# Status strings shown on the secondary label per card state.
_TEXT_LOADING = "Loading\u2026"
_TEXT_PRIVATE = "Private / not found"
_TEXT_NETWORK = "Network error"
_TEXT_NO_DATA = "No data"
# Fallback glyphs for the hero icon when no portrait applies.
_GLYPH_PRIVATE = "?"
_GLYPH_NETWORK = "!"


class ElidedLabel(QLabel):
    """A single-line label that elides with an ellipsis instead of wrapping."""

    def __init__(self, color: QColor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color = color
        self._full_text = ""
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def setText(self, text: str) -> None:  # noqa: N802 - Qt override name
        self._full_text = text or ""
        self.updateGeometry()
        self.update()

    def text(self) -> str:  # noqa: D401 - Qt override name
        return self._full_text

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override name
        painter = QPainter(self)
        painter.setFont(self.font())
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(
            self._full_text, Qt.TextElideMode.ElideRight, self.width()
        )
        painter.setPen(self._color)
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            elided,
        )


class PlayerCard(QWidget):
    """Fixed-size card for one tracked teammate."""

    def __init__(self, battletag: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.battletag = battletag
        self.setFixedSize(theme.CARD_WIDTH_PX, theme.CARD_HEIGHT_PX)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self._icon = HeroIcon(self)
        self._ring = WinRateRing(self)
        self._name_label = ElidedLabel(theme.qcolor(theme.COLOR_LABEL_PRIMARY), self)
        self._sub_label = ElidedLabel(theme.qcolor(theme.COLOR_LABEL_SECONDARY), self)

        self._name_label.setFont(
            theme.build_font(theme.FONT_LABEL_NAME_SIZE_PT, theme.FONT_LABEL_NAME_WEIGHT)
        )
        self._sub_label.setFont(
            theme.build_font(theme.FONT_LABEL_SUB_SIZE_PT, theme.FONT_LABEL_SUB_WEIGHT)
        )

        self._build_layout()

    def _build_layout(self) -> None:
        labels = QWidget(self)
        labels.setFixedSize(theme.LABEL_AREA_WIDTH_PX, theme.LABEL_AREA_HEIGHT_PX)
        labels.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        labels_layout = QVBoxLayout(labels)
        labels_layout.setContentsMargins(_LAYOUT_ZERO, _LAYOUT_ZERO, _LAYOUT_ZERO, _LAYOUT_ZERO)
        labels_layout.setSpacing(theme.LABEL_LINE_SPACING_PX)
        # Top-aligned so the area's spare height leaves room for extra metric
        # lines later (DESIGN.md → Card spec).
        labels_layout.addWidget(self._name_label)
        labels_layout.addWidget(self._sub_label)
        labels_layout.addStretch()

        row = QHBoxLayout(self)
        row.setContentsMargins(
            theme.CARD_PADDING_PX,
            theme.CARD_PADDING_PX,
            theme.CARD_PADDING_PX,
            theme.CARD_PADDING_PX,
        )
        row.setSpacing(theme.CARD_ELEMENT_GAP_PX)
        row.addWidget(self._icon, _LAYOUT_ZERO, Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(self._ring, _LAYOUT_ZERO, Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(labels, _LAYOUT_ZERO, Qt.AlignmentFlag.AlignVCenter)
        row.addStretch()

    def update_stats(self, stats: PlayerStats) -> None:
        """Apply a resolved ``PlayerStats`` to every child widget."""
        self._name_label.setText(stats.username)
        handlers = {
            CardState.LOADING: self._apply_loading,
            CardState.OK: self._apply_ok,
            CardState.PRIVATE_OR_NOT_FOUND: self._apply_private,
            CardState.NETWORK_ERROR: self._apply_network_error,
        }
        handlers.get(stats.state, self._apply_network_error)(stats)

    def _apply_loading(self, stats: PlayerStats) -> None:
        self._ring.set_win_rate(None)
        self._icon.set_portrait(None)
        self._icon.set_fallback_text(stats.username)
        self._sub_label.setText(_TEXT_LOADING)

    def _apply_ok(self, stats: PlayerStats) -> None:
        self._ring.set_win_rate(stats.win_rate)
        self._icon.set_portrait(stats.hero_portrait)
        self._icon.set_fallback_text(stats.hero_name or stats.username)
        self._sub_label.setText(stats.hero_name or _TEXT_NO_DATA)

    def _apply_private(self, stats: PlayerStats) -> None:
        self._ring.set_win_rate(None)
        self._icon.set_portrait(None)
        self._icon.set_fallback_text(_GLYPH_PRIVATE)
        self._sub_label.setText(_TEXT_PRIVATE)

    def _apply_network_error(self, stats: PlayerStats) -> None:
        self._ring.set_win_rate(None)
        self._icon.set_portrait(None)
        self._icon.set_fallback_text(_GLYPH_NETWORK)
        self._sub_label.setText(_TEXT_NETWORK)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override name
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        border_inset = theme.CARD_BORDER_WIDTH_PX / _HALF_DIVISOR
        panel_rect = QRectF(self.rect()).adjusted(
            border_inset, border_inset, -border_inset, -border_inset
        )
        path = QPainterPath()
        path.addRoundedRect(
            panel_rect, theme.CARD_CORNER_RADIUS_PX, theme.CARD_CORNER_RADIUS_PX
        )

        painter.fillPath(path, theme.qcolor(theme.COLOR_CARD_BG, theme.COLOR_CARD_BG_ALPHA))
        self._paint_accent_bar(painter, path, panel_rect)

        pen = QPen(theme.qcolor(theme.COLOR_CARD_BORDER, theme.COLOR_CARD_BORDER_ALPHA))
        pen.setWidthF(theme.CARD_BORDER_WIDTH_PX)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    def _paint_accent_bar(
        self, painter: QPainter, panel_path: QPainterPath, panel_rect: QRectF
    ) -> None:
        painter.save()
        painter.setClipPath(panel_path)
        accent_rect = QRectF(
            panel_rect.left(),
            panel_rect.top(),
            theme.CARD_ACCENT_WIDTH_PX,
            panel_rect.height(),
        )
        painter.fillRect(accent_rect, theme.qcolor(theme.COLOR_CARD_ACCENT))
        painter.restore()
