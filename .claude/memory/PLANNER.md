# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-09, at a third context clear. `main` was at
`76b8c89`.

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
  sends work for this area to you, and since 2026-11-09 plans the
  owner-queue mod (see "What this session answers for").
- **Your own ids.** The app session id is
  `local_9830794b-c1e9-400a-ba66-e6abb9432396` and stays the same. The
  queue id changes at every `/clear`: it was `4dcde8eb`, then `ca5b616a`,
  then `2dd6e973`. After a clear, learn the new one and send it to the
  manager for any open entry that names the old one (see "Queue entries
  raised"). You learn it either way:
  - the owner-queue mod tells you in the system prompt, but only once a
    queue is read. This repo has no queue of its own, so the line needs
    the owner's `queues` setting to list dynasty's queue. On 2026-11-09 it
    wasn't set yet, and the dynasty planner was giving the owner the
    block;
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
- **After every merge**, the manager pulls both checkouts at closeout
  ([PROJECT-RULES.md](PROJECT-RULES.md), "Closeout pulls"; #112):
  - **the main checkout:** `~/.claude/agents`, `~/.claude/skills/*` and
    `~/.claude/hooks/*` link here;
  - **the live clone** `C:\Users\benha\claude-live\skills-plugins-hooks-agents`:
    the plugins load from here.

  Check the heads the manager reports against `origin/main`. Hand the
  owner pull commands only for a pull the manager has parked.
- **Your own PRs** (state-backs, syncs, rule lines) come from a worktree
  under `.claude/worktrees/`, never by switching branches in the main
  checkout. Use `EnterWorktree`, so that the session's folder is the
  worktree, and `/security-review` and the git guardrail see its branch.
  The worktree `t112-closeout-pulls` holds merged or open-PR branches
  only: make each new PR there on a fresh branch from `origin/main`, after
  `git status` shows it clean.

## What this session answers for

- Tickets, tiers, `Profile:` lines and briefs for this repository.
- Gaps found in the session-dispatch plugin and in this repo.
- This repo's `PROJECT-RULES.md`.
- The baseball handoff doc.

**Not the owner-queue mod.** Since 2026-11-09 the dynasty planner plans
it (#99, #110, #111, and #104's held decision). Send it anything about the
mod. It sends you each new mod version for the handoff's owner-queue row.

Not building, not dispatching, and never a settings file or
`.claude/dispatch.json`.

## Maps

- **In flight:**
  - #108 (low, the git rm and git mv command form): builder `t108-gitrm`,
    PR #115, green on CI; manager re-proof queued.
  - #99 (the dynasty planner's): PR #107; manager re-proof queued.
  - #112: Part 1 merged (PR #114, `76b8c89`). Part 2, six allow rules in
    dynasty's `managers.settings.json`, is queued for the owner. Close #112
    when both are in.
- **#113 (high), code review at re-proof.** The owner's go is given.
  - Step 0: issuecomment-6730548975.
  - The brief: issuecomment-6730589750.
  - The ruleset:
    - the manager's draft: issuecomment-6730689017;
    - my read: issuecomment-6730710094;
    - the owner's light review: issuecomment-6730815633;
    - amendments 1 to 3: issuecomment-6730858927, -6730867839,
      -6730905864;
    - the dynasty planner's owner-queue rows (P11, P13, P14):
      issuecomment-6730846724.
  - Dispatch after PR #115, PR #107 and #116 (if it is still open) merge.
  - After PR A merges, my planner PR:
    - `PROJECT-RULES.md` Green items: no upheld blocking finding left
      open; `claude plugin test plugins/owner-queue` after a mod change;
      #117's re-proof line, if ready;
    - the live `.claude/agents/pr-code-reviewer.md`, on the owner's word.
  - Dynasty #490 (low) waits for PR A.
- **Waiting for the owner's go:**
  - #116 (medium): the `dispatch.ps1` step 8 bugs from Step 0's review.
  - #117 (medium): commit the manager's re-proof script and run it from the
    live clone. The manager was asked to post its `tgreen.sh` there.
- **Vendor lane, one ticket at a time:** #49 closed (PR #103), then #57
  (medium) → #52 → #50.
  - #52's delete steps are no longer blocked: the git rm and git mv allow
    lines are in.
  - #50 is high and needs the owner's word. It also carries the ADR-0006
    tightening line (comment on #50).
- **Then #55**, once #50 has merged.
- **#47** has a lane of its own: high, needs the owner's word, and can't
  run beside #54 (both edit `README.md`).
- **Held for owner-led steps:**
  - #48 first, then #51, #53 and #54;
  - those three also need the owner's `--apply` run and junction changes;
  - #54's builder checks whether `powerbi-report-cli` hands off to
    `semantic-model-authoring` (#49 comment).
- **Any time:** #58 (low). It waits on the owner keeping or dropping the
  untracked `GEMINI.md` and `.agents/` in the main checkout.

## Waiting on the owner

- The go on #116 and #117.
- Delete the stray branch `pr109`, which #113's Step 0 left in this repo
  (the manager asked too):
  `git -C C:/Users/benha/OneDrive/Documents/GitHub/skills-plugins-hooks-agents branch -D pr109`.
- **`sync stage-builder`.** The owner ticked the Action on 2026-11-08 at
  19:31, but the live file still lacks the #98 bullet (the correction is on
  #98, issuecomment-6730128372). On those words, open the one-file PR, from
  a worktree, that copies
  `plugins/session-dispatch-managers-build-review/templates/agents/stage-builder.md`
  over `.claude/agents/stage-builder.md`. Until it merges, the manager
  keeps the line in every brief.
- The six-rule Action (#112 Part 2), in the pane.
- #58: keep or drop `GEMINI.md` and `.agents/`.
- The ADR-0011 links finding (see Gaps): a ticket was offered, and the
  owner hasn't answered yet.
- The owner's approval of PR #118, the handoff refresh, and then of this
  state-back's PR. Once #118 merges, tell the owner the handoff is ready
  to share with SpunkyLlama.

## Queue entries raised

Open entries in dynasty's `NEEDS-OWNER.md` that name this session's
queue id. After a clear, re-key each one through the manager.

- None open that name `2dd6e973`. The entries sent this session (the tools
  git rm and git mv line, and #112's six rules) carry no Session line.

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
- 2026-11-09:
  - semantic-model-authoring is manual-only (#49 → PR #103);
  - step 8 waits up to 30 s for the worktree and stops by short id
    (#101 → PR #109);
  - the manager pulls both tools checkouts at closeout (#112 → PR #114);
  - the git rm and git mv allow lines are in both repos' builder
    settings;
  - the baseball handoff was refreshed for owner-queue 0.9.0 (PR #118,
    open at this state-back).

## Sweeps

None.

## Gaps

- **#48:** builders are denied edits to `.claude/agents/`, so agent changes
  are owner-led. The stage-builder sync and the #113 reviewer agent are two
  of these.
- **The `~/.claude` links point at the OneDrive main checkout,** not at the
  live clone that ADR-0011 revision 2 names. Checked 2026-11-09: agents,
  all 38 skills and the 4 hooks. Only the plugins load from the live
  clone. The owner was offered a ticket to re-point them, or to revise the
  ADR.
- **The baseball handoff.**
  [docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md)
  is for SpunkyLlama's agent. It was refreshed 2026-11-09. Update it when
  what it points at changes:
  - the owner-queue version (the dynasty planner sends each one);
  - the session-dispatch version, which hasn't moved since #84;
  - template commits;
  - the #108 command form and #113's review, once they merge.

  Its credential step stays generic: no file, ref or host in a public
  repo.
- **`CLAUDE.md`'s CI sentence is out of date.** CI runs all of `tests/`
  plus the `CATALOG.md` check (`.github/workflows/test.yml`). It is small,
  and has no ticket yet.
- **Builder pushes.** A builder's `git push origin <branch>` is refused,
  because only `git push` and `git push -u origin *` are allowed. Plain
  `git push` works, so this needs no ticket.
- **Not yet asked:** `git merge origin/main`, the form the session-rules
  give for bringing `main` into a branch, isn't in this repo's builder
  allow list. No builder has hit it yet. Offer the owner the line if one
  does.

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
  Checking an entry before it is saved is held (#104, 2026-11-08). This is
  now the dynasty planner's.
- #101: after the wait, the script stops the builder and confirms that it
  is gone (2026-11-08).
- Builders in both repos delete with git rm and rename with git mv, and
  every brief names the paths (#108, 2026-11-09).
- The manager pulls both tools checkouts at closeout (#112, 2026-11-09).
- The dynasty planner plans the owner-queue mod (2026-11-09).
- #113: code review at re-proof, per Q1 to Q15. In this repo, a
  rule-text-only builder PR gets a light review (2026-11-09).
- #117 opened at the owner's word (2026-11-09).

## Lessons

- A probe rule's exact name never limited what the script does. What
  limits a probe is the hosts named in its brief, its `ALLOWED_HOSTS`
  check and the manager's read at closeout.
- A `Write(path)` rule matches nothing. Scope writes with `Edit(path)`.
- A base settings file must allow every tool the project's `readLine`
  uses (`Skill`, #85).
- A builder can't start a test session or run `claude`. Put CLI-behavior
  checks on the manager, as #101's and #113's first steps did.
- The vendor tool has no `--check` flag. The check is the no-argument run,
  which uses the network, so the manager runs it.
- Never name the file, ref or host of someone else's leaked credential in
  a public repo or PR. Keep the text generic, and pass the exact location
  privately (#93).
- A queue id changes at every `/clear`, but the app session id doesn't.
  Address sessions by app id, and re-key `Session:` lines by queue id
  (#99).
- Check the state of the checkouts before relaying a manager's claim
  about them. The manager's view of the checkouts went stale twice on
  2026-11-08.
- Builders finish fast: #104 went from ticket to merge in about two hours.
  Before amending a ticket's scope, check whether its PR is already open
  or merged.
- A ticked pane Action isn't proof that its steps happened. Check the
  file before relaying "done" (the stage-builder sync, 2026-11-09).
- `code-review` forks a general-purpose agent. It starts in the session's
  primary folder, not the caller's, so give it the full PR URL. It may run
  `git fetch` wherever it lands (#113 Step 0).
- A script run as one Bash call hides its inner commands from the
  permission rules: one approval covers all of them (#117).
- In a worktree-isolated session, `git -C` to the main checkout and
  compound commands are refused, and so is `gh … --body` text with
  backticks. Use `--body-file`, and read files outside the worktree with
  the Read or Grep tools.
