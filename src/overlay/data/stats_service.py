"""Transform raw OverFast payloads into ``PlayerStats`` and cache hero icons.

This layer owns all knowledge of the API's JSON shape, the win-rate basis
(competitive-only vs. competitive + quickplay combined), and the on-disk
portrait cache. It never touches Qt, so it is safe to call from the refresh
worker thread. The hero key->portrait map is fetched once and kept in memory;
portraits are downloaded to ``assets/heroes/`` once and reused thereafter.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import (
    BASIS_COMBINED,
    DEFAULT_BASIS,
    TOP_HERO_COUNT,
    VALID_BASES,
    CardState,
    HeroStat,
    PlayerStats,
    ProfileStats,
    basis_label,
    _username_from_battletag,
)
from .overfast_client import (
    GAMEMODE_COMPETITIVE,
    GAMEMODE_QUICKPLAY,
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
_NO_GAMES = 0
_PERCENT_SCALE = 100.0
_SINGLE_SUMMARY = 1


class StatsService:
    """Fetch and shape teammate stats; manage the hero portrait cache."""

    def __init__(
        self,
        client: OverFastClient,
        assets_dir: Path,
        basis: str = DEFAULT_BASIS,
    ) -> None:
        self._client = client
        self._assets_dir = assets_dir
        self._basis = basis if basis in VALID_BASES else DEFAULT_BASIS
        self._hero_names: dict[str, str] = {}
        self._hero_portrait_urls: dict[str, str] = {}
        self._hero_map_loaded = False
        # The overlay (teammates) and stats view (owner) run on separate worker
        # threads but share this one service + its hero-map cache; guard the
        # lazy load so a mode switch can never populate the cache twice at once.
        self._hero_map_lock = threading.Lock()
        self._assets_dir.mkdir(parents=True, exist_ok=True)

    def set_basis(self, basis: str) -> None:
        """Update the win-rate basis (used when settings are saved/reloaded)."""
        self._basis = basis if basis in VALID_BASES else DEFAULT_BASIS

    def fetch_player_stats(self, battletag: str) -> PlayerStats:
        """Resolve one teammate's stats, mapping any failure to a card state."""
        username = _username_from_battletag(battletag)
        player_id = battletag_to_player_id(battletag)
        try:
            summaries = self._fetch_summaries(player_id)
            return self._build_stats(battletag, username, summaries)
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

    def _fetch_summaries(self, player_id: str) -> list[dict[str, Any]]:
        """Fetch the summary payload(s) the configured basis requires.

        Competitive is always fetched (a 404 here means private/not found and
        propagates). For the combined basis quickplay is added best-effort; a
        quickplay-only failure is ignored so the card still shows competitive.
        """
        summaries = [self._client.get_player_summary(player_id, GAMEMODE_COMPETITIVE)]
        if self._basis == BASIS_COMBINED:
            try:
                summaries.append(
                    self._client.get_player_summary(player_id, GAMEMODE_QUICKPLAY)
                )
            except OverFastError:
                pass
        return summaries

    def _build_stats(
        self, battletag: str, username: str, summaries: list[dict[str, Any]]
    ) -> PlayerStats:
        win_rate, games_played, games_won = _merge_general(summaries)
        hero_totals = _merge_hero_time(summaries)
        hero_key = _most_played_hero_key(hero_totals)
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

    def fetch_profile_stats(self, battletag: str) -> ProfileStats:
        """Resolve the owner's own profile for the game-closed stats view.

        Surfaces overall win rate / games / wins / losses, the basis label and
        the top-3 most-played heroes. Failures map to the same card states as
        :meth:`fetch_player_stats` so the stats window can render all four data
        states without ever crashing the worker.
        """
        label = basis_label(self._basis)
        username = _username_from_battletag(battletag)
        player_id = battletag_to_player_id(battletag)
        try:
            summaries = self._fetch_summaries(player_id)
            return self._build_profile(battletag, username, label, summaries)
        except PlayerNotFoundError:
            return ProfileStats(
                battletag, username, CardState.PRIVATE_OR_NOT_FOUND, label
            )
        except OverFastError as exc:
            return ProfileStats(
                battletag, username, CardState.NETWORK_ERROR, label,
                error_message=str(exc),
            )
        except Exception as exc:  # noqa: BLE001 - never let the worker crash
            return ProfileStats(
                battletag, username, CardState.NETWORK_ERROR, label,
                error_message=str(exc),
            )

    def _build_profile(
        self, battletag: str, username: str, label: str, summaries: list[dict[str, Any]]
    ) -> ProfileStats:
        win_rate, games_played, games_won = _merge_general(summaries)
        games_lost = (
            games_played - games_won
            if games_played is not None and games_won is not None
            else None
        )
        return ProfileStats(
            battletag=battletag,
            username=username,
            state=CardState.OK,
            basis_label=label,
            win_rate=win_rate,
            games_played=games_played,
            games_won=games_won,
            games_lost=games_lost,
            top_heroes=self._top_hero_stats(summaries),
        )

    def _top_hero_stats(self, summaries: list[dict[str, Any]]) -> list[HeroStat]:
        """Build the top-``TOP_HERO_COUNT`` heroes by total time played."""
        aggregates = _merge_hero_details(summaries)
        ranked = sorted(
            aggregates.items(), key=lambda item: item[1].time_played, reverse=True
        )
        heroes: list[HeroStat] = []
        for hero_key, agg in ranked[:TOP_HERO_COUNT]:
            heroes.append(
                HeroStat(
                    hero_key=hero_key,
                    hero_name=self._resolve_hero_name(hero_key) or hero_key,
                    win_rate=agg.win_rate(),
                    games_played=agg.games_played if agg.has_games else None,
                    hero_portrait=self._resolve_hero_portrait(hero_key),
                )
            )
        return heroes

    def _ensure_hero_map(self) -> None:
        with self._hero_map_lock:
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


