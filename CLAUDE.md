# CLAUDE.md

Project: central repository for Claude Code skills, plugins, and hooks —
`benjamininja/skills-plugins-hooks-agents`. Every skill lives at a flat, loadable
path (`skills/<name>/SKILL.md`); some are authored here, most are vendored
from upstream projects and credited in `README.md`. This is the source of
truth other repos symlink/junction from — see `README.md`'s Installation
section.

> **Always read overarching developer preferences from
> `C:\Users\benha\.claude\memory\preferences.md` before generating code.**

## Memory layout

- **`.claude/memory/` (this repo, project-specific)**:
  - [MEMORY.md](.claude/memory/MEMORY.md) — index of project state
  - [program-status.md](.claude/memory/program-status.md) — the 3-goal
    restructure/saturation program: what's shipped, what's next
- **`C:\Users\benha\.claude\memory\` (global, cross-project)**:
  - `preferences.md` — working style, cross-project git/workflow rules
  - `MEMORY.md` — index across all of Ben's projects

No `CONTEXT.md` here — this repo's own `README.md` (Conventions, Repository
Structure, Sources & Credits sections) already serves as the glossary for a
skills-catalog repo; a separate glossary would duplicate it rather than add
to it.

## Project-wide rules

- **Provenance tracking**: `vendor-skills.json` is the source of truth for
  every vendored skill's upstream repo/branch/commit/source path —
  `skills[]` for faithful vendors, `forks[]` for skills that deliberately
  diverged (see [ADR-0001](docs/adr/0001-vendor-cache-fork-pattern.md)),
  `plugin_manifests_only[]` for cataloged-but-not-vendored bundles (see
  [ADR-0002](docs/adr/0002-plugin-manifests-only.md)). `manifest.json`
  tracks *membership* (what's in this repo) separately from provenance.
- **One skill per folder** under `skills/`, named for the skill, with a
  `SKILL.md` at its root carrying `name` + `description` frontmatter (with a
  trigger hint in the description).
- **Installation is per-skill links, not a single library symlink** —
  Claude Code discovers skills one level deep only. See
  [ADR-0003](docs/adr/0003-junction-vs-symlink-fallback.md) for the
  symlink/junction distinction and why junctions are the practical default
  on this machine.
- **No CI, and no local hook standing in for one, today** — see
  [ADR-0004](docs/adr/0004-ci-over-local-pr-hook.md): CI is the correct
  enforcement layer for "tests must pass before merge," a local hook is a
  legitimate complement to it but not a substitute. This repo does run one
  local `pre-commit` hook, `check-in-hygiene` (from `project-memory-template`,
  scoped to `.claude/memory/`/`CLAUDE.md`/`docs/adr/` hygiene) — a
  different concern ADR-0004 doesn't cover. Setup: `pip install pre-commit`,
  then `pre-commit install`.

## Git

Feature branch → `main` via PR. Never commit or push directly to `main`,
even solo, even for "just documentation" (violated once, 2026-07-11 — see
root `preferences.md`'s Git & Version Control section for the incident and
why it matters). Commit only when asked.
