# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-15 (UTC), at a fourteenth context clear.
`origin/main` was still at `134691e` (#177): nothing merged in that
session either. The #180 merge waits on Ben invoking `session-dispatch`
in the manager's session.

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
  each clear (`efe5ed14-3c04-4790-abf0-8442b111611a` on 2026-11-15). Its
  messages can sit queued while it is mid-turn: if it seems to miss a
  head or a go, re-send it with the PR comment link.
- **Merges (since #170):** the manager merges head-pinned in one call once
  Green, on Ben's pane Approve or his merge word. "Approve N" alone is an
  approval, not a merge word: ask Ben whether the manager may merge on
  Green. Relay his words word for word, record them on the PR.
- **The dynasty planner** (`local_84c6f2af-95ee-4c21-9c02-95877dc0cd21`)
  plans the owner-queue mod (#111, #137, #142, #147, #161, #179, #185,
  #188, #202). Its queue id was `c19bc37f-d5c9-4e25-af7e-36bff3f31a00`
  on 2026-11-15; Ben then asked it to prepare for a clear, so a new id
  follows by message.
- **The draft advisory GHSA-27j5-qx96-v8w3 holds what public tickets may
  not** (Ben, 2026-11-15: "Move to advisory, delete (Recommended)").
  Which push form a settings file or the hook does not refuse, and the
  rule text that closes it, go in the advisory, under "Moved from public
  tickets", and a ticket gets a pointer. Read it with
  `gh api repos/benjamininja/skills-plugins-hooks-agents/security-advisories/GHSA-27j5-qx96-v8w3 --jq .description`.
  Check a comment for such detail before posting it.
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

0a. **Re-read the dynasty queue file first.** Its three tools Actions
   (#195, #193, #204) still named the id `b5e85b86-f217-4a16-94e3-bc154bfd9e2f`
   at the last read, two clears old, though the manager was asked three
   times to re-key them. An answer on them is said in no chat: read the
   file for `Answer:` and `Note:` lines and for a ticked entry, and send
   the manager the new id.
0b. **The seven-rule edit to the tools builders' settings file** is
   Ben's hand, from chat, not a queue entry (Ben: "Ben does it now, from
   chat (Recommended)"; advisory section H). The steps were given in
   chat on 2026-11-15. Check the file's deny list: the new line follows
   the line that ends with the `origin main` rule. If it is not there,
   ask Ben by button whether to show the steps again. The rule text is
   in the advisory, section C; it goes in no tracked file.
0c. **#213's edit history** holds the first body twice: the first
   revision and the planner's own tier edit after it. The dynasty
   planner's queue Action asks Ben to remove the first; the manager and
   the dynasty planner are told it is two.
1. **The #195 Action** is in the dynasty queue. When Ben marks it done and
   says the pane's version, record it on #195 and tell the dynasty planner:
   #202 (the pane shows one queue) is most likely the same fault. Then
   propose the README line that names one source for the plugin folders.
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
2c. **The #204 read Action** is in the queue. When Ben pastes the window's
   output: post the result table on #204. If Green's read (the Action's
   step 5) worked, tell the manager #206 may dispatch (Ben's go: "Go,
   after the reads", issues/206 issuecomment-6886359008). If it failed,
   ask Ben by button what #206 should cover before any dispatch.
2. **The #193 Action** is in the dynasty queue (apply the no-force-push
   ruleset to this repo, one test push by Ben's hand). When Ben pastes the
   output of its steps 5 and 6: read the ruleset with
   `gh api repos/benjamininja/skills-plugins-hooks-agents/rulesets`, post
   the proof on #193, and tell the dynasty planner the trial passed. The
   dynasty ruleset is then the dynasty planner's own Action. After that, a
   small docs PR adds the setup-guide section.
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
4. **PR #184** (#183's rule text and ADR-0016, at `9b75719`) is stacked on
   #180. When #180 merges: merge `origin/main` in, add the rule text Ben's
   answers on #185 call for (the Id field, the queues setting's new shape:
   #185 issuecomment-6885472513), add one sentence to `parking.md`'s
   Answer section (a flagged `Answer:` line is not the owner's; Ben:
   "Add to PR #184", pull/184 issuecomment-6887449330) and name it in
   the body as outside ADR-0016, push, and ask Ben to approve and whether
   the manager may merge on Green. Its merge is the switch: from then,
   tools entries go to the tools queue.
5. **This state-back** (PR #198) is stacked on #181. After #181 merges,
   merge `origin/main` in, keep this branch's `PLANNER.md`, push, read its
   comments, and ask Ben by button to approve and give a merge word.
6. **#204** (narrow Ben's own GitHub login, owner-led): step 1, the call
   list, is posted (issuecomment-6885992121), with Ben's ruling "Reads
   now, writes by script" (issuecomment-6886194312). Next is item 2c.
7. **Findings to rule on** when their builders post them: #189, #187, #192
   (how the host matches rules; two more checks from the dynasty planner
   are on it, issuecomment-6886001749), #191 (how a one-hour token reaches
   a builder; a real fork goes to Ben by button). #200's design goes to
   Ben by button, as #168's did. #207 is dispatched at the manager's next
   free slot; read its PR against the ticket if the manager asks.
8. **#164** is done: the first no-fork review link is noted on it.
9. **#212** (five rules from the dynasty Lessons lists, low, the
   planner's own PR): open one PR from `main` only after #180, #210 and
   #184 have merged, then ask Ben to approve. Tell the dynasty planner
   the merge commit; #111's third commit then needs no rule text of its
   own.

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

- **Planner PRs:** #180 (#178, approved, merge on Green at `86a45e3`, in
  re-proof Green, pull/180 issuecomment-6886463954, merge due in the
  manager's next session); #194 (approved, merge on Green at `8b66806`,
  next in line); #181 (approved, merge on Green at `148c9d1`); #184
  (stacked on #180, not approved); #205 (stacked on #194, not approved);
  this state-back, #198 (stacked on #181, not approved); #208 (approved,
  merge on Green at `0f1e1a1`, CI green); #210 (approved, merge on Green
  at `0b5acdb`, by pane answer).
- **Builder PRs:** #182 (#175); #199 (#186); #196 (#179) and #197 (#161),
  the dynasty planner's; #211 (#168, at `df23375`, review at high and a
  queue entry for Ben's ADR-0017 text are the manager's next steps).
