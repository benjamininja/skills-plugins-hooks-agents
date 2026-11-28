# session-dispatch-managers-build-review

A Claude Code plugin for a project that is worked by three kinds of
session: a **planner**, a **builder manager** and **builders**. The
planner sets a tier on each ticket; the manager starts a builder at that
tier with one script; the builder works in its own worktree and opens a
PR, which the manager re-proves and merges.

Windows only in 0.1.0: the script is Windows PowerShell 5.1.

## What is in it

| Part | What it is |
|---|---|
| `scripts/dispatch.ps1` | Starts one builder. A dry run unless `-Apply` is given. |
| `scripts/prepend_state.py` | Puts a block read from a file at the top of a state file, before its first `- **CURRENT STATE` line: `prepend_state.py <state in> <block file> <state out>`. |
| `scripts/closeout.py` | Closes out one builder: removes its worktree and branch when they hold nothing unmerged or uncommitted, and says why when it refuses. `--list` counts leftover worktrees. A dry run unless `--apply` is given. See [Closeout](#closeout). |
| `scripts/resume_plain.ps1` | Resumes a stopped builder with a follow-up message and no other flag. The manager uses it for a follow-up when SendMessage cannot reach the builder. |
| `skills/session-rules` | The rules every role keeps: tiers, briefs, the "Never" list, a denied call, parking, who may merge. Any session may load it. It starts nothing. |
| `skills/session-dispatch` | The manager's procedures that change things: dispatch, merging a builder's PR, closeout. Manual only (`disable-model-invocation: true`): the owner invokes it in a manager's session. |
| `templates/` | Blank files for a new project: three role files and the code reviewer agent, the config, the queue file, the project rules file, two state files, three example settings files, an example profiles file, a brief and a gap ticket. |

## Install

Point Claude Code at the plugin folder, as for any plugin under
development:

- one session: `claude --plugin-dir <this folder>`;
- every session: name the folder in `CLAUDE_CODE_PLUGIN_DIRS`, in the `env`
  block of `~/.claude/settings.json` and nowhere else (the `owner-queue`
  README, Install, says why and how to check).

`claude plugin validate <this folder>` checks the manifest.

## What the project owner does by hand

No agent creates or edits these files. The plugin's skills forbid it and
the example settings files deny it.

1. Copy `templates/dispatch.json` to `<main checkout>/.claude/dispatch.json`
   and edit it. Without this file the script refuses to run.
2. Copy `templates/dispatch-projects.json` to
   `<user profile>/.claude/dispatch-projects.json` and list the main
   checkout in it. `-Apply` acts only in a listed project.
3. Copy the four agent files from `templates/agents/` to
   `.claude/agents/`: the three role files, and `pr-code-reviewer.md`,
   the read-only reviewer the manager starts at re-proof
   (`session-rules`, `references/code-review.md`). A project with a
   Supabase database may also copy the fifth, `supabase-look.md`, and put
   its own server's name in the `tools` line: a look-only subagent with
   no SQL tool, for the planner and the manager (tools ADR-0019). Copy
   `PROJECT-RULES.md`, `NEEDS-OWNER.md`,
   `PLANNER.md` and `MANAGER.md` to `.claude/memory/`. Add
   `.claude/memory/NEEDS-OWNER.md` to the project's `.gitignore`: the
   queue is never committed. Fill in
   `PROJECT-RULES.md`: the project's list of proofs ("Green"), its own
   "Never" lines, its stages.
4. Write the builders' and the managers' settings files, starting from
   the two `*.settings.example.json` files. Add the project's proof
   commands to the builders' allow list. The managers' file needs an
   allow rule for the script; the example has one.
5. Add the line `builder-state/` to the project's `.gitignore`. A
   builder keeps its working notes there; its lasting state is its
   ticket and its commits.
6. Keep deny rules for every settings file, for `.claude/dispatch.json`,
   for the profiles file and for the list of projects in both files, so
   no session can change its own fence.
7. Optional: write a profiles file and any base settings file it names,
   starting from `templates/builder-profiles.example.json` and
   `templates/research.settings.example.json`, and name the profiles
   file under `buildersProfiles`. See [Profiles](#profiles).
8. On GitHub, add the two branch rulesets. See
   [Server-side rulesets](#server-side-rulesets).

## The config, `.claude/dispatch.json`

| Key | Meaning |
|---|---|
| `agent` | The agent a builder runs as: a file in `.claude/agents/`, without `.md`. |
| `buildersSettings` | The builders' settings file, from the main checkout. Its `permissions.deny` list is also passed to the session. |
| `buildersProfiles` | Optional. The owner's profiles file, from the main checkout, for `-Profile`. See [Profiles](#profiles). |
| `claude` | The Claude CLI: a name on `PATH` or a full path. |
| `setup` | PowerShell lines run in the new worktree before the session starts, by default. Meant to be the light list. They run as written, which is why only the owner writes this file. See [Setup](#setup). |
| `setupFull` | Optional. The full list, run in place of `setup` only with `-FullSetup`. Empty or missing: `-FullSetup` is refused. |
| `readLine` | The first lines of every builder's prompt. No double quote. |
| `tiers` | Optional overrides of the tier table: `model`, `effort`, `turnCap` per tier. |

A key that starts with `//` is a note and is not read.

## Setup

The config holds two lists of setup lines. The script runs one of them
in the new worktree, after it is made and before the session starts,
each line as `powershell.exe -NoProfile -NonInteractive -Command <line>`
from the worktree's top. A line that exits non-zero refuses the
dispatch. Nothing is put in place of a name in a line, and each line is
a new process, so a variable does not carry from one line to the next.

| The brief's `venv:` line | The manager passes | The list that runs |
|---|---|---|
| `light` | nothing | `setup` |
| `full` | `-FullSetup` | `setupFull` |
| `no` | `-NoSetup` | none |

`-NoSetup` wins over `-FullSetup`. With `-FullSetup` and an empty or
missing `setupFull`, the dispatch is refused before anything is made:
no fetch, no branch, no worktree. A config with no `setupFull` key runs
`setup` as before when the switch is not passed. The dry run prints the
list's name and its lines. A missed `-FullSetup` is not caught by the
script: the builder's work fails at the first missing package.

**The light form.** A light `.venv` is a venv made with the main
checkout's `.venv\Scripts\python.exe` and no pip, plus one `.pth` file
in its `Lib\site-packages` that names the main checkout's
`.venv\Lib\site-packages`, so the builder runs with the main checkout's
packages and installs nothing. Its limits:

- The `.pth` holds the main checkout's path as it was when the worktree
  was made. If the main checkout moves, or its `.venv` is rebuilt or
  deleted, the light `.venv` breaks with no error until an import fails.
- A setup line calls no program of the main checkout's `.venv` but
  `python.exe`. Its other programs (`pytest.exe` and the like) name
  their interpreter by an absolute path that may be stale; the light
  form runs everything as `python.exe -m <module>`.
- The `.pth` is written without a byte-order mark (`Set-Content
  -Encoding ascii`). Windows PowerShell 5.1 writes one with `-Encoding
  utf8`, and Python then reads a path that names no folder.
- So a main checkout whose path has a character outside ASCII cannot
  use the light list: its `setup` is the full list.
- A hook that makes its own environment, such as a `language: python`
  pre-commit hook, is not affected by either list.

## The owner's list of projects

The config file sits in the project, and its setup lines run as
written. A session that may run the script could otherwise make a
folder of its own with its own config and its own weak settings file,
and run the script there. So `-Apply` acts only where the main checkout
is named in `<user profile>/.claude/dispatch-projects.json`:

```json
{ "projects": ["C:/path/to/the/main/checkout"] }
```

The script takes the profile folder from the system, not from an
environment variable. A dry run works in any project, since it runs
nothing, and says whether `-Apply` would be refused there.

## Server-side rulesets

A hook and a deny rule are guards inside a session. A ruleset is held by
GitHub, for every login, the owner's included. The owner adds two on the
repository's Rules page (Settings, Rules, Rulesets), each Active and
with an empty bypass list:

| Ruleset | Target | Branch rules |
|---|---|---|
| `main: require PR` | the default branch | Require a pull request before merging (no approval count), Block force pushes, Restrict deletions |
| `all branches: no force push` | all branches | Block force pushes, and no other |

- **The one trap:** GitHub may pre-tick Restrict deletions on the second
  ruleset. Untick it, or no merged branch can be deleted.
- **The check:** `gh api repos/<owner>/<repo>/rulesets` lists both, and
  `gh api repos/<owner>/<repo>/rulesets/<id>` shows
  `current_user_can_bypass: never` for each.
- **The test, by the owner's hand only.** A force push is under "Never"
  for every agent. It uses a throwaway branch and two commits of the
  repository, the later one first:

  ```
  git push origin <later commit>:refs/heads/ruleset-test
  git push --force origin <earlier commit>:refs/heads/ruleset-test
  git push origin --delete ruleset-test
  ```

  GitHub must refuse the second push with `GH013` and "Cannot force-push
  to this branch". The first and the third must succeed.
- **Where a push to any branch starts workflows,** skip the test push:
  the proof is the API read and the next normal run.

## The permission mode

There is no key for the permission mode. The script starts every builder
in `dontAsk`, and nothing in the config or on the command line can
change that.

## Tiers

| Tier | Model | Effort | Turn cap |
|---|---|---|---|
| haiku | claude-haiku-5-5 | medium | 15 |
| low | claude-sonnet-5-5 | medium | 30 |
| medium | claude-sonnet-5-5 | high | 80 |
| high | claude-opus-5-5 | medium | 200 |

No tier, no dispatch: the script refuses a run without `-Tier`.

The turn cap is advice, not a limit. The `claude` start command has no
turn-limit option (`claude --bg` is an interactive session, and the one
budget option, `--max-budget-usd`, works only with `--print`), so the
script adds "Or stop after N turns." to the prompt and nothing stops a
session that runs past it. What the script does enforce is the number:
`-TurnCap` can only lower the tier's cap. Raising a cap is the owner's, in
the config's `tiers`.

## Dispatch

```
dispatch.ps1 -Name <name> -Tier <haiku|low|medium|high> -PromptFile <file>
             [-Profile <name>] [-TurnCap <n>] [-Base origin/<branch>]
             [-FullSetup] [-NoSetup] [-Project <folder>] [-Apply]
```

Without `-Apply` the script reads the config, the brief, the deny list
and the profile, prints every command it would run, the setup list
included by its name, and changes nothing.
Read that output, then run the same line with `-Apply`.

The script refuses, with exit code 2 and one line that begins
`dispatch refused:`, when:

- the config file is missing;
- no tier is given, or the tier is not in the table;
- the name is not lower-case letters, digits and hyphens;
- the brief or the read line holds a double quote;
- the builders' settings file is missing or has no deny rule;
- the agent, the model, the effort, the prompt, a deny rule or a
  profile's allow rule starts with a hyphen, so no value can pass for a
  flag of the CLI;
- `-Profile` is given and: the config names no profiles file, the file
  is missing or not JSON, the profile is not in it (the refusal lists
  the profiles that are), the name is not lower-case letters, digits and
  hyphens, the profile has no rule and no base file, a rule is not a
  string, holds a double quote or ends in a backslash, or its base file is missing, not JSON or lacks a shared
  deny rule;
- `-TurnCap` is zero, negative, or above the tier's cap;
- `-FullSetup` is given without `-NoSetup`, and the config's `setupFull`
  is empty or missing;
- `-Base` is not `origin/<branch>`, or starts with a hyphen;
- `-Apply` is given and the project is not on the owner's list;
- `-Apply` is given, the worktree is not there yet, and `git fetch origin`
  fails in the main checkout, or the base (`refs/remotes/<base>`, so a
  local branch or tag of the same name cannot stand in for it) does not
  exist after it (nothing is started).

The dry run prints the base, `origin/main` unless `-Base` names another,
with its commit as of the last fetch. It does not fetch.

With `-Apply` it fetches `origin` in the main checkout (that moves no
file and not the checkout's branch), makes the worktree
`.claude/worktrees/<name>` on branch `worktree-<name>` at the base, with
no upstream, runs the chosen setup list (see [Setup](#setup)), starts the session in the
background, and checks that the session is alive and runs in its
worktree. If the check fails it stops the session and says so. A worktree
already there is left as it is, at whatever base it has, and no fetch is
made for it.

`-Base` is for a stacked brief: the brief's `Base:` line names
`origin/<branch>` of an open PR in the same repository, and the manager
passes it on. The default is `origin/main`.

Follow-up is not in the script. Its commands are in
`skills/session-dispatch/references/dispatch.md`.

## Closeout

```
python closeout.py <main checkout> <builder name> [--branch <name>]... [--apply]
python closeout.py <main checkout> --list
```

Python 3.8 or later, standard library only, so any project's
interpreter runs it. The manager runs it right after it merges a
builder's PR and pulls: first the dry run, then with `--apply`. It
removes the builder's worktree, then its local branch, only when the
branch is merged (the head of a PR merged into the main branch, or an
ancestor of one, or nothing of its own beyond the remote main branch; a
PR merged into any other base does not count) and has no open PR,
`git status --porcelain --untracked-files=normal --ignore-submodules=none`
prints nothing, whatever the git config says (lines that hold no content, a
line-ending flag with an empty diff or a deleted tracked file, are
restored first), the worktree is not locked, its HEAD can be read, no
folder link in it points out, and, on Windows, nothing in it is open.
There is no force option.
Everything it refuses is printed as one list for the owner's queue and
left where it is.

`--list` changes nothing. It prints every worktree git knows with its
verdict, and ends with one `count of worktrees:` line, one bucket per
worktree: merged and still there, no commit of its own, unknown, open
PR, locked, no readable HEAD, refused for another reason, outside the
folder. The manager runs it at every state-back.

The script's own git calls are not seen by the git-guardrails hook,
which judges tool calls only. The script is the guard, which is why it
is one reviewed file under one exact allow rule in the managers'
settings file. The full rules are in
`skills/session-dispatch/references/dispatch.md`, "The closeout
script", and the decision in ADR-0020 of the tools repository.

## Profiles

A profile is a named list of rules for one kind of ticket, so one
ticket's wider access is not an edit to the shared builders' file that
widens it for every builder running at the time. The owner writes the
profiles file; no agent does.

```json
{
  "profiles": {
    "research": {
      "baseSettings": ".claude/research.settings.json",
      "allow": ["WebSearch", "WebFetch", "Edit(builder-state/**)"],
      "deny": ["Bash(gh pr *)"]
    }
  }
}
```

With `-Profile <name>`:

- `allow` rules go to the session with `--allowedTools`, after the
  prompt. They add to the settings file's allow list, not replace it.
- `deny` rules go with `--disallowedTools`, after the shared deny list.
- The shared deny list is always passed. A deny wins over any allow, so
  no profile removes a shared deny.
- `baseSettings`, optional, names a settings file passed on
  `--settings` in place of the shared builders' file. A profile needs
  one to allow *less* than the shared file: the shared file allows bare
  `Edit` and `Write`, and a profile's rules only add, so an
  `Edit(builder-state/**)` rule narrows nothing while the shared file is
  on `--settings`. The script refuses a base file that is missing or
  whose deny list lacks any shared deny rule, and still passes the
  shared denies on `--disallowedTools`. A base file must allow every
  tool the project's `readLine` asks the builder to use.
- The header prints the profile, each of its rules, and which settings
  file is used. Without `-Profile` it prints `profile: none` and the
  start command is as before.

Scope a write with `Edit(path)`, never `Write(path)`: a `Write(path)`
rule matches nothing, and an `Edit(path)` rule covers the Write tool. A
relative path passed by flag is read from the session's working
directory, the worktree.

Probes have one profile, `probe`, with exactly one rule:
`Bash(.venv/Scripts/python.exe builder-state/probe.py)`. No argument,
no wildcard, never `builder-state/*.py`. The builder writes the script
at that fixed path, and it enforces its own `ALLOWED_HOSTS` on every
request and every redirect hop. The brief names the hosts, and the
manager reads `builder-state/probe.py` against them at closeout. A
script that changes data is not a probe. The rule never goes in the
shared builders' file or in another profile.

A script run once for one ticket that changes data that is not rebuilt
has one profile, `oneshot`, with exactly one rule:
`Bash(.venv/Scripts/python.exe builder-state/oneshot.py)`. No argument,
no wildcard. The brief names the data the script may change. The
builder posts the script whole on its ticket and parks before the run,
which waits for the owner's answer; the manager reads the script before
it relays that answer and again at closeout. A project without the
profile keeps a rule the owner adds by hand. The rule never goes in the
shared builders' file or in another profile.

These points were tested in throwaway sessions (Claude Code 2.1.318),
recorded on tools issue #83: `--allowedTools` adds to the `--settings`
allow list under `dontAsk`; a settings-file deny beats an exact
`--allowedTools` allow; a relative `Edit(builder-state/**)` passed by
flag anchors at the working directory.

## The owner's queue

Every session leaves what waits on the owner in a project's
`.claude/memory/NEEDS-OWNER.md`: one queue per project, untracked, and
an entry goes to the queue of the repo its ticket lives in
(`session-rules`, `references/parking.md`). The `owner-queue` plugin of this
repository (0.5.0 or later) shows that file as a pane and carries an
answer back to the session that asked. This plugin works without it: the
queue is then read and answered in the file.

## Tests

`tests/test_session_dispatch.py`, at the repository root, runs the
script's dry run against a temporary project (Windows only; skipped
elsewhere). It covers each refusal, the start command for each tier, that a
dry run creates nothing, that `-Apply` is refused in a project
the owner has not listed, and a profile's rules, base file and header.

`tests/test_closeout.py` builds throwaway repositories and runs
`closeout.py` against them on every platform: each refusal, a removal,
the dry run and list-only mode changing nothing, and what git itself
does with ignored files, an open file and a link out of a worktree.

## Not proven

A real start with `-Apply` has not been run from this plugin's tests.
One point to watch at the first one: whether `--disallowedTools` takes
path-scoped rules such as `Edit(.claude/settings.json)`. If it does not,
those rules are still enforced by the builders' settings file.
