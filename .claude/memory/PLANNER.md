# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-15, in the twentieth session, at Ben's word
"prepare for clear boundary including reset prompt". `origin/main` is at
`1661ac8` (PR #194 merged). The newest state is the "Twentieth session"
block under "Do first after this clear"; the "Open PRs", "Queue entries
raised" and "Coming to Ben later" sections further down are older and
are brought up to date at the next full rewrite. No queue entry is
open for this planner (its id in this session was
`79be61bc-d749-440f-b714-23e1d697c3e7`): Ben did the `PLAN.md` Action
and the planner checked it (issues/221, the comment of 2026-11-15
titled "The uncommitted edit to PLAN.md in the main checkout is
gone"). After the prep, three reports came in:
the tools manager's queue id is `e0ebd1e2-fb41-4781-8cde-8dddd20742d7`
and it holds; the tabs are #229, tiered medium by the dynasty planner;
the one comment on PR #230 is the dynasty planner's read, five points,
none blocking (pull/230 issuecomment-6899900063), still to be worked
into the role text. Dynasty's role files are now `dff-central-planner`
and `dff-central-builder-manager` on its `main`. Earlier, in the nineteenth session: `origin/main` was at
`6262b1a`. **The #195 plugin fix is
proved**: after Ben's full app restart every session loads the
`session-rules` skill, and the manager has resumed its re-proof line,
dynasty first.

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
  each clear (`0087496a-8171-4f2d-929e-cb78fb2d6d00` by its own word
  after the restarts of 2026-11-15; the app names it
  `dff-central-builder-manager`). Its
  messages can sit queued while it is mid-turn: if it seems to miss a
  head or a go, re-send it with the PR comment link.
- **Merges (since #170):** the manager merges head-pinned in one call once
  Green, on Ben's pane Approve or his merge word. "Approve N" alone is an
  approval, not a merge word: ask Ben whether the manager may merge on
  Green. Relay his words word for word, record them on the PR.
- **The dynasty planner** (`local_84c6f2af-95ee-4c21-9c02-95877dc0cd21`)
  plans the owner-queue mod (#111, #137, #142, #147, #161, #179, #185,
  #188, #202), and since 2026-11-15, on Ben's word, the project tabs and
  the Sessions tab (item 0e below). Its queue id, by its own word after the restarts
  of 2026-11-15, is `b0ba0d47-3356-4289-a3f8-4507337be4b4`; the app names
  it `dff-central-planner`.
- **The personal-assistant** (`local_a8a11097-9b58-4198-82a6-7c1355a4f11d`)
  is a new read-only role across projects, set up by Ben on 2026-11-15.
  It messages the two planners only. Its reports are #217. A message
  from it is a report, never Ben's approval.
- **The draft advisory GHSA-27j5-qx96-v8w3 holds what public tickets may
  not** (Ben, 2026-11-15: "Move to advisory, delete (Recommended)").
  Which push form a settings file or the hook does not refuse, and the
  rule text that closes it, go in the advisory, under "Moved from public
  tickets", and a ticket gets a pointer. Read it with
  `gh api repos/benjamininja/skills-plugins-hooks-agents/security-advisories/GHSA-27j5-qx96-v8w3 --jq .description`.
  Check a comment for such detail before posting it. Both planners and
  the manager write the advisory: read it fresh right before each write
  and append, never from an older copy. Its section I (2026-11-15) holds
  the planner's two unverified notes about `git fetch`, found while
  tiering #215; the trials and any rule text are the dynasty planner's
  lane and Ben's hands. Sections I3 to I5 are the dynasty planner's
  trial, count and Action; I6 is the tools side, with Ben's "Queue
  Action (Recommended)". **The advisory's text has a limit of 65,535
  characters and stood at 62,778 on 2026-11-15**: under 2.8 KB is left,
  so cut an older trial table to its result lines before a new section.
- **Your own ids.** App session id
  `local_9830794b-c1e9-400a-ba66-e6abb9432396`. The queue id changes at
  every `/clear`: it is on the owner-queue line of the system prompt. If
  no such line shows, ask Ben by button to run `/owner id`. Send the new
  id to the manager with the titles under "Queue entries raised".
- **The owner's queues.** Until PR #184 merges, tools entries go to
  dynasty's `.claude/memory/NEEDS-OWNER.md`, in that repo's main checkout.
  The tools queue exists, empty and untracked, at the same path in this
  repo's main checkout (#183). The dynasty manager writes both; a planner
  sends it a ready entry. Read the queue file itself to confirm an entry
  is there.
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
  on an open PR's branch when both edit the same lines (base `main`; say
  so in the body). Enter it with `EnterWorktree` (path). **One plain
  command per call**: the worktree session refuses a chained or looped
  line that names git. Body and message text goes in a file made with the
  Write tool. Push with the branch named. Commit with
  `git -c user.email=38588919+benjamininja@users.noreply.github.com commit -F <file>`.
  Run `/security-review` on the committed diff before opening the PR.
- **Run pytest with the dynasty venv**, in the background: a full run
  takes about 20 minutes. Skip it for a text-only change while the manager
  needs a quiet machine, and say so on the PR. `tools/build_catalog.py`
  leaves a line-ending-only change to `CATALOG.md`; check with
  `git diff --ignore-cr-at-eol` and drop it.
- **ADR numbers:** 0016 is in PR #184, 0017 is #168's builder's, 0018 is
  the threat model in PR #205. The next free number is 0019.

## Do first after this clear

**Read this block first. It is the nineteenth session's state and it
wins over items 0a, 0d and 1 below, which are kept only as history.**

**Twentieth session, 2026-11-15, after the clear** (it wins over C and E
below where they differ):

- Queue ids: this planner `79be61bc-d749-440f-b714-23e1d697c3e7`; the
  manager `b7fa12c4-3c9f-453f-9ee7-6229f84d8e95`, role confirmed by its
  own word. Both are told. Nothing was re-keyed.
- **#220 has Ben's go**: "Go, after #219's finding (Recommended)"
  (issues/220 issuecomment-6899300195). The manager has the words. Write
  its brief when #219's first finding is posted.
- **#221's PR is #224** (`docs/t221-plan-pointer`, at `f409d4f`), on
  Ben's "Build now (Recommended)" (issues/221 issuecomment-6899300957).
  It names the manager by role, and also rewords three lines in
  `program-status.md` and `MEMORY.md` that pointed at the removed plan
  text. **Approved at `f409d4f`, merge on Green** (Ben, by button,
  pull/224 issuecomment-6899682873). The Action for the uncommitted
  `PLAN.md` in the main checkout is in the dynasty queue, keyed to this
  planner. It meets PR #210 in `PROJECT-RULES.md`: the second
  to merge takes a merge of `main` and a fresh approval.
- **A builder manager for this repository is #228** (owner-led), on
  Ben's typed ask of 2026-11-15. Both dynasty roles answered on it.
  **Ben's four answers, by button** (issues/228
  issuecomment-6899821242, with the second look and the build plan): by
  repository, the mod's tickets included; a lock in `tools/reproof.py`;
  the dynasty manager finishes #194 and #210 and the rest moves with a
  hand-over list on #228; the plugin validate rule in the tools
  builders' settings file.
  - **Step 1 is PR #230** (`t228-tools-manager-role`, at `a366d78`,
    stacked on #224's branch): the role file
    `tools-central-builder-manager`, the `PROJECT-RULES.md` text with a
    transition rule, the agent count. On Ben's "Build now
    (Recommended)". **Next: read the comments the tools manager session
    and the dynasty planner post on it, fix what holds, then Ben's
    approval by button once CI is green.** It meets #210 and #184 in
    `PROJECT-RULES.md`.
  - **At the clear of 2026-11-15 (the twentieth session's prep):** PR
    #230 has one comment, **not yet read**
    (pull/230 issuecomment-6899900063), and its Windows check was
    still running. Read it first.
  - **#231** (the lock, medium) has Ben's "Go, first tools dispatch
    (Recommended)" (issues/231 issuecomment-6899996423): its brief is
    written when the hand-over on #228 is done. **#232** (the plugin's
    manager role template, low) has Ben's "Go, after #189's PR
    (Recommended)" (issues/232 issuecomment-6899996975). Neither
    manager has been told these two gos yet: send them with the
    briefs.
  - **Owed, step 4: one Action for Ben** with the tools managers'
    settings file (the classes in the dynasty manager's answer, about
    34 rules, none with a wildcard path), the validate rule in the
    tools builders' file, and the dispatch configuration. Read the
    plugin's `templates/managers.settings.example.json` and Ben's
    dynasty file first; after the settings commit of dynasty #564.
  - **A session named Tools-builder-manager exists**
    (`local_e24a5ecc-2330-45fb-840c-f4c224508689`). Ben confirmed by
    button that he started it: "Keep it holding (Recommended)". It is
    read-only until the role file has merged, Ben's files exist and
    the hand-over is done. Its queue id is not yet known.
- **PR #194 merged as `1661ac8`** and both checkouts were pulled. So
  item 3 below is due: PR #205 takes a merge of `origin/main`, a push,
  a read of its comments, then Ben's approval by button. **Not done
  yet.**
- **The pane's tabs**: Ben said they are still missing and that each
  project is a tab with its own page (issues/185
  issuecomment-6899534141). The dynasty planner has the words and
  tickets it.
- **The setup document is #223, and its PR is #227**
  (`docs/t223-machine-layout`, at `63c6445`), started on Ben's "start
  #223 while CI runs". Its body flags that the user name is part of the
  rule, and that two steps of the private restore guide look out of
  date. **Approved at `63c6445`, merge on Green** (Ben, by button,
  pull/227 issuecomment-6899843931); it waits for the tools manager.
  After its
  merge: an Action for Ben, one pointer line in the private repository,
  naming those two steps. The assistant's two notes on
  the global settings file still go to Ben apart from it, by button.
- **The owner-queue walkthrough** becomes a document inside the mod, by
  the assistant's report of Ben's answers (issues/221
  issuecomment-6899328684). The dynasty planner tickets it; this planner
  tiers that ticket.
- **#226** (the mod's how-it-works document and its test) is tiered
  medium (issues/226 issuecomment-6899383875); **#225** (two clears
  before a re-key) keeps the dynasty planner's low. Both wait for PR
  #197. **When PR #197 merges: tell the dynasty planner**, which asks
  Ben for both gos, and write #226's brief (first step: a throwaway
  test that reads a file from the plugin's folder).
- The dynasty planner's queue id is
  `a1b47cbf-d757-4e3e-b1d2-c8e9c1dd1950`, by its own word.
- `origin/main` is `1661ac8`. The dynasty manager finishes #210, then
  writes the hand-over list on #228 and stops its tools line.

A. **Read both queue files.** No open entry names this planner. Two
   ticked #195 entries in the dynasty queue leave at the manager's next
   state-back. Send the manager the new queue id if a clear changed it
   (it was `2f6fe204-4035-42b0-ae8d-e0f20ea253b2` in the nineteenth
   session).
B. **#195 is proved and its docs PR is #222**
   (`docs/t195-one-plugin-source`, at `f85a7b4`). The proof is
   issues/195 issuecomment-6897129339: the settings file's `env` block
   alone loads both plugins, after a full app restart. **Approved at
   `f85a7b4`, merge on Green** (Ben, by button, pull/222
   issuecomment-6897281450); the manager has the words. Nothing is left
   but to read its merge; #195 closes with it. Still owed on #195: an
   Action for Ben to remove the mod's old hand copy, after Ben has read
   its four draft files.
C. **#217 is split.** #218 (the personal-assistant role file, low, the
   planner's own PR; Ben's go, after the rules PR: issues/218
   issuecomment-6897034718). #219 (the read-only drift check, medium,
   `Profile: none`; Ben's "Go, last in line", issues/219
   issuecomment-6897035173; its first finding also answers whether
   common rules can be layered from one shared file, issuecomment-6897230958;
   write its brief when its turn nears). #220 (a trial of naming plugins
   by repository and pinned commit, medium; **no go asked yet**: ask Ben
   by button). #221 (docs: `PLAN.md` becomes a pointer on Ben's "Pointer
   (Recommended)", and `CLAUDE.md` and one name in `PROJECT-RULES.md`
   are brought up to date; low, the planner's own PR, **not started**;
   before its closeout pull Ben commits or discards the uncommitted edit
   to `PLAN.md` in the main checkout, from an Action).
