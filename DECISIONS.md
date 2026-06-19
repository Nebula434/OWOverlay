# DECISIONS.md — Human decisions resolved by the orchestrator

> Orchestrator-owned coordination record. Captures the user's answers to the gating
> "Open Questions" from `DESIGN.md`. The **design-subagent** should fold these into `DESIGN.md`
> (resolving its Open Questions); the **code-subagent** must implement to match. Status of the
> build flow is at the bottom.

| # | Question | Decision | Impact |
|---|---|---|---|
| 1 | Ring fill style | **Segmented ticks now** (full Overwatch tick look) | code: ring renders `RING_TICK_COUNT` ticks with `RING_TICK_GAP_DEG`, win ticks `COLOR_WIN_ARC`, loss ticks `COLOR_LOSS_ARC` — not smooth arcs |
| 2 | Hero icon frame shape | **Rounded rectangle for v1** (shield shape deferred) | code: use `ICON_CORNER_RADIUS_PX`; no shield/chevron path yet |
| 3 | Overlay anchor corner | **Configurable (TL/TR/BL/BR), default top-right** | code: anchor corner is a `config.json` setting, default top-right; window positions off the chosen corner using `OVERLAY_MARGIN_PX` |
| 4 | Arc seam between green/red | **No seam** — arcs touch and fill the whole ring | no new token needed; matches current `DESIGN.md` |
| 5 | Win-rate metric basis | **Quickplay + competitive combined** | code: fetch both gamemodes and combine; win rate shown is the combined figure, NOT competitive-only |
| 6 | HUD font | **Closest-to-Overwatch font as default, but user-configurable** | code: font family is a config-overridable setting (default = nearest free condensed face, e.g. Bebas Neue / Oswald); do not hard-require Oswald |

## Notes for the subagents

- **Decision 5 changes the data layer.** The code-subagent prompt (`prompts/02_code_subagent.md`)
  specifies `gamemode=competitive` only. Combined means querying competitive **and** quickplay
  summaries and merging them (e.g. recompute win rate from combined games_won / games_played,
  and pick the most-played hero across both). The design treats this as the single 0–100% value
  per teammate; visuals are unchanged.
- **Decision 6 makes the font a setting.** `FONT_FAMILY_PRIMARY` stays the default token in
  `theme.py`, but the effective font must be overridable from `config.json` so the user can pick
  any installed font. Bundle no copyrighted Overwatch fonts.
- Decisions 1, 2, 4 are already consistent with `DESIGN.md` as written (ticks intended,
  rounded-rect fallback, no seam) — they just confirm those paths.
- Decision 3 adds an anchor-corner config key (default top-right).

## Build flow status

- HALTED by orchestrator pending these decisions — **now resolved above**.
- Awaiting the user's explicit **`CONTINUE`** before the design/code/review subagents resume.
