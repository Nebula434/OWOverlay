# Overwatch Teammate Win-Rate Overlay

A quiet, top-most HUD that appears at the edge of your screen and shows, per
tracked teammate, **who they play** and **how often they win** — rendered in the
visual language of the Overwatch ultimate-charge ring. Each teammate is one wide
card: a framed shield hero portrait, a circular win/loss "ult ring," and a
name / most-played-hero label.

The overlay is frameless, translucent, always-on-top, and **click-through**
(input passes through to the game), with no taskbar entry.

> **Project direction.** This overlay is the first surface of a larger effort that is expanding into
> a **full standalone Overwatch companion application**. Its look is being specified in
> `APP_DESIGN.md` (the forthcoming app spec, alongside the existing overlay spec in `DESIGN.md`)
> from the `concepts/CONCEPT_STANDALONE_APPLICATION.png` concept, and it aims to use **real/existing
> Overwatch assets** (rank, role, and stat icons, hero portraits) rather than placeholder shapes.
> The overlay install / configure / run steps below remain current.

## Requirements

- **Python 3.11+**
- Windows (built/tested for Windows; the global hotkey uses `pynput`)
- Each tracked player's **career profile must be public** (Overwatch → Settings →
  Social → *Career Profile Visibility: Everyone*). A private or unknown profile
  shows a "Private / not found" card.

Stats come from the public [OverFast API](https://overfast-api.tekrop.fr).
**No API key or login is required.**

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configure

Copy the example config and edit it:

```powershell
Copy-Item config.example.json config.json
```

`config.json` fields:

| Field | Meaning | Default |
|---|---|---|
| `battletags` | Teammates to track, as `Name#1234` | — |
| `refresh_interval_seconds` | How often to refresh stats (min 15) | `60` |
| `anchor` | Screen corner: `top-left`, `top-right`, `bottom-left`, `bottom-right` | `top-left` |
| `winrate_basis` | `competitive` or `combined` (competitive + quickplay) | `combined` |
| `font_family` | Optional font override; `null` uses the built-in HUD chain | `null` |
| `toggle_hotkey` | Global show/hide hotkey ([pynput format](https://pynput.readthedocs.io/en/latest/keyboard.html#monitoring-the-keyboard)) | `<ctrl>+<alt>+o` |
| `quit_hotkey` | Global quit hotkey | `<ctrl>+<alt>+q` |

If `config.json` is missing, the app falls back to `config.example.json`.

## Run

```powershell
python -m src.overlay.main
```

The overlay starts **hidden**. Press the **toggle hotkey** (default
`Ctrl+Alt+O`) during hero select to fade the column in; press it again to fade
it out. Press the **quit hotkey** (default `Ctrl+Alt+Q`) to exit.

> The visible behavior matches the design: shown during hero select, hidden
> otherwise. Because Overwatch exposes no hero-select API, showing/hiding is a
> manual global hotkey. If `pynput` is not installed, the overlay stays
> continuously visible instead.

## How it works

- Hero portraits and the hero key→portrait map are fetched once and cached under
  `assets/heroes/`; the HTTP client is reused across requests.
- Network calls run on a background thread, so the UI never blocks.
- Most-played hero = the hero with the most time played; win rate is either the
  competitive win rate or the combined competitive + quickplay rate, per
  `winrate_basis`.
- The entire look is defined by `DESIGN.md` (overlay) — with `APP_DESIGN.md` to follow for the
  standalone application — and centralized in `src/overlay/ui/theme.py`. Re-theming only ever edits
  that one file.

## Project layout

```
src/overlay/
  main.py             # entry point: window + refresh loop + hotkey
  config.py           # config.json loading and defaults
  data/               # OverFast client, stats transforms, refresh worker
  ui/
    theme.py          # ALL design tokens (the single source of truth)
    winrate_ring.py   # the segmented win/loss ult ring
    hero_icon.py      # the shield hero portrait
    player_card.py    # one teammate card
    overlay_window.py # the transparent click-through window
```
