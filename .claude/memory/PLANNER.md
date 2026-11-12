# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-12, at a sixth context clear. `main` was at
`29f77d5` (#143), and both tools checkouts were at it.

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
  plans the owner-queue mod (#111, #137, #142) and sends you each new
  mod version for the handoff's owner-queue row.
- **Your own ids.** The app session id is
  `local_9830794b-c1e9-400a-ba66-e6abb9432396` and stays the same. The
  queue id changes at every `/clear`. Since 2026-11-11 the owner's
  `queues` setting lists dynasty's queue (`~/.claude/settings.json`,
  `pluginConfigs`), so the owner-queue mod gives you the id in the system
  prompt of a new session. Since owner-queue 0.10.0 the mod re-keys open
  `Session:` lines at a `/clear` itself. If no id line shows up, ask the
  owner to run `/owner id`.
- **The owner's queue** is dynasty's
  `C:\Users\benha\OneDrive\Documents\GitHub\Python-PowerBI-DynastyFantasyFootball\.claude\memory\NEEDS-OWNER.md`.
  Read it at start. Only the manager writes it.
- **Queue entries.** Every ask to the owner goes to the manager as a ready
  entry, with:
  - the context;
  - the exact command or text to paste;
  - the options, each one standing alone (#94);
  - your recommendation first.
- **Ask the owner** with the context, then the pros, the cons and the
  recommendation, written above the question (root `preferences.md`).
- **A new ticket needs the owner's go before dispatch.** The manager
  won't take "the owner may still stop it" as a go (#144, 2026-11-12).
  Ask in chat, or send a queue Decision.
- **After every merge**, the manager pulls both checkouts at closeout
  ([PROJECT-RULES.md](PROJECT-RULES.md), "Closeout pulls"). Check the
  heads it reports by reading each checkout's `.git/refs/heads/main`
  before you relay them.
- **Your own PRs** (state-backs, syncs, rule lines) come from the worktree
  `.claude/worktrees/t112-closeout-pulls`, on a fresh branch from
  `origin/main` once `git status` shows it clean. Enter it with
  `EnterWorktree` (path). In it, run one plain git command per call:
  compound commands, loops and `git -C` are refused. Push with the branch
  named (`git push origin <branch>`). Commit with
  `git -c user.email=38588919+benjamininja@users.noreply.github.com commit -F <file>`.
  Run `/security-review` before opening the PR. On an uncommitted diff it
  sees nothing, so review the real diff yourself.
- **Run pytest with the dynasty venv**
  (`C:/Users/benha/OneDrive/Documents/GitHub/Python-PowerBI-DynastyFantasyFootball/.venv/Scripts/python.exe -m pytest -q tests`):
  neither tools checkout has a `.venv`. The full suite takes about 15
  minutes; run it in the background.

## Do first after this clear

1. **This state-back's PR** needs the owner's approval. Read its comments
   first: the approval may already be recorded. Relay it to the manager
   word for word and post it on the PR.
2. **Sync the live reviewer agent.** PR #143 (#136) changed the template
   `plugins/session-dispatch-managers-build-review/templates/agents/pr-code-reviewer.md`,
   so the live `.claude/agents/pr-code-reviewer.md` now differs from it.
   Copy the template over the live file in a planner PR (as #130 did),
   then ask the owner to approve it. Builders may not write `.claude/`
   (#48).
3. **PR #140 (#135)** is on the owner's **Rule B** (issuecomment-6823618419).
   The owner's condition: if B's re-check finds a new bypass, close #135
   and #140 as won't-fix and open a ticket for F10 alone (`git switch -C
   main` clears `SWITCHED_TO_MAIN`). Wait for the manager's report.
4. **#144** (high): the owner's go is a queue Decision the manager raised.
   On the owner's yes, the manager dispatches. #139 and #143 have both
   merged, so nothing blocks it.

## What this session answers for

- Tickets, tiers, `Profile:` lines and briefs for this repository.
- Rulings on builder PRs when the manager asks ("no breach" or "plan
  breach", scope questions, design questions that aren't the owner's).
- Gaps found in the session-dispatch plugin and in this repo.
- This repo's `PROJECT-RULES.md`.
- The baseball handoff doc.

**Not the owner-queue mod.** The dynasty planner plans it.

Not building, not dispatching, and never a settings file or
`.claude/dispatch.json`.

## Open PRs and in-flight work

- **PR #140** (#135, medium): the push guard reads the worktree's branch.
  The rounds so far: Rule A failed its re-check (F7 to F10, four bypasses),
  and the owner chose Rule B, an allowlist of the exact plain push. t135
  is resuming. A fresh reviewer re-checks, and the manager runs the hook
  tests before merging (Always parks).
- **#144** (high, doc only): an ADR-0015 revision for the first live
  review run, and `relink_live.ps1` help naming both setups. Waiting on
  the owner's go (queue Decision).
- **#137** (medium), **#142** (low, F2 from #121), **#111**: owner-queue,
  all the dynasty planner's. #137 lands after #121, which has merged. When
  it does, the handoff's owner-queue row needs a bump.
- **#112**: open, tier none. Closeout pulls run every merge; nothing is
  left for this session on it.

## Waiting on the owner

- Approve this state-back.
- #144's go (queue Decision).
- The reviewer agent sync PR, once you open it.
- #48's owner-led steps (below).

## Queue entries raised

Open entries in dynasty's `NEEDS-OWNER.md` that name this session's
queue id. After a clear the mod re-keys them; check each one.

- None. The #144 Decision carries the manager's id.

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
- **#58** closed, not planned (2026-11-11): `GEMINI.md` and
  `.agents/AGENTS.md` belong to the owner's Gemini session, which keeps
  them current. Claude sessions don't touch them.

## Milestones

- 2026-11-07 to 2026-11-09: builder profiles (#84); the session-rules
  rules for refused calls, probes, robots.txt and options (#86, #90, #92,
  #97); the planner state file and the baseball handoff (#91, #93);
  owner-queue Submit, many queues and Session lines across a clear (#100,
  #105, #107); closeout pulls (#114); git rm and git mv (#115);
  `tools/reproof.py` (#122); code review at re-proof (#123, #125).
- 2026-11-10/11: Green gains the mod test and the code review (#126); the
  export's git index (#129); the live reviewer agent (#128); the
  stage-builder sync (#130); the fourth and fifth state-backs (#127,
  #132 `10606aa`); the re-proof line (#131 `93833a5`, #117 closed).
- 2026-11-11/12: owner-queue 0.10.0 (#121 `e754faa`, #110 closed); the
  first live code review (it caught #121's F1); #113 closed;
  `reproof.py` runs the mod test (#138 `228e69c`, #133 closed); the
  handoff to 0.10.0 (#141 `8e4cb02`, ready to share); ADR-0011 Revision
  3 (#139 `9dbe4d1`, #134 closed); the code review reads its ruleset from
  `origin/main` and checks the fork on every review (#143 `29f77d5`, #136
  closed).

## Gaps

- **#48:** builders are denied edits to `.claude/agents/`, so agent changes
  are owner-led planner PRs (as #128 and #130 were).
- **The baseball handoff**
  ([docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md))
  is for SpunkyLlama's agent. Update it when the owner-queue version, the
  session-dispatch version, template commits or carried-over rules change.
- **`CLAUDE.md` is out of date** in two places: its CI sentence (CI runs
  all of `tests/` plus the `CATALOG.md` check) and "Three agents live in
  `.claude/agents/`" (more now, with `pr-code-reviewer`). Small; no ticket
  yet.
- **#140 F11:** a `-C` path is final even when it can't be resolved. It
  was already like that on `main`; no ticket yet.
- **Reviewer drift:** the code-review fork strayed from its limits in two
  of the first runs (a `cd`, a `--comment` mention). #143 made the check
  run on every review. If strays keep happening, consider dropping the
  fork (#136 ticket, Not in scope).
- **Not yet asked:** `git merge origin/main` isn't in this repo's builder
  allow list. Offer the owner the line if a builder hits it.

## Decided since

Owner decisions, each recorded on its ticket. Earlier ones are in git
history of this file (state-backs #95 to #132).

- *Approve 131*, *Approve 132 (Recommended)*, *Approve 141
  (Recommended)* (2026-11-11).
- #121's live check: *#121 complete and tested successfully.*
- #58 won't happen; the Gemini session keeps its own files.
- *#2* the `queues` setting (done by the owner), *#4* #133, *#5* ADR-0011
  revised (#134), *#6* the guardrail ticket (#135); *Yes, ticket it*
  (#136).
- #135: *Rule A, fail-closed*, then *Rule B allowlist* (2026-11-12), with
  the drop condition.

## Lessons

- Address sessions by app id; check the checkouts before relaying a
  manager's claim about them.
- Before recommending a hold or asking for an approval, read the PR's
  comments: an approval given before a clear is recorded there.
- A manager that resumes in a new session may miss a relay. Re-send it
  with the PR comment link.
- **A safety hook loosened by a list of forms to catch gets bypassed one
  form at a time.** #140 needed an allowlist (Rule B). Start there for any
  loosening of a guard.
- **A limit text has to allow the tool the same text tells the reader to
  use.** #136's amendment, *only the ruleset skill*, would have forbidden
  code-review itself (#143 F1). Check a new limit against every step.
- **A generic install doc and this machine's setup are different
  audiences.** Ask which one a line speaks for before calling it wrong
  (#134 ruling).
- Worktrees share branch refs, and only `HEAD` is per worktree (#135
  force-delete ruling).
- `/security-review` sees only commits. Commit first, or review the
  working diff yourself.
- A script run as one Bash call hides its inner commands from the
  permission rules (#117).
- A worktree session can't `git -C` the main checkout. Read each
  checkout's `.git/refs/heads/main` instead.
