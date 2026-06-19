"""Plain data types shared between the data layer and the UI.

These have no Qt dependency so they can be created and tested off the UI
thread inside the refresh worker, then handed to widgets via signals.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# Win-rate basis choices (behavioral; user-configurable, default combined).
BASIS_COMPETITIVE = "competitive"
BASIS_COMBINED = "combined"
VALID_BASES: frozenset[str] = frozenset({BASIS_COMPETITIVE, BASIS_COMBINED})
DEFAULT_BASIS = BASIS_COMBINED

# Human-readable basis labels shown as the stats-view subtitle (UI copy, not a
# visual token — the basis only changes which value/label is shown).
BASIS_LABELS: dict[str, str] = {
    BASIS_COMPETITIVE: "Competitive",
    BASIS_COMBINED: "Competitive + Quick Play",
}


def basis_label(basis: str) -> str:
    """Return the display label for a win-rate ``basis`` (default if unknown)."""
    return BASIS_LABELS.get(basis, BASIS_LABELS[DEFAULT_BASIS])


# How many most-played heroes the game-closed view surfaces. Coupled by design
# to ``STATS_BODY_HEIGHT_PX`` (= this many card rows); product count, not a
# visual token, so it lives with the neutral data types rather than in theme.
TOP_HERO_COUNT = 3


class CardState(Enum):
    """Render state of a single teammate card."""

    LOADING = "loading"
    OK = "ok"
    PRIVATE_OR_NOT_FOUND = "private_or_not_found"
    NETWORK_ERROR = "network_error"


@dataclass
class PlayerStats:
    """Resolved stats for one tracked teammate.

    Fields are optional because, depending on ``state``, the data may not be
    available (e.g. a private profile or a network failure). Widgets read
    ``state`` first and only rely on the other fields when it is ``OK``.
    """

    battletag: str
    username: str
    state: CardState
    hero_key: str | None = None
    hero_name: str | None = None
    hero_portrait: str | None = None
    win_rate: float | None = None
    games_played: int | None = None
    games_won: int | None = None
    error_message: str | None = None

    @classmethod
    def loading(cls, battletag: str) -> "PlayerStats":
        """Build a placeholder shown before the first fetch completes."""
        return cls(
            battletag=battletag,
            username=_username_from_battletag(battletag),
            state=CardState.LOADING,
        )


@dataclass
class HeroStat:
    """One hero in the game-closed view's top-played list."""

    hero_key: str
    hero_name: str
    win_rate: float | None = None
    games_played: int | None = None
    hero_portrait: str | None = None


@dataclass
class ProfileStats:
    """The user's own profile for the game-closed stats view.

    Carries the overall win rate / games / wins / losses plus the configured
    basis label and the top-3 most-played heroes. Like :class:`PlayerStats`,
    consumers check ``state`` first; the numeric fields and ``top_heroes`` are
    only populated when ``state`` is ``OK``.
    """

    battletag: str
    username: str
    state: CardState
    basis_label: str
    win_rate: float | None = None
    games_played: int | None = None
    games_won: int | None = None
    games_lost: int | None = None
    top_heroes: list[HeroStat] = field(default_factory=list)
    error_message: str | None = None

    @classmethod
    def loading(cls, battletag: str, basis_label_text: str) -> "ProfileStats":
        """Build the placeholder shown while the first profile fetch runs."""
        return cls(
            battletag=battletag,
            username=_username_from_battletag(battletag),
            state=CardState.LOADING,
            basis_label=basis_label_text,
        )


def _username_from_battletag(battletag: str) -> str:
    """Return the human-readable name portion of a ``Name#1234`` BattleTag."""
    return battletag.split("#", 1)[0] if "#" in battletag else battletag
