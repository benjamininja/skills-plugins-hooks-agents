# Dispatch, watch, follow up, close out

## What the script does

`scripts/dispatch.ps1` (Windows PowerShell), from the plugin's folder:

```
dispatch.ps1 -Name <name> -Tier <low|medium|high> -PromptFile <file>
             [-TurnCap <n>] [-NoSetup] [-Project <folder>] [-Apply]
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
8. Checks that the session has a pid and runs in its worktree. If not,
   it stops the session and says so. Look before a second try.

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
`claude stop <id>` first, then, from the builder's worktree,
`claude --resume <sessionId> --bg <message>` with the same mode,
settings file and `--plugin-dir`. Resuming a session that is still alive starts a copy.
The message holds no double quote.

## Close out, only when a builder has stopped

Never while it is still running, and only for a builder this session
dispatched.

1. For each open PR of that builder: re-prove Green, post the output on
   the PR, then squash-merge. A PR that is not green is not merged; it
   is listed for the owner.
2. `git pull --ff-only` on the main checkout.
3. Delete that builder's remaining branches, each only after
   `git cherry` against the main branch shows nothing missing.
4. Remove that builder's worktree, only if it has no uncommitted file.
   `claude rm <id>` belongs here and nowhere earlier.
5. State-back, then report to the owner with the commands and their
   output.

Anything unmerged, uncommitted or not that builder's is listed for the
owner and left where it is.
