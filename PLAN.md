# PLAN.md

Scratchpad for active/upcoming work. Expected to drift — completed items
collapse to one-liners once their durable signal lands in an ADR or
`.claude/memory/`. Blow-by-blow does NOT live here.

## Working state (2026-07-11)

- All Goal 3 work-to-date is merged to `main` (PRs #6, #8, #9 here; #2 on
  `project-memory-template`) — no open PRs on either repo. This repo's own
  memory architecture (`CLAUDE.md`, this file, `.claude/memory/`,
  `docs/adr/`) is live, not just proposed.
- User re-sequenced the remaining slate (2026-07-11): this repo needs to be
  fully trustworthy on its own before being used as the pattern for
  elsewhere. Regression-testing standard (Dynasty-facing) moved to *last* —
  it was about to be built next, but the user wants this repo's own
  in-repo tooling (guardrail, hygiene) proven out first.

## ➡ NEXT — in order

1. ~~`continual-learning` hook port~~ — built and merged (PR #11), see
   `hooks/continual-learning/`. Ported (not copied) to Claude Code's
   `SessionStart`/`PostToolUse`/`PostToolUseFailure`/`SessionEnd` events;
   global-scope install (works in every repo, not just this one) with the
   original's two-tier global+local SQLite DB design preserved.
   **Activation gate (open)**: this machine has neither `sqlite3` nor `jq`
   on `PATH` in Git Bash, so the hook currently no-ops everywhere if
   installed as-is. Before flipping it on, interrogate (plan +
   crystallize, not just "go install it"): which binaries/how (winget vs.
   choco vs. manual download+PATH edit), whether both are strictly
   required or `jq`'s absence is an acceptable degrade long-term, and
   whether this is a one-time machine setup step or something the hook's
   own README should test/warn about at session start. Landing the code
   was not landing the capability — treat "hook active and actually
   persisting learnings" as the real done-condition, not "PR merged."
2. ~~Git guardrail hook~~ — built, see `hooks/git-guardrails/`. Branch-aware
   `git push` guard (blocks only `main`/`master` targets, allows feature
   branches) plus the upstream blanket-blocked destructive patterns
   (`reset --hard`, `clean -f(d)`, `branch -D`, `checkout .`/`restore .`),
   global-scope install per user decision (matches `continual-learning`'s
   scope). No `jq` dependency (uses `sed`) — **not gated on the same
   activation problem as `continual-learning`**, this one can actually be
   installed and active today. Verified against 14 hand-built test cases
   (main/master targets by refspec, delete, rename-into-main, bare push
   falling back to current branch, explicit non-main branches, force-push
   to a feature branch, non-git commands) before writing it up. Needs a
   PR + merge, then an explicit decision on whether to actually install it
   into `~/.claude/settings.json` on this machine now.
3. **Check-in hygiene hook** — flags empty/stale scaffold files + README
   staleness (see the `README.md` Roadmap item logged during
   `project-memory-template` planning).
4. **Regression-testing standard** — Dynasty-facing (pytest + pre-commit +
   `check_sources.py`), fully designed and grilled already (notebook
   strategy, pre-commit scope, `offline_smoke.py` rename, no venv wrapper,
   CI deferred with ADR-0004 reasoning) — just needs building. Deliberately
   last in this re-sequencing, not because the design work is stale.

## [ ] Deferred

- [ ] `update-vendor-skills.ipynb` rework — drift detection, fork-handling
  automation, `plugin_manifests_only[]` awareness.
- [ ] Skill-stage/domain routing map maintenance — keep in sync if the
  skill catalog churns (flagged as a Divergent-Change risk in review).
- [ ] Orphan project-skill detection — hook/subagent scanning consuming
  repos' own `.claude/skills/` for skills not in this central catalog.
- [ ] Apply `project-memory-template` to a fresh environment as a test
  case — after the above, not yet chosen.

## Shipped (one-liners; full detail in ADR / `.claude/memory/`)

- **Goal 1**: renamed `skills` → `skills-plugins-hooks`, added
  `plugins/`/`hooks/` scaffolding.
- **Goal 2**: saturated the catalog (Pocock's idea→ship flow, ponytail,
  Power BI/Fabric skills) — merged PR #4.
- **Goal 3, in progress**: `project-memory-template` scaffold; skill-
  distribution bugs found and fixed; skill-stage/domain routing map;
  two-axis review of both repos' shipped work + fixes; this repo's own
  `common/` relocation (→ `skills/_powerbi-authoring-common/`) and full
  memory architecture (`CLAUDE.md`/`PLAN.md`/`.claude/memory/`/4 ADRs) —
  all merged to `main`.
