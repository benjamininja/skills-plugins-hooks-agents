# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
`PROJECT-RULES.md`; this file is state.

## START HERE

Written 2026-11-24 13:25Z by the tools manager (session
Tools-builder-manager, id `5074d20f`), after the clear of 2026-11-23.
**PR #236 is merged** at `20f0954` on Ben's "Post and merge
(Recommended)" (pull/236 issuecomment-7132452441). `origin/main`, the
main checkout and the live clone are all at `20f0954`. The state
branch took a merge of `main` and goes on in a new PR. The role is in
full ("Hand-over done" on #228). `session-dispatch` was typed by Ben
in this session; it must be typed again after every clear (a compact
keeps it).

**One full test run on the machine at a time**, by message with
dff-central-builder-manager until #231's lock (PR #242) merges and is
pulled: a start notice before, an end notice after. **The line is with
tools** since 2026-11-24 13:21Z, for the re-proof of PR #253 at
`b958ffa` on `20f0954` (memory at start: 4.6 GB free, commit 41.8 of
56.2 GB). When it ends: end notice at once, then **dynasty has the
line next** (dynasty PR #659, about 5 minutes); PR #255's re-proof
starts only after dynasty's end notice. A full run takes about 59
minutes (608 tests). No builder runs a full suite without the line.

**Written again at a compact prep, 2026-11-24 about 13:50Z.** Since
the lines above: PR #256 is this file's PR; `check-in-hygiene` passed
over #253's branch (run with the system Python 3.12,
`python -m pre_commit run --from-ref origin/main --to-ref HEAD` in the
builder's branch); PR #255 (#254, head `ec8d30d`) had its code review,
no findings (pull/255 issuecomment-7132924099), and waits for its
re-proof with `pre-commit` not needed (one file, `.gitattributes`).
The owner-queue mod's planning moved to Tools-central-planner (issues/137
issuecomment-7132702847); #137's Bring to Chat is not built.

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

0. **t244 closeout is left for #250's script**, on Ben's button
   ("Leave for #250 (Recommended)", pull/246 issuecomment-7104203919):
   its branch `worktree-t244-pytest-hang` and its worktree stay. No
   `claude rm` was run.
1. **#236** is merged (above). Its Green is spent: every other PR is
   re-proved on `20f0954` or later.
1a. **#253** (#248's builder PR, `b958ffa`): code review closed, six
   advisories all fixed and accepted (pull/253
   issuecomment-7104501918). Re-prove next, once dynasty's end notice
   arrives, with a start notice first and `pre-commit` run
   by the manager (the PR touches `docs/adr/`; the main checkout's
   `.venv` holds no `pre-commit` and none is on PATH, so find the
   runner first); read Windows CI green on one read. A builder PR for a dispatched ticket: merge on Green with
   no further word. After it merges, every PR that adds an ADR needs a
   row in `docs/adr/README.md` or its re-proof fails (#184, #205, #211,
   #249; the planner is told), and #249 must correct the roles row.
   Then close out `t248`: list its leftovers for Ben as with t244.
   ADR-0012's new note says the manager removes the empty, untracked
   `hooks/continual-learning/` folder in the main checkout before any
   `relink_live.ps1 -Apply`: ask Ben by button before removing it.
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
   **#250**: the planner's ruling on Part 1 (issues/250
   issuecomment-7103994943) and its amendment (issuecomment-7104205770)
   went to `t250` whole, on Ben's "Confirm, send (Recommended)"
   (issuecomment-7104196182). The second amendment (points 16 to 22,
   issuecomment-7104581056) went whole by resume on 2026-11-24, on
   Ben's "Confirm, send whole (Recommended)" (issuecomment-7132487415).
   PR #252 at `ab3c279` predates it: no code review (full, high) and no
   re-proof until `t250` answers points 16 to 22 at a new head. The
   builder asks the manager for the test line before any full run.
   **#254** (low, Profile none): dispatched 2026-11-24 as
   `t254-gitattributes` on Ben's "Dispatch when level (Recommended)"
   (issues/254 issuecomment-7132504195). **#251** (medium)
   only once the planner posts its brief after #189's PR merges (Ben's
   go given here 2026-11-23). **#137** Bring to Chat + auto-close: Ben
   chose a planner refresh; dff-central-planner folds #137 and #111 and
   adds auto-close (issues/137 issuecomment-7103524615); ask Ben's go by
   button when its brief is posted. PRs #196/#197 touch the same file.
   **#249** (planner PR, #247) joins the planner PRs after #205.
