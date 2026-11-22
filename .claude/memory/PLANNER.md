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

Last state-back: 2026-11-22, after the compact: the #243 root split
merged. dff-central-builder-manager has not
yet reported its own memory review (#243); nothing is owed to it.

## Current

**Ids (queue ids change at every clear).** This planner:
`019c4c0b-d63a-4262-9ee1-558f1408fd4f`. Tools-builder-manager:
`55edaa09-855e-454f-991a-371eb4875402`. dff-central-builder-manager:
`1a0538b1-047b-4ba3-8967-ff325369e7ab`. dff-central-planner:
`65cb1676-fc95-4abf-8174-422c03a5f64e`. Neither queue holds an entry for
this planner. Two dynasty entries (#548) still carry dff-central-planner's
old id `5e9a5f7b-…`; that planner has been told.

**Merge line (Tools-builder-manager, one re-proof at a time, each merge
word asked of Ben by button):** #236, PR #238 (the planner's), #239
(#237), #242 (#231). #241 follows #239. Nothing has merged since
`f1ff785` (2026-11-19).
- **#244 goes first** (medium, `Profile: none`; Ben's "Go, first
  (Recommended)", 2026-11-22; brief: issues/244
  issuecomment-7082663876). Dispatched as builder `t244-pytest-hang`
  (issuecomment-7083733874). #236's re-proof timed out in pytest at 3600s
  twice (`7b5b408`, `629074b`), while Windows CI passes in 17–19 min.
  Every tools re-proof is held until #244's Part 1 finding. Rule on it
  when it comes; it feeds #187.
- #242: the re-check accepted F1 and F2 at `b278602`. It needs only its
  re-proof.

**Next for this planner, in order:**
1. **After #242 merges:** the planner's PR that replaces PROJECT-RULES'
   one-run message rule with the lock.
2. **#233's finding** when it comes: rule on it. Send the link to
   dff-central-planner, which files the dynasty follow-up.
3. **#243, the memory review: the root split is done.** dotclaude PR #9
   merged as `cfba40f` on Ben's buttons (issues/243
   issuecomment-7084451575). Dynasty's stale descriptions of root are
   dynasty #637. Left here: (a) one planner PR for this repo's stale
   OneDrive paths (`README.md` 86-87, `PROJECT-RULES.md` 101 and 112,
   `tools/relink_live.ps1` 27-28, `hooks/root-memory-propagation/README.md`
   53), list in issuecomment-7083787493; (b) #245 (low), the propagation
   registry's dead path, which needs Ben's go before dispatch. Peers:
   Tools-builder-manager trims `MANAGER.md` after #236 merges;
   personal-assistant's points are on #218 (issuecomment-7082200407).
   The local dotclaude branch `memory/root-split-243` is merged content;
   the guard hook refuses its delete from here, so it is left.
4. **Dispatchable after the merge line** (sent to Tools-builder-manager,
   gos recorded): #189, #219. #232 follows #189's PR; #220 follows
   #219's first finding (go recorded, brief then); #218 follows the #217
   rules PR, which follows PR #210; #226 follows PR #197.
5. **#235 remainders:** step 3's prune of merged worktrees (the manager's,
   on Ben's word), then step 11 (Ben removes the old folder).

**Open planner PRs** (each needs `origin/main` merged in and Ben's
approval at its new head when its turn comes; an approval covers one
head): #181 and #198 (old state-backs, likely to be closed instead), #184
(#183, queue per project, ADR-0016), #205 (ADR-0018), #208 (`git restore`
form), #210 (reset prompt as pointer, one Current block), #216 (ruleset
setup), #222 (#195 docs), #227 (#223 setup doc), #238.

**Open builder PRs:** #182 (#175), #196 (#179), #197 (#161), #211 (#168),
#214 (#207), #239, #242. #196 and #197 are planned by
dff-central-planner.

**Planned, not opened:** the `session-rules` PR for #217's choices 1, 2
and 4 with 245,000 (after PR #210; its text: #217
issuecomment-6896675395, #161 issuecomment-6895988934); #212's PR
(after #210 and #184); the baseball handoff bump (after #180, #184,
#205, #208, #210 and #212 merge).

**Dispatch line on recorded gos, after the above:** #206; #167; #187;
#192 (first PR: checks 1, 2, 3, 7); #176 after #50; #200 after #168
merges; #213 after #200; #215 after #213 (the hook lane, one writer at a
time); #203 and #191 after PR #205 (#191 only on the planner's word);
#201 after #191. Vendor lane: #50, then #176, then #57, then #52, then
#55. #47 runs alone (not beside #54). #51, #53 and #54 after #48.

**Findings to rule on when posted:** #189, #187, #192, #191 (a real fork
goes to Ben by button), #233. #200's design goes to Ben by button.

**Coming to Ben later (not waiting yet):**
- The approvals of the open planner PRs above, each at its turn.
- The `session-rules` PR for #217, then the Action for the assistant's
  state branch.
- The write half of #204's test, after #206 merges.
- #209's go, after #210 merges and dynasty's state files are in the new
  shape.
- The Action to remove the mod's old hand copy (#195).
- The merge of the private configuration repository's working branch.
- #245's go (low), and the planner PR for the stale OneDrive paths.

**Owed to Tools-builder-manager** (its session was not running at
2026-11-22's send): #245's go (issuecomment-7084478611, dispatch after
the line), and the note that #243's root split merged (dotclaude #9).

**Waiting on Ben:** nothing.

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
- Not the owner-queue mod (dff-central-planner plans it). Never builds,
  never dispatches, never writes a settings file or `.claude/dispatch.json`.
- **Peers** (address by name from ListAgents): Tools-builder-manager
  (dispatches, re-proves, merges and writes this repo's queue);
  dff-central-builder-manager and dff-central-planner (dynasty);
  personal-assistant (reports only, never Ben's approval);
  supabase-consultant-dispatch.

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
  in PR #205. The next free number is 0019.
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
