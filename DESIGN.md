# DESIGN.md — Overwatch Teammate Win-Rate Overlay (Visual Spec)

> Single source of truth for the **look** of the overlay. The code subagent must copy the
> values in the **Design Tokens** table verbatim into a `theme` module and reference them by
> name. No raw numbers/colors may appear in logic — only token references.

---

## Vision

A quiet, always-on-top HUD column that floats at the edge of the screen and shows, per tracked
teammate, *who they play* and *how often they win*, in the visual language of the Overwatch
ultimate-charge ring. Each teammate is one self-contained **card**: a framed shield-style hero
portrait paired immediately with a circular win-rate "ult ring," and a small name / most-played
-hero label beneath. The ult ring is re-themed into a **full donut** whose circumference is
split into a **vivid green win arc** and a **harsh red loss arc** (green% + red% = 100%), with
the win-rate number sitting bold and italic in the center. We keep the source HUD's character —
a dark recessed track, a beveled double rim, a cyan accent, a soft glow, and the segmented-tick
treatment on the filled arc — so it reads instantly as "Overwatch," while the green/red split
communicates performance at a glance. The aesthetic is dark, cool-toned, and crisp: navy
panels, cyan edges, confident color-coded arcs.

---

## Layout

- **Window**: a single transparent, frameless, always-on-top, click-through overlay window with
  no taskbar presence. The window background is fully transparent (`COLOR_OVERLAY_BG` at
  `COLOR_OVERLAY_BG_ALPHA = 0`); only the cards paint pixels.
