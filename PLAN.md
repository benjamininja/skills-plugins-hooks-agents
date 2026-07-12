# PLAN.md

Scratchpad for active/upcoming work. Expected to drift — completed items
collapse to one-liners once their durable signal lands in an ADR or
`.claude/memory/`. Blow-by-blow does NOT live here.

## Working state (2026-07-12)

**Goal 3 is fully shipped, including activation.** All four re-sequenced
items landed and merged to `main` on every repo touched
(`skills-plugins-hooks`, `project-memory-template`,
`Python-PowerBI-DynastyFantasyFootball`) — zero open PRs anywhere. The
`continual-learning` hook is now installed and live on this machine (see
Shipped below). Full detail in `.claude/memory/program-status.md`.

## ➡ NEXT

**2026-07-12, second session: skill routing + drift detection, shipped.**
A post-audit discovery (every `~/.claude/skills/` junction on this machine
was broken — pointed at the repo's name from *before* even the Goal-1
rename, silently stranding every Pocock-flow skill for weeks) turned into
a grilled, ADR'd design covering three related gaps. See
[ADR-0005](docs/adr/0005-skill-routing-and-drift-detection.md) for full
reasoning; summary:

- **`hooks/skill-catalog-health/`** (new, installed and active) —
  `SessionStart` hook injecting a compact routing index (mirrors upstream
  `mattpocock/skills`' own README Reference-table format) so
  `disable-model-invocation: true` router skills still get surfaced as
  suggestions without changing their manual-invoke status, plus flags any
  broken skill junction going forward instead of failing silently.
- **`skills/setup-project-memory`** (new, manual-invoke) — orchestrates
  the three previously-uncoordinated bootstrap steps (memory tier scaffold,
  `setup-matt-pocock-skills`, `check-in-hygiene` pre-commit wiring) for a
  brand-new or partially-wired project. Lives here (the one canonical
  skill-source repo), reads tier content from `project-memory-template`.
- `ask-matt`'s Precondition section updated to point at it.
- `manifest.json`'s `hooks: []` was also stale (never listed
  `continual-learning`/`git-guardrails` despite both being real, active
  hooks) — fixed alongside adding the new entries.

This also unblocks the long-deferred "apply `project-memory-template` to a
fresh environment" item below — `setup-project-memory` is that test case,
not yet run.

## [ ] Deferred

- [ ] `update-vendor-skills.ipynb` rework — drift detection, fork-handling
  automation, `plugin_manifests_only[]` awareness.
- [ ] Skill-stage/domain routing map maintenance — keep in sync if the
  skill catalog churns (flagged as a Divergent-Change risk in review).
- [ ] Orphan project-skill detection — hook/subagent scanning consuming
  repos' own `.claude/skills/` for skills not in this central catalog.
- [ ] Apply `project-memory-template` to a fresh environment as a test
  case, now via `/setup-project-memory` — not yet run.

## Shipped (one-liners; full detail in ADR / `.claude/memory/`)

- **Goal 1**: renamed `skills` → `skills-plugins-hooks`, added
  `plugins/`/`hooks/` scaffolding.
- **Goal 2**: saturated the catalog (Pocock's idea→ship flow, ponytail,
  Power BI/Fabric skills) — merged PR #4.
- **Goal 3, done**: `project-memory-template` scaffold; skill-distribution
  bugs found and fixed; skill-stage/domain routing map; two-axis review of
  both repos' shipped work + fixes; this repo's own `common/` relocation
  (→ `skills/_powerbi-authoring-common/`) and full memory architecture
  (`CLAUDE.md`/`PLAN.md`/`.claude/memory/`/4 ADRs); `continual-learning`
  hook port and activation (`sqlite3`/`jq` installed via `winget`, hooks
  merged into `~/.claude/settings.json`, verified persisting real rows);
  `git-guardrails` hook (built and activated); `check-in-hygiene` hook;
  regression-testing standard (general doc + Dynasty retrofit, ADR-0008)
  — all merged to `main` across all three repos. Full detail in
  `.claude/memory/program-status.md`.
