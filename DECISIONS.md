# DECISIONS.md — Human decisions resolved by the orchestrator

> Orchestrator-owned coordination record of the user's confirmed choices. After the
> design-subagent's overhaul of `DESIGN.md`, the user re-confirmed the conflicting points
> (see "Round 2" below). **The revised `DESIGN.md` is now authoritative and matches these
> decisions** — the code-subagent implements `DESIGN.md`; the review-subagent verifies against it.

## Round 1 — gating Open Questions

| # | Question | Decision | Impact |
|---|---|---|---|
| 1 | Ring fill style | **Segmented ticks** (full Overwatch tick look) | `DESIGN.md`: `RING_TICK_COUNT = 50`, each tick = 2%, `RING_TICK_GAP_DEG`, `RING_TICK_LENGTH_PX` |
| 5 | Win-rate metric basis | **Quickplay + competitive combined** (now exposed as a user-configurable basis) | code: support combined basis; `DESIGN.md` Open Q7 makes comp-only vs combined a `config.json` setting |
| 6 | HUD font | **Closest-to-Overwatch font as default, user-configurable** | `DESIGN.md`: `FONT_FAMILY_PRIMARY = "Koverwatch"` (free OW replica) + fallback chain; code must let the user override the font via `config.json`, bundle nothing copyrighted |

## Round 2 — re-confirmed after the DESIGN.md overhaul

The design-subagent's revision changed three Round-1 answers; the user reviewed and chose to
**adopt the revised design** in all three cases:

| # | Original Round-1 answer | Final decision (authoritative) | Reflected in `DESIGN.md` as |
|---|---|---|---|
| 2 | Rounded rectangle for v1 | **Shield/badge silhouette** | `ICON_TOP_CORNER_RADIUS_PX` + `ICON_BOTTOM_POINT_DEPTH_PX` shield path |
| 3 | Default top-right | **Default top-left** (avoids the in-game party panel; still configurable) | anchor default top-left, `OVERLAY_MARGIN_X_PX` / `OVERLAY_MARGIN_Y_PX` |
| 4 | No seam | **6° dark seam** between win/loss arcs | `RING_ARC_GAP_DEG = 6` (the recessed track shows through) |

## Outstanding code follow-ups (orchestrator review)

These are gaps in the 9 modules produced before the code-subagent restarted; verify they are
addressed in the restarted run (or fix during the orchestrator review pass):

- **Win-rate basis (decision 5):** earlier code was competitive-only. Implement the configurable
  comp-only vs combined basis (combined = merge competitive + quickplay summaries).
- **Configurable font (decision 6):** earlier `theme.FONT_FAMILY_PRIMARY` was fixed; expose a
  `config.json` font override that feeds the font family used by `theme`/widgets.
- **Shield icon (decision 2):** earlier `hero_icon.py` drew a rounded rectangle; it must paint the
  shield silhouette per the revised `DESIGN.md`.
- **Arc seam (decision 4):** earlier `winrate_ring.py` had no seam token; honor `RING_ARC_GAP_DEG`.

## Build flow status

- Round-1 and Round-2 decisions are **resolved**; revised `DESIGN.md` is authoritative.
- Code-subagent has restarted and is implementing the revised design — orchestrator is monitoring
  and will do a consolidated review once it finishes.

## 2026-06-19 — Design expansion: standalone application spec (`APP_DESIGN.md`)

> Orchestrator coordination record (not a review finding, not a design decision). Logs a
> rules-maintenance pass that realigns the workflow for a major design expansion. **No subagent was
> spawned and `APP_DESIGN.md` was NOT created** in this pass — the design-subagent owns that file.

**What is changing.** The design-subagent is being re-pointed to author a brand-new, authoritative
spec **`APP_DESIGN.md`** that exhaustively documents the concept image
`concepts/CONCEPT_STANDALONE_APPLICATION.png` — a **full standalone application** — so the
code-subagent can implement it easily. `APP_DESIGN.md` sits **alongside `DESIGN.md`**, which keeps
the in-game overlay plus the interim game-closed stats and settings windows. The app should reuse
**real/existing Overwatch assets** (rank, role/tank, elims, damage-done, etc.) instead of
placeholder shapes wherever possible.

**Faithful summary of the design-subagent prompt (reference-only; NOT executed here).**
- Start the design-subagent and have it create a new file `APP_DESIGN.md`.
- In `APP_DESIGN.md`, exhaustively document **every detail** of
  `concepts/CONCEPT_STANDALONE_APPLICATION.png` so the code-subagent can implement it easily.
