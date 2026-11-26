# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill (0.5.2 since #290) and in
`PROJECT-RULES.md`; this file is state.

## Current

### Saved

2026-11-26, about 13:45Z, by Tools-builder-manager, queue id
`3bac2fdb-b847-4732-b572-e582ae2af312`, at a compact prep on Ben's word.
`origin/main`, the main checkout and the live clone are at `63b678f`
(#208). Ben invoked `session-dispatch` in this session. A compact keeps
it; a clear needs it typed again.

### Next

1. **#187, Ben's top priority.** Ben's decision (issues/187
   issuecomment-7193473530): Windows returns to code PRs as a required
   check, 6 shards, check names fixed (`pytest (ubuntu-latest)`,
   `CATALOG.md is current`, `pytest (windows)`). Relayed word for word
   to t187-windows-time. The planner ruled on its finding
   (issuecomment-7193574558): six shards, no xdist, and a digest of the
   ordered test ids on each shard's line is required. The reporting job
   fails on unequal digests where the workflow can do it; otherwise the
   manager reads the six digests at re-proof. Relayed. When t187 reports
   a green head: the full code review at medium (`high`), then send the
   head to Tools-central-planner (digests, counts, GitHub's docs), then
   the dff-central-planner's read as lead, then Ben's merge word. **Right
   after the merge, tell the planner at once**, so #292 takes main and
   shows the skip case. Ben changes the ruleset only after #292's run
   shows the skip.
2. **The next text round:** #227 `5b7eba2`, #222 `f86692c`, #205
   `4046027`, #184 `def65a8`. Main `63b678f` is merged into each, and CI
   is green. To do: re-prove each one (hygiene in a detached checkout,
   no review for planner PRs), then ask Ben's word. #205 and #184 share
   `docs/adr/README.md` and session-rules SKILL.md, so they can't merge
   in the same round. #249 takes main after #205.
3. **Before the next merge,** read main's run on `63b678f`. At the prep
   the runs on `ede2171`, `94ce7e2`, `35302b6` and `63b678f` were still
   going; the last finished run was `e3a342f`, success.
4. **The code stop is lifted** (Ben, issues/187 issuecomment-7193345327).
   Each code ticket still needs Ben's go by button in this chat: #289
   (find-out first), #285, #262's rule-text build, #251's build. Merge
   questions: #214, #196, #242; #211 after Claude reads F11's class
   (pull/211 issuecomment-7193291072: blocking means a fresh re-check
   and a ruling, advisory means record that no round is owed; #211
   before #289); #182 after it takes main (pull/182
   issuecomment-7193290392; keep both passages against #290). #197 is
   rework, and the planner writes the brief.
5. **#251's bounded run** (issues/251 issuecomment-7191499904), when the
   machine has no other full run: in the t251 worktree,
   `.venv-light/Scripts/python.exe -m pytest -q tests --ignore=tests/test_git_guardrails.py`
   (about 10 minutes). Post the count on #251.
6. **#256**, this state branch's PR. Refresh it and ask Ben's word at a
   check-in.

### Waiting

- On Ben: merge words for item 2, the #187 workflow PR's merge word
  (after the review and the lead's read), the code tickets' gos in item
  4, the dotclaude#12 merge, and the managers settings text as one
  Action (still owed). The queue file is empty.
- On builders: t187-windows-time's green head.
- Left for Ben: worktree `s70-guard` (untracked `builder-state/`),
  `t112-closeout-pulls` (commits after merged PR #198), and branch
  `t161-reset-prompt-pointer`. `C:\Users\benha\.claude` stays on
  `settings/shared-rule-trial` until dotclaude#12 merges.

### In flight

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t187-windows-time` | #187 | medium | `2bc62b36` | draft #291 at `13c4399` | working on the xdist run, the finding and the PR to merge |
| `t251-venv-setup` | #251 | medium | `4c191e7f` | none | not running; keeps `.venv-light` for the bounded run; build waits for Ben's go |
| `t175-reproofrule` | #175 | low | `9144aeda` | #182 at `5632555` | listed as blocked; #182 takes main |
| `t231-reproof-lock` | #231 | medium | `8506434b` | #242 at `b278602` | not running; merge question now open |
| `t207-resumechecks` | #207 | low | n/a | #214 at `a6d7a6c` | merge question |
| `t168-gitgate` | #168 | high | n/a | #211 at `7c1bafb` | F11's class read owed |
| `t179-answerhold` | #179 | low | n/a | #196 at `7b8f1e9` | merge question |
| `t161-queuemod` | #161 | high | n/a | #197 at `b7ef918` | rework, the planner's brief |

Open PRs: 292, 291, 256, 249, 242, 227, 222, 214, 211, 205, 197, 196,
184, 182.

### Peers

Tools-central-planner (session `a09ca279-6faa-4a61-a313-10328ff9c39d`),
personal-assistant (`ff1e3261`), dff-central-builder-manager
(`9d28e196-d848-4cf7-a3d6-f97cbe859143`), dff-central-planner (the lead
for shared rules and the CI gate). Reach them by name with ListAgents.

### Reads and checks due

- Main's last finished run before each merge, and a red run stops
  merges (#287).
- Before a pull that changes session-rules, session-dispatch, a role
  file, a hook or the mod: notice to dff-central-builder-manager and
  both planners, with both heads sent after.
- The closeout script is at the live clone's plugin `scripts/closeout.py`,
  run with the main checkout's `.venv`. Hygiene runs with
  `C:\Users\benha\AppData\Local\Programs\Python\Python312\python.exe -m pre_commit`
  in a temporary detached checkout of the PR head, which is removed
  after a junction scan. Its scope is CLAUDE/README/PLAN/GLOSSARY.md,
  docs/adr and `.claude/memory/MEMORY.md` only.

### Decided since the last merged state PR

- 2026-11-26, Ben's buttons in the tools manager's chat:
  - Resume t187 for #187 Part 2 (issues/187 issuecomment-7191766144).
  - Ben unlocked t283's stale worktree lock, and t283 was closed out
    (issues/283 issuecomment-7191791109).
  - Merge #290, keeping the skills/plugins/hooks/agents line (merged
    `e3a342f`).
  - Ignore the Google Sheet in the browser pane.
  - After Ben signed in again, t187 was followed up (issues/187
    issuecomment-7193035709).
  - Merge #239, #238, #216 and #208 (merged `ede2171`, `94ce7e2`,
    `35302b6`, `63b678f`; #237 closed).
  - Clear the closeout backlog now: 32 of 32 removed (issues/250
    issuecomment-7193535351).
- 2026-11-26, closed out: t250, t257, t260-261, t219, t189, t283, t237.
- 2026-11-26, Ben's buttons in the planner's chat (reports, on record):
  the stop lifted (issues/187 issuecomment-7193345327); Windows
  required, 6 shards (issuecomment-7193473530).
- Lesson: Ben reads "hold closeout run" as being about CI. Claude
  explains first that closeout is a local script run with no CI.
- Lesson: a builder's expired Claude login shows as `blocked`, with
  "Login expired · Please run /login" in its transcript. Ben signs in
  again (`claude`, then `/login`), and the follow-up goes by SendMessage
  while the builder is listed.

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
