# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in `PROJECT-RULES.md`
(the table of checks and "Merging on Green" since #292); this file is
state.

## Current

### Saved

2026-11-28, by Tools-builder-manager, queue id
`ea58e038-9092-4552-9e4c-32bb3cdf8281`, at a compact prep on Ben's word.
`origin/main` is at `189093c` (#308), and main's CI is green there and at
every merge before it. Both checkouts are at `189093c`. `session-dispatch`
is armed in this session; a compact keeps it and the id, a clear drops
both.

**The trial line is live** (#309 as `d1b920c`, under #303's conditions):
from 2026-11-28 to 2026-12-12, low and haiku tickets dispatch without a
go. Before each one, read the ticket's labels and body: a `held` label or
a `Held:` line means Ben's word is needed. List each such dispatch below
(In flight, "trial") and mark any that went wrong. Medium and high, gate
text and merge words keep Ben's word as before.

**Background at the save:**
- `tools/reproof.py 304 7a741a45e72d0b16b130af308becffe69eb79c5d`, running
  from the live clone since 07:23, task `bnh0cbrz8`. Its result also lands
  as `result-304-7a741a45e72d.txt` in `~/.claude-reproof/`.
- The code review of #316 (low, first round), a background reviewer.

### Next

1. **#316** (#312, `t312-usageprints`, head `d0686a9`, trial): hygiene
   passed and the review is running. On a clean review, post the re-proof
   and merge on Green (paths only `tools/`, `tests/`), then close out.
2. **#304** (#293, `t293-optionsnote`, `7a741a4`): review posted, with no
   blocking finding. On reproof.py's result: post it, run hygiene, post
   the re-proof, ask Ben's merge word. At the merge, tell both managers
   that a Decision with one option or a broken second key loses its
   buttons and shows the new note. Then dispatch #240 (after #293).
3. **#313** (#299 part 2, `t299-oneshot`, gate text): `t299-oneshot` is
   making six edits (pull/313 issuecomment-7240460466 and
   issuecomment-7240483125). On its new head: re-check the changed
   lines, run hygiene, send the head to dff-central-planner for a read,
   then ask Ben's merge word. After the merge, tell the planner, which
   lifts #317's hold. #317 is gate text and keeps Ben's go.
4. **#307** (`t307-boardutf8`, low, trial): cp1252 fix plus parts A and B
   (issues/307 issuecomment-7240559476: `--owner @me` after a login
   check, and `--boards-only`). Re-prove when reported, and merge on Green
   if its paths are only `tools/` and `tests/`. Then the planner raises
   the D rows re-run Action; #285 stays open until D1 passes.
5. **#298** (`t298-blanklines`, low, plugin): resumed at about 08:30 to
   merge main, push and open its PR. Then review (low), hygiene, one
   `-FullSetup` dry run, and Ben's word (plugin).
6. **#211** (`t168-gitgate`, high): resumed at about 08:35 to merge main
   (it was 14 behind) and push. Then a fresh re-check of F11, the hook
   tests, hygiene, the re-proof, and Ben's word naming #295's four
   classes.
7. **#256**, this branch's PR: merge `origin/main` in, push, ask Ben.
8. **#182 repair** (`t175-reproofrule`, DIRTY): waits for the planner's
   brief.
9. **Waiting on merges:** #289 step 1 (high, find-out) when no test run is
   on the machine; #295, then #289 step 2, then #200, after #211; #262's
   build on Ben's go; #111 in the mod lane.

### Waiting

- On Ben: nothing in the queue. Merge words: #304, #313, #298, #211, #256.
- On the planner: the #182 repair brief, and #263's close (ruled; the
  planner closes it).
- Left for Ben, unchanged: worktree `s70-guard`, `t112-closeout-pulls`,
  branch `t161-reset-prompt-pointer`, `~/.claude` on
  `settings/shared-rule-trial` until dotclaude#12 merges.

### In flight

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t312-usageprints` | #312 | low, trial | `1b977f71` | #316 at `d0686a9` | review running |
| `t293-optionsnote` | #293 | medium | `d4cf10e4` | #304 at `7a741a4` | reproof.py running |
| `t299-oneshot` | #299 | medium | `ab68bc30` | #313 at `80e795f`+ | six edits |
| `t307-boardutf8` | #307 | low, trial | `0f9021bd` | none yet | building, parts A and B added |
| `t298-blanklines` | #298 | low | `4f110cf4-0db4-49d6-b1bd-6acf7a0a4a15` | none yet | resumed to open its PR |
| `t168-gitgate` | #168 | high | `2b73b5ff-0140-485b-a518-27a4fb54c994` | #211 at `89a57ae` | resumed to merge main |
| `t175-reproofrule` | #175 | low | `9144aeda` | #182 at `5632555` | DIRTY; waits for a brief |

Trial dispatches so far: #307 and #312, both on 2026-11-28; none has gone
wrong.

Open PRs: 316, 313, 304, 256, 211, 182.

### Peers

Tools-central-planner (`0a6ad927-943a-481d-99fc-f2cbfcda8498`),
personal-assistant (`061c1d24-09c1-4c01-8d89-ff693eb974d9`),
dff-central-builder-manager (`637314ca-f6ae-4049-a3ff-576bd1479cfe`),
dff-central-planner (`0ef68551-3dad-4f09-b5af-b164a0307ae9`). Reach them
by name with ListAgents.

### Reads and checks due

- Main's last finished run before each merge; CI on main's new commit
  after each merge.
- `tools/reproof.py` takes the full 40-character head sha, holds a
  machine-wide lock and runs about 70 minutes. It is only for PRs that
  touch `plugins/owner-queue/`.
- Hygiene: the system Python's `-m pre_commit run check-in-hygiene
  --from-ref origin/main --to-ref HEAD`, in a temporary detached worktree
  of the PR head, removed after.
- Closeout: stop the builder, check its pid is dead, `git worktree
  unlock` if locked, closeout.py dry run then `--apply`, then
  `claude rm`. Then the pulls, with a notice first when a role file,
  session-rules, session-dispatch, a hook or the owner-queue mod moves.
- Never `cd` into a builder worktree. Edit the queue file with the Edit
  or Write tool only, never with a script: a script splice broke its
  `## Actions` heading once.
- Builders write nothing under `.claude/`: a brief whose files are there
  goes to the planner (#294).

### Decided since the last merged state PR

- 2026-11-28, Ben's buttons in the tools manager's chat:
  - Retry the #296 `-FullSetup` dry run once (refused, exit 2, as
    expected).
  - Merge #296 at `624b511` (`a774e8e`); t251b and t251-venv-setup are
    closed out.
  - Dispatch all ready items (issues/300 issuecomment-7239545798).
  - #294's files are written by the Tools planner (issues/294
    issuecomment-7239883980).
  - Merge #302 at `3f02699` (`0105706`).
  - The personal-assistant runs the #263 probe, and after #308 the
    `tags` read, on the real store.
  - Merge #305 (`805aab5`), #303 (`25aef1a`), #309 (`d1b920c`), #310
    (`3eba79a`) and #311 (`347188b`).
  - Dispatch #299 part 2 (issues/299 issuecomment-7240316779).
- 2026-11-28, on Green: #306 (`7385794`) and #308 (`189093c`); t285-board
  and t263-usage-scripts are closed out.
- 2026-11-28, Ben in the pane: no allow rule for the builders' catalog
  check (issues/299 issuecomment-7240505050). Boards token made, D1 fails
  (issues/285 issuecomment-7240599188).
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
