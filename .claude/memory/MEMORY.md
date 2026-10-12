# Memory Index — skills-plugins-hooks-agents (project)

> Project-local memory. Cross-project preferences, terminology, and working
> method live in root (`C:\Users\benha\.claude\`). Consolidated 2026-07-11
> from the harness-tier scratch store (`~/.claude/projects/c--Users-benha-
> OneDrive-Documents-GitHub-skills/memory/`), which now holds only a
> redirect — this file and root are the authoritative copies going forward.

## Active Files

- [Program status](program-status.md) — the 3-goal restructure/saturation
  program, all shipped; pointer file to PLAN.md/README/ADRs + one open
  question (agents catalog directory)

## Related decision records elsewhere

- `vendor-skills.json` `known_local_edits` entries — the three-state
  vendor ontology's per-skill annotations (grilled 2026-07-12, design in
  PR #25 body and README "Maintaining vendored skills")
- Dynasty `docs/adr/0009-first-subagent-roster.md` — first subagent
  roster + rejected-candidates record (the former open `agents/`
  directory question — resolved by ADR-0011's revision: one junction)
- `benjamininja/dotclaude` — versioned root tier; RESTORE.md documents
  new-machine bootstrap order

## Decisions (ADRs)

- `docs/adr/0001-vendor-cache-fork-pattern.md` — pristine-mirror fork
  pattern for skills that must diverge from a faithful vendor copy
- `docs/adr/0002-plugin-manifests-only.md` — manifest-only cataloging for
  large upstream plugin bundles with mostly-unused content
- `docs/adr/0003-junction-vs-symlink-fallback.md` — directory junctions as
  the practical install mechanism when symlinks need elevation
- `docs/adr/0004-ci-over-local-pr-hook.md` — why a server-side CI gate
  beats a client-side pre-PR hook for "tests must pass before merge"
- `docs/adr/0005-skill-routing-and-drift-detection.md` — router-skill
  nudge-not-auto-invoke design, junction drift detection; status now notes
  partial supersession by ADR-0006
- `docs/adr/0006-blast-radius-tiered-model-invocation.md` — flips
  `disable-model-invocation` off for 5 skills (`grill-me`,
  `grill-with-docs`, `teach`, `writing-great-skills`, `ask-matt`) whose
  worst-case wrong-trigger is conversation/local-file-write only; `triage`
  and `wayfinder` stay manual (external issue-tracker writes)
- `docs/adr/0007-first-subagents-vendor-sync-and-safety-audit.md` — first
  `.claude/agents/` roster in this repo: `vendor-sync-reapply` (background)
  and `skill-safety-auditor` (foreground), both born from gaps found while
  executing ADR-0006 in the same session
- `docs/adr/0008-plan-gate-sync-auditor.md` — **superseded 2026-10-12, agent
  retired** (tiers no longer restate the plan gate). History: third agent, homed here
  despite auditing `project-memory-template`'s tier CLAUDE.md files against
  the private `dotclaude` root — chosen over homing it in either of those
  repos since this repo is the one every project already junction-installs
  from
- `docs/adr/0009-security-review-at-pr-time.md` — `/security-review`
  (Claude Code's built-in skill, not a repo file) required before opening
  a PR in both this repo and `project-memory-template`'s three tiers;
  extends ADR-0004's CI-vs-agent-in-the-loop boundary to a new case
- `docs/adr/0010-root-memory-propagation-audit.md` — fourth agent,
  `root-memory-propagation-auditor` (background), paired with a new
  `hooks/root-memory-propagation/` nudge hook: sweeps known downstream
  repos for stale copies of root-memory content after it changes, judging
  genuine duplicates apart from coincidental text matches
- `docs/adr/0011-unified-distribution-architecture.md` — **under revision
  2026-10-12**: original design (registry + `tools/manage_distribution.py`,
  all 4 artifact types) is deferred history. Current scope: agents + hooks
  only, via ADR-0003 directory junctions (`~/.claude/agents` and
  `~/.claude/hooks/<name>`); registry/CLI/check-in wait for observed
  drift; native plugin marketplace evaluated, not adopted. `CONTEXT.md`'s
  distribution terms match the rescope.
  **Revision 2 (2026-10-12)**: all `~/.claude` links point at a live clone
  pinned to `main` (`C:\Users\benha\claude-live\skills-plugins-hooks-agents`),
  created by `tools/relink_live.ps1`; pull it after every merge. Reason: an
  uncommitted 2026-08-02 re-vendor in the working checkout was live for ten
  weeks with four skills' `disable-model-invocation` wrongly restored.
- `docs/adr/0012-retire-continual-learning.md` — hook removed: its only
  output was "tool X frequently fails", injected every session
- `docs/adr/0013-session-dispatch-plugin.md` — plugin
  `plugins/session-dispatch-managers-build-review/`: a dry-run-first
  script that starts a builder session at a tier, with the permission
  mode fixed in the script and one owner-only config file; two skills
  split by ADR-0006 (`session-rules` loadable, `session-dispatch`
  manual only); templates. First skills that live inside a plugin
- **Agents are wired, three remain** (`vendor-sync-reapply`,
  `skill-safety-auditor`, `root-memory-propagation-auditor`): real `model:`
  aliases, the vendor tool's reapply notice names them, `CLAUDE.md` has an
  "Agents — when to run" section. They had 0 runs before 2026-10-12 because
  two could not parse and nothing triggered the others.
