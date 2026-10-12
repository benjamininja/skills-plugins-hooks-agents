# plan-gate-sync-auditor: a third agent, homed here despite auditing a different repo

- Status: superseded (2026-10-12) — the agent is retired. `project-memory-template`'s
  tiers no longer restate the plan gate (root `~/.claude/CLAUDE.md` supplies it in
  every session on the owner's machines), so there is nothing left to keep in sync.
  The agent also had no trigger and was never run. Text below is history.
- Date: 2026-07-17
- Scope: `.claude/agents/plan-gate-sync-auditor.md`

## Context

Running `/subagent-audit` against `project-memory-template` (a separate,
docs-only template repo) turned up almost no real subagent surface — it
doesn't dogfood its own scaffold, so most categories (context firewall,
schema transformer, MCP wrapper, parallel dispatch) had nothing to attach
to, and its `check-in-hygiene` hook already correctly covers what a
deterministic script can catch (unfilled placeholders, dangling references,
scoped to the current commit).

One real gap survived: `project-memory-template`'s own README and the
private root `C:\Users\benha\.claude\CLAUDE.md`'s plan-gate section both
call out, unenforced, that the three tier `CLAUDE.md` files carry a
**distilled paraphrase** of the root's plan-gate threshold and escape
hatches, not a byte-identical copy — "nothing enforces that the three
copies stay in sync" is the template README's own words. A text-diff hook
can't check this: the tiers are deliberately reworded for brevity, so
literal difference is expected and not itself a bug. Checking whether the
*meaning* still matches after either side changes is a genuine judgment
task.

The open question was placement: the auditor's subjects (root CLAUDE.md +
three tier files) live in two other repos (`dotclaude`, private; and
`project-memory-template`), neither of which has a `.claude/agents/` home
or memory scaffold today. Discussed with the user directly: `dotclaude` is
the more "obvious" home by subject matter, but this repo
(`skills-plugins-hooks-agents`) is the one every project already
junction-installs from — an agent here is reachable everywhere, matching
the precedent set by [ADR-0007](0007-first-subagents-vendor-sync-and-safety-audit.md)'s
first two agents. The user chose this repo.

## Decision

Add `plan-gate-sync-auditor` (background, category B — domain auditor) to
`.claude/agents/`. It reads both the root plan gate and the three tier
copies (all outside this repo's own tree — the agent's file-read scope
isn't confined to `skills-plugins-hooks-agents`, which is a departure from
`vendor-sync-reapply`/`skill-safety-auditor`'s repo-local scope, but not a
new mechanism — agents already read cross-repo where needed, same as
`setup-project-memory` reading tier content from `project-memory-template`
per ADR-0005) and reports semantic drift, never textual drift.

## Alternatives rejected

- **Home it in `dotclaude`** — rejected; that repo has no established
  `.claude/agents/` pattern yet, and centralizing in the one repo every
  project already links from is more consistent with how `setup-
  project-memory` and the two ADR-0007 agents are already discovered.
- **Home it in `project-memory-template`** — rejected; that repo has no
  `.claude/agents/` directory or memory scaffold to anchor the decision in,
  and (per the audit) has essentially no other subagent surface to build a
  precedent around.
- **A pre-commit hook doing text diff on the sync-marker block** — rejected;
  the tiers are deliberately reworded, not copied verbatim, so a literal
  diff would false-positive on every legitimate paraphrase and miss actual
  semantic drift hidden behind matching wording.
- **Building the deferred `check-in-hygiene` staleness/delete-offer
  features as subagents** — considered during the same audit pass;
  rejected as out of scope here because `project-memory-template` never
  has a live, filled-in scaffold instance to judge staleness of (only
  unfilled template content under `tiers/`) — that candidate belongs in a
  *consuming* repo, not this audit.

## Consequences

- Third agent in this repo's roster; `CATALOG.md`'s dynamic Agents line
  (added in ADR-0007's follow-up to `tools/build_catalog.py`) will pick it
  up automatically on next `build_catalog.py` run.
- First agent here whose read scope extends outside this repo's own
  working tree — worth noting if a future audit tightens agent tool/path
  scoping conventions.
- `project-memory-template` itself gets no new files from this decision —
  consistent with it having no memory scaffold to write into (per
  `/subagent-audit`'s own fallback: summarize in the report, don't force a
  write).
