---
name: setup-project-memory
description: Fully wire a brand-new (or partially-wired) project — memory scaffold, engineering-skills config, and pre-commit hooks — in one pass instead of three separate manual steps.
disable-model-invocation: true
---

# Setup Project Memory

Orchestrates the three mechanisms that together make a project "fully
wired," none of which currently call each other:

1. **Memory scaffold** — a `project-memory-template` tier
   (minimal/standard/full) copied and filled in for this repo.
2. **Engineering-skills config** — `setup-matt-pocock-skills`' issue
   tracker / triage labels / domain-doc layout.
3. **Pre-commit hooks** — `check-in-hygiene` (from `project-memory-template`)
   wired into this repo's `.pre-commit-config.yaml`, installed and active.

See [ADR-0005](../../docs/adr/0005-skill-routing-and-drift-detection.md)
for why this exists: three uncoordinated manual steps meant even the most
mature real example (`Python-PowerBI-DynastyFantasyFootball`) shipped a
`.pre-commit-config.yaml` that nothing ever activated.

This is a prompt-driven skill, not a deterministic script — explore,
present what's missing, confirm with the user, then write/run.

## Process

### 0. Precondition check

Before anything else, check whether the machine-wide skill-junction
install is healthy — `skill-catalog-health`'s `SessionStart` output (if
that hook is installed) will have already flagged any broken links this
session. If it reported broken links, or the hook isn't installed at all,
stop and resolve that first (relink per the skill-source repo's README
Installation section) — the rest of this flow depends on
`setup-matt-pocock-skills` and other engineering skills actually being
reachable.

### 1. Explore

Look at the current repo to understand its starting state — read
whatever exists, don't assume:

- `CLAUDE.md` / `AGENTS.md`, `PLAN.md`, `.claude/memory/`, `docs/adr/` —
  does a memory scaffold already exist, and which tier does it resemble?
- `docs/agents/issue-tracker.md` — has `setup-matt-pocock-skills` already
  run here?
- `.pre-commit-config.yaml` — does it exist? Does it already reference
  `check-in-hygiene`? Is `.git/hooks/pre-commit` actually installed
  (`pre-commit install`, not just the config file existing — this is
  exactly the gap Dynasty had)?
- The project's dependency manifest (`requirements.txt`, `pyproject.toml`,
  `package.json`, etc.) — is there an established convention to add
  `pre-commit` to, or does none exist yet (e.g. a docs/skills-only repo)?
- Is this repo itself `project-memory-template` or
  `skills-plugins-hooks-agents`? If so, stop and say why this skill
  doesn't apply (the former is the scaffold source, not a consumer; the
  latter's own bootstrap is documented directly in its `CLAUDE.md`).

### 2. Present findings and ask, one section at a time

Skip a section entirely when exploration already found it done.

**Section A — Memory tier.** If no scaffold exists, recommend a tier per
`project-memory-template/docs/graduating-tiers.md`'s own guidance (default
**minimal** for a new/small repo, **standard** or **full** only if the
repo already shows real decision-density — multiple contributors, an
existing `docs/adr/`, etc.). Copy the chosen tier's files from
`project-memory-template/tiers/<tier>/` into this repo, filling in the
bracketed placeholders from what you learned in Explore rather than
leaving them for `check-in-hygiene` to catch — that hook exists as a
safety net, not as this skill's editor.

**Section B — Engineering-skills config.** If `docs/agents/issue-tracker.md`
doesn't exist, run `setup-matt-pocock-skills` now (don't duplicate its
logic — invoke it as a sub-step and let it own its own explore/ask/write
loop).

**Section C — Pre-commit.** If `.pre-commit-config.yaml` doesn't exist or
doesn't reference `check-in-hygiene`:

1. Look up `project-memory-template`'s current `main` commit SHA (`git
   ls-remote https://github.com/benjamininja/project-memory-template main`)
   — pin `rev` to that, not a hardcoded value that will drift.
2. Add or extend `.pre-commit-config.yaml`:
   ```yaml
   repos:
     - repo: https://github.com/benjamininja/project-memory-template
       rev: <sha from step 1>
       hooks:
         - id: check-in-hygiene
   ```
3. Add `pre-commit` to the project's dependency manifest if one exists
   (matching its existing pin-looseness convention — don't over-pin); if
   the repo has no Python/Node tooling at all, note that `pre-commit`
   needs a global `pip install pre-commit` instead (same situation
   `skills-plugins-hooks-agents` itself was in).
4. Run the install: `pip install pre-commit` (or the project's own venv
   equivalent) then `pre-commit install`.
5. Verify: `pre-commit run --all-files` — confirm it actually passes (or
   fails for a real, expected reason) rather than silently no-op'ing.

### 3. Confirm and write

Show the user what will change before writing — new files, the
`.pre-commit-config.yaml` diff, and which commands will run. Let them
edit before proceeding. Never skip the verify step in Section C.3 —
"the config file exists" is not the done-condition, "a real commit
exercises the hook" is (see ADR-0005's own context for why that
distinction matters).

### 4. Done

Report what's now wired and what (if anything) was already in place and
left untouched. If `setup-matt-pocock-skills` wrote an `## Agent skills`
block, mention it's there. Re-running this skill later is safe — each
section skips itself when it finds its own precondition already met.
