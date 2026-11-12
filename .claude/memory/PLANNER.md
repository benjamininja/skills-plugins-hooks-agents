# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-12, at a seventh context clear. `origin/main` was
at `5a29cd6` (#151). Both tools checkouts were still at `29f77d5`: the
manager holds the closeout pulls until Rule B (#135) merges, so the live
push hook stays on the stricter pre-#140 version.

## START HERE

- You are **Tools-central-planner**, the standing planner for
  `benjamininja/skills-plugins-hooks-agents` (since 2026-11-07). Call the
  owner **Ben** or "the owner", and yourself **Claude**, never "you" or
  "I" for either (Ben, 2026-11-12, root `preferences.md`).
- **Every question to Ben goes through a button**: AskUserQuestion when
  Ben is in the chat, a queue entry when not. Context, pros, cons and the
  recommendation sit above the question. Never a prose question at the
  end of a reply (Ben, 2026-11-12; #152 carries it into session-rules).
- Read the open issues with their `tier:` labels:
  `gh issue list -R benjamininja/skills-plugins-hooks-agents --state open`,
  and `gh pr list` for open PRs.
- **The dynasty builder manager** dispatches here, and queues each Green
  merge for Ben as an Action: Ben runs the merges (Ben's choice,
  2026-11-12, after the manager's merge call was refused). Address it by
  app session id, `local_39e3ac7a-9d6d-4524-82e4-9b5f0e6db274`.
- **The dynasty planner** (`local_84c6f2af-95ee-4c21-9c02-95877dc0cd21`)
  plans the owner-queue mod (#111, #137, #142, #147, #148's pane part,
  #153).
- **Your own ids.** App session id
  `local_9830794b-c1e9-400a-ba66-e6abb9432396`. The queue id changes at
  every `/clear`; it was `e4ecef5c-3183-4be1-8b67-0da82c468858` before
  this clear. If no owner-queue id line shows in the system prompt, ask
  Ben to run `/owner id`.
- **The owner's queue** is dynasty's `.claude/memory/NEEDS-OWNER.md`, in
  that repo's main checkout. Read it at start. Only the manager writes it.
- **Ask Ben** with the context, then pros, cons and the recommendation,
  above the button question (root `preferences.md`).
- **A new ticket needs Ben's go before dispatch.** Ask by button, record
  the go on the ticket, relay it to the manager word for word.
- **After every merge**, the manager pulls both checkouts at closeout
  ([PROJECT-RULES.md](PROJECT-RULES.md), "Closeout pulls"). Check the
  heads by reading each checkout's `.git/refs/heads/main` before relaying.
- **Everything on GitHub resolves on GitHub** (#149, session-rules): no
  scratch, Temp or worktree path and no gitignored file in an issue, PR,
  comment, commit message or committed file. Ids are allowed as lookup
  keys. Durable private records go to Ben's private repo and mailbox;
  reusable tools become tracked code.
- **Your own PRs** (state-backs, syncs, rule lines) come from the planner
  worktree whose first branch was `t112-closeout-pulls`, on a fresh branch
  from `origin/main` once `git status` shows it clean. Enter it with
  `EnterWorktree` (path). In it, run one plain git command per call.
  Push with the branch named (`git push origin <branch>`). Commit with
  `git -c user.email=38588919+benjamininja@users.noreply.github.com commit -F <file>`.
  Run `/security-review` on the committed diff before opening the PR.
- **Run pytest with the dynasty venv** (neither tools checkout has a
  `.venv`). The full suite takes about 15 minutes; run it in the
  background. `tools/build_catalog.py` leaves a line-ending-only change to
  `CATALOG.md` here; check with `git diff --ignore-cr-at-eol` and drop it.

## Do first after this clear

1. **This state-back's PR** needs Ben's approval, by button. Read its
   comments first. Relay the approval to the manager word for word and
   post it on the PR.
2. **#152** (low, planner PR): one session-rules section on how sessions
   talk to Ben: every question through a button, and the naming rule
   (Ben/owner and Claude). Scope on #152's comments. #151 has merged, so
   nothing blocks it. Write it, `/security-review`, ask Ben to approve.
3. **#149's sweep** (follow-up on #149): template and state text that
   names local paths (the PLANNER.md and MANAGER.md templates,
   `references/parking.md`, `builder-state/` mentions in tickets).
   Ticket or planner PR; Claude's call on tier.
4. **#155** (low): needs Ben's go to dispatch. Ask by button.
5. **Rule B for #135**: t135 opens a new PR on top of #140's merge. Wait
   for its number from the manager. When it merges, the manager runs the
   held closeout pulls; then check both heads.

## What this session answers for

- Tickets, tiers, `Profile:` lines and briefs for this repository.
- Rulings on builder PRs when the manager asks ("no breach" or "plan
  breach", scope questions, design questions that aren't Ben's).
- Gaps found in the session-dispatch plugin and in this repo.
- This repo's `PROJECT-RULES.md`, and the session-rules side of #148.
- The baseball handoff doc.

**Not the owner-queue mod.** The dynasty planner plans it.

Not building, not dispatching, and never a settings file or
`.claude/dispatch.json`.

## Open PRs and in-flight work

- **#135** (reopened): #140 merged at its Rule A head (`d75b4fb`), from
  Ben's account. Ben's ruling: "Keep it; Rule B on top fast". t135 lands
  Rule B (F10 included) as a new PR, with a fresh re-check and the
  manager's hook tests. The earlier drop condition is retired.
- **PR #150** (#144, high, docs): ADR-0015 Revision 1 and the relink
  help text. Light review done; re-proof next.
- **#153** (medium, owner-queue, dynasty planner's): a tracked CLI for
  queue edits. Dispatched; its runtime question is a Decision in Ben's
  queue.
- **#154** (low): the manager's resume helper as a tracked
  session-dispatch script. Dispatched on Ben's go.
- **#155** (low): the manager's state-file prepend helper as a tracked
  script. Ticketed on Ben's word; not yet a go to dispatch.
- **#148** (owner-led): reset prompts at a clear boundary (three
  triggers), a Copy button per prompt in the pane, and an End of Day
  button. Scope on #148 (issuecomment-6824810985). The dynasty planner
  leads the design with Ben; Claude writes the session-rules side once
  the answers come.
- **#147** (medium, dynasty planner's): typed comments are written
  before Submit.
- **#137** (medium), **#142** (low), **#111**: owner-queue, the dynasty
  planner's. #137 waits on Ben's go, then #142.
- **#112**: open, tier none. Nothing is left for this session on it.

## Waiting on Ben

- Approve this state-back.
- #152's PR, once written.
- #155's go.
- #148's design questions (through the dynasty planner).
- #48's owner-led steps (below).

## Queue entries raised

- None in this session's name.

## Vendor lane and held tickets

- **Vendor lane, one ticket at a time:** #57 (medium) → #52 → #50.
  #50 is high, needs Ben's word, and carries the ADR-0006 tightening
  line (comment on #50). Then #55, once #50 has merged.
- **#47** has a lane of its own: high, needs Ben's word, and can't
  run beside #54 (both edit `README.md`).
- **Held for owner-led steps:** #48 first, then #51, #53 and #54 (they also
  need Ben's `--apply` run and junction changes). #54's builder
  checks whether `powerbi-report-cli` hands off to
  `semantic-model-authoring` (#49 comment).
- **#58** closed, not planned: `GEMINI.md` and `.agents/AGENTS.md`
  belong to Ben's Gemini session. Claude sessions don't touch them.

## Milestones

- 2026-11-07 to 2026-11-09: builder profiles (#84); session-rules rules
  for refused calls, probes, robots.txt and options (#86, #90, #92, #97);
  the planner state file and the baseball handoff (#91, #93); owner-queue
  Submit, many queues and Session lines across a clear (#100, #105,
  #107); closeout pulls (#114); git rm and git mv (#115);
  `tools/reproof.py` (#122); code review at re-proof (#123, #125).
- 2026-11-10/11: Green gains the mod test and the code review (#126); the
  export's git index (#129); the live reviewer agent (#128); the
  stage-builder sync (#130); state-backs (#127, #132); the re-proof line
  (#131).
- 2026-11-11/12: owner-queue 0.10.0 (#121 `e754faa`); `reproof.py` runs
  the mod test (#138); the handoff to 0.10.0 (#141); ADR-0011 Revision 3
  (#139); the ruleset from `origin/main` (#143 `29f77d5`).
- 2026-11-12: state-back (#145 `af86414`); the live reviewer synced with
  #143's template (#146 `33722aa`); #140 merged at Rule A (`d75b4fb`);
  everything on GitHub resolves on GitHub (#151 `5a29cd6`, part of #149).

## Gaps

- **#48:** builders are denied edits to `.claude/agents/`, so agent changes
  are owner-led planner PRs (as #128, #130 and #146 were).
- **The baseball handoff**
  ([docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md))
  is for SpunkyLlama's agent. Update it when the owner-queue version, the
  session-dispatch version, template commits or carried-over rules change.
  #151 and #152 add carried-over rules: bump it after #152.
- **`CLAUDE.md` is out of date** in two places: its CI sentence and "Three
  agents live in `.claude/agents/`". Small; no ticket yet.
- **#140 F11:** a `-C` path is final even when it can't be resolved. No
  ticket yet.
- **Reviewer drift:** if the code-review fork keeps straying, consider
  dropping it (#136, Not in scope).
- **Not yet asked:** `git merge origin/main` isn't in this repo's builder
  allow list. Offer Ben the line if a builder hits it.

## Decided since

Ben's decisions, each recorded on its ticket. Earlier ones are in git
history of this file.

- *Approve 145*, *Approve 146*, *Approve 151 at ee75490* (2026-11-12).
- #149: *Planner PR now*; scope files, paths and session ids, then
  refined to *Ids yes, local paths no*; the queue's `Session:` lines stay;
  *Private repo for all; tools tracked* (no `private/` folder).
- #152: *Ticket it, low*; *Add to #152* (the naming rule).
- #154: *Go: dispatch #154*. #155: *Ticket it, low*.
- #140: *Keep it; Rule B on top fast*. Merges: Ben runs them from the
  queue.

## Lessons

- Address sessions by app id; check the checkouts before relaying a
  manager's claim about them.
- Before asking for an approval, read the PR's comments: an approval
  given before a clear is recorded there.
- A manager that resumes may miss a relay. Re-send it with the PR comment
  link (#151's new head crossed in flight).
- **An approval covers one head.** When a later ruling changes an approved
  PR, hold it with the manager first, rework, then ask again (#151).
- **Check `origin/main` before naming a merge commit.** Two merges landed
  a minute apart; Claude credited #146's commit to #145 at first.
- **A safety hook loosened by a list of forms to catch gets bypassed one
  form at a time.** Start from an allowlist (#140, Rule B).
- **A limit text has to allow the tool the same text tells the reader to
  use** (#143 F1).
- Worktrees share branch refs; only `HEAD` is per worktree.
- `/security-review` sees only commits. Commit first.
- A script run as one Bash call hides its inner commands from the
  permission rules (#117).
- A worktree session can't `git -C` the main checkout. Read each
  checkout's `.git/refs/heads/main` instead.
