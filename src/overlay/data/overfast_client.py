"""Thin HTTP client for the public OverFast API.

OverFast (https://overfast-api.tekrop.fr) mirrors Blizzard career profiles and
requires no API key. This client only knows how to talk HTTP and surface
results/errors; transforming raw payloads into ``PlayerStats`` is the job of
``stats_service``. A single ``httpx.Client`` instance is reused for every
request so connections are pooled.
"""
from __future__ import annotations

from typing import Any

import httpx

BASE_URL: str = "https://overfast-api.tekrop.fr"
GAMEMODE_COMPETITIVE: str = "competitive"
GAMEMODE_QUICKPLAY: str = "quickplay"
DEFAULT_TIMEOUT_SECONDS: float = 10.0
HTTP_STATUS_NOT_FOUND: int = 404


class OverFastError(Exception):
    """Raised when the API is unreachable or returns an unexpected response."""


class PlayerNotFoundError(OverFastError):
    """Raised on a 404: the profile is private or does not exist."""


def battletag_to_player_id(battletag: str) -> str:
    """Convert a ``Name#1234`` BattleTag into the API's ``Name-1234`` id."""
    return battletag.replace("#", "-")


class OverFastClient:
    """Reusable client wrapping the handful of endpoints the overlay needs."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout_seconds)

    def get_player_summary(
        self, player_id: str, gamemode: str = GAMEMODE_COMPETITIVE
    ) -> dict[str, Any]:
        """Fetch ``/players/{id}/stats/summary`` for the given gamemode.

        Raises ``PlayerNotFoundError`` on 404 (private/not found) and
        ``OverFastError`` for any other transport or HTTP failure.
        """
        path = f"/players/{player_id}/stats/summary"
        return self._get_json(path, params={"gamemode": gamemode})

    def get_heroes(self) -> list[dict[str, Any]]:
        """Fetch ``/heroes`` (key, name, portrait, role, ...) for icon mapping."""
        data = self._get_json("/heroes")
        if not isinstance(data, list):
            raise OverFastError("Unexpected /heroes payload: expected a list.")
        return data

    def download_bytes(self, url: str) -> bytes:
        """Download a raw asset (e.g. a hero portrait) and return its bytes."""
        try:
            response = self._client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OverFastError(f"Failed to download asset: {url}") from exc
        return response.content

    def close(self) -> None:
        """Close the underlying connection pool."""
        self._client.close()

    def _get_json(
        self, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        try:
            response = self._client.get(path, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == HTTP_STATUS_NOT_FOUND:
                raise PlayerNotFoundError(path) from exc
            raise OverFastError(f"HTTP error for {path}: {exc}") from exc
        except httpx.HTTPError as exc:
            raise OverFastError(f"Network error for {path}: {exc}") from exc
        try:
            return response.json()
        except ValueError as exc:
            raise OverFastError(f"Invalid JSON for {path}") from exc
