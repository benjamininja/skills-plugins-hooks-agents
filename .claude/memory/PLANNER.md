# PLANNER: state-back of the planner session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
[PROJECT-RULES.md](PROJECT-RULES.md); this file is state. GitHub issues are
the record. This file links to them and does not repeat them.

Last state-back: 2026-11-12, at an eighth context clear. `origin/main` was
at `f2f9061` (#158). Both tools checkouts were still at `29f77d5`: the
manager holds the closeout pulls until Rule B (#159, for #135) merges.

## START HERE

- You are **Tools-central-planner**, the standing planner for
  `benjamininja/skills-plugins-hooks-agents` (since 2026-11-07). Call the
  owner **Ben** or "the owner", and yourself **Claude**, never "you" or
  "I" for either (`session-rules`, "Asking the owner", #158).
- **Every question to Ben goes through a button**: AskUserQuestion when
  Ben is in the chat, a queue entry when not. Context, pros, cons and the
  recommendation sit above the question (`session-rules`, #158).
- Read the open issues with their `tier:` labels:
  `gh issue list -R benjamininja/skills-plugins-hooks-agents --state open`,
  and `gh pr list` for open PRs.
- **The dynasty builder manager** dispatches here, re-proves, and queues
  each Green merge for Ben as an Action: Ben runs the merges. Address it
  by app session id, `local_39e3ac7a-9d6d-4524-82e4-9b5f0e6db274`. It
  cleared at about the same time as this state-back; its reset prompt
  carries Claude's heads and gos. If it seems to miss one, re-send it
  with the PR comment link.
- **The dynasty planner** (`local_84c6f2af-95ee-4c21-9c02-95877dc0cd21`)
  plans the owner-queue mod (#111, #137, #142, #147, #153, #161).
- **Your own ids.** App session id
  `local_9830794b-c1e9-400a-ba66-e6abb9432396`. The queue id changes at
  every `/clear`. No owner-queue id line showed in the last session, and
  Ben said he would run `/owner id`; if none shows, ask again by button.
- **The owner's queue** is dynasty's `.claude/memory/NEEDS-OWNER.md`, in
  that repo's main checkout. Read it at start. Only the manager writes it.
  A planner sends the manager a ready entry. Steps that open a file use
  a command naming the exact file, plus a check that it is the right one
  (Ben, 2026-11-12: "make sure instruction is accurate in queue. i open
  what i am given.").
- **A new ticket needs Ben's go before dispatch.** Ask by button, record
  the go on the ticket, relay it to the manager word for word.
- **After every merge**, the manager pulls both checkouts at closeout
  ([PROJECT-RULES.md](PROJECT-RULES.md), "Closeout pulls"). Check the
  heads by reading each checkout's `.git/refs/heads/main` before relaying.
- **Everything on GitHub resolves on GitHub** (`session-rules`): no
  scratch, Temp or worktree path and no gitignored file in an issue, PR,
  comment, commit message or committed file. Ids are allowed as lookup
  keys.
- **The clear boundary** (`session-rules`, once #160 merges): the prep
  runs in order: close the step, record, state-back PR, memory flush,
  reset prompt last. Until #161 builds the mod's store, the reset prompt
  goes to Ben in chat.
- **Your own PRs** (state-backs, syncs, rule lines) come from the planner
  worktree whose first branch was `t112-closeout-pulls`, on a fresh branch
  from `origin/main`. Enter it with `EnterWorktree` (path). In it, run
  one plain git command per call. Push with the branch named
  (`git push origin <branch>`). Commit with
  `git -c user.email=38588919+benjamininja@users.noreply.github.com commit -F <file>`.
  Run `/security-review` on the committed diff before opening the PR.
  When the manager asks Claude to bring a PR up to date, merge
  `origin/main` into it, check the diff against main is unchanged, push,
  and ask Ben to approve the new head.
- **Run pytest with the dynasty venv** (neither tools checkout has a
  `.venv`). The full suite takes about 15 minutes; run it in the
  background. `tools/build_catalog.py` leaves a line-ending-only change to
  `CATALOG.md` here; check with `git diff --ignore-cr-at-eol` and drop it.

## Do first after this clear

1. **This state-back's PR** needs Ben's approval, by button. Read its
   comments first. Relay the approval to the manager word for word.
2. **Watch the re-proof line**, in the manager's order: #160 (`48acd7b`),
   #165 (`f546113`), #166 (`813aa7a`), then #163 (after the dynasty
   planner confirms its three CLI behaviours). #162 is Green; its merge
   is queued for Ben. All four planner PRs carry Ben's approval on the
   PR. If the manager asks for an update, merge `origin/main` in and
   ask Ben again.
3. **#159 (Rule B for #135)** waits on its builder's F1 fix (review:
   PR #159 issuecomment-6828816366). When it merges: the manager runs
   the held closeout pulls; check both heads; then #168 dispatches (Ben's
   go is on #168).
4. **#167** (medium): Ben's go is recorded; the manager dispatches it. Its
   builder reports the smallest fix on #167 before it builds.
5. **#168** (high): its builder posts a fail-closed design on #168; put
   it to Ben by button before the build.
6. **After #165 merges and the pull:** reviews no longer use the
   code-review fork. Watch the first review for the closing line on the
   reviewer's own calls.
7. **Baseball handoff**: bump it for #158's and #160's carried-over rules
   once both merge (Gaps, below).

## What this session answers for

- Tickets, tiers, `Profile:` lines and briefs for this repository.
- Rulings on builder PRs when the manager asks ("no breach" or "plan
  breach", scope questions, design questions that aren't Ben's).
- Gaps found in the session-dispatch plugin and in this repo.
- This repo's `PROJECT-RULES.md`, and the session-rules side of #148.
- The baseball handoff doc.

**Not the owner-queue mod.** The dynasty planner plans it, including
#153's CLI behaviours and #161.

Not building, not dispatching, and never a settings file or
`.claude/dispatch.json`.

## Open PRs and in-flight work

- **PR #160** (#148, planner): a role session's clear boundary and reset
  prompt. Approved at `48acd7b` (`origin/main` merged in after #158).
- **PR #165** (#164, planner): drops the code-review fork; ADR-0015
  Revision 2. Approved at `f546113`; supersedes the rewording approved
  at `03e1bac`.
- **PR #166** (planner): an `Answer:` line leaves only with its whole
  entry. Approved at `813aa7a`. After it merges, the manager aligns the
  live queue file's header.
- **PR #159** (#135, Rule B): F1 back with the builder. Ben's ruling:
  "Keep #135; fix F1 here (Recommended)".
- **PR #162** (#155): Green; merge queued for Ben.
- **PR #163** (#153, the dynasty planner's): review round closed; re-proof
  waits on that planner's confirmation of three CLI behaviours.
- **#161** (high, the dynasty planner's): the mod side of #148. Its first
  step checks what the mod host can measure; if the write route changes
  from whole-file replace, the dynasty planner tells Claude.
- **#167** (medium) and **#168** (high): gos recorded; see Do first.
- **#147** (medium), **#137** (medium), **#142** (low), **#111**:
  owner-queue, the dynasty planner's.
- **#112**: open, tier none. Nothing is left for this session on it.

## Waiting on Ben

- Approve this state-back.
- Merges as they turn Green: #162 now; #160, #165, #166, #163, #159.
- Dynasty PR #531 (ADR-0001 amendment, ~255K ceiling).
- `/owner id` in this session.
- #168's design, when its builder posts it.
- #48's owner-led steps (below).

## Queue entries raised

- The corrected "Add the git merge allow rule to the TOOLS builders'
  settings" Action (#135), sent to the manager 2026-11-12; Ben added the
  line, and the manager reported it done.

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
- 2026-11-12: state-backs (#145 `af86414`, #156 `b493243`); the live
  reviewer synced (#146 `33722aa`); #140 merged at Rule A (`d75b4fb`);
  everything on GitHub resolves on GitHub (#151 `5a29cd6`; #149 closed
  after a clean sweep); ADR-0015 Revision 1 (#150 `b032aec`); the resume
  helper (#157 `85021b8`); questions by button and the naming rule
  (#158 `f2f9061`).

## Gaps

- **#48:** builders are denied edits to `.claude/agents/`, so agent changes
  are owner-led planner PRs (as #128, #130, #146 and #165 are).
- **The baseball handoff**
  ([docs/handoff/baseball-session-dispatch.md](../../docs/handoff/baseball-session-dispatch.md))
  is for SpunkyLlama's agent. Update it when the owner-queue version, the
  session-dispatch version, template commits or carried-over rules change.
  #151, #158 and #160 add carried-over rules, and #165 changes the
  reviewer: bump it after they merge.
- **`CLAUDE.md` is out of date** in two places: its CI sentence and "Three
  agents live in `.claude/agents/`". Small; no ticket yet.
- **#140 F11:** a `-C` path is final even when it can't be resolved. No
  ticket yet; fold it into #168 if its builder touches that code.

## Decided since

Ben's decisions, each recorded on its ticket or PR. Earlier ones are in git
history of this file.

- *Approve 158*, *Approve 160* (then *at 48acd7b*), *Approve 165* (then
  *at f546113*), *Approve 166* (2026-11-12).
- #149: *Close #149*. #155: *Go: dispatch #155*. #167: *Go: dispatch
  #167*. #168: *Go after #159*.
- #148: *Approve as drafted*; ADR-0001: *Amend: add ceiling* (dynasty
  #531).
- #164: *Reword limits, low*, then *Drop the fork*, *Go as planned*.
- #135: *Keep #135; fix F1 here* (relayed by the manager).

## Lessons

- Address sessions by app id; check the checkouts before relaying a
  manager's claim about them.
- Before asking for an approval, read the PR's comments: an approval
  given before a clear is recorded there.
- A manager that resumes may miss a relay. Re-send it with the PR comment
  link.
- **An approval covers one head.** A merge of `origin/main` or a later
  ruling makes a new head; ask Ben again (#160, #165).
- **Check `origin/main` before naming a merge commit.**
- **A safety hook loosened by a list of forms to catch gets bypassed one
  form at a time.** Start from an allowlist (#140, Rule B, #168).
- **A limit text has to read right to the tool it is handed** (#143 F1;
  #164: limits that name a flag make code-review report it as passed).
- **A general-purpose fork can't be held by wording or a `tools:` line**
  (#165).
- **`gh issue create --label` can leave a ticket unlabelled.** Check the
  labels in `gh issue list` after filing (#167, #168).
- **Check a claim about a file before relaying it.** Claude told Ben his
  paste went into the wrong file; the manager showed the line was there
  before. Say what is in the file, not how it got there.
- Worktrees share branch refs; only `HEAD` is per worktree.
- `/security-review` sees only commits. Commit first.
- A script run as one Bash call hides its inner commands from the
  permission rules (#117).
- A worktree session can't `git -C` the main checkout. Read each
  checkout's `.git/refs/heads/main` instead.
