"""Application configuration loading and saving.

Reads ``config.json`` from the repository root; if it is missing, falls back to
``config.example.json`` so the overlay still runs out of the box. Unknown or
missing fields fall back to the defaults below. These are behavioral settings
(which teammates to track, the user's own ``owner`` BattleTag, how often to
refresh, where to anchor, the win-rate basis, an optional font override, and the
show/hide + quit + config hotkeys) and are deliberately kept out of the visual
token file ``ui/theme.py``. :func:`save_config` writes the same shape back so the
in-app settings window can persist edits.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .data.models import DEFAULT_BASIS, VALID_BASES

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
DEFAULT_ANCHOR = ANCHOR_TOP_LEFT
DEFAULT_OWNER = ""
MIN_REFRESH_INTERVAL_SECONDS = 15
MAX_REFRESH_INTERVAL_SECONDS = 3600
# pynput hotkey strings (the "<modifier>+<key>" format parsed by
# pynput.keyboard.HotKey.parse).
DEFAULT_TOGGLE_HOTKEY = "<ctrl>+<alt>+o"
DEFAULT_QUIT_HOTKEY = "<ctrl>+<alt>+q"
DEFAULT_CONFIG_HOTKEY = "<ctrl>+<alt>+c"

# BattleTag format: a name (no '#'/whitespace) + '#' + a numeric discriminator.
_BATTLETAG_PATTERN = re.compile(r"^[^#\s]+#\d{3,}$")
_JSON_INDENT = 2

_CONFIG_FILENAME = "config.json"
_EXAMPLE_CONFIG_FILENAME = "config.example.json"

_FIELD_BATTLETAGS = "battletags"
_FIELD_OWNER = "owner"
_FIELD_REFRESH = "refresh_interval_seconds"
_FIELD_ANCHOR = "anchor"
_FIELD_WINRATE_BASIS = "winrate_basis"
_FIELD_FONT_FAMILY = "font_family"
_FIELD_TOGGLE_HOTKEY = "toggle_hotkey"
_FIELD_QUIT_HOTKEY = "quit_hotkey"
_FIELD_CONFIG_HOTKEY = "config_hotkey"


@dataclass
class AppConfig:
    """Resolved, validated runtime configuration."""

    battletags: list[str]
    owner: str = DEFAULT_OWNER
    refresh_interval_seconds: int = DEFAULT_REFRESH_INTERVAL_SECONDS
    anchor: str = DEFAULT_ANCHOR
    winrate_basis: str = DEFAULT_BASIS
    font_family: str | None = None
    toggle_hotkey: str = DEFAULT_TOGGLE_HOTKEY
    quit_hotkey: str = DEFAULT_QUIT_HOTKEY
    config_hotkey: str = DEFAULT_CONFIG_HOTKEY


def load_config(repo_root: Path) -> AppConfig:
    """Load configuration from the repo root, falling back to the example file."""
    raw = _read_config_dict(repo_root)
    return AppConfig(
        battletags=_clean_battletags(raw.get(_FIELD_BATTLETAGS)),
        owner=_clean_owner(raw.get(_FIELD_OWNER)),
        refresh_interval_seconds=_clean_interval(raw.get(_FIELD_REFRESH)),
        anchor=_clean_choice(raw.get(_FIELD_ANCHOR), VALID_ANCHORS, DEFAULT_ANCHOR),
        winrate_basis=_clean_choice(
            raw.get(_FIELD_WINRATE_BASIS), VALID_BASES, DEFAULT_BASIS
        ),
        font_family=_clean_optional_str(raw.get(_FIELD_FONT_FAMILY)),
        toggle_hotkey=_clean_hotkey(raw.get(_FIELD_TOGGLE_HOTKEY), DEFAULT_TOGGLE_HOTKEY),
        quit_hotkey=_clean_hotkey(raw.get(_FIELD_QUIT_HOTKEY), DEFAULT_QUIT_HOTKEY),
        config_hotkey=_clean_hotkey(
            raw.get(_FIELD_CONFIG_HOTKEY), DEFAULT_CONFIG_HOTKEY
        ),
    )


def save_config(repo_root: Path, config: AppConfig) -> bool:
    """Write ``config`` back to ``config.json``; return ``True`` on success.

    Serialises the same field shape :func:`load_config` reads, so the settings
    window persists through the one loader that also feeds the overlay and the
    stats view. Any filesystem failure is reported as ``False`` rather than
    raising, so the UI can surface a save error without crashing.
    """
    payload = {
        _FIELD_BATTLETAGS: list(config.battletags),
        _FIELD_OWNER: config.owner,
        _FIELD_REFRESH: config.refresh_interval_seconds,
        _FIELD_ANCHOR: config.anchor,
        _FIELD_WINRATE_BASIS: config.winrate_basis,
        _FIELD_FONT_FAMILY: config.font_family,
        _FIELD_TOGGLE_HOTKEY: config.toggle_hotkey,
        _FIELD_QUIT_HOTKEY: config.quit_hotkey,
        _FIELD_CONFIG_HOTKEY: config.config_hotkey,
    }
    try:
        path = repo_root / _CONFIG_FILENAME
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=_JSON_INDENT)
        return True
    except OSError:
        return False


def is_valid_battletag(value: str) -> bool:
    """Whether ``value`` matches the ``Name#1234`` BattleTag format."""
    return bool(_BATTLETAG_PATTERN.match(value.strip())) if isinstance(value, str) else False


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
    return [tag.strip() for tag in value if isinstance(tag, str) and tag.strip()]


def _clean_owner(value: object) -> str:
    return value.strip() if isinstance(value, str) else DEFAULT_OWNER


def _clean_interval(value: object) -> int:
    try:
        interval = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return DEFAULT_REFRESH_INTERVAL_SECONDS
    return min(max(interval, MIN_REFRESH_INTERVAL_SECONDS), MAX_REFRESH_INTERVAL_SECONDS)


def _clean_choice(value: object, valid: frozenset[str], default: str) -> str:
    if isinstance(value, str) and value in valid:
        return value
    return default


def _clean_optional_str(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _clean_hotkey(value: object, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default
