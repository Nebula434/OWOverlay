# APP_DESIGN.md — Standalone Player-Profile Application (Visual Spec)

> Single source of truth for the **look** of the standalone desktop **application window**
> (`concepts/CONCEPT_STANDALONE_APPLICATION.png`, identical to
> `concepts/overlay_dashboard_v2_tabs_connected.png`). This is the full player-profile
> dashboard — **not** the transparent teammate overlay and **not** the `DESIGN.md`
> game-closed stats view. The code subagent must copy every value in the **Design Tokens**
> table verbatim into the `theme` module and reference tokens **by name only**; no raw
> numbers or hex colors may appear in logic or drawing code.
>
> This spec **reuses** the existing visual language (`DESIGN.md` / `src/overlay/ui/theme.py`)
> wherever the dashboard shares it, and introduces **new** tokens only for genuinely new
> dashboard pieces. Every token row in the table is tagged **reused** or **new**.
>
> **The stat numbers in the screenshot are placeholders** — their values are irrelevant. Every
> *region, label, icon slot, and styling treatment* that produces the look is what this spec
> locks down.

---

## 1. Overview / Vision

This is a dark, cool-toned **Overwatch career-profile dashboard** rendered as a self-contained
desktop window in the unmistakable Overwatch HUD idiom: an angular "tech-panel" frame with
beveled corners and glowing cyan edge lines, a faint hex-mesh backdrop, navy glass panels, and
confident color-coded data. The window is organized as a top **tab bar** over a **three-column
body** (hero picker · the hero's big win-rate ring · stat cards + recent-form chart), capped by
a **six-cell bottom stat bar**. The centerpiece is the **win-rate ring** — the Overwatch
ult-charge ring re-themed into a green **win**-arc and a harsh red **loss**-arc with a big
bold-italic percentage in the hole. The aesthetic goal: it should read at a glance as a screen
lifted straight out of Overwatch's UI, while staying crisp, legible, and fully implementable
from tokens.

---

## 2. Window & Global Layout

### Outer window / frame chrome
- **Size**: fixed `APP_WINDOW_WIDTH_PX` × `APP_WINDOW_HEIGHT_PX` (the design resolution; a clean
  3:2 echoing the concept). Opens centered on the primary screen.
- **Frame**: a **rounded, opaque tech-panel** — corner radius `APP_WINDOW_CORNER_RADIUS_PX`,
  with the top corners additionally **clipped/beveled** by `APP_FRAME_BEVEL_PX` for the angular
  Overwatch silhouette. Fill is `COLOR_STATS_WINDOW_BG` @ `COLOR_STATS_WINDOW_BG_ALPHA` (reused
  opaque deep navy).
- **Frame edge**: a base border `APP_FRAME_BORDER_WIDTH_PX` in `COLOR_CARD_BORDER`, traced on its
  inner side by a **bright cyan hairline** in `COLOR_RING_BEVEL_OUTER`, and surrounded by a soft
  outer **cyan glow** `COLOR_RING_GLOW` @ `COLOR_RING_GLOW_ALPHA`, blur `APP_FRAME_GLOW_BLUR_PX`.
  (Frameless window; the tab bar doubles as the drag region — see Open Questions.)
- **Background field**: inside the frame, the content area behind every panel is
  `COLOR_APP_CONTENT_BG`, overlaid with a **faint hexagon mesh**: regular flat-top hexagons
  `HEX_PATTERN_CELL_PX` across (flat-to-flat), stroked at `CARD_BORDER_WIDTH_PX` in
  `COLOR_HEX_PATTERN_LINE` @ `COLOR_HEX_PATTERN_ALPHA`, tiled edge-to-edge.

### Global structure
- **Inner padding**: `APP_WINDOW_PADDING_PX` on all sides → content box is
  `APP_WINDOW_WIDTH_PX − 2 × APP_WINDOW_PADDING_PX` wide and
  `APP_WINDOW_HEIGHT_PX − 2 × APP_WINDOW_PADDING_PX` tall.
- **Vertical bands** (top → bottom), separated by `APP_BAND_GAP_PX`:
  1. **Tab bar** — `APP_TABBAR_HEIGHT_PX`.
  2. **Main body** — the remaining height (deterministic:
     `content_height − APP_TABBAR_HEIGHT_PX − APP_BOTTOMBAR_HEIGHT_PX − 2 × APP_BAND_GAP_PX`).
  3. **Bottom stat bar** — `APP_BOTTOMBAR_HEIGHT_PX`.
- **Three-column body**, left → right, separated by `APP_COL_GAP_PX`:
  - **Left** `APP_COL_LEFT_WIDTH_PX` — hero picker.
  - **Center** `APP_COL_CENTER_WIDTH_PX` — win-rate ring + W/L pill + role/rank chips.
  - **Right** `APP_COL_RIGHT_WIDTH_PX` — 2×2 stat cards over the recent-performance chart.
  - Widths satisfy `LEFT + CENTER + RIGHT + 2 × APP_COL_GAP_PX = content_width` (center is the
    exact remainder; no magic constant).

---

## 3. Top Tab Bar

- A horizontally **centered group of three connected tabs** sitting in the `APP_TABBAR_HEIGHT_PX`
  band: **PROFILE** (active) · **PLAYER LOOKUP** · **FRIENDS**.
- **Tab shape**: each tab is a **right-leaning parallelogram**, width `TAB_WIDTH_PX`, height
  `TAB_HEIGHT_PX`, side skew `TAB_SKEW_PX` (the angular OW cut). Adjacent tabs are **connected**,
  separated only by a `TAB_SEAM_WIDTH_PX` dark **central seam** in `COLOR_APP_CONTENT_BG`.
- **Active tab (PROFILE)**: fill `COLOR_TAB_ACTIVE_FILL`; a bright **top accent line**
  `TAB_ACCENT_HEIGHT_PX` tall in `COLOR_RING_BEVEL_OUTER`; a cyan **glow** `COLOR_RING_GLOW` @
  `COLOR_RING_GLOW_ALPHA`, blur `TAB_GLOW_BLUR_PX`. Label `COLOR_LABEL_PRIMARY`.
- **Inactive tabs**: fill `COLOR_CARD_BG` @ `COLOR_CARD_BG_ALPHA`, border `CARD_BORDER_WIDTH_PX`
  in `COLOR_CARD_BORDER`, no top accent, no glow. Label `COLOR_LABEL_SECONDARY`.
- **Tab label**: `FONT_SECTION_TITLE_SIZE_PT` / `FONT_SECTION_TITLE_WEIGHT`, italic
  (`FONT_RING_CENTER_ITALIC` slant), tracked by `FONT_SECTION_TITLE_LETTER_SPACING_PCT`,
  centered.
- **FRIENDS count badge**: a filled **circle** `FRIENDS_BADGE_DIAMETER_PX` in `COLOR_CARD_ACCENT`,
  placed at the right end of the FRIENDS label (gap `CARD_ELEMENT_GAP_PX`), with the count numeral
  centered in `FONT_RANK_SIZE_PT` / `FONT_RANK_WEIGHT`, color `COLOR_BUTTON_PRIMARY_TEXT` (dark on
  cyan). (Count is data; the badge slot is always reserved.)

---

## 4. Left Column — Hero Picker

Top → bottom inside `APP_COL_LEFT_WIDTH_PX`: header → search box → hero list.

### Header
- An **OW emblem glyph** `LEFT_EMBLEM_SIZE_PX` square (asset, tinted `COLOR_CARD_ACCENT`) +
  the caps title **"SELECT HERO"**, gap `CARD_ELEMENT_GAP_PX`, on a `LEFT_HEADER_HEIGHT_PX` row.
  Title: `FONT_SECTION_TITLE_SIZE_PT` / `FONT_SECTION_TITLE_WEIGHT`, italic, tracked by
  `FONT_SECTION_TITLE_LETTER_SPACING_PCT`, `COLOR_LABEL_PRIMARY`.

### Search box
- A **recessed input**, full column width, height `CONTROL_HEIGHT_PX`, radius
  `CONTROL_CORNER_RADIUS_PX`, fill `COLOR_RING_TRACK`, border `CARD_BORDER_WIDTH_PX` in
  `COLOR_CARD_BORDER`, text inset `CONTROL_PADDING_X_PX`.
- A **magnifier glyph** `SEARCH_ICON_SIZE_PX` (asset, `COLOR_LABEL_SECONDARY`) at the left inset,
  then placeholder **"SEARCH HEROES"** in `FONT_INPUT_SIZE_PT` / `FONT_INPUT_WEIGHT`,
  `COLOR_LABEL_SECONDARY`.

### Hero list (scrollable)
- A vertical list of **hero rows**, each `HERO_ROW_HEIGHT_PX` tall, separated by
  `HERO_ROW_GAP_PX` (row pitch = `HERO_ROW_HEIGHT_PX + HERO_ROW_GAP_PX`), filling the remaining
  left-column height. The list is clipped to its region so the **last visible row is cut off
  mid-row** to imply scrolling.
- **Row content**, left → right, vertically centered, separated by `CARD_ELEMENT_GAP_PX`:
  1. **Hero portrait** — a **square framed thumbnail** `HERO_LIST_PORTRAIT_SIZE_PX`, corner
     radius `HERO_LIST_PORTRAIT_RADIUS_PX`, portrait scaled to fill and clipped; frame
     `ICON_FRAME_WIDTH_PX` in `COLOR_ICON_FRAME` with inner bevel `COLOR_ICON_FRAME_INNER`.
     Missing-portrait fallback reuses `COLOR_ICON_BG_FALLBACK` + initial/`?` in
     `COLOR_ICON_FALLBACK_TEXT` (`FONT_ICON_FALLBACK_SIZE_PT` / `FONT_ICON_FALLBACK_WEIGHT`).
  2. **Text block**, stacked:
     - **Hero name** (e.g. "ZARYA") — `FONT_HERO_NAME_SIZE_PT` / `FONT_LABEL_NAME_WEIGHT`,
       italic, `COLOR_LABEL_PRIMARY`, elided.
     - **"LEVEL ##"** — `FONT_LABEL_SUB_SIZE_PT` / `FONT_LABEL_SUB_WEIGHT`, tracked by
       `FONT_SECTION_TITLE_LETTER_SPACING_PCT`, `COLOR_CARD_ACCENT` (cyan).
- **Row states**:
  - **Default**: transparent over the hex field (no panel).
  - **Hover**: fill `COLOR_CARD_ACCENT` @ `COLOR_ROW_HOVER_ALPHA`, radius `CARD_CORNER_RADIUS_PX`.
  - **Selected** (e.g. ZARYA): a navy panel `COLOR_CARD_BG` @ `COLOR_CARD_BG_ALPHA`, radius
    `CARD_CORNER_RADIUS_PX`, **cyan border** `CONTROL_FOCUS_BORDER_WIDTH_PX` in
    `COLOR_CARD_ACCENT` with the ring/frame cyan **glow** (`COLOR_RING_GLOW` @
    `COLOR_RING_GLOW_ALPHA`), and a **left-edge arrow indicator** — a right-pointing triangle
    `HERO_ROW_SEL_ARROW_W_PX` × `HERO_ROW_SEL_ARROW_H_PX` in `COLOR_CARD_ACCENT`, sitting in the
    left padding gutter, vertically centered on the row.
- **Scrollbar**: a thin track at the column's right edge, `SCROLLBAR_WIDTH_PX` wide; the thumb is
  `COLOR_CARD_ACCENT` (radius = half its width), the track `COLOR_RING_TRACK`.

---

## 5. Center Column — Win-Rate Ring, W/L Pill, Role/Rank Chips

Vertically arranged, horizontally centered in `APP_COL_CENTER_WIDTH_PX`, stacked top → bottom and
separated by `CENTER_STACK_GAP_PX`:

1. **Win-rate ring** — the large ring, `APP_RING_DIAMETER_PX` (see §9). Center shows the win-rate
   number + "WIN RATE" caption.
2. **W/L pill** — a rounded **pill** (radius = half its height) of height `WL_PILL_HEIGHT_PX`,
   horizontal padding `WL_PILL_PADDING_X_PX`, fill `COLOR_RING_TRACK`, border
   `CARD_BORDER_WIDTH_PX` in `COLOR_CARD_BORDER`. Content (centered, single line,
   `FONT_HERO_NAME_SIZE_PT` / `FONT_LABEL_NAME_WEIGHT`, italic): the wins value + "W" in
   `COLOR_WIN_ARC`, a separator "/" in `COLOR_LABEL_SECONDARY`, the losses value + "L" in
   `COLOR_LOSS_ARC`.
3. **Role + rank chip row** — two chips side by side, gap `CARD_ELEMENT_GAP_PX`, each height
   `CHIP_HEIGHT_PX`, radius `CARD_CORNER_RADIUS_PX`, fill `COLOR_CARD_BG` @ `COLOR_CARD_BG_ALPHA`,
   border `CARD_BORDER_WIDTH_PX` in `COLOR_CARD_BORDER`, with the left cyan accent bar
   `CARD_ACCENT_WIDTH_PX` in `COLOR_CARD_ACCENT` and inner padding `CARD_PADDING_PX`. Each chip =
   an **icon** `CHIP_ICON_SIZE_PX` (asset) + a label (gap `CARD_ELEMENT_GAP_PX`),
   `FONT_SECTION_TITLE_SIZE_PT` / `FONT_SECTION_TITLE_WEIGHT`, italic, tracked by
   `FONT_SECTION_TITLE_LETTER_SPACING_PCT`, `COLOR_LABEL_PRIMARY`:
   - **Role chip** — role icon + role name (e.g. "TANK").
   - **Rank chip** — competitive rank emblem + tier/division (e.g. "DIAMOND 2").

---

## 6. Right Column (Top) — 2×2 Stat Cards

A **2×2 grid** of stat cards filling the right column width, gap `STATCARD_GAP_PX` between
columns and rows. Each card: width = `(APP_COL_RIGHT_WIDTH_PX − STATCARD_GAP_PX) / 2`, height
`STATCARD_HEIGHT_PX`; panel `COLOR_CARD_BG` @ `COLOR_CARD_BG_ALPHA`, radius
`CARD_CORNER_RADIUS_PX`, border `CARD_BORDER_WIDTH_PX` in `COLOR_CARD_BORDER`, inner padding
`CARD_PADDING_PX`.

**Shared card structure**: a **header row** (a `STAT_ICON_SIZE_PX` icon, tinted
`COLOR_CARD_ACCENT`, + a caps **title**, gap `STATCARD_HEADER_GAP_PX`, title
`FONT_SECTION_TITLE_SIZE_PT` / `FONT_SECTION_TITLE_WEIGHT`, tracked, `COLOR_LABEL_PRIMARY`) above
a **value/body** and a **caption** (`FONT_STAT_CAPTION_SIZE_PT` / `FONT_STAT_CAPTION_WEIGHT`,
tracked, `COLOR_LABEL_SECONDARY`).

- **KDA** (top-left): crossed-swords icon; value row `FONT_STATCARD_VALUE_SIZE_PT` /
  `FONT_STAT_VALUE_WEIGHT`, italic — the kills & assists values in `COLOR_CENTER_TEXT`, the
  **middle deaths value in `COLOR_LOSS_ARC`**, slashes in `COLOR_LABEL_SECONDARY`; caption
  "AVG PER 10 MIN".
- **TOTAL MATCHES** (top-right): bar-chart icon; value `FONT_STATCARD_VALUE_SIZE_PT` /
  `FONT_STAT_VALUE_WEIGHT`, italic, `COLOR_CENTER_TEXT`; caption "ALL MODES".
- **HOURS PLAYED** (bottom-left): clock icon; value (e.g. "86h") same treatment; caption
  "ALL MODES".
- **HERO LEVEL** (bottom-right): a **gold hexagon badge** + an **XP progress bar**:
  - **Hex badge** — a regular hexagon `HEX_BADGE_SIZE_PX` (point-to-point), face fill
    `COLOR_HERO_LEVEL_GOLD`, beveled edge `HEX_BADGE_BORDER_WIDTH_PX` in
    `COLOR_HERO_LEVEL_GOLD_DARK`; level numeral centered in `FONT_STATCARD_VALUE_SIZE_PT` /
    `FONT_STAT_VALUE_WEIGHT`, italic, `COLOR_BUTTON_PRIMARY_TEXT` (dark on gold).
  - **XP bar** (below the title, right of / under the badge) — a track height `XP_BAR_HEIGHT_PX`
    (radius = half height) in `COLOR_RING_TRACK`, filled left-to-right in `COLOR_HERO_LEVEL_GOLD`
    by the XP fraction. Caption "#,### / ##,### XP": the earned value in `COLOR_HERO_LEVEL_GOLD`,
    the "/ total XP" remainder in `COLOR_LABEL_SECONDARY`, `FONT_LABEL_SUB_SIZE_PT` /
    `FONT_LABEL_SUB_WEIGHT`.

---

## 7. Right Column (Bottom) — Recent-Performance Chart

- A **panel** filling the right column, height `RECENTPERF_HEIGHT_PX` (= right-body height −
  2-row grid − `APP_BAND_GAP_PX`; deterministic), styled like the stat cards (`COLOR_CARD_BG` @
  `COLOR_CARD_BG_ALPHA`, `CARD_CORNER_RADIUS_PX`, `CARD_BORDER_WIDTH_PX` border in
  `COLOR_CARD_BORDER`, padding `CARD_PADDING_PX`).
- **Header row** `RECENTPERF_HEADER_HEIGHT_PX`: title **"RECENT PERFORMANCE"**
  (`FONT_SECTION_TITLE_SIZE_PT` / `FONT_SECTION_TITLE_WEIGHT`, tracked, `COLOR_LABEL_PRIMARY`) on
  the left; **"LAST 20 GAMES"** caption (`FONT_STAT_CAPTION_SIZE_PT` /
  `FONT_STAT_CAPTION_WEIGHT`, tracked, `COLOR_LABEL_SECONDARY`) right-aligned. (Game count is
  data.)
- **Plot area** height `CHART_PLOT_HEIGHT_PX`, with a left **y-axis gutter** `CHART_YAXIS_WIDTH_PX`
  holding **0% / 50% / 100%** labels (`FONT_STAT_CAPTION_SIZE_PT` / `FONT_STAT_CAPTION_WEIGHT`,
  `COLOR_LABEL_SECONDARY`). Three horizontal **gridlines** at 0/50/100% span the plot at
  `CARD_BORDER_WIDTH_PX` in `COLOR_CARD_BORDER`.
- **Bars**: one vertical bar per recent game, width `CHART_BAR_WIDTH_PX`, gap `CHART_BAR_GAP_PX`,
  height = that game's value mapped to the 0–100% scale, bottom-aligned to the 0% line, top
  corners squared. **Win bars** fill `COLOR_CHART_WIN_BAR` (azure); **loss bars** fill
  `COLOR_LOSS_ARC` (red).
- **W/L letter row** `CHART_WL_ROW_HEIGHT_PX` beneath the plot, one letter centered under each
  bar: **"W"** in `COLOR_CHART_WIN_BAR`, **"L"** in `COLOR_LOSS_ARC`,
  `FONT_STAT_CAPTION_SIZE_PT` / `FONT_RING_CENTER_WEIGHT` (bold).

---

## 8. Bottom Stat Bar

- A full-width band `APP_BOTTOMBAR_HEIGHT_PX` tall, divided into **six equal cells**:
  **ELIMINATIONS · DAMAGE DONE · DAMAGE BLOCKED · OBJECTIVE TIME · OBJECTIVE KILLS · DEATHS**.
- Cells are separated by thin **vertical dividers** `CARD_BORDER_WIDTH_PX` in `COLOR_CARD_BORDER`,
  inset `BOTTOM_STAT_DIVIDER_INSET_PX` from the band's top and bottom (the dividers don't reach
  the edges).