def _merge_general(
    summaries: list[dict[str, Any]],
) -> tuple[float | None, int | None, int | None]:
    """Combine the ``general`` blocks into (win_rate, games_played, games_won).

    A single summary keeps the API-reported win rate. Multiple summaries are
    merged by summing games and recomputing the win rate from total wins over
    total games, so the combined basis reflects real aggregate performance.
    """
    extracted = [_extract_general(summary.get(_KEY_GENERAL) or {}) for summary in summaries]
    if len(extracted) == _SINGLE_SUMMARY:
        played, won, win_rate = extracted[0]
        return win_rate, played, won

    total_played = _NO_GAMES
    total_won = _NO_GAMES
    has_games = False
    for played, won, _winrate in extracted:
        if played:
            total_played += played
            has_games = True
        if won:
            total_won += won
    if not has_games or total_played <= _NO_GAMES:
        return None, (total_played if has_games else None), None
    win_rate = total_won / total_played * _PERCENT_SCALE
    return win_rate, total_played, total_won


def _extract_general(
    general: dict[str, Any],
) -> tuple[int | None, int | None, float | None]:
    """Pull (games_played, games_won, win_rate) from one ``general`` block.

    Some gamemodes report a win rate but omit ``games_won``; derive wins from
    the win rate and games played in that case so merges stay consistent.
    """
    played = _as_optional_int(general.get(_KEY_GAMES_PLAYED))
    won = _as_optional_int(general.get(_KEY_GAMES_WON))
    win_rate = _as_optional_float(general.get(_KEY_WINRATE))
    if won is None and win_rate is not None and played is not None:
        won = round(win_rate / _PERCENT_SCALE * played)
    return played, won, win_rate


def _merge_hero_time(summaries: list[dict[str, Any]]) -> dict[str, int]:
    """Sum ``time_played`` per hero key across every summary."""
    totals: dict[str, int] = {}
    for summary in summaries:
        heroes = summary.get(_KEY_HEROES) or {}
        for key, stats in heroes.items():
            if not isinstance(stats, dict):
                continue
            time_played = _as_optional_int(stats.get(_KEY_TIME_PLAYED)) or _NO_TIME_PLAYED
            totals[key] = totals.get(key, _NO_TIME_PLAYED) + time_played
    return totals


@dataclass
class _HeroAgg:
    """Per-hero accumulator used to rank and rate the top-played heroes."""

    time_played: int = _NO_TIME_PLAYED
    games_played: int = _NO_GAMES
    games_won: int = _NO_GAMES
    has_games: bool = False

    def win_rate(self) -> float | None:
        """Win rate % from accumulated wins/games, or ``None`` with no games."""
        if not self.has_games or self.games_played <= _NO_GAMES:
            return None
        return self.games_won / self.games_played * _PERCENT_SCALE


def _merge_hero_details(summaries: list[dict[str, Any]]) -> dict[str, _HeroAgg]:
    """Aggregate time/games/wins per hero across summaries for the top-N list.

    Wins are derived from the reported win rate when a gamemode omits
    ``games_won`` (mirroring :func:`_extract_general`) so the combined basis
    rates each hero from real aggregate wins over games.
    """
    totals: dict[str, _HeroAgg] = {}
    for summary in summaries:
        heroes = summary.get(_KEY_HEROES) or {}
        for key, stats in heroes.items():
            if not isinstance(stats, dict):
                continue
            agg = totals.setdefault(key, _HeroAgg())
            agg.time_played += _as_optional_int(stats.get(_KEY_TIME_PLAYED)) or _NO_TIME_PLAYED
            played = _as_optional_int(stats.get(_KEY_GAMES_PLAYED))
            won = _as_optional_int(stats.get(_KEY_GAMES_WON))
            win_rate = _as_optional_float(stats.get(_KEY_WINRATE))
            if won is None and win_rate is not None and played is not None:
                won = round(win_rate / _PERCENT_SCALE * played)
            if played:
                agg.games_played += played
                agg.has_games = True
            if won:
                agg.games_won += won
    return totals


def _most_played_hero_key(hero_totals: dict[str, int]) -> str | None:
    """Return the hero key with the largest summed ``time_played``."""
    best_key: str | None = None
    best_time = _NO_TIME_PLAYED
    for key, time_played in hero_totals.items():
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
