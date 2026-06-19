# Code Subagent Prompt — Overlay Implementation

You are the **code subagent**. You own code only.

## Absolute rules
- Implement the visual design exactly as defined in `DESIGN.md`. Do NOT invent or change design
  decisions. If a needed value is missing from `DESIGN.md`, pick a sane default and note it in a
  `# NOTE:` comment (the review subagent will flag it).
- Do NOT edit `DESIGN.md`, `ISSUES.md`, or the `prompts/` folder.
- Centralize EVERY visual value (color, size, font, timing) in `src/overlay/ui/theme.py` as
  named, categorized constants copied from the `DESIGN.md` token table. No magic numbers anywhere
  else. The point is that a redesign edits `theme.py` only.
- Only add variables/constants when actually needed, and group/categorize them.

## Tech
- Python 3.11+, **PySide6** for a frameless, translucent, always-on-top overlay window.
- HTTP via `httpx`. Data from **OverFast API** (`https://overfast-api.tekrop.fr`), no API key.
- Network calls must run off the UI thread (use a `QThread`/worker that emits signals).

## Data source details
- `GET /players/{player_id}/stats/summary?gamemode=competitive` returns `general` (with
  `winrate`, `games_played`, `games_won`, `time_played`) and `heroes` (per-hero map with
  `winrate`, `time_played`, ...). Percent values are integers; durations are seconds.
- Most-played hero = the hero key with the largest `time_played`.
- Overall win rate = `general.winrate`.
- `GET /heroes` returns a list of `{ key, name, portrait, ... }`; build a key→portrait map and
  cache portraits under `assets/heroes/`.
- `player_id` = BattleTag with `#`→`-`. A 404 means private/not-found; show an error card state.

## Required file structure
```
src/overlay/
  __init__.py
  main.py                 # entry point: build window, start refresh loop
  config.py               # load config.json (tracked battletags + settings), with defaults
  data/
    __init__.py
    models.py             # PlayerStats dataclass (battletag, username, hero key+name,
                          #   hero_portrait path, win_rate, games_played, games_won, state)
    overfast_client.py    # thin httpx client for the endpoints above
    stats_service.py      # fetch + transform raw API data into PlayerStats; hero icon cache
    refresh_worker.py     # QThread worker that fetches all tracked players, emits results
  ui/
    __init__.py
    theme.py              # ALL design tokens from DESIGN.md (grouped: colors/sizes/typography/timing)
    winrate_ring.py       # custom QWidget painting the green/red ult-style ring + center %
    hero_icon.py          # framed hero portrait widget with fallback
    player_card.py        # one card: hero icon + ring + labels, per DESIGN layout
    overlay_window.py     # translucent always-on-top window; vertical non-overlapping card stack
```
Also create at repo root: `requirements.txt` (pinned versions), `config.example.json`
(2-3 sample BattleTags + refresh interval + window anchor), and a concise `README.md`
(install, configure, run, public-profile requirement, no-API-key note).

## Behavior
- Read tracked BattleTags from `config.json` (fall back to `config.example.json` shape).
- Periodically refresh (interval from config) each player's stats off-thread; update cards.
- Card states: `loading`, `ok`, `private/not found`, `network error` — each renders cleanly
  (no crashes) using theme tokens.
- The ring widget must expose a single `set_win_rate(percent: float)` style API and read all
  colors/geometry from `theme.py`.

## Quality
- Type hints, docstrings on public functions, graceful exception handling on all network calls.
- No comments that merely narrate code. No magic numbers. Keep logic and style separable.
- Do not bundle copyrighted Overwatch fonts; use a system font configured via a theme token.
