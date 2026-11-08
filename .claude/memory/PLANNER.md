# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-08, at a context clear. `main` was at `dcd351a`.

## START HERE

- You are **Tools-central-planner**, the standing planner for
  `benjamininja/skills-plugins-hooks-agents` (since 2026-11-07).
- Read the open issues with their `tier:` labels:
  `gh issue list -R benjamininja/skills-plugins-hooks-agents --state open`.
- **The dynasty builder manager** dispatches and merges here. Address it
  by session id, `local_39e3ac7a-9d6d-4524-82e4-9b5f0e6db274`; its name
  address has gone stale before.
- **The dynasty planner** (`local_84c6f2af-95ee-4c21-9c02-95877dc0cd21`)
  sends work for this area to you.
- **Queue entries.** Every ask to the owner goes to the manager as a ready
  queue entry: the context, the exact command or paste text, the options
  (each one standing alone, #94), and your recommendation first. A bare
  one-line ask is useless to the owner. Put this session's id on the
  entry, as `/owner id` prints it. Before 2026-11-08's clear the id was
  `4dcde8eb`; check it again after a clear.
- **After every merge**, the owner pulls the main checkout and the live
  clone `C:\Users\benha\claude-live\skills-plugins-hooks-agents`. Every
  `~/.claude` link, and since 2026-11-08 the owner-queue plugin directory,
  point into that clone. Give the exact command:
  `git -C C:/Users/benha/claude-live/skills-plugins-hooks-agents pull --ff-only`.

## What this session answers for

Tickets, tiers, `Profile:` lines and briefs for this repository, and
gaps found in the session-dispatch and owner-queue plugins. Not building,
not dispatching, and never a settings file or `.claude/dispatch.json`.
The baseball handoff doc is also this session's to keep current.

## Maps

The 2026-11-08 dispatch order, with the owner's go for wave 1:

- **Wave 1:**
  - #56: t56 is building.
  - #81: t81 has parked; see "Waiting" below.
  - #80: closed, not planned, with a reopen condition.
- **Can go any time:** #94 (low).
- **Vendor lane, one ticket at a time:** #49 → #57 → #52 → #50.
  - #52 needs no `--bless`, so it can go first.
  - #50 is high and needs the owner's word.
- **Then #55**, after #50 and #56.
- **#47** goes in its own lane: high, needs the owner's word, and can't run
  beside #54 (both edit `README.md`).
- **Held for owner-led steps:** #48 first, then #51, #53 and #54, which also
  need the owner's `--apply` run and junction changes.

## Waiting

- **#81:** the owner answered (issuecomment-6723739198): option (a), and
  builders run `claude plugin test plugins/owner-queue`. Amendment 1 (the
  README Install section) and amendment 2 (the parser fix,
  issuecomment-6723749482) are on the ticket. t81 builds once the owner has
  added `"Bash(claude plugin test plugins/owner-queue)"` to this repo's
  `.claude/builders.settings.json`.
  - **Not yet sent:** a message telling the manager that this Decision is
    answered, to pass the answers and amendment 2 to t81, and to close out
    t80. The send was refused by the auto-mode classifier on 2026-11-08.
    Ask the owner first; don't route around it.
- **Owner Decision:** the `--bless` allow rule for tools builders, queued
  with session id `4dcde8eb`. The vendor lane waits on it.

## Milestones

- 2026-11-07: builder profiles shipped (#83 → PR #84).
- 2026-11-07/08: session-rules gained several rules:
  - a refused call ends a builder's attempt, and probe hosts are named
    (#82 → PR #86);
  - the probe path and the `Profile:` line (#87 → PR #90);
  - reading the web, robots.txt first, in a call of its own (#88 → PR #92).
- 2026-11-08: the research base template allows `Skill` (#85 → PR #89).
- 2026-11-08: this file and the planner line in PROJECT-RULES (PR #91);
  the baseball handoff (PR #93).
- 2026-11-08: the owner-queue mod loads from the live clone. Before that
  it loaded from a hand copy in `~/.claude/mods`.

## Sweeps

None.

## Gaps

- **#58:** an untracked `GEMINI.md` and `.agents/` sit in the owner's main
  checkout. They are the owner's to keep or drop before #58 builds.
- **#48:** builders are denied edits to `.claude/agents/`, so agent changes
  are owner-led.
- **Owner-queue only reaches sessions in a project with its own
  `NEEDS-OWNER.md`.** This repo has none, so its sessions' entries go
  through dynasty's queue and need the right `Session:` id. The README fix
  is in #81.
- **The baseball handoff.**
  [docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md)
  is for SpunkyLlama's agent. Update it when what it points at changes:
  the owner-queue version after #81, plugin versions, and template
  commits. Its credential step stays generic: no file, ref or host in a
  public repo. The owner gave SpunkyLlama the exact locations privately.

## Decided since

Owner decisions, each recorded on its ticket:

- Builders only: a refused call ends the attempt (#82).
- The probe-host control applies in every project (#82).
- A profile's own base file, option A (#83).
- One fixed probe path (#83).
- robots.txt first, in every project, read in a call of its own (#88).
- The manager may merge Green PRs here (2026-11-07).
- #81: comments and Send as answer wait for Submit; builders run the pane
  tests (2026-11-08).
- The baseball handoff is merged only after SpunkyLlama has been told
  privately (#93, 2026-11-08).

## Lessons

- A probe rule's exact name never limited what the script does. What
  limits a probe is the hosts named in its brief, its `ALLOWED_HOSTS`
  check and the manager's read at closeout.
- A `Write(path)` rule matches nothing. Scope writes with `Edit(path)`.
- A base settings file must allow every tool the project's `readLine`
  uses (`Skill`, #85).
- A builder can't start a test session. Put CLI-behavior checks on the
  manager before dispatch.
- The vendor tool has no `--check` flag. The check is the no-argument run,
  which uses the network, so the manager runs it.
- Never name the file, ref or host of someone else's leaked credential in
  a public repo or PR. Keep the text generic, and pass the exact location
  privately (#93).
- A PR from a worktree outside the session's folder can't use
  `/security-review`, and the git guardrail reads the session folder's
  branch. Use `git -C <worktree>` with an explicit `push origin <branch>`.
