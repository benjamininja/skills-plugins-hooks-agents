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
| `skills/session-rules` | The rules every role keeps: tiers, briefs, the "Never" list, a denied call, parking, who may merge. Any session may load it. It starts nothing. |
| `skills/session-dispatch` | The manager's procedures that change things: dispatch, merging a builder's PR, closeout. Manual only (`disable-model-invocation: true`): the owner invokes it in a manager's session. |
| `templates/` | Blank files for a new project: three role files, the config, the queue file, the project rules file, two state files, two example settings files, a brief and a gap ticket. |

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
3. Copy the three role files from `templates/agents/` to
   `.claude/agents/`, and `PROJECT-RULES.md`, `NEEDS-OWNER.md`,
   `PLANNER.md` and `MANAGER.md` to `.claude/memory/`. Fill in
   `PROJECT-RULES.md`: the project's list of proofs ("Green"), its own
   "Never" lines, its stages.
4. Write the builders' and the managers' settings files, starting from
   the two `*.settings.example.json` files. Add the project's proof
   commands to the builders' allow list. The managers' file needs an
   allow rule for the script; the example has one.
5. Keep deny rules for every settings file, for `.claude/dispatch.json`
   and for the list of projects in both files, so no session can
   change its own fence.

## The config, `.claude/dispatch.json`

| Key | Meaning |
|---|---|
| `agent` | The agent a builder runs as: a file in `.claude/agents/`, without `.md`. |
| `buildersSettings` | The builders' settings file, from the main checkout. Its `permissions.deny` list is also passed to the session. |
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
             [-TurnCap <n>] [-NoSetup] [-Project <folder>] [-Apply]
```

Without `-Apply` the script reads the config, the brief and the deny
list, prints every command it would run, and changes nothing. Read that
output, then run the same line with `-Apply`.

The script refuses, with exit code 2 and one line that begins
`dispatch refused:`, when:

- the config file is missing;
- no tier is given, or the tier is not in the table;
- the name is not lower-case letters, digits and hyphens;
- the brief or the read line holds a double quote;
- the builders' settings file is missing or has no deny rule;
- the agent, the model, the effort, the prompt or a deny rule starts
  with a hyphen, so no value can pass for a flag of the CLI;
- `-Apply` is given and the project is not on the owner's list.

With `-Apply` it makes the worktree `.claude/worktrees/<name>` on branch
`worktree-<name>`, runs the setup lines, starts the session in the
background, and checks that the session is alive and runs in its
worktree. If the check fails it stops the session and says so.

Follow-up and closeout are not in the script in 0.1.0. Their commands
are in `skills/session-dispatch/references/dispatch.md`.

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
dry run creates nothing, and that `-Apply` is refused in a project
the owner has not listed.

## Not proven

A real start with `-Apply` has not been run from this plugin's tests.
One point to watch at the first one: whether `--disallowedTools` takes
path-scoped rules such as `Edit(.claude/settings.json)`. If it does not,
those rules are still enforced by the builders' settings file.