- **The manager's order (2026-11-15):** #180 merge, then the re-proofs of
  #194, #181, #182, #199, #208, #196, #197, #211; #207 at the next free
  slot. Agreed.
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
- **Dispatch line, on Ben's recorded gos:** #207 at the next free slot,
  ahead of the line; then #167, #189, then #187, then
  #192 (first PR: checks 1, 2, 3 and 7); #176 after the pull and #50; #200
  after #168 merges; #213 after #200 merges; #203 and #191 after PR #205
  merges (#191 only on the planner's word); #201 after #191 merges.
- **Owner-led:** #183 (open for PR #184, #185 and dynasty #562); #190 (open
  until its follow-ups cite the ADR); #193 (item 1; item 2 waits for #191);
  #195; #204.
- **`Tier: unset`:** #188 is the dynasty planner's to tier.
- **#148**, **#112**: open, tier none.

## Queue entries raised

Three are in the dynasty queue, read there on 2026-11-15, each still with
`Session: b5e85b86-f217-4a16-94e3-bc154bfd9e2f`. The session's id in
between was `57c20f52-66e7-4467-99d7-7d0768349609`; the manager was sent
it three times and had not re-keyed at the last read.

- *Point the plugin folder variable at the live clone (owner-queue 0.7.2
  is loading)*, #195.
- *Add the no-force-push ruleset to the tools repository and test it
  (#193)*. The ruleset list held only "main: require PR" at the last read.
- *Make a test token and run nine read calls with it (#204)*.

Gone from the queue: the tools builders' allow-rule Action (done) and the
PR #210 Decision (answered and recorded).

## Waiting on Ben

- The #195 Action (queue).
- The #193 Action (queue).
- The #204 read Action (queue).
- The seven-rule edit to the tools builders' settings file: by Ben's own
  ruling it is done from chat, not from the queue (item 0b).

## Coming to Ben later

- Approval of PR #205, after #194 merges.
- Approval of PR #184, after #180 merges.
- Approval of this state-back, after #181 merges.
- Approval of #212's PR, after #180, #210 and #184 merge.
- #206's dispatch word, or a button on its scope, after #204's reads.
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

## Gaps

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
- Worktrees share branch refs; only `HEAD` is per worktree.
- `/security-review` sees only commits. Commit first.
- A worktree session can't `git -C` the main checkout. Read each
  checkout's `.git/refs/heads/main` instead.
