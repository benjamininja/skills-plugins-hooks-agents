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
  dispatched and in what order; it is not, alone, the word to start.
  **One exception.** A project rules file may name tiers, never above
  low, whose tickets are dispatched without that word. It holds only
  for a ticket whose `Tier:` line the planner set, whose brief names
  its files and its proof, and which is not held: neither by the
  owner, nor by the planner's order behind another ticket. The project
  rules file names how a hold is marked, and a held ticket keeps the
  owner's word. Nor does the exception hold for a ticket with
  `Profile: oneshot`, which keeps the owner's word whatever its tier.
  The owner having invoked this skill in
  the session stays required, and nothing under "Never" in
  `session-rules` loosens. The manager says in its next report which
  tickets it dispatched this way. A project whose rules file names no
  such tier keeps the owner's word for every dispatch;
- the brief is written to a file and holds no double quote;
- a brief whose work changes the project's list of packages says
  `venv: full` (`session-rules`, "A brief"). One that says anything
  else goes back to the planner;
- the project's `.claude/dispatch.json` exists, and the project is on
  the owner's list (`<user profile>/.claude/dispatch-projects.json`).
  The owner writes both; a session never does, and never runs the
  script in a folder it made itself.

## Dispatch

Read `references/dispatch.md` before the first dispatch of a session.

1. Dry run, always first:
   `scripts/dispatch.ps1 -Name <name> -Tier <tier> -PromptFile <file>`
   (the script is two folders above this skill's base folder). Read
   every line it prints: the tier, the worktree, the base commit, the
   settings file, the profile, the deny rules, the start command.
   **When a brief has a `Base:` line other than `origin/main`**, add
   `-Base <that value>`. A brief with no `Base:` line starts at
   `origin/main`, fetched at `-Apply`.
   **When a brief names a profile** (a `Profile:` line), add
   `-Profile <name>`, and check that the printed rules are what the
   ticket needs. A brief with no `Profile:` line gets no profile. A
   profile the script does not know is refused: ask the owner to add it,
   never widen the shared settings file instead. A session never writes
   the profiles file or a base settings file.
2. Only if the dry run shows what the ticket asked for: the same command
   with `-Apply`.
3. Watch by events, not by polling. A follow-up (`stop`, then
   `--resume`) is only for a builder this session dispatched, on the
   same ticket.

A refusal by the script is not worked around. It is fixed at its cause
or parked.

**The main checkout's packages change only while no builder is
running.** A light environment reads the main checkout's packages, so
an install, an upgrade or a removal there changes what every running
builder tests against. Before any such change the manager reads its
list of running builders; if one is running, the change waits for its
closeout or is parked. The install itself is the owner's, or the
manager's on the owner's word.

## Merging a builder's PR

Only after the builder has reported the PR green, and only after the
manager has re-proved every item of the project's Green list itself and
posted the output on the PR. Then one squash-merge. A PR that is not
green is not merged. A builder's PR for a dispatched ticket needs no
further word from the owner, except where `session-rules` keeps the
owner's word ("Merging on Green": a gate change, a path no required
check covers, the parking list, a migration or published data); any
other PR (the manager's
own, the planner's) is merged only after the owner has approved that PR.
`references/manager.md` has those merges and the planner's read.

## Closeout

Only for a builder this session dispatched, only when it has stopped,
and in the order of `references/dispatch.md`. Right after the merge, as
one step with no separate word from the owner, the manager runs
`scripts/closeout.py` for that builder: a dry run, then the same line
with `--apply`. The script alone removes the worktree and deletes the
branch, and only when they hold nothing unmerged or uncommitted.
Anything it refuses is listed for the owner and left where it is.
Nothing else is deleted: not another session's branch or worktree, and
nothing the owner has not named.
