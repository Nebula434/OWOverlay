"""Design tokens for the overlay.

Every visual constant from ``DESIGN.md`` lives here, grouped by category
(colors, sizes, typography, timing). No other module may hard-code a visual
value; they import the named tokens from this module instead. A full re-theme
of the overlay should require editing only this file, never any logic.

The token names and values are copied verbatim from the ``DESIGN.md`` token
table. A few small framework helpers (``qcolor``, ``build_font``,
``easing_type``) live alongside the tokens so the rest of the code can turn a
token into a concrete ``QColor`` / ``QFont`` without repeating Qt boilerplate.
"""
from __future__ import annotations

from PySide6.QtCore import QEasingCurve
from PySide6.QtGui import QColor, QFont

# ---------------------------------------------------------------------------
# Shared constants (framework baselines, not design choices)
# ---------------------------------------------------------------------------
ALPHA_OPAQUE: int = 255
LETTER_SPACING_NORMAL_PCT: float = 100.0  # Qt PercentageSpacing baseline (no extra spacing).

# Allowed values for ``RING_SWEEP_DIRECTION`` so logic compares against names,
# not raw string literals.
SWEEP_DIRECTION_CLOCKWISE: str = "clockwise"
SWEEP_DIRECTION_COUNTERCLOCKWISE: str = "counterclockwise"

# ---------------------------------------------------------------------------
# Colors
# Hex strings are 6-digit ``#RRGGBB``. Matching ``*_ALPHA`` tokens are 0-255
# integers so a QColor can be built without hex-alpha-ordering ambiguity.
# ---------------------------------------------------------------------------
COLOR_OVERLAY_BG: str = "#000000"
COLOR_OVERLAY_BG_ALPHA: int = 0
COLOR_CARD_BG: str = "#0E1626"
COLOR_CARD_BG_ALPHA: int = 210
COLOR_CARD_BORDER: str = "#2A3A5C"
COLOR_RING_TRACK: str = "#0B1220"
COLOR_RING_BEVEL_OUTER: str = "#5FD8EC"
COLOR_RING_BEVEL_INNER: str = "#1C5C73"
COLOR_RING_ACCENT_CYAN: str = "#4DD2E6"
COLOR_RING_GLOW: str = "#36C8E0"
COLOR_RING_GLOW_ALPHA: int = 140
COLOR_WIN_ARC: str = "#34C759"
COLOR_LOSS_ARC: str = "#E5383B"
COLOR_CENTER_TEXT: str = "#F0F4F8"
COLOR_CENTER_TEXT_SHADOW: str = "#0A1018"
COLOR_CENTER_TEXT_SHADOW_ALPHA: int = 160
COLOR_LABEL_PRIMARY: str = "#FFFFFF"
COLOR_LABEL_SECONDARY: str = "#9FB2CC"
COLOR_ICON_FRAME: str = "#4DD2E6"
COLOR_ICON_FRAME_GLOW: str = "#36C8E0"
COLOR_ICON_FRAME_GLOW_ALPHA: int = 130
COLOR_ICON_BG_FALLBACK: str = "#1A2740"
COLOR_ICON_FALLBACK_TEXT: str = "#C8D6EC"

# ---------------------------------------------------------------------------
# Sizes (device-independent pixels, except angles in degrees / direction name)
# ---------------------------------------------------------------------------
OVERLAY_MARGIN_PX: int = 24
CARD_WIDTH_PX: int = 320
CARD_HEIGHT_PX: int = 96
CARD_SPACING_PX: int = 12
CARD_CORNER_RADIUS_PX: int = 12
CARD_BORDER_WIDTH_PX: int = 1
CARD_PADDING_PX: int = 12
CARD_ELEMENT_GAP_PX: int = 12
ICON_SIZE_PX: int = 72
ICON_FRAME_WIDTH_PX: int = 3
ICON_CORNER_RADIUS_PX: int = 10
ICON_FRAME_GLOW_BLUR_PX: int = 6
RING_DIAMETER_PX: int = 72
RING_THICKNESS_PX: int = 10
RING_TRACK_INSET_PX: int = 2
RING_BEVEL_OUTER_WIDTH_PX: int = 2
RING_BEVEL_INNER_WIDTH_PX: int = 2
RING_ACCENT_WIDTH_PX: int = 1
RING_GLOW_BLUR_PX: int = 8
RING_GLOW_SPREAD_PX: int = 2
RING_FULL_SWEEP_DEG: int = 360
RING_START_ANGLE_DEG: int = 90
RING_SWEEP_DIRECTION: str = SWEEP_DIRECTION_CLOCKWISE
RING_TICK_COUNT: int = 36
RING_TICK_GAP_DEG: int = 2
LABEL_AREA_MIN_WIDTH_PX: int = 120
LABEL_LINE_SPACING_PX: int = 4

