# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
`PROJECT-RULES.md`; this file is state.

## START HERE

Written 2026-11-23, state-back at 14:40Z, by the tools manager (session
Tools-builder-manager). `origin/main`, the main checkout and the live
clone are all at `aefbc68` (PR #246 merged and pulled). The role is in
full ("Hand-over done" on #228). `session-dispatch` must be typed again
after every clear (a compact keeps it).

**One full test run on the machine at a time**, by message with
dff-central-builder-manager until #231's lock (PR #242) merges and is
pulled: a start notice before, an end notice after. The line is with
tools: dynasty said at 14:27Z it needs no full run now and asks tools
before its next one. A full run takes about 59 minutes (608 tests).
Builders `t248` and `t250` run no full suite until the manager gives
them the line.

**#244 Part 2 is merged**: PR #246 at `aefbc68`. Its re-proof was GREEN
with the pytest step at 3510.8s, 89s under the old 3600s cap (pull/246
issuecomment-7103972437). From the next re-proof the pytest step has a
5400s cap and prints the 25 slowest tests. #244 is the planner's to
close.

**Windows hazard** (t250's Part 1 finding, issues/250
issuecomment-7103861254): `git worktree remove` follows a junction and
deletes the contents of the folder it points to, and a file held open
stops it part way while git drops its record. Before any worktree
removal, scan it: `Get-ChildItem -Recurse -Force -Attributes
ReparsePoint`. Both planners and the dynasty manager are told.

Next, in order:

0. **t244 closeout, left open.** The builder has stopped and its PR is
   merged. `git cherry` lists its two commits as not in main (a squash
   merge changes the patch id) though `git diff origin/main` is empty;
   its worktree lists `CATALOG.md` as modified, by line endings only;
   it holds no junction. Under the rule both stay until Ben names
   them or #250's script lands; asked of Ben by button.
1. **#236** (this file): its re-proof starts right after this
   state-back (output in the scratchpad as `reproof-236.txt`), then the
   merge word by button. No push to this branch between the re-proof
   and the merge: a push moves the head.
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
   **#248** is dispatched (builder table). **#250**: the planner's
   ruling on Part 1 is issues/250 issuecomment-7103994943; its point 3
   is Ben's button in the planner's chat, so Ben confirms by button
   here, then the comment goes whole to `t250` by SendMessage while it
   is listed (else `resume_plain.ps1`). **#251** (medium)
   only once the planner posts its brief after #189's PR merges (Ben's
   go given here 2026-11-23). **#137** Bring to Chat + auto-close: Ben
   chose a planner refresh; dff-central-planner folds #137 and #111 and
   adds auto-close (issues/137 issuecomment-7103524615); ask Ben's go by
   button when its brief is posted. PRs #196/#197 touch the same file.
   **#249** (planner PR, #247) joins the planner PRs after #205.
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
| `t244-pytest-hang` | #244 | medium | `9fd98bc0` | #246 merged at `aefbc68` | stopped; closeout left open (step 0) |
| `t250-closeout-script` | #250 | high | `08a25cd7` | #252, draft, tests only | Part 1 posted; waits for the ruling to be sent; no full run without the test line |
| `t248-adr-hygiene` | #248 | low | `f328d768` | none yet (branch pushed) | working; no full run without the test line |

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
| #198 | `f280c65` | planner state-back, clears 11 and 12 and later |
| #197 | `b7ef918` | owner-queue clear prep (#161) |
| #196 | `7b8f1e9` | owner-queue Answer hold (#179) |
| #184 | `05f2a7f` | one queue per project (#183) |
| #182 | `5632555` | re-proof one script, one rule (#175) |
| #181 | `148c9d1` | planner state-back, clear 10 |

Read-only pass of 2026-11-23 at `f1ff785`: #227, #222, #216, #214,
#211, #210, #208, #205, #197 and #196 merge clean with CI green. Four
are with Tools-central-planner on Ben's button ("Send to planner
(Recommended)"), each ruling to come as a comment on its PR: #198 (head
moved, about 60 state commits), #181 (an ancestor of #198's branch),
#184 (conflicts on `PROJECT-RULES.md` with main and with #238; its
one-writer text is stale since #230), #182 (its allow rule names
`scripts/reproof.py`; main has `tools/reproof.py`). The planner is
repairing #227 and #184 on Ben's button in its chat: their heads will
move.

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
- 2026-11-23: Ben's go for #244 Part 2, "Send to t244 (Recommended)"
  (issues/244 issuecomment-7088267365); sent by resume
  (issuecomment-7101564153).
- 2026-11-23: Ben's go for #250, "Now, no full run (Recommended)"
  (issues/250 issuecomment-7103443214); dispatched. #251's go given,
  waits for its brief.
- 2026-11-23: #247 deny-rule Action done (issues/247
  issuecomment-7103215501) and removed from the queue.
- 2026-11-23: PR #246 merged at `aefbc68` on a GREEN re-proof
  (pull/246 issuecomment-7103972437); both checkouts pulled.
- 2026-11-23: Ben's "Both" by button: #248 dispatched ahead of the
  merge line (issues/248 issuecomment-7103854424), and a read-only pass
  of the 14 older PRs; then "Send to planner (Recommended)" for the
  four that need a call.

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
- A builder that is no longer listed is followed up with
  `resume_plain.ps1`; it wakes with its saved options (settings, mode).
  A quiet transcript is not a stopped builder (it may sit in
  `gh pr checks --watch`): watch `claude agents` state instead.
- The re-proof runs the live clone's `reproof.py`, never a PR's copy:
  a change to the tool takes effect only after it merges and is pulled.
- Before `git worktree remove` on Windows, scan the worktree for
  reparse points: git follows a junction and deletes what it points
  to (#250 Part 1).
- A squash merge leaves `git cherry` listing the branch's commits as
  missing. Compare trees (`git diff origin/main <branch>`) and list the
  branch for Ben; the cherry rule is not met by a tree match alone.
- Peers: Tools-central-planner, dff-central-planner,
  dff-central-builder-manager. Find them with ListAgents by name; ids
  change at a relaunch.