8. Trim still owed (Ben's button, pull/236 issuecomment-7082192929):
   once #231 and #237 close, drop the 2026-11-19 history. "What this
   session answers for" was dropped on 2026-11-24; the role file holds
   it.

## Builders running

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t231-reproof-lock` | #231 | medium | `8506434b` | #242 at `b278602` | review closed; waiting for re-proof (state-back issues/231 issuecomment-7025354702) |
| `t237-path-move` | #237 | low | `f0de4ab6` | #239 at `c64cf25` | review done; waiting for re-proof |
| `t244-pytest-hang` | #244 | medium | `9fd98bc0` | #246 merged at `aefbc68` | stopped; branch and worktree left for #250's script (step 0) |
| `t250-closeout-script` | #250 | high | `08a25cd7` | #252 at `ab3c279` | resumed 2026-11-24 with the second amendment; working; no full run without the test line |
| `t248-adr-hygiene` | #248 | low | `f328d768` | #253 at `b958ffa` | stopped; review closed; waits for the re-proof (step 1a) |
| `t254-gitattributes` | #254 | low | `cd093765` | #255 at `ec8d30d` | reported green; review done, no findings; waits for the re-proof |
| `t257-autoclose` | #257 | low | `a72dcbd0` | none yet | dispatched 2026-11-24 on Ben's "Dispatch now (Recommended)" (issues/257 issuecomment-7133071425); shares three files with PR #197 |
| `t111-findout` | #111, first step | high | `6145f7ac` | none: it posts one comment | dispatched 2026-11-24 on Ben's "Dispatch now (Recommended)" (issues/111 issuecomment-7133071967); the build is not dispatched |

The first two are not listed by `claude agents` since the app restart;
check before closeout. `t244`'s first session `8ef7acf3` was stopped
(its Bash was refused after the memory kill); its worktree is reused.
`t175-reproofrule` (`9144aeda`, old OneDrive path) is blocked with no
pid; neither manager dispatched it, so it is left for Ben.

## Open PRs

In the line now: #253, #238, #239, #242 (above). The older line, each
read again before its re-proof:

| PR | Head | Subject |
|---|---|---|
| #227 | `1b4200b` | machine layout and cold setup (#223); planner fixed five stale paths; Ben's approval of 2026-11-15 covered `63c6445` only |
| #222 | `f85a7b4` | one plugin source (#195) |
| #216 | `3e99496` | ruleset setup guide (#193) |
| #214 | `a6d7a6c` | resume_plain.ps1 input checks (#207) |
| #211 | `7c1bafb` | git-guardrails git name (#168) |
| #210 | `dce2100` | reset prompt is a pointer (#161) |
| #208 | `0f1e1a1` | git restore command form |
| #205 | `bb80384` | ADR-0018 threat model (#190) |
| #198 | moving | the planner's live state branch; not in the line until the planner names a head (pull/198 issuecomment-7104044082) |
| #197 | `b7ef918` | owner-queue clear prep (#161) |
| #196 | `7b8f1e9` | owner-queue Answer hold (#179) |
| #184 | `8acbb17` | one queue per project (#183); planner rework, main merged in; Ben's approval asked at its turn (pull/184 issuecomment-7104045891) |
| #182 | `5632555` | re-proof one script, one rule (#175); keeps its place, no rework (pull/182 issuecomment-7104046736) |

Read-only pass of 2026-11-23 at `f1ff785`: #222, #216, #214, #211,
#210, #208, #205, #197 and #196 merge clean with CI green. The planner
ruled on the other four on Ben's button ("Send to planner
(Recommended)"); the rulings are in the table. #181 is closed without
merging on Ben's button (pull/181, superseded by #198). Also open:
#249 (planner PR, #247) and #252 (t250's, out of draft).

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
send the new queue id to both planners and the dynasty manager (done
2026-11-24). Coming later, each by button when it is ready: the merge
words for #238, #239 and #242 after their re-proofs; the removal of
the empty `hooks/continual-learning/` folder after #253 merges; the
go for #137 once dff-central-planner posts its brief.

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
- 2026-11-23: Ben's three buttons after the #246 merge: "Confirm, send
  (Recommended)" for the #250 ruling (issues/250
  issuecomment-7104196182); "Leave for #250 (Recommended)" for t244's
  leftovers (pull/246 issuecomment-7104203919); "Close #181
  (Recommended)" (closed with a comment on the PR).
- 2026-11-23: PR #253's code review closed (pull/253
  issuecomment-7104501918); the reviewers' four read-only calls beyond
  their packets are recorded on #248.
- 2026-11-24: Ben's three buttons after the clear: "Post and merge
  (Recommended)" for PR #236, merged at `20f0954` on the GREEN
  re-proof of 2026-11-23 (pull/236 issuecomment-7132452441), both
  checkouts pulled; "Confirm, send whole (Recommended)" for #250's
  second amendment (issues/250 issuecomment-7132487415); "Dispatch
  when level (Recommended)" for #254 (issues/254
  issuecomment-7132504195).

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
- After a squash merge of a state PR, the state branch takes a merge
  of `origin/main`; the state file conflicts (add/add) and the
  branch's copy is kept.
- Peers: Tools-central-planner, dff-central-planner,
  dff-central-builder-manager. Find them with ListAgents by name; ids
  change at a relaunch.
