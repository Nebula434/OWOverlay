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
   - Output: `DESIGN.md` (the single source of truth for the look) + a design-token table.
2. **Code subagent** (`02_code_subagent.md`)
   - Focuses ONLY on code. Implements the app to match `DESIGN.md`.
   - MUST centralize every visual value (colors, sizes, fonts) in one theme module so a
     redesign means editing tokens, not logic.
   - MUST NOT invent design decisions — it reads them from `DESIGN.md`.
3. **Design-review subagent** (`03_review_subagent.md`)
   - Verifies the code result matches the design vision in `DESIGN.md`.
   - For every mismatch: append a clear entry to `ISSUES.md`.
   - For anything that needs a human decision: list it under "Questions for the user" so the
     orchestrator can surface it in chat.
   - MUST NOT fix code; it only documents findings.

## Sequence
1. Design subagent → `DESIGN.md`.
2. Code subagent → application code + `requirements.txt` + `config.example.json` + `README.md`.
3. Design-review subagent → `ISSUES.md` (+ questions surfaced to the user).
4. Orchestrator reviews everything, fixes blocking bugs/lints, reports to the user.

## Shared facts (given to every subagent)
- Data source: **OverFast API** (`https://overfast-api.tekrop.fr`) — unofficial, **no API key**.
- Player id format: BattleTag with `#` replaced by `-` (e.g. `TeKrop-2217`).
- Profiles must be **public** on Blizzard for stats to resolve, else the API returns 404.
- There is **no API to auto-detect live teammates**, so tracked players come from a config list.
- Language: **Python 3.11+ with PySide6** (transparent, always-on-top overlay window).
- User constraints: no magic numbers; only add variables/constants when needed and categorize them.
