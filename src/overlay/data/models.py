"""Plain data types shared between the data layer and the UI.

These have no Qt dependency so they can be created and tested off the UI
thread inside the refresh worker, then handed to widgets via signals.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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


def _username_from_battletag(battletag: str) -> str:
    """Return the human-readable name portion of a ``Name#1234`` BattleTag."""
    return battletag.split("#", 1)[0] if "#" in battletag else battletag
