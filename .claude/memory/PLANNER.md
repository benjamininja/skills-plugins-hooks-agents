# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-14, at an eleventh context clear. `origin/main` and
both tools checkouts were at `189a2a5` (#159). The hold on the closeout
pulls is lifted.

## START HERE

- You are **Tools-central-planner**, the standing planner for
  `benjamininja/skills-plugins-hooks-agents` (since 2026-11-07). Call the
  owner **Ben** or "the owner", and yourself **Claude**, never "you" or
  "I" for either.
- **Every question to Ben goes through a button**: AskUserQuestion when
  Ben is in the chat, a queue entry when not. Context, pros, cons and the
  recommendation sit above the question.
- **Button or queue, never prose** (Ben, 2026-11-14). A ready item gets a
  button in that same turn. Anything still open when a turn ends goes to
  the manager as a ready queue entry. An item Ben cannot act on yet is
  listed as "coming later", never as "waiting on Ben".
- **Second look, then a SWOT** (Ben, 2026-11-14, twice). Before the first
  design question, check the answer against long-term best practice: one
  source of truth, the rule changes before it is used, risk as likelihood
  times impact. Once a plan is agreed, run a self-critical SWOT, reconcile,
  and only then present and file it.
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
  plans the owner-queue mod (#111, #137, #142, #147, #161, #179, #185,
  #188).
- **Your own ids.** App session id
  `local_9830794b-c1e9-400a-ba66-e6abb9432396`. The queue id changes at
  every `/clear`: ask Ben by button to run `/owner id` if no owner-queue
  line shows, and send the new id to the manager.
- **The owner's queues.** Until PR #184 merges, tools entries go to
  dynasty's `.claude/memory/NEEDS-OWNER.md`, in that repo's main checkout.
  The tools queue exists, empty and untracked, at the same path in this
  repo's main checkout, and Ben's `queues` setting lists both (#183). The
  dynasty manager writes both; a planner sends it a ready entry.
- **A new ticket needs Ben's go before dispatch.** Ask by button, record
  the go on the ticket, relay it to the manager word for word.
- **After every merge**, the manager pulls both checkouts at closeout.
  Check the heads by reading each checkout's `.git/refs/heads/main`.
- **Everything on GitHub resolves on GitHub.** No scratch, Temp or
  worktree path and no gitignored file in an issue, PR, comment, commit
  message or committed file. Ids are allowed as lookup keys.
- **The clear boundary** (`session-rules`): close the step, record,
  state-back PR, memory flush, reset prompt last. Until #161's PR #197
  merges and is live, the reset prompt goes to Ben in chat.
- **Your own PRs** come from the planner worktree whose first branch was
  `t112-closeout-pulls`, on a fresh branch from `origin/main`, or stacked
  on an open PR's branch when both edit the same lines. Enter it with
  `EnterWorktree` (path). One plain git command per call, never a `cd`
  that stays. Push with the branch named. Commit with
  `git -c user.email=38588919+benjamininja@users.noreply.github.com commit -F <file>`.
  Run `/security-review` on the committed diff before opening the PR.
- **Run pytest with the dynasty venv**, in the background: a full run
  takes about 20 minutes. Skip it for a text-only change while the manager
  needs a quiet machine, and say so on the PR. `tools/build_catalog.py`
  leaves a line-ending-only change to `CATALOG.md`; check with
  `git diff --ignore-cr-at-eol` and drop it.

## Do first after this clear

1. **This state-back** is its own PR, stacked on #181's branch. After
   #181 merges, merge `origin/main` in, keep this branch's `PLANNER.md`,
   push, read its comments, and ask Ben by button to approve and give a
   merge word.
2. **Tier the four tickets** the dynasty planner filed `Tier: unset` on
   Ben's ruling: #190 (threat-model ADR), #191 (a least-privilege GitHub
   credential for builders), #192 (a settings and profile linter in CI),
   #193 (server-side rulesets on every branch). Read each, do the second
   look, set the `Tier:` line and label, then ask Ben for each go by
   button. #190 comes first: the others hang off it.
3. **PR #184** (#183's rule text and ADR-0016, at `9b75719`) is stacked on
   #180. When #180 merges, merge `origin/main` in, push, and ask Ben to
   approve and whether the manager may merge on Green. Its merge is the
   switch: from then, tools entries go to the tools queue.
4. **#164** closes when the first code review run with the pulled
   reviewer shows no code-review fork and ends with a line on the
   reviewer's own calls. The manager was asked for that review's link.
5. **#168** (high): Ben's go is recorded
   (issuecomment-6829480746); the manager was asked to add its dispatch.
   Its fail-closed design goes to Ben by button before the build.
6. **#195**: the manager was sent a ready Action for Ben (point the
   user-level plugin variable at the live clone). Check that it is in the
   queue. When Ben marks it done, record the pane's version on #195, then
   propose the README line that names one source for the plugin folders.
7. **The manager's tools line**, one Green at a time: #177, #180, #181,
   #194, #182 (#175), #196 (#179), #197 (#161). Dispatches, in order, on
   Ben's recorded gos: #186, then #167, #189, #187 (#186 and #167 both
   edit `tools/reproof.py`); #168; #176 after #177, the pull and #50.
8. **#50** grows to `teach` and `grill-with-docs` and runs first in the
   vendor lane once #177 merges (comment on #50).

## What this session answers for

- Tickets, tiers, `Profile:` lines and briefs for this repository.
- Rulings on builder PRs when the manager asks, and on the findings that
  #186's, #189's and #187's builders post before they change code.
