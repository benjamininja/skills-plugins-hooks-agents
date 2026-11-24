# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
`PROJECT-RULES.md`; this file is state.

## START HERE

Written 2026-11-24 about 14:40Z by the tools manager (session
Tools-builder-manager, id `5074d20f`), at a clear prep on Ben's word.
`origin/main`, the main checkout and the live clone are all at
`6f67165` (**PR #253 merged** 14:20Z on a GREEN re-proof, pull/253
issuecomment-7134126115). `session-dispatch` must be typed by Ben again
after the clear. After the clear, send the new queue id to both planners
and the dynasty manager.

**One full test run on the machine at a time**, by start and end notices
with dff-central-builder-manager until #231's lock (PR #242) merges and
is pulled. Dynasty's #669 run ended GREEN; tools gave the line to
dynasty for its #671 while it clears, so **wait for dynasty's end
notice for #671**, then tools takes the line for #255. A full
run now takes about 26 minutes (609 tests, the pytest step 1575s on
2026-11-24), not 59. Log memory before and after.

**The app restarted about 13:40Z** and killed #253's first background
run (no result); a long run never depends on the session staying up.

**Ben's choice on the queue** (button, 2026-11-24 about 14:15Z): items
that can wait stay as chat buttons at their turn, not queue entries,
while Ben is in the chat. The queue file has no entries.

Next, in order:

1. **PR #255** (#254, `t254-gitattributes`, head `ec8d30d`, one file
   `.gitattributes`): code review done, no findings (pull/255
   issuecomment-7132924099). On dynasty's end notice: start notice,
   re-prove, post, merge on Green (builder PR, no further word), pulls,
   close out t254.
2. **PR #259** (#257, `t257-autoclose`, head `85186e1`): version bumped
   on the planner's ruling (issues/257 issuecomment-7133159600, no plan
   breach). Code review: one advisory, F1, nothing blocking (pull/259
   issuecomment-7133398803); F1 goes into #111's build brief and holds
   nothing (issues/257 issuecomment-7133418739). `pre-commit` passed.
   Re-prove with the plugin test step (`plugins/owner-queue/` is
   touched), merge, close out t257 (it is idle-running: `claude stop`
   first). It shares files with PR #197: the second to merge takes a
   merge of main and the next version number.