- **Anchor**: pinned to the **top-left** screen corner by default, offset inward by
  `OVERLAY_MARGIN_X_PX` (from the left edge) and `OVERLAY_MARGIN_Y_PX` (from the top, clearing
  the game's top nav bar). Top-left matches the rough placement mock and avoids the in-game
  party panel that sits top-right. (Corner is a single configurable choice — see Open Questions.)
- **Card stacking**: cards form a **single vertical column**, top to bottom, in the configured
  teammate order. Cards **never overlap** — a fixed `CARD_SPACING_PX` gap separates each card
  from the next (this is the explicit fix for the overlapping rough mock). The column grows
  downward to fit 1…N cards.
- **Uniform sizing**: every card is exactly `CARD_WIDTH_PX` × `CARD_HEIGHT_PX`, giving the
  column a clean, uniform left edge regardless of teammate count.

---

## Win-Rate Ring spec

**Geometry**
- Outer diameter = `RING_DIAMETER_PX`; donut wall thickness = `RING_THICKNESS_PX`
  (inner hole diameter = `RING_DIAMETER_PX − 2 × RING_THICKNESS_PX`).
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
  `RING_BEVEL_INNER_WIDTH_PX` in `COLOR_RING_BEVEL_INNER`.
- A **cyan accent hairline** (`COLOR_RING_ACCENT_CYAN`, `RING_ACCENT_WIDTH_PX`) traces the inner
  edge of the track for the HUD sheen.
- A soft **glow** (`COLOR_RING_GLOW` at `COLOR_RING_GLOW_ALPHA`) surrounds the ring with
  `RING_GLOW_BLUR_PX` blur and `RING_GLOW_SPREAD_PX` spread.

**Arc-color rules**
- **Win arc** = `COLOR_WIN_ARC` (vivid, non-neon green). **Loss arc** = `COLOR_LOSS_ARC` (harsh
  red). The win arc starts at `RING_START_ANGLE_DEG` and sweeps clockwise by the win-rate share;
  the loss arc continues from where it ends and fills the remainder back to the start, so the
  two always complete the whole ring (green% + red% = 100%, no leftover track shows when data
  exists).
- Each arc carries a faint same-color glow at `COLOR_ARC_GLOW_ALPHA` (the glow reuses that arc's
  own RGB) so the lit segment feels emissive like the ult charge.
- Win rate 0% → fully red; 100% → fully green.
- **No data / unresolved teammate** → draw no colored arc; only the dark track + rim show (a
  neutral "empty" state), and the center shows a dash instead of a percentage.

**Tick / segment treatment (primary look)**
- The filled arcs render as a band of short radial **tick segments**, echoing the ult charge
  ticks: `RING_TICK_COUNT` evenly spaced segments around the full circle, each separated by
  `RING_TICK_GAP_DEG`. With `RING_TICK_COUNT = 50`, **each tick = 2%** of win rate, so:
  `green_tick_count = round(win_rate_percent × RING_TICK_COUNT ÷ 100)`, and the remaining ticks
  are red. (A smooth solid arc, where `win_sweep_deg = win_fraction × RING_FULL_SWEEP_DEG`, is
  the documented fallback — see Open Questions.)

**Center text**
- The win-rate percentage (e.g. `63%`) is centered in the hole in HUD style: `FONT_FAMILY_PRIMARY`,
  number at `FONT_RING_CENTER_SIZE_PT`, the trailing `%` at the smaller `FONT_RING_SUFFIX_SIZE_PT`,
  weight `FONT_RING_CENTER_WEIGHT`, italic `FONT_RING_CENTER_ITALIC`, tracking
  `FONT_HUD_LETTER_SPACING_PCT`, color `COLOR_CENTER_TEXT`, over a drop shadow
  (`COLOR_CENTER_TEXT_SHADOW` at `COLOR_CENTER_TEXT_SHADOW_ALPHA`) for legibility above the glow.

---

## Card spec

- **Panel**: a rounded-rectangle filled with `COLOR_CARD_BG` at `COLOR_CARD_BG_ALPHA`, corner
  radius `CARD_CORNER_RADIUS_PX`, with a `CARD_BORDER_WIDTH_PX` border in `COLOR_CARD_BORDER`
  at `COLOR_CARD_BORDER_ALPHA`.
- **Accent**: a vertical cyan accent bar of `CARD_ACCENT_WIDTH_PX` in `COLOR_CARD_ACCENT` runs
  down the panel's left inside edge (an Overwatch HUD signature).
- **Inner padding**: `CARD_PADDING_PX` on all sides.
- **Top row (the cohesive icon+ring pairing)** — laid out left → right, vertically centered,
  separated by `CARD_ELEMENT_GAP_PX`:
  1. **Hero shield icon** (`ICON_BADGE_WIDTH_PX` × `ICON_BADGE_HEIGHT_PX`).
  2. **Win-rate ring** (`RING_DIAMETER_PX`), *directly next to the icon* per "the Hero Icon with
     Win Rate right next to it." Icon and ring sit adjacent but **never overlap**.
- **Label block**: below the top row, separated by `LABEL_BLOCK_GAP_PX`, left-aligned, of height
  `LABEL_AREA_HEIGHT_PX`, holding two stacked lines separated by `LABEL_LINE_SPACING_PX`:
  - **Line 1 — player name**: `COLOR_LABEL_PRIMARY`, `FONT_LABEL_NAME_SIZE_PT`, weight
    `FONT_LABEL_NAME_WEIGHT`.
  - **Line 2 — most-played hero**: `COLOR_LABEL_SECONDARY`, `FONT_LABEL_SUB_SIZE_PT`, weight
    `FONT_LABEL_SUB_WEIGHT`.
  - The block is intentionally sized to leave room for one or two extra metric lines later
    (e.g. games played).
- Text wider than the content area is truncated with an ellipsis (no wrapping), to preserve the
  uniform card height.

---

## Hero icon spec

- **Frame shape**: a **shield/badge** silhouette matching the concept — a rectangle with rounded
  top corners (`ICON_TOP_CORNER_RADIUS_PX`) whose bottom edges angle inward to a centered point
  that drops `ICON_BOTTOM_POINT_DEPTH_PX` below the sides. This is the primary shape, not a
  fallback.
- **Frame border**: a glowing cyan edge `ICON_FRAME_WIDTH_PX` wide in `COLOR_ICON_FRAME`, backed
  by a darker inner bevel line in `COLOR_ICON_FRAME_INNER` (mirroring the ring's double rim), and
  a soft outer glow (`COLOR_ICON_FRAME_GLOW` at `COLOR_ICON_FRAME_GLOW_ALPHA`, blur
  `ICON_FRAME_GLOW_BLUR_PX`) so the badge and ring share one cyan family.
- **Portrait**: the hero portrait scales to fill and is clipped to the shield path.
- **Fallback (missing / loading / unknown hero)**: fill the shield with `COLOR_ICON_BG_FALLBACK`
  and center the hero's initial(s) or `?` in `COLOR_ICON_FALLBACK_TEXT` at
  `FONT_ICON_FALLBACK_SIZE_PT`, keeping the same shield + frame + glow so the layout never shifts.

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
| color | `COLOR_RING_TRACK` | `#0B1220` | Dark recessed donut track behind the arcs |
| color | `COLOR_RING_BEVEL_OUTER` | `#5FD8EC` | Bright outer rim of the beveled double border |
| color | `COLOR_RING_BEVEL_INNER` | `#1C5C73` | Darker inner bevel of the double border |
| color | `COLOR_RING_ACCENT_CYAN` | `#4DD2E6` | Cyan accent hairline on the track inner edge |
| color | `COLOR_RING_GLOW` | `#36C8E0` | Cyan glow color around the ring |
| color | `COLOR_RING_GLOW_ALPHA` | `130` | Ring glow opacity |
| color | `COLOR_WIN_ARC` | `#4CC95A` | Win-rate arc (vivid, non-neon grass green) |
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
| size | `OVERLAY_MARGIN_X_PX` | `24` | Column inset from the screen's left edge |
| size | `OVERLAY_MARGIN_Y_PX` | `96` | Column inset from the top (clears the game nav bar) |
| size | `CARD_WIDTH_PX` | `170` | Fixed card width |
| size | `CARD_HEIGHT_PX` | `148` | Fixed card height |
| size | `CARD_SPACING_PX` | `14` | Vertical gap between stacked cards (enforces no overlap) |
| size | `CARD_CORNER_RADIUS_PX` | `10` | Card panel corner radius |
| size | `CARD_BORDER_WIDTH_PX` | `1` | Card panel border thickness |
| size | `CARD_ACCENT_WIDTH_PX` | `3` | Width of the card's left cyan accent bar |
| size | `CARD_PADDING_PX` | `12` | Inner padding inside each card |
| size | `CARD_ELEMENT_GAP_PX` | `10` | Horizontal gap between the hero shield and the ring |
| size | `LABEL_BLOCK_GAP_PX` | `8` | Vertical gap between the icon/ring row and the label block |
| size | `LABEL_AREA_HEIGHT_PX` | `38` | Height reserved for the label block |
| size | `LABEL_LINE_SPACING_PX` | `3` | Vertical gap between the two label lines |
| size | `ICON_BADGE_WIDTH_PX` | `64` | Hero shield width |
| size | `ICON_BADGE_HEIGHT_PX` | `78` | Hero shield height (taller than wide) |
| size | `ICON_FRAME_WIDTH_PX` | `3` | Hero shield frame border thickness |
| size | `ICON_TOP_CORNER_RADIUS_PX` | `8` | Rounding of the shield's top corners |
| size | `ICON_BOTTOM_POINT_DEPTH_PX` | `12` | How far the shield's bottom point drops below its sides |
| size | `ICON_FRAME_GLOW_BLUR_PX` | `6` | Blur radius of the hero shield frame glow |
| size | `RING_DIAMETER_PX` | `72` | Outer diameter of the win-rate donut |
| size | `RING_THICKNESS_PX` | `10` | Donut wall thickness |
| size | `RING_TRACK_INSET_PX` | `2` | Inset of the recessed track for depth |
| size | `RING_BEVEL_OUTER_WIDTH_PX` | `2` | Outer rim line width |
| size | `RING_BEVEL_INNER_WIDTH_PX` | `2` | Inner bevel line width |
| size | `RING_ACCENT_WIDTH_PX` | `1` | Cyan accent hairline width |
| size | `RING_GLOW_BLUR_PX` | `8` | Blur radius of the ring glow |
| size | `RING_GLOW_SPREAD_PX` | `2` | Spread of the ring glow |
| size | `RING_FULL_SWEEP_DEG` | `360` | Degrees in a full ring (avoids a bare 360) |
| size | `RING_START_ANGLE_DEG` | `90` | Arc start at 12 o'clock (Qt convention, CCW-positive) |
| size | `RING_SWEEP_DIRECTION` | `"clockwise"` | Direction the arcs grow from the start angle |
| size | `RING_TICK_COUNT` | `50` | Tick segments around the full ring (each = 2% of win rate) |
| size | `RING_TICK_GAP_DEG` | `2` | Angular gap between adjacent tick segments |
| typography | `FONT_FAMILY_PRIMARY` | `"Oswald"` | HUD font family (fallback: "Bebas Neue", "Arial Narrow", sans-serif) |
| typography | `FONT_RING_CENTER_SIZE_PT` | `19` | Win-rate number size |
| typography | `FONT_RING_SUFFIX_SIZE_PT` | `11` | Trailing `%` sign size (smaller than the number) |
| typography | `FONT_RING_CENTER_WEIGHT` | `700` | Win-rate number weight (bold) |
| typography | `FONT_RING_CENTER_ITALIC` | `true` | Win-rate number italic (HUD slant) |
| typography | `FONT_HUD_LETTER_SPACING_PCT` | `4` | Letter spacing for the center number (% of em) |
| typography | `FONT_LABEL_NAME_SIZE_PT` | `11` | Player-name label size |
| typography | `FONT_LABEL_NAME_WEIGHT` | `700` | Player-name label weight |
| typography | `FONT_LABEL_SUB_SIZE_PT` | `9` | Most-played-hero label size |
| typography | `FONT_LABEL_SUB_WEIGHT` | `400` | Most-played-hero label weight |
| typography | `FONT_ICON_FALLBACK_SIZE_PT` | `16` | Fallback initial / `?` size in the shield |
| timing | `RING_FILL_ANIM_MS` | `600` | Duration of the arc sweep animation on data update |
| timing | `RING_FILL_EASING` | `"OutCubic"` | Easing curve for the arc fill |
| timing | `VALUE_TWEEN_MS` | `600` | Duration of the center number counting up to its value |
| timing | `CARD_FADE_IN_MS` | `250` | Fade-in duration when a card first appears |
| timing | `CARD_STAGGER_MS` | `80` | Per-card delay so the column fades in top-down |
| timing | `GLOW_PULSE_PERIOD_MS` | `2400` | Period of the subtle cyan glow pulse |

---

## Open Questions

1. **Anchor corner**: default is **top-left** to match the rough mock and avoid the in-game
   party panel (top-right). Confirm top-left, or expose the corner (TL/TR/BL/BR) as a config
   setting.
2. **Exact arc hexes**: committed to `COLOR_WIN_ARC = #4CC95A` (vivid grass green, kept clearly
   distinct from the cyan rim) and `COLOR_LOSS_ARC = #E53935` (harsh red). Confirm these exact
   values or nudge the green warmer/cooler.
3. **Tick vs solid arcs**: segmented ticks (`RING_TICK_COUNT = 50`, each = 2%) are the intended
   ult-ring look. Is a smooth solid arc an acceptable v1 fallback if ticks prove fiddly to render?
4. **Card composition**: committed to the **compact vertical card** (icon + ring on top, label
   beneath) so the column stays narrow against the screen edge like the mock. Confirm, or prefer
   the alternative (icon | ring | labels in one wide horizontal row → shorter but ~320px-wide
   cards).
5. **Shield vs rounded rectangle**: committed to the full **shield/badge** silhouette
   (`ICON_TOP_CORNER_RADIUS_PX` + `ICON_BOTTOM_POINT_DEPTH_PX`). Acceptable to ship a plain
   rounded rectangle for v1 if the shield path is deferred?
6. **Arc seam**: green and red currently meet with no gap so they fill the whole ring. Want a
   tiny dark seam between them for separation? (Would add a `RING_ARC_GAP_DEG` token.)
7. **Win-rate metric basis**: competitive-only vs quickplay + competitive combined. Affects the
   number shown, not the visuals (the design assumes one 0–100% value per teammate).
8. **Font bundling**: `FONT_FAMILY_PRIMARY = "Oswald"` assumes the font is bundled/installed.
   Confirm we may ship it; otherwise the spec falls back to a condensed system sans-serif.
