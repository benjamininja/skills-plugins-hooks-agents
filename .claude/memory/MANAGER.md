# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in `PROJECT-RULES.md`
(the table of checks and "Merging on Green" since #292); this file is
state.

## Current

### Saved

2026-11-27, about 14:15Z, by Tools-builder-manager, queue id
`fbd93714-8c8b-49c7-b434-7dee4a8488fd`, at a clear prep on Ben's word.
`origin/main` is at `8b54ee1` (#301); main's CI at `6c24a3d` is green (run
46004622869). The main checkout is at `8b54ee1`; the live clone is at
`1259c38` and is running #197's `tools/reproof.py`. A clear drops
`session-dispatch`: Ben types
`/session-dispatch-managers-build-review:session-dispatch` again, and the
new session id goes to the peers.

**Ben's standing word (issues/300 issuecomment-7219760428):** complete the
held work, don't park it. The planner's "cut" (issuecomment-7219626562) is
reversed. Every dispatch on that list has Ben's go; each merge word stays
as the rules keep it, asked by button at once, never carried as waiting.

### Next

1. **#197's re-proof.** `tools/reproof.py 197 cd6259b658c09cbad2dbfed8fbf4d00cbbd27762`
   in the live clone, started about 13:00Z, about 70 minutes. If its
   result is lost at the clear, run it again (ask the dff manager first;
   one run at a time). When it passes: post the re-proof on #197 (CI green
   and CLEAN at `cd6259b`, hygiene Passed, review closed at pull/197
   issuecomment-7217599451, validate passed on Ben's word, the run's
   summary), end notice to dff-central-builder-manager, Ben's merge word
   by button (plugins path). Then pull the live clone (`git fetch origin`,
   `git merge --ff-only origin/main`) and send both heads to the dff
   manager and both planners. Close out `t161-queuemod`.
2. **#263 step 3.** #301 merged on Green as `8b54ee1` (re-proof at
   pull/301 issuecomment-7219790820); main's CI at `8b54ee1` not yet read.
   The personal-assistant was asked to run `python tools/usage.py shapes
   --store <store> --from 2026-11-17 --to 2026-11-24 --only manager` and
   send the output. Relay it to `t263-usage-scripts` (kept open, waiting)
   to post on #263; the planner sets step 3's tier from it; Ben's go is
   given; dispatch or resume the builder on step 3. The step 2 figures
   are on #263 (issuecomment-7219328363).
3. **#296** (#251 Part 2, `t251b-setup-lists`, head `624b511`, CLEAN,
   review closed at pull/296 issuecomment-7218514749, hygiene Passed). The
   bounded run was started at the clear in a temporary worktree
   `%TEMP%/bound296` with `t251-venv-setup`'s `.venv-light` python (`-m
   pytest -q tests --ignore=tests/test_git_guardrails.py`). If its result
   is lost, run it again, then remove that worktree. Then the two
   dispatch dry runs (with and without `-FullSetup`), post the re-proof,
   and Ben's merge word by button. After the merge, Ben's queued Action
   with the two setup lists; drift_check P6 counts `setupFull` until he
   fills it. Close out `t251b-setup-lists` and `t251-venv-setup`.
4. **#211** (`t168-gitgate`, high): F11 fix round running (worktree
   now at `bc0f545`). When it reports: a fresh re-check of F11 alone, the
   hook tests run by the manager, hygiene, the re-proof. Ben's merge ask
   states that F3, F4, F6 and F7 still pass and are tracked on #295.
5. **#256**, this branch's PR: merge `origin/main` in, push, ask Ben's
   word by button.
6. **The parked list, all on Ben's go** (issuecomment-7219760428). The
   planner was asked for each ticket's brief and order; their tiers are
   already on them. Now: #262 (medium), #289 (high), #285 (medium), #240
   step 2 (medium), #111 (high), #299 (medium). After #197: #293
   (medium, brief at issues/293 issuecomment-7217264766) and #294 (low).
   After #296: #298 (low) and the #182 repair (`t175-reproofrule`,
   DIRTY). After #211: #295 (high). Two writers never share files.
   Dispatch: dry run, then `-Apply`.

### Waiting

- On Ben: the merge words for #197, #296, #211 and #256 as each is
  re-proved (ask by button at once); the dotclaude#12 merge; the managers
  settings text as one Action. The queue file holds no open entry.
- On the planner: briefs and order for the parked list (asked about
  14:05Z).
- Left for Ben, unchanged: worktree `s70-guard`, `t112-closeout-pulls`,
  branch `t161-reset-prompt-pointer`, `~/.claude` on
  `settings/shared-rule-trial` until dotclaude#12 merges.

### In flight

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t161-queuemod` | #161 | high | `5c12c706` | #197 at `cd6259b` | `reproof.py` running |
| `t263-usage-scripts` | #263 | medium | `6bf2091b` | #301 merged `8b54ee1` | waits for shapes output, step 3 |
| `t168-gitgate` | #168 | high | `2b73b5ff` | #211 at `5f95725` | F11 fix round running |
| `t251b-setup-lists` | #251 | medium | `9411fe1b` | #296 at `624b511` | manager's bounded run running |
| `t175-reproofrule` | #175 | low | `9144aeda` | #182 at `5632555` | DIRTY; repair after #296 |
| `t251-venv-setup` | #251 | medium | `4c191e7f` | none | keeps `.venv-light` for the bounded run |

