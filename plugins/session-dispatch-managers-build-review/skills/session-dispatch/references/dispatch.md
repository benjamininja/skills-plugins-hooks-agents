# Dispatch, watch, follow up, close out

## What the script does

`scripts/dispatch.ps1` (Windows PowerShell), from the plugin's folder:

```
dispatch.ps1 -Name <name> -Tier <low|medium|high> -PromptFile <file>
             [-Profile <name>] [-TurnCap <n>] [-NoSetup] [-Project <folder>] [-Apply]
```

It is a dry run unless `-Apply` is given. In order:

1. Reads `<main checkout>/.claude/dispatch.json`. No file, no run.
2. Takes the tier's model, effort and turn cap. No tier, no dispatch.
3. Reads the prompt file. A double quote in it is refused: PowerShell
   cuts a prompt off at the first one.
4. Reads `permissions.deny` from the builders' settings file the config
   names. The same rules are passed to the session with
   `--disallowedTools`, so the list is kept in one place. The settings
   file stays the fence; the flag can only deny, and it holds even if
   the file is not read.
   With `-Profile`, it reads that profile from the config's
   `buildersProfiles` file: its allows go on `--allowedTools`, its
   denies after the shared ones, and its `baseSettings` file, if any,
   takes the shared file's place on `--settings` only if it holds every
   shared deny. An unknown profile is refused. See the plugin README,
   Profiles.
   With `-Apply` it first checks that the main checkout is on the
   owner's list, `<user profile>/.claude/dispatch-projects.json`, and
   refuses if it is not.
5. Makes the worktree `.claude/worktrees/<name>` on branch
   `worktree-<name>`, unless it is there.
6. Runs the config's setup commands in the worktree. `-NoSetup` skips
   them, for a read-only job whose brief says so.
7. Starts the session in the background from the main checkout, in
   `dontAsk` mode, with the config's agent. The prompt is the config's
   read line, the brief, then "Or stop after N turns."
