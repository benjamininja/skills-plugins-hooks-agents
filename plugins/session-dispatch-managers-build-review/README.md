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
| `scripts/resume_plain.ps1` | Resumes a stopped builder with a follow-up message and no other flag. The manager uses it for a follow-up when SendMessage cannot reach the builder. |
| `skills/session-rules` | The rules every role keeps: tiers, briefs, the "Never" list, a denied call, parking, who may merge. Any session may load it. It starts nothing. |
| `skills/session-dispatch` | The manager's procedures that change things: dispatch, merging a builder's PR, closeout. Manual only (`disable-model-invocation: true`): the owner invokes it in a manager's session. |
| `templates/` | Blank files for a new project: three role files and the code reviewer agent, the config, the queue file, the project rules file, two state files, three example settings files, an example profiles file, a brief and a gap ticket. |

## Install

Point Claude Code at the plugin folder, as for any plugin under
development:

- one session: `claude --plugin-dir <this folder>`;
- every session: name the folder in `CLAUDE_CODE_PLUGIN_DIRS`.

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
   (`session-rules`, `references/code-review.md`). Copy
   `PROJECT-RULES.md`, `NEEDS-OWNER.md`,
   `PLANNER.md` and `MANAGER.md` to `.claude/memory/`. Fill in
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

## The config, `.claude/dispatch.json`

| Key | Meaning |
|---|---|
| `agent` | The agent a builder runs as: a file in `.claude/agents/`, without `.md`. |
| `buildersSettings` | The builders' settings file, from the main checkout. Its `permissions.deny` list is also passed to the session. |
| `buildersProfiles` | Optional. The owner's profiles file, from the main checkout, for `-Profile`. See [Profiles](#profiles). |
| `claude` | The Claude CLI: a name on `PATH` or a full path. |
| `setup` | PowerShell lines run in the new worktree before the session starts. They run as written, which is why only the owner writes this file. |
| `readLine` | The first lines of every builder's prompt. No double quote. |
| `tiers` | Optional overrides of the tier table: `model`, `effort`, `turnCap` per tier. |

A key that starts with `//` is a note and is not read.

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

## The permission mode

There is no key for the permission mode. The script starts every builder
in `dontAsk`, and nothing in the config or on the command line can
change that.

## Tiers

| Tier | Model | Effort | Turn cap |
|---|---|---|---|
| low | claude-sonnet-5-5 | medium | 30 |
| medium | claude-sonnet-5-5 | high | 80 |
| high | claude-opus-5-5 | medium | 200 |

No tier, no dispatch: the script refuses a run without `-Tier`.

## Dispatch

```
dispatch.ps1 -Name <name> -Tier <low|medium|high> -PromptFile <file>
             [-Profile <name>] [-TurnCap <n>] [-NoSetup] [-Project <folder>] [-Apply]
```

Without `-Apply` the script reads the config, the brief, the deny list
and the profile, prints every command it would run, and changes nothing.
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
- `-Apply` is given and the project is not on the owner's list.

With `-Apply` it makes the worktree `.claude/worktrees/<name>` on branch
`worktree-<name>`, runs the setup lines, starts the session in the
background, and checks that the session is alive and runs in its
worktree. If the check fails it stops the session and says so.

Follow-up and closeout are not in the script in 0.1.0. Their commands
are in `skills/session-dispatch/references/dispatch.md`.

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

These points were tested in throwaway sessions (Claude Code 2.1.318),
recorded on tools issue #83: `--allowedTools` adds to the `--settings`
allow list under `dontAsk`; a settings-file deny beats an exact
`--allowedTools` allow; a relative `Edit(builder-state/**)` passed by
flag anchors at the working directory.

## The owner's queue

Every session leaves what waits on the owner in
`.claude/memory/NEEDS-OWNER.md`. The `owner-queue` plugin of this
repository (0.5.0 or later) shows that file as a pane and carries an
answer back to the session that asked. This plugin works without it: the
queue is then read and answered in the file.

## Tests

`tests/test_session_dispatch.py`, at the repository root, runs the
script's dry run against a temporary project (Windows only; skipped
elsewhere). It covers each refusal, the start command for each tier, that a
dry run creates nothing, that `-Apply` is refused in a project
the owner has not listed, and a profile's rules, base file and header.

## Not proven

A real start with `-Apply` has not been run from this plugin's tests.
One point to watch at the first one: whether `--disallowedTools` takes
path-scoped rules such as `Edit(.claude/settings.json)`. If it does not,
those rules are still enforced by the builders' settings file.
