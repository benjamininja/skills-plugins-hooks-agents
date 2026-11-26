# skills-plugins-hooks-agents

The central tools repo: first-party skills, plugins, hooks, and agents,
vendored third-party skills. Skills, agents, and hooks are distributed to
`~/.claude/` and other repos on this machine via ADR-0003 directory
junctions (scope per ADR-0011's 2026-10-12 revision); drift detection and
check-in tooling are deferred until drift is observed.

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
- **Distribution** = this repo → downstream repos (and `~/.claude/`),
  by directory junction (ADR-0003). A registry and `--check`/`--bless`
  tooling (`distribution-registry.json`, `tools/manage_distribution.py`)
  were designed but are deferred — ADR-0011 revision.

**Junction-linked artifact**:
A skill, agent, or hook whose file(s) live physically in the central
repo and are made to appear in a downstream repo (or `~/.claude/`) via a
directory junction (ADR-0003's mechanism), rather than a copy. Editing
the file anywhere edits the one physical file everywhere it's linked.
_Avoid_: Installed skill/agent/hook (doesn't distinguish link from copy)

**Directory-level junction**:
The actual unit of linking: one junction per folder (a skill folder,
`.claude/agents/`, or a hook's `hooks/<name>/`). Junctions cannot link a
single file, so "junction each agent `.md`" is not possible; agents share
one junction `~/.claude/agents` → `<repo>\.claude\agents`.

> The four terms below name detection/tooling that is **deferred**
> (ADR-0011 revision, 2026-10-12) — kept as vocabulary, not built.

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
auto-repair) via a future `--bless` verb. Mirrors
`vendor-skills.json`'s `known_local_edits[]` concept, applied to the
opposite direction.

**Project-scoped plugin**:
A plugin enabled via a specific downstream repo's own
`.claude/settings.json` (`enabledPlugins`/`extraKnownMarketplaces`),
rather than globally in `~/.claude/settings.json`. Lets one plugin be
distributed to some downstream repos and not others — the mechanism
plugins use in place of junctions, since plugins aren't a file tree.

## Trust and reach

The words of the threat model for role sessions (ADR-0018).

**Misled session**:
A session that acts on text it should have read as data.
_Avoid_: Compromised session, rogue agent

**Mistaken session**:
A session that is honest and wrong.

**Approval**:
The owner's own decision, in the owner's own words in a session's chat
or as an answer the owner gave from the queue pane.
_Avoid_: Sign-off, go-ahead (a recorded go is record text, not approval)

**Record text**:
Text the owner's GitHub login wrote and last edited on a ticket or a PR,
or a committed rule file on `main`. A session may act on it inside its
role; it never approves anything.
_Avoid_: Instruction, trusted text

**Data** (of text):
Any text that is neither approval nor record text. A session reads and
reports it, and takes no instruction from it.
_Avoid_: Untrusted input

**Limit**:
A restriction enforced outside a session's own process and judgement: by
GitHub's servers, by the operating system, or by the thing not being in
reach.
_Avoid_: Hard stop, control

**Guard**:
A restriction the session's own host or judgement applies: a deny rule,
a hook, rule text, the two-key merge. A first line, never a limit.
_Avoid_: Limit, protection

**Accepted risk**:
A high-impact asset with no limit, recorded as such in the owner's name
with its rating.

**Actor**:
The identity GitHub attributes an action to: the owner's login, the
builders' App, or a project's pipeline App.
_Avoid_: User, account (an App is neither)