3. **PR #252** (#250, `t250-closeout-script`): review closed after two
   rounds (round 1 pull/252 issuecomment-7133602626, F1 and F2 blocking,
   upheld; round 2 issuecomment-7133842294, all resolved). The planner's
   read: no breach, three text fixes (issuecomment-7133882719), done at
   `447f3fc`. After #253, t250 was sent to merge main and add ADR-0020's
   row to `docs/adr/README.md`; it reported green at `a417165` (main
   merged, the row added, `test_adr_readme.py` and `test_closeout.py`
   pass; state-back on #250). Check the three fixes and the row,
   re-prove, merge.
   After it merges: one Action for Ben with the real managers settings
   text (the closeout allow rule plus the `git branch` force deny lines
   from the example).
4. **The planner's order** (asked at Ben's word; pull/198
   issuecomment-7134281643). Test line: #255, #259, #252, then PR #197.
   Dispatch now, in order, each go record checked on its ticket first
   and each asked of Ben by button (a relay): #187 (medium, test speed
   find-out), #189 (medium), #219 (medium), #206 (low), #167 (medium,
   only after PR #242 merges), #192 first PR (medium). Nothing to close.
   Planner PRs #205, #184 and #249 have main and their ADR rows; PR #210
   at `a30c3fa` adds an In flight block to a manager's Current block
   (answers #262's point 3), Ben's approval to come. #211's builder must
   merge main and add ADR-0017's row.
5. Gated, each needing Ben's go by button at its turn: #240 step 2
   (ruled option A, brief issues/240 issuecomment-7133603553; after #259
   and #197 merge); #111's build (ruled, issuecomment-7133339403 and
   -7133604792; after #240 step 2); #260 and #261 (after PR #210); #262's
   build (ruled, issues/262 issuecomment-7134266469: Ben types the
   compact, the mod counts, a clear after the third; after #210, #260
   and #197); #263, #264. **#262 asks the manager:** at its next compact,
   check whether `session-dispatch` is still in force afterwards and
   say so on #262.
6. **#111 part 5** asks the manager: on the next real Mark done and
   Submit of an entry whose Session line names another running session,
   record on #111 whether that session's chat got the line, with both
   times.
7. Then #238 (merge word by button, before #239), #239, #242 (send the
   lock format text to dff-central-planner for dynasty #620 after), and
   the older PR line below, in the planner's order once it sends one.
   ADR PRs need a README row now (#184, #205, #211, #249; #249 must also
   correct the roles row; the planner is told).
8. **t244 closeout** is left for #250's script, on Ben's button (pull/246
   issuecomment-7104203919): branch `worktree-t244-pytest-hang` and its
   worktree stay.
9. Trim still owed (Ben's button, pull/236 issuecomment-7082192929):
   once #231 and #237 close, drop the 2026-11-19 history.

**Windows hazard** (issues/250 issuecomment-7103861254): `git worktree
remove` follows a junction. Scan first: `Get-ChildItem -Recurse -Force
-Attributes ReparsePoint`.

## Builders running

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t231-reproof-lock` | #231 | medium | `8506434b` | #242 at `b278602` | review closed; waiting for re-proof |
| `t237-path-move` | #237 | low | `f0de4ab6` | #239 at `c64cf25` | review done; waiting for re-proof |
| `t244-pytest-hang` | #244 | medium | `9fd98bc0` | #246 merged | stopped; left for #250's script |
| `t250-closeout-script` | #250 | high | `08a25cd7` | #252 at `a417165` | reported green; waits for the re-proof (stop it before any resume) |
| `t254-gitattributes` | #254 | low | `cd093765` | #255 at `ec8d30d` | waits for the re-proof |
| `t257-autoclose` | #257 | low | `a72dcbd0` | #259 at `85186e1` | idle-running; waits for the re-proof |

Closed out on 2026-11-24, each with no commit left and the worktree
removed: `t248-adr-hygiene` (after #253's merge, on Ben's button, both
branch copies deleted; the squash tree matched the tested tree),
`t111-findout`, `t240-findout`, `t262-findout` (find-outs, one comment
each). `t175-reproofrule` (`9144aeda`, old OneDrive path) is blocked
with no pid; neither manager dispatched it, so it is left for Ben.

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

The queue file has no entries; Ben chose chat buttons for waiting items
while he is in the chat (2026-11-24). Coming later, each by button: the
merge words for #238, #239, #242 and #256; the gos (relays) for the
planner's dispatch list (item 4); after #252 merges, the managers
settings text as one Action.

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

- 2026-11-24, after the 13:50Z compact: the planner ruled #259's
  version bump (no breach); #137 closed not planned on Ben's "Close now
  (Recommended)"; #240 step 1 dispatched on Ben's "Dispatch now
  (Recommended)" (issues/240 issuecomment-7133412676), finding posted,
  Ben chose option A in the planner's chat; #262 step 1 dispatched on
  Ben's "Dispatch now (Recommended)" (issues/262
  issuecomment-7134055165), finding ruled; PR #253 merged at `6f67165`;
  t248 leftovers and the empty `hooks/continual-learning/` folder
  removed on Ben's "Remove all three (Recommended)" and "Remove it
  (Recommended)" (pull/253 issuecomment-7134178626); Ben chose "Keep
  asking in chat" for the queue.

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
- `resume_plain.ps1` on a builder that is still running in the
  background (idle) starts a copy session without the builders'
  settings, which is refused every tool. `claude stop <short id>` an
  idle builder first. Never `claude rm` a copy: rm removes the worktree.
- `claude rm <id>` removes a stopped builder's clean worktree and its
  branch when nothing is unpushed; a worktree locked by a session is
  removed that way, not by `git worktree remove`.
- The git-guardrails hook reads a `gh ... --body` text too: a comment
  that quotes a force branch delete is blocked. Post with `--body-file`.
- A full run took 26 minutes on 2026-11-24 (609 tests), not 59.
- A finding about deny rules goes to the planner; the rules live in
  Ben's settings files, which no session writes.
