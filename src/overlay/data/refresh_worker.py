"""Off-thread fetch workers.

Both workers live on a dedicated ``QThread`` and expose a ``refresh`` slot
triggered (via a queued connection) once on startup and again on every timer
tick, so all network I/O happens off the UI thread:

- ``RefreshWorker`` fetches each tracked teammate and emits ``player_updated``
  per result so the overlay cards update incrementally, then ``cycle_finished``.
- ``ProfileWorker`` fetches the owner's own profile (overall stats + top-3
  heroes) for the game-closed stats view and emits ``profile_updated``.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from .models import PlayerStats, ProfileStats
from .stats_service import StatsService


class RefreshWorker(QObject):
    """Fetches every tracked teammate and reports results via signals."""

    player_updated = Signal(object)
    cycle_finished = Signal()

    def __init__(self, service: StatsService, battletags: list[str]) -> None:
        super().__init__()
        self._service = service
        self._battletags = list(battletags)

    @Slot(object)
    def set_battletags(self, battletags: list[str]) -> None:
        """Replace the tracked list (queued from the UI thread on reload)."""
        self._battletags = list(battletags)

    @Slot()
    def refresh(self) -> None:
        """Fetch all tracked players; emit one signal per player, then finish."""
        for battletag in self._battletags:
            stats: PlayerStats = self._service.fetch_player_stats(battletag)
            self.player_updated.emit(stats)
        self.cycle_finished.emit()


class ProfileWorker(QObject):
    """Fetches the owner's own profile for the game-closed stats view."""

    profile_updated = Signal(object)

    def __init__(self, service: StatsService, owner: str) -> None:
        super().__init__()
        self._service = service
        self._owner = owner

    @Slot(object)
    def set_owner(self, owner: str) -> None:
        """Replace the owner BattleTag (queued from the UI thread on reload)."""
        self._owner = owner

    @Slot()
    def refresh(self) -> None:
        """Fetch the owner profile and emit it, unless no owner is configured."""
        if not self._owner:
            return
        profile: ProfileStats = self._service.fetch_profile_stats(self._owner)
        self.profile_updated.emit(profile)
