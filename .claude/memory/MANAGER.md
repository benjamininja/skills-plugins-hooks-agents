# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
`PROJECT-RULES.md`; this file is state.

## START HERE

Written 2026-11-22, second prep of the day, by the tools manager
(session Tools-builder-manager). `origin/main`, the main checkout and
the live clone were all at `f1ff785` on the last read. The role is in
full ("Hand-over done" on #228). `session-dispatch` must be typed again
after every clear.

**One full test run on the machine at a time**, by message with the
dynasty manager (dff-central-builder-manager) until #231's lock (PR
#242) merges and is pulled. At this prep the line was with dynasty:
the tools end notice went out after the #244 re-run at 14:56. Ask for
it again before any tools full run.

**The merge line is held by #244.** #236's re-proof timed out at 3600s
twice (`7b5b408`, then `629074b`: pull/236 issuecomment-7082628279),
while Windows CI passed in 17 to 19 minutes. #244 (medium, Profile none)
was dispatched twice on Ben's go; Claude Code killed both pytest runs
for low memory, at 326 and 309 of 603 tests, no failures, no hang, at
3.4 and 5.8 s a test (issues/244 issuecomment-7084964448,
issuecomment-7085660045). Memory figures: issuecomment-7085240670 and
issuecomment-7085659785 (commit charge 52 to 59.6 GB of 58 to 61 GB).
At 5.8 s a test the suite is about 58 minutes, at the cap: the
timeouts fit slowness under memory pressure. Tools-central-planner is
taking it to Ben; wait for its ruling on #244. No tools re-proof until
a full run can finish.

Next, in order, once #244 is ruled and a full run can finish:

1. **#236** (this file, head moved by this state-back): re-prove at the
   new head, then the merge word by button.
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
   **#189** and **#219** (medium, Profile none), then **#241** (low, after
   #239; it now holds #245's point, closed as a duplicate on Ben's
   ruling, issues/241 issuecomment-7085619927); then the older open PR
   line below. Each go quoted and asked of Ben by button.
8. At the state-back after #236 merges, trim this file (Ben's button,
   pull/236 issuecomment-7082192929): drop "What this session answers
   for" and, once #231 and #237 close, the 2026-11-19 history.

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
| `t244-pytest-hang` | #244 | medium | `9fd98bc0` | none | Part 1 stopped twice for low memory; idle, no file changed; waits for the planner's ruling |

The first two are not listed by `claude agents` since the app restart;
check before closeout. `t244`'s first session `8ef7acf3` was stopped
(its Bash was refused after the memory kill); its worktree is reused.
`t175-reproofrule` (`9144aeda`, old OneDrive path) is blocked with no
pid; neither manager dispatched it, so it is left for Ben.

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
| #198 | `e16203d` | planner state-back, clears 11 and 12 |
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
- 2026-11-22: Ben's go for #244, "Dispatch when clear (Recommended)"
  (issues/244 issuecomment-7083138076), and for the re-run, "Freed,
  dispatch re-run" then "Run now" (issuecomment-7085240670).
- 2026-11-22: Ben's memory-review answers (pull/236
  issuecomment-7082192929): trim this file after #236 merges; reset
  prompts stay at 400 words or fewer, as pointers.

## Lessons

- The git-guardrails hook blocks a chained command that holds a push:
  one git command per call, and push with
  `git -C <worktree> push origin <branch>`.
- In Git Bash, `git show <branch>:<path>` needs `MSYS_NO_PATHCONV=1`,
  or the argument is rewritten into a Windows path.
- A reviewer runs read-only, so it may run during another manager's
  test line; only the full suite waits for the line.
- Run `dispatch.ps1` with no `2>&1`: in PowerShell 5.1 git's stderr
  line becomes an error and stops the script after the worktree step.
- In PowerShell 5.1, `claude agents --json | ConvertFrom-Json` gives one
  array object: unwrap with `ForEach-Object { $_ }` before filtering.
- A builder's idle notice can fire at a turn break while its test run
  goes on. To be woken at the run's end, run `Wait-Process` on the
  pytest process ids as a background command.
- A builder in dontAsk mode cannot use AskUserQuestion, Monitor or a
  memory probe; after a harness kill its Bash may be refused too. The
  manager reads its transcript and posts for it.
- Before a long full run, log memory (physical free, commit charge):
  Claude Code kills background runs when the machine is low.
- Peers: Tools-central-planner, dff-central-planner,
  dff-central-builder-manager. Find them with ListAgents by name; ids
  change at a relaunch.
