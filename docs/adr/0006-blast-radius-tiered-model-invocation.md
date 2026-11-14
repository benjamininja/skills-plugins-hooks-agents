# Blast-radius-tiered model-invocation for a subset of router skills

- Status: accepted; revised 2026-11-14 (Revision 1 below corrects the
  rule: it rates impact and trigger breadth)
- Date: 2026-07-17
- Scope: `skills/grill-me/SKILL.md`, `skills/grill-with-docs/SKILL.md`,
  `skills/teach/SKILL.md`, `skills/writing-great-skills/SKILL.md`,
  `skills/ask-matt/SKILL.md`, `vendor-skills.json`

## Context

[ADR-0005](0005-skill-routing-and-drift-detection.md) considered and
rejected blanket auto-invocation for Pocock's flow-entry/router skills,
reasoning that they're deliberately `disable-model-invocation: true` because
the model shouldn't silently decide to kick off a multi-session flow on its
own. It built a `SessionStart` routing-index nudge
(`hooks/skill-catalog-health/`) instead: the model can surface "this looks
like `/wayfinder` territory," but the human still decides.

Revisiting this: ADR-0005's reasoning treats "router skill" as one bucket,
but the actual risk a wrongly-triggered skill carries isn't uniform across
that bucket. What matters is what happens on a false-positive trigger:

- A **nudge that's ignored** degrades to status quo — the user has to
  remember and type the command themselves, exactly as if the hook didn't
  exist. Cheap failure.
- An **auto-invoked skill that writes to shared, external state** (creates
  issues on a tracker, runs an installer, writes files across a repo
  unprompted) is a real action taken on a guess. Expensive, sometimes
  irreversible failure.
- An **auto-invoked skill whose worst case is a conversation, or a local
  git-tracked file write** sits in between: visible in `git diff`, trivially
  reversible, no one but the current user is affected either way.

That last category was hiding inside ADR-0005's single "router skills"
bucket. Auditing all 13 then-manual skills by what they actually do if
triggered wrong:

- `ask-matt` — pure routing, asks a question, no side effects.
- `grill-me` / `grill-with-docs` — interview-driven; `grill-with-docs`
  writes ADRs/glossary entries, but locally, git-tracked, reversible.
- `teach` — writes to a local teaching-workspace directory (lessons,
  learning records), same local/reversible shape.
- `writing-great-skills` — pure reference, no side effects.
- `triage` and `wayfinder` were initially proposed for this tier too, but
  re-reading their bodies showed both write to the **external issue
  tracker** (triage moves issues through tracker state; wayfinder creates a
  `wayfinder:map` issue plus child ticket issues) — that's shared, external
  state, not a local diff. Both stay in the high-consequence bucket.
- `handoff`, `setup-project-memory`, `setup-matt-pocock-skills`, `to-spec`,
  `to-tickets`, `implement`, `improve-codebase-architecture` were not
  re-examined in detail here — they were already understood to run
  installers, write across a repo, or touch external trackers, matching
  ADR-0005's original reasoning without needing a recheck.

## Decision

Flip `disable-model-invocation` off (remove the line) for exactly five
skills — `grill-me`, `grill-with-docs`, `teach`, `writing-great-skills`,
`ask-matt` — whose worst-case wrong-trigger outcome is a conversation or a
local, git-tracked file write.

Leave every other previously-manual skill untouched, including `triage` and
`wayfinder`, which were considered and rejected for this tier specifically
because they write to the external issue tracker.

**Mechanism**: record each edit in `vendor-skills.json`'s existing
`known_local_edits[]` array (already used by `ask-matt` for an unrelated
edit) rather than the heavier `vendor-cache/` fork pattern from ADR-0001.
This is a single-field diff per skill, not a substantial rewrite — the fork
pattern exists for the latter (see `two-axis-code-review`, ADR-0001's only
current fork). `known_local_edits` already does the right thing for this
shape of change: `tools/update_vendor_skills.py`'s drift check classifies an
edited file as *known* drift (not *new* drift) as long as its blessed
`local_sha` still matches; when a future `--apply` re-vendors the skill and
overwrites the file, the tool's existing "reapply ritual" reminder is what
resurfaces the need to redo the one-line removal and re-`--bless`.

