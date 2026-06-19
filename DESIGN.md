# DESIGN.md — Overwatch Teammate Win-Rate Overlay (Visual Spec)

> Single source of truth for the **look** of the overlay. The code subagent must copy the
> values in the **Design Tokens** table verbatim into a `theme` module and reference them by
> name. No raw numbers/colors may appear in logic — only token references.

> **Scope & relationship to `APP_DESIGN.md` (cross-reference, not new design).** This file
> (`DESIGN.md`) is the authoritative spec for the **in-game overlay**, plus the interim
> **Game-Closed Stats View** and **In-App Configuration Screen** documented below. The project is
> expanding toward a **full standalone application**, whose authoritative spec is **`APP_DESIGN.md`**
> (per `concepts/CONCEPT_STANDALONE_APPLICATION.png`). `APP_DESIGN.md` is authored by the
> design-subagent and **may not exist yet** (forward reference); when present, it governs the
> standalone application while this file continues to govern the overlay. The two share one visual
> language (win-rate ring, shield hero icon, navy panels, cyan accents, typography); where they
> overlap, `APP_DESIGN.md` is authoritative for the standalone app and `DESIGN.md` for the overlay.
> No tokens or vision are (re)defined in this note — see each spec's own token table.

---

## Vision

A quiet, top-most HUD that appears at the edge of the screen during **hero select** and shows,
per tracked teammate, *who they play* and *how often they win*, in the visual language of the
Overwatch ultimate-charge ring. Each teammate is one self-contained **wide horizontal card**: a
framed shield-style hero portrait, the circular win-rate "ult ring," and a name / most-played
-hero label, all in a single vertically-centered row. The ult ring is re-themed into a **full
donut** whose circumference is split into a **warm yellow-green win arc** and a **harsh red loss
arc** (green% + red% = 100%), with the win-rate number sitting bold and italic in the center. We
keep the source HUD's character — a dark recessed track, a beveled double rim, a cyan accent, a
soft glow, and the segmented-tick treatment — but render the colored band as a **thin ring near
the outer edge**, matching the thin grouped charge-ticks of the real ult HUD. The aesthetic is
dark, cool-toned, and crisp: navy panels, cyan edges, confident color-coded arcs.

---

## Layout

- **Window**: a single transparent, frameless, always-on-top, click-through overlay window with
  no taskbar presence. The window background is fully transparent (`COLOR_OVERLAY_BG` at
  `COLOR_OVERLAY_BG_ALPHA = 0`); only the cards paint pixels.