- **Each cell**, left → right: a stat **icon** `BOTTOM_STAT_ICON_SIZE_PX` (asset, tinted
  `COLOR_CARD_ACCENT`) + a stacked text block (gap `CARD_ELEMENT_GAP_PX`):
  - **Label** (caps, e.g. "ELIMINATIONS") — `FONT_STAT_CAPTION_SIZE_PT` /
    `FONT_STAT_CAPTION_WEIGHT`, tracked by `FONT_SECTION_TITLE_LETTER_SPACING_PCT`,
    `COLOR_LABEL_SECONDARY`.
  - **Value** (e.g. "4,812") — `FONT_BOTTOMSTAT_VALUE_SIZE_PT` / `FONT_STAT_VALUE_WEIGHT`,
    italic, `COLOR_CENTER_TEXT`.
  - **Caption** "AVG ## / 10 MIN" — `FONT_STAT_CAPTION_SIZE_PT` / `FONT_STAT_CAPTION_WEIGHT`,
    `COLOR_LABEL_SECONDARY`.

---

## 9. Win-Rate Ring (as applied here)

The dashboard ring is the **`DESIGN.md` Win-Rate Ring**, **scaled up** to
`APP_RING_DIAMETER_PX`. It **reuses** that ring's character and tokens unchanged except for the
diameter, band thickness, and sweep direction noted below:

