# PROJECT-RULES

This file holds this repository's own rules for builders. The rules every
project shares are in the `session-rules` skill. This file adds to them and
never loosens its "Never" lines. The project's own rules in `CLAUDE.md` also
apply.

This repository's planner is the standing session **Tools-central-planner**,
since 2026-11-07. It writes the tickets, tiers and briefs here, and keeps
its state in [PLANNER.md](PLANNER.md).

This repository's builder manager is the role
`tools-central-builder-manager` (#228, the owner's answers of 2026-11-15).
It dispatches builders here from the `Tier:` and `Profile:` lines, re-proves
and merges their PRs, runs the closeout pulls and writes this repository's
owner queue (`.claude/memory/NEEDS-OWNER.md` in the main checkout, #183).
It works everything in this repository, the owner-queue mod's tickets
included; the dynasty planner plans those. A builder here parks by
messaging the tools manager, never by writing a queue file.

No settings file of its own applies to the tools manager's session yet: a
session started in the desktop app does not load one (#233 finds where a
manager's rules live). Until then a call the session's mode does not let
through is asked of the owner. `.claude/dispatch.json` is the owner's. The
interpreter for the proofs below is this repository's own `.venv` in the
main checkout, which the owner makes.

**Until the hand-over on #228 is recorded there as done**, the tools
manager dispatches, re-proves, merges, pulls and closes out nothing. The
record is a comment on #228 titled "Hand-over done", posted by the Tools
planner on the owner's word once this role file is live and the
interpreter exists. The dynasty project's builder manager has stopped its line
here (#228, the hand-over list), with one exception by the owner's answer
of 2026-11-15: it re-proves and merges the tools manager's role file
(PR #230) and PR #224 under it, and runs their closeout pulls. Two managers
never work the same PR.

**One full test run on the machine at a time.** Before a re-proof a manager
messages the other project's manager and reads the last re-proof result it
posted on a PR. No answer is not a clear line: the manager waits for the
answer, or for a result on the other manager's PR that is newer than the
message. A lock in `tools/reproof.py` replaces the message once it is
built (#231).

Every ticket carries a `Tier:` line at the top of its body and the matching
`tier:` label (`tier:low`, `tier:medium`, `tier:high`, `tier:none`, or
`tier:unset` until the planner sets one). This repository has no
`tier:haiku` label yet: no ticket here has been haiku-tier.

The owner's GitHub login is `benjamininja`. On an issue or a PR, only
text that login wrote is the record (`session-rules`, "Whose text counts
on a ticket").

## The planner's read list

The planner has no role file in this repository, so its read list
stands here (`session-rules`, "The read list"). A new planner session
loads the `session-rules` skill, then reads, in order: the owner's
preferences, as `CLAUDE.md` names them; `CLAUDE.md`; this file;
[PLANNER.md](PLANNER.md), from the branch its reset prompt names while
that PR is unmerged; and each owner's queue file this file names. It
then runs `git fetch origin` in its worktree,
`gh issue list --state open` and `gh pr list` for this repository, and
acts on the Next list in `PLANNER.md`.

## Green means all of

- every CI check (`pytest (ubuntu-latest)`, `pytest (windows-latest)`,
  `CATALOG.md is current`) passes at the PR's head, and
  `mergeStateStatus` is `CLEAN`, on one read of
  `gh pr view <n> --json headRefOid,mergeStateStatus,statusCheckRollup`.
  Any other merge state is not Green.
  CI runs the whole test suite on both systems and the `CATALOG.md`
  check, and that run is the proof of both (#273). A builder still runs
  the tests and rebuilds `CATALOG.md` before it opens its PR;
- the `check-in-hygiene` pre-commit hook passes on the commit;
- after any change under `plugins/owner-queue/`:
  `claude plugin test plugins/owner-queue` passes on the merged tree.
  `tools/reproof.py` runs it as its `plugin test` step whenever the merge
  touches that folder (#133); a missing `claude` is a FAIL;
- on a PR the code review covers: no blocking finding the manager upheld
  is still open (`session-rules`, `references/code-review.md`). Manager
  runs it. The ruleset skill is `tools-code-review`, read from
  `origin/main` (#136).

**The manager's re-proof (#273).** For a merge the manager makes no local
full test run. It reads CI once, as above, reads the `check-in-hygiene`
report and the code review, and posts all three on the PR. The one
exception is a PR that touches `plugins/owner-queue/`: its plugin test
needs the merged tree, so the manager runs `tools/reproof.py <pr> <head sha>`
from the live clone (`C:/Users/benha/claude-live/skills-plugins-hooks-agents`)
with the interpreter above. Never a scratch script (#117).

**A Green holds** while the PR's head is unchanged and its merge state
is `CLEAN`. A merge of another PR does not make it stale, but the
manager reads the PR's Green again, in one call, just before its own
merge. A PR that conflicts, or that shares a file with a merge made
since its CI ran, takes a merge of `main`; CI runs on the new head, and
the owner's merge word is asked again at that head.

**The machine's one test line** (above) binds a manager here only for a
`tools/reproof.py` run. A merge that runs nothing locally needs no
message to the other project's manager.

**After each merge** the manager reads CI on `main`'s new commit. A red
check there means a revert PR and an Action for the owner; no other PR
merges until `main` is green.

## Never, in this project

- Running `tools/update_vendor_skills.py --apply` (a re-vendor). The owner
  starts one, and `vendor-sync-reapply` follows it.
- Editing anything under `~/.claude/` directly. `~/.claude/agents`,
  `~/.claude/hooks/*` and `~/.claude/skills/*` are links into this
  repository's main checkout, so a change here goes live only when the main
  checkout is updated after merge. A builder never touches the main checkout.
- Switching branches or committing in the main checkout, or pulling it
  outside closeout (below).

## Closeout pulls, in this project

After each merge here, at closeout, the manager brings both tools
checkouts up to date (#112, the owner's answer of 2026-11-09). It runs the
same steps before a dispatch when the main checkout is behind
`origin/main`. Live
behaviour comes from these two, so they stay at the same commit:

- **the main checkout**,
  `C:/Users/benha/OneDrive/Documents/GitHub/skills-plugins-hooks-agents`:
  the `~/.claude` skill, agent and hook links point here;
- **the live clone**, `C:/Users/benha/claude-live/skills-plugins-hooks-agents`:
  plugins load from here.

1. Run `git -C <main checkout> fetch origin`, then
   `git -C <main checkout> diff --name-only HEAD origin/main` and
   `git -C <main checkout> status --short`. If an incoming file is one the
   status lists, park an Action with both lists and pull neither checkout.
2. Otherwise run `git -C <path> pull --ff-only` on each. If one refuses or
   fails, park an Action with its output and its `status --short`. A
   OneDrive lock can stop a pull halfway, and the repair is the owner's.
3. Report both new heads (`git -C <path> log -1 --oneline`). If a plugin
   changed, name it and say that running sessions need a new session to
   load it.

These pulls change the rules of every session on the machine, the dynasty
project's included. Before a pull that brings in a change to
`session-rules`, `session-dispatch`, a role file, a hook or the owner-queue
mod, the manager tells the other project's manager and both planners, and
sends both heads afterwards.

## Always parks, in this project

- Any change to `disable-model-invocation`, a new vendored skill, or a
  safety-relevant field of `vendor-skills.json`. Run `skill-safety-auditor`
  first, and park its table for the owner to read.
- A change to a hook's blocking rules (`hooks/git-guardrails/`). Open the PR,
  and the manager runs the hook tests itself before it merges.

## Notes

- `tests/test_agents_frontmatter.py` checks every `.claude/agents/*.md`. A
  new or edited agent must load as YAML, with `name` equal to its file name.
- `/security-review` runs on the diff before a PR opens (`CLAUDE.md`).