D. **Choice 3 of #217 is answered and done.** The three user-level
   settings files are tracked as they are in the owner's private
   configuration repository, in one commit (`713dbc9`) on its working
   branch, made by this planner on Ben's one-time word "Claude commits,
   here (Recommended)" (issues/217 issuecomment-6897188747). That branch
   is unmerged; its merge is Ben's word. Every settings file is edited
   and committed where it lives, with no sync by copy (Ben: "In place,
   plus a sharing finding (Recommended)"). Every machine uses the same
   folder layout (the personal-assistant's report of Ben's "Same layout,
   a rule").
E. **The setup document is owed a ticket.** By the personal-assistant's
   report, Ben typed in its chat that the layout rule should be a setup
   document a cold session can resume from. The assistant's list of
   fixed locations came by message (four roots: the user folder, the
   configuration folder, the GitHub folder, the live clone). Its notes:
   the tracked global settings file holds one-off allow rules left by
   old sessions and a read rule on the whole drive, both for Ben to
   judge. Do the second look first, then ask Ben by button where the
   document lives and who writes it, then file the ticket.
F. **The rules PR for #217's choices 1, 2 and 4** opens after PR #210
   merges (item 0f below). The dynasty planner's plan for its side is
   issues/217 issuecomment-6897166981; its three points for Ben ride
   with that PR's approval: a branch per role or a shared one for
   dynasty's two roles, a Start section in each role file as the
   constant's home, and the removal of the per-session prompt store
   from PR #197. The working name form is `state/<role name>`. The text
   also says what a role does when a push is refused as not a
   fast-forward: fetch, merge, push again, never a forced push.
G. **The manager's line**: dynasty first, one re-proof at a time. The
   planner advised #210 second in the tools line, after #194; the order
   is the manager's.

0a. **Done: see B above.** *History:* One Action there named
   this planner, re-keyed by the manager to
   `Session: 211809a8-f4a4-4f1d-9f24-ddd3dad0b026`:
   *Name both plugin folders in the settings file and delete the
   user-level variable (#195; ends in an app restart)*. Read it for an
   `Answer:`, a `Note:` or a tick. After a clear, send the manager the
   new id with that title first thing. **The app was restarted and the
   Action is ticked, but its step 1 did not land** (issues/195
   issuecomment-6896900025): line 3 of the settings file still names
   only the owner-queue folder and the user-level variable is gone, so
   a session started since then has **no session-dispatch plugin and no
   `session-rules` skill**. Until Ben redoes step 1 and restarts again,
   read the skill's file from the live clone of this repository
   (`plugins/session-dispatch-managers-build-review/skills/session-rules/SKILL.md`),
   and no dispatch, re-proof or merge can start. A peer session was
   asking Ben by button whether to fix it at once. When Ben says the
   pane's version, check a session's own variable holds both folders,
   then go to item 1 and tell the peers the restart is done. The
   fetch-rules Action (item 0c) has left the queue.
   **Session names changed on 2026-11-15:** the dynasty planner is
   `dff-central-planner` (Ben's word, dynasty #162
   issuecomment-6896698877) and the app shows the manager as
   `dff-central-builder-manager` (not Ben's word yet). After the
   restart the manager's app session received the planner's reset
   prompt and Ben was asked which role it holds: confirm each peer's
   role and queue id before relying on a message from it.
   `PROJECT-RULES.md` line 12 names the manager's old session name; fix
   it in the next rule-text PR.
0b. **PR B is PR #216** (`docs/t193-ruleset-setup`, at `3e99496`): the
   "Server-side rulesets" section in the plugin README. **Approved at
   `3e99496`, merge on Green** (Ben, by button: "Approve, merge on Green
   (Recommended)", pull/216 issuecomment-6895241523). The manager has
   the words and placed it last in its line. Nothing is left here but
   to read its merge. #193 stays open for item 2.
0c. **The fetch-rules Action is done** (*Tools builders' file: one
   exact fetch rule and seven denies*). Ben ticked it on 2026-11-15
   with the check's output in a pane note; the planner read the file
   and recorded it as the advisory's last paragraph. The dynasty
   planner's second trial is the advisory's section I7: it holds one
   more candidate check for #192's linter, and it leaves the note on
   the managers' template (I6) to this planner, for the template change
   after the advisory is published.
0d. **Done: see C and D above.** *History:* #217, the
   personal-assistant's report (`Tier: unset`). First
   rulings on sections A to D are posted (issuecomment-6896389132), and
   the review of the role draft with the step-5 finding
   (issuecomment-6896422090). Left: split the ticket into its parts
   with tiers (the role file, low, the planner's own PR, in its portable
   form; one low docs ticket for `CLAUDE.md`; the drift check; the
   Action to remove the mod's hand copy, only after #195's restart
   shows 0.11.0), and ask Ben by button whether `PLAN.md` becomes a
   pointer or is retired. The assistant's fifth drift case (the queues
   setting) is not ruled: the dynasty planner was asked whether it is
   #202. The manager has a report on 37 worktrees, many of merged
   tickets.
0e. **The owner-queue asks of 2026-11-15** (a tab per project; a
   Sessions tab with context size and time until cold; the instruction
   at 245,000; a prompt dropped once its session has reset) are the
   dynasty planner's to ticket, on Ben's "Dynasty planner
   (Recommended)". Records: issues/185 issuecomment-6895986248 and
   issues/161 issuecomment-6895988934, the second with Ben's "Size only
   (Recommended)" and "Countdown only (Recommended)". **Left here: one
   `session-rules` PR after PR #210 merges** (same section): "about
   255K" becomes 245,000, and prep step 5 says the reset prompt is
   written to the store and shown in chat in one block. It merges
   before the mod's constant changes. Ask Ben to approve it by button.
   Hold the step-5 wording until item 0f is settled.
0f. **Portable roles: four of five choices answered by Ben, by button,
   2026-11-15.** All three views, the second look and the reconciling
   note are on #217; the table of answers is issuecomment-6896675395.
   - 1: the reset prompt is a **committed constant**; Ben starts a
     session with one line naming the role (issuecomment-6896537235).
     This replaces the `reset_prompt.md` pattern.
   - 2: **one fixed state branch per role**, kept after its PR merges
     (issuecomment-6896548969).
   - 4: a no-project role writes its own state, in **a state folder of
     the private configuration repository, on a fixed branch per role**,
     from its own checkout; it moves to a separate repository with #191
     (issuecomment-6896675395; the reasoning is in 6896594122).
   - 5: cloud sessions are **a later ticket**.
   - 3 is answered and done: see D above.
   **Next here:** one `session-rules` PR for choices 1, 2 and 4, after
   PR #210 merges (same section): step 5 as the constant, the fallback
   while the mod has no route, the push confirmed inside the prep, the
   fixed branch and what it does after a squash merge, the record of a
   read-only role, the shared live-sources lines, 245,000 (item 0e).
   Send the branch to the dynasty planner for a read, then ask Ben to
   approve. Then an Action for Ben: the assistant's branch, checkout and
   allow rules. Put a line on #191 for the move. Until that PR is live,
   the reset prompt for a clear is still a local, untracked file with a
   pointer in Ben's hands; if the pointer is lost, start from this file.
1. **Done: see B above.** *History:* #195: the pane shows 0.11.0 (Ben's
   word, issuecomment-6894719062)
   and the dynasty planner is told for #202. Ben ruled the one source:
   "Settings file (Recommended)" (issuecomment-6895058128). The new
   Action (item 0a) is Ben's hand step; the manager says in its chat
   when it is a quiet moment for it. When Ben says the version after
   the restart: read the new session's own `CLAUDE_CODE_PLUGIN_DIRS`,
   record both on #195, offer the commit of Ben's settings file by
   button, then open PR A as that comment says: a few lines after the
   `env` example in `plugins/owner-queue/README.md` and one clause in
   the Install line of the session-dispatch plugin's README, branch
   `docs/t195-one-plugin-source`. Read the hunks of PR #196 and PR #197
   in the owner-queue README first. If the pane is missing after the
   restart, Ben sets the user-level variable to the two live-clone
   plugin folders again and the choice goes back to Ben by button.
2a. **PR #210** (`t161-reset-prompt-pointer`, at `0b5acdb`, from `main`):
   the `session-rules` text for the redesign Ben approved on #161
   (issuecomment-6886175657). **Approved at `0b5acdb`, merge on Green**,
   by Ben's pane answer in the manager's session (pull/210
   issuecomment-6887544775); the Decision has left the queue. The
   manager re-proves and merges. After it merges: rewrite this
   file to the new shape (Current, then Reference) at the next
   state-back, and ask Ben for #209's go once the dynasty planner says on
   #161 that dynasty's state files are in the new shape. Three lines of
   `parking.md` conflict with #180 and #184: whichever merges second takes
   a merge of `main`.
2b. **PR #208** (`command-forms-restore`, at `0f1e1a1`): the `git restore`
   line in Command forms. Ben approved it to merge on Green
   (pull/208 issuecomment-6886359918); CI is green. The manager's next
   session merges it. Its settings half is done and has left the queue
   (pull/208 issuecomment-6886582743).
2c. **#204's reads are done**: the result table is posted
   (issuecomment-6894703025). Eight of nine reads worked, none failed,
   and Green's read worked. The repository is public, so most reads
   show only that the token does not break them; the table says so. The
   manager is told #206 may dispatch. When #206 merges: an Action for
   Ben to regenerate the token and run `tools/token_check.py`, then the
   result table, then Ben's decision on the switch by button.
2. **#193's trial passed** on the tools repository
   (issuecomment-6894814836, with Ben's push output: `GH013`). The
   dynasty ruleset Action is with the dynasty manager, with no test
   push there. PR B is open as #216 (item 0b). The ticket stays open
   for item 2, which waits for #191.
3. **PR #205** (ADR-0018 for #190, at `a9571f3`) is stacked on #194. When
   #194 merges: merge `origin/main` in, push, read its comments, ask Ben by
   button to approve at the new head and whether the manager may merge on
   Green. Its body flags two points for Ben's read. After it merges:
   - rewrite #191's body to cite the ADR (the App, the token rule, the
     ruleset that keeps the merge with the owner's login, the script's
     author and last-editor check), then tell the manager it may dispatch;
   - tell the manager #203 may dispatch;
   - ask the manager to draft the code-review ruleset line for the first
     review trigger (ADR-0015's route);
   - ask the dynasty planner for dynasty's asset list in its rules file.
4. **PR #184** (#183's rule text and ADR-0016) is at `05f2a7f`, with
   `main` merged in and three additions: the `Id:` line rule and the
   queue's set name (Ben's answers on #185; noted there,
   issuecomment-6888155220), and the flagged-`Answer:` sentence.
   ADR-0016's point 5 is reworded to those answers. **Approved at
   `05f2a7f`, merge on Green** (Ben, by button: "Approve, merge on Green
   (Recommended)", pull/184 issuecomment-6888151069). The manager noted
   the approval for its state file and gives #184 a place in its
   re-proof line. If `parking.md` conflicts after #210
   merges first, merge `main` in and ask Ben again: an approval covers
   one head. Its merge is the switch: from then, tools entries go to the
   tools queue. Then ask the manager to move the three planner Actions
   to the tools queue and to update each queue's head to the template
   (it gains the `Id:` field line).
5. **This state-back** (PR #198) is stacked on #181. After #181 merges,
   merge `origin/main` in, keep this branch's `PLANNER.md`, push, read its
   comments, and ask Ben by button to approve and give a merge word.
6. **#215** (the hook refuses a force delete of a branch whose tip is
   behind its merged PR's head; filed by the dynasty planner) is tiered
   medium, `Profile: none`. Ben's go: "Go, after #213 merges
   (Recommended)"; the closeout line is part 3 of its body, on Ben's "In
   #215's brief, object-only (Recommended)" (issuecomment-6894950231).
   Write its brief when #213 merges. The brief also adds one sentence to
   the hook README's layered-defense note: a second ruleset blocks force
   pushes on every branch. The reason for the object-only fetch is the
   advisory's section I.
7. **Findings to rule on** when their builders post them: #189, #187, #192
   (how the host matches rules; two more checks from the dynasty planner
   are on it, issuecomment-6886001749), #191 (how a one-hour token reaches
   a builder; a real fork goes to Ben by button). #200's design goes to
   Ben by button, as #168's did. #207's PR is #214; read it against the
   ticket if the manager asks.
8. **#164** is done: the first no-fork review link is noted on it.
9. **#212** (six rules from the dynasty Lessons lists, low, the
   planner's own PR): row 8 joined on Ben's "Add to #212 (Recommended)"
   (issuecomment-6894952102). Open one PR from `main` only after #210
   and #184 have merged (#180 has), then ask Ben to approve. Tell the
   dynasty planner the merge commit; #111's third commit then needs no
   rule text of its own.

## What this session answers for

- Tickets, tiers, `Profile:` lines and briefs for this repository.
- Rulings on builder PRs when the manager asks, and on first-step findings.
- Gaps found in the session-dispatch plugin and in this repo.
- This repo's `PROJECT-RULES.md` and the session-rules text (#148, #178,
  #183, PR #194), and the threat model (ADR-0018).
- The baseball handoff doc.

**Not the owner-queue mod.** The dynasty planner plans it.

Not building, not dispatching, and never a settings file or
`.claude/dispatch.json`.

## Open PRs and in-flight work

- **Merged 2026-11-15:** #180 as `fca5373`; #199 (#186) as `6262b1a`.
  Both tools checkouts were pulled to `6262b1a`.
- **Planner PRs:** #194 (approved, merge on Green at `8b66806`,
  next in line); #181 (approved, merge on Green at `148c9d1`); #184
  (approved, merge on Green at `05f2a7f`, sixth in the manager's
  line, after #210); #205 (stacked on #194, not approved);
  this state-back, #198 (stacked on #181, not approved); #208 (approved,
  merge on Green at `0f1e1a1`, CI green); #210 (approved, merge on Green
  at `0b5acdb`, by pane answer); #216 (approved, merge on Green at
  `3e99496`, last in the manager's line); #222 (the #195 docs, approved,
  merge on Green at `f85a7b4`).
- **Filed 2026-11-15, the nineteenth session:** #218, #219, #220, #221
  (item C).
- **Builder PRs:** #182 (#175, low review posted, no blocking finding);
  #196 (#179) and #197 (#161, the re-check accepted all seven answers),
  the dynasty planner's; #211 (#168, at `df23375`, its builder is
  working its one answer); #214 (#207, at `8e96d0b`, the re-check
  accepted all four answers).
