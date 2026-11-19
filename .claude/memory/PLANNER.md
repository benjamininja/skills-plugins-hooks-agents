# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-14, at a tenth context clear. `origin/main` was at
`01e2f46` (#173). Both tools checkouts were still at `29f77d5`: the manager
holds the closeout pulls until Rule B (#159, for #135) merges.

## START HERE

- You are **Tools-central-planner**, the standing planner for
  `benjamininja/skills-plugins-hooks-agents` (since 2026-11-07). Call the
  owner **Ben** or "the owner", and yourself **Claude**, never "you" or
  "I" for either.
- **Every question to Ben goes through a button**: AskUserQuestion when
  Ben is in the chat, a queue entry when not. Context, pros, cons and the
  recommendation sit above the question.
- Read the open issues with their `tier:` labels:
  `gh issue list -R benjamininja/skills-plugins-hooks-agents --state open`,
  and `gh pr list` for open PRs.
- **The dynasty builder manager** dispatches here, re-proves and merges.
  Address it by app session id,
  `local_39e3ac7a-9d6d-4524-82e4-9b5f0e6db274`. Its queue id changes at
  each clear. If it seems to miss a head or a go, re-send it with the PR
  comment link.
- **Merges (since #170):** the manager merges head-pinned in one call once
  Green, on Ben's pane Approve or his merge word. "Approve N" alone is an
  approval, not a merge word: ask Ben whether the manager may merge on
  Green. Relay his words word for word, record them on the PR.
- **The dynasty planner** (`local_84c6f2af-95ee-4c21-9c02-95877dc0cd21`)
  plans the owner-queue mod (#111, #137, #142, #147, #161, #179).
- **Your own ids.** App session id
  `local_9830794b-c1e9-400a-ba66-e6abb9432396`. The queue id changes at
  every `/clear`: ask Ben by button to run `/owner id` if no owner-queue
  line shows, and send the new id to the manager. Under #178, entries
  this planner raises name the planner itself.
- **The owner's queue** is dynasty's `.claude/memory/NEEDS-OWNER.md`, in
  that repo's main checkout. Only the manager writes it; a planner sends
  it a ready entry.
- **A new ticket needs Ben's go before dispatch.** Ask by button, record
  the go on the ticket, relay it to the manager word for word.
- **After every merge**, the manager pulls both checkouts at closeout.
  Check the heads by reading each checkout's `.git/refs/heads/main`.
- **Everything on GitHub resolves on GitHub.** No scratch, Temp or
  worktree path and no gitignored file in an issue, PR, comment, commit
  message or committed file. Ids are allowed as lookup keys.
- **The clear boundary** (`session-rules`): close the step, record,
  state-back PR, memory flush, reset prompt last. Until #161 builds the
  mod's store, the reset prompt goes to Ben in chat.
- **Your own PRs** come from the planner worktree whose first branch was
  `t112-closeout-pulls`, on a fresh branch from `origin/main`. Enter it
  with `EnterWorktree` (path). One plain git command per call. Push with
  the branch named. Commit with
  `git -c user.email=38588919+benjamininja@users.noreply.github.com commit -F <file>`.
  Run `/security-review` on the committed diff before opening the PR.
- **Run pytest with the dynasty venv**, in the background: a full run
  takes about 19 minutes. `tools/build_catalog.py` leaves a
  line-ending-only change to `CATALOG.md`; check with
  `git diff --ignore-cr-at-eol` and drop it.

## Do first after this clear

1. **This state-back** is its own PR, stacked on #174's branch, so #174
   merges as approved at `5ea612b` (its re-proof is GREEN; the manager
   merges it next). After #174 merges, merge `origin/main` into this
   branch, keep this branch's `PLANNER.md`, push, and ask Ben by button
   to approve and give a merge word. Read its comments first.
2. **The manager's line**, one Green at a time: #174, #159 (Ben's merge
   word recorded, issuecomment-6880389251), #161's dispatch, then #177
   (Ben: *Approve, merge on Green*, issuecomment-6881756914), then PR
   #180 (#178) once Ben approves it. #159's re-proof was NOT GREEN only on
   the 1800s pytest timeout; the manager re-runs it on a quiet machine.
   The manager edits the queue by hand until owner-queue 0.11.0 is live,
   reading each entry whole first (#178).
3. **When #159 merges**, the manager runs the held closeout pulls. Check
   both heads. Then: the first review runs no code-review fork and closes
   with a line on the reviewer's own calls; close #164. #168 dispatches
   (Ben's go recorded); its fail-closed design goes to Ben by button
   before the build.
4. **#161** (high): Ben's go recorded (issuecomment-6880538296), plus two
   requirements from the #178 grill (issuecomment-6881790327). The manager
   dispatches it; the dynasty planner rules on its first-step finding.
   When the finding posts on #161, send its comment link to the dynasty
   planner (it asked, 2026-11-14).
5. **PR #180** (#178, session-rules: the Session line names the session that
   acts on the answer): ask Ben to approve and whether the manager may
   merge on Green. The manager reports on #178 when its local prune
   script is retired and the dynasty queue header matches the template.
6. **#50** grows to `teach` and `grill-with-docs` and runs first in the
   vendor lane once #177 merges (comment on #50). Then **#176** (sweep,
   `domain-modeling` first) at Ben's go.
7. **#167** (medium): Ben's go is recorded; the manager dispatches it.
   **#175** (low) needs Ben's go; its template line is Ben's to apply.

## What this session answers for

- Tickets, tiers, `Profile:` lines and briefs for this repository.
- Rulings on builder PRs when the manager asks.
- Gaps found in the session-dispatch plugin and in this repo.
- This repo's `PROJECT-RULES.md`, the session-rules text (#148, #178).
- The baseball handoff doc.

**Not the owner-queue mod.** The dynasty planner plans it.

Not building, not dispatching, and never a settings file or
`.claude/dispatch.json`.

## Open PRs and in-flight work

- **PR #174**: re-proof GREEN, merge next; this state-back is stacked on it. **PR #159** (#135): re-proof pending.
- **PR #177** (#48): auditor input, whole-folder read, ADR-0006
  Revision 1. Approved with a merge word.
- **PR #180** (#178): opened at this clear; awaiting Ben's approval.
- **#161** (high), **#168** (high), **#167** (medium): gos recorded.
- **#175** (low), **#176** (medium), **#179** (low, dynasty planner's):
  filed 2026-11-14, need Ben's go.
- **#147**, **#137**, **#142**, **#111**: owner-queue, the dynasty
  planner's.
- **#148**, **#112**: open, tier none. **#164**: close after the first
  closeout pull shows no fork.

## Waiting on Ben

- Approve this state-back's PR (after #174 merges and it is brought up to date).
- Approve PR #180 (#178), and whether the manager may merge it on Green.
- Gos on #175, #176 (and #179 via the dynasty planner).
- #168's design, when its builder posts it.

## Vendor lane and held tickets

- **Vendor lane, one ticket at a time:** #50 first once #177 merges
  (`teach` and `grill-with-docs` back to manual), then #57 → #52. #50
  needs the `--bless` allow rule or the manager's run. Then #55.
- **#47** has a lane of its own: high, needs Ben's word, and can't run
  beside #54 (both edit `README.md`).
- **#48 is in PR #177.** After it merges: #51, #53 and #54 (they also
  need Ben's `--apply` run and junction changes).
- **`GEMINI.md` and `.agents/`** belong to Ben's Gemini session. Claude
  sessions don't touch them.

## Milestones

- 2026-11-07 to 2026-11-12: see git history of this file.
- 2026-11-14: Ben's GitHub rulesets on `main` in both repos (recorded on
  #135, issuecomment-6880318944); dynasty #531 merged; #174, #159, #177
  approved with merge words; #48 built as PR #177; tickets #175, #176,
  #178, #179 filed; the #526 queue-routing grill (#178).

## Gaps

- **The baseball handoff**
  ([docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md))
  is current at `01e2f46`. Bump it after #178 and #177 merge (parking
  rule and auditor changed).
- **`CLAUDE.md`'s CI sentence** is out of date. The agents line is fixed
  in #177.
- **#140 F11:** a `-C` path is final even when it can't be resolved. No
  ticket yet.
- **Re-proof refusals:** #175 holds the long-term fix.
- **A sweep of all model-invocable skills** is #176.

## Decided since the last state-back

Ben's decisions, each recorded on its ticket or PR.

- *Approve 174*, *Merge 174 on Green* (at `5ea612b`).
- *approved to merge 159 once green*.
- *File it, low tier* (#175).
- #48: *Start #48 now*; *Approve plan*; *Fix it here*; *Revise it in
  #48*; *Impact and trigger*; *The five ADR-0006 skills*; *Accept:
  manual*; *Grow #50, first in lane*; *Sweep ticket, it first* (#176).
- *Go on #161*.
- #178 grill: *Who acts: manager*; *Add to #161*; *All three*; *Add the
  line*; *Three pieces*; *No glossary entry*; *Confirmed, go*.
- *Approve, merge on Green* (#177).

## Lessons

- Address sessions by app id; check the checkouts before relaying a
  manager's claim about them.
- Before asking for an approval, read the PR's comments.
- **An approval covers one head.**
- **"Approve" is not "merge".**
- **Check `origin/main` before naming a merge commit.**
- **Start a safety rule from an allowlist; put the hard stop on the
  server** (#140, #159, #168; the rulesets are now in).
- **A rule that rates only impact misses likelihood.** ADR-0006
  Revision 1 rates trigger breadth too (#48).
- **A queue entry's Session line must name a session that will wake**
  (#178).
- **An allow rule must match the command actually run**; a chained line
  never matches one rule (#175).
- Worktrees share branch refs; only `HEAD` is per worktree.
- `/security-review` sees only commits. Commit first.
- A worktree session can't `git -C` the main checkout. Read each
  checkout's `.git/refs/heads/main` instead.
