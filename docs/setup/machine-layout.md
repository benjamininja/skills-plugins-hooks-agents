# Machine layout

Every machine that runs these projects uses the same folders. This
document names them, says what depends on each, and gives the order of a
cold setup. A session on a new or restored machine can start from here.

It holds layout only. It repeats no step that another document owns, and
nothing from the private settings files.

## The rule

**Every machine uses the same user name and the same four roots below.**
The owner's settings files hold absolute paths and are tracked as they
are (#217, choice 3). With one layout they are identical on every
machine, and nothing has to be built to adapt them. A machine that
differs gets no error: a path in a settings file or a link simply stops
resolving.

## The four roots

| Root | Path | What lives there |
|---|---|---|
| User folder | `C:\Users\benha` | The configuration folder and the live clone. |
| Configuration folder | `C:\Users\benha\.claude` | A clone of the owner's private configuration repository: the global `CLAUDE.md`, the settings files, cross-project memory. Also the skill, agent and hook links, which are made on each machine and not tracked. |
| GitHub folder | `C:\source\Github` | One main checkout per project, named for its repository. Role sessions and builders work in worktrees under a checkout's `.claude\worktrees`. It is outside the user folder and outside any synced folder (#235). |
| Live clone | `C:\Users\benha\claude-live\skills-plugins-hooks-agents` | A second clone of this repository that only ever holds merged `main` and is never edited by hand. |

## What depends on each

- **Configuration folder.** Claude Code reads its settings and the
  global `CLAUDE.md` from here. Each project's `CLAUDE.md` names the
  preferences file in it by full path.
- **GitHub folder.**
  - The skill, agent and hook links point into this repository's main
    checkout here ([ADR-0011](../adr/0011-unified-distribution-architecture.md),
    Revision 3). A junction holds an absolute path: if the checkout
    moves, every link breaks without a message.
  - The settings files name folders here by full path, among them each
    project's owner queue file.
  - The closeout pulls name this repository's main checkout
    ([PROJECT-RULES.md](../../.claude/memory/PROJECT-RULES.md),
    "Closeout pulls").
- **Live clone.**
  - Plugins load from its `plugins\` folders; the settings file names
    them by full path (#195).
  - The manager runs its re-proof from here, and pulls it with the main
    checkout after every merge (#112).
- **Inside a checkout, made on each machine and never tracked:** the
  project's `.venv`, its raw data folders, its worktrees, its owner
  queue file. A fresh clone has none of them.

## A cold setup, in order

Each step is owned by the document it names. This list gives only the
order.

1. Create the user with the same name, and install Git, the GitHub CLI,
   Python and Claude Code.
2. Restore the configuration folder from the owner's private
   configuration repository, by that repository's own restore guide.
   Sign in again: credentials are never tracked.
3. Clone each project into the GitHub folder, under its repository's
   name.
4. Clone this repository a second time as the live clone, at the path
   above.
5. Make the links: [README.md](../../README.md), "Installation". It says
   which checkout the links point at: the main checkout where a manager
   runs closeout pulls, the live clone elsewhere.
6. Per project: its virtual environment and its hooks, by that project's
   own `CLAUDE.md` and rules file.
7. Quit the Claude desktop app fully and start it again. A session reads
   its plugin folders once, when the app starts it.
8. Start one role session. It reads its state file and finds its work
   from there.

## Checking a machine against this document

Each line must print `True`:

```powershell
Test-Path "C:\Users\benha\.claude\settings.json"
```

```powershell
Test-Path "C:\source\Github\skills-plugins-hooks-agents\skills"
```

```powershell
Test-Path "C:\Users\benha\claude-live\skills-plugins-hooks-agents\plugins"
```

The links are checked with a dry run, which changes nothing and must
report nothing to create or repoint:

```powershell
.\tools\relink_live.ps1 -Source C:\source\Github\skills-plugins-hooks-agents
```

The two clones of this repository must sit at the same merged commit
(`git log -1 --oneline` in each). A read-only check that a role session
runs at its start is planned in #219; when it exists it replaces this
section.

## When the layout changes

A root is moved only by a change to this document first, in a PR, with
the settings files, the links and the closeout pulls brought along in
the same sitting. The GitHub folder's move out of OneDrive on
2026-11-19 (#235) was such a change.

## Not covered here

- What the settings files hold, and the order of the private restore:
  the owner's private configuration repository.
- How the links are made and kept: `README.md`, "Installation".
- How a role session starts and what it reads: the `session-rules`
  skill and each project's rules file.