- **The manager's order (2026-11-15):** one re-proof at a time: #194
  (its re-proof was running at the manager's clear), #181, #182, #208,
  #210, #184, #196, #197, #211, #214. The closeout of #186's builder is
  done.
- **Planned, not opened:** PR A for #195 (item 1), and the 245,000
  rule-text PR (item 0e).
- **Filed 2026-11-15, the seventeenth session:** #217 (`Tier: unset`,
  item 0d).
- **Filed 2026-11-15:** #212 (five rules, low, the planner's own PR, no
  dispatch); #213 (the hook and one more push form, medium,
  `Profile: none`, filed by the dynasty planner; Ben's go "Go, after #200
  merges (Recommended)", issues/213 issuecomment-6887956636; its detail
  is in the advisory, sections D, G and H, and its brief is written from
  them).
- **#189 is amended before dispatch** (issuecomment-6887448484): the two
  role templates drop their tier table and point to `session-rules`,
  Tiers; the README, `templates/brief.md` and `templates/gap-ticket.md`
  gain haiku.
- **Filed 2026-11-14, night, all low, `Profile: none`:** #206
  (`tools/token_check.py`, the write half of #204's test; go after the
  reads); #207 (`resume_plain.ps1` input checks; go at the next free
  slot); #209 (retire `prepend_state.py`; no go asked, not before #210
  merges).
