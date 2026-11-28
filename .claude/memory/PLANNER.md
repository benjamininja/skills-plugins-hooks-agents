# PLANNER: state of the Tools planner

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record; this file links to them and does not repeat them.

**Shape (Ben, 2026-11-22, #243: "One Current block").** One Current block,
then Reference. Each state-back rewrites Current in place. Older state is
in this file's git history:
`git log -p origin/state/tools-central-planner -- .claude/memory/PLANNER.md`.
The last stacked version, with 26 session blocks, is that branch's commit
before the #243 rewrite.

Last state-back: 2026-11-28, before the second compact of the day that
Ben asked for. Compacts since the clear of 2026-11-27: 2 once it is
done. A clear gives this planner a new queue id: send it to the four
peers.

## Current

### Saved

2026-11-28, before the second compact Ben asked for that day. Session
0a6ad927-943a-481d-99fc-f2cbfcda8498, known to the four peers (a
compact keeps it). Compacts since the clear of 2026-11-27: 2 once this
compact is done. No background task runs. Nothing waits on Ben in the
planner's chat. This block is whole: older blocks are in this file's
git history.

### Next

1. **#307** (low; board.py's cp1252 crash, plus part A `--owner @me`
   and part B `--boards-only`, issues/307 issuecomment-7240559476). No
   PR is open yet; the manager tells the planner when its PR merges.
   Then: send the manager a ready Action for Ben to re-run the D rows
   with `--boards-only` on board 2, with this session's id. **#285**
   closes when D1 passes. If D1 still fails it comes back to the
   planner; the next option is the script's own query, not `read:org`.
2. **#317** (low, gate text): dispatched on Ben's go as `t317-msgrules`
   (the manager's report). Its head goes to the dynasty planner; it
   keeps Ben's merge word. Two weeks after it merges: one
   `usage.py tags` run on Ben's word, compared on #317.
3. **#319** (PR #320) and **#307** (PR #321) are under review (the
   manager's report). The ticket from PR #304's finding F1 is filed,
   low, held behind #240 step 2 (`t240-rekey`); lift the label and the
   `Held:` line when that PR merges.
4. **The trial line** (PR #309, merged): low and haiku dispatch
   without a go from 2026-11-28 to 2026-12-12. By 2026-12-12 the
   planner posts the manager's count on #300 and asks Ben by button
   whether it becomes standing, runs again or ends.
5. Reads and rulings as they post: #289 step 1; #295's design (parks
   with Ben); any head the manager asks for.
6. **#262:** the rule-text build is the manager's on Ben's go; the mod
   half's brief is owed after #240 step 2 merges.
7. **#111** (the Ask planner button): all five questions ruled; the
   build brief is owed after #240 step 2 merges and after #262's mod
   half. Ben on 2026-11-28: keep the order, it was a check that it is
   not lost.
8. The draft advisory GHSA-27j5-qx96-v8w3: the dynasty planner's
   pointer is dynasty #564 issuecomment-7239843007; no date yet. Tell
   it when PR #211 merges and when #295's design is approved. No
   detail of an open gap goes on any public record.
9. **#323** (owner-led): the wave manager, trialed in Dugout Standard
   first (Ben's button there and his word here). Length by Ben's
   button "10 merged PRs (Recommended)": the first 10 merged builder
   PRs in Dugout Standard, or 2026-12-31 if sooner. Then one
   `usage.py` run on Ben's word, the figures on #323 and a button:
   rule for all, again, or end. The Dugout session answers the
   ticket's eight points for the trial.
10. The older list: #217 C to F, the assistant's owner-queue text PR,
   the ADR index sentence, #167.

### Waiting

- On Ben, in the manager's chat: the go for #317, for #262's rule-text
  build and for every medium or high dispatch.
- On Ben, in the queue: nothing raised by this session is open.
- On the manager: the builders for #307 and #319, PR #318 (#298, to
  merge main and take plugin version 0.6.4), PR #304 (#293), then
  #240 step 2.
- In the hook lane: PR #211, then #295, then #289 step 2, then #200.
  In the owner-queue lane: PR #304, #240 step 2, #262's mod half,
  #111. The repair of PR #182 follows PR #318.
- The dynasty planner was told of the `oneshot` hand step on
  2026-11-28; the send noted a new session under that name, so its id
  below may be stale until it sends its own.
- A report went to the Dugout Standard session on how context is
  saved here (Dugout-Standard-App issue 49); nothing is owed.

### Peers

Ids of 2026-11-28. Tools-builder-manager
ea58e038-9092-4552-9e4c-32bb3cdf8281; dff-central-planner
0ef68551-3dad-4f09-b5af-b164a0307ae9; dff-central-builder-manager
637314ca-f6ae-4049-a3ff-576bd1479cfe; personal-assistant
061c1d24-09c1-4c01-8d89-ff693eb974d9.

### Reads and checks due

- 2026-12-31 or Dugout Standard's tenth merged builder PR: the wave
  manager's figures on #323 and the button to Ben.
- 2026-12-12: the trial's count on #300 and the button to Ben.
- Two weeks after #317 merges: the `usage.py tags` re-run.
- The planner's worktrees `t300-rule-texts`, `t294-start-lines`,
  `t300-never-line`, `t300-trial-line`, `t262-row1l` and
  `t285-role-line` hold merged branches. Removing them is the
  manager's closeout or Ben's word, not the planner's own step.

### Decided since the last merged state PR

All on 2026-11-28, by Ben's button unless said.

- The cut is reversed and #300 is whole: "Reverse all, #300 whole
  (Recommended)" (issues/300 issuecomment-7239515907).
- One PR for both rule texts: "One PR for both (Recommended)"; PR
  #303, merged `25aef1a`, plugin 0.6.2.
- #294 written by the planner: "Tools planner (Recommended)", in the
  manager's chat (issues/294 issuecomment-7239883980); PR #305, merged
  `805aab5`.
- #299: "Add oneshot profile (Recommended)" (issues/299
  issuecomment-7240005690). The catalog check gets no builder allow
  rule: Ben's pane answer (a) (issues/299 issuecomment-7240505050).