- **Geometry**: outer diameter `APP_RING_DIAMETER_PX`; band wall thickness `APP_RING_THICKNESS_PX`
  (proportionally the same thin-ish band as the overlay ring, just larger). Full circle
  `RING_FULL_SWEEP_DEG`, arcs start at 12 o'clock (`RING_START_ANGLE_DEG`).
- **Track + rim + glow (reused)**: dark recessed track `COLOR_RING_TRACK` (inset
  `RING_TRACK_INSET_PX`); beveled double rim `COLOR_RING_BEVEL_OUTER` /
  `COLOR_RING_BEVEL_INNER`; cyan accent hairline `COLOR_RING_ACCENT_CYAN`; outer glow
  `COLOR_RING_GLOW` @ `COLOR_RING_GLOW_ALPHA` (blur `RING_GLOW_BLUR_PX`, spread
  `RING_GLOW_SPREAD_PX`).
- **Arcs**: **win = `COLOR_WIN_ARC`** (green), **loss = `COLOR_LOSS_ARC`** (red), each with its
  same-color emissive glow at `COLOR_ARC_GLOW_ALPHA`. A dark **seam** of `RING_ARC_GAP_DEG` (the
  track showing through) sits at each green↔red boundary.
- **Direction (dashboard-specific)**: to match the concept (**green fills the left/upper-left,
  red the right**), the **win arc sweeps `APP_RING_WIN_SWEEP_DIRECTION` (counter-clockwise)** from
  the top; the loss arc takes the remainder clockwise from the top. This is the mirror of the
  overlay's clockwise win arc — see Open Questions.