- **Dispatch line, on Ben's recorded gos:** #206 (the manager places
  it); then #167, #189, then #187, then
  #192 (first PR: checks 1, 2, 3 and 7); #176 after the pull and #50; #200
  after #168 merges; #213 after #200 merges; #215 after #213 merges (the
  hook lane, one writer at a time); #203 and #191 after PR #205
  merges (#191 only on the planner's word); #201 after #191 merges.
- **Owner-led:** #183 (open for PR #184, #185 and dynasty #562); #190 (open
  until its follow-ups cite the ADR); #193 (item 1; item 2 waits for #191);
  #195; #204.
- **`Tier: unset`:** #188 is the dynasty planner's to tier.
- **#148**, **#112**: open, tier none.

## Queue entries raised

None open. Two #195 Actions in the dynasty queue file are ticked and
done, keyed to `Session: 2f6fe204-4035-42b0-ae8d-e0f20ea253b2`; they
leave at the manager's next state-back.

## Waiting on Ben

Nothing is waiting on Ben from this planner.

## Coming to Ben later

- The go for #220 (the plugin-source trial).
- Where the setup document lives and who writes it (item E).
- Approval of #221's PR, and the Action for the uncommitted edit to
  `PLAN.md` in the main checkout.
- The merge of the private configuration repository's working branch.
- The Action to remove the mod's old hand copy (#195).
- Approval of the `session-rules` PR for #217's choices 1, 2 and 4
  (with 245,000), with the dynasty planner's three points, after #210
  merges; then the Action that sets up the assistant's state branch.