8. Before step 5 it reads `claude agents --json` and sets aside the ids
   of rows already named `<name>`; if that read fails, nothing is
   started. After step 7 it reads the list every 2 seconds, for up to
   30 seconds, until a row that is not one of those has a pid, a status
   and the worktree as its cwd. (A new row names the main checkout, with
   no status, for the first few seconds. The default list holds live
   rows only: an exited or stopped session leaves it.) A list that
   fails to read, or is empty, counts as a look that failed; the next
   look follows. If 30 seconds pass without a good row, it runs
   `claude stop <short id>` (the row's `id`, not its `sessionId`) on
   each new row, then reads the list every 2 seconds, for up to 10
   seconds, until the row has left it, and refuses with what it saw:
   stopped and gone, or the row still listed, or the list unreadable,
   with the short id and what to do by hand. If it never read the list,
   or saw no new row, it says the session may be running and that
   nothing was stopped. Look before a second try.
   On a good dispatch it prints `started: <name>, pid <n>, session <id>`,
   and a `warning:` line if another new row has the same name.

Run it from PowerShell, never from Git Bash: Git Bash rewrites a prompt
that starts with a slash into a path.

## Watch

- `claude agents --json`: `status`, `state` and `waitingFor` per
  session.
- The session's transcript file. `claude logs` is not readable.
- Event-driven: a park, a PR reported green, a stopped or idle builder.
  One fallback look after 60 quiet minutes. No polling.

## Follow up

Only for a builder this session dispatched, on the same ticket.
While the builder is listed, use SendMessage. Otherwise, from the
builder's worktree, run `claude --resume <sessionId> --bg <message>`
with no flags, through `scripts/resume_plain.ps1 -Worktree <worktree>
-SessionId <sessionId> -MessageFile <file>` (it also takes an optional
`-Claude <path>`; it refuses a missing worktree and a message with a
double quote, and prints `exit: <code>`). Never resume a builder that is still running, and never
pass flags: either one starts a copy without the builder settings.
The message holds no double quote.
If a resume starts a copy anyway, stop that copy at once with
`claude stop <its short id>`, check that it is gone, and record it on
the ticket. The copy and the builder can share a name, so tell them
apart by id: the builder's is the first 8 characters of the session id
on the `started:` line, and the copy is the other row. Never stop by
name.

## Close out, only when a builder has stopped

Never while it is still running, and only for a builder this session
dispatched.

1. For each open PR of that builder: re-prove Green, post the output on
   the PR, then squash-merge. A PR that is not green is not merged; it
   is listed for the owner.
   On a PR the repo's ruleset reviews, start the reviewer before the
   re-proof is posted, and run the one round (`session-rules`,
   `references/code-review.md`). Green waits for the round. The builder
   answers through Follow up, above.
   For a builder dispatched with `-Profile probe`, first read its
   `builder-state/probe.py` against the hosts its brief names: its
   `ALLOWED_HOSTS` must hold no other host and be checked on every
   request and redirect hop, and the script must change no data.
   Anything else is listed for the owner.
2. `git pull --ff-only` on the main checkout.
3. Right after the merge and the pull, with no separate word from the
   owner, run the closeout script for that builder (below): the dry run,
   then the same line with `--apply`. Name each other branch the builder
   opened a PR from with `--branch`. Never remove a worktree or delete a
   branch of a builder any other way.
4. Only when the script printed `removed` for that builder, run
   `claude rm <id>`. A refused worktree keeps its session, so the owner
   can resume it to finish the work.
5. State-back, then report to the owner with the commands and their
   output. The script's `refused, for the owner queue:` list goes to the
   queue as one entry.

An `in use` refusal: close any terminal or editor in the folder, check
that the builder's session has ended, and run the script again. A second
`in use` refusal is listed for the owner. Anything unmerged, uncommitted
or not that builder's is listed for the owner and left where it is.

## The closeout script

`scripts/closeout.py` (Python 3.8 or later, standard library only), run
with the project's interpreter as one plain command:

```
closeout.py <main checkout> <builder name> [--branch <name>]... [--apply]
closeout.py <main checkout> --list
```

Without `--apply` it is a dry run and changes nothing. Its first line
names the git version. It acts only on a worktree that
`git worktree list --porcelain` names and that sits directly under
`<main checkout>/.claude/worktrees`, and removes it only when all hold:

- **merged:** the branch's tip is a merged PR's head or an ancestor of
  one, or the tip (a detached one too) is on the remote main branch and
  so holds no commit of its own; a detached HEAD also passes when it is
  exactly a merged PR's head. `git cherry` is not used: it shows every
  commit of a squash of several as missing;
- **clean:** `git status --porcelain` prints nothing. Ignored files
  (`.venv`, `builder-state/`) leave with the worktree;
- **not locked;**
- **its `.git` file is the main checkout's:** it points to the main
  checkout's record of that worktree, and the record points back. Only
  then does any git call run against it;
- **no link out:** no junction or folder symlink in it points out of it,
  no link fails to resolve, and its top folder is not a link;
- **not in use** (Windows, at apply time): it renames the folder to
  `<name>.closeout-inuse` and back. An open file or a process running in
  the folder stops the rename, before anything is deleted.

There is no force option. Its only deletes are `git worktree remove`
without `--force`, then `git branch -D` of the builder's branches on the
same merged test. It never fetches, pushes, prunes or deletes a remote
ref. It prints `removed` only when the folder is gone and git no longer
lists it, whatever git's exit code; otherwise it prints what is left and
exits 3. One `gh pr list --state merged` call gives the merged PRs; if
`gh` fails, nothing is removed. A merged PR head that is not local is
`unknown`, with the fetch to run (`git -C <main checkout> fetch origin
pull/<n>/head`); run it, then the script again. The main branch is read
from `refs/remotes/origin/HEAD`, so the pull of step 2 comes first.

Exit codes: 0 done (or, in a dry run, would be); 1 something refused or
unknown; 2 the run itself refused; 3 a removal or the in-use check did
not finish.

**List-only mode** changes nothing. It prints every worktree under the
folder with its verdict, every folder there that git does not know
(never removed, scanned for links), and ends with one count line:
`count: merged and still there <n>; no commit of its own <n>; unknown <n>`.
The manager runs it at every state-back and writes the count line into
the state file. A just-dispatched builder counts as "no commit of its
own", so read that number against the builders running. A folder git
does not know, or a git record whose folder is gone, is listed for the
owner; pruning stays the manager's command.
