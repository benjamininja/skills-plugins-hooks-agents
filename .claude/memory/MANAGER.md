# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in `PROJECT-RULES.md`
(the table of checks and "Merging on Green" since #292); this file is
state.

## Current

### Saved

2026-11-28, by Tools-builder-manager, queue id
`ea58e038-9092-4552-9e4c-32bb3cdf8281`, at a compact prep on Ben's word.
`origin/main` is at `0105706` (#302); main's CI green at `a774e8e`, the
run at `0105706` was in progress at the save. Both checkouts are at
`0105706`. `session-dispatch` is armed in this session; a compact keeps
it and the id, a clear drops both.

**Ben's standing word (issues/300 issuecomment-7219760428, confirmed
issuecomment-7239515907):** complete the held work. Every tools dispatch
keeps Ben's go by button until #300's exception (#303) and the trial line
have both merged; merge words stay as the rules keep them.

**Background at the save:** `tools/reproof.py 304 7a741a45e72d0b16b130af308becffe69eb79c5d`
running from the live clone (about 70 min), task `bnh0cbrz8`; its
result is also kept as `result-304-7a741a45e72d.txt` beside the lock in
`~/.claude-reproof/`.

### Next

1. **#304** (#293, `t293-optionsnote`, head `7a741a4`): review posted
   (pull/304 issuecomment-7239929415), no blocking finding, F1 advisory
   to the planner for a ticket. When reproof.py returns: post it, hygiene
   over the branch, post the re-proof, ask Ben's merge word. At
   merge, tell both managers: a Decision with one option or a broken
   second key loses its buttons and shows the new note.
2. **#305** (#294 start lines, planner's PR, head `a535511`): re-proved
   Green (pull/305 issuecomment-7239912343). Read main's run at
   `0105706`, then ask Ben's merge word.
3. **#303** (#300 exception and #250 decision 10, planner's PR, head
   `2ba4275`, dynasty planner's read at pull/303 issuecomment-7239906356):
   re-prove when CI finishes (hygiene, no review), ask Ben's word. Then
   the planner's trial-line PR, and the #262 rule-text build on Ben's go
   (ruling at issues/262 issuecomment-7239858390).
4. **#306** (#285, `t285-board`): builder building after the planner's
   read (issues/285 issuecomment-7239802406); re-prove when reported.
5. **#298** (`t298-blanklines`): commit `79c7618` on its branch; wait for
   its report, then review (low), hygiene, one dry run with `-FullSetup`,
   Ben's word (plugin).
6. **#263 step 3** (`t263-usage-scripts`, probe at `8b7084b`): Ben
   approved the personal-assistant's run; the assistant was not running.
   Queue Action placed. When it is up, send it Ben's word and the
   command, relay the three count sections to the builder.
7. **#211** (`t168-gitgate`, high, `89a57ae`): check behind main; fresh
   re-check of F11; hook tests by the manager; hygiene; re-proof; Ben's
   word naming #295's four classes.
8. **#256**, this branch's PR: merge `origin/main` in, push, ask Ben.
9. **#182 repair** (`t175-reproofrule`, DIRTY): brief from the planner,
   now freed by #296.
10. **Waiting on merges:** #289 step 1 (high, find-out) when no test run
    is on the machine; #295 then #289 step 2 then #200 after #211;
    #240 after #293; #111 in the mod lane; #299 part 2 and #262 build
    after the planner's rulings.

### Waiting

- On Ben (queue): fill `setup`/`setupFull` in the dispatch config (#251);
  start the personal-assistant for the #263 probe; the deny rules for
  approvals and re-runs (#300, then the manager runs `gh run rerun --help`
  expecting a refusal). Merge words as each PR is re-proved.
- On the planner: rulings on #299 step 1 (issues/299
  issuecomment-7239905558); the #182 repair brief.
- Left for Ben, unchanged: worktree `s70-guard`, `t112-closeout-pulls`,
  branch `t161-reset-prompt-pointer`, `~/.claude` on
  `settings/shared-rule-trial` until dotclaude#12 merges.

### In flight

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t293-optionsnote` | #293 | medium | `d4cf10e4` | #304 at `7a741a4` | green by builder; review and reproof.py running |
| `t285-board` | #285 | medium | `cf0646a1` | #306 | building after the planner's read |
| `t298-blanklines` | #298 | low | `4f110cf4` | not yet | commit `79c7618`, idle |
| `t263-usage-scripts` | #263 | medium | `6bf2091b` | none yet | waits for the probe output |
| `t168-gitgate` | #168 | high | `2b73b5ff` | #211 at `89a57ae` | manager's re-check owed |
| `t175-reproofrule` | #175 | low | `9144aeda` | #182 at `5632555` | DIRTY; repair to brief |

Open PRs: 306, 305, 304, 303, 256, 211, 182.

### Peers

Tools-central-planner (`0a6ad927-943a-481d-99fc-f2cbfcda8498`),
personal-assistant (not running at the save), dff-central-builder-manager
(`637314ca-f6ae-4049-a3ff-576bd1479cfe`), dff-central-planner
(`0ef68551`). Reach them by name with ListAgents.

### Reads and checks due

- Main's last finished run before each merge; CI on main's new commit
  after each merge.
- `tools/reproof.py` takes the full 40-character head sha, holds a
  machine-wide lock, about 70 minutes; only for PRs that touch
  `plugins/owner-queue/`.
- Hygiene: the system Python's `-m pre_commit run check-in-hygiene
  --from-ref origin/main --to-ref HEAD` in a temporary detached worktree
  of the PR head, removed after.
- Closeout: stop the builder, check its pid is dead, `git worktree
  unlock`, closeout.py dry run then `--apply`, then `claude rm`.
- Never `cd` into a builder worktree: the session's folder follows it.
- Builders write nothing under `.claude/`: a brief whose files are
  there goes to the planner (#294).
- #187 watch, for the planner.

### Decided since the last merged state PR

- 2026-11-28, Ben's buttons in the tools manager's chat:
  - Retry the #296 `-FullSetup` dry run once (refused, exit 2, as expected).
  - Merge #296 at `624b511` (`a774e8e`); t251b and t251-venv-setup closed out.
  - Dispatch all ready items (issues/300 issuecomment-7239545798):
    t294, t293, t285, t298, t299, t262 dispatched; t263 resumed for step 3.
  - #294's files are written by the Tools planner (issues/294
    issuecomment-7239883980); t294 closed out.
  - Merge #302 at `3f02699` (`0105706`).
  - The personal-assistant runs the #263 probe on the real store.
  - Delete t251-venv-setup's `.venv-light` and close it out (done).
- 2026-11-28: t262 and t299 find-outs posted and closed out
  (issues/262 issuecomment-7239815948, issues/299 issuecomment-7239905558).
- 2026-11-27 decisions: see this file at `e40c8c7`.

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
