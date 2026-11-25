# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
`PROJECT-RULES.md`; this file is state.

## START HERE

Written 2026-11-25 by the tools manager (session
Tools-builder-manager, queue id `dabbbcd0-2b97-445e-a2d9-4502691fb617`),
at a second compact prep on Ben's word. A compact keeps the session id
and the `session-dispatch` skill; after a clear Ben retypes
`/session-dispatch-managers-build-review:session-dispatch` and the new
queue id goes to the peers. `origin/main`, the main checkout and the
live clone are all at `450ee52` (#267 merged 2026-11-25, after #210 at
`f873dd3`).

Peers: Tools-central-planner (`ad857488`), dff-central-builder-manager
(`4ff97ebc`), dff-central-planner (by name).

**Nothing tools runs at the prep.** Dynasty holds the test line for its
#689 and #692, back to back; its end notice hands the line to tools for
PR #274.

**Test line** (agreed with dynasty): dynasty #689, #692 (running), then
tools #274 (Ben's button 2026-11-25), #259, #268, #265 and #272, #271.
One full run on the machine at a time, with start and end notices.
**After #274 merges and is pulled, its rules replace these** (#273): CI
at the PR's head with merge state CLEAN is the test proof, no local full
run except an owner-queue PR's `reproof.py`; a Green holds while the head
is unchanged; read CI on main after each merge; one merge-word question
may name several PRs.

**Rules kept:** the merge word is asked of Ben by button at the
re-proved head for every PR (role file). A go or approval given in a
planner's chat is a report: re-ask Ben by button, quoting the record.
Never `cd` into a builder worktree in a Bash or PowerShell call: the
harness moves the session's working directory; use `git -C`.

Next, in order:

1. **PR #274** (planner, #273, head `72453f7`; all three of the
   manager's points taken, pull/274 issuecomment-7164121459): after
   dynasty's end notice, start notice, full re-proof under today's rules,
   pre-commit (it touches PROJECT-RULES.md and the role file), Ben's
   merge word, merge, closeout pulls with the rules-change notice to the
   other manager and both planners first. #267 is closed: GREEN at
   `b99dcae` (pull/267 issuecomment-7164176257), merged at `450ee52`;
   builder t206's branch and worktree are left for Ben (squash merge, so
   `git cherry` lists its commits; the files match main).
2. **PR #259** (#257, click to close, head `85186e1`): review done, one
   advisory; pre-commit passed. Re-prove with the owner-queue plugin test
   (it keeps `reproof.py` under #274 too), Ben's word, merge, pull the
   live clone, tell Ben a new session loads the mod. Shares files with
   #197.
3. **PR #268** (#189, head `8272b9a`): re-check accepted F1 to F3,
   ruling posted (pull/268 issuecomment-7162472269); planner no breach
   (issuecomment-7162486091); dry runs clean (issuecomment-7162725979).
   Owed: merge main if needed, full re-proof, pre-commit, Ben's word.
   After it merges, dispatch takes `-Base origin/<branch>`; the first
   real `-Apply` is the proof of that path.
4. **PR #265** (planner, head `8f4b89e`, base main): Ben approved in the
   planner's chat (pull/265 issuecomment-7162899681), a report: re-ask.
   Keep branch `t217-portable-roles` after the merge until the planner
   retargets #266. **PR #272** (t260-261, #260/#261, head `869b260`,
   rule text only): light review, one advisory folded into #262
   (pull/272 issuecomment-7163121752); planner no breach
   (issuecomment-7163106276). #265 and #272 both set 0.4.0 and edit the
   clear-boundary section: the second to merge takes main (the planner
   reads that merge). #268 meets #265 in the two role templates.
5. **PR #271** (#219, head `7621bed`): review closed, all six accepted
   (pull/271 issuecomment-7163450315); planner no breach and F1 ruling
   (issuecomment-7162651862). Owed: full re-proof, and the script run
   against the real files.
6. **#262 dispatch** (medium, Profile none, Base origin/main): brief
   issues/262 issuecomment-7162955348 plus amendment -7163139510 (point
   11). Ben's go in the planner's chat (-7163080874) is to dispatch after
   #265 and #272 both merge: then ask Ben by button quoting it, dry run,
   `-Apply`.
7. **#269** (planner PR #270, head `0535c32`, approved by Ben in the
   planner's chat at pull/270 issuecomment-7162436664, a report): joins
   the line; after it merges, the first builder dispatched gives the after
   figure and runs `git log -1 --grep=shared-rule-trial` for the #219
   trial (it must be denied).
8. **#219 trial:** `C:\Users\benha\.claude` is on branch
   `settings/shared-rule-trial` until Ben merges benjamininja/dotclaude#12;
   do not switch it. Record: issues/219 issuecomment-7162465174.
9. **PR #252** (#250, head `a417165`; conflicts with main in `templates/MANAGER.md` after #210, so t250 merges main first, on Ben's button to resume it, pull/252 issuecomment-7163590008), **#197**, **#242**, **#239**,
   **#238**, **#266** (stacked on #265), then the older line below.
   Gated on Ben's go by button: #240 step 2, #111's build, #263, #187,
   #167, #192.
10. **#111 part 5** and the t244 closeout leftovers: as before
    (pull/246 issuecomment-7104203919; pull/236 issuecomment-7082192929).
