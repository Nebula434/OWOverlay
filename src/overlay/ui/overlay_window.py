"""The overlay window: a transparent, click-through HUD hosting the card column.

This is the single top-level window. It is frameless, translucent, always-on-top,
click-through (input passes through to the game), and absent from the taskbar.
It hosts a vertical, non-overlapping column of :class:`PlayerCard` widgets,
anchored to a screen corner, and fades the column in/out (with a per-card
stagger) for the hero-select show/hide lifecycle. All visual values come from
:mod:`overlay.ui.theme`.
"""
from __future__ import annotations

from PySide6.QtCore import QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QPainter
from PySide6.QtWidgets import QGraphicsOpacityEffect, QVBoxLayout, QWidget

from ..config import (
    ANCHOR_BOTTOM_LEFT,
    ANCHOR_BOTTOM_RIGHT,
    ANCHOR_TOP_RIGHT,
    DEFAULT_ANCHOR,
)
from ..data.models import PlayerStats
from . import theme
from .player_card import PlayerCard

_OPACITY_HIDDEN = 0.0
_OPACITY_VISIBLE = 1.0
_LAYOUT_ZERO = 0
_GAP_COUNT_OFFSET = 1
_RIGHT_ANCHORS = frozenset({ANCHOR_TOP_RIGHT, ANCHOR_BOTTOM_RIGHT})
_BOTTOM_ANCHORS = frozenset({ANCHOR_BOTTOM_LEFT, ANCHOR_BOTTOM_RIGHT})


class OverlayWindow(QWidget):
    """Top-level transparent window stacking one card per tracked teammate."""

    def __init__(self, battletags: list[str], anchor: str = DEFAULT_ANCHOR) -> None:
        super().__init__()
        self._anchor = anchor
        self._visible = False
        self._cards: dict[str, PlayerCard] = {}
        self._effects: dict[str, QGraphicsOpacityEffect] = {}
        self._fade_anims: dict[str, QPropertyAnimation] = {}

        self._configure_window()
        self._build_column(battletags)

    def _configure_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

    def _build_column(self, battletags: list[str]) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            _LAYOUT_ZERO, _LAYOUT_ZERO, _LAYOUT_ZERO, _LAYOUT_ZERO
        )
        layout.setSpacing(theme.CARD_SPACING_PX)
        for battletag in battletags:
            card = PlayerCard(battletag, self)
            card.update_stats(PlayerStats.loading(battletag))
            effect = QGraphicsOpacityEffect(card)
            effect.setOpacity(_OPACITY_HIDDEN)
            card.setGraphicsEffect(effect)
            layout.addWidget(card)
            self._cards[battletag] = card
            self._effects[battletag] = effect

        count = len(battletags)
        width = theme.CARD_WIDTH_PX
        height = count * theme.CARD_HEIGHT_PX + (
            max(_LAYOUT_ZERO, count - _GAP_COUNT_OFFSET) * theme.CARD_SPACING_PX
        )
        self.setFixedSize(width, height)

    def update_player(self, stats: PlayerStats) -> None:
        """Route a resolved ``PlayerStats`` to its matching card (UI thread)."""
        card = self._cards.get(stats.battletag)
        if card is not None:
            card.update_stats(stats)

    # -- visibility lifecycle ---------------------------------------------
    def toggle(self) -> None:
        """Flip between the shown and hidden states."""
        if self._visible:
            self.hide_overlay()
        else:
            self.show_overlay()

    def show_overlay(self) -> None:
        """Show the column during hero select, fading cards in top-down.

        NOTE: the per-card top-down stagger (``CARD_STAGGER_MS``) is intentional
        per DESIGN.md ("cards may still stagger in"); it is the designed feel,
        not a bug. The first-press reliability fix for the show/hide hotkey lives
        in ``main.HotkeyManager`` (the press is now detected on the very first
        chord); this method already shows + raises + fades the whole column.
        """
        self._visible = True
        self._position_at_anchor()
        self.show()
        self.raise_()
        for index, battletag in enumerate(self._cards):
            delay = index * theme.CARD_STAGGER_MS
            QTimer.singleShot(delay, lambda tag=battletag: self._fade_in_card(tag))

    def hide_overlay(self) -> None:
        """Fade the whole column out, then stop painting once it is invisible."""
        self._visible = False
        for battletag in self._cards:
            self._fade_card(battletag, _OPACITY_HIDDEN)
        QTimer.singleShot(theme.CARD_FADE_IN_MS, self._finish_hide)

    def _fade_in_card(self, battletag: str) -> None:
        if self._visible:
            self._fade_card(battletag, _OPACITY_VISIBLE)

    def _fade_card(self, battletag: str, end: float) -> None:
        effect = self._effects.get(battletag)
        if effect is None:
            return
        existing = self._fade_anims.get(battletag)
        if existing is not None:
            existing.stop()
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(theme.CARD_FADE_IN_MS)
        anim.setStartValue(effect.opacity())
        anim.setEndValue(end)
        anim.start()
        self._fade_anims[battletag] = anim

    def _finish_hide(self) -> None:
        if not self._visible:
            self.hide()

    def _position_at_anchor(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        area = screen.geometry()
        right_aligned = self._anchor in _RIGHT_ANCHORS
        bottom_aligned = self._anchor in _BOTTOM_ANCHORS

        if right_aligned:
            x = area.left() + area.width() - self.width() - theme.OVERLAY_MARGIN_X_PX
        else:
            x = area.left() + theme.OVERLAY_MARGIN_X_PX
        if bottom_aligned:
            y = area.top() + area.height() - self.height() - theme.OVERLAY_MARGIN_Y_PX
        else:
            y = area.top() + theme.OVERLAY_MARGIN_Y_PX
        self.move(x, y)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override name
        # The window base is fully transparent (COLOR_OVERLAY_BG at alpha 0);
        # only the cards paint pixels. Writing the token color with a Source
        # composition keeps the surface cleared to exactly that value.
        painter = QPainter(self)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.fillRect(
            self.rect(),
            theme.qcolor(theme.COLOR_OVERLAY_BG, theme.COLOR_OVERLAY_BG_ALPHA),
        )
