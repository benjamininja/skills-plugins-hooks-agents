# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
`PROJECT-RULES.md`; this file is state.

## START HERE

Written 2026-11-25 by the tools manager (session Tools-builder-manager,
queue id `dabbbcd0-2b97-445e-a2d9-4502691fb617`), at a clear prep on
Ben's word. After the clear Ben retypes
`/session-dispatch-managers-build-review:session-dispatch` and the new
queue id goes to the peers. `origin/main`, the main checkout and the
live clone are all at `acae1e7` (#288).

Peers: Tools-central-planner (`c4259ce4`), personal-assistant
(`ff1e3261`), dff-central-builder-manager, dff-central-planner (lead
reader for shared rules; Ben's condition for Windows' return), builders
t187-windows-time and t283-ci-scope by name.

**Ben's CI stop (issues/187, from issuecomment-7167028313).** First
priority across all sessions: the cost of CI as the merge gate. Code
work stays stopped until #187's change is in; text-only PRs move again
since #284 merged (the planner's reading of Ben's button).

**Green now (PROJECT-RULES via #286, session-rules 0.5.1 via #288,
#287):** the ruleset's required checks (`pytest (ubuntu-latest)`,
`CATALOG.md is current`), no conflict (CLEAN, or UNSTABLE from a
Windows job alone), the hygiene hook, the review where due. Windows is
not part of Green on a PR until Ben says so; his conditions for its
return: the #187 research scopes it and dff-central-planner approves.
PRs run no Windows job at all (#284, `04b91c1`); Windows runs on a push
to main only. **Before each merge, read main's last finished run
(#287): red stops all merges until a fix or revert.** One merge-word
question may name several PRs; a head that takes main is asked again.
The merge word is Ben's in this chat; a go in the planner's chat
arrives as a report. GitHub's API had an incident on 2026-11-25
(GraphQL merge and comment calls failed for about 30 minutes); Ben
merged #265, #270 and #284 on the web page then.

Merged on 2026-11-25 since the last prep: #259 `c915c9f`, #252
`f70ebe2`, #265 `ab37521`, #270 `7064f34`, #284 `04b91c1`, #286
`cb7fc13`, #266 `15196f2`, #198 `3d6ed6d`, #287 `8bdf0da`, #288
`acae1e7` (merged by the planner on Ben's word there). Branch
`t217-portable-roles` deleted on Ben's word.

Next, in order:

1. **Main's Windows runs** at `04b91c1` onward were still running at
   the prep. Read the last finished run first; a Windows result on
   `04b91c1` goes on #283 as the push half of amendment 2's proof.
2. **#187** (t187-windows-time, medium, session `2bc62b36`): finding
   posted (issues/187 issuecomment-7168273303): about 80% of Windows
   time is `test_git_guardrails.py` (Git Bash plus 150 to 250 child
   processes per hook run); 722 tests baseline; 2 Windows-only failures
   in 413 runs, none on main; options a to g, a/b/c/e/f need Ben, g
   ruled out. Waits for the planner's ruling; then resume t187 for
   Part 2 (the change, one PR). #283's addition (facts for a Windows
   budget, four points) was sent to t187 and is in the finding.
3. **Closeouts owed** (closeout script from #252 now on main): t283
   (`8cbd6fb8`, #284 merged), t250 (#252 merged; its CATALOG.md working
   copy differs in line endings only), t257 (#259), t260-261 (#272),
   t219 (#271), t189 (#268). Each after its builder has stopped.
4. **#251** (t251, `4c191e7f`): rows 3 and 4 on record (issuecomment-7168534999);
   row 3 stopped at 39% with no failure. The planner rules whether it
   reruns, then t251 resumes for Part 2.
5. **#262 dispatch** on Ben's button once code work restarts (brief:
   issues/262 issuecomment-7162955348, -7163139510, -7164631610).
6. Then, each by the rules above: text PRs #238, #239, #216, #222,
   #227, #205, #208, #184, #197, #196, #256 (this state file); code PRs
   #242, #214, #211, #182 after the stop lifts. Gated on Ben's go:
   #240 step 2, #111's build, #263, #167, #192. #249 is the Supabase
   dispatcher's.
7. A code review for #284 and #288 was not run (Ben and the planner
   merged first); the planner takes any finding as a follow-up PR.
8. Left for Ben: t206's branch and worktree; branch
   `t161-reset-prompt-pointer`. `C:\Users\benha\.claude` stays on
   `settings/shared-rule-trial` until dotclaude#12 merges. After #252,
   the managers settings text as one Action (still owed).

**Windows hazard** (issues/250 issuecomment-7103861254): `git worktree
remove` follows a junction. Scan first: `Get-ChildItem -Recurse -Force
-Attributes ReparsePoint`.

## Builders running

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t187-windows-time` | #187 | medium | `2bc62b36` | none yet | dispatched 2026-11-25; finding posted; waits for the planner's ruling |
| `t283-ci-scope` | #283 | medium | `8cbd6fb8` | #284 merged `04b91c1` | done; closeout owed; its #283 state-back may be unposted (GitHub incident) |
| `t251-venv-setup` | #251 | medium | `4c191e7f` | none yet | Part 1 posted; rows 3-4 on record; waits for the planner |
| `t250-closeout-script` | #250 | high | `08a25cd7` | #252 merged `f70ebe2` | done; closeout owed |
| `t257-autoclose` | #257 | low | `a72dcbd0` | #259 merged `c915c9f` | done; closeout owed |
| `t260-261-readbudget` | #260, #261 | low | `d7e77ffa` | #272 merged `a445087` | done; closeout owed |
| `t219-drift-check` | #219 | medium | `750159d3` | #271 merged `e1fed0c` | done; closeout owed |
| `t189-dispatch-base` | #189 | medium | `2eb375b2` | #268 merged `4c5e387` | done; closeout owed |
| `t206-token-check` | #206 | low | `116a30e9` | #267 merged `450ee52` | not running; branch and worktree left for Ben |
| `t231-reproof-lock` | #231 | medium | `8506434b` | #242 at `b278602` | not running; code PR, waits for the stop to lift |
| `t237-path-move` | #237 | low | `f0de4ab6` | #239 at `c64cf25` | not running; waits for its turn |
| `t244-pytest-hang` | #244 | medium | `9fd98bc0` | #246 merged | stopped; left for #250's script |

## Open PRs

The line now is START HERE item 6. The older table, each read again
before its re-proof (#198 merged as `3d6ed6d`):

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

The queue file is empty at this state-back. Waiting on Ben, by button
at each turn: merge words for the text PRs in START HERE item 6; the
#262 dispatch once code work restarts; Ben's say on Windows' return to
PRs (after #187's research and dff-central-planner's approval); the
merge of benjamininja/dotclaude#12; the managers settings text as one
Action.

## Queue entries raised

- 2026-11-24, Action: trial deny rule in the user-level settings file
  (#219), raised by the planner; Ben marked it done the same day and
  the entry left the queue.

- 2026-11-19, Decision: #231 builder parked at Part 1. Answered the same
  day: Ben chose "Rule from reading (Recommended)" (issues/231
  issuecomment-7024139524); the entry left the queue.

## Decided since

- 2026-11-25, fourth prep, by Ben's words and buttons in the tools
  manager's chat: merge #252, #265, #270, #286, #266, #198, #287;
  dispatch #283 (t283-ci-scope) and #187 (t187-windows-time); amendment
  2's matrix proven by CI, the builder's refused docs read not routed
  elsewhere; Ben discarded a stray uncommitted test.yml line in the main
  checkout (command shown to him); delete branch t217-portable-roles;
  run #251 rows 3 and 4 (row 3 later stopped for #187's timings). Ben's
  CI stop and Green rule are on issues/187 (from issuecomment-7167028313)
  and in PROJECT-RULES (#286). Lesson: a command for Ben goes inside the
  pop-up too, since the pop-up may be all he sees.

- 2026-11-25, third prep, by Ben's words and buttons in the tools
  manager's chat: stop #274's local run and merge on CI green (merged
  `a6d23d6`, pull/274 issuecomment-7164741435), after Ben asked why
  45-minute local runs were spent on text-only PRs; merge #268, #271,
  #272 (merged `4c5e387`, `e1fed0c`, `a445087`); 259, 265, 272 and 271
  approved to merge; dispatch #251 now (t251-venv-setup); resume t250
  for #252's main merge; Ben runs the `.venv-light` lines himself after
  the manager's permission check refused them. Ben made the three CI
  checks required on main and switched the stored login to the narrowed
  token (#204).

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
- Never add `2>&1` to a `dispatch.ps1` or other script call in Windows
  PowerShell 5.1: git writes progress to stderr, and the redirect turns
  it into an error that stops the script (2026-11-25, #251).
- A `.pth` or other file Python reads is written with `-Encoding ascii`
  in PowerShell 5.1; `utf8` adds a byte-order mark (#251).