- **Anchor**: pinned to the **top-left** screen corner by default, offset inward by
  `OVERLAY_MARGIN_X_PX` (from the left edge) and `OVERLAY_MARGIN_Y_PX` (from the top, clearing
  the game's top nav bar). Top-left matches the rough placement mock and avoids the in-game
  party panel that sits top-right. (Corner is a single configurable choice — see Open Questions.)
- **Visibility lifecycle**: the overlay is **not** shown for the whole match. Its intended
  visible behavior has two states:
  - **Shown** — during **hero select**, the full column is visible. On entering this state the
    overlay fades **in** over `CARD_FADE_IN_MS` (cards may still stagger in via `CARD_STAGGER_MS`).
  - **Hidden** — once hero select ends, the overlay fades **out** over `CARD_FADE_IN_MS` (the
    same timing token reused for symmetry) and paints nothing.
  - Overwatch exposes no reliable API for hero-select start/end, so this spec **fixes only the
    *visible behavior*** (shown during hero select, hidden after, fading via `CARD_FADE_IN_MS`) and
    **deliberately delegates the *trigger mechanism* to the code subagent's implementation
    judgment** — it is not a design decision. **Recommended v1 default:** a manual show/hide
    **global hotkey** (simplest, fully reliable, no detection guesswork). Acceptable alternatives
    if the code subagent prefers: a **timed window** or **screen detection**. The code subagent may
    proceed with the recommended hotkey default without further input. See Open Question #1.
- **Card stacking**: cards form a **single vertical column**, top to bottom, in the configured
  teammate order. Cards **never overlap** — a fixed `CARD_SPACING_PX` gap separates each card
  from the next (this is the explicit fix for the overlapping rough mock). The column grows
  downward to fit 1…N cards.
- **Uniform sizing**: every card is exactly `CARD_WIDTH_PX` × `CARD_HEIGHT_PX` (a wide, short
  card), giving the column a clean, uniform left edge regardless of teammate count.

---

## Win-Rate Ring spec

**Geometry**
- Outer diameter = `RING_DIAMETER_PX`; donut wall thickness = `RING_THICKNESS_PX`
  (inner hole diameter = `RING_DIAMETER_PX − 2 × RING_THICKNESS_PX`). The wall is deliberately
  **thin** so the colored band hugs the outer edge like the ult HUD's grouped charge ticks, while
  the large inner hole keeps the center percentage clearly readable.
- The full ring spans `RING_FULL_SWEEP_DEG` (one complete circle).
- Arcs **start at 12 o'clock** (`RING_START_ANGLE_DEG`, in Qt's convention where 0° is at
  3 o'clock and angles increase counter-clockwise, so 90° = top).
- Sweep direction is **clockwise** (`RING_SWEEP_DIRECTION`), so the win arc grows clockwise from
  the top and the loss arc completes the circle back to the top.

**Track + rim (keep the ult-ring character)**
- A **dark recessed track** (`COLOR_RING_TRACK`) is drawn first under the full circle, inset by
  `RING_TRACK_INSET_PX` so it reads as a recessed channel.
- A **beveled double border** frames the donut: a bright outer rim of
  `RING_BEVEL_OUTER_WIDTH_PX` in `COLOR_RING_BEVEL_OUTER`, plus a darker inner bevel of
  `RING_BEVEL_INNER_WIDTH_PX` in `COLOR_RING_BEVEL_INNER`. With the thin wall these are kept to
  hairlines so they frame, not fill, the band.
- A **cyan accent hairline** (`COLOR_RING_ACCENT_CYAN`, `RING_ACCENT_WIDTH_PX`) traces the inner
  edge of the track for the HUD sheen.
- A soft **glow** (`COLOR_RING_GLOW` at `COLOR_RING_GLOW_ALPHA`) surrounds the ring with
  `RING_GLOW_BLUR_PX` blur and `RING_GLOW_SPREAD_PX` spread.

**Arc-color rules**
- **Win arc** = `COLOR_WIN_ARC` (warm yellow-green). **Loss arc** = `COLOR_LOSS_ARC` (harsh
  red). The win arc starts at `RING_START_ANGLE_DEG` and sweeps clockwise by the win-rate share;
  the loss arc continues and fills the remainder back toward the start, so the two together
  account for the whole ring (green% + red% = 100%).
- **Arc seam**: a small dark seam of `RING_ARC_GAP_DEG` separates the green and red arcs at each
  boundary (the win→loss boundary and the loss→win boundary back at the start). The seam is **the
  dark recessed track (`COLOR_RING_TRACK`) showing through** the gap — no extra color token is
  needed. This keeps the two arcs visually distinct rather than bleeding into one another.
- Each arc carries a faint same-color glow at `COLOR_ARC_GLOW_ALPHA` (the glow reuses that arc's
  own RGB) so the lit segment feels emissive like the ult charge.
- Win rate 0% → fully red; 100% → fully green.
- **No data / unresolved teammate** → draw no colored arc; only the dark track + rim show (a
  neutral "empty" state), and the center shows a dash instead of a percentage.

**Tick / segment treatment (the committed look)**
- The filled arcs render as a band of short radial **tick segments**, echoing the thin ult
  charge ticks: `RING_TICK_COUNT` evenly spaced segments around the full circle, each separated
  by `RING_TICK_GAP_DEG` and each `RING_TICK_LENGTH_PX` long in the radial direction (sitting
  within the thin wall near the outer edge). With `RING_TICK_COUNT = 50`, **each tick = 2%** of
  win rate, so: `green_tick_count = round(win_rate_percent × RING_TICK_COUNT ÷ 100)`, and the
  remaining ticks are red, with the `RING_ARC_GAP_DEG` seam inserted at the color boundaries.
- This segmented-tick rendering is the spec, not a fallback. *(Only if ticks prove impossible to
  render cleanly may a smooth solid arc — `win_sweep_deg = win_fraction × RING_FULL_SWEEP_DEG` —
  be used as an emergency fallback; it is not the intended look.)*

**Center text**
- The win-rate percentage (e.g. `63%`) is centered in the hole in HUD style: `FONT_FAMILY_PRIMARY`,
  number at `FONT_RING_CENTER_SIZE_PT`, the trailing `%` at the smaller `FONT_RING_SUFFIX_SIZE_PT`,
  weight `FONT_RING_CENTER_WEIGHT`, italic `FONT_RING_CENTER_ITALIC`, tracking
  `FONT_HUD_LETTER_SPACING_PCT`, color `COLOR_CENTER_TEXT`, over a drop shadow offset diagonally by
  `CENTER_TEXT_SHADOW_OFFSET_PX` (`COLOR_CENTER_TEXT_SHADOW` at `COLOR_CENTER_TEXT_SHADOW_ALPHA`)
  for legibility above the glow.
- The number reflects the configured **win-rate basis** (see Card spec / Open Questions); the
  basis only changes the value, never the visual treatment.

**Motion**
- When a card's data first resolves or updates, the colored ticks sweep up to their target over
  `RING_FILL_ANIM_MS` using the `RING_FILL_EASING` curve, while the center number counts up to its
  value over `VALUE_TWEEN_MS` (the two run together so the ring and number land in sync).
- At rest, the cyan ring/icon glow breathes on a slow loop with period `GLOW_PULSE_PERIOD_MS` for
  the live HUD feel. These are the only idle and transition animations; nothing else moves.

---

## Card spec

- **Orientation**: a **wide horizontal card** — a single row laid out left → right, all elements
  vertically centered: **hero shield icon | win-rate ring | label area**. The card is wide and
  short (`CARD_WIDTH_PX` × `CARD_HEIGHT_PX`).
- **Panel**: a rounded-rectangle filled with `COLOR_CARD_BG` at `COLOR_CARD_BG_ALPHA`, corner
  radius `CARD_CORNER_RADIUS_PX`, with a `CARD_BORDER_WIDTH_PX` border in `COLOR_CARD_BORDER`
  at `COLOR_CARD_BORDER_ALPHA`.
- **Accent**: a vertical cyan accent bar of `CARD_ACCENT_WIDTH_PX` in `COLOR_CARD_ACCENT` runs
  down the panel's left inside edge (an Overwatch HUD signature).
- **Inner padding**: `CARD_PADDING_PX` on all sides. The content height (card height minus top and
  bottom padding) equals both `ICON_BADGE_HEIGHT_PX` and `RING_DIAMETER_PX`, so the shield and the
  ring share a common height and baseline.
- **Row elements** — left → right, vertically centered, each separated by `CARD_ELEMENT_GAP_PX`:
  1. **Hero shield icon** (`ICON_BADGE_WIDTH_PX` × `ICON_BADGE_HEIGHT_PX`).
  2. **Win-rate ring** (`RING_DIAMETER_PX`), *directly next to the icon* per "the Hero Icon with
     Win Rate right next to it." Icon and ring sit adjacent but **never overlap**.
  3. **Label area** (`LABEL_AREA_WIDTH_PX` × `LABEL_AREA_HEIGHT_PX`), left-aligned, holding two
     stacked lines separated by `LABEL_LINE_SPACING_PX`:
     - **Line 1 — player name**: `COLOR_LABEL_PRIMARY`, `FONT_LABEL_NAME_SIZE_PT`, weight
       `FONT_LABEL_NAME_WEIGHT`.
     - **Line 2 — most-played hero**: `COLOR_LABEL_SECONDARY`, `FONT_LABEL_SUB_SIZE_PT`, weight
       `FONT_LABEL_SUB_WEIGHT`.
     - The area is intentionally sized to leave room for one or two extra metric lines later
       (e.g. games played).
- Text wider than the label area is truncated with an ellipsis (no wrapping), to preserve the
  uniform card size.

---

## Hero icon spec

- **Frame shape**: a **shield/badge** silhouette matching the concept — a rectangle with rounded
  top corners (`ICON_TOP_CORNER_RADIUS_PX`) whose bottom edges angle inward to a centered point
  that drops `ICON_BOTTOM_POINT_DEPTH_PX` below the sides. This is the committed shape (a plain
  rounded rectangle is no longer being considered).
- **Frame border**: a glowing cyan edge `ICON_FRAME_WIDTH_PX` wide in `COLOR_ICON_FRAME`, backed
  by a darker inner bevel line `ICON_FRAME_INNER_WIDTH_PX` wide in `COLOR_ICON_FRAME_INNER`
  (mirroring the ring's double rim), and a soft outer glow (`COLOR_ICON_FRAME_GLOW` at
  `COLOR_ICON_FRAME_GLOW_ALPHA`, blur `ICON_FRAME_GLOW_BLUR_PX`) so the badge and ring share one
  cyan family.
- **Portrait**: the hero portrait scales to fill and is clipped to the shield path.
- **Fallback (missing / loading / unknown hero)**: fill the shield with `COLOR_ICON_BG_FALLBACK`
  and center the hero's initial(s) or `?` in `COLOR_ICON_FALLBACK_TEXT` at
  `FONT_ICON_FALLBACK_SIZE_PT` in weight `FONT_ICON_FALLBACK_WEIGHT`, keeping the same shield +
  frame + glow so the layout never shifts.

---

## Game-Closed Stats View (standalone profile window)

> A **second surface** in the same visual language, shown when **Overwatch is not running**. It
> presents the **user's own** profile — overall stats plus their **top-3 most-played heroes** — in a
> normal application window instead of the transparent teammate overlay. It reuses the existing
> language verbatim (win-rate ring, shield hero icon, rounded navy panels, cyan accent, typography
> / font chain) and only adds tokens for the genuinely new pieces (the window, the profile header,
> the rank badge, the readouts, the state messages).

**Relationship to the overlay — same DNA, different chrome.** Only one surface is visible at a
time (overlay while the game runs; this view when it is closed).

| | Teammate overlay | Game-closed stats view |
|---|---|---|
| Whose data | tracked teammates | the **user's own** profile |
| Window | transparent, click-through, always-on-top, off-taskbar, corner-anchored | **opaque, focusable, normal taskbar window**, centered on open |
| Content | a column of small wide cards | a **profile header** + a **top-3 hero list** |
| When | during hero select (game running) | when **Overwatch is closed** |

### Window & layout
- **Frame**: preferred is a **frameless, opaque, rounded** panel — corner radius
  `STATS_WINDOW_CORNER_RADIUS_PX`, filled with `COLOR_STATS_WINDOW_BG` @ `COLOR_STATS_WINDOW_BG_ALPHA`,
  with a `CARD_BORDER_WIDTH_PX` border in `COLOR_CARD_BORDER`. When frameless, the **profile header
  doubles as the drag region** and a small close **✕** (`FONT_SECTION_TITLE_SIZE_PT`,
  `COLOR_LABEL_SECONDARY`) sits in the top-right inside the window padding. *(An OS-standard title bar
  is an acceptable fallback if frameless adds too much code — see Open Question #9.)*
- **Size**: fixed width `STATS_WINDOW_WIDTH_PX`; height is the natural sum of the stacked sections at
  their tokenized heights (deterministic — no separate magic constant). Opens **centered on the
  primary screen**.
- **Padding**: `STATS_WINDOW_PADDING_PX` on all sides; the content column is
  `STATS_WINDOW_WIDTH_PX − 2 × STATS_WINDOW_PADDING_PX` wide.
- **Vertical structure** (top → bottom), each block separated by `STATS_SECTION_GAP_PX`:
  1. **Profile header panel** (overall stats) — fixed `PROFILE_HEADER_HEIGHT_PX`.
  2. **"TOP HEROES" section title**.
  3. **Top-hero list / state body** — fixed `STATS_BODY_HEIGHT_PX`. This region swaps between the
     3-row hero list and a centered state message, so the **window never resizes between data states**.
  4. **Footer status line**.

### Profile header spec (the user's overall stats)
- One **rounded navy panel** reusing the Card panel exactly (`COLOR_CARD_BG` @ `COLOR_CARD_BG_ALPHA`,
  `CARD_CORNER_RADIUS_PX`, `CARD_BORDER_WIDTH_PX` border in `COLOR_CARD_BORDER`, and the left cyan
  accent bar `CARD_ACCENT_WIDTH_PX` in `COLOR_CARD_ACCENT`), inner padding `CARD_PADDING_PX`, height
  `PROFILE_HEADER_HEIGHT_PX`.
- **Row**, vertically centered, left → right, separated by `PROFILE_ELEMENT_GAP_PX`:
  1. **Large win-rate ring** — the full **Win-Rate Ring spec** rendered at `PROFILE_RING_DIAMETER_PX`
     (everything else — ticks, seam, rim, glow, center typography — unchanged). It shows the user's
     **overall** win rate and is the "hero/profile header with the large win-rate ring." The overall
     win rate drives the green/red split exactly as in the overlay; no special-casing.
  2. **Text block** (fills the remaining width), vertically centered:
     - **Name** — the user's BattleTag, `FONT_PROFILE_NAME_SIZE_PT` / `FONT_PROFILE_NAME_WEIGHT`,
       `COLOR_LABEL_PRIMARY`, elided if too long.
     - **Subtitle** — the win-rate basis label (e.g. "Competitive + Quick Play"), `FONT_LABEL_SUB_SIZE_PT`
       / `FONT_LABEL_SUB_WEIGHT`, `COLOR_LABEL_SECONDARY`.
     - **Overall stat readouts** — a bottom row of three: **GAMES / WINS / LOSSES**, separated by
       `STATS_READOUT_GAP_PX` with thin `CARD_BORDER_WIDTH_PX` dividers in `COLOR_CARD_BORDER` between
       them. Each readout is a value (`FONT_STAT_VALUE_SIZE_PT` / `FONT_STAT_VALUE_WEIGHT`,
       `COLOR_LABEL_PRIMARY`) above a caption (`FONT_STAT_CAPTION_SIZE_PT` / `FONT_STAT_CAPTION_WEIGHT`,
       tracked by `FONT_SECTION_TITLE_LETTER_SPACING_PCT`, `COLOR_LABEL_SECONDARY`).

### Section title spec
- The caps label **"TOP HEROES"**: `FONT_SECTION_TITLE_SIZE_PT` / `FONT_SECTION_TITLE_WEIGHT`, color
  `COLOR_CARD_ACCENT` (cyan), tracked by `FONT_SECTION_TITLE_LETTER_SPACING_PCT`, left-aligned.

### Top-Heroes list spec (top-3)
- Exactly **three hero rows**, stacked and separated by `CARD_SPACING_PX` (reused), filling the fixed
  `STATS_BODY_HEIGHT_PX` region (`= 3 × CARD_HEIGHT_PX + 2 × CARD_SPACING_PX`).
- **Each row reuses the Card spec verbatim** (panel, left accent bar, `CARD_PADDING_PX`,
  `CARD_ELEMENT_GAP_PX`, height `CARD_HEIGHT_PX`) and spans the **full content width** (wider than the
  overlay card). The only additions are the **rank badge** and the per-hero content mapping. Row
  elements, left → right, vertically centered, each separated by `CARD_ELEMENT_GAP_PX`:
  1. **Rank badge** — a circle `RANK_BADGE_DIAMETER_PX` filled `COLOR_RING_TRACK` with a
     `RANK_BADGE_BORDER_WIDTH_PX` border in `COLOR_CARD_ACCENT`, the numeral **1–3** centered in
     `FONT_RANK_SIZE_PT` / `FONT_RANK_WEIGHT`, `COLOR_LABEL_PRIMARY`. The circle echoes the ring motif.
  2. **Hero shield** (`ICON_BADGE_WIDTH_PX × ICON_BADGE_HEIGHT_PX`) — that hero's portrait per the
     **Hero icon spec** (including the `?` fallback).
  3. **Win-rate ring** (`RING_DIAMETER_PX`) — that hero's win rate.
  4. **Label** — Line 1 hero name (`FONT_LABEL_NAME_SIZE_PT` / `FONT_LABEL_NAME_WEIGHT`,
     `COLOR_LABEL_PRIMARY`); Line 2 games on that hero, e.g. "128 games" (`FONT_LABEL_SUB_SIZE_PT` /
     `FONT_LABEL_SUB_WEIGHT`, `COLOR_LABEL_SECONDARY`), separated by `LABEL_LINE_SPACING_PX`. Both elided.

### Footer status line
- One line: a **status dot** (`STATS_STATUS_DOT_DIAMETER_PX`) + caption (`FONT_LABEL_SUB_SIZE_PT` /
  `FONT_LABEL_SUB_WEIGHT`, `COLOR_LABEL_SECONDARY`), separated by `CARD_ELEMENT_GAP_PX`. The dot color
  encodes the data state, **reusing existing colors only**:
  - **OK** → `COLOR_WIN_ARC` (green) — e.g. "Updated • OverFast".
  - **Loading** → `COLOR_CARD_ACCENT` (cyan), **breathing** on `GLOW_PULSE_PERIOD_MS` — "Loading profile…".
  - **Private / not found** → `COLOR_LABEL_SECONDARY` (neutral) — "Private / not found".
  - **Network error** → `COLOR_LOSS_ARC` (red) — "Network error — will retry".

### Data states (all four — no layout shift)
The **header panel** and the **`STATS_BODY_HEIGHT_PX` region** are always present; only their contents
change, so the window stays the same size across every state.
- **Loading** — the header renders its scaffold: the BattleTag name (known from config), the ring in
  its **no-data** form (dash center, no colored arcs) with the cyan glow **breathing**, and stat
  readouts showing "—". The body shows three **placeholder rows** (shield `?` fallback, no-data ring,
  dimmed label text). Footer dot cyan/breathing. When data resolves, rings fill (`RING_FILL_ANIM_MS`,
  `RING_FILL_EASING`), center numbers count up (`VALUE_TWEEN_MS`), and rows stagger in top-down
  (`CARD_STAGGER_MS`).
- **OK** — everything populated as specced above.
- **Private / not found** — the header shows the BattleTag, the **no-data ring** (dash) and "—"
  readouts; the body region is **replaced** by a centered **state message**: a headline "Profile is
  private or not found" (`FONT_STATS_MESSAGE_SIZE_PT` / `FONT_STATS_MESSAGE_WEIGHT`,
  `COLOR_LABEL_PRIMARY`) above subtext "Set this profile to Public on your Blizzard account to see
  stats." (`FONT_LABEL_SUB_SIZE_PT` / `FONT_LABEL_SUB_WEIGHT`, `COLOR_LABEL_SECONDARY`), separated by
  `STATS_MESSAGE_GAP_PX`. Footer dot neutral.
- **Network error** — the same header scaffold; the body region is **replaced** by a centered state
  message: headline "Can't reach the stats service" + subtext "Check your connection — will retry
  automatically." (same message typography). Footer dot red.

### Motion
Reuses the overlay's motion vocabulary only — **no new timing tokens**:
- The window fades in over `CARD_FADE_IN_MS`; state-body swaps cross-fade over the same token.
- Rings fill (`RING_FILL_ANIM_MS` / `RING_FILL_EASING`) and centers count up (`VALUE_TWEEN_MS`) together.
- The three top-hero rows stagger in top-down via `CARD_STAGGER_MS`.
- At rest, the cyan glow on the rings and shields **breathes** on `GLOW_PULSE_PERIOD_MS`.

> **Notes for the code subagent (product / architecture assumptions — design only, not specced here):**
> - **Game-running detection is out of scope for design.** This spec assumes the app shows the **stats
>   view when Overwatch is closed** and the **teammate overlay while it is running** (mutually
>   exclusive). The *mechanism* (process scan, manual toggle, etc.) is the code subagent's call.
> - **The user's own BattleTag source is out of scope.** Assume a new `config.json` field (e.g. an
>   `owner` / `self` BattleTag) feeds this view.
> - **Data the view needs the data layer to surface:** overall **win rate %**, **games / wins /
>   losses**, and the **basis label**; plus the **top-3 heroes**, each with **portrait key, hero name,
>   win rate %, and games played**. The data layer currently resolves only a single most-played hero +
>   overall rate, so extending it is code work.
> - **Refresh cadence and how the window is launched are behavioral** — design covers only the look.