# ---------------------------------------------------------------------------
# Typography (sizes in points)
# ---------------------------------------------------------------------------
FONT_FAMILY_PRIMARY: str = "Oswald"
# NOTE: DESIGN.md lists the fallback chain "Bebas Neue", "Arial Narrow",
# sans-serif. The overlay does not bundle a copyrighted font (Open Question 7);
# it relies on a system-installed Oswald and degrades to these condensed
# sans-serif fallbacks.
FONT_FAMILY_FALLBACKS: tuple[str, ...] = ("Bebas Neue", "Arial Narrow", "sans-serif")
FONT_RING_CENTER_SIZE_PT: int = 20
FONT_RING_CENTER_WEIGHT: int = 700
FONT_RING_CENTER_ITALIC: bool = True
FONT_HUD_LETTER_SPACING_PCT: int = 4
FONT_LABEL_NAME_SIZE_PT: int = 12
FONT_LABEL_NAME_WEIGHT: int = 700
FONT_LABEL_SUB_SIZE_PT: int = 10
FONT_LABEL_SUB_WEIGHT: int = 400
FONT_ICON_FALLBACK_SIZE_PT: int = 18

# ---------------------------------------------------------------------------
# Timing (milliseconds, plus easing curve name)
# ---------------------------------------------------------------------------
RING_FILL_ANIM_MS: int = 600
RING_FILL_EASING: str = "OutCubic"
VALUE_TWEEN_MS: int = 600
CARD_FADE_IN_MS: int = 250
CARD_STAGGER_MS: int = 80
GLOW_PULSE_PERIOD_MS: int = 2400
HOVER_TRANSITION_MS: int = 150

# ---------------------------------------------------------------------------
# Helpers: turn tokens into concrete Qt objects
# ---------------------------------------------------------------------------
_EASING_BY_NAME: dict[str, QEasingCurve.Type] = {
    "Linear": QEasingCurve.Type.Linear,
    "InCubic": QEasingCurve.Type.InCubic,
    "OutCubic": QEasingCurve.Type.OutCubic,
    "InOutCubic": QEasingCurve.Type.InOutCubic,
    "OutQuad": QEasingCurve.Type.OutQuad,
}


def qcolor(hex_rgb: str, alpha: int = ALPHA_OPAQUE) -> QColor:
    """Return a ``QColor`` from a ``#RRGGBB`` token and a 0-255 alpha token."""
    color = QColor(hex_rgb)
    color.setAlpha(alpha)
    return color


def build_font(
    size_pt: int,
    weight: int,
    *,
    italic: bool = False,
    letter_spacing_pct: int | None = None,
) -> QFont:
    """Build a ``QFont`` from typography tokens.

    The family list applies the primary HUD font with its condensed fallbacks.
    ``letter_spacing_pct`` is the extra spacing as a percentage of an em (added
    on top of the Qt normal baseline).
    """
    font = QFont()
    font.setFamilies([FONT_FAMILY_PRIMARY, *FONT_FAMILY_FALLBACKS])
    font.setPointSize(size_pt)
    font.setWeight(QFont.Weight(weight))
    font.setItalic(italic)
    if letter_spacing_pct is not None:
        font.setLetterSpacing(
            QFont.SpacingType.PercentageSpacing,
            LETTER_SPACING_NORMAL_PCT + letter_spacing_pct,
        )
    return font


def easing_type(name: str) -> QEasingCurve.Type:
    """Map an easing token name to a ``QEasingCurve.Type`` (linear fallback)."""
    return _EASING_BY_NAME.get(name, QEasingCurve.Type.Linear)
