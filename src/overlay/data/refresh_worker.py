"""Off-thread fetch worker.

A ``RefreshWorker`` lives on a dedicated ``QThread``. Its ``refresh`` slot is
triggered (via a queued connection) once on startup and again on every timer
tick. It fetches each tracked teammate sequentially and emits ``player_updated``
per result so cards update incrementally, then emits ``cycle_finished``. All
network I/O therefore happens off the UI thread.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from .models import PlayerStats
from .stats_service import StatsService


class RefreshWorker(QObject):
    """Fetches every tracked teammate and reports results via signals."""

    player_updated = Signal(object)
    cycle_finished = Signal()

    def __init__(self, service: StatsService, battletags: list[str]) -> None:
        super().__init__()
        self._service = service
        self._battletags = list(battletags)

    @Slot()
    def refresh(self) -> None:
        """Fetch all tracked players; emit one signal per player, then finish."""
        for battletag in self._battletags:
            stats: PlayerStats = self._service.fetch_player_stats(battletag)
            self.player_updated.emit(stats)
        self.cycle_finished.emit()