---

## In-App Configuration Screen (settings window)

> The settings surface for `ISSUES.md` → *C-SA CB "No in-app configuration screen"* / Question #2.
> A focusable window that edits everything in `config.json` — the tracked teammate BattleTags plus the
> behavioral fields — without hand-editing JSON. It **reuses the game-closed stats-window chrome**
> (`COLOR_STATS_WINDOW_BG` @ `COLOR_STATS_WINDOW_BG_ALPHA`, `STATS_WINDOW_CORNER_RADIUS_PX`,
> `STATS_WINDOW_PADDING_PX`, `STATS_SECTION_GAP_PX`, the section-title + label typography) and the
> overlay's navy-panel / cyan-accent language. New tokens cover only the form-control kit.

### Window & layout
- Same chrome and behavior as the stats view: **opaque, focusable, centered**, frameless rounded panel
  (`COLOR_STATS_WINDOW_BG` @ `COLOR_STATS_WINDOW_BG_ALPHA`, `STATS_WINDOW_CORNER_RADIUS_PX`,
  `CARD_BORDER_WIDTH_PX` border in `COLOR_CARD_BORDER`), inner padding `STATS_WINDOW_PADDING_PX`. Width
  is `CONFIG_WINDOW_WIDTH_PX` (wider than the stats view to fit the two-column form); height is the
  natural sum of its sections (no magic constant), and the teammate list scrolls once it exceeds
  `CONFIG_LIST_MAX_HEIGHT_PX`.
