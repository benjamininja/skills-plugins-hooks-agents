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

Last state-back: 2026-11-24, at the start after the clear of
2026-11-23. All four role sessions cleared and restarted; their new
queue ids are below. Nothing has merged since `aefbc68` (PR #246,
2026-11-23). The planner checked PR #252 against the second amendment
and sent both owed items to Tools-builder-manager again; it answered
both. dff-central-builder-manager has not yet reported its own memory
review (#243); nothing is owed to it.

## Current

**Ids (queue ids change at every clear).** This planner:
`2f55ae6a-00e1-46b6-9f89-e3d2d939e0de` since the clear of 2026-11-23
(before it: `6b47c44d-e4cb-43be-8d0a-51ec2776881b`), sent to the three
peers on 2026-11-24. Each peer's id is from its own message of
2026-11-24. Tools-builder-manager:
`5074d20f-d5f6-4edf-b1b1-e18d5f31db19`. dff-central-builder-manager:
`695f05fc-6dff-445b-a9fd-af605c6997d9` (before:
`aa75bef2-1167-49fd-995a-bdee72226d36`, which its two entries in the
dynasty queue still named on 2026-11-24; the re-key is its own).
dff-central-planner: `cff0e612-f08d-401c-9bb6-2a60446c1492`. Neither
queue holds an entry for this planner; the tools queue is empty.

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
- **PR #253** (#248, builder t248) is open at `b958ffa`; its code review
  is closed with no blocking finding (record: pull/253
  issuecomment-7104501918). It adds `tests/test_adr_readme.py`: every
  file in `docs/adr/` needs a row in `docs/adr/README.md`, linked in the
  row's first cell. **After #253 merges, the planner merges main into
  #184, #205 and #249 and adds each ADR's row**; #211 (ADR-0017) is a
  builder PR and needs a follow-up to its builder. The README's roles
  row says PR #249 replaces the dispatch role file with
  `supabase-router` and updates the row (F2). That is not yet true of
  #249; the planner makes it true when #249 merges main in.

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
0. **Awaited:** PR #252's new head from builder t250. If the manager
   asks, read it against points 16 to 22. Tell dff-central-planner when PR #249
   merges (dynasty PR #653 goes ready then).
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
- **First: #137 with #111 and auto-close, one design.** Nothing was
  drafted by dff-central-planner and it holds no answer of Ben's. The
  tools-side notes are at #137 issuecomment-7132602474. The design goes
  to Ben by button: auto-close in the file or only in the pane (advice:
  pane only), one button or two, the order against PRs #197 and #196.
  Then the brief, tier and Ben's go, sent to the manager. ADR 0014 is
  held for it. The rule text (`parking.md`, the queue template, #111's
  comment rule) is one planner PR beside the mod PR.
- **Constraints from dynasty** (the handoff): the manager is the queue
  file's only writer and records every Note and Answer before the CLI
  removes an entry; a message keeps the question, the answer and a
  `Time:` line; nothing acts on an entry mid re-key. dff-central-planner
  wants one line when the pane's behaviour changes.
- **The lane's other open tickets, not yet read by this planner:** #240,
  #234, #229, #226, #225, #202, #188, #185, #179 (PR #196), #161
  (PR #197), #147, #142, #195.

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

**Waiting on Ben:** nothing from this planner. No button is pending.

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
