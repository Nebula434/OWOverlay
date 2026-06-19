# Orchestration Plan — Overwatch Teammate Win-Rate Overlay

This file documents how subagents are used to build this project and the rules each one
must follow. The orchestrator (lead agent) coordinates them in sequence.

## Goal
A desktop overlay that displays, for each tracked teammate, a card showing their
**most-played hero** and **win rate**, with the win-rate visual styled after the
Overwatch ultimate-charge HUD ring. Code must be cleanly structured so the look can be
overhauled later without touching logic.

## Roles & hard rules
1. **Design subagent** (`01_design_subagent.md`)
   - Focuses ONLY on design/visual specification.
   - MUST NOT write, edit, or read-to-modify any code files (`*.py`, configs, requirements).
   - Output: `DESIGN.md` (overlay + interim stats/settings windows) and `APP_DESIGN.md` (the full
     standalone application per `concepts/CONCEPT_STANDALONE_APPLICATION.png`) — the sources of
     truth for the look — each with a design-token table.
2. **Code subagent** (`02_code_subagent.md`)
   - Focuses ONLY on code. Implements the app to match `DESIGN.md` and `APP_DESIGN.md`.
   - MUST centralize every visual value (colors, sizes, fonts) in one theme module so a
     redesign means editing tokens, not logic.
   - SHOULD prefer real/existing Overwatch assets (rank / role / stat icons, hero portraits) over
     placeholder shapes, cached under `assets/`.
   - MUST NOT invent design decisions — it reads them from `DESIGN.md` / `APP_DESIGN.md`.
3. **Design-review subagent** (`03_review_subagent.md`)
   - Verifies the code result matches the design vision in `DESIGN.md` and `APP_DESIGN.md`
     (including that real Overwatch assets are used where the spec calls for them).
   - For every mismatch: append a clear entry to `ISSUES.md`.
   - For anything that needs a human decision: list it under "Questions for the user" so the
     orchestrator can surface it in chat.
   - MUST NOT fix code; it only documents findings.

## Subagent authorization (required before any spawn)
The orchestrator has **NO standing authority to start subagents.** Before launching the design,
code, or review subagent it MUST request the user's explicit authorization for that specific
dispatch — naming the subagent, the task, and why — and wait for approval. A broad instruction
like "do all the work" is **not** blanket permission to spawn subagents. The sequence below is
the plan; every spawning step still requires the user's go-ahead. (Reviewing existing files does
not require a spawn and remains allowed, but the orchestrator does NOT modify code itself — all
code work, including bug/lint fixes, goes to the code subagent.)

## Sequence
1. Design subagent → `DESIGN.md` and `APP_DESIGN.md`.
2. Code subagent → application code + `requirements.txt` + `config.example.json` + `README.md`.
3. Design-review subagent → `ISSUES.md` (+ questions surfaced to the user).
4. Orchestrator reviews everything, routes any needed code fixes to the code subagent, reports to the user.

> Each of steps 1-3 spawns a subagent and therefore requires the user's explicit authorization
> first (see *Subagent authorization* above).

## Shared facts (given to every subagent)
- Data source: **OverFast API** (`https://overfast-api.tekrop.fr`) — unofficial, **no API key**.
- Player id format: BattleTag with `#` replaced by `-` (e.g. `TeKrop-2217`).
- Profiles must be **public** on Blizzard for stats to resolve, else the API returns 404.
- There is **no API to auto-detect live teammates**, so tracked players come from a config list.
- Language: **Python 3.11+ with PySide6** (transparent, always-on-top overlay window).
- The project is expanding toward a **full standalone application** specified in `APP_DESIGN.md`
  (per `concepts/CONCEPT_STANDALONE_APPLICATION.png`); `DESIGN.md` remains the spec for the in-game
  overlay (and the interim game-closed stats + settings windows).
- Prefer **real/existing Overwatch assets** (rank, role/tank, elims, damage-done, etc.) over
  placeholder shapes wherever possible; cache them under `assets/`.
- User constraints: no magic numbers; only add variables/constants when needed and categorize them.
