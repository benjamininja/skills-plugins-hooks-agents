# Unified bidirectional distribution architecture (skills, plugins, hooks, agents)

- Status: accepted (design only — no implementation yet)
- Date: 2026-07-18
- Scope: repo-wide; introduces `distribution-registry.json`,
  `tools/manage_distribution.py`, and a junction-based install path for
  agents and hooks (generalizing ADR-0003's skill mechanism)

## Context

This repo distributes skills to `~/.claude/skills/` and downstream repos
via directory junctions (ADR-0003). Plugins, hooks, and agents have no
distribution mechanism at all — `root-memory-propagation-auditor`
(ADR-0010), built this session, is only invokable from a session rooted
in this exact repo, with no way to reach it from
`Python-PowerBI-DynastyFantasyFootball` or any other downstream repo.

Separately, nothing detects the reverse: a downstream repo building its
own new artifact, or a downstream copy diverging from what central last
shipped, has no path back to this repo's attention. `vendor-skills.json`
and `tools/update_vendor_skills.py` already solve a structurally similar
problem — but for the opposite direction (external upstream → this repo).
That shape (a registry file + `--check`/`--bless`/`--apply` verbs) is
reused here, not the direction.

Resolved via a `/grill-with-docs` session (`grilling` + `domain-modeling`)
on 2026-07-18. See `CONTEXT.md` for the terms coined during that session
(artifact, central/downstream repo, junction-linked artifact, broken
junction, downstream-built artifact, blessed divergence, project-scoped
plugin).

## Decision

**Scope**: all four artifact types (skills, plugins, hooks, agents),
bidirectional (distribution + check-in). Plugins are in scope despite
`plugins/` being nearly empty today (manifest-only cataloging per
ADR-0002) — a concrete near-term case exists:
`frontend-design@claude-plugins-official` enabled in both this repo and
`Python-PowerBI-DynastyFantasyFootball`.

**One unified registry, `distribution-registry.json`** (repo root, sibling
to `vendor-skills.json` — not merged with it, since it tracks the opposite
direction). Top-level keys per artifact type; each holds a list of
`{artifact name, downstream repos linked into, link path, status}`.

**One CLI tool, `tools/manage_distribution.py`**, verb set
`--check`/`--bless`/`--apply` (mirrors `update_vendor_skills.py`):
- `--apply` installs or repairs the artifact in a downstream repo —
  junction for skills/agents/hooks, `.claude/settings.json` entry merge
  for plugins.
- `--check` scans registered downstream repos for two kinds of drift:
  distribution drift (a downstream repo missing an artifact or entry it
  should have) and upstream check-in candidates (see below). On-demand
  only — no background subagent or auto-triggering hook for this first
  version, matching how `update_vendor_skills.py` is invoked today.
- `--bless` marks a downstream divergence as intentional, so `--check`
  stops flagging it. Mirrors `known_local_edits[]`.

**Mechanism per type**:
- **Skills**: unchanged — ADR-0003's junction, now also reachable from
  the unified tool.
- **Agents**: junction each `.md` file individually into the downstream
  repo's (or `~/.claude/`'s) `.claude/agents/`, live-updating like skills.
- **Hooks**: junction the script file itself (replacing the current
  copy-and-manually-re-copy pattern); the `settings.json` hook
  registration (matcher + command path) still requires an explicit merge
  step, since a JSON object entry can't be symlinked.
- **Plugins**: project-scoped. `--apply` merges `enabledPlugins`/
  `extraKnownMarketplaces` entries into the downstream repo's own
  `.claude/settings.json`, tracked per-repo in the registry. Rejected a
  global-only `~/.claude/settings.json` entry: it can't express "this
  plugin belongs in these 2 repos, not the other N," which the
  `frontend-design` test case requires.

**Upstream check-in detects two distinct cases**, both surfaced by
`--check`:
1. **Downstream-built artifact** — a skill/plugin/hook/agent that exists
   in a downstream repo but isn't in the registry at all (no junction was
   ever established).
2. **Broken junction** — a registry-tracked link whose downstream path is
   no longer actually a junction (replaced by a standalone copy,
   accidentally or deliberately), so it's stopped receiving central's
   live edits.

Neither case auto-resolves. `--check` reports; the user decides whether
to `--apply` (pull the downstream artifact into central, or re-link a
broken junction) or `--bless` (leave it diverged on purpose).

**`root-memory-propagation` (ADR-0010) stays separate**, not absorbed
into this registry — it tracks prose/memory content drift via text-diff-
and-judge, a different domain from link/copy-and-new-artifact-detection.
The two systems may share the *concept* of a downstream-repo list without
sharing a schema.

## Alternatives rejected

- **Scope skills+hooks+agents only, defer plugins** — rejected during
  grilling; the user explicitly wants plugin distribution in scope now,
  citing both the `fabric-collection` plugins and a concrete near-term
  need (`frontend-design@claude-plugins-official` in two repos).
- **Four separate per-type registries** — rejected in favor of one file
  with per-type top-level keys; keeps "one unified registry" literal
  rather than four registries that happen to share a verb set.
- **Fold `known-downstream-repos.json` (ADR-0010) into this registry** —
  rejected; different schema needs (text-diff vs. link/copy tracking)
  would force one system's model onto the other for no real gain today.
- **Background subagent or auto-triggering hook for check-in detection**
  — rejected for this first version; adds judgment-agent and
  hook-distribution overhead before the underlying CLI mechanics even
  exist. Revisit once `manage_distribution.py --check` has real mileage,
  the same maturation path `update_vendor_skills.py` already took before
  anything was layered on top of it.
- **Global-only plugin enablement** (`~/.claude/settings.json` only) —
  rejected; can't express per-repo plugin membership, which the
  `frontend-design` test case requires.

## Consequences

- Hooks' distribution model changes (copy → junction for the script
  file); existing installed copies (e.g.
  `~/.claude/hooks/root-memory-propagation/nudge.sh`,
  `~/.claude/hooks/git-guardrails/`) will need migrating to junctions
  when `manage_distribution.py --apply` is built and run — not done by
  this ADR, which is design-only.
- Agents gain their first distribution path at all; until
  `manage_distribution.py` exists, `root-memory-propagation-auditor` and
  the other three agents remain invokable only from a session rooted in
  this repo.
- `distribution-registry.json` starts empty (or seeded with the
  `frontend-design` test case) — this ADR does not populate it.
- Implementation (the tool, the registry file, the junction migration) is
  follow-up work, not part of this ADR.
