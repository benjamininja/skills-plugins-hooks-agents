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
- By the personal-assistant session's read-only count in dynasty, 73 of
  82 worktrees were clean, so the uncommitted-file guard is not the main
  cause.

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
issuecomment-7104205770) added one answer of Ben's, by button. A worktree
with no commit of its own is removable: "Removable (Recommended)".

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
  - `git status --porcelain` prints nothing for it. Ignored files leave
    with the worktree;
  - it is not locked;
  - no folder link in it points out, no link fails to resolve, and its
    top folder is not a link;
  - on Windows, at apply time, it can be renamed to a sibling and back.
- **Merged** means one of these:
  - the branch's tip is the head of a merged PR, or an ancestor of one.
    This covers #215's tip that is behind the head;
  - the tip, a detached one included, is an ancestor of the remote main
    branch, so it holds no commit of its own;
  - for a detached HEAD, it is exactly a merged PR's head.

  One `gh pr list --state merged` call answers the PR part. If `gh`
  fails, nothing is removed. A list cut at its limit says so in every
  `no merged PR` reason. `git cherry` is dropped.
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
  the builder's local branches. A branch is deleted only after its
  worktree is gone, on the same merged test, and only if no worktree has
  it checked out. Other branches of the builder are named with
  `--branch`. The script never pushes, prunes or deletes a remote ref,
  and it deletes no file itself.
- **Refusals go to the owner as one list.** The script ends with
  `refused, for the owner queue:` and each refused worktree with its
  reason. The manager sends it to the queue as one entry.
- **The count at every state-back.** List-only mode changes nothing. It
  prints every worktree under the folder with its verdict, and ends with
  `count: merged and still there <n>; no commit of its own <n>; unknown
  <n>`. The manager runs it at every state-back, and `MANAGER.md` holds
  the line.
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
- **Not yet proven:**
  - A removal that stopped part way explains folders unknown to git. It
    does not explain the clean worktrees that git still lists. For those,
    closeout not run to its end is the inferred cause.
  - The first live run will show how many unknowns the no-fetch rule
    leaves.