- **Vertical structure** (top → bottom), blocks separated by `STATS_SECTION_GAP_PX`:
  1. **Header bar** — title **"SETTINGS"** (`FONT_SECTION_TITLE_SIZE_PT` / `FONT_SECTION_TITLE_WEIGHT`,
     `COLOR_CARD_ACCENT`, tracked by `FONT_SECTION_TITLE_LETTER_SPACING_PCT`) on the left; a close **✕**
     (`FONT_SECTION_TITLE_SIZE_PT`, `COLOR_LABEL_SECONDARY`) on the right. The header doubles as the
     drag region.
  2. **"TRACKED TEAMMATES"** section — the list + the add row.
  3. **"PREFERENCES"** section — the behavioral fields.
  4. **Action bar** — validation status (left) + Cancel / Save (right), above a `CARD_BORDER_WIDTH_PX`
     divider in `COLOR_CARD_BORDER`.

### Form-control styling (the OW-HUD control kit)
All controls share one height (`CONTROL_HEIGHT_PX`), corner radius (`CONTROL_CORNER_RADIUS_PX`), and
horizontal text inset (`CONTROL_PADDING_X_PX`) so the form reads as one system.
- **Text input** — a recessed field: fill `COLOR_RING_TRACK`, `CARD_BORDER_WIDTH_PX` border in
  `COLOR_CARD_BORDER`, text `FONT_INPUT_SIZE_PT` / `FONT_INPUT_WEIGHT` in `COLOR_LABEL_PRIMARY`,
  placeholder in `COLOR_LABEL_SECONDARY`. **Focus**: border → `COLOR_CARD_ACCENT` at
  `CONTROL_FOCUS_BORDER_WIDTH_PX`. **Invalid**: border → `COLOR_LOSS_ARC` at
  `CONTROL_FOCUS_BORDER_WIDTH_PX` (see States).