- **Rendering**: at this large scale the band reads as **solid arcs** (matching the screenshot),
  not the overlay's tiny ticks. (`RING_TICK_*` are not applied here — see Open Questions.)
- **Center text**: the win-rate number in `FONT_APP_RING_CENTER_SIZE_PT` with the trailing "%" at
  `FONT_APP_RING_SUFFIX_SIZE_PT`, weight `FONT_RING_CENTER_WEIGHT`, italic
  (`FONT_RING_CENTER_ITALIC`), tracked `FONT_HUD_LETTER_SPACING_PCT`, color `COLOR_CENTER_TEXT`
  over a `CENTER_TEXT_SHADOW_OFFSET_PX` drop shadow (`COLOR_CENTER_TEXT_SHADOW` @
  `COLOR_CENTER_TEXT_SHADOW_ALPHA`). Below it, the **"WIN RATE"** caption:
  `FONT_SECTION_TITLE_SIZE_PT` / `FONT_SECTION_TITLE_WEIGHT`, tracked, `COLOR_WIN_ARC` (green).
- **No-data state (reused)**: dash in the center, no colored arcs — only track + rim show.

---

## 10. Asset Manifest (use real Overwatch assets)

The user requires **real Overwatch assets** wherever possible rather than custom glyphs. Per
Absolute Rule 1 the design subagent does **not** create assets; the **code subagent fetches and
places** them. Each iconographic slot below maps to a real OW asset, its likely source, and its
on-screen size token. Where no official asset exists, the code subagent should source the closest
official OW career-UI icon and only fall back to a neutral monochrome glyph if none is available
(flag it rather than invent a stylized custom icon).