- The trial line and the hold mark: "Label plus Held line
  (Recommended)" (issues/300 issuecomment-7240118647); PR #309, merged
  `d1b920c`.
- #263: "Both rules (Recommended)" (issues/263
  issuecomment-7240534221); #317 filed.
- The deny rules reach the planner's session (issues/300
  issuecomment-7239984512).
- #323 filed; Ben typed: great call on trialing dugout standard,
  first (recorded on #323).
- Merged on Ben's word: PR #318 `ed3a569` (#298), PR #304 `148b48e`
  (#293). #240 step 2 is dispatched.
- Merged, builders': PR #313 `f88d633` (the `oneshot` profile, on Ben's
  button), PR #316 `13481f0` (#312). Holds lifted on #317 and #319.
- Merged, the planner's own: PR #302 `0105706`, PR #310 `3eba79a`
  (#262 row 1l), PR #311 `347188b` (#285 disposition 4). Builders':
  PR #306 `7385794`, PR #308 `189093c`.
- Planner rulings: #285's plan read (issues/285
  issuecomment-7239802406); #262's re-read (issues/262
  issuecomment-7239858390); PR #313's read and edits; the D1 failure
  onto #307.

### Rules in force that a new reader needs first

- Merging on Green covers only a builder's PR whose paths are all
  under `tools/`, `tests/`, `docs/` outside `docs/adr/`, or the
  catalog files. Every other PR keeps Ben's merge word, given in the
  manager's chat; the planner merges only a PR Ben names to it.
- The dynasty planner leads and signs off every shared gate text; a
  read holds for one head.
- A brief names no file under `.claude/`: those are the planner's own
  PRs. A brief holds no double quote.
- A held ticket carries the `held` label and a `Held:` line; only the
  planner or Ben sets or removes them.
- State is pushed from the local branch `docs/planner-state-1114c` in
  the worktree `t112-closeout-pulls`:
  `git push origin docs/planner-state-1114c:state/tools-central-planner`,
  confirmed with `git ls-remote`.

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
