# A builder's environment: light at dispatch, removed at closeout by one script

- Status: accepted
- Date: 2026-11-23
- Scope: `plugins/session-dispatch-managers-build-review/` (`scripts/closeout.py`,
  the Closeout text of `session-dispatch`'s `SKILL.md` and
  `references/dispatch.md`, the `MANAGER.md` and managers' settings
  templates); the dispatch half is tools #251
- Ticket: tools #250 (dynasty #655 is the same gap from the dynasty side)

## Context

The written closeout rule said a builder's worktree is removed "only if it
has no uncommitted file", and a branch is deleted only after `git cherry`
shows nothing missing. The practice disagreed with it. On 2026-11-23
there were 41 worktree folders in this repository, 6 of them on branches
fully merged into `origin/main`. Dynasty had 88 folders, 13 of them
merged, and 5 folders that git does not know. A dynasty venv is about
660 MB.

- There was no closeout script. Step 4 was the manager's hand commands,
  and "an uncommitted file" was not defined anywhere.
- No closeout record says step 4 ran, was skipped or failed. The cause
  stays inferred: closeout was not run to its end.
- By the personal-assistant session's corrected read-only count in
  dynasty (#250, issuecomment-7104579581), 49 of 82 worktrees were clean,
  9 had local changes, and in 24 the status check could not run (a
  record with no readable HEAD). A first count of "73 of 82 clean" was
  wrong. In this repository, `CATALOG.md` flagged with an empty diff was
  the only status line in 15 of the 17 merged worktrees that were not
  clean. The causes this points to are under Consequences.

The builder's Part 1 finding (#250, issuecomment-7103861254, corrected in
issuecomment-7104084566) tested git itself in throwaway repositories
(`tests/test_closeout.py`):

- **Ignored files only** (`.venv/`, `builder-state/`): `git status
  --porcelain` prints nothing, and `git worktree remove` removes the whole
  folder.
- **A file held open, on Windows** (Git 2.50.1.windows.1): git deletes in
  name order and stops at the first file it cannot delete. It still
  deletes its own admin folder, so the leftover is a folder git no longer
  knows, with no `.git` file. A removal that stopped part way explains
  the folders unknown to git. On Linux an open file does not block the
  removal.
- **A junction out of the worktree, on Windows**, differs by git version:
  - Git 2.50.1.windows.1 (the owner's machine) exited 0, removed the
    worktree, and deleted the file in the folder the junction pointed
    to, outside the worktree.
  - Git 2.56.1.windows.1 (the `windows-latest` CI runner) exited 0 with no
    message and left the worktree folder in place.

  On Linux, git removes a symlink and not its target.
- **`git cherry` cannot see a squash of several commits.** It prints every
  commit of the branch as missing, so the old step 3 never passed for
  one.

## The owner's answers

Ben's eleven decisions, from the grill he held in the personal-assistant
session's chat and confirmed in the planner's chat by "Yes, record all
eleven (Recommended)" (#250, issuecomment-7103259381):

1. The cleanup of the existing worktrees waits until this fix merges, and
   runs through it as its first test: "Yes, after the fix merges".
2. The fix lives in the shared session-dispatch plugin, and each project
   supplies only config: "Yes, shared plugin".
3. A builder's environment is made small at dispatch, and its removal is
   guaranteed at closeout: "Yes, both".
4. A standing check counts leftover worktrees on merged branches: "Yes,
   add a detector".
5. Dispatch builds the light venv by default, and a brief says `venv:
   full` only when it changes `requirements.txt`: "Yes, light by
   default".
6. The manager removes a builder's worktree right after merging its PR,
   as one step, with no separate word from Ben: "Yes, merge then remove".
   Anything unmerged or uncommitted is left in place and listed for Ben.
7. Closeout is one tracked script in the plugin that checks, removes, and
   prints the reason when it refuses: "Yes, one script".
8. The detector is the script's list-only mode, run by the manager at
   every state-back: "Yes, at manager state-back".
9. What the script refuses goes to Ben as one owner-queue list, to decide
   one by one: "Yes, one queue list".
10. The main checkout's packages change only when no builder is running,
    and a `requirements.txt` ticket always gets `venv: full`: "Yes, both
    rules".
11. `dispatch.json` holds a light and a full setup list, and `dispatch.ps1`
    chooses full by a switch: "Yes, two lists and a switch".

Decisions 5, 10 and 11, and the light half of 3, are built in tools
#251. The others are built here.

The planner's ruling on the finding (issuecomment-7103994943, amended in
issuecomment-7104205770 and issuecomment-7104581056) added two answers of
Ben's, by button:

- A worktree with no commit of its own is removable: "Removable
  (Recommended)".
