"""Off-thread Overwatch process detection.

``GameMonitor`` polls for the Overwatch client process on a timer and emits
``game_state_changed(running)`` whenever the running/closed state flips (plus
once for the initial state). It drives the app's mutually-exclusive surfaces:
the teammate overlay while the game runs, the stats view while it is closed.

Detection uses :mod:`psutil` when installed. If psutil is missing we cannot
scan processes, so the app degrades to *assuming the game is running* — that
keeps the original teammate-overlay path working rather than forcing the stats
view. The poll runs on the monitor's own ``QThread``, so enumerating processes
never blocks the UI thread.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal, Slot

try:
    import psutil
except ImportError:  # pragma: no cover - optional dependency
    psutil = None  # type: ignore[assignment]

# Windows client executable name(s), matched case-insensitively.
_OVERWATCH_PROCESS_NAMES: frozenset[str] = frozenset({"overwatch.exe"})
_PROCESS_NAME_ATTR = "name"
# How often to re-scan the process list (behavioral, not a visual token).
_POLL_INTERVAL_MS = 5000
# Fallback when detection is unavailable/failing: assume running so the overlay
# (the original behavior) stays usable instead of being hidden behind the view.
_ASSUME_RUNNING_ON_FAILURE = True


def detection_available() -> bool:
    """Whether real process detection is possible (psutil importable)."""
    return psutil is not None


class GameMonitor(QObject):
    """Polls for the Overwatch process and signals running/closed transitions."""

    game_state_changed = Signal(bool)

    def __init__(self, poll_interval_ms: int = _POLL_INTERVAL_MS) -> None:
        super().__init__()
        self._poll_interval_ms = poll_interval_ms
        self._timer: QTimer | None = None
        self._last_running: bool | None = None

    @Slot()
    def start(self) -> None:
        """Create the poll timer on this object's thread and poll immediately.

        Invoked via the owning ``QThread``'s ``started`` signal so the timer
        belongs to the worker thread and fires there, never on the UI thread.
        """
        if self._timer is None:
            self._timer = QTimer(self)
            self._timer.setInterval(self._poll_interval_ms)
            self._timer.timeout.connect(self._poll)
        self._timer.start()
        self._poll()

    @Slot()
    def stop(self) -> None:
        """Stop polling (queued from the UI thread before the thread quits)."""
        if self._timer is not None:
            self._timer.stop()

    def _poll(self) -> None:
        running = self._detect()
        if running != self._last_running:
            self._last_running = running
            self.game_state_changed.emit(running)

    @staticmethod
    def _detect() -> bool:
        if psutil is None:
            return _ASSUME_RUNNING_ON_FAILURE
        try:
            for proc in psutil.process_iter([_PROCESS_NAME_ATTR]):
                name = (proc.info.get(_PROCESS_NAME_ATTR) or "").lower()
                if name in _OVERWATCH_PROCESS_NAMES:
                    return True
            return False
        except Exception:  # noqa: BLE001 - detection must never crash the app
            return _ASSUME_RUNNING_ON_FAILURE