- Approval of PR #205, after #194 merges.
- Approval of this state-back, after #181 merges.
- Approval of #212's PR, after #210 and #184 merge.
- The write half of #204's test, after #206 merges.
- #209's go, after #210 merges and dynasty's state files change shape.
- #200's design, and any real fork in #191's first finding.

## Vendor lane and held tickets

- **Vendor lane, one ticket at a time:** #50 first (`teach` and
  `grill-with-docs` back to manual; #177 has merged), then #176's sweep,
  then #57 → #52. #50 needs the `--bless` allow rule or the manager's run.
  Then #55.
- **#47** has a lane of its own: high, needs Ben's word, and can't run
  beside #54 (both edit `README.md`).
- **After #48:** #51, #53 and #54 (they also need Ben's `--apply` run and
  junction changes).
- **`GEMINI.md` and `.agents/`** belong to Ben's Gemini session. Claude
  sessions don't touch them.

## Milestones

- 2026-11-07 to 2026-11-12: see git history of this file.
- 2026-11-14, morning: Ben's GitHub rulesets on `main` in both repos;
  #174, #159, #177 approved with merge words; #48 built as PR #177;
  tickets #175, #176, #178, #179 filed.
- 2026-11-14, afternoon: #174 and #159 merged; the multi-repo owner queue
  grilled and filed (#183, ADR-0016 in PR #184); #186, #187, #189 and #195
  filed; PR #194 opened for the draft advisory GHSA-27j5-qx96-v8w3.
- 2026-11-14, evening: #177 merged at `134691e`; #190 to #193 and #200
  tiered with Ben's gos; #190 grilled in four rounds, SWOT, confirmed, and
  written as ADR-0018 in PR #205; #201, #203 and #204 filed; #193's ruleset
  text posted and its Action queued.
- 2026-11-14, night: #204's call list posted and its read Action queued;
  #206, #207 and #209 filed; PR #208 (the `git restore` form) opened and
  approved; PR #210 (the reset prompt as a pointer, the state file's one
  Current block) opened; the first no-fork review noted on #164.
