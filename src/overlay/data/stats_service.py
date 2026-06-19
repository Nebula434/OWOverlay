"""Transform raw OverFast payloads into ``PlayerStats`` and cache hero icons.

This layer owns all knowledge of the API's JSON shape and the on-disk portrait
cache. It never touches Qt, so it is safe to call from the refresh worker
thread. The hero key->portrait map is fetched once and kept in memory;
portraits are downloaded to ``assets/heroes/`` once and reused thereafter.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import CardState, PlayerStats, _username_from_battletag
from .overfast_client import (
    GAMEMODE_COMPETITIVE,
    OverFastClient,
    OverFastError,
    PlayerNotFoundError,
    battletag_to_player_id,
)

# API payload field names (avoid scattering raw string keys through the logic).
_KEY_GENERAL = "general"
_KEY_HEROES = "heroes"
_KEY_WINRATE = "winrate"
_KEY_GAMES_PLAYED = "games_played"
_KEY_GAMES_WON = "games_won"
_KEY_TIME_PLAYED = "time_played"
_HERO_FIELD_KEY = "key"
_HERO_FIELD_NAME = "name"
_HERO_FIELD_PORTRAIT = "portrait"

_HERO_PORTRAIT_EXTENSION = ".png"
_NO_TIME_PLAYED = 0


class StatsService:
    """Fetch and shape teammate stats; manage the hero portrait cache."""

    def __init__(
        self,
        client: OverFastClient,
        assets_dir: Path,
        gamemode: str = GAMEMODE_COMPETITIVE,
    ) -> None:
        self._client = client
        self._assets_dir = assets_dir
        self._gamemode = gamemode
        self._hero_names: dict[str, str] = {}
        self._hero_portrait_urls: dict[str, str] = {}
        self._hero_map_loaded = False
        self._assets_dir.mkdir(parents=True, exist_ok=True)

    def fetch_player_stats(self, battletag: str) -> PlayerStats:
        """Resolve one teammate's stats, mapping any failure to a card state."""
        username = _username_from_battletag(battletag)
        player_id = battletag_to_player_id(battletag)
        try:
            summary = self._client.get_player_summary(player_id, self._gamemode)
            return self._build_stats(battletag, username, summary)
        except PlayerNotFoundError:
            return PlayerStats(
                battletag=battletag,
                username=username,
                state=CardState.PRIVATE_OR_NOT_FOUND,
            )
        except OverFastError as exc:
            return PlayerStats(
                battletag=battletag,
                username=username,
                state=CardState.NETWORK_ERROR,
                error_message=str(exc),
            )
        except Exception as exc:  # noqa: BLE001 - never let the worker crash
            return PlayerStats(
                battletag=battletag,
                username=username,
                state=CardState.NETWORK_ERROR,
                error_message=str(exc),
            )

    def _build_stats(
        self, battletag: str, username: str, summary: dict[str, Any]
    ) -> PlayerStats:
        general = summary.get(_KEY_GENERAL) or {}
        heroes = summary.get(_KEY_HEROES) or {}

        win_rate = _as_optional_float(general.get(_KEY_WINRATE))
        games_played = _as_optional_int(general.get(_KEY_GAMES_PLAYED))
        games_won = _as_optional_int(general.get(_KEY_GAMES_WON))

        hero_key = _most_played_hero_key(heroes)
        hero_name = self._resolve_hero_name(hero_key)
        hero_portrait = self._resolve_hero_portrait(hero_key)

        return PlayerStats(
            battletag=battletag,
            username=username,
            state=CardState.OK,
            hero_key=hero_key,
            hero_name=hero_name,
            hero_portrait=hero_portrait,
            win_rate=win_rate,
            games_played=games_played,
            games_won=games_won,
        )

    def _ensure_hero_map(self) -> None:
        if self._hero_map_loaded:
            return
        try:
            heroes = self._client.get_heroes()
        except OverFastError:
            self._hero_map_loaded = True
            return
        for hero in heroes:
            key = hero.get(_HERO_FIELD_KEY)
            if not key:
                continue
            name = hero.get(_HERO_FIELD_NAME)
            portrait = hero.get(_HERO_FIELD_PORTRAIT)
            if name:
                self._hero_names[key] = name
            if portrait:
                self._hero_portrait_urls[key] = portrait
        self._hero_map_loaded = True

    def _resolve_hero_name(self, hero_key: str | None) -> str | None:
        if hero_key is None:
            return None
        self._ensure_hero_map()
        return self._hero_names.get(hero_key, _key_to_display_name(hero_key))

    def _resolve_hero_portrait(self, hero_key: str | None) -> str | None:
        if hero_key is None:
            return None
        cached = self._cached_portrait_path(hero_key)
        if cached is not None:
            return cached
        self._ensure_hero_map()
        url = self._hero_portrait_urls.get(hero_key)
        if not url:
            return None
        return self._download_portrait(hero_key, url)

    def _cached_portrait_path(self, hero_key: str) -> str | None:
        path = self._portrait_path_for(hero_key)
        return str(path) if path.exists() else None

    def _download_portrait(self, hero_key: str, url: str) -> str | None:
        try:
            data = self._client.download_bytes(url)
        except OverFastError:
            return None
        path = self._portrait_path_for(hero_key)
        try:
            path.write_bytes(data)
        except OSError:
            return None
        return str(path)

    def _portrait_path_for(self, hero_key: str) -> Path:
        return self._assets_dir / f"{hero_key}{_HERO_PORTRAIT_EXTENSION}"


def _most_played_hero_key(heroes: dict[str, Any]) -> str | None:
    """Return the hero key with the largest ``time_played`` (most played)."""
    best_key: str | None = None
    best_time = _NO_TIME_PLAYED
    for key, stats in heroes.items():
        if not isinstance(stats, dict):
            continue
        time_played = _as_optional_int(stats.get(_KEY_TIME_PLAYED)) or _NO_TIME_PLAYED
        if best_key is None or time_played > best_time:
            best_key = key
            best_time = time_played
    return best_key


def _key_to_display_name(hero_key: str) -> str:
    """Best-effort title from a hero key when the names map is unavailable."""
    return hero_key.replace("-", " ").replace("_", " ").title()


def _as_optional_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _as_optional_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None
