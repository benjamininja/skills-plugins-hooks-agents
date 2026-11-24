# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
`PROJECT-RULES.md`; this file is state.

## START HERE

Written 2026-11-24 about 17:20Z by the tools manager (session
Tools-builder-manager, queue id `e7026592`), at a clear prep on Ben's
word. `origin/main`, the main checkout and the live clone are all at
`f6ce9b1` (#255 merged). After the clear: Ben types
`/session-dispatch-managers-build-review:session-dispatch` again; send
the new queue id to Tools-central-planner, dff-central-planner and
dff-central-builder-manager. dff-central-builder-manager cleared too;
its new id comes by message, and until then it is addressed by name.

**PR #210's re-proof is RUNNING** in the background, started about
16:05Z from the live clone at `a30c3fa` on main `f6ce9b1` (the last run
took 61 min). Its output goes to a session scratch file, which the reset
prompt names. Its summary prints only at the end. After a clear the
finish notice does not come. Check for a python `reproof.py` process
first. If none remains and there is no `RESULT:` line, run it again:
`tools/reproof.py 210 a30c3fa7d232d3b6a17ec9371a35374e206b23dc` from the
live clone with the main checkout's `.venv` interpreter, after a start
notice to dynasty. `pre-commit run --all-files` at `a30c3fa` already
**passed** (in a throwaway detached worktree; the hook is
`python -m pre_commit` from the Python312 install, not the venv). It is
not yet posted.

**Test line** (agreed with dynasty): tools #210 (now), dynasty #684,
dynasty #690, dynasty #689, then tools #267 and #268. One full run on
the machine at a time, with start and end notices.

**Rules kept:** the merge word is asked of Ben by button at the
re-proved head for every PR, a builder's included (role file). A go
given in a planner's chat is a report: re-ask Ben by button, quoting the
record. Every hand step in a queue entry names its file by full path in
a code mark of its own (Ben's correction, 2026-11-24).

Next, in order:

0. **When #210's run ends:** post the output and the pre-commit pass on
   PR #210. On GREEN, ask Ben's merge word by button at `a30c3fa`, then
   squash-merge **without `--delete-branch`** (PRs #265 and #266 are
   stacked on `t161-reset-prompt-pointer`; tell the planner before that
   branch is deleted). Closeout pulls of both checkouts. End notice to
   dff-central-builder-manager. One line to the planner. Message
   `t260-261-readbudget` to run `git fetch origin`, then
   `git merge origin/main`, and build (Ben's button: wait for #210,
   issues/261 issuecomment-7137335139).
1. **PR #267** (#206, t206, head `b99dcae`): review closed, F1 to F4
   fixed, N1 and N2 advisory (pull/267 issuecomment-7137992307). Only the
   full re-proof is left (no pre-commit scope: `tools/` and `tests/`
   only), at its turn on the line. Then Ben's merge word, merge, pulls,
   close out t206.
2. **PR #268** (#189, t189, head `c446faa`): round one is out to the
   builder. F1 is blocking and confirmed by the manager: the `-Apply`
   worktree add has no base. F2 is blocking: resolve
   `refs/remotes/<base>`. F3 is advisory. Records: pull/268
   issuecomment-7138014936, and the dry runs at issuecomment-7137993262.
   On the builder's new head: a fresh reviewer re-checks (packet:
   re-check, high), the manager decides, then the dry runs again, the full
   re-proof and pre-commit, then Ben's word. Merge main first if #210
   has landed. After it merges, dispatch takes `-Base origin/<branch>`
   from a brief's `Base:` line.
3. **PR #271** (#219, t219 `750159d3`, head `d7795c9`): reported green
   after the clear prep (state-back issues/219 issuecomment-7138242550;
   `tests/test_drift_check.py` 45 passed). Not yet reviewed. Owed: the
   code review (medium: full, high), then the full re-proof at its turn on the line,
   and the script run against the real files (expect P11 to differ by 1,
   the learning-script link, plus counts on P6 and P8). The PR body asks the planner
   two things: how P6 handles allow rules, and that an optional template with no real file
   prints skipped.
4. **#269** (planner PR, route 2, no builder): the before figure is
   posted (issues/269 issuecomment-7137665661, about 54.9k). After its PR
   merges on Ben's word and the closeout pull, the **first builder
   dispatched** gives the after figure: the first-turn usage in its
   transcript, under `~/.claude/projects/<slug>/<session>.jsonl`. That
   same builder runs `git log -1 --grep=shared-rule-trial` for the #219
   trial (it must be denied). Post both results.
5. **#219 trial:** the desktop result is posted: denied, live without a
   restart (issues/219 issuecomment-7137847286). The rule is in
   `C:\Users\benha\.claude\settings.json`, committed on branch
   `settings/shared-rule-trial`, with PR benjamininja/dotclaude#12 for
   Ben to merge. **`C:\Users\benha\.claude` is checked out on that
   branch:** do not switch it to main before #12 merges, or the rule
   leaves the live settings. After the merge, on Ben's word: switch to
   main, then pull.
6. **PR #259** (#257, head `85186e1`): review done, one advisory;
   pre-commit passed. Re-prove with the plugin test step, Ben's word,
   merge, close out t257 (`claude stop` first). It shares files with
   #197: whichever merges second takes main and the next version.
7. **PR #252** (#250, head `a417165`): review closed, the three fixes
   and the ADR-0020 row verified. Re-prove, Ben's word, merge. Then one
   Action with the managers settings text.
8. **PR #197** (head `b7ef918`). Then planner PRs #265 and #266 (text,
   stacked on #210, Ben's approval), #238 (before #239), #239, and #242
   (then send the lock format text to dff-central-planner for dynasty
   #620). Then the older line below, in the planner's order.
9. Gated, each needing Ben's go by button at its turn: #240 step 2,
   #111's build, #262's build, #263, and the planner's list (#187, #167
   after #242, #192). **#262 asks the manager:** say on #262 whether
   `session-dispatch` survives. It survived the compact of 2026-11-24,
   and after this clear Ben retypes it. Not yet posted on #262.
10. **#111 part 5:** on the next real Mark done of an entry naming
    another running session, record on #111 whether that chat got the
    line, with both times. (The 10:32 Mark done named this session, so
    it does not count.)
11. t244 closeout is left for #250's script (pull/246
    issuecomment-7104203919). Trim still owed once #231 and #237 close
    (pull/236 issuecomment-7082192929).

**Windows hazard** (issues/250 issuecomment-7103861254): `git worktree
remove` follows a junction. Scan first: `Get-ChildItem -Recurse -Force
-Attributes ReparsePoint`.

## Builders running

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t260-261-readbudget` | #260, #261 | low | `d7e77ffa` | none yet | holds until #210 merges, then merges origin/main |
| `t189-dispatch-base` | #189 | medium | `2eb375b2` | #268 at `c446faa` | answering review round one (F1, F2 blocking) |
| `t219-drift-check` | #219 | medium | `750159d3` | #271 at `d7795c9` | reported green; review and re-proof owed |
| `t206-token-check` | #206 | low | `116a30e9` | #267 at `b99dcae` | review closed; waits for the full re-proof |
| `t231-reproof-lock` | #231 | medium | `8506434b` | #242 at `b278602` | review closed; waits for re-proof |
| `t237-path-move` | #237 | low | `f0de4ab6` | #239 at `c64cf25` | review done; waits for re-proof |
| `t244-pytest-hang` | #244 | medium | `9fd98bc0` | #246 merged | stopped; left for #250's script |
| `t250-closeout-script` | #250 | high | `08a25cd7` | #252 at `a417165` | waits for re-proof (stop it before any resume) |
| `t257-autoclose` | #257 | low | `a72dcbd0` | #259 at `85186e1` | waits for re-proof |

Closed out on 2026-11-24, each with no commit left and the worktree
removed: `t254-gitattributes` (after #255's merge, `git cherry` clean),
`t264-context-size` (a find-out with no commits, issues/264
issuecomment-7137410487), `t248-adr-hygiene`, `t111-findout`,
`t240-findout`, `t262-findout`. `t175-reproofrule` (`9144aeda`, old
OneDrive path) is blocked with no pid; neither manager dispatched it, so
it is left for Ben.

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

The queue file has no entries. The #219 trial Action was done by Ben
on 2026-11-24 and left the queue at this state-back. Waiting on Ben,
by button at each turn: the merge words for #210, #267, #268, #259,
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