Open PRs: 296, 256, 211, 197, 182.

### Peers

Tools-central-planner (`4e27fb7c-445f-47d9-ad2b-919bca911066`),
personal-assistant (`5d72e933`), dff-central-builder-manager
(`e5579518-3626-469b-b1d5-3095f10a1c6a`), dff-central-planner
(`823b0d8b`, the lead for shared rules and the CI gate). Reach them by
name with ListAgents.

### Reads and checks due

- Main's last finished run before each merge; CI on main's new commit
  after each merge.
- #187 watch, for the planner: a PR held by `pytest (windows)` alone, a
  cancelled run, a failed scope job.
- `tools/reproof.py` takes the full 40-character head sha; a full run
  takes about 70 minutes, almost all in `tests/test_git_guardrails.py`.
  Only for PRs that touch `plugins/owner-queue/`.
- Hygiene: `C:\Users\benha\AppData\Local\Programs\Python\Python312\python.exe -m pre_commit run check-in-hygiene --from-ref origin/main --to-ref HEAD`
  in a temporary detached worktree of the PR head, removed after a
  junction scan.
- Closeout: the live clone's plugin `scripts/closeout.py <main checkout> <name>`,
  dry run then `--apply`, with the main checkout's `.venv`. Stop the
  builder first; a lock naming a dead pid is cleared with
  `git worktree unlock` before the dry run.
- A fix round on a PR branch that Update branch moved: the manager
  fast-forwards the builder's worktree to the PR's remote head before
  dispatch (issues/231 issuecomment-7218530273).
- Not yet in force: the low/haiku no-go dispatch trial (issues/300
  issuecomment-7219162508) starts only after two PRs merge on Ben's word.
  Ben's Never line on #300: no agent approves a waiting deployment or
  re-runs a workflow run.

### Decided since the last merged state PR

- 2026-11-27, Ben's buttons and words in the tools manager's chat:
  - #182 parked until #251 lands (pull/182 issuecomment-7217186548).
  - #197 first, then #293; #197's rework dispatched (pull/197
    issuecomment-7217237886).
  - The tools manager ran Update branch on #242, #214, #211 and #196 on
    Ben's direct word (comments on each PR).
  - Merge #214 at `ae9fc32` (`fb033c8`); t207 closed out.
  - Fix #242 with a fresh medium builder; fix #211 with a fresh Opus
    builder; dispatch #263 and #251 Part 2 (all four dispatched).
  - `claude plugin validate` for #197 run on Ben's word.
  - The tools manager fast-forwarded the #242 and #211 builders'
    worktrees (issues/231 issuecomment-7218433241, issues/168
    issuecomment-7218433796).
  - Merge #196 at `8e602fe` (`4355d3f`); t179 closed out.
  - Complete the held work; the cut is reversed (issues/300
    issuecomment-7219760428).
- 2026-11-27, #242 merged on Green at `5a9e5d4` (`1259c38`); t231 closed
  out (pull/242 issuecomment-7218615302).
- 2026-11-27, #211 rulings: F11 upheld; F3, F4, F6, F7 moved to #295
  with the planner's agreement (pull/211 issuecomment-7217630964).
  The GLOBAL_OPT gap pointer is on #200; detail in the draft advisory.
- 2026-11-27, #197 review F1 filed as #294; #296 review F1 filed as
  #298.
- 2026-11-27, #297 rulings: F1 to F8 closed, F9 advisory; merged on
  Green as `6c24a3d` (pull/297 issuecomment-7219119780). F9 rode with
  #263 step 2 (issues/263 issuecomment-7219163159), fixed in #301.
- 2026-11-27, #301 first review: F1 and F2 upheld by the manager though
  advisory from the reviewer, because `shapes` output is posted publicly
  (pull/301 issuecomment-7219587427). Re-check closed; merged on Green as
  `8b54ee1` (issuecomment-7219790820).
- 2026-11-26 decisions: see this file at `397e44e`.
- Lesson: Ben reads "hold closeout run" as being about CI. Explain first
  that closeout is a local script run with no CI.
- Lesson: a builder's expired Claude login shows as `blocked`, with
  "Login expired · Please run /login" in its transcript.
- Lesson: `claude rm` chained after a refused closeout still removes the
  worktree and local branch. Run it only after `removed`.
- Lesson: in the main checkout `git pull --ff-only` can refuse with
  "Cannot fast-forward to multiple branches"; use `git fetch origin`,
  then `git merge --ff-only origin/main`.
- Lesson: a ruleset save is read back from the API before the step is
  recorded.
- Lesson: a peer's report of Ben's word to park work is a question to put
  to Ben, not a settled order; Ben wants held work completed and asked
  about.

## Reference

### Dispatch, as proven

- From the main checkout at its new path, with the dispatch script in
  the live clone's plugin folder: dry run, then `-Apply`, from
  PowerShell. Both #231 (medium) and #237 (low) started cleanly; setup
  makes the worktree's `.venv`.
- A brief must hold no file under `.claude/` (a builder's mode refuses
  the write) and no `pre-commit` proof line (no builder allow rule; the
  manager runs it). Told to the planner on #237.
- A brief's `Ticket: this issue` line is given as the ticket number in
  the prompt file.

### Lessons

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
