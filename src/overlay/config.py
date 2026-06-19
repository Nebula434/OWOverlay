"""Application configuration loading.

Reads ``config.json`` from the repository root; if it is missing, falls back to
``config.example.json`` so the overlay still runs out of the box. Unknown or
missing fields fall back to the defaults below. These are behavioral settings
(which teammates to track, how often to refresh, where to anchor) and are
deliberately kept out of the visual token file ``ui/theme.py``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .data.overfast_client import GAMEMODE_COMPETITIVE

# Anchor corner choices for the overlay column.
ANCHOR_TOP_LEFT = "top-left"
ANCHOR_TOP_RIGHT = "top-right"
ANCHOR_BOTTOM_LEFT = "bottom-left"
ANCHOR_BOTTOM_RIGHT = "bottom-right"
VALID_ANCHORS: frozenset[str] = frozenset(
    {ANCHOR_TOP_LEFT, ANCHOR_TOP_RIGHT, ANCHOR_BOTTOM_LEFT, ANCHOR_BOTTOM_RIGHT}
)

# Behavioral defaults (not visual tokens).
DEFAULT_REFRESH_INTERVAL_SECONDS = 60
DEFAULT_ANCHOR = ANCHOR_TOP_RIGHT
DEFAULT_GAMEMODE = GAMEMODE_COMPETITIVE
MIN_REFRESH_INTERVAL_SECONDS = 15

_CONFIG_FILENAME = "config.json"
_EXAMPLE_CONFIG_FILENAME = "config.example.json"

_FIELD_BATTLETAGS = "battletags"
_FIELD_REFRESH = "refresh_interval_seconds"
_FIELD_ANCHOR = "anchor"
_FIELD_GAMEMODE = "gamemode"


@dataclass
class AppConfig:
    """Resolved, validated runtime configuration."""

    battletags: list[str] = field(default_factory=list)
    refresh_interval_seconds: int = DEFAULT_REFRESH_INTERVAL_SECONDS
    anchor: str = DEFAULT_ANCHOR
    gamemode: str = DEFAULT_GAMEMODE


def load_config(repo_root: Path) -> AppConfig:
    """Load configuration from the repo root, falling back to the example file."""
    raw = _read_config_dict(repo_root)
    return AppConfig(
        battletags=_clean_battletags(raw.get(_FIELD_BATTLETAGS)),
        refresh_interval_seconds=_clean_interval(raw.get(_FIELD_REFRESH)),
        anchor=_clean_anchor(raw.get(_FIELD_ANCHOR)),
        gamemode=str(raw.get(_FIELD_GAMEMODE, DEFAULT_GAMEMODE)),
    )


def _read_config_dict(repo_root: Path) -> dict:
    for filename in (_CONFIG_FILENAME, _EXAMPLE_CONFIG_FILENAME):
        path = repo_root / filename
        if not path.exists():
            continue
        try:
            with path.open(encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError):
            continue
    return {}


def _clean_battletags(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(tag) for tag in value if isinstance(tag, str) and tag.strip()]


def _clean_interval(value: object) -> int:
    try:
        interval = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return DEFAULT_REFRESH_INTERVAL_SECONDS
    return max(interval, MIN_REFRESH_INTERVAL_SECONDS)


def _clean_anchor(value: object) -> str:
    if isinstance(value, str) and value in VALID_ANCHORS:
        return value
    return DEFAULT_ANCHOR
