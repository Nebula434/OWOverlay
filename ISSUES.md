# ISSUES.md — Design-Vision Compliance Review

Review of `src/overlay/**` against `DESIGN.md` (visual spec / Design Tokens table) and the
confirmed choices in `DECISIONS.md`. Severities: BLOCKER, MAJOR, MINOR, NIT.

> **This run is a pure code-vs-spec review — there is NO video / screen-recording evidence.**
> Every prior finding (the previous review also leaned on 5 extracted recording frames) has been
> **re-verified against the current code**. Findings that previously depended on the video frames
> are re-stated here as code-structure observations only and are *not* asserted from stills.

> **Headline:** the codebase still matches the authoritative `DESIGN.md` vision. **No BLOCKER or
> MAJOR design-compliance issues.** Token centralization holds — `ui/theme.py` carries every visual
> value from the Design Tokens table verbatim and **no** hard-coded hex / `QColor` / `QFont` /
> `setPointSize` literal appears in any other module; a re-theme would touch only `theme.py`. The
> prior **MINOR** idle-animation gap (hero-icon glow never breathing) is **now RESOLVED in code** —
> `hero_icon.py` has a looping glow animation mirroring the ring. The only remaining design-compliance
> finding is one **NIT** (no-data label copy is not specified by `DESIGN.md`). Both prior RESOLVED
> NITs (token-table completeness; config→httpx import) remain resolved. The two `C-SA CB`
> feature-gap reports (no in-app config screen; no game-closed stats view) **still stand** and are
> confirmed structurally in code; the `C-SA CB` toggle-reliability item has its code-side fix in
> place but its runtime behavior **cannot be re-confirmed in a code-only pass**.

---

## Code-only review note (this run)

- **No recording this run.** All findings are derived strictly from the code vs `DESIGN.md` /
  `DECISIONS.md`.
- The prior run's frames corroborated runtime-visible aspects (top-left anchor + downward column,
  vertical non-overlapping stacking, the icon | ring | label row, the `?` icon fallback, the
  dash-only no-data ring, window transparency, and the show/hide lifecycle). Those remain **fully
  consistent with the current code** but are not independently re-confirmable here.