| Element | Real OW asset to use | Likely source | Size token |
|---|---|---|---|
| Hero portraits (left list; future icons) | Per-hero portrait images | OverFast API `/heroes` portraits, cached under `assets/heroes/` (`mei.png`, `mercy.png`, `zarya.png` already exist) | `HERO_LIST_PORTRAIT_SIZE_PX` |
| Role icon — **Tank** (+ Damage / Support variants) | Official OW role icons | OverFast API roles / Blizzard role-icon CDN | `CHIP_ICON_SIZE_PX` |
| Competitive rank emblem — **Diamond 2** (+ all tiers Bronze→Champion and divisions 1–5) | Official competitive rank-tier icons | OverFast API competitive rank icons / Blizzard CDN | `CHIP_ICON_SIZE_PX` |
| KDA icon (crossed swords) | OW combat/elimination iconography | OW career-profile UI icon set | `STAT_ICON_SIZE_PX` |
| Total matches (bar chart) | OW games-played / matches icon | OW career-profile UI icon set | `STAT_ICON_SIZE_PX` |
| Hours played (clock) | OW time-played icon | OW career-profile UI icon set | `STAT_ICON_SIZE_PX` |
| Hero level (gold hexagon) | OW endorsement/level hex frame art (gold) | OW UI hex/level art | `HEX_BADGE_SIZE_PX` |
| Eliminations | OW "eliminations" stat icon (reticle) | OW career-profile stat icons | `BOTTOM_STAT_ICON_SIZE_PX` |
| Damage done | OW "damage" stat icon | OW career-profile stat icons | `BOTTOM_STAT_ICON_SIZE_PX` |
| Damage blocked | OW "damage blocked / mitigated" stat icon | OW career-profile stat icons | `BOTTOM_STAT_ICON_SIZE_PX` |
| Objective time | OW "objective time" stat icon | OW career-profile stat icons | `BOTTOM_STAT_ICON_SIZE_PX` |
| Objective kills | OW "objective kills" stat icon (flag) | OW career-profile stat icons | `BOTTOM_STAT_ICON_SIZE_PX` |
| Deaths | OW "deaths" stat icon (skull) | OW career-profile stat icons | `BOTTOM_STAT_ICON_SIZE_PX` |
| "SELECT HERO" emblem | Overwatch logo / hero-select emblem glyph | Official OW logo mark | `LEFT_EMBLEM_SIZE_PX` |
| Search glyph | Standard magnifier (neutral, tinted to theme) | Generic UI icon, tinted `COLOR_LABEL_SECONDARY` | `SEARCH_ICON_SIZE_PX` |

> All icon assets are tinted/placed by code; this spec only fixes **which** asset and at **what
> size**. Cyan-tinted stat/role icons use `COLOR_CARD_ACCENT`; the hex badge keeps its native gold.

---

## 11. Design Tokens

> **Conventions:** Colors are 6-digit `#RRGGBB`; transparency is a separate `*_ALPHA` token
> (0–255). Sizes are device-independent px; type sizes are points (`pt`); durations are ms;
> angles in degrees. **Source** = `reused` (already in `DESIGN.md` / `theme.py`, copy by name) or
> `new` (add to `theme.py`). Only tokens actually used by this screen are listed.

### color

