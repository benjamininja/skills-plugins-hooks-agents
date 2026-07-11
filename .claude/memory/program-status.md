# Program status — 3-goal restructure/saturation program

Three-goal program, planned 2026-07-11:

1. Rename `skills` repo → `skills-plugins-hooks`, add `plugins/`/`hooks/`
   scaffolding — **done**.
2. Saturate the repo (ponytail scan + Matt Pocock skill-gap integration) —
   **done and merged to main** (PR #4, merge commit `3c609ca`).
3. Synthesize `project-memory-template` from `Python-PowerBI-
   DynastyFantasyFootball`'s memory architecture — **scaffold done and
   merged** (public repo `benjamininja/project-memory-template`: tiered
   minimal/standard/full, `docs/graduating-tiers.md`, stress-tested against
   ponytail's YAGNI ladder + Pocock's grill-with-docs/domain-modeling
   live-generation pattern).

**Why:** a reusable, complexity-scaled memory-architecture template plus
tooling, informed by aligning with Matt Pocock's skill ecosystem and an
existing working example (the Dynasty repo).

## What Goal 2 actually landed

All in `skills/`, `vendor-skills.json` is the source of truth:

- Fixed a real vendor-drift bug: local `grill-with-docs` had silently
  forked from upstream's thin-pointer form; realigned by vendoring its two
  dependencies (`grilling`, `domain-modeling`) and restoring the pointer.
- Adopted Pocock's full idea→ship engineering flow (`ask-matt` router,
  `to-spec`/`to-tickets`/`implement`/`tdd`/`two-axis-code-review`/`triage`/
  `wayfinder`/`codebase-design`/`diagnosing-bugs`/
  `improve-codebase-architecture`/`prototype`/`resolving-merge-conflicts`/
  `setup-matt-pocock-skills`/`teach`/`writing-great-skills`) using its
  local-markdown tracker mode (no GitHub Issues needed).
- Forked `code-review` → `two-axis-code-review` (naming collision with an
  already-available `code-review` skill) — see
  [ADR-0001](../../docs/adr/0001-vendor-cache-fork-pattern.md).
- Vendored `microsoft-docs` and, from `microsoft/skills-for-fabric`, fully
  vendored the `powerbi-authoring` bundle (5 skills + `common/`) since Power
  BI/TMDL is real active work in the Dynasty repo — but kept
  `fabric-authoring`/`fabric-operations`/`fabric-skills` manifest-only, see
  [ADR-0002](../../docs/adr/0002-plugin-manifests-only.md).
- Evaluated ponytail: corrected an earlier wrong claim that it "competes"
  with `caveman` — it doesn't, it's complementary (ponytail governs code
  generation, caveman governs prose). Vendored `ponytail` + `ponytail-debt`;
  skipped `ponytail-review`/`ponytail-audit` (redundant with existing
  `code-review`/`simplify`) and `ponytail-gain`/`ponytail-help` (low value).
- Reviewed but did NOT vendor: `continual-learning` hook (SQLite
  learning-capture, built for GitHub Copilot CLI's hook format not Claude
  Code's) and `git-guardrails-claude-code` (a real, ready-to-adapt Claude
  Code `PreToolUse` hook — needs adapting from blanket-block-all-push to
  main-only, scope not yet decided). Both documented in `hooks/README.md`.

## What Goal 3 has landed so far

- `project-memory-template` scaffold (see above).
- Fixed real skill-distribution bugs: the README's single library-level
  symlink instruction never actually worked (Claude Code discovers skills
  one level deep only); found and fixed genuine drift between
  `~/.claude/skills/` live copies and this repo's vendored copies
  (`fantasy-football-python`'s live version was more current;
  `grill-with-docs`'s live version was stale) — merged.
- Confirmed via VS Code's own docs that `.claude/skills/` is natively
  shared across Claude Code CLI, the VS Code extension, and VS Code's
  Agents-window Skills panel (the `agentskills.io` open standard) — no
  separate distribution mechanism needed for that surface.
- Shipped the skill-stage/domain routing map (merged) — all 34 skills
  cross-cut by Plan/Crystallize/Execute + domain.
- Relocated `common/` → `skills/_powerbi-authoring-common/` (aimless at
  repo root, only used by the powerbi-authoring family; nested inside
  `skills/` over `plugins/` for shorter, more reliably-resolved relative
  paths — reasoning in the merge commit, not a separate ADR).
- Retrofitted this repo's own memory architecture (`CLAUDE.md`, `PLAN.md`,
  `.claude/memory/`, 4 ADRs) — merged.