- **Dropdown** — a text input with a chevron glyph (`COLOR_LABEL_SECONDARY`) at the right inset; the
  popup is a `COLOR_CARD_BG` @ `COLOR_CARD_BG_ALPHA` panel (`CARD_CORNER_RADIUS_PX`, `COLOR_CARD_BORDER`
  border) whose items are `CONTROL_HEIGHT_PX` tall, item text `FONT_INPUT_*` in `COLOR_LABEL_PRIMARY`,
  hover fill `COLOR_CARD_ACCENT` @ `COLOR_ROW_HOVER_ALPHA`, the selected item's text `COLOR_CARD_ACCENT`.
- **Segmented toggle** (2-state choice; echoes the OW mode tabs) — a `COLOR_RING_TRACK` track split into
  two equal segments; the selected segment fills `COLOR_CARD_ACCENT` with `COLOR_BUTTON_PRIMARY_TEXT`
  text, the unselected segment shows `COLOR_LABEL_SECONDARY` text; height `CONTROL_HEIGHT_PX`, radius
  `CONTROL_CORNER_RADIUS_PX`.
- **Number input** — a text input restricted to digits with a trailing unit caption (e.g. "sec",
  `FONT_STAT_CAPTION_SIZE_PT` / `FONT_STAT_CAPTION_WEIGHT`, `COLOR_LABEL_SECONDARY`) in the right inset.
- **Hotkey capture** — a text input that shows the current combo (e.g. "Ctrl + Alt + O", `FONT_INPUT_*`);
  on focus it reads "Press keys…" in `COLOR_LABEL_SECONDARY` until a combo is captured. (Capture is code.)
- **Buttons** — height `CONTROL_HEIGHT_PX`, radius `CONTROL_CORNER_RADIUS_PX`, horizontal padding
  `BUTTON_PADDING_X_PX`, label `FONT_LABEL_NAME_SIZE_PT` / `FONT_LABEL_NAME_WEIGHT` upper-cased and
  tracked by `FONT_SECTION_TITLE_LETTER_SPACING_PCT`:
  - **Primary** (Save, Add) — fill `COLOR_CARD_ACCENT`, text `COLOR_BUTTON_PRIMARY_TEXT`; hover fill
    brightens to `COLOR_RING_BEVEL_OUTER`.
  - **Secondary** (Cancel) — transparent fill, `CARD_BORDER_WIDTH_PX` border in `COLOR_CARD_BORDER`,
    text `COLOR_LABEL_PRIMARY`; hover border + text → `COLOR_CARD_ACCENT`.
  - **Icon button** (row edit / remove) — `ICON_BUTTON_SIZE_PX` square, transparent fill; edit glyph
    `COLOR_LABEL_SECONDARY` (hover → `COLOR_CARD_ACCENT`), remove glyph `COLOR_LOSS_ARC`.

### Tracked-teammates list spec (`battletags`)
- A vertical list of **teammate rows**, each `CONFIG_ROW_HEIGHT_PX` tall, full content width, padded
  `CARD_PADDING_PX` horizontally, separated by a `CARD_BORDER_WIDTH_PX` divider in `COLOR_CARD_BORDER`.
  It scrolls once the rows exceed `CONFIG_LIST_MAX_HEIGHT_PX`.
- **Row (view mode)** — BattleTag text on the left (`FONT_INPUT_*`, `COLOR_LABEL_PRIMARY`, elided); on
  the right an **edit** icon button then a **remove** icon button, separated by `CARD_ELEMENT_GAP_PX`.
  Row hover fill `COLOR_CARD_ACCENT` @ `COLOR_ROW_HOVER_ALPHA`.
- **Row (edit mode)** — the BattleTag text becomes an inline **text input** filling the row minus the
  action buttons; the edit icon becomes a **confirm ✓** (`COLOR_CARD_ACCENT`); validation applies inline.
- **Add row** (below the list, gap `CONFIG_FIELD_GAP_PX`) — a **text input** filling the width minus an
  **"Add"** primary button (`CARD_ELEMENT_GAP_PX` between them); placeholder "Add BattleTag — e.g.
  Name#1234".

### Preferences form spec
- A field = a **label** above its control. Label: `FONT_LABEL_SUB_SIZE_PT` / `FONT_LABEL_SUB_WEIGHT`,
  `COLOR_LABEL_SECONDARY`, upper-cased and tracked by `FONT_SECTION_TITLE_LETTER_SPACING_PCT`; gap to
  its control `CONFIG_LABEL_GAP_PX`. Field rows are separated by `CONFIG_FIELD_GAP_PX`; two-column rows
  split the content width with `CONFIG_COLUMN_GAP_PX` between the columns.
- Fields (mapped to `config.json`):
  1. **Your BattleTag** *(the `owner` / `self` field the game-closed view assumes)* — full-width text
     input. Placeholder "Your BattleTag — e.g. Name#1234".
  2. **Win-rate basis** (`winrate_basis`) — segmented toggle "Comp Only | Combined". · **Overlay
     anchor** (`anchor`) — dropdown (Top-Left / Top-Right / Bottom-Left / Bottom-Right).
  3. **Refresh interval** (`refresh_interval_seconds`) — number input, unit "sec". · **Font override**
     (`font_family`) — text input, placeholder "Default (Koverwatch)".
  4. **Show / Hide hotkey** (`toggle_hotkey`) — hotkey capture. · **Quit hotkey** (`quit_hotkey`) —
     hotkey capture.

### States
- **Empty list** — with no teammates, the list region shows a centered hint "No teammates tracked yet —
  add one below." (`FONT_LABEL_SUB_*`, `COLOR_LABEL_SECONDARY`) at a minimum height of
  `CONFIG_ROW_HEIGHT_PX`, so the add row never jumps.
- **Invalid input (inline)** — a malformed BattleTag (not `Name#1234`) gives the offending input an
  error border (`COLOR_LOSS_ARC` at `CONTROL_FOCUS_BORDER_WIDTH_PX`) and a helper line below it in
  `COLOR_LOSS_ARC` (`FONT_LABEL_SUB_*`): "Use the format Name#1234." A helper line's height is reserved
  beneath validated inputs so the layout never shifts when an error appears.
- **Save feedback** — the action bar's left side carries a status line (a dot
  `STATS_STATUS_DOT_DIAMETER_PX` + caption `FONT_LABEL_SUB_*`, reusing the stats-view footer pattern):
  - **Saved** → green dot `COLOR_WIN_ARC` + "Settings saved", fading in over `CARD_FADE_IN_MS`.
  - **Blocked by errors** (Save pressed while invalid) → red dot `COLOR_LOSS_ARC` + "Fix the
    highlighted field(s) to save."; the first invalid field scrolls into view.