- Status lines that hold no content are restored, and then the worktree
  is removed: "Both kinds (Recommended)". The option read: the script
  restores a file whose git diff is empty and a tracked file deleted
  from the folder, checks the status is then empty, and removes the
  worktree; all other checks still apply; a new untracked file still
  refuses.

## Decision

- **Closeout is `scripts/closeout.py`.** It is standard-library Python
  3.8 or later, so any project's interpreter runs it. It is a dry run
  unless `--apply` is given. The manager runs it right after the merge
  and the pull, as one step, for the named builder.
- **Allowlist first.** It acts only on a worktree that `git worktree
  list --porcelain` names and that sits directly under `<main
  checkout>/.claude/worktrees`, and never on the main checkout. Paths are
  compared after `realpath` and `normcase`. A folder there that git does
  not know is listed and never removed.
- **A worktree is removed only when all of these hold:**
  - it is merged;
  - `git status --porcelain` prints nothing for it, once lines that hold
    no content are restored (below). The read pins
    `--untracked-files=normal --ignore-submodules=none`, so the owner's
    config cannot hide an untracked file or a submodule change. Ignored files leave with the
    worktree;
  - it is not locked. The refusal prints the lock's reason, and the
    script never unlocks;
  - its HEAD can be read. A record whose HEAD git cannot read (forty
    zeros in `git worktree list --porcelain`) is `no readable HEAD`, is
    never judged by its branch name, and is repaired outside the script;
  - its branch has no open PR;
  - no folder link in it points out, no link fails to resolve, and its
    top folder is not a link;
  - on Windows, at apply time, it can be renamed to a sibling and back.
- **Merged** means one of these:
  - the branch's tip is the head of a PR merged into the main branch, or
    an ancestor of one. This covers #215's tip that is behind the head.
    A PR merged into any other base (a stacked PR) does not count;
  - the tip, a detached one included, is an ancestor of the remote main
    branch, so it holds no commit of its own;
  - for a detached HEAD, it is exactly a merged PR's head.

  One `gh pr list --state all` call answers the PR part, with each PR's
  state, so a branch with an open PR is told apart from a branch with
  commits and no PR. Both refuse. If `gh` fails, nothing is removed. A
  list cut at its limit says so. `git cherry` is dropped. When any git
  read the script needs fails, the verdict is a refusal with that
  reason, never a guess.
