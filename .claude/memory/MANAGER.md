# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
`PROJECT-RULES.md`; this file is state.

## START HERE

Written 2026-11-22 by the tools manager (session Tools-builder-manager),
at a clear boundary. `origin/main`, the main checkout and the live clone
were all at `f1ff785` on the last read. The role is in full ("Hand-over
done" on #228); the move (#235) is done for this repository through
step 7. `session-dispatch` must be typed again after every clear.

**One full test run on the machine at a time**, by message with the
dynasty manager (dff-central-builder-manager) until #231's lock (PR
#242) merges and is pulled. At the clear the line was free: the
dynasty manager's end notice came after #621 (GREEN, merged `5bd92f4`)
and #625. Its next session asks for the line before it re-runs #625.
After the clear, tell the dynasty manager the tools manager takes the
line, then run.

Next, in order:

1. **#236** (this file): the re-proof at `7b5b408` was NOT GREEN, as
   pytest hit the 3600s cap while every other step passed
   (pull/236 issuecomment-7026612616). CI's Windows pytest passed at
   that head in 19m13s, and no leftover pytest process remained, so
   the cause is the machine (a local hang or contention), not the PR.
   This state-back moves the head: re-prove at the new head. A second
   timeout opens a `Tier: unset` ticket on the local hang for the
   planner. Then the merge word by button.
2. **#238** (the planner's `PROJECT-RULES.md` half of #237, `c211cad`,
   CI clean): re-prove, merge word by button. No code review (planner
   PR). It merges before #239.
3. **#239** (#237's builder PR, `c64cf25`): first review done (full at
   `low`; the ruleset counts every non-Markdown file as code). No
   blocking finding. F1 (advisory) is closed by #238
   (pull/239 issuecomment-7025383696). Re-prove after #238 merges,
   with `pre-commit` run by the manager, then the merge word.
4. **#242** (#231's lock, builder PR, `b278602`, CI clean): code review
   closed, F1 and F2 accepted at re-check and closed
   (pull/242 issuecomment-7025134405). Re-prove, then the merge word.
   Then send the final lock format text (in the PR body) to
   dff-central-planner for dynasty #620.
5. Closeout pulls after each merge. #238 and #242 change rules or the
   re-proof tool: tell the dynasty manager and both planners before the
   pull and send both heads after.
6. Closeout of `t237-path-move` and `t231-reproof-lock` after their PRs
   merge, per session-dispatch `references/dispatch.md`.
7. Then **#233**, then **#232**, each go asked of Ben by button; then
   the older open PR line below.

## What this session answers for

As the role file `.claude/agents/tools-central-builder-manager.md`
says: dispatch, the owner's queue (`.claude/memory/NEEDS-OWNER.md` in the
main checkout), re-proof and the code review, the merge (each merge word
asked of Ben by button at the re-proved head), closeout and the closeout
pulls of the main checkout and the live clone, and this file.

## Builders running

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t231-reproof-lock` | #231 | medium | `8506434b` | #242 at `b278602` | review closed; waiting for re-proof (state-back issues/231 issuecomment-7025354702) |
| `t237-path-move` | #237 | low | `f0de4ab6` | #239 at `c64cf25` | review done; waiting for re-proof |

Both are held from the full local suite: the manager's re-proof runs it.

## Open PRs

In the line now: #236, #238, #239, #242 (above). The older line, each
read again before its re-proof:

| PR | Head | Subject |
|---|---|---|
| #227 | `63c6445` | machine layout and cold setup (#223); needs the new path too |
| #222 | `f85a7b4` | one plugin source (#195) |
| #216 | `3e99496` | ruleset setup guide (#193) |
| #214 | `a6d7a6c` | resume_plain.ps1 input checks (#207) |
| #211 | `7c1bafb` | git-guardrails git name (#168) |
| #210 | `dce2100` | reset prompt is a pointer (#161) |
| #208 | `0f1e1a1` | git restore command form |
| #205 | `bb80384` | ADR-0018 threat model (#190) |
| #198 | `e7148b3` | planner state-back, clears 11 and 12 |
| #197 | `b7ef918` | owner-queue clear prep (#161) |
| #196 | `7b8f1e9` | owner-queue Answer hold (#179) |
| #184 | `05f2a7f` | one queue per project (#183) |
| #182 | `5632555` | re-proof one script, one rule (#175) |
| #181 | `148c9d1` | planner state-back, clear 10 |

## Dispatch, as proven

- From the main checkout at its new path, with the dispatch script in
  the live clone's plugin folder: dry run, then `-Apply`, from
  PowerShell. Both #231 (medium) and #237 (low) started cleanly; setup
  makes the worktree's `.venv`.
- A brief must hold no file under `.claude/` (a builder's mode refuses
  the write) and no `pre-commit` proof line (no builder allow rule; the
  manager runs it). Told to the planner on #237.
- A brief's `Ticket: this issue` line is given as the ticket number in
  the prompt file.

## Waiting on the owner (pointer to NEEDS-OWNER.md)

The queue file is empty. The owner-queue line came back in this
session's system prompt on 2026-11-19 (relevant to #240); after a clear,
send the new queue id to both planners and the dynasty manager.

## Queue entries raised

- 2026-11-19, Decision: #231 builder parked at Part 1. Answered the same
  day: Ben chose "Rule from reading (Recommended)" (issues/231
  issuecomment-7024139524); the entry left the queue.

## Decided since

- 2026-11-19: Ben's go for #231 after the move repair (issues/231
  issuecomment-7023959064); dispatched (issuecomment-7024077556).
- 2026-11-19: Ben's three answers on #231's finding (lock in
  ~/.claude-reproof, one result file per PR and head, accept the orphan
  child), issues/231 issuecomment-7024312664.
- 2026-11-19: Ben's go for #237 after the planner dropped file 1
  (issues/237 issuecomment-7024307994); dispatched on the six-file brief
  (issuecomment-7024353364).

## Lessons

- The git-guardrails hook blocks a chained command that holds a push:
  one git command per call, and push with
  `git -C <worktree> push origin <branch>`.
- In Git Bash, `git show <branch>:<path>` needs `MSYS_NO_PATHCONV=1`,
  or the argument is rewritten into a Windows path.
- A reviewer runs read-only, so it may run during another manager's
  test line; only the full suite waits for the line.
- Peers: Tools-central-planner, dff-central-planner,
  dff-central-builder-manager. Find them with ListAgents by name; ids
  change at a relaunch.