| Token | Value | Controls | Source |
|---|---|---|---|
| `COLOR_STATS_WINDOW_BG` | `#080D17` | Window frame fill (opaque) | reused |
| `COLOR_STATS_WINDOW_BG_ALPHA` | `255` | Window frame fill opacity | reused |
| `COLOR_APP_CONTENT_BG` | `#07161E` | Content field behind panels (holds the hex mesh); tab seam | new |
| `COLOR_HEX_PATTERN_LINE` | `#15333D` | Hexagon mesh stroke on the content field | new |
| `COLOR_HEX_PATTERN_ALPHA` | `55` | Hex mesh stroke opacity | new |
| `COLOR_CARD_BG` | `#0E1626` | All panels: cards, chart, chips, selected row, inactive tabs | reused |
| `COLOR_CARD_BG_ALPHA` | `200` | Panel fill opacity | reused |
| `COLOR_CARD_BORDER` | `#2A3A5C` | Panel/frame borders, dividers, gridlines | reused |
| `COLOR_CARD_BORDER_ALPHA` | `230` | Border opacity | reused |
| `COLOR_CARD_ACCENT` | `#4DD2E6` | Cyan accents: bars, icon tint, selected row, friends badge, scrollbar, "LEVEL ##" | reused |
| `COLOR_TAB_ACTIVE_FILL` | `#1A9BD5` | Active tab (PROFILE) body fill | new |
| `COLOR_RING_TRACK` | `#0B1220` | Ring track, search box, W/L pill, XP bar track | reused |
| `COLOR_RING_BEVEL_OUTER` | `#5FD8EC` | Bright cyan edge: frame hairline, active-tab top line, ring outer rim | reused |
| `COLOR_RING_BEVEL_INNER` | `#1C5C73` | Ring/icon inner bevel | reused |
| `COLOR_RING_ACCENT_CYAN` | `#4DD2E6` | Ring cyan accent hairline | reused |
| `COLOR_RING_GLOW` | `#36C8E0` | Cyan glow: frame, active tab, ring, selected row | reused |
| `COLOR_RING_GLOW_ALPHA` | `130` | Cyan glow opacity | reused |
| `COLOR_WIN_ARC` | `#6FD23A` | Win ring arc, "WIN RATE" caption, wins "##W" | reused |
| `COLOR_LOSS_ARC` | `#E53935` | Loss ring arc, losses "##L", KDA deaths value, chart loss bars + "L" | reused |
| `COLOR_ARC_GLOW_ALPHA` | `110` | Per-arc emissive glow opacity | reused |
| `COLOR_CHART_WIN_BAR` | `#15ACF3` | Recent-performance win bars + "W" letters | new |
| `COLOR_CENTER_TEXT` | `#F0F4F8` | Ring number; big stat/card/bottom values | reused |
| `COLOR_CENTER_TEXT_SHADOW` | `#06090F` | Ring-number drop shadow | reused |
| `COLOR_CENTER_TEXT_SHADOW_ALPHA` | `170` | Ring-number shadow opacity | reused |
| `COLOR_LABEL_PRIMARY` | `#FFFFFF` | Titles, hero names, active tab, chip labels | reused |
| `COLOR_LABEL_SECONDARY` | `#9FB2CC` | Captions, inactive tabs, placeholders, "/ XP" remainder, axis labels | reused |
| `COLOR_ICON_FRAME` | `#4DD2E6` | Hero-portrait frame | reused |
| `COLOR_ICON_FRAME_INNER` | `#1C5C73` | Hero-portrait inner bevel | reused |
| `COLOR_ICON_FRAME_GLOW` | `#36C8E0` | Hero-portrait frame glow | reused |
| `COLOR_ICON_FRAME_GLOW_ALPHA` | `120` | Portrait frame glow opacity | reused |
| `COLOR_ICON_BG_FALLBACK` | `#1A2740` | Missing-portrait fill | reused |
| `COLOR_ICON_FALLBACK_TEXT` | `#C8D6EC` | Missing-portrait initial/`?` | reused |
| `COLOR_BUTTON_PRIMARY_TEXT` | `#06121A` | Dark numeral on cyan friends badge & on gold hex badge | reused |
| `COLOR_ROW_HOVER_ALPHA` | `30` | Hero-row hover fill opacity (on `COLOR_CARD_ACCENT`) | reused |
| `COLOR_HERO_LEVEL_GOLD` | `#F0B441` | Hex badge face, XP bar fill, earned-XP value | new |
| `COLOR_HERO_LEVEL_GOLD_DARK` | `#A66A18` | Hex badge beveled edge / shade | new |

### size

