# Root-memory propagation check: hook nudge + subagent judgment

- Status: accepted
- Date: 2026-07-18
- Scope: `hooks/root-memory-propagation/`, `.claude/agents/root-memory-propagation-auditor.md`

## Context

Root memory (`~/.claude/memory/*.md`, `~/.claude/CLAUDE.md`) is auto-loaded
into every session — in principle no downstream repo needs its own copy.
In practice, at least one does: `Python-PowerBI-DynastyFantasyFootball` had
hand-duplicated the token-gating loop's compact-budget figure across
`docs/adr/0001-*.md`, `CLAUDE.md`, `PLAN.md`, and
`.claude/memory/MEMORY.md`.

On 2026-07-18, root's compact-budget framing changed (from "~35% of window
on Opus" to a concrete "~125K–150K tokens"). The propagation plan named 2
specific downstream files to update. A grep run afterward, purely as a
verification afterthought, found the same stale figure in 2 *more* files
the plan never enumerated (`PLAN.md`, `.claude/memory/MEMORY.md`). Nothing
mechanical caught this — only a manual full-repo grep did, and only because
it happened to occur to the session to run one.

This is the same failure shape ADR-0005 already caught once for skill
junctions (a fixed list of "known" things silently drifts from reality) and
ADR-0007's `vendor-sync-reapply`/`skill-safety-auditor` closed for two other
cases in the same repo. The fix pattern is established: split the
deterministic trigger (a hook) from the judgment call (a subagent), rather
than either building a fully-automated auto-fixer or leaving it manual.

## Decision

Add a hook + subagent pair:

- **`hooks/root-memory-propagation/nudge.sh`** (`PostToolUse` on
  `Edit|Write`) — purely deterministic: checks whether the touched file is
  under root's `.claude/memory/` or is root's `CLAUDE.md` (anchored on
  `$HOME/.claude` specifically, so it does not fire on any project repo's
  own local `.claude/memory/`), and if so prints a reminder. Never blocks.
- **`root-memory-propagation-auditor`** (background subagent) — does the
  actual sweep: `git -C ~/.claude diff` to get the real old text (not a
  guessed keyword), greps every repo in a registry
  (`hooks/root-memory-propagation/known-downstream-repos.json`, seeded with
  the one confirmed repo) for that text, and for each hit judges genuine
  stale duplicate vs. coincidental match (this session's own false-positive
  case: an unrelated "35% market value" line in
  `05a_startup_draft_board.py` shares digits with the old compact-budget
  figure but means something else entirely — a plain grep sweep without
  judgment would have flagged it wrongly).

The registry is deliberately non-exhaustive on day one — it grows as new
duplicates are found, same as this ADR's own motivating incident.

## Alternatives rejected

- **A single hook that auto-fixes downstream repos** — rejected; the
  genuine-vs-coincidental judgment call (see the market-value false
  positive above) needs a reader, not a script, and auto-editing another
  repo's files without review violates the plan-gate norm this session
  otherwise follows for cross-repo changes.
- **Rely on the plan's own file list, improved with "be more thorough"
  instructions** — rejected; this is exactly what just failed. A plan
  written before the sweep runs cannot enumerate files nobody has looked
  for yet.
- **A single combined script doing diff + grep + auto-report with no
  subagent** — rejected; the judgment step (context-reading to dismiss
  coincidental matches) is the same kind of task ADR-0007 already
  disqualified from being a hook, for the same reason.

## Consequences

- Every root-memory edit made through Claude Code now gets a reminder to
  sweep; a direct filesystem edit outside the harness (or an edit routed
  through some other tool) won't trigger it — same layered-defense caveat
  as `hooks/git-guardrails`.
- The registry needs upkeep — a repo not yet listed won't be swept even if
  it duplicates content. This is an accepted gap, not a claim of full
  coverage; the point is closing the *known* case mechanically, not
  guaranteeing an exhaustive one.
- `CATALOG.md`/`build_catalog.py`'s agent count should reflect the fourth
  agent on the next catalog rebuild (follow-up, not blocking, same note
  ADR-0007 left for its own two agents).
