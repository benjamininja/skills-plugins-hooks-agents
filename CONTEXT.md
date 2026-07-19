# skills-plugins-hooks-agents

The central tools repo: first-party skills, plugins, hooks, and agents,
vendored third-party skills, and (as of ADR-0011) the machinery that
distributes these artifacts to other repos on this machine and detects
when those repos have drifted from or extended what's here.

## Language

**Artifact**:
Any one of the four distributable unit types this repo produces: a skill,
plugin, hook, or agent.
_Avoid_: Tool (too easily confused with `tools/*.py`, the scripts that
manage artifacts, not the artifacts themselves)

**Central repo**:
This repo (`skills-plugins-hooks-agents`), when discussed in its role as
the single source of truth that artifacts distribute *from* and check in
*to*. Distinguishes it from a **downstream repo**.
_Avoid_: Upstream repo (correct in the vendoring direction — see
Vendoring vs. Distribution below — but ambiguous here since this repo is
simultaneously "upstream" of downstream repos and "downstream" of the
external sources it vendors skills from)

**Downstream repo**:
Any other repo on this machine that consumes artifacts distributed from
the central repo (e.g. `project-memory-template`,
`Python-PowerBI-DynastyFantasyFootball`).

**Vendoring vs. Distribution**:
Two distinct, opposite-direction drift problems that must not be
conflated:
- **Vendoring** = external upstream (e.g. `anthropics/claude-code`) →
  this repo. Tracked in `vendor-skills.json`, managed by
  `tools/update_vendor_skills.py`.
- **Distribution** = this repo → downstream repos, plus downstream local
  changes flowing back. Tracked in `distribution-registry.json`, managed
  by `tools/manage_distribution.py` (ADR-0011).

**Junction-linked artifact**:
A skill, agent, or hook whose file(s) live physically in the central
repo and are made to appear in a downstream repo (or `~/.claude/`) via a
directory junction or file symlink (ADR-0003's mechanism), rather than a
copy. Editing the file anywhere edits the one physical file everywhere
it's linked.
_Avoid_: Installed skill/agent/hook (doesn't distinguish link from copy)

**Broken junction**:
A junction-linked artifact whose link has been replaced by a standalone
copy downstream (accidentally or deliberately), so it no longer receives
central's live edits. One of the two upstream check-in detection cases
(ADR-0011).

**Downstream-built artifact**:
A wholly new skill/plugin/hook/agent created inside a downstream repo
that was never linked from central. The other upstream check-in
detection case (ADR-0011) — distinct from a broken junction, since there
was never a link to break.

**Blessed divergence**:
A downstream-built artifact or broken junction that the user has
reviewed and decided to leave as-is (not pull into central, not
auto-repair) via `manage_distribution.py --bless`. Mirrors
`vendor-skills.json`'s `known_local_edits[]` concept, applied to the
opposite direction.

**Project-scoped plugin**:
A plugin enabled via a specific downstream repo's own
`.claude/settings.json` (`enabledPlugins`/`extraKnownMarketplaces`),
rather than globally in `~/.claude/settings.json`. Lets one plugin be
distributed to some downstream repos and not others — the mechanism
plugins use in place of junctions, since plugins aren't a file tree.