- Aspects that are inherently runtime-only — the all-"Private / not found" state seen in the prior
  frames, and the live behavior of the show/hide hotkey — are **not asserted** from this pass. Where
  possible they are re-stated as static code-structure observations instead (e.g. "there is no
  `config.json`, only `config.example.json`, whose placeholder tags are unlikely to resolve").
- Aspects that could never be read from 5 stills anyway (the green/red tick split + exact hexes, the
  6° seam, the center `%` typography, the fill/count-up animation, the glow breathing, the per-card
  stagger) are now **verified directly in the drawing code** and are listed under "Verified
  compliant" below.

---

## Verified compliant (re-checked against the current code)

- **Token centralization** — `ui/theme.py` matches the `DESIGN.md` Design Tokens table value-for-
  value across all groups (colors + `*_ALPHA`, sizes, angles, typography, timing). A repo scan found
  **every** `#RRGGBB` literal only inside `theme.py`, and **no** `QColor(...)` / `QFont(...)` /
  `setPointSize(...)` / `setLetterSpacing(...)` literal in any other module (only the `theme.qcolor`
  / `theme.build_font` helpers). Widgets reference tokens by name only. The font fallback chain
  (`Big Noodle Titling → Bebas Neue → Oswald → Arial Narrow → sans-serif`) matches `DESIGN.md`.
  Framework baselines that `DESIGN.md` does not theme (`ALPHA_OPAQUE`,
  `LETTER_SPACING_NORMAL_PCT`, `SWEEP_DIRECTION_*`) and the per-module geometry/math constants
  (`_HALF_DIVISOR`, `_QT_ANGLE_UNITS_PER_DEGREE`, etc.) are **named, not magic numbers**.
- **Ring** (`ui/winrate_ring.py`) — full donut; soft cyan glow → recessed track
  (`COLOR_RING_TRACK`, inset `RING_TRACK_INSET_PX`) → `RING_TICK_COUNT = 50` radial ticks (each = 2%,
  `green_count = round(fraction × 50)`) → beveled double rim (`COLOR_RING_BEVEL_OUTER/INNER`) → cyan
  accent hairline. Green-win / red-loss split (`is_win = index < green_count`); a dark seam (the
  track showing through) widened to `RING_ARC_GAP_DEG = 6` at **both** the win→loss and the loss→win
  (start) boundaries via `leading_seam` / `trailing_seam`; per-arc same-color glow
  (`COLOR_ARC_GLOW_ALPHA`). Starts at 12 o'clock (`RING_START_ANGLE_DEG = 90`) sweeping **clockwise**
  (negative sign in Qt's CCW-positive convention). Center: number at `FONT_RING_CENTER_SIZE_PT` +
  smaller `%` at `FONT_RING_SUFFIX_SIZE_PT`, bold/italic, letter-spaced, with a
  `CENTER_TEXT_SHADOW_OFFSET_PX` drop shadow. 0% → all red, 100% → all green, no-data → no ticks +
  dash. Fill + count-up animations run together; glow loops on `GLOW_PULSE_PERIOD_MS`.
- **Card** (`ui/player_card.py`) — wide horizontal `QHBoxLayout` row (icon → ring → label), each
  `AlignVCenter`; icon and ring adjacent and layout-separated by `CARD_ELEMENT_GAP_PX` (never
  overlap). Rounded navy panel (`COLOR_CARD_BG` @ `_ALPHA`, `CARD_CORNER_RADIUS_PX`) with border and
  the cyan left accent bar (`CARD_ACCENT_WIDTH_PX`, clipped to the panel). Two stacked elided labels
  (name `COLOR_LABEL_PRIMARY`, sub `COLOR_LABEL_SECONDARY`). Content height (102 − 2×12 = 78) equals
  both `ICON_BADGE_HEIGHT_PX` and `RING_DIAMETER_PX`. All four card states handled.
- **Stacking** (`ui/overlay_window.py`) — single `QVBoxLayout` with `CARD_SPACING_PX` spacing;
  window height = `count × CARD_HEIGHT + (count − 1) × CARD_SPACING`, so cards cannot overlap; the
  column grows downward.
- **Hero icon** (`ui/hero_icon.py`) — true shield silhouette (`_build_shield_path` from
  `ICON_TOP_CORNER_RADIUS_PX` + `ICON_BOTTOM_POINT_DEPTH_PX`); cyan frame + darker inner bevel +
  soft outer glow; portrait clipped to the shield path; fallback fill (`COLOR_ICON_BG_FALLBACK`) +
  initial/`?` (`COLOR_ICON_FALLBACK_TEXT`) keeps frame + glow so the layout never shifts. **Now also
  breathes** (see RESOLVED below).
- **Window / entry point** — frameless, translucent (`WA_TranslucentBackground`), always-on-top,
  click-through (`WindowTransparentForInput`), off-taskbar (`Tool`), non-focusing; base painted with
  `COLOR_OVERLAY_BG` @ alpha `0` via `CompositionMode_Source` (only cards paint pixels). `main.py`
  wires the off-thread refresh worker, the refresh timer, and the global show/hide + quit hotkeys,
  degrading to an always-visible overlay if `pynput` is missing.
- **Decisions (`DECISIONS.md`)** — win-rate basis is configurable and defaults to **combined**
  (`data/stats_service.py` merges competitive + quickplay and recomputes the rate from summed
  games); font is user-overridable via `config.font_family` → `theme.apply_font_override`; anchor
  defaults to **top-left** (all four corners exposed); the **shield** icon and the **6° arc seam**
  are implemented.

---

## [RESOLVED — was MINOR] Hero-icon glow now breathes (idle pulse implemented)
- Area: design
- Location: `src/overlay/ui/hero_icon.py:73-80` (looping `_glow_anim`), `:82-84` (`_on_glow_value`),
  `:122-134` (`_paint_glow` applies the pulse) vs. `src/overlay/ui/winrate_ring.py:75-82` (the ring's
  matching `_glow_anim`).
- Status: the prior review flagged `HeroIcon._paint_glow` as fully static, leaving half of
  `DESIGN.md` → Motion (*"the cyan **ring/icon** glow breathes on a slow loop with period
  `GLOW_PULSE_PERIOD_MS`"*) unimplemented. **Re-verified: now fixed.** `HeroIcon` runs a looping
  `QVariantAnimation` over `GLOW_PULSE_PERIOD_MS` (start 0 → peak `1.0` at the half-period → 0,
  `loopCount = -1`), driving `_glow_phase`, and `_paint_glow` modulates the glow alpha by that pulse
  exactly as `winrate_ring` does. The badge and ring now breathe together. No action needed.

## [NIT] No-data secondary-label copy is not covered by `DESIGN.md`
- Area: design
- Location: `src/overlay/ui/player_card.py:24-27` (`_TEXT_LOADING` / `_TEXT_PRIVATE` / `_TEXT_NETWORK`
  / `_TEXT_NO_DATA`), set on the secondary label in `_apply_loading`/`_apply_ok`/`_apply_private`/
  `_apply_network_error` (`:129`, `:135`, `:141`, `:147`).
- Problem: `DESIGN.md` → Card spec defines label Line 2 only as *"most-played hero"* and never
  specifies copy for the loading / private / error states. The code authors four status strings
  ("Loading…", "Private / not found", "Network error", "No data") that sit outside the token/spec.
  The interpretation (reuse the hero line for a short status when there is no hero) is reasonable and
  the ring's no-data treatment is fully compliant, so this is a **spec-coverage gap, not a rendering
  violation** — hence NIT. (Whether these strings are good UX is tracked under `C-SA CB` #3.)
- Suggested fix (design owner): either bless these status strings in `DESIGN.md` (so the no-data
  label copy becomes part of the spec) or define the intended empty-state text/treatment. See
  Questions for the user #1.

## [RESOLVED — was NIT] Three effect values are first-class `DESIGN.md` tokens
- Area: design
- Location: `src/overlay/ui/theme.py:85` (`ICON_FRAME_INNER_WIDTH_PX = 1`), `:104`
  (`CENTER_TEXT_SHADOW_OFFSET_PX = 1`), `:131` (`FONT_ICON_FALLBACK_WEIGHT = 700`).
- Status: re-verified — all three remain present in `theme.py` **and** in the `DESIGN.md` Design
  Tokens table, with no stray `# NOTE` markers in `theme.py`. "Copy the table verbatim" holds. No
  action needed.

## [RESOLVED — was NIT] Config no longer pulls in the HTTP stack for its constants
- Area: code-structure
- Location: `src/overlay/config.py:16` (`from .data.models import DEFAULT_BASIS, VALID_BASES`);
  `src/overlay/data/models.py:12-15` (the `BASIS_*` / `VALID_BASES` / `DEFAULT_BASIS` definitions).
- Status: re-verified — the basis constants live in the neutral `data/models.py` (no Qt / `httpx`
  imports; only `dataclass` + `enum`), and both `config.py` and `stats_service.py` import them from
  there. Loading config no longer transitively drags in `overfast_client` → `httpx`. No action
  needed.

---

## Reported runtime bugs — `C-SA CB` (code subagent to debug & fix)

> Behavioral / feature findings against the shipped code (not `DESIGN.md` compliance gaps). Each
> title keeps the **`C-SA CB`** prefix so the code subagent picks it up; the code subagent fixes the
> referenced code and does **not** edit this file. Re-verified this run against the current code
> (code-only — no recording).

## [MINOR] C-SA CB Toggle reliability — code-side fix is present; runtime unverifiable code-only
- Area: code-structure
- Location: `main.py:117-249` (`HotkeyManager`), `:86-114` (`_trigger_vk` / `_matches_trigger`),
  `:144-165` (`start`, which calls `self._listener.wait()` so a press right after startup is not
  missed); `overlay_window.py:89-118` (`toggle` / `show_overlay` / `hide_overlay`).
- Re-verification (code-only): the prior MAJOR→MINOR downgrade relied on the recording showing the
  toggle working, which **cannot be re-confirmed in a code-only pass**. Reading the current code,
  the originally reported "needs multiple presses / first press dropped" symptom has a **targeted
  fix in place**: the listener matches the trigger by **virtual-key code** first (stable even while
  Ctrl+Alt / AltGr rewrites the delivered character on Windows) and only falls back to the canonical
  char, and `start()` blocks on `listener.wait()`. The `toggle` / `show_overlay` / `_visible` logic
  reads correctly with no obvious dropped-press path. The "cards pop in one-by-one" sub-claim is
  **intended** (`CARD_STAGGER_MS = 80`, the spec's top-down stagger), not a defect. Severity stays
  MINOR.
- Suggested fix (only if it recurs at runtime): add input-level logging in `HotkeyManager` (raw
  listener key events vs. delivered `toggle_requested`) to catch any dropped/odd-modifier events;
  otherwise treat the current code as the fix.

## [MAJOR] C-SA CB No in-app configuration screen to edit tracked BattleTags
- Area: code-structure
- Location: `config.py` (JSON-only load; no UI), `main.py:294-299` (the `# NOTE: DEFERRED …` marker),
  `config.py:63-68` (matching marker); **no `ui/config_window.py` exists** (confirmed by file scan).
- Re-verification (code-only): **still valid.** Tracked BattleTags can only be changed by
  hand-editing `config.json`; there is no in-app way to add/remove/edit teammates. Structurally
  confirmed without the video: there is **no `config.json`** in the repo — only
  `config.example.json`, whose placeholder tags (`Krusher#9999`, `Awkward#2616`,
  `TimTheTatman#1432`) are loaded by `config.py`'s fallback and are highly unlikely to resolve, so a
  fresh checkout runs entirely on non-resolving example data. (The prior all-"Private / not found"
  frames are consistent with this but are not re-asserted from stills.)
- Suggested fix: add a settings/config window (e.g. `ui/config_window.py`) shown on first run and/or
  on demand that edits the tracked tags (and other `config.json` fields) and writes them back through
  `config.py`. NOTE: this is a new UI surface **not covered by `DESIGN.md`**; its look needs a design
  pass first (see Questions for the user #2) — the code subagent must not invent the visual design.

## [MAJOR] C-SA CB No standalone stats view when Overwatch is closed (own stats + top heroes)
- Area: data | code-structure
- Location: `main.py:309-315` (the `# NOTE: DEFERRED …` marker; no game-running detection / mode
  switch), `data/stats_service.py:248-265` (`_most_played_hero_key` resolves only the single
  most-played hero), `data/models.py:35-40` (`PlayerStats` carries no top-N heroes and no notion of
  the user's own profile).
- Re-verification (code-only): **still valid.** The data layer resolves only one most-played hero +
  an overall win rate per teammate; there is no game-closed mode presenting the user's own profile
  (overall stats + top-3 most-played heroes), no own-BattleTag config field, and no game-running
  detection. (Prior frames captured with Overwatch closed corroborated this, but the runtime state
  is not re-asserted here.) The three `# NOTE: DEFERRED` markers remain in place, all pointing at
  Questions for the user #3.
- Suggested fix: add a "game-closed" mode — detect whether Overwatch is running, identify the user's
  own BattleTag (a new `config.json` field), extend the data layer to return top-N heroes, and
  present a dedicated stats window. NOTE: a sizable new feature/UI **beyond the current
  `DESIGN.md`**; it needs a design spec before implementation (see Questions for the user #3).

---

## Real-data screenshot review — 2026-06-19 (overlay running over the live game)

> **This run IS screenshot-evidenced** (contrast the code-only note near the top). Source:
> `screenshot_overlay_realdata.png` — the overlay over Overwatch hero-select with three *resolved*
> teammate cards: **Nebula434 / Zarya / 50%**, **jjstansloona / Mei / 49%**, **mjmeows / Mercy /
> 50%**. All findings below are **screenshot-traced** (zoomed crops + pixel sampling of the three
> top-left overlay cards only; the game UI behind them was ignored).
>
> **Outcome: the overlay renders to `DESIGN.md`. Both candidate discrepancies raised for this pass
> were investigated and REJECTED. No new `C-SA CB` code bugs were found.** The runtime aspects that
> earlier (code-only / 5-frame) passes could not confirm are now verified directly.

### Now confirmed CORRECT at runtime (aspects earlier passes could not verify)
- **Hero shield + portrait clip** — the with-portrait path renders the true shield silhouette
  (rounded top corners tapering to a centered bottom point) with the portrait clipped to it — **not**
  a rounded rectangle. Bottom-point crops show the cyan frame angling inward to the point and the
  portrait following the same path.
- **Win/loss arc + sweep direction** — green win arc sweeps **clockwise from 12 o'clock**; the red
  loss arc completes the circle back to the top. The 50 / 49 / 50 values read as ~half green
  (right side) / ~half red (left side).
- **Arc seam** — dark seams are visible at the top (loss→win boundary) and at the win→loss boundary
  (~6 o'clock at 50%).
- **Segmented ticks** — the band is discrete radial ticks, not a smooth solid arc (the committed
  look, not the emergency fallback).
- **Center % typography** — large bold-italic number with a smaller trailing `%`, off-white.
- **Cyan rim + glow, left accent bar, two-line labels (bold white name + dimmer hero), vertical
  non-overlapping stacking, top-left anchor** — all present and matching the tokens.
- **Card panel is genuinely painted** — pixel sampling behind the bright "ANIMA STRIKE" art shows
  the lower-card panel darkens a pure-white (255) background stroke to ≈(72, 79, 97), i.e. an
  effective alpha ≈185–195 ≈ the spec `COLOR_CARD_BG_ALPHA = 200`.

### [REJECTED — screenshot] Candidate: hero icon is a rounded rectangle, not a shield
- Area: design
- Location: `src/overlay/ui/hero_icon.py:34-57` (`_build_shield_path`), `:102-120` (`paintEvent`
  builds `outer_path`), `:136-153` (`_paint_portrait`; `painter.setClipPath(path)` at `:141`),
  `:155-165` (`_paint_fallback` fills the same `path`).
- Problem (hypothesis tested): "the with-portrait paint path falls back to a rounded rect instead of
  reusing the shield clip path the `?` fallback uses."
- Finding: **NOT A BUG.** `paintEvent` builds one `outer_path = _build_shield_path(...)` and passes
  that *same* path to both `_paint_portrait` (which clips the portrait to it) and `_paint_fallback`.
  There is no rounded-rect code path. Zoomed 12× crops of the shield bottoms confirm a real shield
  point (depth ≈9–10 px on the ~62 px badge) with the portrait clipped to it.
- Suggested fix / trace pointer: none — the rounded-rect impression in the un-zoomed shot is just
  the rounded TOP corners (`ICON_TOP_CORNER_RADIUS_PX = 8`) plus a modest
  `ICON_BOTTOM_POINT_DEPTH_PX = 12`; at 1:1 it is clearly a shield. Do not "fix" this.

### [REJECTED — screenshot] Candidate: lower-card panels are under-painted / panel-less
- Area: design | code-structure
- Location: `src/overlay/ui/player_card.py:149-168` (`paintEvent`; panel fill at `:161` =
  `theme.qcolor(COLOR_CARD_BG, COLOR_CARD_BG_ALPHA)`), token `src/overlay/ui/theme.py:41`
  (`COLOR_CARD_BG_ALPHA = 200`); per-card opacity in `src/overlay/ui/overlay_window.py:68-70`
  (effect init to `0.0`) and `:96-122` (`show_overlay` stagger → `_fade_in_card` → `_fade_card`).
- Problem (hypothesis tested): "a per-card opacity/stagger animation leaves the lower panels
  under-painted, so text/ring float over the game with no panel."
- Finding: **NOT A CODE BUG.** Measured effective panel alpha on cards 2 & 3 ≈185–195 ≈ spec 200;
  the panels clearly darken the bright art behind them (white → dark slate). The faintness is the
  semi-transparent (alpha-200) panel sitting over the *bright* event background, whereas card 1 sits
  over a *dark* area — so the identical panel reads "solid navy" on top and "translucent slate"
  below. The `QGraphicsOpacityEffect` fades the panel **and** its child content together, but the
  content (rings, %, portraits, names) is at full brightness on all three cards, which rules out a
  mid-stagger capture — i.e. the opacity effect is not the cause.
- Suggested fix / trace pointer: none in code — the alpha is a `DESIGN.md` token choice
  (`COLOR_CARD_BG_ALPHA = 200`), not a code deviation. Whether to raise it for more consistent
  solidity over bright game backgrounds is a design-owner decision (see Questions for the user #4).

---

## Questions for the user

1. **No-data label copy (the NIT).** `DESIGN.md` specifies label Line 2 only as the "most-played
   hero" and never defines copy for the empty/error states, yet the code shows author-written
   strings ("Loading…", "Private / not found", "Network error", "No data"). Should these be
   blessed/standardized in `DESIGN.md` (making the no-data label part of the spec), or do you want
   different empty-state copy/treatment? Non-blocking — the ring's neutral no-data rendering is
   already compliant.
2. **Config-screen design (from the `C-SA CB` MAJOR).** The BattleTag-editing settings window is a
   UI surface not in `DESIGN.md`. Should it get a `DESIGN.md` / design-subagent spec (look, layout,
   tokens) before the code subagent builds it, and should it open on first run, behind a hotkey, or
   both?
3. **"Game-closed" stats app (from the `C-SA CB` MAJOR).** Confirm the scope and design for the
   standalone view shown when Overwatch is closed: which of the user's own stats to display alongside
   the top-3 heroes, how to detect that the game is closed, and where the user's own BattleTag is
   configured.
4. **Card-panel opacity over bright game backgrounds (design tuning — NOT a code bug).** The
   real-data screenshot shows `COLOR_CARD_BG_ALPHA = 200` faithfully implemented, but over the
   game's bright event art the lower cards' panels read as translucent slate and look inconsistent
   with cards sitting over dark areas (the "faint panel" first noticed in the un-zoomed shot). Do
   you want the panel alpha raised (more solid / more consistent over any background) or kept at 200
   (lighter, more "HUD-like")? This is purely a `DESIGN.md` token decision; the code already matches
   the token.

All other earlier questions are resolved in `DECISIONS.md` (track current `DESIGN.md`: yes; shield
icon: yes; anchor default top-left: yes; 6° arc seam: yes; win-rate basis: configurable, default
combined; font: Koverwatch + fallback chain, user-overridable). The visibility-trigger mechanism
(global hotkey) was adopted under the `DESIGN.md` delegation and needs no sign-off. The prior MINOR
(hero-icon glow) and both prior NITs (token-table completeness; config→httpx import) are now
**resolved in code** and need no decision.
