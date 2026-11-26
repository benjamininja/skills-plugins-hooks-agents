# PLANNER: state of the Tools planner

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record; this file links to them and does not repeat them.

**Shape (Ben, 2026-11-22, #243: "One Current block").** One Current block,
then Reference. Each state-back rewrites Current in place. Older state is
in this file's git history:
`git log -p origin/docs/planner-state-1114c -- .claude/memory/PLANNER.md`.
The last stacked version, with 26 session blocks, is that branch's commit
before the #243 rewrite.

Last state-back: 2026-11-26, after the compact Ben asked for; the
lead approved the Windows plan, part 2 runs (draft PR #291), #289 is
filed and PR #290 is at a new head with the lead for a second read.
Compacts since that clear: 1.
A clear gives this planner a new queue id: send it to the four peers.

## Current

**Rules in force since 2026-11-25 (PR #274, #286, #287, #288).** Green is
the ruleset's required checks at the PR's head (Ubuntu and the catalog
check; Windows is no part of it), no conflict, the code review, the
hygiene hook; the manager reads main's last finished run before each
merge; no local full test run for a merge, except a PR that touches
`plugins/owner-queue/`. A Green holds while the head is unchanged. One
merge word in the manager's chat may name several PRs and is also the
approval of a planner's PR, so the planner asks no separate approval
question. The planner opens no new process ticket while more than ten
PRs are open, except for a real defect (its own rule, on #273).

**Next (act on this list, in order).**

1. **The CI gate fix: what is in, and what is left.** Ben's first
   priority of 2026-11-25; every word and button of his is on
   issues/187 from issuecomment-7167028313 on.
   - **In force (all merged 2026-11-25):** a PR runs Ubuntu (the whole
     suite, about 90 seconds) and the catalog check only; Windows runs
     on a push to main; a newer head cancels the older run (PR #284,
     `04b91c1`). Green on a PR has no Windows part (PR #286, `cb7fc13`).
     The manager reads main's last finished run before each merge and a
     red one stops merges (PR #287, `8bdf0da`). `session-rules` has "CI
     as a gate", five lines and a transition sentence, plugin 0.5.1 (PR
     #288, `acae1e7`, merged by the planner on Ben's "Yes, merge both").
     Ben took `pytest (windows-latest)` off the ruleset's required
     checks himself.
   - **Who signs off:** the dynasty planner leads every shared CI-gate
     text and signs off (Ben's word, relayed by the personal-assistant).
     Each head goes to it for approve or change before Ben; a new head
     needs a new read; its answer is recorded on the PR.
   - **Windows returns to a PR only after, in order:** #187's research;
     the dynasty planner consulted and approving the plan; Ben's word.
     Putting the check back on the ruleset is Ben's own step.
   - **Done 2026-11-26: the finding is ruled** (finding: issues/187
     issuecomment-7168273303; ruling: issuecomment-7191498749). About
     80% of the Windows job is process starts in
     `tests/test_git_guardrails.py`. Shards split by position are the
     route for part 2, which measures 4 and 6 shards and one
     `pytest-xdist` run on a draft PR and merges nothing; the part 2
     brief is the ruling's point 4. The hook's process starts (option
     b) are a separate ticket, **not opened**: ask Ben first.
   - **Done 2026-11-26: the plan is posted and sent to the lead**
     (issuecomment-7191499374): a skip list (`.md` outside `tests/`
     skips), shards plus one reporting job `pytest (windows)`, required
     or not on the measured time with about 6 minutes proposed as
     "cheap", the cost each time and for the 9 open PRs with a
     non-`.md` path.
   - **The lead approved with five changes** (issuecomment-7191535909)
     and all five are taken in (issuecomment-7191556477): no line in
     minutes before the measurement; the question to Ben says a
     deleting script's fault is not undone by a revert; the reporting
     job passes in two cases only; part 2 also measures queue time,
     flakes, per-shard set-up and order dependence.
   - **Part 2 runs:** builder `t187-windows-time` was resumed on
     2026-11-26 on Ben's button in the manager's chat (issues/187
     issuecomment-7191766144, the manager's report). **WAITING on part 2's finding:** rule
     on it, then ask Ben by button with the measured time beside
     Ubuntu's 1.1 minutes and dynasty's `storage-pg` at 4.7 (required
     on code PRs, or stay on main). The lead reads the workflow PR
     before its merge and the table of checks before Ben.
   - **#289 is filed** on Ben's "File now, find-out first
     (Recommended)": the hook's 150 to 250 process starts, tier high,
     step 1 a find-out that changes nothing. It stands behind PR #211
     in the hook lane; the manager is not told to dispatch it yet. Its
     step 2 needs the planner's ruling and Ben's go.
   - **#251's row 3 is ruled** (issues/251 issuecomment-7191499904):
     no whole local rerun; the manager runs the suite without the
     guardrails file in the light venv, about 10 minutes, and posts the
     count. A brief names `python -m pre_commit`.
   - **Left, c, text-only, may start now:** the tools table of checks in
     `PROJECT-RULES.md` (line 5 of the rule: each check, what it
     protects, which PRs run it, its measured time, required or not);
     the CI line of `CLAUDE.md`, which still says both systems on every
     PR; a look at ADR-0004 for the same. To the lead before Ben.
2. **The stop.** Ben stopped all tools work until the fix was in
   (issuecomment-7167039858); it covers the tools repository only.
   Text-only work restarted when PR #284 merged (his button). **Work
   that touches code stays stopped until Ben lifts it:** ask him by
   button when #187's change has merged, or earlier if he raises it.
   Held meanwhile: #285, the first real closeout run (#250), #251's
   build, every other dispatch. Running: `t187-windows-time` only, as
   far as the planner knows.
3. **PR #290 is open, the rest of #273** (head `651bc72`, on Ben's
   "Write it now (Recommended)", issues/273 issuecomment of
   2026-11-26): the four merge points, merging on Green with gate
   exceptions, one reviewer per PR, the planner's read list, the
   manager's role file, plugin 0.5.2. The dynasty planner read head
   `5c0ca5f`: approve, with three changes (pull/290
   issuecomment-7191805581). All three are taken at `651bc72`
   (issuecomment-7192280346) and that head is with it for a new read;
   CI at the new head was not read at the state-back. On its approval:
   tell the tools manager, who asks Ben the merge word (it is a gate
   change). By change 1 no path is covered until a project's table of
   checks is written and Ben has set the ruleset from it, so after
   this merge every tools PR still keeps Ben's word until the table
   PR (item 1's follow-on). One line is the
   planner's own and marked in the body for Ben to keep or strike: in
   this repository the word also stays for `skills/`, `plugins/`,
   `hooks/` and `.claude/agents/`. Until it merges, #273's text
   stands. The lines that #260 and #261 merged went out on 2026-11-26
   (issues/262 issuecomment-7191511586).
   **The state branch is `state/tools-central-planner` from
   2026-11-26** (PR #290 names it); `docs/planner-state-1114c` holds
   the same history up to that day and is left for Ben to delete.
4. **#204:** the narrowed token is the stored login; the Workflows
   permission is added and the retried workflow push went through
   (issuecomment-7167053023). The ticket stays open until Ben revokes
   the old wide login. Open: a pattern to test once GitHub is healthy,
   whether the token can merge a PR that changes a workflow file
   (issuecomment-7167819547; GitHub had an incident on 2026-11-25 from
   about 15:45Z, which explains the failures so far). Not ticketed: a
   `tools/token_check.py` row for a workflow push.
5. **#285, the boards token script** (medium): Ben approved the design
   (issues/204 issuecomment-7167394643) with no exemption from the
   stop. When code work restarts the manager dispatches it; the planner
   then posts the two hand steps for Ben as an Action. PR #266 merged
   with the boards duty as section 8 of the personal-assistant's role
   file; no board is edited before #285 merges. Owed from PR #266: the
   first session started from the merged role file tests its tools
   line, result on #233. The assistant will send Ben a design for one
   board over both repositories; both planners read it first.
6. **#262's rule-text build** is dispatched by the manager, now that PR
   #265 merged (`ab37521`), once the stop allows. Brief: issues/262
   issuecomment-7162955348 plus point 11 (issuecomment-7163139510) and
   point 12 (issuecomment-7164631610); Ben's go:
   issuecomment-7163080874. After it merges: the tools manager's role
   file line (a planner PR), the merge date on #262, one line to the
   dynasty planner.
7. **#250 and #251:** PR #252 merged (`f70ebe2`); the closeout
   prediction is on #250 (issuecomment-7167294872). The first real run
   waits for the stop; then the manager's Action with the text for
   Ben's managers settings file, and one line to the dynasty planner.
   #251: rule on its finding when the manager says it is posted.
8. **#219:** PR #271 merged (`e1fed0c`). Owed: a line there that one
   drift_check test's exit code depends on the clone it runs in (seen
   on PR #284); the trial's builder result from the next builder
   dispatched; then the deny entries common to every project and Ben's
   button on the private configuration repository's PR 12 (pointer:
   issues/219 issuecomment-7162465533).
9. **PR #270 merged** (`7064f34`): the manager posts the after figure
   on #269; no drop from about 55k means a revert PR. #264 closes with
   #269's reading.
10. **PR #227** (approved at `1b4200b`, pull/227
    issuecomment-7163729381): after its merge, the pointer-line Action
    for the private restore guide.
11. **After PR #197 merges:** ask Ben's go for #240 step 2 (brief at
    issues/240 issuecomment-7133603553); then #111's build brief; then
    #262's mod brief (ruling issues/262 issuecomment-7134266469).
12. After PR #249 merges (it read DIRTY on 2026-11-25): tell the
    dynasty planner, archive session
    `local_6b981a48-1f7d-4986-93e6-6af76d316f28`, comment on #235,
    #217, #161 and PR #197. PRs #205, #184, #216 and #222 wait on the
    manager's line.
13. Weigh whether #231, PR #242, PR #182 and #167 still earn their
    place now that no merge takes a local full run (#273) and CI's
    cost is being scoped (#187). #263 has no go; #258 holds the
    re-measure list.
14. **Coming to Ben later, by button:** what the owner-queue pane does
    with terminal output pasted into a Note (the personal-assistant's
    report of 2026-11-25; nothing reached GitHub). Not asked yet.

**Waiting on Ben:** nothing in this chat. His own later steps:
revoking the old wide login (#204); putting the Windows check back on
the ruleset, only after item 1's three conditions. Ben's standing
word, 2026-11-25: a session that needs him asks by pop-up in its own
chat.

**A lesson the planner keeps (Ben's words: unacceptably poor systems
thinking):** #273 made CI the gate before its cost was read, and the
first fix was put to Ben without saying that open PRs would keep
paying. Before any recommendation that adds or moves a gate: its cost
each time, how often it is paid, and what happens to work already
open, with figures; no figures, no recommendation yet. Every question
to Ben says what it costs him.

**No Done list is kept here** (the dynasty planner's point on #273):
the ticket is the record. Earlier state is in this file's git history.

**Ids (queue ids change at every clear).** This planner:
`a09ca279-6faa-4a61-a313-10328ff9c39d` since the start of 2026-11-26,
until the next clear. Peers, all new on 2026-11-26 after their own
clears, each sent by the peer itself:
Tools-builder-manager `3bac2fdb-b847-4732-b572-e582ae2af312`;
dff-central-builder-manager `9d28e196-d848-4cf7-a3d6-f97cbe859143`;
dff-central-planner `536a467f-4989-475e-bcc0-c7a14917d52a`;
personal-assistant `6f53e894-fbd7-4d4b-894d-55ffd90c0f71` (it was
started from a local pointer, so its role file's start line is still
untested; owed on #233). The tools queue is empty. PR #198 merged on
2026-11-25; the state branch has main merged in since and no open PR.
The assistant's start measurements of 2026-11-26 and two faults in the
measuring method are on issues/258 issuecomment-7191534990; both go to
#263's step 1. Its summary of a short form of the root preferences
file (24,018 characters to 6,227; untested; Ben's own change) is on
issues/258 issuecomment-7191748990. The manager reports t250, t257,
t260-261, t219 and t189 closed out and t283 waiting on Ben for a stale
worktree lock; not checked by the planner.

**Merge line (Tools-builder-manager, one re-proof at a time, each merge
word asked of Ben by button):** #236, PR #238 (the planner's), #239
(#237), #242 (#231). #241 follows #239. **PR #236 merged as `20f0954`
on 2026-11-24** (pull/236 issuecomment-7132452441); `origin/main` is
there, and by the manager's message so are both checkouts. Every
earlier Green is stale against it. The test line is with dynasty for
one full run (dynasty PR #659); #253's re-proof follows dynasty's end
notice. The manager's next state PR is #256.
- **#244 is done.** PR #246 merged as `aefbc68` on 2026-11-23, the first
  merge since `f1ff785` (2026-11-19), and closed #244. Its re-proof took
  3510.8 s for pytest, 89 s under the old 3600 s cap (pull/246
  issuecomment-7103972437). From the next re-proof the cap is 5400 s and
  the 25 slowest tests are printed; that table is #187's first evidence.
  Both checkouts are at `aefbc68`. t244's worktree is left for the #250
  script, on Ben's button in the manager's chat.
- #242: the re-check accepted F1 and F2 at `b278602`. It merges main in
  (#246 changed the same script), then needs its re-proof.
- **PR #253 (#248) merged as `6f67165` on 2026-11-24.** Every ADR file
  now needs a row in `docs/adr/README.md` (`tests/test_adr_readme.py`).
  **Done by the planner the same day:** main merged in and the row
  added on #205 (`3bddb2c`), #184 (`540dfff`) and #249 (`c010847`, which
  also makes the two Supabase role rows true). The three and PR #252
  each add a row at the same place, so whichever merges second merges
  main in again. #211 (ADR-0017) needs its builder to do the same; the
  manager is told.
- **The work order for the manager** (asked at Ben's request):
  pull/198 issuecomment-7134281643. Dispatch now on recorded gos: #187,
  #189, #219, #206, #167 (after #242), #192. Test line after #255, #259
  and #252: #197 first, then #210, #242, #205 and #249, #239 and #238,
  #211, #184, the rest. Nothing to close.

**#247, the Supabase roles (grilled with Ben, 2026-11-23; the ten
decisions are the ticket's body).** PR #249 is open: `supabase-router`
replaces the dispatch role file, the consultant is session-only with
assignment from Ben alone, a `supabase-look` template, an on-call
subagents rule in `session-rules`, ADR-0019. It merges after PR #205.
- **The deny rule is done and tested** (2026-11-23, #247
  issuecomment-7103215501): `Agent(supabase-consultant)` is in Ben's user
  settings, the session form still starts, and a subagent start is
  refused. The line is committed in the private configuration
  repository (its PR 11, merged as `680e7d9` on Ben's "Merge now
  (Recommended)"; #247 issuecomment-7104407619), so a restore carries
  it. That folder is back on its main branch, clean.
- **Dynasty's half** is dff-central-planner's own PR (`supabase-look.md`,
  draft dynasty PR #653, merges after #249)
  plus a `GOAL-RUN.md` line queued for Ben; a builder cannot write under
  `.claude/` (#247 issuecomment-7102585142). **The builder-subagent
  check is done** (#247 issuecomment-7103503667): with no deny rule a
  builder and its subagent were offered the server's 10 tool names;
  with `mcp__supabase-dynasty` denied in the builders' settings, none.
  Dynasty PR #657 carries that rule, and Ben's merge answer is recorded
  (issuecomment-7103550708). Dynasty PR #656 (the consultant line in its
  `GOAL-RUN.md`) merged as `97dbebb` (issuecomment-7103677619).
  dff-central-planner ruled that dynasty's builders also deny the
  separate, unauthenticated Supabase plugin server
  (issuecomment-7103639275). Dynasty PR #657 merged as `6721d97`. The
  second line is an Action for Ben in the dynasty queue, not yet ticked
  on 2026-11-24 (#247 issuecomment-7104068971).
- **After #249 merges:** archive the old session
  `local_6b981a48-1f7d-4986-93e6-6af76d316f28` (Ben's "Record, then
  archive after merge"; its final record: #247 issuecomment-7102435808,
  nothing open). Then comment the outcome on #235 (item c), #217, #161
  and PR #197 (drop dispatch from `ROLES`).
- **#248** (low): ADR hygiene. Ben's "Go, after line"
  (issuecomment-7102642772). Built as PR #253 (see the merge line). The
  planner's roles answer is on the ticket.
- The Tools planner now designs consultant, auditor and on-call
  subagent roles; `supabase-router` supplies drafts.

**#250 and #251, the builder environment's lifetime** (Ben's eleven
decisions from the assistant's grill, confirmed by button here:
issues/250 issuecomment-7103259381; dynasty's half is dynasty #655).
- **#250** (high, `Profile: none`): the closeout half. One script,
  `scripts/closeout.py` in the plugin, with a list-only count for every
  manager state-back, the closeout rule text and ADR-0020. Brief:
  issuecomment-7103342516. Ben's "Go, after the merge line
  (Recommended)" (issuecomment-7103389275), sent to
  Tools-builder-manager. Ben then told the manager "250 and 251 approved
  to launch" and chose "Now, no full run (Recommended)"
  (issuecomment-7103443214): dispatched as builder `t250-closeout-script`
  from `f1ff785`, with one added paragraph that the builder runs no full
  suite until the manager gives the test line. Its plan is
  issuecomment-7103465652.
  - **Part 1 is ruled.** Finding: issuecomment-7103861254, with a
    correction (issuecomment-7104084566). On Windows a held-open file
    stops `git worktree remove` part way while git drops its record,
    and a junction inside a worktree is handled badly in two different
    ways by two git versions (one deletes the target's contents).
  - Ruling: issuecomment-7103994943; amendment:
    issuecomment-7104205770. In-use check by rename, apply-only and
    Windows-only; the script never fetches; a folder link that points
    out refuses; the script checks the folder itself after git returns.
  - **Ben's word on one point:** a clean worktree with no merged PR and
    no commit of its own is removable when named ("Removable
    (Recommended)", in the ruling; confirmed in the manager's chat,
    issuecomment-7104196182). The list count shows those apart.
  - Part 2 is being built in PR #252. Both hazards went to the dynasty
    manager and planner as a report. The tools manager checks for
    junctions by hand before any removal until the script lands.
  - **Second amendment** (issuecomment-7104581056), after the
    personal-assistant's read-only classification of all 125 worktrees
    (recorded at issuecomment-7104579581, with its expected numbers for
    the first list-only run). On Ben's "Both kinds (Recommended)": the
    script restores status lines that hold no content (a file whose git
    diff is empty; a tracked file deleted from the folder), then
    removes. A record with no readable HEAD has its own verdict and is
    never removed (dynasty has 24, 15.7 GB; their repair is dynasty's,
    #655). Locks are printed and counted apart. The list covers every
    worktree under the folder. An open PR is its own verdict.
  - **The second amendment is not in the build yet** (checked
    2026-11-24). PR #252 left draft at `ab3c279` four minutes after the
    amendment was posted. Its body cites the ruling and the first
    amendment only, and its count line has three buckets. The planner
    sent the comment to Tools-builder-manager again on 2026-11-24, and
    the manager sent it to builder t250 whole, on Ben's "Confirm, send
    whole (Recommended)" in its chat (issuecomment-7132487415). No code
    review and no re-proof of #252 until t250 answers points 16 to 22
    at a new head.
  - The builder's state-back (issuecomment-7104691933) adds one check
    beyond the ruling, from its security review: the worktree's `.git`
    file is checked against the main checkout's record before any git
    call runs in the worktree. It also names a stale line in the
    manager reference, outside its brief (see Gaps).
- **#251** (medium, `Profile: none`): the dispatch half. `setup` and
  `setupFull` lists, a switch on `dispatch.ps1`, and the brief line
  `venv: light, full or no`. Ben's "Go, after #189's PR (Recommended)"
  (issues/251 issuecomment-7103390046). **The planner writes its brief
  when #189's PR merges**, and rules on its finding.
- **#254** (low, `Profile: none`): one `.gitattributes` line,
  `CATALOG.md text eol=lf`. The catalog build leaves `CATALOG.md`
  flagged as modified with an empty diff, and git then refuses to
  remove the worktree; by the assistant's count that is the only status
  line in 15 of 31 merged tools worktrees. The planner reproduced it
  and tested the fix in its own worktree. Brief in the ticket's body;
  Ben's "File it and go, low (Recommended)" (issues/254
  issuecomment-7104636475). Dispatched on 2026-11-24 as builder
  `t254-gitattributes`, on Ben's "Dispatch when level (Recommended)" in
  the manager's chat (issues/254 issuecomment-7132504195).
- **Planned planner PR, after #251's finding:** decision 10's two rules
  in `session-rules` (the main checkout's packages change only when no
  builder runs; a `requirements.txt` ticket gets `venv: full`).
- **The cleanup** is the script's first real run after #250 merges, by
  each manager on Ben's word; refusals go to Ben as one queue list. It
  replaces the #235 step 3 prune, which waits until then.
- The cause is still inferred (closeout not run to its end). The tools
  manager has run no closeout yet, by its own state file.

**Next for this planner, in order:**
0. **PR #210, brought forward on Ben's "Bring PR #210 forward
   (Recommended)"** (pull/210 issuecomment-7134168914). Main is merged
   in and a manager's Current block gains an In flight section; head
   `a30c3fa` (pull/210 issuecomment-7134267607). **CI is green there and Ben approved it: "Approve at a30c3fa
   (Recommended)"** (recorded on the PR; the manager is told). The planner moved it
   to the front of the manager's test line (2026-11-24, after the third
   compact). #261 and #260 are amended (issues/261
   issuecomment-7134902887, issues/260 issuecomment-7134903881) and
   **Ben gave the go for both as one builder PR at #210's merge: "Go,
   assistant waits"** (on #261). The personal-assistant proposes its
   short preferences only after #261's PR merges; send it one line then.
   The one brief for both is issues/261 issuecomment-7134928088, with
   one correction after it (issuecomment-7135557161: the manager runs
   pre-commit at re-proof). The manager reports Ben confirmed the
   dispatch in its chat; #210 is next in its line after #255.
   **Ben wants the tickets ahead of the personal-assistant (#261, #264)
   worked actively; the assistant holds** (his words on issues/261
   issuecomment-7135940410). So the #260/#261 builder starts now,
   stacked on PR #210's branch, and **#264 has Ben's go: "Go now
   (Recommended)"** (issues/264 issuecomment-7135982334). Dispatch
   order given to the manager: #260/#261, #264, #189, #219, #206; code
   reviews of PR #197, #259, #242 meanwhile (pull/198
   issuecomment-7135884969). Rule on #264's finding when posted and
   tell the assistant.
   **#218 also stands before the assistant's trim** (its report, issues/218
   issuecomment-7136008534; it did not name #264). Ben: "Write both now
   (Recommended)" (issues/218 issuecomment-7136027605). Written and
   open, stacked: **PR #265** (#217's choices 1, 2, 4 in session-rules;
   branch `t217-portable-roles`, base PR #210's branch) and **PR #266**
   (#218's role file; branch `t218-personal-assistant-role`, base
   #265's branch). Merge order #210, #265, #266; each needs Ben's
   approval at its head once CI is green, and main merged in after the
   PR before it merges. Open point in #265's body: #260, #261 and
   #262's ruling 5 still speak of a reset prompt; under choice 1 there
   is none, so the planner rewords them when the PRs meet, or Ben
   reverses choice 1. #266 asks Ben: model opus or fable. The
   assistant read #266 and its six points are in at head `3c01e78`
   (pull/266 issuecomment-7136204252). **Next on these two:** when PR
   #210 is squash-merged, merge origin/main into `t217-portable-roles`,
   retarget #265 to main (`gh pr edit 265 --base main`), read CI, ask
   Ben's approval at that head; the same for #266 after #265. The
   manager keeps PR #210's branch until #265 is retargeted.
   dff-central-planner's id since its clear:
   `9bcc0c9c-574c-4ebb-b4f4-18edc03af9aa`; it expects one line when
   #249, #260, #261 or #262 merges and when PR #252's script first runs.
   **#262's rule-text brief:** write it when the #260/#261 PR opens (same
   section), then ask Ben's go by button. Its mod brief follows PR #197,
   after #240 step 2 and #111.
0b. Tell dff-central-planner when PR #249 merges (dynasty PR #653 goes
   ready then).
1. **After #242 merges:** the planner's PR that replaces PROJECT-RULES'
   one-run message rule with the lock.
2. **#233's finding** when it comes: rule on it. Send the link to
   dff-central-planner, which files the dynasty follow-up.
3. **#243, the memory review: the root split is done.** dotclaude PR #9
   merged as `cfba40f` on Ben's buttons (issues/243
   issuecomment-7084451575). Dynasty's stale descriptions of root are
   dynasty #637. The stale-paths planner PR is dropped: #238 and #239
   cover every path. #245 is closed as a duplicate, folded into #241 on
   Ben's "Fold into #241 (Recommended)" (issues/243
   issuecomment-7085623163; #241 issuecomment-7085619927). Peers:
   Tools-builder-manager trims `MANAGER.md` after #236 merges;
   personal-assistant's points are on #218 (issuecomment-7082200407).
   The local dotclaude branch `memory/root-split-243` is merged content;
   the guard hook refuses its delete from here, so it is left.
4. **Dispatchable after the merge line** (sent to Tools-builder-manager,
   gos recorded): #189, #219. #232 follows #189's PR; #220 follows
   #219's first finding (go recorded, brief then); #218 follows the #217
   rules PR, which follows PR #210; #226 follows PR #197.
5. **#235 remainders:** step 3's prune is now #250's first real run (the
   manager's, on Ben's word), then step 11 (Ben removes the old folder).

**Open planner PRs** (each needs `origin/main` merged in and Ben's
approval at its new head when its turn comes; an approval covers one
head): #184 (#183, queue per project, ADR-0016), #198 (this state
branch), #205 (ADR-0018), #208 (`git restore` form), #210 (reset prompt
as pointer, one Current block), #216 (ruleset setup), #222 (#195 docs),
#227 (#223 setup doc), #238, #249 (#247, after #205).
- **#184** was reworked on Ben's "Both PR repairs (Recommended)": head
  `8acbb17`, main merged in, main's PROJECT-RULES text taken, ADR-0016
  brought up to date (pull/184 issuecomment-7104281978).
- **#227** is at `1b4200b`: the GitHub folder's path corrected after the
  move, on Ben's "Fix the paths now (Recommended)". Ben's approval of
  2026-11-15 covered `63c6445` and has lapsed (pull/227
  issuecomment-7104213254).
- **#198** is not in the merge line; the planner names its head at a
  quiet point (pull/198 issuecomment-7104044082). Its branch is not
  deleted outside that merge.
- **#181** is closed as superseded by #198, on Ben's button in the
  manager's chat.

**Open builder PRs:** #182 (#175), #196 (#179), #197 (#161), #211 (#168),
#214 (#207), #239, #242, #252 (#250, draft), #253 (#248). #182 keeps
its place with no rework (pull/182 issuecomment-7104046736). #196 and
#197 were planned by dff-central-planner and are this planner's now,
with the rest of the mod lane (above).

**The owner-queue mod lane is the Tools planner's since 2026-11-24.**
Ben's "Transfer the whole mod lane" in dff-central-planner's chat
(handoff: #137 issuecomment-7132677793), confirmed here by button,
"Whole mod lane (Recommended)" (#137 issuecomment-7132702847). It
replaces the lane ruling of 2026-11-09. Tools-builder-manager is told.
- **The design is decided, by four buttons here on 2026-11-24.**
  - Auto-close is an entry collapsing at the press of an option or Mark
    done; no entry is hidden and the file is untouched (#137
    issuecomment-7132851563). It needs no rule text.
  - The button is "Ask planner only": #111 is its ticket, and #137's
    Bring to Chat is not built (#137 issuecomment-7132901826).
  - "Two tickets, auto-close first (Recommended)", which is also the go
    for both items below.
- **#257** (low, `Profile: none`): auto-close. Brief in the body; go at
  issues/257 issuecomment-7132994645. Sent to the manager.
- **#111** (high): amendment 2 refreshes it against mod 0.11.0 and
  holds the brief for its first step, a find-out with no code change
  (issuecomment-7133007701). Sent to the manager. **The build waits**
  for the planner's ruling on that finding, PR #197's merge and #240's
  finding; the planner then posts the build brief and asks Ben's go.
  ADR 0014 is held for it. #137's F7 fold-in moved here.
- **#257 is built as PR #259.** Planner read: no breach, and the
  version constant (`register.tsx` line 48, `answer.test.ts` line 182)
  goes to 0.11.1 (issues/257 issuecomment-7133159600). New head
  `85186e1`; the manager's code review and re-proof follow.
- **#111's first step is done and ruled** (finding:
  issuecomment-7133152245; ruling: issuecomment-7133339403). A final
  question is asked alone and single-select; `result.response` first,
  then an exact label match. Nothing is staged on a timeout, a follow-up,
  a deny or an error. The store crossing gets a live check, with no
  code, before the build brief. What names a project in the store is
  held for #240's finding.
  - Ben's "Command plus fixed names" (issuecomment-7133391701, against
    the planner's recommendation of the command only): `/owner planner`
    plus role names fixed in the mod's code, matched exactly on
    `$.session.info().agentType`. The names are set in the build brief;
    the value is printed in `/owner id` and read live at re-proof. The
    Tools planner has no role file, so it registers by the command.
- **#240** (medium): Ben's "Find-out now (Recommended)". Step 1 is a
  read-only find-out, brief at issues/240 issuecomment-7133315138, sent
  to the manager; done by builder `t240-findout` (finding:
  issuecomment-7133503110).
  - **Ruled, with Ben's "A. Re-key by path (Recommended)"**
    (issuecomment-7133603553, which also holds the step 2 brief): a
    one-time move of the path-keyed records, no prune, a toast when the
    own queue file is missing, one shared constant of store families.
    **Step 2 is dispatched after PR #259 and PR #197 merge**; the go is
    asked of Ben by button then.
  - #111's question 4 follows it (issues/111 issuecomment-7133604792):
    the record is keyed by `at()`, its family joins the constant, and
    #111's build also waits for #240's step 2 to merge.
- **#137 is closed as not planned,** on Ben's "Close now (Recommended)". PR #259's review advisory F1 (no test of an
  entry that starts closed) goes into #111's build brief (issues/257
  issuecomment-7133418739).
- PR #255 (#254) is open with a clean code review; its re-proof follows
  #253's.
- **Constraints from dynasty** (the handoff): the manager is the queue
  file's only writer and records every Note and Answer before the CLI
  removes an entry; a message keeps the question, the answer and a
  `Time:` line; nothing acts on an entry mid re-key. dff-central-planner
  wants one line when the pane's behaviour changes.
- **The lane's other open tickets, not yet read by this planner:** #240,
  #234, #229, #226, #225, #202, #188, #185, #179 (PR #196), #161
  (PR #197), #147, #142, #195.

**#258, token cost by role** (`Tier: unset`): the personal-assistant's
ledger of 2026-11-24, held as a report. Managers and planners carry 55
percent of the tokens, and most of every role's cost is context
re-read per message. Open: whether a cost rule (model and effort per
role, a lower clear point, a start-up read budget) is worth a ticket.
Part 3 (fixed context itemized; a compact costs about 0.15 million
against a clear's median 0.71) and the planner's four answers are at
issuecomment-7133316206.
- **The trial compact is done** (list: issuecomment-7133403017; result:
  issuecomment-7133497414; figures: issuecomment-7133550402; dynasty's
  trial beside it: issuecomment-7133606065). The short list was enough;
  about 0.18 million and 112k of context, against 0.33 and 0.60 million
  for this planner's clear starts.
- **Ben's "Wait for numbers (Recommended)"; the rule's ticket is #260**
  (low): after a compact a role session reads the issue and PR lists and
  its queue files only. Dispatched after PR #210 merges (same section).
- **Ben chose all four further pieces for tickets** ("Start-up read
  budget, Prefer compact to clear, Manager cost find-out, Fixed context
  find-out"), then asked that the plan be agreed with
  dff-central-planner and personal-assistant first. The draft plan and
  the questions to each are at issuecomment-7133848772; both are
  messaged. **Both agreed, each with three changes, all taken**
  (issuecomment-7133939762). **Filed: #261** (low, start-up read budget;
  after PR #210 and #260), **#262** (medium, compact by default; first
  step a find-out), **#263** (medium, manager cost find-out; step 1
  ports the assistant's scripts to tracked code), **#264** (medium,
  fixed context find-out, lowest priority). **#262's find-out has Ben's
  "Go, find-out now"** (issues/262 issuecomment-7134018512, with the
  brief; the manager's view on three compacts is at
  issuecomment-7133968750). Done by builder `t262-findout` (finding:
  issuecomment-7134196482) and **ruled** (issuecomment-7134266469): the
  owner types the compact; the mod counts, the state file is the
  fallback; the boundary after the third compact is a clear; the reset
  prompt is still written before a compact and read after it when a
  background task ran or there was no prep. **This planner is not
  tracked by the mod, so its count stands here: compacts since the last
  clear (2026-11-23): 3 once the compact Ben asked for late on
  2026-11-24 is done (two came earlier that day), so the boundary after
  it is a clear, if the rule is applied before it is built. Ben asked
  for a further compact later that day ("prepare for compact"): 4 once
  it is done, one past the ruling's three. The prep serves a clear as
  well; the boundary after it is a clear.** The build
  brief follows after PR #210, #260 and PR #197; go by button then. Its finding comes to the planner to
  rule. The others are not dispatched; each go is asked of Ben by
  button at its turn. **The baseline is frozen on #258** (issuecomment-7134046140: 145.2
  million over 68 sessions, each reply counted once; the earlier 242
  million used another rule). #263 amendment 1 carries its two rules.
  No retention setting is asked of Ben. After
  #261 merges the assistant proposes a short form of the root
  preferences file on #258; the change is Ben's.
- The assistant's third data point (a clear with a short fixed list:
  0.20 million, 126k) is at issuecomment-7133736829.
- **PR #252 (#250):** code review closed with no blocking finding open.
  The planner confirmed F1 (merged means merged into main; pull/252
  issuecomment-7133650154). Plan-breach read at `5f253ba`: no breach,
  three text fixes before the merge (ADR-0020's stale count, the
  docstring and README, the settings example's note and deny lines;
  pull/252 issuecomment-7133882719). **The fixes are in at head
  `447f3fc`**; the manager checks them at re-proof, and no new planner
  read is needed. After the merge the manager queues
  one Action for Ben with the text for his managers settings file.
  ADR-0020 needs an index row once PR #253 merges.
- Each ticket number split out of #258 goes to the assistant when filed.

**Planned, not opened:** the `session-rules` PR for #217's choices 1, 2
and 4 with 245,000 (after PR #210; its text: #217
issuecomment-6896675395, #161 issuecomment-6895988934); #212's PR
(after #210 and #184); the baseball handoff bump (after #180, #184,
#205, #208, #210 and #212 merge).

**Dispatch line on recorded gos, after the above:** #254 (low, when the
manager has a slot); #206; #167; #187;
#192 (first PR: checks 1, 2, 3, 7); #176 after #50; #200 after #168
merges; #213 after #200; #215 after #213 (the hook lane, one writer at a
time); #203 and #191 after PR #205 (#191 only on the planner's word);
#201 after #191. Vendor lane: #50, then #176, then #57, then #52, then
#55. #47 runs alone (not beside #54). #51, #53 and #54 after #48.

**Findings to rule on when posted:** #189, #187, #192, #191 (a real fork
goes to Ben by button), #233, #251. #200's design goes to Ben by
button. #250's PR #252 comes to the planner for a plan-breach read if
the manager asks.

**Coming to Ben later (not waiting yet):**
- The approvals of the open planner PRs above, each at its turn.
- The `session-rules` PR for #217, then the Action for the assistant's
  state branch.
- The write half of #204's test, after #206 merges.
- #209's go, after #210 merges and dynasty's state files are in the new
  shape.
- The Action to remove the mod's old hand copy (#195).
- The merge of the private configuration repository's working branch.

**Waiting on Ben:** nothing. Next asks, each by
button at its turn: the go for #240's step 2 (after PR #259 and PR #197 merge), then #111's
build brief, and any point of the cost plan the three sessions do not
agree on.

## Reference

### Role

- **Tools-central-planner**, the standing planner for
  `benjamininja/skills-plugins-hooks-agents` (since 2026-11-07). Call the
  owner **Ben** or "the owner", and this session **Claude**, never "you"
  or "I".
- Answers for: tickets, tiers, `Profile:` lines and briefs here; rulings
  on findings and on builder PRs when the manager asks; gaps in the
  session-dispatch plugin and this repo; `PROJECT-RULES.md`, the
  `session-rules` text and ADR-0018; the baseball handoff doc.
- Also the owner-queue mod, since 2026-11-24 (#137
  issuecomment-7132702847). Never builds,
  never dispatches, never writes a settings file or `.claude/dispatch.json`.
- **Peers** (address by name from ListAgents): Tools-builder-manager
  (dispatches, re-proves, merges and writes this repo's queue);
  dff-central-builder-manager and dff-central-planner (dynasty);
  personal-assistant (reports only, never Ben's approval). The
  supabase-consultant-dispatch session is retired (#247) and waits for
  its archive.

### Working rules

- **Every question to Ben goes through a button**, with summary, pros,
  cons, then the recommendation above it. A ready item gets a button that
  turn; an open item goes to Tools-builder-manager as a ready queue
  entry; never a prose list.
- **Second look, then a SWOT** before a rule or ADR question (Ben,
  2026-11-14).
- **A new ticket needs Ben's go before dispatch.** Record the go on the
  ticket; relay it word for word.
- **"Approve" is not "merge"**: ask whether the manager may merge on
  Green. The manager asks Ben again in its own chat for every PR.
- **After every merge** the manager pulls both checkouts. Check the heads
  by reading each checkout's `.git/refs/heads/main`.
- **Advisory rule:** an unrefused command form goes only in the draft
  advisory GHSA-27j5-qx96-v8w3, and the public ticket gets a pointer. Read
  it fresh before each write:
  `gh api repos/benjamininja/skills-plugins-hooks-agents/security-advisories/GHSA-27j5-qx96-v8w3 --jq .description`.
  The limit is 65,535 characters, and it stood near 62,800 on 2026-11-15.
- **Briefs:** nothing under `.claude/` in a builder brief. The proof line
  `pre-commit run --from-ref origin/main --to-ref HEAD` is the manager's,
  at re-proof.
- **Planner PRs** come from the worktree whose first branch was
  `t112-closeout-pulls` (`C:\source\Github\skills-plugins-hooks-agents`
  is the main checkout). Use a fresh branch from `origin/main`, then
  switch back to `docs/planner-state-1114c`. Run one plain git command
  per call. Body text goes in a file made with Write. Commit with
  `git -c user.email=38588919+benjamininja@users.noreply.github.com commit -F <file>`.
  Run `/security-review` on the committed diff before the PR.
- **pytest** runs with this repo's own `.venv` in the main checkout, in
  the background (about 20 minutes). Skip it for a text-only change while
  the manager needs a quiet machine, and say so on the PR.
  `tools/build_catalog.py` leaves a line-ending-only change in
  `CATALOG.md`: check it with `git diff --ignore-cr-at-eol` and drop it.
- **ADR numbers:** 0016 is in PR #184, 0017 is #168's builder's, 0018 is
  in PR #205, 0019 is in PR #249, 0020 is #250's builder's. The next free
  number is 0021.
- **The clear boundary** (`session-rules`): close the step, record, then
  state-back on this branch, then memory, then the reset prompt last. The
  reset prompt is a local, untracked `reset_prompt.md` in this worktree's
  `builder-state/`, and Ben gets its path plus a short pointer, each in
  its own code block.
- `GEMINI.md` and `.agents/` belong to Ben's Gemini session; leave them.

### Gaps (not yet ticketed)

- An Action that ends in an app restart needs a quiet moment from every
  desktop session, asked by one session (#195); a candidate for #212.
- The three settings templates lag the real files (advisory I6). The
  builders' template has no fetch allow rule.
- A project with a database server needs a server-level deny rule in its
  builders' settings: without one, a builder is offered the server's
  tools (#247 issuecomment-7103503667). The plugin's builders template
  and setup guide do not say so. The same holds for a plugin's server
  that is not signed in: its sign-in tools are still offered
  (issuecomment-7103639275).
- Root preferences hold a caution, marked as the agent's own, against
  a junction inside a worktree. #250's tests now prove the hazard for
  the git on this machine; the line can say so at the next root-memory
  change (a private-repository PR, on Ben's word).
- Tracked `.claude/agents` files are deleted from the folder in some
  old worktrees in both projects; which tool did it is not known (#250
  issuecomment-7104579581, finding 3).
- `session-dispatch`'s `references/manager.md`, "Its own merges",
  deletes the manager's own or the planner's merged PR branch once
  `git cherry` shows nothing missing. `git cherry` compares commit by
  commit, so after a squash of several commits it still lists them and
  the test never passes. Reported by #250's builder
  (issuecomment-7104691933); the planner read the line and has not
  tested it. The fitting test is the closeout script's merged test, so
  the text change waits for PR #252 to merge.
- The hook README's layered-defense note names only the `main` ruleset;
  the fix sentence goes in #215's brief.
- The Tools planner has no role file; its read list goes into
  `PROJECT-RULES.md` with PR #210.
- #140 F11: a `-C` path is final even when it can't be resolved.
- The re-key text in `parking.md` stays until #188 finding 1 is live.
- To confirm in #191's first finding: whether an App with contents and PR
  write access can merge, and whether the API gives a body's last editor.
- The dynasty pipeline's App merges its own PR; dff-central-planner lists
  its limits.

### Lessons

- Read what the code does today before putting design options to Ben,
  and ask what a word of his means before building options on it. For
  "auto-close" the planner offered three ways to hide or remove an
  entry; Ben meant the entry collapsing, and the closed row already
  showed the staged choice (#137, #257, 2026-11-24).
- Before filing a ticket or planning a PR, search open issues and PRs
  for the same file. #245 and a planned PR duplicated #237, #239 and
  #241 (2026-11-22).
- Never `cd` into another repository in a shell call: the session is
  re-rooted there and cannot re-enter this worktree with EnterWorktree.
  Read another repository with `git -C` or with absolute paths. If it
  happens, `cd` back to the worktree's full path.
- A builder cannot write under `.claude/`, so a project's agent file or
  rules file is never a builder ticket: it is that project's planner's
  PR, or text queued for Ben (#247, dynasty PR #653).
- On a design question that touches safety or trust, Ben wants a second,
  critical pass before the recommendation: read the files line by line,
  check the claim against the ADRs, and say what changed (#247: the
  spoofable dispatch name, and "a tools line is a guard, not a limit").

- Address sessions by name; check checkouts and queue files before
  relaying a claim about them. A peer's finding is a report to check.
- Read a PR's comments before asking for its approval. An approval
  covers one head. Check `origin/main` before naming a merge commit.
- Start a safety rule from an allowlist; put the hard stop on the server.
  A limit is enforced outside the session; the rest are guards
  (ADR-0018). A personal token is its owner, to GitHub.
- A proof an agent may not run is the owner's step.
- Rate risk as likelihood times impact.
- A queue entry's Session line must name a session that will wake. Read
  the queue file at every start and after each wait.
- An allow rule must match the command actually run; a chained line
  never matches. The worktree session counts the word git in a path.
- A step called small may hide the hazard. Check what version actually
  runs, and that a file is loaded, before designing on it.
- On a public repo, check who wrote a ticket's text. A public ticket gets
  a pointer, never the open form: edit history keeps every revision.
- A date only a session remembers is missed: put the trigger on the
  server.
- "Done" or a ticked Action without output is checked in the files
  before it is recorded. Ask for missing output by button, with the
  commands shown.
- An Action's check step says what the screen shows on a pass and on a
  fail, and gives the folder as a full path. Ben ran the #247 session
  check, could not tell whether its output was a pass, and asked for
  help (2026-11-23).
- Check a gap's premise before offering its fix. The planner offered
  Ben a deny-rule line for PR #227 unchecked; the document excludes
  settings content and the settings file is tracked in the private
  repository. The PR's real fault was stale paths (2026-11-23).
- An unmerged PR written before a move or a role change goes stale
  without a conflict: read its text again before its turn (#227, #184).
- Git reads a changed file size as a change without comparing content.
  A file rewritten with other line endings stays flagged in
  `git status` with an empty diff until git records its size again
  (`git add`, `git restore`). Test a line-ending fix on a file checked
  out after the fix (#254).
- This session's guard refuses `git -C` into any other worktree of this
  repository, not only the main checkout. A claim about another
  worktree is checked in the planner's own, or recorded as the
  reporter's.
- A proof step that leaves a worktree not clean defeats closeout: check
  what each proof command leaves behind (#250, #254).
- An Action that says "replace line N" quotes what line N holds now.
  "Restarted" means the app quit fully, tray included. Leave "Undo:"
  lines out of the steps.
- Messages cross near a clear: after a peer's clear, send one message
  repeating what was owed, with links.
- A relayed answer of Ben's is confirmed before it is recorded. A
  question states its premise and the alternatives first.
- A reset prompt is stale once the session works on: keep it in a file
  and hand over a pointer, with no commit hashes.
- Plan mode stops a clear prep: put the prep in the plan.
- A merge commit takes the default author: pass the noreply email on
  `git merge` too.
- Worktrees share branch refs; only `HEAD` is per worktree.
  `/security-review` sees only commits. A worktree session can't
  `git -C` the main checkout.
- A stacked state file grows without bound: 26 blocks reached 69 KB
  (#243). Rewrite Current in place.
- dotclaude changes go by branch and PR: the guard hook refuses a push
  to its `main`. The hook checks merged PRs only in the session's own
  repo, so it refuses a local delete of a merged dotclaude branch.