11. Branch `t161-reset-prompt-pointer` (#210's, merged) is not a builder
    branch: on the owner's list, left in place.

**Windows hazard** (issues/250 issuecomment-7103861254): `git worktree
remove` follows a junction. Scan first: `Get-ChildItem -Recurse -Force
-Attributes ReparsePoint`.

## Builders running

After the app restart before 2026-11-25 no tools builder was listed;
two were resumed on Ben's buttons with `resume_plain.ps1` (each woke with
its saved options).

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t260-261-readbudget` | #260, #261 | low | `d7e77ffa` | #272 at `869b260` | resumed 2026-11-25; reported green; waits for re-proof |
| `t219-drift-check` | #219 | medium | `750159d3` | #271 at `7621bed` | resumed 2026-11-25; review closed; waits for re-proof |
| `t189-dispatch-base` | #189 | medium | `2eb375b2` | #268 at `8272b9a` | not running; review closed; waits for re-proof |
| `t206-token-check` | #206 | low | `116a30e9` | #267 merged `450ee52` | not running; branch and worktree left for Ben |
| `t231-reproof-lock` | #231 | medium | `8506434b` | #242 at `b278602` | not running; waits for re-proof |
| `t237-path-move` | #237 | low | `f0de4ab6` | #239 at `c64cf25` | not running; waits for re-proof |
| `t244-pytest-hang` | #244 | medium | `9fd98bc0` | #246 merged | stopped; left for #250's script |
| `t250-closeout-script` | #250 | high | `08a25cd7` | #252 at `a417165` | not running; waits for re-proof |
| `t257-autoclose` | #257 | low | `a72dcbd0` | #259 at `85186e1` | not running; next after #689 |

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

The queue file has no entries. The #219 trial Action was done by Ben
on 2026-11-24 and left the queue at this state-back. Waiting on Ben,
by button at each turn: the merge words for #274, #268, #259,
#252, #197, #265, #266, #238, #239, #242, #256 and #269's PR; the
merge of benjamininja/dotclaude#12; after #252 merges, the managers
settings text as one Action.

## Queue entries raised

- 2026-11-24, Action: trial deny rule in the user-level settings file
  (#219), raised by the planner; Ben marked it done the same day and
  the entry left the queue.

- 2026-11-19, Decision: #231 builder parked at Part 1. Answered the same
  day: Ben chose "Rule from reading (Recommended)" (issues/231
  issuecomment-7024139524); the entry left the queue.

## Decided since

- 2026-11-25, later, by Ben's buttons in the tools manager's chat:
  #274 goes next on the line, ahead of #259 (the planner wrote #273's
  simpler merge rule on Ben's word; the manager's three points, all
  taken, at pull/274 issuecomment-7164081041); merge PR #267 at
  `b99dcae` (GREEN, 640 passed, 61 min; merged `450ee52`, both
  checkouts pulled). Ben approved #227 at `1b4200b` and #265 at
  `8f4b89e` in the planner's chat (reports). #252 conflicts with main
  after #210 (pull/252 issuecomment-7163590008). Done ahead of the line:
  pre-commit passed on #268 at `8272b9a`, skipped on #272 (no files in
  scope); #271's drift check against the real files posted
  (issuecomment-7163837481).

- 2026-11-25, by Ben's buttons in the tools manager's chat: merge PR
  #210 at `a30c3fa` (merged `f873dd3`, both checkouts pulled, notices and
  heads sent); resume `t260-261-readbudget` (issues/261
  issuecomment-7162636577) and `t219-drift-check` (issues/219
  issuecomment-7162703919); re-prove #259 next after #267, ahead of
  #268. Posted: #262 (session-dispatch survives a compact, not a clear,
  issuecomment-7162476049); #219 (who committed the trial rule,
  issuecomment-7162465174).

- 2026-11-24, by Ben's buttons in the tools manager's chat: merge #255
  (merged `f6ce9b1`); t260-261 waits for #210 rather than an allow rule
  for another branch's merge (issues/261 issuecomment-7137335139); the
  dotclaude trial rule is committed by branch and PR (dotclaude#12).

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

- 2026-11-24, after the 14:50Z clear: Ben's buttons in the tools
  manager's chat: #260/#261 go ("Dispatch after #210", then "Dispatch
  stacked"); #189, #219, #206 all chosen, timing "After #255 ends";
  #264 "Dispatch second"; test line "Keep agreed order". Each is
  recorded on its ticket (links in START HERE item 0).

## Lessons

- Never pipe the dispatch script with `2>&1` in PowerShell 5.1: git's
  progress line on stderr becomes an error, and the script stops after
  the worktree add. Check the half-made worktree, remove it if clean,
  and run again without the redirect.
- A builder's brief that merges another branch is refused: builders may
  merge only `origin/main`. Until #268 lands, a stacked builder waits for
  its base to merge.

- A re-proof that looks hung: check pytest's children
  (`Win32_Process` with `ParentProcessId=<pytest pid>`). New `bash.exe`
  children with fresh creation times mean the git-guardrails tests are
  still running; pytest's own CPU stays near zero while they do.

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
- Never `cd` (Bash) or `Set-Location` (PowerShell) into a builder
  worktree: the harness moves the session's working directory there.
  Use `git -C`, or run a script by its full path.
