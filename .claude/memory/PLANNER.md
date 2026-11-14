# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-14, at a ninth context clear (the clear boundary
of #160). `origin/main` was at `01e2f46` (#173). Both tools checkouts were
still at `29f77d5`: the manager holds the closeout pulls until Rule B
(#159, for #135) merges.

## START HERE

- You are **Tools-central-planner**, the standing planner for
  `benjamininja/skills-plugins-hooks-agents` (since 2026-11-07). Call the
  owner **Ben** or "the owner", and yourself **Claude**, never "you" or
  "I" for either (`session-rules`, "Asking the owner").
- **Every question to Ben goes through a button**: AskUserQuestion when
  Ben is in the chat, a queue entry when not. Context, pros, cons and the
  recommendation sit above the question.
- Read the open issues with their `tier:` labels:
  `gh issue list -R benjamininja/skills-plugins-hooks-agents --state open`,
  and `gh pr list` for open PRs.
- **The dynasty builder manager** dispatches here, re-proves and merges.
  Address it by app session id,
  `local_39e3ac7a-9d6d-4524-82e4-9b5f0e6db274` (its queue id changes at
  each clear). If it seems to miss a head or a go, re-send it with the PR
  comment link.
- **Merges (since #170):** the manager merges head-pinned in one call once
  Green, on Ben's pane Approve or Ben's merge word. "Approve N" alone is an
  approval, not a merge word: on Green the manager then queues a merge
  Action. When Ben says "merge N", relay it word for word, record it on
  the PR, and the manager re-proves and merges on Green. Never skip the
  re-proof; offer it as a choice only if Ben asks to.
- **The dynasty planner** (`local_84c6f2af-95ee-4c21-9c02-95877dc0cd21`)
  plans the owner-queue mod (#111, #137, #142, #147, #161).
- **Your own ids.** App session id
  `local_9830794b-c1e9-400a-ba66-e6abb9432396`. The queue id changes at
  every `/clear`: ask Ben to run `/owner id` by button if no owner-queue
  line shows, and send the new id to the manager for re-keying.
- **The owner's queue** is dynasty's `.claude/memory/NEEDS-OWNER.md`, in
  that repo's main checkout. Read it at start. Only the manager writes it.
  A planner sends the manager a ready entry, with a command naming the
  exact file plus a check step. Its header is the template's since #166.
- **A new ticket needs Ben's go before dispatch.** Ask by button, record
  the go on the ticket, relay it to the manager word for word.
- **After every merge**, the manager pulls both checkouts at closeout
  ([PROJECT-RULES.md](PROJECT-RULES.md), "Closeout pulls"). Check the
  heads by reading each checkout's `.git/refs/heads/main` before relaying.
- **Everything on GitHub resolves on GitHub.** No scratch, Temp or
  worktree path and no gitignored file in an issue, PR, comment, commit
  message or committed file. Ids are allowed as lookup keys.
- **The clear boundary** (`session-rules`, #160): close the step, record,
  state-back PR, memory flush, reset prompt last. Until #161 builds the
  mod's store, the reset prompt goes to Ben in chat.
- **Your own PRs** come from the planner worktree whose first branch was
  `t112-closeout-pulls`, on a fresh branch from `origin/main`. Enter it
  with `EnterWorktree` (path). One plain git command per call (the
  worktree guard refuses chains and loops that name git). Push with the
  branch named. Commit with
  `git -c user.email=38588919+benjamininja@users.noreply.github.com commit -F <file>`.
  Run `/security-review` on the committed diff before opening the PR.
  When the manager asks Claude to bring a PR up to date, merge
  `origin/main` into it, check the diff against main is unchanged, push,
  and ask Ben to approve the new head.
- **Run pytest with the dynasty venv** (neither tools checkout has a
  `.venv`). `tools/build_catalog.py` leaves a line-ending-only change to
  `CATALOG.md` here; check with `git diff --ignore-cr-at-eol` and drop it.

## Do first after this clear

1. **This state-back's PR** needs Ben's approval, by button. Read its
   comments first. Relay to the manager word for word.
2. **#159 (Rule B for #135)** is at `13a0fcd`, CLEAN; the narrow re-check
   after Ben's F15 ruling found the clear path gone and no new bypass
   (PR #159, latest comments). Next: the manager's hook tests, re-proof,
   then Ben's merge. When it merges, the manager runs the held closeout
   pulls; check both heads.
3. **After the closeout pull:** #165's reviewer (no code-review fork) and
   #172's dispatch rule go live. Check the first review after it closes
   with a line on the reviewer's own calls and runs no fork.
4. **#168** (high, narrowed to F5's is-it-git gate plus README limits;
   #168 issuecomment-6835504448) dispatches after #159 merges, at Ben's
   go (recorded on #168). Its builder posts a fail-closed design on #168;
   put it to Ben by button before the build.
5. **#167** (medium): Ben's go is recorded; the manager dispatches it. Its
   builder reports the smallest fix on #167 before it builds.
6. **Ben's GitHub ruleset** on `main` in both repos (require a PR, block
   force pushes and deletion) is a queue Action from the manager (#135
   ruling). Once in, #168's README names it as the first layer.

## What this session answers for

- Tickets, tiers, `Profile:` lines and briefs for this repository.
- Rulings on builder PRs when the manager asks ("no breach" or "plan
  breach", scope questions, design questions that aren't Ben's).
- Gaps found in the session-dispatch plugin and in this repo.
- This repo's `PROJECT-RULES.md`, and the session-rules side of #148.
- The baseball handoff doc.

**Not the owner-queue mod.** The dynasty planner plans it, including #161.

Not building, not dispatching, and never a settings file or
`.claude/dispatch.json`.

## Open PRs and in-flight work

- **PR #159** (#135, Rule B): `13a0fcd`, re-check clean; re-proof and
  merge next.
- **#168** (high) and **#167** (medium): gos recorded; see Do first.
- **#161** (high, the dynasty planner's): the mod side of #148.
- **#147** (medium), **#137** (medium), **#142** (low), **#111**:
  owner-queue, the dynasty planner's.
- **#148** and **#112**: open, tier none. #148's session-rules side
  merged (#160); its mod side is #161. Nothing is left for this session
  on #112 once the first closeout pull runs.
- **#164**: open, tier low; PR #165 (merged) carried it. Close it after
  the closeout pull, when the first review shows no fork.

## Waiting on Ben

- Approve this state-back.
- #159's merge, when Green.
- The GitHub ruleset Action (#135).
- Dynasty PR #531 (ADR-0001 amendment, ~255K ceiling).
- #168's design, when its builder posts it.
- #48's owner-led steps (below).

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
- **`GEMINI.md` and `.agents/`** belong to Ben's Gemini session (#58,
  closed). Claude sessions don't touch them.

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
  (#131); owner-queue 0.10.0 (#121); ADR-0011 Revision 3 (#139); the
  ruleset from `origin/main` (#143 `29f77d5`).
- 2026-11-12: state-backs (#145, #156, #169 `8548410`); #140 at Rule A;
  everything on GitHub resolves on GitHub (#151); ADR-0015 Revision 1
  (#150); the resume helper (#157); questions by button (#158
  `f2f9061`); `prepend_state.py` (#162 `15ec7ee`); the clear boundary
  (#160 `ec523e6`); no code-review fork (#165 `42e11f3`); the `Answer:`
  line (#166 `7131c29`); the queue CLI, owner-queue 0.11.0 (#163
  `3be0767`); no workflow dispatch (#172 `1bbf198`); the baseball handoff
  (#173 `01e2f46`); the head-pinned merge rule (#170, closed 2026-11-14).

## Gaps

- **#48:** builders are denied edits to `.claude/agents/`, so agent changes
  are owner-led planner PRs.
- **The baseball handoff**
  ([docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md))
  is current at `01e2f46`. Bump it when the owner-queue version, the
  session-dispatch rules, template commits or carried-over rules change.
- **`CLAUDE.md` is out of date** in two places: its CI sentence and "Three
  agents live in `.claude/agents/`". Small; no ticket yet.
- **#140 F11:** a `-C` path is final even when it can't be resolved. No
  ticket yet.
- **The plugin's settings templates** still deny only
  `Bash(gh workflow run*)`; #172's rule covers the other routes in text.
  A template change is Ben's (settings files).

## Decided since the last state-back

Ben's decisions, each recorded on its ticket or PR. Earlier ones are in
git history of this file.

- *Approve 169*; *Run /owner id now*.
- #170: *Add the rule* (head-pinned merge allow rule; Ben added it).
- #171: *(a) General, session-rules*; *Approve 172*; *merge 172*.
- Handoff: *Once, after #172*; *Approve 173*; *Merge 173 on Green*.
- *merge 166 and 163*, then *(a) Manager re-proves, then merges*.
- Queue header: *Replace whole* (on #166).
- #135 (in the manager's chat): *Keep #135; t135 fixes F10/F11*; *Keep
  #135; t135 drops d*; *Remove clear path + server rule*.

## Lessons

- Address sessions by app id; check the checkouts before relaying a
  manager's claim about them.
- Before asking for an approval, read the PR's comments: an approval
  given before a clear is recorded there.
- A manager that resumes may miss a relay. Re-send it with the PR comment
  link.
- **An approval covers one head.** A merge of `origin/main` or a later
  ruling makes a new head; ask Ben again.
- **"Approve" is not "merge".** Ask whether the manager may merge on
  Green when Ben approves a planner PR, or relay his merge word.
- **A merge stalled on an allow rule that didn't match the command
  actually run** (`--match-head-commit` after `--delete-branch`). Read
  the exact rule against the exact command before blaming the classifier.
- **Check `origin/main` before naming a merge commit.**
- **A safety hook loosened by a list of forms to catch gets bypassed one
  form at a time.** Start from an allowlist, and put the hard stop on the
  server (#140, #159, #168).
- **A limit text has to read right to the tool it is handed** (#143, #164).
- **`gh issue create --label` can leave a ticket unlabelled.** Check the
  labels after filing.
- **Check a claim about a file before relaying it.**
- Worktrees share branch refs; only `HEAD` is per worktree.
- `/security-review` sees only commits. Commit first.
- A script run as one Bash call hides its inner commands from the
  permission rules (#117).
- A worktree session can't `git -C` the main checkout. Read each
  checkout's `.git/refs/heads/main` instead.