- Gaps found in the session-dispatch plugin and in this repo.
- This repo's `PROJECT-RULES.md` and the session-rules text (#148, #178,
  #183, PR #194).
- The baseball handoff doc.

**Not the owner-queue mod.** The dynasty planner plans it.

Not building, not dispatching, and never a settings file or
`.claude/dispatch.json`.

## Open PRs and in-flight work

- **Planner PRs:** #180 (#178, approved, merge on Green at `86a45e3`);
  #181 (approved, merge on Green at `148c9d1`); #184 (#183, stacked on
  #180, not yet approved); #194 (ticket-text authors, approved, merge on
  Green at `8b66806`, issuecomment-6885042241); this state-back.
- **Builder PRs:** #177 (#48, approved with a merge word); #182 (#175);
  #196 (#179) and #197 (#161), the dynasty planner's.
- **Gos recorded, not yet dispatched:** #186 (low), #167 (medium), #189
  (medium), #187 (medium), #168 (high), #176 (medium).
- **Owner-led:** #183 (open for PR #184, #185 and dynasty #562); #195.
- **`Tier: unset`, to tier:** #190, #191, #192, #193. #188 is the dynasty
  planner's to tier.
- **#148**, **#112**: open, tier none. **#164**: see Do first, item 4.

## Queue entries raised

- *Point the plugin folder variable at the live clone (owner-queue 0.7.2
  is loading)*, #195, `Session: f62a060b-a79a-4e55-ad82-7e18265f2117`.
  Sent to the manager as a ready entry; not yet seen in the queue at this
  state-back.

## Waiting on Ben

Each has a queue entry or was asked by button; nothing here is prose only.

- The #195 Action, once the manager has written it.

## Coming to Ben later

- Approval of this state-back, after #181 merges.
- Approval of PR #184, after #180 merges.
- Gos on #190 to #193, once they are tiered.
- #168's design, when its builder posts it.
- The three questions on #185 (project key, stable ids, heading name):
  the dynasty planner brings them.

## Vendor lane and held tickets

- **Vendor lane, one ticket at a time:** #50 first once #177 merges
  (`teach` and `grill-with-docs` back to manual), then #176's sweep, then
  #57 → #52. #50 needs the `--bless` allow rule or the manager's run. Then
  #55.
- **#47** has a lane of its own: high, needs Ben's word, and can't run
  beside #54 (both edit `README.md`).
- **#48 is in PR #177.** After it merges: #51, #53 and #54 (they also
  need Ben's `--apply` run and junction changes).
- **`GEMINI.md` and `.agents/`** belong to Ben's Gemini session. Claude
  sessions don't touch them.

## Milestones

- 2026-11-07 to 2026-11-12: see git history of this file.
- 2026-11-14, morning: Ben's GitHub rulesets on `main` in both repos;
  #174, #159, #177 approved with merge words; #48 built as PR #177;
  tickets #175, #176, #178, #179 filed.
- 2026-11-14, afternoon: #174 and #159 merged and both checkouts pulled
  to `189a2a5`; the multi-repo owner queue grilled and filed (#183,
  ADR-0016 in PR #184), the tools queue set up; #186, #187, #189 and #195
  filed; PR #194 opened for the draft advisory GHSA-27j5-qx96-v8w3.

## Gaps

- **The baseball handoff**
  ([docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md))
  is current at `01e2f46`. Bump it after #178, #177, #184 and #194 merge
  (parking, the auditor, the queue per project and the author rule
  changed).
- **`CLAUDE.md`'s CI sentence** is out of date. The agents line is fixed
  in #177.
- **#140 F11:** a `-C` path is final even when it can't be resolved. No
  ticket yet.
- **The draft advisory's other fixes** are settings and script changes:
  Ben's hands and the dynasty planner's tickets. Its detail stays out of
  public tickets until it is published (at the fixes, or on 2026-11-28).
- **The re-key text** in `parking.md` and the queue template still makes
  a session send its new id by hand. It stays until the mod change in
  #188 finding 1 is live; reword it with that change.
- **A script-side check of a ticket line's author** would back PR #194's
  rule with code. Raise it under #190.

## Decided since the last state-back

Ben's decisions, each recorded on its ticket or PR.

- *Approve, merge on Green* (#180, #181, #194).
- *go on 175 and 176*.
- #183 grill: *In repo, untracked*; *Ticket's repo, full link*; *Fixed
  order, per-project numbers*; *Dynasty manager, via CLI*; *Short ADR*;
  *Confirmed, go*; after the SWOT, *Set up now, entries later* and *Own
  ticket, owner-attended*.
- *Go, ahead of #167* (#186); *File it, medium* then *Go, after #189*
  (#187); *Go, after #186* (#189).
- *All ticket text* (PR #194's scope).
- *Button or queue, never prose*; *Claude finds out first* (#195).

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
- **A step called small may hide the hazard.** Untracking a live,
  modified tracked file: the pull refuses or deletes it (#183, dynasty
  #562).
- **A chat list of what waits on Ben is not a queue.** Button or queue
  (2026-11-14).
- **Check what version actually runs** before reasoning from the
  repository: the pane was a 0.7.2 hand copy (#195).
- **On a public repo, check who wrote a ticket's text** (PR #194).
- Worktrees share branch refs; only `HEAD` is per worktree.
- `/security-review` sees only commits. Commit first.
- A worktree session can't `git -C` the main checkout. Read each
  checkout's `.git/refs/heads/main` instead.
