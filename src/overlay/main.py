"""Application entry point.

Builds the overlay window, wires the off-thread refresh worker and its periodic
loop, and installs the visibility trigger. The visible behavior is fixed by
``DESIGN.md`` (the column is shown during hero select and hidden otherwise,
fading via ``CARD_FADE_IN_MS``); the *trigger* is the DESIGN-recommended default
— a manual show/hide global hotkey. The hotkey dependency (``pynput``) is
imported defensively so a missing package degrades to an always-visible overlay
rather than crashing.

Run from the repository root with ``python -m src.overlay.main``.
"""
from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QMetaObject, QObject, Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import QApplication

from .config import AppConfig, load_config
from .data.overfast_client import OverFastClient
from .data.refresh_worker import RefreshWorker
from .data.stats_service import StatsService
from .ui import theme
from .ui.overlay_window import OverlayWindow

try:
    from pynput import keyboard as _pynput_keyboard

    _HOTKEY_AVAILABLE = True
except Exception:  # noqa: BLE001 - optional dependency; any import failure disables it
    _pynput_keyboard = None
    _HOTKEY_AVAILABLE = False

_MS_PER_SECOND = 1000
_ASSETS_SUBDIR = ("assets", "heroes")
_REPO_ROOT_DEPTH = 2
_REFRESH_SLOT = "refresh"
# A single-character hotkey part (e.g. the "o" in "<ctrl>+<alt>+o").
_SINGLE_CHAR_LEN = 1


class _ParsedHotkey:
    """A hotkey spec split into its required modifiers plus a single trigger key.

    The trigger is matched by virtual-key code (``vk``) first, falling back to
    the canonical character. Matching by ``vk`` is what makes activation
    reliable on Windows: while Ctrl+Alt (which Windows treats as AltGr) is held,
    the OS rewrites the character delivered for a letter key, so pynput's
    char-based canonicalisation can fail to match and silently drop the press.
    The ``vk`` is unaffected by modifier state, so the very first press matches.
    """

    def __init__(
        self,
        required_modifiers: frozenset[str],
        trigger_key: object,
        trigger_vk: int | None,
        on_activate: Callable[[], None],
    ) -> None:
        self.required_modifiers = required_modifiers
        self.trigger_key = trigger_key
        self.trigger_vk = trigger_vk
        self.on_activate = on_activate


def _build_modifier_family() -> dict[object, str]:
    """Map every concrete modifier key to its family name (ctrl/alt/shift/cmd).

    Collapsing the left/right/generic (and AltGr) variants of each modifier into
    one family lets the held-modifier set be compared regardless of which
    physical modifier keys the user actually pressed.
    """
    key = _pynput_keyboard.Key
    families: dict[str, tuple[object, ...]] = {
        "ctrl": (key.ctrl, key.ctrl_l, key.ctrl_r),
        "alt": (key.alt, key.alt_l, key.alt_r, key.alt_gr),
        "shift": (key.shift, key.shift_l, key.shift_r),
        "cmd": (key.cmd, key.cmd_l, key.cmd_r),
    }
    return {member: name for name, members in families.items() for member in members}


def _trigger_vk(trigger: object) -> int | None:
    """Return the virtual-key code used to match a parsed trigger key.

    Special keys (function keys, numeric vks) already carry their ``vk``. For a
    single ASCII letter/digit the Windows virtual-key code equals the code point
    of its uppercase form (e.g. ``"o"`` -> ``ord("O")`` == ``VK_O``), which is
    stable even when AltGr rewrites the delivered character. Anything else
    returns ``None`` and is matched on its canonical character instead.
    """
    vk = getattr(trigger, "vk", None)
    if vk is not None:
        return vk
    char = getattr(trigger, "char", None)
    if (
        isinstance(char, str)
        and len(char) == _SINGLE_CHAR_LEN
        and char.isascii()
        and char.isalnum()
    ):
        return ord(char.upper())
    return None