- Merged all of the above (4 PRs total, 2 repos) — verified `main` on both
  repos actually carries the content, not just open PRs claiming it does.
- Ran a `two-axis-code-review` pass (Standards + Spec) against both this
  repo and `project-memory-template`'s shipped work — found and fixed 3
  real issues in `project-memory-template` (broken ADR-template link,
  missing organizational-pattern guidance, undocumented CLAUDE.md
  sync-maintenance burden); this repo came back clean.
- Grilled and agreed the design for a regression-testing standard
  (Dynasty-facing: pytest + pre-commit + `check_sources.py`), including a
  real evaluation (via `/ponytail`) of whether a custom hook/subagent
  pre-PR gate could substitute for CI — concluded CI is architecturally
  correct and a custom gate would be strictly weaker, see
  [ADR-0004](../../docs/adr/0004-ci-over-local-pr-hook.md).
- Retrofitted this repo's own memory architecture (this file and its
  siblings) — the harness-tier store was carrying real, growing project
  state and decision-density past what a scratch store should hold; this
  is that Phase 0 consolidation.

## Goal 3 remaining slate, re-sequenced 2026-07-11

Original order put regression-testing next; user re-sequenced after
catching that `.claude/memory`/`docs/adr` were still empty on `main` (every
PR was open, none merged) and that `continual-learning` had silently
dropped off tracking. Stance: **this repo needs to be fully trustworthy on
its own before being used as the pattern elsewhere** — "I need to be able
to trust it elsewhere and we are not there yet."

1. ~~Skill distribution beyond manual symlink~~ — done, merged.
2. ~~Skill-stage/domain routing map~~ — done, merged.
3. ~~This repo's own memory architecture + `common/` relocation~~ — done,
   merged (all 4 PRs: #6, #8, #9 here; #2 on `project-memory-template`).
4. ~~`continual-learning` hook port~~ — built and merged, PR #11
   (`hooks/continual-learning/`: `learn.sh`, `settings-snippet.json`,
   README). **Not yet activated**: `sqlite3`/`jq` aren't on `PATH` in this
   machine's Git Bash, so the hook would no-op if installed as-is.
   Deliberately left as an open gate rather than silently installed —
   which binaries, how (winget/choco/manual), and whether `jq` is
   optional long-term all still need a real decision. See `PLAN.md`.
5. ~~Git guardrail hook~~ — built, merged (PR #13), **activated** on this
   machine. Branch-aware `git push` guard (blocks `main`/`master` targets
   only, allows feature branches) + upstream's blanket-blocked destructive
   patterns kept as-is; global-scope install, registered in
   `~/.claude/settings.json`'s `hooks.PreToolUse`. No `jq` dependency, so
   unlike `continual-learning` this one isn't gated on a missing binary —
   it's live from the next session on. See `PLAN.md` for the test matrix
   it was verified against, pre- and post-install.
6. **Check-in hygiene hook** — flags empty/stale scaffold files + README
   staleness.
7. **Regression-testing standard** — moved to *last*, not because the
   design is stale (it's fully grilled and agreed — see `PLAN.md`) but
   because the user wants this repo's own tooling proven out first.
8. **`update-vendor-skills.ipynb` rework** — drift detection, fork-handling
   automation, `plugin_manifests_only[]` awareness.

## How to apply

Re-read the repo root `README.md` Roadmap section for the current/live
state — this file is a snapshot as of 2026-07-11. Root
`memory-architecture.md` describes the Phase 0 algorithm this file's own
creation is an instance of.