| Token | Value | Controls | Source |
|---|---|---|---|
| `APP_WINDOW_WIDTH_PX` | `1200` | Window width (design resolution) | new |
| `APP_WINDOW_HEIGHT_PX` | `800` | Window height (3:2) | new |
| `APP_WINDOW_CORNER_RADIUS_PX` | `18` | Outer frame corner radius | new |
| `APP_FRAME_BORDER_WIDTH_PX` | `2` | Outer frame base border width | new |
| `APP_FRAME_BEVEL_PX` | `22` | Angular clip on the frame's top corners | new |
| `APP_FRAME_GLOW_BLUR_PX` | `16` | Outer frame cyan-glow blur | new |
| `APP_WINDOW_PADDING_PX` | `16` | Inner padding (frame → content) | new |
| `APP_BAND_GAP_PX` | `12` | Gap between tab bar / body / bottom bar | new |
| `APP_TABBAR_HEIGHT_PX` | `52` | Top tab-bar band height | new |
| `APP_BOTTOMBAR_HEIGHT_PX` | `100` | Bottom stat-bar band height | new |
| `APP_COL_GAP_PX` | `16` | Gap between the three body columns | new |
| `APP_COL_LEFT_WIDTH_PX` | `280` | Left (hero-picker) column width | new |
| `APP_COL_CENTER_WIDTH_PX` | `346` | Center column width (= content − left − right − 2 gaps) | new |
| `APP_COL_RIGHT_WIDTH_PX` | `510` | Right column width | new |
| `HEX_PATTERN_CELL_PX` | `28` | Hexagon size (flat-to-flat) in the background mesh | new |
| `TAB_WIDTH_PX` | `230` | Width of each tab | new |
| `TAB_HEIGHT_PX` | `44` | Tab height | new |
| `TAB_SKEW_PX` | `18` | Parallelogram side skew of each tab | new |
| `TAB_SEAM_WIDTH_PX` | `2` | Dark seam between connected tabs | new |
| `TAB_ACCENT_HEIGHT_PX` | `3` | Bright top accent line on the active tab | new |
| `TAB_GLOW_BLUR_PX` | `12` | Active-tab cyan-glow blur | new |
| `FRIENDS_BADGE_DIAMETER_PX` | `22` | Circular count badge on FRIENDS | new |
| `LEFT_HEADER_HEIGHT_PX` | `30` | "SELECT HERO" header row height | new |
| `LEFT_EMBLEM_SIZE_PX` | `22` | OW emblem glyph in the header | new |
| `SEARCH_ICON_SIZE_PX` | `14` | Magnifier glyph in the search box | new |
| `HERO_ROW_HEIGHT_PX` | `72` | Height of one hero-list row | new |
| `HERO_ROW_GAP_PX` | `8` | Gap between hero-list rows | new |
| `HERO_LIST_PORTRAIT_SIZE_PX` | `56` | Square hero thumbnail in a list row | new |
| `HERO_LIST_PORTRAIT_RADIUS_PX` | `6` | Hero-thumbnail corner radius | new |
| `HERO_ROW_SEL_ARROW_W_PX` | `12` | Selected-row arrow indicator width | new |
| `HERO_ROW_SEL_ARROW_H_PX` | `18` | Selected-row arrow indicator height | new |
| `SCROLLBAR_WIDTH_PX` | `6` | Hero-list scrollbar width (thumb radius = half) | new |
| `APP_RING_DIAMETER_PX` | `300` | Outer diameter of the large dashboard win-rate ring | new |
| `APP_RING_THICKNESS_PX` | `26` | Band wall thickness of the dashboard ring | new |
| `APP_RING_WIN_SWEEP_DIRECTION` | `"counterclockwise"` | Win-arc growth direction (green on the left) | new |
| `CENTER_STACK_GAP_PX` | `16` | Vertical gap: ring ↔ W/L pill ↔ chip row | new |
| `WL_PILL_HEIGHT_PX` | `34` | W/L pill height (radius = half) | new |
| `WL_PILL_PADDING_X_PX` | `18` | W/L pill horizontal padding | new |
| `CHIP_HEIGHT_PX` | `44` | Role / rank chip height | new |
| `CHIP_ICON_SIZE_PX` | `26` | Role icon & rank emblem size | new |
| `STATCARD_GAP_PX` | `14` | Gap between the 2×2 stat cards | new |
| `STATCARD_HEIGHT_PX` | `140` | Height of one stat card (card width = (right − gap)/2) | new |
| `STAT_ICON_SIZE_PX` | `26` | Stat-card header icon | new |
| `STATCARD_HEADER_GAP_PX` | `8` | Gap between a card's header icon and title | new |
| `HEX_BADGE_SIZE_PX` | `64` | Gold hero-level hexagon (point-to-point) | new |
| `HEX_BADGE_BORDER_WIDTH_PX` | `3` | Hex-badge beveled edge width | new |
| `XP_BAR_HEIGHT_PX` | `10` | Hero-level XP progress bar height (radius = half) | new |
| `RECENTPERF_HEIGHT_PX` | `286` | Recent-performance panel height (= right body − grid − band gap) | new |
| `RECENTPERF_HEADER_HEIGHT_PX` | `24` | Chart header row height | new |
| `CHART_PLOT_HEIGHT_PX` | `180` | Bar plot area height | new |
| `CHART_YAXIS_WIDTH_PX` | `34` | Left gutter for 0/50/100% labels | new |
| `CHART_BAR_WIDTH_PX` | `10` | Width of one performance bar | new |
| `CHART_BAR_GAP_PX` | `10` | Gap between performance bars | new |
| `CHART_WL_ROW_HEIGHT_PX` | `20` | W/L letter row beneath the plot | new |
| `BOTTOM_STAT_ICON_SIZE_PX` | `28` | Icon in each bottom stat cell | new |
| `BOTTOM_STAT_DIVIDER_INSET_PX` | `18` | Top/bottom inset of the bottom-bar dividers | new |
| `CARD_CORNER_RADIUS_PX` | `10` | Panel/chip/row corner radius | reused |
| `CARD_BORDER_WIDTH_PX` | `1` | Borders, dividers, gridlines | reused |
| `CARD_ACCENT_WIDTH_PX` | `3` | Left cyan accent bar on chips | reused |
| `CARD_PADDING_PX` | `12` | Inner padding of panels/cards/chips | reused |
| `CARD_ELEMENT_GAP_PX` | `10` | Generic gap between adjacent row elements | reused |
| `CONTROL_HEIGHT_PX` | `34` | Search-box height | reused |
| `CONTROL_CORNER_RADIUS_PX` | `6` | Search-box corner radius | reused |
| `CONTROL_PADDING_X_PX` | `10` | Search-box text inset | reused |
| `CONTROL_FOCUS_BORDER_WIDTH_PX` | `2` | Selected hero-row border width | reused |
| `ICON_FRAME_WIDTH_PX` | `3` | Hero-thumbnail frame width | reused |
| `RING_TRACK_INSET_PX` | `1` | Ring track inset | reused |
| `RING_GLOW_BLUR_PX` | `8` | Ring glow blur | reused |
| `RING_GLOW_SPREAD_PX` | `2` | Ring glow spread | reused |
| `RING_FULL_SWEEP_DEG` | `360` | Full-circle degrees | reused |
| `RING_START_ANGLE_DEG` | `90` | Arc start at 12 o'clock | reused |
| `RING_ARC_GAP_DEG` | `6` | Dark seam at each win/loss boundary | reused |
| `CENTER_TEXT_SHADOW_OFFSET_PX` | `1` | Ring-number shadow offset | reused |

