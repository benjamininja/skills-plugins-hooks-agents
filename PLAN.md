# PLAN.md

Scratchpad for active/upcoming work. Expected to drift — completed items
collapse to one-liners once their durable signal lands in an ADR or
`.claude/memory/`. Blow-by-blow does NOT live here.

## Working state (2026-07-12)

**Goal 3 is fully shipped, including activation.** All four re-sequenced
items landed and merged to `main` on every repo touched
(`skills-plugins-hooks-agents`, `project-memory-template`,
`Python-PowerBI-DynastyFantasyFootball`) — zero open PRs anywhere. The
`continual-learning` hook is now installed and live on this machine (see
Shipped below). Full detail in `.claude/memory/program-status.md`.

**2026-07-12 rename**: repo renamed `skills-plugins-hooks` →
`skills-plugins-hooks-agents` on GitHub (`gh repo rename`) and locally
(folder renamed by user, `origin` remote updated to match). In-repo
references to the old name updated in `CLAUDE.md`, `README.md`, `PLAN.md`,
`.claude/memory/MEMORY.md`; historical mentions of the Goal-1
`skills`→`skills-plugins-hooks` rename left as accurate history. No
`agents/` directory exists yet — the name anticipates future scope, not
yet scaffolded; revisit when agent content actually lands.

## ➡ NEXT

**`subagent-audit` skill + first real run (2026-07-12, in flight).** User
supplied a "Subagent Opportunity Audit" prompt (six candidate categories,
hard hook-vs-subagent boundary, 3–5 candidate cap, `.claude/agents/*.md`
draft output); decided it belongs here as an authored skill — this repo is
the skill catalog and the `-agents` rename anticipated exactly this scope
(`project-memory-template` was considered and rejected: memory-scoped, and
a doc there isn't invocable). Adaptations over the raw prompt: inventory
step also reads reachable skills so it doesn't propose subagents that
duplicate them; added an explicit skill (vs hook/subagent) definition; new
Step 5 persists accepted/rejected reasoning to the target repo's memory
scaffold. Acceptance test: run the audit for real against
`Python-PowerBI-DynastyFantasyFootball` (richest target: MCP surface,
large data fixtures, scrapers). Its output will produce the first real
`.claude/agents/` definitions anywhere in this ecosystem — which then
informs whether this repo grows an `agents/` catalog directory.

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
- **Repo renamed** `skills-plugins-hooks` → `skills-plugins-hooks-agents`
  (2026-07-12, `gh repo rename` + local remote + in-repo references).
- **Post-Goal-3 audit, all 4 gaps fixed**: `continual-learning` re-verified
  live post-restart (real harness-fired `tool_log` rows) and grilled
  against upstream `microsoft/skills` source (two known limitations
  confirmed inherited, not port bugs — see `hooks/continual-learning/README.md`);
  Dynasty's `pre-commit install` activated (`Python-PowerBI-DynastyFantasyFootball#20`);
  `check-in-hygiene` adopted by a real consumer for the first time ever
  (Dynasty + this repo), which surfaced and fixed two genuine cross-platform
  packaging bugs (`project-memory-template#6`); stale docs (`hooks/README.md`,
  root `README.md`) corrected.
- **Skill routing + junction drift detection** (ADR-0005): discovered
  every `~/.claude/skills/` junction on this machine was broken (pointed
  at the repo's pre-Goal-1 name, silently stranding every Pocock-flow
  skill for weeks) — all 34 relinked. New `hooks/skill-catalog-health/`
  (`SessionStart`) injects a self-generated routing index (mirrors
  upstream `mattpocock/skills`' README Reference-table format) so
  `disable-model-invocation: true` router skills still get surfaced, and
  flags future broken junctions instead of failing silently. New
  `skills/setup-project-memory` orchestrates the three previously
  uncoordinated bootstrap steps (memory tier, `setup-matt-pocock-skills`,
  `check-in-hygiene` pre-commit) in one pass — resolves the "apply
  `project-memory-template` to a fresh environment" deferred item below
  (not yet run as a live test).
