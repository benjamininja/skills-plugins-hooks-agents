# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in `PROJECT-RULES.md`
(the table of checks and "Merging on Green" since #292); this file is
state.

## Current

### Saved

2026-11-26, about 15:00Z, by Tools-builder-manager, queue id
`3bac2fdb-b847-4732-b572-e582ae2af312`, at a clear prep on Ben's word.
`origin/main`, the main checkout and the live clone are at `3bdba9c`
(#292). After the clear the id changes: send the new one to the peers,
and Ben types `/session-dispatch-managers-build-review:session-dispatch`
again before any dispatch, merge or closeout.

### Next

1. **Merging on Green is live** (PROJECT-RULES since #292; the ruleset
   read is on issues/187 issuecomment-7194905033). A builder PR whose
   paths are all under `tools/`, `tests/`, `docs/` outside `docs/adr/`,
   or the catalog files merges on Green alone. Any other path
   (`skills/`, `plugins/`, `hooks/`, `.claude/agents/`, `docs/adr/`, a
   root file, a settings file) keeps Ben's word, asked by button in
   this chat.
2. **Every open code PR takes main** before its next re-proof. Their
   heads predate #291, so they never reported `pytest (windows)` and
   show BLOCKED: #242, #214, #211, #196; #182 is also DIRTY (conflict).
   The builder merges `origin/main`; the manager re-proves at the new
   head and checks each one's paths against item 1.
3. **#211** (git-guardrails, #168): F11 is advisory, recorded
   (pull/211 issuecomment-7193764388). Owed: take main (28+ behind),
   then a fresh reviewer re-checks the ten blocking findings F1 to F10
   (all `fixed at 60248a6`; text in the draft advisory), then the
   re-proof, then Ben's word (hooks path). Before #289.
4. **Code gos owed from Ben**, by button: #289 (find-out first), #285,
   #262's rule-text build, #251's build. Merge questions once main is
   in: #214, #196, #242; #182 (keep both passages against #290, pull/182
   issuecomment-7193290392). #197 is rework; the planner writes the
   brief.
5. **#251's bounded run** (issues/251 issuecomment-7191499904), when no
   other full run is on the machine: in the t251 worktree,
   `.venv-light/Scripts/python.exe -m pytest -q tests --ignore=tests/test_git_guardrails.py`
   (about 10 minutes). Post the count on #251.
6. **#293** (owner-queue: an Options field whose second key has no `;`
   before it parses as one option). Tiered medium and ruled (issues/293
   issuecomment-7194918923): fewer than two parsed options is drawn as
   malformed; the builder first confirms the cause from the two
   entries' Options lines (dff-central-builder-manager was asked to post
   them). It changes the owner-queue plugin, so it keeps Ben's word and
   is not built at the same time as #197; the manager picks the order.
7. **#256**, this state branch's PR: BLOCKED (head predates #291). At a
   check-in: merge `origin/main` into the state branch (the state file
   conflicts add/add; keep the branch's copy), push, ask Ben's word.

### Waiting

- On Ben: the code gos and merge questions in items 3 and 4, the
  dotclaude#12 merge, and the managers settings text as one Action
  (still owed). The queue file holds no open entry.
- On the planner: #197's rework brief (its first step after its own
  clear; its queue id changes, and it sends the new one). Its state is
  at `80502c5` on `state/tools-central-planner`.
- On builders: each code PR taking main (item 2).
- Left for Ben: worktree `s70-guard` (untracked `builder-state/`),
  `t112-closeout-pulls` (commits after merged PR #198), and branch
  `t161-reset-prompt-pointer`. `C:\Users\benha\.claude` stays on
  `settings/shared-rule-trial` until dotclaude#12 merges. The remote
  branch `worktree-t187-windows-time` is kept (merged at `e8b6973`).

### In flight

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t251-venv-setup` | #251 | medium | `4c191e7f` | none | not running; keeps `.venv-light` for the bounded run; build waits for Ben's go |
| `t175-reproofrule` | #175 | low | `9144aeda` | #182 at `5632555` | listed as blocked; DIRTY, takes main |
| `t231-reproof-lock` | #231 | medium | `8506434b` | #242 at `b278602` | not running; BLOCKED, takes main |
| `t207-resumechecks` | #207 | low | n/a | #214 at `a6d7a6c` | takes main |
| `t168-gitgate` | #168 | high | n/a | #211 at `7c1bafb` | takes main, then the F1-F10 re-check |
| `t179-answerhold` | #179 | low | n/a | #196 at `7b8f1e9` | takes main |
| `t161-queuemod` | #161 | high | n/a | #197 at `b7ef918` | DIRTY; rework, the planner's brief |

Open PRs: 256, 242, 214, 211, 197, 196, 182. Main's run on `6e4cc59`
is green; the runs on `40e5847` and `3bdba9c` were still going at the
save.

### Peers

Tools-central-planner (session `a09ca279-6faa-4a61-a313-10328ff9c39d`),
personal-assistant (`6f53e894`), dff-central-builder-manager
(`9d28e196-d848-4cf7-a3d6-f97cbe859143`), dff-central-planner
(`536a467f`, the lead for shared rules and the CI gate). Reach them by
name with ListAgents.

### Reads and checks due

- Main's last finished run before each merge; a red run stops merges.
- Before a pull that changes session-rules, session-dispatch, a role
  file, a hook, the mod or PROJECT-RULES: notice to
  dff-central-builder-manager and both planners, with both heads sent
  after.
- A PR that changes `.github/workflows/` is read by the planner and by
  the dynasty planner as lead before its merge.
- Closeout: the live clone's plugin `scripts/closeout.py`, with the main
  checkout's `.venv`. Run `claude rm <id>` only after it prints
  `removed`, never in the same command.
- Hygiene:
  `C:\Users\benha\AppData\Local\Programs\Python\Python312\python.exe -m pre_commit run check-in-hygiene --from-ref origin/main --to-ref HEAD`
  in a temporary detached checkout of the PR head, removed after a
  junction scan.

### Decided since the last merged state PR

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
