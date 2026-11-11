# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-10, at a fourth context clear, amended
2026-11-11 after the restart's Do-first work. `main` was at `2090367`
(#126), and both tools checkouts were at it.

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
  then `2dd6e973`, then unknown (the owner hadn't run `/owner id` by the
  2026-11-10 clear). After a clear, learn the new one and send it to the
  manager for any open entry that names an old one (see "Queue entries
  raised"). You learn it either way:
  - the owner-queue mod tells you in the system prompt, but only once a
    queue is read. This repo has no queue of its own, so the line needs
    the owner's `queues` setting to list dynasty's queue. On 2026-11-10 it
    still wasn't set (no `pluginConfigs` in `~/.claude/settings.json`);
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
  ([PROJECT-RULES.md](PROJECT-RULES.md), "Closeout pulls"; #112). Check
  the heads it reports against `origin/main` before relaying them.
- **Your own PRs** (state-backs, syncs, rule lines) come from the worktree
  `.claude/worktrees/t112-closeout-pulls`, on a fresh branch from
  `origin/main` once `git status` shows it clean. Enter it with
  `EnterWorktree` (path), so `/security-review` and the git guardrail see
  its branch. In a worktree session, run one plain git command per call:
  compound commands are refused.
- **Run pytest with the dynasty venv**
  (`C:/Users/benha/OneDrive/Documents/GitHub/Python-PowerBI-DynastyFantasyFootball/.venv/Scripts/python.exe -m pytest -q tests`):
  neither tools checkout has a `.venv`. The full suite takes about 15
  minutes; run it in the background.

## Do first after this clear

1. **Relay the owner's approval of #128, #130 and this PR (#127)** to the
   manager, word for word, and post it on each PR, if the owner has given
   it and it isn't recorded yet. Read each PR's comments first.
2. **Learn your queue id** (above), and send it to the manager only if an
   open entry names an old one.

## What this session answers for

- Tickets, tiers, `Profile:` lines and briefs for this repository.
- Rulings on builder PRs when the manager asks ("no breach" or "plan
  breach", and readings).
- Gaps found in the session-dispatch plugin and in this repo.
- This repo's `PROJECT-RULES.md`.
- The baseball handoff doc.

**Not the owner-queue mod.** The dynasty planner plans it (#99, #110,
#111, and #104's held decision). It sends you each new mod version for the
handoff's owner-queue row.

Not building, not dispatching, and never a settings file or
`.claude/dispatch.json`.

## Open PRs and in-flight work

- **PR #128** (planner, Refs #113): the live
  `.claude/agents/pr-code-reviewer.md`, copied from the template, no model
  line. Split from #126 on the owner's *Separate PR* (2026-11-11), since
  the owner had approved #126 at `fc290a0` without it (#113
  issuecomment-6783382194). CI green. Waits on the owner's approval. Its
  merge turns on #126's code-review Green item.
- **PR #130** (planner, Refs #98): the live `stage-builder.md` gains #98's
  three-line bullet, on the owner's *sync stage-builder* (2026-11-11).
  Waits on the owner's approval.
- **This state-back's PR (#127)**: needs the owner's approval too.
- **PR #121** (#110, owner-queue 0.10.0, the mod re-keys `Session:` lines
  at a `/clear`): CI green; waits on the owner's live-check Action, then
  the manager's re-proof. When it merges, the manager and the dynasty
  planner message you. Then:
  - tell the owner 0.10.0 is checked in and live (check both heads);
  - open one handoff PR changing the owner-queue row (line 43 of
    `docs/handoff/baseball-session-dispatch.md`) to 0.10.0 and the
    session-dispatch and skills rows to the new `main`; the #108 git rm and
    git mv rule and #113's code review may each earn a line under "Rules
    that carry over"; owner approves;
  - after it merges, tell the owner the handoff is ready to share.
- **#124** (low): `tools/reproof.py` gives its export a git index before
  pytest. Found by the manager's first real run (#117
  issuecomment-6732532982). The owner gave the go; builder
  `t124-reproofindex` opened PR #129. After it merges and a real re-proof with the script is GREEN, add
  #117's `PROJECT-RULES.md` line (*the manager re-proves with
  `tools/reproof.py` from the live clone, or with direct commands, never
  with a scratch script*) in a planner PR. Until then the manager uses its
  scratchpad `tgreen.sh`, which that line would forbid.
- **#117**: open until the #124 fix, a GREEN real run and the line above.
  The owner chose the dynasty `.venv` for the interpreter (pane,
  2026-11-10 18:17) and added its allow rule to dynasty's
  `managers.settings.json` (line 24, 2026-11-11).
- **#113**: PR #123 `620815e`, PR #125 `21ce308` and PR #126 `2090367`
  merged. Open for #128 (the live agent) and the first live review run. Dynasty #490 (low) waited for PR A and can go now.
- **#116** closed (PR #120 `94c8ca9`). The manager owes one more real
  dispatch with the new step 8, and the exit code of the first `claude
  stop` that succeeds.

## Waiting on the owner

- Approve #128, #130 and this state-back (#127).
- The #121 live check (queue Action, open).
- The owner-queue `queues` setting: add `pluginConfigs` →
  `owner-queue` → `options` → `queues` (dynasty's `NEEDS-OWNER.md` path)
  to `~/.claude/settings.json` (line 5, before `permissions`), then a new
  session; or `/owner id` here.
- Offered, not answered: a low ticket for a `claude plugin test` step in
  `tools/reproof.py` that runs only when the merge diff touches
  `plugins/owner-queue/` (PR #122 read, issuecomment-6732270477).
- #58: keep or drop the untracked `GEMINI.md` (a 36-line copy of the
  rules, not the thin pointer #58 asks for; recommended: drop) and
  `.agents/` (unread).
- The ADR-0011 links finding (see Gaps). Recommended: revise the ADR,
  since #112's closeout pulls keep both checkouts at one commit.

## Queue entries raised

Open entries in dynasty's `NEEDS-OWNER.md` that name this session's
queue id. After a clear, re-key each one through the manager.

- None. The interpreter Decision (#117) carries the manager's id, not
  this session's.

## Vendor lane and held tickets

- **Vendor lane, one ticket at a time:** #57 (medium) → #52 → #50.
  #50 is high, needs the owner's word, and carries the ADR-0006 tightening
  line (comment on #50). Then #55, once #50 has merged.
- **#47** has a lane of its own: high, needs the owner's word, and can't
  run beside #54 (both edit `README.md`).
- **Held for owner-led steps:** #48 first, then #51, #53 and #54 (they also
  need the owner's `--apply` run and junction changes). #54's builder
  checks whether `powerbi-report-cli` hands off to
  `semantic-model-authoring` (#49 comment).
- **Any time:** #58 (low), after the owner's keep-or-drop.

## Milestones

- 2026-11-07: builder profiles (#83 → PR #84).
- 2026-11-07/08: session-rules rules: a refused call ends a builder's
  attempt (#82 → PR #86); the probe path and `Profile:` line (#87 → PR
  #90); robots.txt first (#88 → PR #92); options never refer to each other
  by letter (#94 → PR #97).
- 2026-11-08: research base allows `Skill` (#85 → PR #89); the planner
  state file (PR #91); the baseball handoff (PR #93); first state-back (PR
  #95); vendor tool handles removed paths (#56 → PR #96); owner-queue
  Submit and boundaries (#81 → PR #100), many queues and a problems log
  (#104 → PR #105); a builder continues after security-review (#98 → PR
  #102); #80 closed, not planned.
- 2026-11-09: semantic-model-authoring manual-only (#49 → PR #103); step 8
  waits 30 s (#101 → PR #109); closeout pulls (#112 → PR #114); git rm and
  git mv (#108 → PR #115); Session lines across a clear (#99 → PR #107);
  the handoff refresh for owner-queue 0.9.0 (PR #118 `c30ce8e`); the
  third state-back (PR #119 `29d6908`); step 8 fixes (#116 → PR #120);
  `tools/reproof.py` (#117 → PR #122 `81afaf0`); the code review at
  re-proof, process (#113 → PR #123) and ruleset `tools-code-review`
  (PR #125).

## Gaps

- **#48:** builders are denied edits to `.claude/agents/`, so agent changes
  are owner-led: the stage-builder sync and the live reviewer agent.
- **The `~/.claude` links point at the OneDrive main checkout,** not at the
  live clone that ADR-0011 revision 2 names. Only plugins load from the
  live clone. The owner was offered a ticket to re-point them, or to revise
  the ADR.
- **The baseball handoff**
  ([docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md))
  is for SpunkyLlama's agent. Update it when the owner-queue version, the
  session-dispatch version, template commits or carried-over rules change.
  Its credential step stays generic.
- **`CLAUDE.md` is out of date** in two places: its CI sentence (CI runs
  all of `tests/` plus the `CATALOG.md` check) and "Three agents live in
  `.claude/agents/`". Small; no ticket yet.
- **Builder pushes.** `git push origin <branch>` is refused for builders;
  plain `git push` works. No ticket needed.
- **Not yet asked:** `git merge origin/main` isn't in this repo's builder
  allow list. Offer the owner the line if a builder hits it.

## Decided since

Owner decisions, each recorded on its ticket:

- Builders only: a refused call ends the attempt (#82). Probe hosts in
  every project (#82). A profile's own base file; one fixed probe path
  (#83). robots.txt first, in a call of its own (#88).
- The manager may merge Green PRs here (2026-11-07).
- #81: comments and Send as answer wait for Submit (2026-11-08).
- The baseball handoff merged only after SpunkyLlama was told privately
  (#93).
- `--bless`: builders run it themselves (2026-11-08).
- #104's developer view (now the dynasty planner's).
- #101: after the wait, stop the builder and confirm it is gone.
- Builders delete with git rm and rename with git mv (#108).
- The manager pulls both tools checkouts at closeout (#112).
- The dynasty planner plans the owner-queue mod (2026-11-09).
- #113: code review at re-proof, per Q1 to Q15; a rule-text-only builder
  PR gets a light review (*Yes, light review*); the live reviewer agent
  has no model line (*Yes, no model line*, 2026-11-10).
- *Approve both*: PRs #118 and #119 (2026-11-09).
- *Go 110 and 116; 117 after 116* (2026-11-09).
- *Approve 126*, and *Merge fc290a0 now* (to the manager); the live
  reviewer agent goes in a *Separate PR* (#128) (2026-11-11).
- *sync stage-builder* (2026-11-11, PR #130).

## Lessons

- A probe is limited by its brief's hosts, its `ALLOWED_HOSTS` check and
  the manager's read at closeout, not by a rule's name.
- A `Write(path)` rule matches nothing. Scope writes with `Edit(path)`.
- A base settings file must allow every tool `readLine` uses (#85).
- A builder can't run `claude`; CLI-behavior checks are the manager's.
- The vendor tool's check is the no-argument run (network), so the
  manager runs it.
- Never name the location of someone else's leaked credential in a public
  repo (#93).
- Address sessions by app id; re-key `Session:` lines by queue id (#99).
- Check the checkouts before relaying a manager's claim about them.
- Before amending a ticket, check whether its PR is already open or
  merged.
- A ticked pane Action isn't proof its steps happened.
- `code-review` forks a general-purpose agent that starts in the session's
  primary folder: give it the full PR URL (#113 Step 0).
- A script run as one Bash call hides its inner commands from the
  permission rules (#117).
- **Before recommending a hold, read the PR's comments:** an approval
  given before a clear is recorded there (#118, 2026-11-09).
- **A note that a step exists "only for X" can hide a second purpose.**
  `tgreen.sh`'s `git init` also gave the tests a repo; the committed
  script dropped it and failed its first real run (#124).
- **Read a ruleset's path list against the owner's later answers.** PR B's
  "anything under `plugins/`" would have given session-rules text the full
  review against the owner's light-review word (#125 ruling).
- **An approval given elsewhere can overtake a Do-first step.** The owner
  approved #126 in another chat before this session pushed to it; check
  the PR's head and any relay before moving an approved head (#128).
- **The worktree commits with the private email,** and a push of it is
  declined. Commit with
  `git -c user.email=38588919+benjamininja@users.noreply.github.com commit ...`.
- **A worktree session can't `git -C` the main checkout.** To check the
  checkouts' heads, Read each one's `.git/refs/heads/main`.
