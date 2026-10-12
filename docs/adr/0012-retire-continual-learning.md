# Retire the continual-learning hook

- Status: accepted
- Date: 2026-10-12
- Scope: `hooks/continual-learning/` (removed), `~/.claude/settings.json` hook entries

## Context

`continual-learning` was ported from microsoft/skills' Copilot CLI hook: it
logged every tool call to SQLite, derived "learnings" at session end, and
injected them at every session start.

In practice the only write path that ever produced a learning was the
tool-failure counter. The injected text was, in every session, some form of
"Tool Bash frequently fails — check usage pattern". The `mistake`,
`preference` and `pattern` categories had no write path in upstream's script
or in the port. So the hook was a closed loop: it recorded that tools
sometimes fail and told every new session so, at the cost of four hook
entries firing on every tool call, session start and session end, plus a
`sqlite3`/`jq` dependency.

## Decision

Remove the hook: delete `hooks/continual-learning/`, remove its four entries
from `~/.claude/settings.json` (`SessionStart`, `PostToolUse`,
`PostToolUseFailure`, `SessionEnd`), and remove its
`~/.claude/hooks/continual-learning` link.

Existing `learnings.db` files (global and per-repo) are left where they are;
nothing reads them any more. `.claude/learnings.db` stays in `.gitignore`.

## Alternatives rejected

- **Give the other categories a write path.** Durable preferences and
  corrections already have a home that is reviewed and versioned: root and
  project memory files. A second, unreviewed store would compete with them.
- **Keep it but stop injecting.** Then it only logs tool calls nobody reads.

## Consequences

- Session start no longer carries a "Global learnings" block.
- One fewer dependency on `sqlite3`/`jq` being on `PATH`.
- The upstream evaluation notes in `README.md` and `PLAN.md` stay as history.
