# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in `PROJECT-RULES.md`
(the table of checks and "Merging on Green" since #292); this file is
state.

## Current

### Saved

2026-11-27, about 12:05Z, by Tools-builder-manager, queue id
`fbd93714-8c8b-49c7-b434-7dee4a8488fd`, at a compact prep on Ben's word.
`origin/main` is at `fb033c8` (#214). The main checkout and the live
clone are still at `3bdba9c`: the closeout pull is owed, held only until
#196's `tools/reproof.py` run in the live clone ends. Main's CI at
`fb033c8` is green. `session-dispatch` is armed in this session; a
compact keeps it.

### Next

1. **#196's re-proof.** `tools/reproof.py 196 8e602fe07f5d36c11699411e52d0293d2225b17f`
   is running in the live clone (background task). When it ends: post
   the re-proof (CI green at `8e602fe`, hygiene Passed, review closed at
   `7b8f1e9` with no findings, the plugin test result), send an end
   notice to dff-central-builder-manager, then ask Ben's merge word
   (plugins path).
2. **The closeout pull** (PROJECT-RULES steps 1 to 3) right after that
   run. The pull notice for #214 has gone to the dff manager and both
   planners; send both heads after it.
3. **Four dispatches, each on Ben's go of 2026-11-27 in this chat,**
   each after the pull, dry run then `-Apply`. The manager keeps the
   brief files privately; each can be rebuilt from its record:
   - #242 fix, `t231-reproof-lock`, medium, `-Base origin/worktree-t231-reproof-lock`
     (brief: the test fake takes the third argument; pull/242
     issuecomment-7217511580).
   - #211 fix, `t168-gitgate`, high, `-Base origin/worktree-t168-gitgate`
     (F11, the ADR-0017 README row, one sentence naming #295; the
     ruling is pull/211 issuecomment-7217630964). Right after it starts,
     send F11's text from the draft advisory, section the re-check at
     5f95725, by message.
   - #263, a new name such as `t263-usage-scripts`, medium, base
     `origin/main`, brief = issues/263 issuecomment-7217315745's code
     block. Then relay the personal-assistant's nine hand-over messages
     (the method points and eight scripts' source) word for word. The
     manager keeps a private copy; if it is lost, the personal-assistant
     resends.
   - #251 Part 2, a new name such as `t251b-setup-lists`, medium, base
     `origin/main`, brief = issues/251 issuecomment-7217395316's code
     block. Before its merge the manager owes the bounded run in the
     `t251-venv-setup` worktree
     (`.venv-light/Scripts/python.exe -m pytest -q tests --ignore=tests/test_git_guardrails.py`),
     the hook runner as `python -m pre_commit`, and the two dry runs.
4. **#197** (t161-queuemod, session `5c12c706`, waiting): review round
   closed with no blocking finding (pull/197 issuecomment-7217599451);
   CI green and hygiene Passed at `cd6259b`; `claude plugin validate`
   passed on Ben's word, with the same type warnings as main plus the
   new `sessions.test.ts`. Owed: `tools/reproof.py 197 <full sha>`
   after #196's run (one run at a time; ask the dff manager first),
   post the re-proof, then Ben's merge word. Then #293 (brief at
   issues/293 issuecomment-7217264766) takes main and is dispatched on
   Ben's go.
5. **#211 after its fix:** a fresh re-check of F11 alone, the hook
   tests run by the manager (PROJECT-RULES, a hook's blocking rules),
   then the re-proof. Ben's merge ask must state that four classes
   (F3, F4, F6, F7) still pass for the local destructive commands,
   pass on main too, and are tracked on #295.
6. **#242 after its fix:** it merges on Green alone (`tools/`, `tests/`).
7. **#256**, this branch's PR: at a check-in, merge `origin/main` in,
   push, ask Ben's word.

### Waiting

- On Ben: the merge words for #196 and #197 once re-proved; the
  dotclaude#12 merge; the managers settings text as one Action. The
  queue file holds no open entry.
- On builders: t161-queuemod waits for the re-proof of #197.
- On the planner: #294 (Tier: low) gets a brief after #197 merges.
- Parked: #182 until #251 lands (pull/182 issuecomment-7217186548).
- Left for Ben, unchanged: worktree `s70-guard`, `t112-closeout-pulls`,
  branch `t161-reset-prompt-pointer`, `~/.claude` on
  `settings/shared-rule-trial` until dotclaude#12 merges.

### In flight

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t161-queuemod` | #161 | high | `5c12c706` | #197 at `cd6259b` | waiting for the re-proof; CLEAN |
| `t231-reproof-lock` | #231 | medium | none yet | #242 at `0e58d68` | red (test fake); fix dispatch owed |
| `t168-gitgate` | #168 | high | none yet | #211 at `5f95725` | red (ADR row) + F11; fix dispatch owed |
| `t179-answerhold` | #179 | low | n/a | #196 at `8e602fe` | CLEAN; plugin test running |
| `t175-reproofrule` | #175 | low | `9144aeda` | #182 at `5632555` | parked until #251; local branch at an older `69a4158` |
| `t251-venv-setup` | #251 | medium | `4c191e7f` | none | keeps `.venv-light` for the bounded run |

Open PRs: 256, 242, 211, 197, 196, 182.

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
- `tools/reproof.py` takes the full 40-character head sha.
- Hygiene: `C:\Users\benha\AppData\Local\Programs\Python\Python312\python.exe -m pre_commit run check-in-hygiene --from-ref origin/main --to-ref HEAD`
  in a temporary detached worktree of the PR head, removed after a
  junction scan.
- Closeout: the live clone's plugin `scripts/closeout.py <main checkout> <name>`,
  dry run then `--apply`, with the main checkout's `.venv`.

### Decided since the last merged state PR

- 2026-11-27, Ben's buttons in the tools manager's chat:
  - #182 parked until #251 lands (pull/182 issuecomment-7217186548).
  - #197 first, then #293; #197's rework dispatched (pull/197
    issuecomment-7217237886).
  - The tools manager ran Update branch on #242, #214, #211 and #196 on
    Ben's direct word (comments on each PR).
  - Merge #214 at `ae9fc32` (`fb033c8`); t207 closed out.
  - Fix #242 with a fresh medium builder; fix #211 with a fresh Opus
    builder; dispatch #263 and #251 Part 2.
  - `claude plugin validate` for #197 run on Ben's word.
- 2026-11-27, #211 rulings: F11 upheld; F3, F4, F6, F7 moved to #295
  with the planner's agreement (pull/211 issuecomment-7217630964).
  The GLOBAL_OPT gap pointer is on #200; detail in the draft advisory.
- 2026-11-27, #197 review F1 filed as #294.
- 2026-11-26, Ben's buttons in the tools manager's chat:
  - Resume t187 for #187 Part 2 (issues/187 issuecomment-7191766144).
  - Ben unlocked t283's stale worktree lock; t283 closed out
    (issues/283 issuecomment-7191791109).
  - Merge #290 (`e3a342f`); #239, #238, #216, #208 (`ede2171`,
    `94ce7e2`, `35302b6`, `63b678f`; #237 closed).
  - Ignore the Google Sheet in the browser pane.
  - Clear the closeout backlog: 32 of 32 removed (issues/250
    issuecomment-7193535351).
  - Merge #227, #222, #205 when main is green (`0c996a8`, `dd6277d`,
    `4a4b2c7`).
  - Merge #184 (`8f12b86`), #249 (`40e5847`), #291 (`6e4cc59`) and #292
    (`3bdba9c`), each after the lead's read.
  - The tools manager may run `gh pr ready 291` (it was already ready).
  - Ben added `pytest (windows)` to ruleset 27266678 (issues/187
    issuecomment-7194856150; it took a second save).
- 2026-11-26, closed out: t250, t257, t260-261, t219, t189, t283, t237,
  t187 (issues/187 issuecomment-7194664435).
- 2026-11-26, F11 on #211 ruled advisory (pull/211
  issuecomment-7193764388).
- 2026-11-26, Ben's buttons in the planner's chat (reports, on record):
  the stop lifted (issues/187 issuecomment-7193345327); Windows
  required, 6 shards (issuecomment-7193473530).
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