- **Lines that hold no content are restored, then the worktree goes**
  (Ben's "Both kinds"):
  - Kind 1 is a path modified in the working tree only whose `git diff
    --quiet` exits 0. Kind 2 is a tracked path deleted from the working
    tree only. Nothing else counts: a staged change, an untracked file
    that is not ignored, a real diff or a conflict refuses.
  - In an apply run, after every other check and the in-use check,
    the script runs `git restore --worktree` for exactly those paths and
    reads the status again. If it prints anything, the script refuses,
    names the restored paths and removes nothing.
  - The dry run and the list name the paths.
  - This restore is the script's one write besides its two deletes.
- **The script never fetches.** A merged PR head that is not local is
  `unknown`, and the script prints the fetch for the manager to run:
  `git -C <main checkout> fetch origin pull/<n>/head`. The reason: the
  case is rare, since a builder's own commits are already in the main
  checkout. Without the fetch, the script does reads and one kind of
  delete and nothing else. If the first list-only runs show many
  unknowns, the planner reopens this point.
- **The scan is the guard against links,** because git's handling of a
  link differs by version and is never relied on:
  - The script walks the worktree with `os.scandir` and `os.lstat`, and
    never follows a link.
  - A link is a symlink, or a name-surrogate reparse point (junctions
    and symlinks). Other reparse points, such as cloud-file
    placeholders, are ordinary files.
  - A folder link that points out refuses. On Windows the folder bit is
    read from `lstat`'s file attributes.
  - A file link is left to git, which removes the link and not its
    target. That is shown by a test on every platform that can make one.
- **The worktree's own `.git` file is not trusted.** A builder can rewrite
  it, and git would then read the config of a repository the builder
  chose. A `core.fsmonitor` command in that config would run in the
  manager's process. So the script checks that the file points to the
  main checkout's record of that worktree, and that the record points
  back. It runs `git status` with that record passed as `--git-dir` and
  with `core.fsmonitor` off. A mismatch refuses. Found by the
  security review before the PR.
- **The in-use check:**
  - It runs on Windows, in an apply run, and last, after every other
    test has passed.
  - It renames the folder to `<name>.closeout-inuse` and back. An open
    file, or a process running in the folder (a builder still running),
    stops the rename before anything is deleted.
  - An existing sibling refuses.
  - If the rename back fails after retries, the script prints both paths
    and the rename that puts the folder back, deletes nothing, and exits
    3.
  - List-only mode names such a sibling as an interrupted check.
- **The script never trusts git's exit code for a removal.** It prints
  `removed` only when the folder is gone and `git worktree list
  --porcelain` no longer names it. Otherwise it prints what is left and
  exits 3. Its first output line names the git version.
- **There is no force option of any kind.** The script's only deletes
  are `git worktree remove` without `--force`, then `git branch -D` of
  the builder's local branches. Its only other write is the restore of
  lines that hold no content. A branch is deleted only after its
  worktree is gone, on the same merged test, and only if no worktree has
  it checked out. Other branches of the builder are named with
  `--branch`. The script never pushes, prunes or deletes a remote ref,
  and it deletes no file itself.
- **Refusals go to the owner as one list.** The script ends with
  `refused, for the owner queue:` and each refused worktree with its
  reason. The manager sends it to the queue as one entry.
- **The count at every state-back.** List-only mode changes nothing. It
  prints every worktree git knows with its verdict, whoever made it, and
  ends with one `count of worktrees:` line, one bucket per worktree:
  merged and still there; no commit of its own; unknown; open PR;
  locked; no readable HEAD; refused for another reason; outside the
  folder. A worktree outside the folder is printed and counted, and
  never acted on. A locked worktree counts as locked, so a running
  builder is not read as an empty one. The manager runs it at every
  state-back, and `MANAGER.md` holds the line.
- **`claude rm <id>` stays the manager's command.** It runs after the
  script, and only when the script printed `removed`. A refused
  worktree keeps its session, so the owner can resume it.

### The script is the guard

The script's own git calls are not seen by the git-guardrails hook,
which judges tool calls only. A `git branch -D` or a `git worktree
remove` inside the script passes no hook. So the script is the guard. It
is one tracked, reviewed file, run under one exact allow rule in the
managers' settings file
(`Bash(.venv/Scripts/python.exe <plugin folder>/scripts/closeout.py *)`).
A change to it is a PR that gets the code review, as a re-proof script
does (#175).

### Unchanged

The `session-rules` "Never" line stands. Removing a worktree stays a
manager's act, for a named ticket, in a session where the owner invoked
`session-dispatch`. Decision 6 removes the separate word from Ben for
each removal; it does not lift that line.

## Alternatives rejected

- **The script fetches a missing PR head itself.** It would keep closeout
  to one command, but put a network write inside the script. The
  planner ruled for the printed fetch.
- **Refuse every link that points out, file links too.** On Linux a
  venv's `bin/python` is a file symlink to the system interpreter, so no
  Linux worktree with a venv would ever be removable. A file link cannot
  be descended, and the test shows git removes only the link.
- **A force switch for the owner.** Ben's decision 6 leaves anything
  unmerged or uncommitted in place. A force switch would let one mistyped
  line delete work.
- **`git cherry` against the main branch.** It is shown wrong after a
  squash of several commits.
- **Trusting `git worktree remove`'s exit code.** One git version exits
  0 and leaves the folder.
- **Deleting the ignored folders first, then calling git.** The planner's
  first sketch did this. The script would then delete files itself and
  could follow a link. Git removes ignored content on its own, and the
  scan and the in-use check cover the hazards.

## Consequences

- The cleanup of the existing worktrees (decision 1) is the script's
  first real run in each project, on Ben's word, after this merges and
  both checkouts are pulled. Its refusals go to Ben as one queue list.
- The owner adds the allow rule to the managers' settings, from text the
  manager queues. Until #233 finds where a desktop manager's rules live,
  the call may be asked of Ben each time.
- A just-dispatched builder counts as "no commit of its own" in the count
  line. The manager reads that number against the builders it has
  running.
- A folder git does not know, and a git record whose folder is gone, are
  listed. Removing or pruning them stays with the owner and the manager.
  A folder unknown to git is scanned for links in list-only mode,
  because removing it by hand carries the same hazard.
- **On the cause, what is tested and what is not:**
  - For this repository there is a tested candidate. `tools/build_catalog.py`
    leaves `CATALOG.md` flagged as modified with an empty diff under
    `core.autocrlf`, and git then refuses to remove the worktree. It is not
    proven for the time of each closeout. A ticket of its own fixes the
    flag at its source; the script's restore covers the worktrees that
    already carry it.
  - Damaged records (no readable HEAD) explain 24 dynasty worktrees, but
    not why their records were damaged.
  - A removal that stopped part way explains folders unknown to git.
  - The first list-only run is checked against the personal-assistant
    session's classification, and any difference is posted on #250
    before the first apply run.
- **Not yet proven:**
  - The cause for the clean worktrees that git still lists, beyond the
    candidates above. Closeout not run to its end stays the inferred
    cause.
  - The first live run will show how many unknowns the no-fetch rule
    leaves.
