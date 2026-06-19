"""Design tokens for the overlay — the single source of truth for the look.

Every visual constant from ``DESIGN.md`` lives here, grouped by category
(colors, sizes, typography, timing) and copied **verbatim** from the
``DESIGN.md`` "Design Tokens" table by name and value. No other module may
hard-code a visual value; they import the named tokens from this module
instead. A full re-theme of the overlay should require editing only this file,
never any logic.

A few small framework helpers (``qcolor``, ``build_font``, ``easing_type``,
``apply_font_override``) live alongside the tokens so the rest of the code can
turn a token into a concrete ``QColor`` / ``QFont`` without repeating Qt
boilerplate. A few framework baselines (e.g. ``ALPHA_OPAQUE``) that Qt requires
but ``DESIGN.md`` does not theme are also defined here so that no magic number
escapes this file.
"""
from __future__ import annotations

from PySide6.QtCore import QEasingCurve
from PySide6.QtGui import QColor, QFont

# ---------------------------------------------------------------------------
# Framework baselines (not design choices; required so logic stays magic-free)
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
COLOR_OVERLAY_BG: str = "#05080D"
COLOR_OVERLAY_BG_ALPHA: int = 0
COLOR_CARD_BG: str = "#0E1626"
COLOR_CARD_BG_ALPHA: int = 200
COLOR_CARD_BORDER: str = "#2A3A5C"
COLOR_CARD_BORDER_ALPHA: int = 230
COLOR_CARD_ACCENT: str = "#4DD2E6"
COLOR_RING_TRACK: str = "#0B1220"
COLOR_RING_BEVEL_OUTER: str = "#5FD8EC"
COLOR_RING_BEVEL_INNER: str = "#1C5C73"
COLOR_RING_ACCENT_CYAN: str = "#4DD2E6"
COLOR_RING_GLOW: str = "#36C8E0"
COLOR_RING_GLOW_ALPHA: int = 130
COLOR_WIN_ARC: str = "#6FD23A"
COLOR_LOSS_ARC: str = "#E53935"
COLOR_ARC_GLOW_ALPHA: int = 110
COLOR_CENTER_TEXT: str = "#F0F4F8"
COLOR_CENTER_TEXT_SHADOW: str = "#06090F"
COLOR_CENTER_TEXT_SHADOW_ALPHA: int = 170
COLOR_LABEL_PRIMARY: str = "#FFFFFF"
COLOR_LABEL_SECONDARY: str = "#9FB2CC"
COLOR_ICON_FRAME: str = "#4DD2E6"
COLOR_ICON_FRAME_INNER: str = "#1C5C73"
COLOR_ICON_FRAME_GLOW: str = "#36C8E0"
COLOR_ICON_FRAME_GLOW_ALPHA: int = 120
COLOR_ICON_BG_FALLBACK: str = "#1A2740"
COLOR_ICON_FALLBACK_TEXT: str = "#C8D6EC"
# Game-closed stats window + in-app config-screen control kit.
COLOR_STATS_WINDOW_BG: str = "#080D17"
COLOR_STATS_WINDOW_BG_ALPHA: int = 255
COLOR_BUTTON_PRIMARY_TEXT: str = "#06121A"
COLOR_ROW_HOVER_ALPHA: int = 30

# ---------------------------------------------------------------------------
# Sizes (device-independent pixels, except angles in degrees / direction name)
# ---------------------------------------------------------------------------
OVERLAY_MARGIN_X_PX: int = 24
OVERLAY_MARGIN_Y_PX: int = 96
CARD_WIDTH_PX: int = 320
CARD_HEIGHT_PX: int = 102
CARD_SPACING_PX: int = 14
CARD_CORNER_RADIUS_PX: int = 10
CARD_BORDER_WIDTH_PX: int = 1
CARD_ACCENT_WIDTH_PX: int = 3
CARD_PADDING_PX: int = 12
CARD_ELEMENT_GAP_PX: int = 10
LABEL_AREA_WIDTH_PX: int = 134
LABEL_AREA_HEIGHT_PX: int = 38
LABEL_LINE_SPACING_PX: int = 3
ICON_BADGE_WIDTH_PX: int = 64
ICON_BADGE_HEIGHT_PX: int = 78
ICON_FRAME_WIDTH_PX: int = 3
ICON_FRAME_INNER_WIDTH_PX: int = 1
ICON_TOP_CORNER_RADIUS_PX: int = 8
ICON_BOTTOM_POINT_DEPTH_PX: int = 12
ICON_FRAME_GLOW_BLUR_PX: int = 6
RING_DIAMETER_PX: int = 78
RING_THICKNESS_PX: int = 6
RING_TICK_LENGTH_PX: int = 5
RING_TRACK_INSET_PX: int = 1
RING_BEVEL_OUTER_WIDTH_PX: int = 1
RING_BEVEL_INNER_WIDTH_PX: int = 1
RING_ACCENT_WIDTH_PX: int = 1
RING_GLOW_BLUR_PX: int = 8
RING_GLOW_SPREAD_PX: int = 2
RING_FULL_SWEEP_DEG: int = 360
RING_START_ANGLE_DEG: int = 90
RING_SWEEP_DIRECTION: str = SWEEP_DIRECTION_CLOCKWISE
RING_TICK_COUNT: int = 50
RING_TICK_GAP_DEG: int = 2
RING_ARC_GAP_DEG: int = 6
CENTER_TEXT_SHADOW_OFFSET_PX: int = 1
# Game-closed stats view (window + profile header + top-hero list + footer).
STATS_WINDOW_WIDTH_PX: int = 480
STATS_WINDOW_PADDING_PX: int = 20
STATS_WINDOW_CORNER_RADIUS_PX: int = 16
STATS_SECTION_GAP_PX: int = 16
PROFILE_HEADER_HEIGHT_PX: int = 156
PROFILE_RING_DIAMETER_PX: int = 132
PROFILE_ELEMENT_GAP_PX: int = 20
STATS_READOUT_GAP_PX: int = 12
STATS_BODY_HEIGHT_PX: int = 334
RANK_BADGE_DIAMETER_PX: int = 24
RANK_BADGE_BORDER_WIDTH_PX: int = 2
STATS_MESSAGE_GAP_PX: int = 8
STATS_STATUS_DOT_DIAMETER_PX: int = 8
# In-app configuration screen (window + OW-HUD form-control kit).
CONFIG_WINDOW_WIDTH_PX: int = 520
CONFIG_LIST_MAX_HEIGHT_PX: int = 200
CONFIG_ROW_HEIGHT_PX: int = 40
CONFIG_FIELD_GAP_PX: int = 14
CONFIG_LABEL_GAP_PX: int = 6
CONFIG_COLUMN_GAP_PX: int = 14
CONTROL_HEIGHT_PX: int = 34
CONTROL_CORNER_RADIUS_PX: int = 6
CONTROL_PADDING_X_PX: int = 10
CONTROL_FOCUS_BORDER_WIDTH_PX: int = 2
ICON_BUTTON_SIZE_PX: int = 28
BUTTON_PADDING_X_PX: int = 16