No change to `hooks/skill-catalog-health/` — its routing index is generated
at runtime from each skill's frontmatter, so it reflects the new
model-invocable status automatically.

## Alternatives rejected

- **Flip all 13 (override ADR-0005 wholesale)** — rejected; would reopen the
  actual load-bearing part of ADR-0005's reasoning (unprompted external-state
  writes), not just the part that turned out to be overbroad.
- **Full `vendor-cache/` fork pattern per skill** — rejected as
  disproportionate for a one-line frontmatter removal; `known_local_edits`
  already exists for exactly this case and is used elsewhere in the same
  file.
- **Include `triage`/`wayfinder` in the flipped tier** — initially proposed,
  rejected on closer reading of their bodies: both write to the external
  issue tracker, matching the exact risk ADR-0005 was written to guard
  against.

## Consequences

- `grill-me`, `grill-with-docs`, `teach`, `writing-great-skills`, `ask-matt`
  can now be reached by the model without the user typing the slash command,
  closing the specific gap this ADR was written to close (planning/
  stress-testing and routing skills that should be reachable ambiently).
- `docs/adr/0005-skill-routing-and-drift-detection.md` is amended with a
  one-line status note pointing here; its body and reasoning for the
  remaining manual-only skills are otherwise unchanged and still authoritative.
- New maintenance surface: after any future `--apply` re-vendors one of
  these five skills, the removed `disable-model-invocation` line must be
  reapplied and re-`--bless`ed, same as any other `known_local_edits` entry.
  Real but pre-existing risk — see `ask-matt`'s prior entry for precedent.

## Revision 1 (2026-11-14): the rule rates impact and trigger breadth

Tickets: tools #48 (this revision and the auditor change), #50 (applies
it). Ben's rulings are on #48.

**What was wrong.** The Context above sorts a wrong trigger into
"conversation or local git-tracked write" (low) and "external shared
state" (high). Two gaps:

- "Local" ran two places together: this repo's tracked files, which this
  repo's review sees, and the folder a session happens to run in, in any
  repo, which no review here sees. `teach` writes seven files and folders
  into the second.
- It judged impact only. How often a skill fires by mistake depends on how
  broad its description is. `teach`'s ("Teach the user a new skill or
  concept") matches nearly any request to explain something.

**The rule now.** Judge a wrong trigger from the skill's whole folder, not
only `SKILL.md`:

1. **Where its writes land.** None (conversation, reading, routing): low
   impact. This repo's git-tracked files only: low (seen in `git diff`,
   undone there). The folder the skill runs from, in any repo, or anywhere
   outside this repo: medium. Shared external state (an issue tracker, an
   installer, a network write): high.
2. **How it is undone.** A write that can't be undone (overwriting or
   deleting existing files, a push) is high impact wherever it lands.
3. **How broad its trigger is.** Narrow: it fires on an explicit phrase or
   command. Broad: it matches common requests that don't mean this skill.

The model may start a skill when its impact is low, or medium with a
narrow trigger. Otherwise it keeps `disable-model-invocation: true`.
Adding the flag is a decision under this rule as well as removing it
(#49, #50), and goes through the same `skill-safety-auditor` gate.

**Where the rule lives.** This revision is the source.
`.claude/agents/skill-safety-auditor.md` carries a working copy and
defers to this revision where the two differ.

**The five skills under the rule** (re-audit in #48's PR):

| Skill | Impact | Trigger | Verdict |
|---|---|---|---|
| `teach` | medium: writes into the folder it runs from | broad | manual (#50) |
| `grill-with-docs` | medium: through `domain-modeling`, creates and edits `GLOSSARY.md` and `docs/adr/` in whatever repo it runs in | broad ("sharpen a plan or design") | manual (#50) |
| `grill-me` | low: conversation only | broad | model may start it |
| `writing-great-skills` | low: reference only | narrow | model may start it |
| `ask-matt` | low: routing and reading only | broad | model may start it |

The Decision above stands for `grill-me`, `writing-great-skills` and
`ask-matt`. #50 restores the flag on `teach` and `grill-with-docs` and
updates their `known_local_edits` entries. The other model-invocable
skills, `domain-modeling` first (it makes the same unconfirmed glossary
edits), are audited under this rule in #176.