### Motion
- The window fades in over `CARD_FADE_IN_MS`; inline error and save-confirmation messages fade over the
  same token. No idle/HUD animation — this is an interactive utility window, not a live HUD.

> **Notes for the code subagent (invocation recommendation + product assumptions — design only):**
> - **Recommended invocation (Question #2): both.** Auto-open the settings window on **first run / when
>   the config is missing or has zero valid BattleTags**, and make it reachable any time via a **global
>   hotkey** plus a **gear (settings) affordance in the game-closed stats-view header**. (First-run
>   detection and registering the hotkey alongside the existing toggle/quit keys are code.)
> - **Persistence**: assume Save validates, then writes every field **back through `config.py`** to
>   `config.json` (the same loader that feeds the overlay and stats view); Cancel discards. A live reload
>   of the overlay / stats view after Save is a code concern.
> - **Validation** of the BattleTag format (`Name#1234`), refresh-interval bounds, and hotkey-combo
>   capture/serialization (pynput `<ctrl>+<alt>+o` style) are code; this spec defines only their visual
>   treatment.
> - **`owner` / `self` field**: this screen edits the same own-BattleTag field the game-closed view
>   assumes; it is **not yet in `config.example.json`** and must be added by the code subagent.

---

## Design Tokens

> **Conventions:** Colors are 6-digit `#RRGGBB`. Transparency is given by separate `*_ALPHA`
> tokens as 8-bit integers `0–255` (0 = transparent, 255 = opaque) so the code subagent can call
> `QColor(r, g, b, a)` with no hex-alpha-ordering ambiguity. Angles are in degrees. Sizes are
> device-independent pixels. Type sizes are points (`pt`). Durations are milliseconds.

| Group | Token | Value | Controls |
|---|---|---|---|
| color | `COLOR_OVERLAY_BG` | `#05080D` | Overlay window background base (kept transparent via alpha) |
| color | `COLOR_OVERLAY_BG_ALPHA` | `0` | Overlay window background opacity (fully transparent) |
| color | `COLOR_CARD_BG` | `#0E1626` | Card panel fill (dark navy) |
| color | `COLOR_CARD_BG_ALPHA` | `200` | Card panel fill opacity (semi-transparent) |
| color | `COLOR_CARD_BORDER` | `#2A3A5C` | Card panel border line |
| color | `COLOR_CARD_BORDER_ALPHA` | `230` | Card panel border opacity |
| color | `COLOR_CARD_ACCENT` | `#4DD2E6` | Cyan accent bar on the card's left edge |
| color | `COLOR_RING_TRACK` | `#0B1220` | Dark recessed donut track behind the arcs (also shows through the arc seam) |
| color | `COLOR_RING_BEVEL_OUTER` | `#5FD8EC` | Bright outer rim of the beveled double border |
| color | `COLOR_RING_BEVEL_INNER` | `#1C5C73` | Darker inner bevel of the double border |
| color | `COLOR_RING_ACCENT_CYAN` | `#4DD2E6` | Cyan accent hairline on the track inner edge |
| color | `COLOR_RING_GLOW` | `#36C8E0` | Cyan glow color around the ring |
| color | `COLOR_RING_GLOW_ALPHA` | `130` | Ring glow opacity |
| color | `COLOR_WIN_ARC` | `#6FD23A` | Win-rate arc (warm yellow-green) |
| color | `COLOR_LOSS_ARC` | `#E53935` | Loss-rate arc (harsh red) |
| color | `COLOR_ARC_GLOW_ALPHA` | `110` | Opacity of each arc's same-color emissive glow |
| color | `COLOR_CENTER_TEXT` | `#F0F4F8` | Win-rate number in ring center (off-white) |
| color | `COLOR_CENTER_TEXT_SHADOW` | `#06090F` | Drop shadow behind the center number |
| color | `COLOR_CENTER_TEXT_SHADOW_ALPHA` | `170` | Center-number shadow opacity |
| color | `COLOR_LABEL_PRIMARY` | `#FFFFFF` | Player-name label text |
| color | `COLOR_LABEL_SECONDARY` | `#9FB2CC` | Most-played-hero / sub-label text |
| color | `COLOR_ICON_FRAME` | `#4DD2E6` | Hero shield frame border (cyan) |
| color | `COLOR_ICON_FRAME_INNER` | `#1C5C73` | Hero shield inner bevel line |
| color | `COLOR_ICON_FRAME_GLOW` | `#36C8E0` | Hero shield frame outer glow |
| color | `COLOR_ICON_FRAME_GLOW_ALPHA` | `120` | Hero shield frame glow opacity |
| color | `COLOR_ICON_BG_FALLBACK` | `#1A2740` | Fallback fill when a portrait is missing |
| color | `COLOR_ICON_FALLBACK_TEXT` | `#C8D6EC` | Fallback initial / `?` text color |
| color | `COLOR_STATS_WINDOW_BG` | `#080D17` | Game-closed stats-window backdrop (opaque deep navy, between overlay and card) |
| color | `COLOR_STATS_WINDOW_BG_ALPHA` | `255` | Stats-window backdrop opacity (fully opaque) |
| color | `COLOR_BUTTON_PRIMARY_TEXT` | `#06121A` | Dark text on the cyan primary button (Save / Add) |
| color | `COLOR_ROW_HOVER_ALPHA` | `30` | Hover-fill opacity for list rows & dropdown items (applied to `COLOR_CARD_ACCENT` rgb) |
| size | `OVERLAY_MARGIN_X_PX` | `24` | Column inset from the screen's left edge |
| size | `OVERLAY_MARGIN_Y_PX` | `96` | Column inset from the top (clears the game nav bar) |
| size | `CARD_WIDTH_PX` | `320` | Fixed card width (wide horizontal card) |
| size | `CARD_HEIGHT_PX` | `102` | Fixed card height (short; = padding×2 + content height) |
| size | `CARD_SPACING_PX` | `14` | Vertical gap between stacked cards (enforces no overlap) |
| size | `CARD_CORNER_RADIUS_PX` | `10` | Card panel corner radius |
| size | `CARD_BORDER_WIDTH_PX` | `1` | Card panel border thickness |
| size | `CARD_ACCENT_WIDTH_PX` | `3` | Width of the card's left cyan accent bar |
| size | `CARD_PADDING_PX` | `12` | Inner padding inside each card |
| size | `CARD_ELEMENT_GAP_PX` | `10` | Horizontal gap between row elements (icon ↔ ring ↔ label) |
| size | `LABEL_AREA_WIDTH_PX` | `134` | Width of the label area (= card width − padding − icon − ring − 2 gaps) |
| size | `LABEL_AREA_HEIGHT_PX` | `38` | Height occupied by the two stacked label lines |
| size | `LABEL_LINE_SPACING_PX` | `3` | Vertical gap between the two label lines |
| size | `ICON_BADGE_WIDTH_PX` | `64` | Hero shield width |
| size | `ICON_BADGE_HEIGHT_PX` | `78` | Hero shield height (= card content height) |
| size | `ICON_FRAME_WIDTH_PX` | `3` | Hero shield frame border thickness |
| size | `ICON_FRAME_INNER_WIDTH_PX` | `1` | Hero shield inner bevel line width (hairline; mirrors the ring's inner bevel) |
| size | `ICON_TOP_CORNER_RADIUS_PX` | `8` | Rounding of the shield's top corners |
| size | `ICON_BOTTOM_POINT_DEPTH_PX` | `12` | How far the shield's bottom point drops below its sides |
| size | `ICON_FRAME_GLOW_BLUR_PX` | `6` | Blur radius of the hero shield frame glow |
| size | `RING_DIAMETER_PX` | `78` | Outer diameter of the win-rate donut (= card content height) |
| size | `RING_THICKNESS_PX` | `6` | Donut wall thickness (thin band near the outer edge) |
| size | `RING_TICK_LENGTH_PX` | `5` | Radial length of each colored tick (within the thin wall) |
| size | `RING_TRACK_INSET_PX` | `1` | Inset of the recessed track for depth |
| size | `RING_BEVEL_OUTER_WIDTH_PX` | `1` | Outer rim line width (hairline on the thin wall) |
| size | `RING_BEVEL_INNER_WIDTH_PX` | `1` | Inner bevel line width (hairline on the thin wall) |
| size | `RING_ACCENT_WIDTH_PX` | `1` | Cyan accent hairline width |
| size | `RING_GLOW_BLUR_PX` | `8` | Blur radius of the ring glow |
| size | `RING_GLOW_SPREAD_PX` | `2` | Spread of the ring glow |
| size | `RING_FULL_SWEEP_DEG` | `360` | Degrees in a full ring (avoids a bare 360) |
| size | `RING_START_ANGLE_DEG` | `90` | Arc start at 12 o'clock (Qt convention, CCW-positive) |
| size | `RING_SWEEP_DIRECTION` | `"clockwise"` | Direction the arcs grow from the start angle |
| size | `RING_TICK_COUNT` | `50` | Tick segments around the full ring (each = 2% of win rate) |
| size | `RING_TICK_GAP_DEG` | `2` | Angular gap between adjacent tick segments |
| size | `RING_ARC_GAP_DEG` | `6` | Dark seam (track showing through) at each win/loss arc boundary |
| size | `CENTER_TEXT_SHADOW_OFFSET_PX` | `1` | Diagonal offset of the win-rate center number's drop shadow |
| size | `STATS_WINDOW_WIDTH_PX` | `480` | Fixed width of the game-closed stats window |
| size | `STATS_WINDOW_PADDING_PX` | `20` | Inner padding around the stats-window content |
| size | `STATS_WINDOW_CORNER_RADIUS_PX` | `16` | Corner radius of the frameless stats window |
| size | `STATS_SECTION_GAP_PX` | `16` | Vertical gap between stats-window sections (header / title / body / footer) |
| size | `PROFILE_HEADER_HEIGHT_PX` | `156` | Profile header panel height (= `PROFILE_RING_DIAMETER_PX` + 2 × `CARD_PADDING_PX`) |
| size | `PROFILE_RING_DIAMETER_PX` | `132` | Diameter of the large overall win-rate ring in the header |
| size | `PROFILE_ELEMENT_GAP_PX` | `20` | Gap between the header ring and the text block |
| size | `STATS_READOUT_GAP_PX` | `12` | Gap between the GAMES/WINS/LOSSES readouts (divider centered in it) |
| size | `STATS_BODY_HEIGHT_PX` | `334` | Fixed height of the top-hero list / state-message region (= 3 × `CARD_HEIGHT_PX` + 2 × `CARD_SPACING_PX`) |
| size | `RANK_BADGE_DIAMETER_PX` | `24` | Diameter of the rank badge on each top-hero row |
| size | `RANK_BADGE_BORDER_WIDTH_PX` | `2` | Border thickness of the rank badge circle |
| size | `STATS_MESSAGE_GAP_PX` | `8` | Gap between a state message's headline and its subtext |
| size | `STATS_STATUS_DOT_DIAMETER_PX` | `8` | Diameter of the footer status dot |
| size | `CONFIG_WINDOW_WIDTH_PX` | `520` | Fixed width of the settings window |
| size | `CONFIG_LIST_MAX_HEIGHT_PX` | `200` | Max height of the teammate list before it scrolls |
| size | `CONFIG_ROW_HEIGHT_PX` | `40` | Height of one teammate list row |
| size | `CONFIG_FIELD_GAP_PX` | `14` | Vertical gap between form field rows (and list ↔ add row) |
| size | `CONFIG_LABEL_GAP_PX` | `6` | Gap between a field label and its control |
| size | `CONFIG_COLUMN_GAP_PX` | `14` | Horizontal gap between the two form columns |
| size | `CONTROL_HEIGHT_PX` | `34` | Shared height of inputs / dropdowns / toggles / buttons |
| size | `CONTROL_CORNER_RADIUS_PX` | `6` | Shared corner radius of form controls |
| size | `CONTROL_PADDING_X_PX` | `10` | Horizontal text inset inside form controls |
| size | `CONTROL_FOCUS_BORDER_WIDTH_PX` | `2` | Border width for focused / invalid controls |
| size | `ICON_BUTTON_SIZE_PX` | `28` | Edit / remove icon-button hit area in a list row |
| size | `BUTTON_PADDING_X_PX` | `16` | Horizontal padding inside text buttons (Save / Cancel / Add) |
| typography | `FONT_FAMILY_PRIMARY` | `"Koverwatch"` | HUD font — free Overwatch-style replica (fallback: "Big Noodle Titling", "Bebas Neue", "Oswald", "Arial Narrow", sans-serif) |
| typography | `FONT_RING_CENTER_SIZE_PT` | `20` | Win-rate number size |
| typography | `FONT_RING_SUFFIX_SIZE_PT` | `11` | Trailing `%` sign size (smaller than the number) |
| typography | `FONT_RING_CENTER_WEIGHT` | `700` | Win-rate number weight (bold) |
| typography | `FONT_RING_CENTER_ITALIC` | `true` | Win-rate number italic (HUD slant) |
| typography | `FONT_HUD_LETTER_SPACING_PCT` | `4` | Letter spacing for the center number (% of em) |
| typography | `FONT_LABEL_NAME_SIZE_PT` | `11` | Player-name label size |
| typography | `FONT_LABEL_NAME_WEIGHT` | `700` | Player-name label weight |
| typography | `FONT_LABEL_SUB_SIZE_PT` | `9` | Most-played-hero label size |
| typography | `FONT_LABEL_SUB_WEIGHT` | `400` | Most-played-hero label weight |
| typography | `FONT_ICON_FALLBACK_SIZE_PT` | `16` | Fallback initial / `?` size in the shield |
| typography | `FONT_ICON_FALLBACK_WEIGHT` | `700` | Weight of the fallback initial / `?` glyph in the hero shield |
| typography | `FONT_PROFILE_NAME_SIZE_PT` | `22` | User BattleTag in the profile header |
| typography | `FONT_PROFILE_NAME_WEIGHT` | `700` | Profile-header name weight |
| typography | `FONT_SECTION_TITLE_SIZE_PT` | `13` | "TOP HEROES" section-title size |
| typography | `FONT_SECTION_TITLE_WEIGHT` | `700` | Section-title weight |
| typography | `FONT_SECTION_TITLE_LETTER_SPACING_PCT` | `10` | Tracking for section titles and stat captions (HUD caps, % of em) |
| typography | `FONT_STAT_VALUE_SIZE_PT` | `18` | Overall stat readout value (games / wins / losses) |
| typography | `FONT_STAT_VALUE_WEIGHT` | `700` | Stat readout value weight |
| typography | `FONT_STAT_CAPTION_SIZE_PT` | `8` | Stat readout caption size |
| typography | `FONT_STAT_CAPTION_WEIGHT` | `400` | Stat readout caption weight |
| typography | `FONT_RANK_SIZE_PT` | `12` | Rank-badge numeral size |
| typography | `FONT_RANK_WEIGHT` | `700` | Rank-badge numeral weight |
| typography | `FONT_STATS_MESSAGE_SIZE_PT` | `15` | State-message headline size (private / network / empty) |
| typography | `FONT_STATS_MESSAGE_WEIGHT` | `700` | State-message headline weight |
| typography | `FONT_INPUT_SIZE_PT` | `11` | Text size in inputs / dropdowns / list rows / hotkey fields |
| typography | `FONT_INPUT_WEIGHT` | `400` | Text weight in inputs / dropdowns / list rows (regular) |
| timing | `RING_FILL_ANIM_MS` | `600` | Duration of the arc sweep animation on data update |
| timing | `RING_FILL_EASING` | `"OutCubic"` | Easing curve for the arc fill |
| timing | `VALUE_TWEEN_MS` | `600` | Duration of the center number counting up to its value |
| timing | `CARD_FADE_IN_MS` | `250` | Overlay/card fade duration (reused for both fade-in and fade-out) |
| timing | `CARD_STAGGER_MS` | `80` | Per-card delay so the column fades in top-down |
| timing | `GLOW_PULSE_PERIOD_MS` | `2400` | Period of the subtle cyan glow pulse |

---

## Implementation handoff (non-negotiables for the code subagent)

- **Tokens are the single source of truth.** Copy every row of the Design Tokens table **verbatim**
  into one `theme` module and reference each value **by name only**. No raw numbers or hex colors
  may appear anywhere in logic or drawing code — only token references.
- **Visibility trigger is yours to choose.** The visible behavior is fixed (shown during hero
  select, hidden after, fading via `CARD_FADE_IN_MS`), but the trigger mechanism is delegated to
  you. **Adopt the recommended default — a manual show/hide global hotkey — and ship it**; a timed
  window or screen detection are acceptable substitutes. No further sign-off needed.
- **Ticks are the committed ring look.** Render the win/loss band as `RING_TICK_COUNT` discrete
  segments (each = 2%). The smooth solid arc is an **emergency-only fallback** if ticks cannot be
  drawn cleanly — do not ship it as the default.
- **The font fallback chain carries the look.** Bundle the `"Koverwatch"` replica only if its
  license permits redistribution; otherwise rely on the fallback chain
  (Bebas Neue → Oswald → Arial Narrow → sans-serif). Either way, never block on the primary font.

---

## Open Questions

1. **Visibility trigger mechanism — delegated to the code subagent (not a design decision).** The
   *behavior* is locked (shown during hero select, hidden after it ends, fading via
   `CARD_FADE_IN_MS`). Because Overwatch has no hero-select API, **how** the show/hide is triggered
   is intentionally left to the code subagent's implementation judgment. **Recommended v1 default:
   a manual show/hide global hotkey** — the code subagent may adopt this and proceed without further
   input. Acceptable alternatives: a **timed window** or **screen detection**. Not blocking.
2. **Anchor corner**: default is **top-left** to match the rough mock and avoid the in-game party
   panel (top-right). Confirm top-left, or expose the corner (TL/TR/BL/BR) as a config setting.
3. **Arc hexes — confirmed**: `COLOR_WIN_ARC = #6FD23A` (warm yellow-green, "Option B") and
   `COLOR_LOSS_ARC = #E53935` (harsh red, "Option D") are the locked values. Listed here only as a
   record; no further design decision needed unless you want to re-tune later.
4. **Card composition — confirmed**: the **wide horizontal card** (icon | ring | label in one row,
   ~`320px` wide, short) is the committed layout. Recorded for traceability; no open decision.
5. **Hero icon shape — confirmed**: the full **shield/badge** silhouette
   (`ICON_TOP_CORNER_RADIUS_PX` + `ICON_BOTTOM_POINT_DEPTH_PX`) is committed; the plain
   rounded-rectangle alternative is dropped.
6. **Arc seam — confirmed**: a `RING_ARC_GAP_DEG = 6` dark seam (the track showing through)
   separates the green and red arcs at each boundary. Confirm the gap width feels right, or nudge
   it.
7. **Win-rate basis — resolved as configurable**: competitive-only vs. quickplay + competitive is
   a **user-configurable** setting. This is behavioral (changes the value only), not a visual
   token; no design impact.
8. **Font — using a free OW replica**: `FONT_FAMILY_PRIMARY = "Koverwatch"`, a free replica of the
   Overwatch typeface (the real UI font is proprietary and cannot be shipped), with a condensed
   fallback chain. Remaining confirm: that we may **bundle/install** the chosen replica and its
   license permits redistribution; otherwise the fallback chain (Bebas Neue → Oswald → Arial
   Narrow → sans-serif) carries the look.
9. **Stats-window frame** (game-closed view): preferred is a **frameless rounded panel**
   (`STATS_WINDOW_CORNER_RADIUS_PX`) with a custom close **✕**; an **OS-standard title bar** is an
   acceptable fallback if frameless adds too much code. Confirm which, or leave it to the code
   subagent like the overlay's visibility trigger. Not blocking.
10. **Header avatar (optional)**: the game-closed header centerpiece is the **overall win-rate ring**
    with no hero shield, to keep "overall" visually distinct from the per-hero list below (and avoid
    duplicating hero #1). If a player avatar / namecard image becomes available later, a small shield
    could be added to the left of the header ring. Not blocking.
11. **Config-screen invocation (Question #2)** — recommended **both**: auto-open on first run / when no
    valid BattleTags exist, plus a global hotkey and a gear affordance in the stats-view header. Confirm,
    or pick a single trigger. The wiring is code; not blocking.
