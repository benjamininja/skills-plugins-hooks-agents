# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-08, at a second context clear. `main` was at
`31741ac`.

## START HERE

- You are **Tools-central-planner**, the standing planner for
  `benjamininja/skills-plugins-hooks-agents` (since 2026-11-07).
- Read the open issues with their `tier:` labels:
  `gh issue list -R benjamininja/skills-plugins-hooks-agents --state open`,
  and `gh pr list` for open PRs.
- **The dynasty builder manager** dispatches and merges here. Address it
  by app session id, `local_39e3ac7a-9d6d-4524-82e4-9b5f0e6db274`. That id
  stays the same across its clears; its CLI (queue) id changes with each
  clear.
- **The dynasty planner** (`local_84c6f2af-95ee-4c21-9c02-95877dc0cd21`)
  sends work for this area to you.
- **Your own ids.** The app session id is
  `local_9830794b-c1e9-400a-ba66-e6abb9432396` and stays the same. The
  queue id changes at every `/clear`: it was `4dcde8eb` and then `ca5b616a`.
  After a clear, learn the new one and send it to the manager for any open
  entry that names the old one (see "Queue entries raised"). You learn it
  either way:
  - the owner-queue mod tells you in the system prompt, once the owner has
    set its `queues` setting (#104);
  - or the owner runs `/owner id`.
- **The owner's queue** is dynasty's
  `C:\Users\benha\OneDrive\Documents\GitHub\Python-PowerBI-DynastyFantasyFootball\.claude\memory\NEEDS-OWNER.md`.
  Read it at start. Only the manager writes it.
- **Queue entries.** Every ask to the owner goes to the manager as a ready
  entry, with:
  - the context;
  - the exact command or text to paste;
  - the options, each one standing alone (#94);
  - your recommendation first.
  A bare one-line ask is useless to the owner.
- **Ask the owner** with the context, then the pros, the cons and the
  recommendation, written above the question (root `preferences.md`).
- **After every merge**, the owner pulls both checkouts:
  - **the main checkout:** `~/.claude/agents`, `~/.claude/skills/*` and
    `~/.claude/hooks/*` link here;
  - **the live clone** `C:\Users\benha\claude-live\skills-plugins-hooks-agents`:
    the plugins load from here.

  Give both commands:
  `git -C C:/Users/benha/OneDrive/Documents/GitHub/skills-plugins-hooks-agents pull --ff-only`
  and
  `git -C C:/Users/benha/claude-live/skills-plugins-hooks-agents pull --ff-only`.
  Before giving them, check with `git diff --name-only <old> origin/main`
  that nothing incoming touches the main checkout's local changes.
- **Your own PRs** (state-backs) come from a worktree under
  `.claude/worktrees/`, never by switching branches in the main checkout.

## What this session answers for

Tickets, tiers, `Profile:` lines and briefs for this repository, and
gaps found in the session-dispatch and owner-queue plugins. This session
develops the owner-queue mod's design. Not building, not dispatching, and
never a settings file or `.claude/dispatch.json`. The baseball handoff doc
is also this session's to keep current.

## Maps

- **Ready for dispatch, with the owner's go:**
  - #99 (medium): "Yes, go 99", relayed 2026-11-08.
- **Waiting for the owner's go:**
  - #101 (low): the owner answered its Decision (a); amendment 2 adds stopping a resume copy at once.
  - #108 (low): the git rm command form.
- **In flight:** PR #103 (#49): manager re-proof done; it waits on the
  owner's Decision on the auditor's table.
- **Vendor lane, one ticket at a time:** #49 → #57 → #52 → #50.
  - The `--bless` allow rule is in.
  - #50 is high and needs the owner's word. It also carries the ADR-0006
    tightening line (comment on #50).
- **Then #55**, now that #56 has merged and once #50 has.
- **#47** has a lane of its own: high, needs the owner's word, and can't
  run beside #54 (both edit `README.md`).
- **Held for owner-led steps:**
  - #48 first, then #51, #53 and #54;
  - those three also need the owner's `--apply` run and junction changes;
  - #54's builder checks whether `powerbi-report-cli` hands off to
    `semantic-model-authoring` (#49 comment).
- **Any time:** #58 (low). It waits on the owner keeping or dropping the
  untracked `GEMINI.md` and `.agents/` in the main checkout.

## Waiting

- **The owner's Action, queued by the manager:** pull both checkouts to
  `31741ac`, set owner-queue's `queues` setting to dynasty's
  `NEEDS-OWNER.md`, and check the pane in a tools session. When that is
  done, this session sees dynasty's queue live.
- **The stage-builder sync:** an owner Action for the manager to queue. It
  was sent 2026-11-08 with no Session line. The step is for the owner to
  say `sync stage-builder` here. Then open a one-file PR, from a worktree,
  that copies
  `plugins/session-dispatch-managers-build-review/templates/agents/stage-builder.md`
  over `.claude/agents/stage-builder.md` (the bullet from #98, PR #102).
- **The owner's go on #101**, to relay to the manager.
- **Deleting and renaming files.** The owner chose (a) for dynasty (dynasty #459 issuecomment-6729399851) and, on 2026-11-09, the same for tools: "Yes, add it (Recommended)".
  - **The owner's Action, sent to the manager to queue:** add `"Bash(git rm *)",` after `"Bash(git add *)",` on line 6 of this repo's `.claude/builders.settings.json`. It blocks the delete steps of #52, #54 and #51.
  - **#108 (low)** adds the session-rules `Command forms` bullet: delete with `git rm <path>`, only paths the brief names; a rename is the new file plus `git rm` of the old one. It needs the owner's go.
  - **Not yet asked:** `git merge origin/main`, the form the session-rules give for bringing `main` into a branch, isn't in this repo's builder allow list. No builder has hit it yet. Offer the owner the line if one does.

## Queue entries raised

Open entries in dynasty's `NEEDS-OWNER.md` that name this session's
queue id. After a clear, re-key each one through the manager.

- None open that name `ca5b616a`. The `--bless` Decision is answered and
  ticked, and the Load-the-mod Action is ticked. The stage-builder Action
  has no Session line.

## Milestones

- 2026-11-07: builder profiles shipped (#83 → PR #84).
- 2026-11-07/08: session-rules gained several rules:
  - a refused call ends a builder's attempt, and probe hosts are named
    (#82 → PR #86);
  - the probe path and the `Profile:` line (#87 → PR #90);
  - reading the web, robots.txt first (#88 → PR #92);
  - an option never refers to another option by its letter (#94 → PR #97).
- 2026-11-08:
  - the research base template allows `Skill` (#85 → PR #89);
  - the planner state file and the planner line in PROJECT-RULES (PR #91);
  - the baseball handoff (PR #93);
  - the planner's first state-back (PR #95);
  - the vendor tool handles paths removed upstream and plugin manifests
    (#56 → PR #96).
- 2026-11-08, owner-queue:
  - comments and typed answers wait for Submit, and option keys are read
    only at boundaries (#81 → PR #100);
  - one pane reads many queues, and a problems log
    (`~/.claude/owner-queue/problems.log`) records what the pane can't draw
    (#104 → PR #105).
- 2026-11-08: a builder continues after the security-review skill, and
  the resume steps take no flags (#98 → PR #102).
- 2026-11-08: #80 closed, not planned, with a reopen condition.

## Sweeps

None.

## Gaps

- **#48:** builders are denied edits to `.claude/agents/`, so agent changes
  are owner-led. The stage-builder sync above is one of these.
- **The baseball handoff.**
  [docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md)
  is for SpunkyLlama's agent. Update it when what it points at changes:
  - the owner-queue version: now past #81 and #104, and not yet updated
    there;
  - plugin versions;
  - template commits.

  Its credential step stays generic: no file, ref or host in a public
  repo.
- **Builder pushes.** A builder's `git push origin <branch>` is refused,
  because only `git push` and `git push -u origin *` are allowed. Plain
  `git push` works, so this needs no ticket.

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
- `--bless`: builders run it themselves; the allow line is in
  (2026-11-08).
- The owner-queue developer's view: one pane reads many queues, the pane
  logs what it can't draw, and every render bug becomes a test fixture.
  Checking an entry before it is saved is held (#104, 2026-11-08).
- #101: after the wait, the script stops the builder and confirms that it
  is gone (2026-11-08).

## Lessons

- A probe rule's exact name never limited what the script does. What
  limits a probe is the hosts named in its brief, its `ALLOWED_HOSTS`
  check and the manager's read at closeout.
- A `Write(path)` rule matches nothing. Scope writes with `Edit(path)`.
- A base settings file must allow every tool the project's `readLine`
  uses (`Skill`, #85).
- A builder can't start a test session or run `claude`. Put CLI-behavior
  checks on the manager, as #101's first step did.
- The vendor tool has no `--check` flag. The check is the no-argument run,
  which uses the network, so the manager runs it.
- Never name the file, ref or host of someone else's leaked credential in
  a public repo or PR. Keep the text generic, and pass the exact location
  privately (#93).
- A PR from a worktree outside the session's folder can't use
  `/security-review`, and the git guardrail reads the session folder's
  branch. Use `git -C <worktree>` with an explicit `push origin <branch>`.
- A queue id changes at every `/clear`, but the app session id doesn't.
  Address sessions by app id, and re-key `Session:` lines by queue id
  (#99).
- Check the state of the checkouts before relaying a manager's claim
  about them. The manager's view of the checkouts went stale twice on
  2026-11-08.
- Builders finish fast: #104 went from ticket to merge in about two hours.
  Before amending a ticket's scope, check whether its PR is already open
  or merged.
