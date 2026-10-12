---
name: session-dispatch
description: Manual. The builder manager's procedures that change things outside the conversation - starting a builder with the plugin's dispatch script, following it up, re-proving and merging a builder's PR, and closing a builder out. Invoked by the owner in a manager's session; no session loads it on its own.
disable-model-invocation: true
---

# Session dispatch

For the builder manager only, and only when the owner has invoked this
skill in the session. The rules every role keeps are in the
`session-rules` skill of this plugin; load it first.

Everything here changes something outside the conversation: a session is
started, a PR is merged, a branch or a worktree is deleted. So each step
is taken for a named ticket, in the order written, and never on the
session's own guess that it would help.

## Before a dispatch

All of these hold, or there is no dispatch:

- a ticket or a stage is named, and it has a tier (`session-rules`,
  "Tiers"). No tier, no dispatch: ask the planner;
- the owner has said, in this session, that this work is to be
  dispatched now. A stage in the project rules file says what may be
  dispatched and in what order; it is not, alone, the word to start;
- the brief is written to a file and holds no double quote;
- the project's `.claude/dispatch.json` exists, and the project is on
  the owner's list (`<user profile>/.claude/dispatch-projects.json`).
  The owner writes both; a session never does, and never runs the
  script in a folder it made itself.

## Dispatch

Read `references/dispatch.md` before the first dispatch of a session.

1. Dry run, always first:
   `scripts/dispatch.ps1 -Name <name> -Tier <tier> -PromptFile <file>`
   (the script is two folders above this skill's base folder). Read
   every line it prints: the tier, the worktree, the settings file, the
   deny rules, the start command.
2. Only if the dry run shows what the ticket asked for: the same command
   with `-Apply`.
3. Watch by events, not by polling. A follow-up (`stop`, then
   `--resume`) is only for a builder this session dispatched, on the
   same ticket.

A refusal by the script is not worked around. It is fixed at its cause
or parked.

## Merging a builder's PR

Only after the builder has reported the PR green, and only after the
manager has re-proved every item of the project's Green list itself and
posted the output on the PR. Then one squash-merge. A PR that is not
green is not merged. A builder's PR for a dispatched ticket needs no
further word from the owner; any other PR (the manager's own, the
planner's) is merged only after the owner has approved that PR.
`references/manager.md` has those merges and the planner's read.

## Closeout

Only for a builder this session dispatched, only when it has stopped,
and in the order of `references/dispatch.md`. A branch is deleted only after `git cherry`
shows nothing missing; a worktree is removed only if it holds no
uncommitted file. Anything else is listed for the owner and left where
it is. Nothing else is deleted: not another session's branch or
worktree, and nothing the owner has not named.