- 2026-11-15 (UTC): PR #210 approved by pane answer; #189 amended; #212
  filed; #213 tiered with Ben's rule and go; three planner comments
  moved into the draft advisory and deleted from #200 and #213.
- 2026-11-15 (UTC), later: #180 and #199 merged; Ben's seven-rule edit
  to the tools builders' settings file done and checked; PR #184 brought
  to `05f2a7f` and approved, merge on Green; #207 dispatched.
- 2026-11-15, the sixteenth session: #204's read table posted and #206
  released; #195 at 0.11.0 and the one-source ruling; #193's trial
  passed; #215 tiered with its go; #212 at six rules; the advisory's
  section I; the plan for PR A and PR B approved.
- 2026-11-15, the seventeenth session: PR #216 built and approved; the
  #195 Action re-keyed; the tools side of the fetch finding read and
  written as the advisory's section I6, and its Action queued; Ben's
  two owner-queue asks recorded on #185 and #161 for the dynasty
  planner; #217 filed.
- 2026-11-15, the eighteenth session: #217 ruled in part, the
  assistant's role draft reviewed, three views and a second look posted;
  Ben's answers on choices 1, 2, 4 and 5; a freeze of all sessions
  asked and reached for the #195 Action's app restart.
- 2026-11-15, the nineteenth session: the #195 fix found under the
  wrong key, corrected by Ben from a queue Action and proved after a
  full restart; PR #222 opened and approved; #217 split into #218 to
  #221; choice 3 answered and the three settings files committed in the
  private repository; `PLAN.md` to become a pointer.

