# Memory Index — skills-plugins-hooks-agents (project)

> Project-local memory. Cross-project preferences, terminology, and working
> method live in root (`C:\Users\benha\.claude\`). Consolidated 2026-07-11
> from the harness-tier scratch store (`~/.claude/projects/c--Users-benha-
> OneDrive-Documents-GitHub-skills/memory/`), which now holds only a
> redirect — this file and root are the authoritative copies going forward.

## Active Files

- [Program status](program-status.md) — the 3-goal restructure/saturation
  program: what's shipped across all three goals, what's next, sequencing
  rationale

## Decisions (ADRs)

- `docs/adr/0001-vendor-cache-fork-pattern.md` — pristine-mirror fork
  pattern for skills that must diverge from a faithful vendor copy
- `docs/adr/0002-plugin-manifests-only.md` — manifest-only cataloging for
  large upstream plugin bundles with mostly-unused content
- `docs/adr/0003-junction-vs-symlink-fallback.md` — directory junctions as
  the practical install mechanism when symlinks need elevation
- `docs/adr/0004-ci-over-local-pr-hook.md` — why a server-side CI gate
  beats a client-side pre-PR hook for "tests must pass before merge"