- The design-subagent **ignores all of its own rules except**: the initial **"Context"**, the
  **"Win-rate ring"** reference concept, and **all Absolute rules except Rule 3** — Rule 3 ("only
  writable deliverable is `DESIGN.md`") is **lifted** so it may write `APP_DESIGN.md`. If achieving
  the goal (ALL design details inside `APP_DESIGN.md`) needs more rules lifted, it should **request**
  those lifts rather than assume them.
- Prefer **existing Overwatch assets** (rank, tank/role, elims, damage-done, etc.) over the
  placeholder assets.
- Double-check the work; make the design plan reproduce the screenshot's **look exactly** (achieve
  the application's look — excluding the specific stat values).

**Rules realignment done in this pass (orchestrator-authored docs only).** Integrated `APP_DESIGN.md`
as a second design source-of-truth, the prefer-real-assets requirement, and the standalone-app
direction across `.cursor/agents/{orchestrator,code-subagent,review-subagent}.md`,
`prompts/{00_orchestration,02_code_subagent,03_review_subagent}.md`, a structural cross-reference in
`DESIGN.md`, and `README.md` (mirrored into `githubREADME.md`). **Untouched by rule:**
`design-subagent.md`, `prompts/01_design_subagent.md`, and all `src/` code.

## Orchestrator Change-Monitor Log

> Orchestrator-owned **monitoring** record — NOT review findings (`ISSUES.md` stays the
> review-subagent's deliverable) and NOT design decisions. Changes are detected by file
> `LastWriteTime` + MD5 hash because the `git` CLI is unavailable in this environment.

### 2026-06-19 — monitoring pass (~06:30–06:34; one interval, ~90 s sleep)
- **Baseline:** user reference ~06:26 (`ISSUES.md` newest); orchestrator hash baseline captured
  06:30:45 over the watched set (`DESIGN.md`, `ISSUES.md`, `DECISIONS.md`, `requirements.txt`,
  `config.example.json`, `README.md`, `src/overlay/**`). Re-checked 06:33:41.
- **Result: CHANGES DETECTED** — the code-subagent is actively editing:
  - `src/overlay/main.py` — 06:29:44 — substantive: new vk-based `HotkeyManager` (fix for the
    `C-SA CB` toggle first-press reliability / Windows AltGr drop).
  - `src/overlay/ui/hero_icon.py` — 06:30:39 — substantive: looping `_glow_anim` added (fix for
    the MINOR "hero-icon glow does not breathe" compliance gap; now mirrors `winrate_ring`).
  - `src/overlay/ui/overlay_window.py` — 06:30:56 — re-saved; hash changed, content functionally
    unchanged on re-read.
  - `src/overlay/config.py` — 06:31:04 — re-saved; content functionally unchanged on re-read.
  - `src/overlay/data/stats_service.py` — 06:31:13 — re-saved; DEFERRED NOTE intact.
  - `src/overlay/data/models.py` — 06:31:20 — re-saved; DEFERRED NOTE intact.
  - (`main.py` + `hero_icon.py` are new vs. the ~06:26 reference; the other four changed strictly
    within the 06:30:45 → 06:33:41 interval. No watched file changed after 06:31:20 — a ~2m20s
    quiet tail, so the burst may be wrapping up.)
- **No halt condition:** the design-blocked features (in-app config screen #2; game-closed stats
  view #3) were NOT started — the `# NOTE: DEFERRED … blocked on ISSUES.md Questions for the user`
  markers remain in `config.py`, `main.py`, `stats_service.py`, `models.py`. Token centralization
  still holds; edits are legitimate in-lane fixes.
- **githubREADME.md:** NOT created this pass — the idle-path trigger ("no changes during one
  monitoring interval") was not met because changes were detected. Deferred to a follow-up once
  the code-subagent's current edit burst is confirmed finished.

### 2026-06-19 — monitoring pass (continuation; ~06:39–06:41)
- **Snapshot A (continuation baseline):** 06:38:59. **New activity since the prior report** (the
  06:33:41 re-check): `src/overlay/config.py` (06:38:05) and `src/overlay/main.py` (06:38:23)
  changed again — both **minor polish, not feature work**: `config.py` corrected a comment to
  reference `pynput.keyboard.HotKey.parse`; `main.py` reformatted the `_trigger_vk` char check
  (lint/style). All four `# NOTE: DEFERRED … blocked on ISSUES.md Questions for the user`
  markers remain intact in `config.py`, `main.py`, `stats_service.py`, `models.py` — the blocked
  features (in-app config screen #2, game-closed stats view #3) were NOT started. No halt
  condition; token centralization and lane discipline preserved.
- **Interval 1:** A (06:38:59) → ~90 s sleep → B (06:41:01) = **IDLE / no watched-file changes.**
  The code-subagent has gone quiet. (Only one interval needed; the ~3.5-min, two-interval cap was
  not reached.)
- **Idle-path goal reached → `githubREADME.md` CREATED** at the repo root (GitHub-facing landing
  page: title + tagline, overview + ult-ring visual language, features, screenshots/concept
  placeholder w/ concept art, requirements, install, configure (mirrors the `README.md` field
  table), run, how it works, project layout, status/roadmap from open `ISSUES.md` items, credits).
  The existing `README.md` was **not** overwritten; **no subagent was spawned** (orchestrator
  wrote it directly as user-assigned documentation).
- **Files the orchestrator changed this pass:** `githubREADME.md` (new) and this `DECISIONS.md`
  monitor log. No code, `DESIGN.md`, or `ISSUES.md` edits.