### typography

| Token | Value | Controls | Source |
|---|---|---|---|
| `FONT_FAMILY_PRIMARY` | `"Koverwatch"` | HUD font (fallback chain: Big Noodle Titling → Bebas Neue → Oswald → Arial Narrow → sans-serif) | reused |
| `FONT_APP_RING_CENTER_SIZE_PT` | `64` | Big win-rate number in the ring | new |
| `FONT_APP_RING_SUFFIX_SIZE_PT` | `34` | Trailing "%" in the ring | new |
| `FONT_STATCARD_VALUE_SIZE_PT` | `26` | 2×2 card values, hex-badge level, KDA values | new |
| `FONT_BOTTOMSTAT_VALUE_SIZE_PT` | `20` | Bottom stat-bar values | new |
| `FONT_HERO_NAME_SIZE_PT` | `14` | Hero name in a list row; W/L pill text | new |
| `FONT_RING_CENTER_WEIGHT` | `700` | Ring number / bold display weight | reused |
| `FONT_RING_CENTER_ITALIC` | `true` | Shared HUD italic slant (ring, tabs, names, values, chips) | reused |
| `FONT_HUD_LETTER_SPACING_PCT` | `4` | Ring-number tracking | reused |
| `FONT_SECTION_TITLE_SIZE_PT` | `13` | Tabs, section/card/chip titles, "WIN RATE" caption | reused |
| `FONT_SECTION_TITLE_WEIGHT` | `700` | Section/title weight | reused |
| `FONT_SECTION_TITLE_LETTER_SPACING_PCT` | `10` | Caps tracking for titles/labels/captions | reused |
| `FONT_STAT_VALUE_WEIGHT` | `700` | Big-value weight (cards, bottom bar, hex badge) | reused |
| `FONT_STAT_CAPTION_SIZE_PT` | `8` | Captions, axis labels, W/L letters | reused |
| `FONT_STAT_CAPTION_WEIGHT` | `400` | Caption weight | reused |
| `FONT_LABEL_NAME_WEIGHT` | `700` | Hero-name / pill weight | reused |
| `FONT_LABEL_SUB_SIZE_PT` | `9` | "LEVEL ##", XP caption | reused |
| `FONT_LABEL_SUB_WEIGHT` | `400` | Sub-label weight | reused |
| `FONT_INPUT_SIZE_PT` | `11` | Search placeholder text | reused |
| `FONT_INPUT_WEIGHT` | `400` | Search text weight | reused |
| `FONT_ICON_FALLBACK_SIZE_PT` | `16` | Missing-portrait initial/`?` size | reused |
| `FONT_ICON_FALLBACK_WEIGHT` | `700` | Missing-portrait initial/`?` weight | reused |
| `FONT_RANK_SIZE_PT` | `12` | FRIENDS badge numeral size | reused |
| `FONT_RANK_WEIGHT` | `700` | FRIENDS badge numeral weight | reused |

### timing

| Token | Value | Controls | Source |
|---|---|---|---|
| `RING_FILL_ANIM_MS` | `600` | Ring arc fill on data load/change | reused |
| `RING_FILL_EASING` | `"OutCubic"` | Ring arc easing (also chart-bar grow) | reused |
| `VALUE_TWEEN_MS` | `600` | Numbers counting up to their value | reused |
| `CARD_FADE_IN_MS` | `250` | Window/tab/selection cross-fades | reused |
| `CARD_STAGGER_MS` | `80` | Stagger for hero rows / stat cards / chart bars | reused |
| `GLOW_PULSE_PERIOD_MS` | `2400` | Idle cyan-glow breathing (frame, active tab, ring) | reused |

---

## 12. Open Questions

1. **Window size / resizability.** The spec fixes a `1200 × 800` (3:2) design resolution matching
   the concept's proportions. Confirm a **fixed-size** window, or should it be resizable/scalable
   (which would require min-size + scaling rules)?
2. **Ring rendering — solid vs ticks.** This dashboard ring is specced as **solid arcs** to match
   the screenshot, whereas the overlay ring (`DESIGN.md`) uses segmented `RING_TICK_*` ticks.
   Confirm solid here, or apply the tick treatment scaled up for consistency with the overlay.
3. **Ring win-arc direction.** To match the concept (green on the left), the dashboard win arc
   sweeps **counter-clockwise** (`APP_RING_WIN_SWEEP_DIRECTION`), the mirror of the overlay's
   clockwise win arc. Confirm the mismatch is intentional, or unify both surfaces to one
   direction.
4. **Real-asset availability.** Hero portraits and role/rank emblems have clear OW/OverFast
   sources, but several **career stat icons** (damage blocked, objective time/kills, etc.) and the
   gold **hero-level hex** may have no cleanly redistributable official asset. Confirm the
   sourcing path / licensing, and the fallback when an official icon can't be obtained.
5. **Tab functionality scope.** PLAYER LOOKUP and FRIENDS tabs (and the FRIENDS "5" badge) are
   drawn but their **screens are out of scope** for this spec (PROFILE only). Confirm that's
   expected for now.
6. **Window chrome.** Preferred is a **frameless** tech-panel with the tab bar as the drag region
   (no OS title bar / no custom min–max–close shown in the concept). Confirm frameless, or add a
   standard title bar / window controls.