## Gaps

- **An Action that ends in an app restart** needs a quiet moment from
  every desktop session, asked by one session with one report to Ben,
  not from the manager alone (issues/195 issuecomment-6896476736). A
  candidate rule for #212.

- **The three settings templates lag the real files** (the advisory's
  section I6): they take the proven rules in one text change after the
  advisory is published. One part is safe to ticket now: the builders'
  template has no fetch allow at all, so under it a builder's
  `git fetch origin` is refused.

- **The hook README's layered-defense note** names only the `main`
  ruleset. Its one sentence goes into #215's brief.
- **The baseball handoff's next bump** also takes PR B (the ruleset
  section) and PR A (one source for the plugin folders).

- **The baseball handoff**
  ([docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md))
  is current at `01e2f46`. Bump it after #180, #184, #194, #205, #208,
  #210 and #212's PR merge (parking, the queue per project, the author rule, the threat
  model, the `git restore` form and the reset prompt changed; #177's
  auditor change is already on `main`).
- **The Tools planner has no role file.** Its read list goes into
  `PROJECT-RULES.md` with PR #210. A real role file is a later question
  for Ben: this repo's agents are linked into the owner's global agents
  folder, and the name would meet dynasty's own.
- **`CLAUDE.md`'s CI sentence** is out of date.
- **#140 F11:** a `-C` path is final even when it can't be resolved. No
  ticket yet.
- **The draft advisory's other fixes** are settings and script changes:
  Ben's hands and the dynasty planner's tickets. Its detail stays out of
  public tickets until it is published (at the fixes, or on 2026-11-28).
  ADR-0018 then gets a revision with that detail, and #192's later checks
  (4, 5, 6, 8) get their own ticket against the ADR's asset table.
- **The re-key text** in `parking.md` and the queue template still makes
  a session send its new id by hand. It stays until the mod change in
  #188 finding 1 is live; reword it with that change.
- **To confirm in #191's first finding:** that an App with write access
  to contents and pull requests can merge a PR (the ADR assumes so and
  asks for a ruleset), and that the API gives a ticket body's last editor.
- **The pipeline's App in dynasty** merges its own PR. ADR-0018 names it
  as a third actor; its limits are the dynasty planner's to list.

## Decided since the last state-back

Ben's decisions, each recorded on its ticket or PR.

