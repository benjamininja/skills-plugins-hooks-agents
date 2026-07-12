# Skill routing nudges, junction drift detection, and a full-repo bootstrap skill

- Status: accepted
- Date: 2026-07-12
- Scope: `hooks/skill-catalog-health/`, `skills/setup-project-memory/`,
  `skills/ask-matt/SKILL.md`, `project-memory-template`

## Context

Two real, related gaps surfaced in the same session:

1. **Router skills go unused because nothing surfaces them.** Pocock's
   flow-entry skills (`ask-matt`, `wayfinder`, `to-spec`, `triage`, etc.)
   are deliberately `disable-model-invocation: true` — the model shouldn't
   silently decide to kick off a multi-session flow on its own. But that
   means their existence is only ever recalled if a human remembers to type
   `/ask-matt`. There was no mechanism making that routing knowledge
   ambient.
2. **Every skill junction on this machine was broken.** `~/.claude/skills/`
   symlinks/junctions all pointed at `C:\...\GitHub\skills\skills\<name>` —
   this repo's name *before* the Goal-1 rename to `skills-plugins-hooks`,
   let alone today's rename to `skills-plugins-hooks-agents`. The repo's
   own README already documented this exact failure mode ("Junction
   caveat": renaming the folder breaks every link silently) — and it had
   already happened, undetected, for weeks. No tactical Pocock skill
   (`tdd`, `diagnosing-bugs`, etc.) was reachable this entire time.
3. **No single step wires a brand-new project up completely.** Three
   separate mechanisms exist — the machine-wide skill-junction install
   (this repo's README), `setup-matt-pocock-skills` (per-repo issue
   tracker/triage/domain-doc config), and per-repo `pre-commit install` +
   `check-in-hygiene` adoption — and none of them call each other. Dynasty,
   the most mature real example, proved this gets missed even when the
   rest is done right (ADR context: `pre-commit install` was never run
   despite `.pre-commit-config.yaml` existing since ADR-0008).

## Decision

### 1. Nudge, don't auto-invoke, for router skills

A new hook, `hooks/skill-catalog-health/`, injects a **compact routing
index** into context at `SessionStart` — one line per installed skill
(name + trigger condition), split User-invoked / Model-invoked, mirroring
the format upstream `mattpocock/skills`' own `README.md` Reference section
already uses (not invented here — matched to existing precedent).
Generated at runtime from each skill's frontmatter `description`, not
hand-maintained, so it can't drift out of sync the way the junction
targets did.

This does **not** change `disable-model-invocation` on any router skill —
the model sees the index and can raise "this looks like `/wayfinder`
territory" as a suggestion, same as a human noticing, but the user still
decides. Preserves Pocock's original safety reasoning while solving "I
didn't know that skill existed for this."

### 2. Detect and report, don't auto-repair, broken junctions

The same hook checks every `~/.claude/skills/*` entry for brokenness
(`-L` but not `-e`) and injects the list of broken links into context if
any exist, rather than silently guessing at a repair. Auto-repair would
need to locate the repo's new path, and a wrong guess (e.g. two
similarly-shaped folders) would silently link to the wrong content —
worse than a loud, visible break. Surfacing it into the agent's context
achieves the same practical outcome (the agent notices and flags it, as
happened manually this session) without that risk.

### 3. `setup-project-memory`: one skill, full bootstrap, manual-invoke

Expands `project-memory-template`'s own previously-deferred idea (a
`setup-project-memory`-style skill, README-noted but never built) beyond
"generate the memory files" to the full bootstrap: verify the skill-
junction install, apply the chosen tier scaffold, invoke
`setup-matt-pocock-skills`, wire and install `pre-commit` +
`check-in-hygiene`. One invocation, one done-condition ("this project is
fully wired"), rather than three uncoordinated manual steps.

Lives in `skills-plugins-hooks-agents/skills/` (this repo — the existing
single source of truth every machine junction-installs from), not in
`project-memory-template`, even though its content is authored there for a
different repo. This keeps the "one canonical skill-source repo" property
intact rather than teaching the install script to scan two sources. It
reads tier content from `project-memory-template` the same way this repo's
skills already read PowerBI/Fabric content from elsewhere — a normal
cross-repo read, not new coupling.

`disable-model-invocation: true` — matches `setup-matt-pocock-skills`'
own precedent. A once-per-repo, file-writing, install-running action is
high-consequence enough that the model shouldn't decide to run it
unprompted; the routing index from decision 1 makes sure it gets
suggested when relevant instead.

## Alternatives rejected

- **Auto-invocation for router skills** — overrides Pocock's own stated
  reasoning for the `disable-model-invocation` split; rejected without
  a concrete failure that reasoning doesn't already cover.
- **Keyword-matching `UserPromptSubmit` hook** instead of `SessionStart`
  routing-index injection — more precise timing in theory, but requires
  building and tuning a trigger-phrase list per skill with real
  false-positive/negative risk, duplicating logic the skill descriptions
  already encode. Rejected in favor of reusing that existing text.
- **Auto-repair of broken junctions** — rejected; see decision 2.
- **`setup-project-memory` authored in `project-memory-template`, with the
  install script scanning two source repos** — rejected; breaks the
  single-source-of-truth property `skills-plugins-hooks-agents`'s own
  `CLAUDE.md` already asserts.
- **`setup-project-memory` as model-invocable** — rejected; matches
  `setup-matt-pocock-skills`' existing manual-only precedent for the same
  consequence-level reasoning.

## Consequences

- Router-skill discoverability no longer depends on a human remembering
  `/ask-matt` exists.
- A repo-folder rename can no longer silently strand every tactical skill
  for weeks the way it just did — the next `SessionStart` after a broken
  rename surfaces it.
- New-project setup becomes one invocation instead of three manual,
  easy-to-skip steps.
- New maintenance surface: the routing-index generator must stay in sync
  with the actual `SKILL.md` frontmatter shape if that ever changes (low
  risk — frontmatter is stable, and generation from source is exactly what
  avoids the drift this ADR is otherwise fixing).