# ---------------------------------------------------------------------------
# Typography (sizes in points)
# ---------------------------------------------------------------------------
FONT_FAMILY_PRIMARY: str = "Koverwatch"
# Fallback chain from DESIGN.md. Nothing copyrighted is bundled; the overlay
# relies on whichever family the system has, degrading down this condensed
# sans-serif chain. The user may also supply a font override via config, which
# is prepended ahead of this chain by :func:`apply_font_override`.
FONT_FAMILY_FALLBACKS: tuple[str, ...] = (
    "Big Noodle Titling",
    "Bebas Neue",
    "Oswald",
    "Arial Narrow",
    "sans-serif",
)
FONT_RING_CENTER_SIZE_PT: int = 20
FONT_RING_SUFFIX_SIZE_PT: int = 11
FONT_RING_CENTER_WEIGHT: int = 700
FONT_RING_CENTER_ITALIC: bool = True
FONT_HUD_LETTER_SPACING_PCT: int = 4
FONT_LABEL_NAME_SIZE_PT: int = 11
FONT_LABEL_NAME_WEIGHT: int = 700
FONT_LABEL_SUB_SIZE_PT: int = 9
FONT_LABEL_SUB_WEIGHT: int = 400
FONT_ICON_FALLBACK_SIZE_PT: int = 16
FONT_ICON_FALLBACK_WEIGHT: int = 700
# Game-closed stats view + config-screen typography.
FONT_PROFILE_NAME_SIZE_PT: int = 22
FONT_PROFILE_NAME_WEIGHT: int = 700
FONT_SECTION_TITLE_SIZE_PT: int = 13
FONT_SECTION_TITLE_WEIGHT: int = 700
FONT_SECTION_TITLE_LETTER_SPACING_PCT: int = 10
FONT_STAT_VALUE_SIZE_PT: int = 18
FONT_STAT_VALUE_WEIGHT: int = 700
FONT_STAT_CAPTION_SIZE_PT: int = 8
FONT_STAT_CAPTION_WEIGHT: int = 400
FONT_RANK_SIZE_PT: int = 12
FONT_RANK_WEIGHT: int = 700
FONT_STATS_MESSAGE_SIZE_PT: int = 15
FONT_STATS_MESSAGE_WEIGHT: int = 700
FONT_INPUT_SIZE_PT: int = 11
FONT_INPUT_WEIGHT: int = 400

# ---------------------------------------------------------------------------
# Timing (milliseconds, plus easing curve name)
# ---------------------------------------------------------------------------
RING_FILL_ANIM_MS: int = 600
RING_FILL_EASING: str = "OutCubic"
VALUE_TWEEN_MS: int = 600
CARD_FADE_IN_MS: int = 250
CARD_STAGGER_MS: int = 80
GLOW_PULSE_PERIOD_MS: int = 2400

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

# Optional user font override (set from config at startup); ``None`` means use
# the DESIGN.md primary + fallback chain unchanged.
_font_override_family: str | None = None


def apply_font_override(family: str | None) -> None:
    """Set (or clear) a user-supplied font family used ahead of the defaults.

    DECISIONS.md makes the HUD font user-configurable. When ``family`` is a
    non-empty string it is prepended to the family list returned by
    :func:`build_font`; ``None`` or empty restores the DESIGN.md default chain.
    """
    global _font_override_family
    cleaned = family.strip() if isinstance(family, str) else ""
    _font_override_family = cleaned or None


def font_families() -> list[str]:
    """Return the active font family list (override first, then DESIGN chain)."""
    families = [FONT_FAMILY_PRIMARY, *FONT_FAMILY_FALLBACKS]
    if _font_override_family is not None:
        return [_font_override_family, *families]
    return families


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

    The family list applies the active HUD font (any user override first) with
    the DESIGN.md condensed fallbacks. ``letter_spacing_pct`` is the extra
    spacing as a percentage of an em, added on top of the Qt normal baseline.
    """
    font = QFont()
    font.setFamilies(font_families())
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
