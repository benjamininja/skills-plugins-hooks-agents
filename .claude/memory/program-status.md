# Program status — 3-goal restructure/saturation program

Three-goal program, planned 2026-07-11 — **all three shipped and merged**:

1. Rename `skills` repo → `skills-plugins-hooks`, add `plugins/`/`hooks/`
   scaffolding.
2. Saturate the repo (ponytail scan + Matt Pocock skill-gap integration) —
   PR #4.
3. Synthesize `project-memory-template` from `Python-PowerBI-
   DynastyFantasyFootball`'s memory architecture (public repo
   `benjamininja/project-memory-template`: tiered minimal/standard/full,
   regression-testing standard, `check-in-hygiene` hook).

**Why:** a reusable, complexity-scaled memory-architecture template plus
tooling, informed by aligning with Matt Pocock's skill ecosystem and an
existing working example (the Dynasty repo).

**Stance that drove sequencing:** this repo needs to be fully trustworthy
on its own before being used as the pattern elsewhere — "I need to be able
to trust it elsewhere and we are not there yet."

## Where the detail lives (do not re-expand it here)

- What shipped, per goal and per session: `PLAN.md` Shipped section.
- Skill catalog, sources, vendoring + three-state drift ontology
  (faithful / vendored-with-known-edits / fork): `README.md`.
- Decisions: `docs/adr/` (indexed in `MEMORY.md`).

## Open question

- Whether this repo grows an `agents/` catalog directory — as of
  ADR-0011's 2026-10-12 revision, agents are distributed by one directory
  junction (`~/.claude/agents` → `.claude/agents`), so a separate catalog
  directory is not needed for distribution.

## How to apply

Re-read `README.md`'s Roadmap and `PLAN.md`'s Shipped section for current
state. Root `memory-architecture.md` describes the Phase 0 algorithm this
file's creation is an instance of.