# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in `PROJECT-RULES.md`
(the table of checks and "Merging on Green" since #292); this file is
state.

## Current

### Saved

2026-11-28, by Tools-builder-manager, queue id
`ea58e038-9092-4552-9e4c-32bb3cdf8281`, at a clear prep on Ben's word.
The id changes at the clear: the new session sends its new id to the
peers, and Ben types `/session-dispatch-managers-build-review:session-dispatch`
again before any dispatch, merge or closeout. `origin/main` is at
`672db7d` (#256), and main's CI is green there and at every merge
before it. Both checkouts are at `598a325`; the main checkout may be
pulled to `672db7d` (state file only).

**The trial line is live** (#309 as `d1b920c`, under #303's conditions):
from 2026-11-28 to 2026-12-12, low and haiku tickets dispatch without a
go. Before each one, read the ticket's labels and body: a `held` label,
a `Held:` line or `Profile: oneshot` (#322) means Ben's word is needed.
List each such dispatch below and mark any that went wrong. Medium and
high, gate text and merge words keep Ben's word as before.

### Next

1. **#328, PR #330** (`t328-ownqueries`, medium, head `ff2cc80`):
   re-proved Green (pull/330 issuecomment-7241753109; three advisories
   sent to the planner). **Not merged on Green:** by Ben's button
   (issues/328 issuecomment-7241637480) it holds until Ben runs the D
   rows from the PR's branch and every row passes. The planner sends that
   Action (the head and the worktree folder were sent). On a full pass:
   merge pinned to the head (paths only `tools/`, `tests/`), close out,
   tell the planner. Then #329 (decimals, low, held behind #330) may go
   under the trial once its hold lifts.
2. **#240, PR #326** (`t240-rekey`, medium, head `d3f4d10`, builder
   done, no report received): re-prove: full review at high effort,
   hygiene, `tools/reproof.py 326 <full sha>` (owner-queue), the brief's
   live check (manager's, after the merge), then Ben's merge word. Then
   the mod half of #262 and #111.
3. **#211** (`t168-gitgate`, high, head `d76b272`, builder working after
   merging main): on its report, a fresh re-check of F11, the hook tests,
   hygiene, the re-proof, then Ben's word naming #295's four classes.
   Then #295, #289 step 2, #200.
4. **#182 repair** (`t175-reproofrule`, DIRTY): waits for the planner's
   brief.
5. **#289 step 1** (high, find-out) when no test run is on the machine.
6. **#324** (PR #304 F1, low): held; waits for the planner.

### Waiting

- On Ben: the queue is empty. Merge words: #326 and #211 when
  re-proved; #330 after his D rows run.
- On the planner: the D rows Action for #330; rulings on #330's
  advisories; the #182 repair brief; the two-week `usage.py tags` run
  after #322.
- Left for Ben, unchanged: worktree `s70-guard`, `t112-closeout-pulls`,
  branch `t161-reset-prompt-pointer`, `~/.claude` on
  `settings/shared-rule-trial` until dotclaude#12 merges.

### In flight

| Builder | Ticket | Tier | Session | PR | Stage |
|---|---|---|---|---|---|
| `t328-ownqueries` | #328 | medium | `3e38704c-c749-42f5-88a0-965bfb714ee2` | #330 at `ff2cc80` | Green; holds for Ben's D rows run |
| `t240-rekey` | #240 | medium | `82127938-63d7-4e04-b800-af2112abb1bf` | #326 at `d3f4d10` | done; re-proof due |
| `t168-gitgate` | #168 | high | `2b73b5ff-0140-485b-a518-27a4fb54c994` | #211 at `d76b272` | working |
| `t175-reproofrule` | #175 | low | `9144aeda-5d4c-49ea-b294-f854aade6daf` | #182 at `5632555` | DIRTY; waits for a brief |

Trial dispatches so far, all 2026-11-28, none gone wrong: #307 (PR
#321, `f50dac1`; stopped once after its security review and was
resumed), #312 (PR #316, `13481f0`), #319 (PR #320, `6fd5dae`), #325
(PR #327, `6db4e43`).

Open PRs: 330, 326, 211, 182.

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
  machine-wide lock and runs about 80 minutes. It is only for PRs that
  touch `plugins/owner-queue/` (so #326, not #330).
- Hygiene: the system Python's `-m pre_commit run check-in-hygiene
  --from-ref origin/main --to-ref HEAD`, in a temporary detached worktree
  of the PR head, removed after.
- Closeout: stop the builder, check its pid is dead, `git worktree
  unlock` if locked, closeout.py dry run then `--apply`, then
  `claude rm`. Then the pulls, with a notice first when a role file,
  session-rules, session-dispatch, a hook or the owner-queue mod moves.
- A builder's local proof is `.venv/Scripts/python.exe -m pytest ...`
  with the worktree's own interpreter; a builder that tries another
  form is told so.
- A builder's parked denied call goes in Ben's queue (and to the
  planner), unless Ben already ruled that case (the catalog check:
  #299, no builder rule).
- Builders dispatched from now on may WebFetch `docs.github.com`
  (Ben's rule, 2026-11-28, #328).
- Never `cd` into a builder worktree. Edit the queue file with the Edit
  or Write tool only, never with a script.

### Decided since the last merged state PR

- 2026-11-28, Ben: merge #256 on Green (`672db7d`); dispatch #328
  (issues/328 issuecomment-7241547879); a queue Decision on builders
  reading docs, answered (b) (issues/328 issuecomment-7241629184), rule
  added by Ben (issuecomment-7241660686); #328 runs before its merge
  (issues/328 issuecomment-7241637480, in the planner's chat).
- 2026-11-28, the Tools planner: #328's plan has no breach, the
  whole-number narrowing stands, decimals are #329 (issues/328
  issuecomment-7241599804).

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