- Gos: *Go, grill this session* (#190); *Go, after #190 merges* (#191);
  *Go, last in line* (#192); *Go, tools repo first* (#193); *Go, after
  #168 merges* (#200); *Yes, file and go* (#201); *File at low, go* (#203);
  *File, test first* (#204).
- #190's grill, fifteen questions, each *the recommended answer*: the
  adversary is a misled or mistaken session; three classes of text;
  limits against guards; one ADR here; nine assets; a GitHub App for
  builders; the owner's token in reach accepted for now; likelihood times
  impact; the token rule now and its mechanism from #191; App text is
  data and record text is written and last edited by the owner's login;
  builders only; one App; three review triggers; public now with classes
  only. Then *Confirmed, write it*.
- 2026-11-14, night, by button in this session: *Reads now, writes by
  script* (#204); *Public low ticket now* (the advisory's fix 7, #207);
  *Rule line and settings* (PR #208); *Go, after the reads* (#206); *Go,
  next free slot* (#207); *Approve, merge on Green* (PR #208 at
  `0f1e1a1`); *Now, from main* and *Project rules file* (PR #210's
  shape); *Not yet, read first* (PR #210's approval).
- 2026-11-15 (UTC), by button in this session, on the dynasty planner's
  candidates: *Add to PR #184* (the flagged Answer line); *Dynasty's
  rules file* (the Status block: no plugin change, dynasty #564
  issuecomment-6887450272); *Amend #189* (the tier table); *Five: 1, 2,
  3, 5, 7* and *Ticket now, PR later* (#212); *Six denies now, rest to
  #200*, then *Seven in one Action*, then *Ben does it now, from chat*
  (the tools builders' file; advisory section H); the hook's rule for
  #213 (advisory section G) and *Go, after #200 merges*; *Move to
  advisory, delete* (the three comments).
- 2026-11-15 (UTC), later, by button in this session: *Show the steps
  now* (the seven-rule edit, then done by Ben's hand); *Approve, merge
  on Green* (PR #184 at `05f2a7f`, pull/184 issuecomment-6888151069).
- 2026-11-15, the sixteenth session, by button in this session: *0.11.0*
  (the pane's version, #195); *It was refused* (#193's test push, then
  Ben's re-run with the output); *Go, after #213 merges*, *In #215's
  brief, object-only* (#215); *Add to #212* (the queue-entry rule from
  the #562 sitting); *Settings file* (the one source for the plugin
  folders, #195); the plan for PR A and PR B, approved in plan mode.
- 2026-11-15, the seventeenth session, by button in this session:
  *Approve, merge on Green* (PR #216 at `3e99496`); *Queue Action* (the
  fetch rules in the tools builders' file; the advisory's section I6);
  *Dynasty planner*, *Size only* and *Countdown only* (the owner-queue
  asks, #161 issuecomment-6895988934); the plan for this clear prep,
  approved in plan mode.
- 2026-11-15, the eighteenth session, by button in this session, all on
  #217: *Committed constant*; *Fixed branch per role*; *Later ticket*
  (cloud); on choice 4, first Ben's own words asking for a second
  thought, then his question why a state repository and not a state
  folder, then *State folder, fixed branch*.
- 2026-11-15, the nineteenth session, by button in this session:
  *Queue Action* (the corrected #195 hand step); *Go, last in line*
  (#219) and, in Ben's words, the go for #218; *Pointer* (`PLAN.md`);
  on choice 3, first Ben's words asking for a simpler question and a
  second thought, then "i'm fine with recc" with the question why by
  his hand, then *Claude commits, here*; *In place, plus a sharing
  finding* (where settings edits are made); *Approve, merge on Green*
  (PR #222 at `f85a7b4`); *Yes, state-back now*.
- By pane answer in the manager's session: PR #210, approve at `0b5acdb`,
  merge on Green (pull/210 issuecomment-6887544775).
- From the dynasty planner's session: *Approve, history to git* (the
  resume-prompt redesign, #161 issuecomment-6886175657).
- From the manager's session: Ben's four design rulings on #168
  (issuecomment-6885492170), and his answers on #185
  (issuecomment-6885472513).

## Lessons

- Address sessions by app id; check the checkouts before relaying a
  manager's claim about them. Read the queue file to confirm an entry.
- Before asking for an approval, read the PR's comments.
- **An approval covers one head.**
- **"Approve" is not "merge".**
- **Check `origin/main` before naming a merge commit.**
- **Start a safety rule from an allowlist; put the hard stop on the
  server** (#140, #159, #168; the rulesets are now in).
- **A limit is enforced outside the session; the rest are guards**
  (ADR-0018). A tested guard is still a guard.
- **A personal token is its owner to GitHub.** Fewer permissions, same
  actor; only an App or a second account can be bound apart by a ruleset
  (#190, #191).
- **A proof an agent may not run is the owner's step.** A force push is
  under "Never", so #193's test push is in Ben's Action.
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
  repository: the pane was a 0.7.2 hand copy (#195, and likely #202).
- **On a public repo, check who wrote a ticket's text** (PR #194).
- **A date only a session remembers is missed.** Put the trigger on the
  server (#203).
- **An entry that names a cleared id hides Ben's answer.** PR #210's pane
  answer sat in the queue file unseen; read the file at every start and
  after each wait, not only the chat.
- **A public ticket gets a pointer, not the open form** (2026-11-15):
  three comments had to be moved to the advisory and deleted. An issue
  body's edit history keeps every revision until Ben removes it, so an
  edit to such a body adds one more.
- **A ticked or reported-done Action is checked in the file** before its
  effect is recorded (#212 row 1).
- **An "Undo:" line under hand steps reads as one more step.** Ben
  asked whether to remove the line just pasted. Say "only to reverse it
  later", or leave the undo out of the steps.
- **A message queued behind a turn is read late.** When both sessions
  are near a clear, say so in the message, and put what must survive on
  the record with its link.
- **A ticked Action may come without its output.** Ask for it by
  button, and show the commands in the question: Ben could not tell
  which output was steps 5 and 6 until the three commands were in chat.
- **Messages cross near a clear.** After a peer's clear, send one
  message that repeats what was owed, each item with its record link.
- **A read of a public repository proves little about a token's
  permissions.** Say which reads are real proofs (#204).
- **The worktree session counts the word git in a path.** A command
  with `hooks/git-guardrails` in an argument is refused as two git
  calls. Read that folder with the Read tool, or name its parent.
- **A pasted reset prompt is stale as soon as the session works on.**
  It was written three times in one hour on 2026-11-15. Keep it in a
  file and hand over a pointer; keep commit hashes out of it.
- **Plan mode stops a clear prep.** Its comments, commit and push are
  all writes. When Ben asks for a prep while plan mode is on, put the
  prep in the plan and ask for approval at once.
- **A draft advisory has a size limit.** Read its length before a
  write, and say the room left to the other writers.
- **A peer's finding is a report to check.** The assistant read the
  mod's hand copy as never loaded; #195 shows it was.
- **A question that takes its premise for granted gets sent back.**
  Choice 4 asked who may commit and assumed where the file is; Ben
  asked for a second thought, and then why a repository and not a
  folder. State the premise and its alternatives first, and say where
  the first case was overstated.
- **A short prompt pasted into the wrong session gives it the wrong
  role.** After the restart the manager's session took the dynasty
  planner's prompt. The handover names the role in its first words;
  the session that receives it checks its own title against it.
- **At a prep, give Ben the file's full path and the short prompt
  together, each in its own code block** (Ben, 2026-11-15, issues/217
  issuecomment-6896764635).
- **State and record take different routes.** A role writes its own
  state; the owning planner posts a read-only role's record.
- **An Action that says "replace line N" quotes what line N holds
  now**, and its check's output comes back before the restart. The #195
  paste went to a line with the same key name, and cost three restarts.
- **"Restarted" must say what a restart is**: the app quit fully, tray
  icon included. A session reads its plugin list once, when the app
  starts it; `/reload-plugins` does not add a folder, and a child shell
  shows the file's value, not what the session loaded.
- **A relayed answer of Ben's is confirmed before it is recorded.**
  "Track as is" came by report; asked directly, Ben wanted a simpler
  question first.
- **"By Ben's hand" needs its reason each time.** Editing a settings
  file is the owner's; committing one as it stands is a record, and Ben
  may give that to a session by a one-time word.
- **The mod's options block in the settings file is written by the
  host's settings dialog**, not by hand (the host's documentation, read
  by a subagent).
- Worktrees share branch refs; only `HEAD` is per worktree.
- `/security-review` sees only commits. Commit first.
- A worktree session can't `git -C` the main checkout. Read each
  checkout's `.git/refs/heads/main` instead.