def _matches_trigger(key: object, canonical: object, binding: _ParsedHotkey) -> bool:
    """Whether ``key`` is ``binding``'s trigger, by vk first then canonical char."""
    vk = getattr(key, "vk", None)
    if binding.trigger_vk is not None and vk == binding.trigger_vk:
        return True
    return canonical == binding.trigger_key


class HotkeyManager(QObject):
    """Detects global hotkeys off the UI thread and re-emits them as Qt signals.

    A single ``pynput`` listener runs on its own thread and tracks which
    modifier families are currently held. When a trigger key is pressed with
    exactly the required modifiers down, the matching signal is emitted; Qt then
    delivers it to a UI-thread slot via a queued connection, so widgets are only
    ever touched on the UI thread.

    Matching the trigger by ``vk`` (see :class:`_ParsedHotkey`) is the fix for
    the Windows AltGr issue where ``<ctrl>+<alt>+<letter>`` combos were dropped
    on the first (and sometimes several) presses before the overlay appeared.
    """

    toggle_requested = Signal()
    quit_requested = Signal()

    def __init__(self, toggle_hotkey: str, quit_hotkey: str) -> None:
        super().__init__()
        self._toggle_hotkey = toggle_hotkey
        self._quit_hotkey = quit_hotkey
        self._listener = None
        self._bindings: list[_ParsedHotkey] = []
        self._modifier_family: dict[object, str] = {}
        self._pressed_modifiers: set[str] = set()
        self._pressed_triggers: set[object] = set()

    def start(self) -> bool:
        """Start the global hotkey listener; return ``False`` if unavailable.

        Blocks briefly until the listener thread is actually running so a key
        press immediately after startup is not missed.
        """
        if not _HOTKEY_AVAILABLE or _pynput_keyboard is None:
            return False
        try:
            self._modifier_family = _build_modifier_family()
            self._bindings = self._build_bindings()
            if not self._bindings:
                return False
            self._listener = _pynput_keyboard.Listener(
                on_press=self._on_press, on_release=self._on_release
            )
            self._listener.start()
            self._listener.wait()
        except Exception:  # noqa: BLE001 - a bad hotkey/backend must not crash startup
            self._listener = None
            return False
        return True

    def stop(self) -> None:
        """Stop the listener thread if it is running."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def _build_bindings(self) -> list[_ParsedHotkey]:
        specs = (
            (self._toggle_hotkey, self.toggle_requested.emit),
            (self._quit_hotkey, self.quit_requested.emit),
        )
        bindings: list[_ParsedHotkey] = []
        for spec, callback in specs:
            parsed = self._parse_hotkey(spec, callback)
            if parsed is not None:
                bindings.append(parsed)
        return bindings

    def _parse_hotkey(
        self, spec: str, callback: Callable[[], None]
    ) -> _ParsedHotkey | None:
        """Parse a pynput hotkey string into modifiers + a single trigger key."""
        try:
            parts = _pynput_keyboard.HotKey.parse(spec)
        except ValueError:
            return None
        modifiers: set[str] = set()
        trigger: object | None = None
        for part in parts:
            family = self._modifier_family.get(part)
            if family is not None:
                modifiers.add(family)
            elif trigger is None:
                trigger = part
            else:
                return None
        if trigger is None:
            return None
        return _ParsedHotkey(
            required_modifiers=frozenset(modifiers),
            trigger_key=trigger,
            trigger_vk=_trigger_vk(trigger),
            on_activate=callback,
        )

    def _on_press(self, key: object) -> None:
        try:
            family = self._modifier_family.get(key)
            if family is not None:
                self._pressed_modifiers.add(family)
                return
            identity = self._trigger_identity(key)
            if identity in self._pressed_triggers:
                return
            self._pressed_triggers.add(identity)
            canonical = self._canonical(key)
            for binding in self._bindings:
                if self._pressed_modifiers == binding.required_modifiers and (
                    _matches_trigger(key, canonical, binding)
                ):
                    binding.on_activate()
        except Exception:  # noqa: BLE001 - a stray key event must never kill the listener
            pass

    def _on_release(self, key: object) -> None:
        try:
            family = self._modifier_family.get(key)
            if family is not None:
                self._pressed_modifiers.discard(family)
                return
            self._pressed_triggers.discard(self._trigger_identity(key))
        except Exception:  # noqa: BLE001 - a stray key event must never kill the listener
            pass

    def _canonical(self, key: object) -> object:
        if self._listener is None:
            return key
        return self._listener.canonical(key)

    def _trigger_identity(self, key: object) -> object:
        """A stable per-key identity (vk if present) for press/repeat tracking."""
        vk = getattr(key, "vk", None)
        return vk if vk is not None else str(self._canonical(key))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[_REPO_ROOT_DEPTH]


def _build_worker_thread(
    service: StatsService, battletags: list[str], window: OverlayWindow
) -> tuple[QThread, RefreshWorker]:
    thread = QThread()
    worker = RefreshWorker(service, battletags)
    worker.moveToThread(thread)
    worker.player_updated.connect(window.update_player)
    thread.start()
    return thread, worker


def _start_visibility_trigger(
    config: AppConfig, window: OverlayWindow, app: QApplication
) -> HotkeyManager:
    hotkeys = HotkeyManager(config.toggle_hotkey, config.quit_hotkey)
    hotkeys.toggle_requested.connect(window.toggle, Qt.ConnectionType.QueuedConnection)
    hotkeys.quit_requested.connect(app.quit, Qt.ConnectionType.QueuedConnection)
    if hotkeys.start():
        print(
            f"Overlay running. Toggle with {config.toggle_hotkey}, "
            f"quit with {config.quit_hotkey}."
        )
    else:
        # No global-hotkey backend: keep the overlay visible so the app is
        # still usable, and tell the user how to enable the toggle.
        print(
            "pynput not available - showing the overlay continuously. Install "
            "pynput to enable the global show/hide hotkey."
        )
        window.show_overlay()
    return hotkeys


def main() -> int:
    """Compose the overlay, start the refresh loop, and run the Qt event loop."""
    repo_root = _repo_root()
    config = load_config(repo_root)
    theme.apply_font_override(config.font_family)
    # NOTE: DEFERRED (ISSUES.md "C-SA CB No in-app configuration screen"): tracked
    # BattleTags can currently only be edited by hand in config.json. An in-app
    # settings/config window is a new UI surface not covered by DESIGN.md and is
    # blocked on the design decision in ISSUES.md "Questions for the user" #2
    # (look/layout + whether it opens on first run, behind a hotkey, or both).
    # Do not invent that UI here.

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    if not config.battletags:
        print(
            "No battletags configured. Add some to config.json "
            "(see config.example.json)."
        )
    # NOTE: DEFERRED (ISSUES.md "C-SA CB No standalone stats view when Overwatch is
    # closed"): there is no "game-closed" mode that shows the user's own profile
    # (overall stats + top-N heroes). That needs game-running detection, an own
    # BattleTag config field, a top-N-hero data extension (see the matching NOTEs
    # in data/stats_service.py and data/models.py), and a dedicated stats window.
    # It is a sizable new feature/UI beyond DESIGN.md, blocked on ISSUES.md
    # "Questions for the user" #3. Do not build it or invent its UX here.

    assets_dir = repo_root.joinpath(*_ASSETS_SUBDIR)
    client = OverFastClient()
    service = StatsService(client, assets_dir, basis=config.winrate_basis)
    window = OverlayWindow(config.battletags, anchor=config.anchor)

    thread, worker = _build_worker_thread(service, config.battletags, window)

    refresh_timer = QTimer()
    refresh_timer.setInterval(config.refresh_interval_seconds * _MS_PER_SECOND)
    refresh_timer.timeout.connect(worker.refresh)
    refresh_timer.start()
    # Kick off the first fetch immediately on the worker thread.
    QMetaObject.invokeMethod(worker, _REFRESH_SLOT, Qt.ConnectionType.QueuedConnection)

    hotkeys = _start_visibility_trigger(config, window, app)

    def _cleanup() -> None:
        refresh_timer.stop()
        hotkeys.stop()
        thread.quit()
        thread.wait()
        client.close()

    app.aboutToQuit.connect(_cleanup)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
