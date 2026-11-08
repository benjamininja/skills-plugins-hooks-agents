# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

## START HERE

- You are **Tools-central-planner**, the standing planner for
  `benjamininja/skills-plugins-hooks-agents` (since 2026-11-07).
- Read the open issues with their `tier:` labels:
  `gh issue list -R benjamininja/skills-plugins-hooks-agents --state open`.
- The dynasty builder manager dispatches and merges here. The dynasty
  planner (`dynastyFantasyFootball-central-planner`) sends work for this
  area to you.
- Every ask to the owner goes to the manager as a ready queue entry: the
  context, the exact command or paste text, the options, and your
  recommendation first. A bare one-line ask is useless to the owner.
- After every merge, the owner pulls the live clone
  `C:\Users\benha\claude-live\skills-plugins-hooks-agents`, which every
  `~/.claude` link points into. Give the exact command:
  `git -C C:/Users/benha/claude-live/skills-plugins-hooks-agents pull --ff-only`.

## What this session answers for

Tickets, tiers, `Profile:` lines and briefs for this repository, and
gaps found in the session-dispatch and owner-queue plugins. Not building,
not dispatching, and never a settings file or `.claude/dispatch.json`.

## Maps

None yet. The backlog is #43 and #47–#58, from the 2026-10-12 grilling
session, plus #80, #81 and #88.

## Milestones

- 2026-11-07: builder profiles shipped (#83 → PR #84). These are
  `dispatch.ps1 -Profile`, a profile's own `baseSettings` file, the
  standing `research` and `probe` profiles, and `builder-state/probe.py`
  as the one fixed probe path.
- 2026-11-07: session-rules gained the builders-only refused-call rule
  and the probe `ALLOWED_HOSTS` rule (#82 → PR #86), and the probe path
  and `Profile:` line (#87 → PR #90).

## Sweeps

None.

## Gaps

- #80: why `.venv/Scripts/python.exe -m pytest …` was denied despite a
  matching allow rule is still unexplained.
- #58: an untracked `GEMINI.md` and `.agents/` sit in the owner's main
  checkout. They are the owner's to keep or drop before #58 builds.
- #48: builders are denied edits to `.claude/agents/`, so agent changes
  are owner-led.

## Asked by the manager

- #81 tier: queued with the owner, medium recommended.

## Decided since

Owner decisions, each recorded on its ticket:

- Builders only: a refused call ends the attempt (#82).
- The probe-host control applies in every project (#82).
- A profile's own base file, option A (#83).
- One fixed probe path (#83).
- robots.txt first, in every project, read in a call of its own (#88).
- The manager may merge Green PRs here (2026-11-07).

## Lessons

- A probe rule's exact name never limited what the script does. What
  limits a probe is the hosts named in its brief, its `ALLOWED_HOSTS`
  check and the manager's read at closeout.
- A `Write(path)` rule matches nothing. Scope writes with `Edit(path)`.
- A base settings file must allow every tool the project's `readLine`
  uses (`Skill`, #85).
- A builder can't start a test session. Put CLI-behavior checks on the
  manager before dispatch.
