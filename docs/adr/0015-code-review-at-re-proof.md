# A code review at re-proof

- Status: accepted; revised 2026-11-11 (Revision 1 below records the
  first live run; the earlier text is kept as history)
- Date: 2026-11-09
- Scope: `plugins/session-dispatch-managers-build-review/` (`session-rules`
  `references/code-review.md`, the close out in `dispatch.md`, the
  `pr-code-reviewer` agent template, the `PROJECT-RULES.md` template);
  each repo's ruleset skill (`tools-code-review` here)
- Ticket: tools #113

## Context

No session ran a correctness review on every PR. Builders run
`security-review`, which covers security only. The manager re-proves
Green and checks scope. The domain auditors run only on their own areas.
The planner reads a PR against its ticket's design only when the manager
asks. In the month to 2026-11-09, dynasty `main` took 219 merges, 22 of
them fixes, and many of those fixed logic bugs that had passed the tests
and the re-proof: wrong step order, the wrong latest row, ids compared
before they were resolved, null keys matching null keys, readers that
depended on row order.

## The owner's answers, as tools #113 quotes them

The dynasty planner grilled the owner on 2026-11-09. The ticket quotes
these answers word for word; Q6 and Q8 to Q11 are not quoted there.

- Q1, who runs the review: "Manager at re-proof".
- Q2, which review: "code-review (Recommended)".
- Q3, how hard it looks: "Scaled by tier (Recommended)".
- Q4, which PRs: "Code PRs only (Recommended)": every builder PR that
  changes code, TMDL and DAX included. Docs-only state-backs and the
  pipeline's data PRs are skipped.
- Mid-grill: "i think it could be a ruleset put out by builder manager
  that it reviews with you, and me as well if necessary."
- Q5, the ruleset: "i was thinking like how we have builder packet we
  would have reviewer packet. the review subagent could rule with the
  builder subagent and builder manager can adjudicate with weigh-in from
  planner. we'd probably want to consider a skill to capture and update
  for this, mrp-dff-code-review that we know to use and build the ruleset
  into that you describe in recc. think critically on this and let me
  know what you think."
- Q7, which repos: "Both, own rulesets (Recommended)".
- Q12, the reviewer's form: "Manager's subagent (Recommended)",
  read-only and started at re-proof, like `cap-ledger-auditor` and
  `supabase-auditor`.
- Q13, how long the exchange runs: "One round (Recommended)".
- Q14, the skill layout: "recommended + tools-code-review". The shared
  process goes in session-rules; the per-repo ruleset skills are
  `mrp-dff-code-review` (dynasty) and `tools-code-review` (here).
- Q15, who updates a ruleset: "Manager drafts, builder lands
  (Recommended)".

Later, on Q4 for this repo, the owner answered "Yes, light review"
(issuecomment-6730815633): a builder PR that changes only rule or skill
text gets a light review at `low`, against the ruleset's text rules only.

## Decision

- **The manager starts a read-only reviewer at re-proof**, the
  `pr-code-reviewer` agent, with a packet: the full PR URL, the head sha,
  the ticket, the tier and the effort it sets, the files, the builder's
  worktree, the ruleset skill, the round and the limits.
- **The reviewer runs `code-review` at the tier's effort** and applies
  the repo's ruleset skill. Haiku and low tickets run at `low`; medium and
  high at `high`. A light review runs at `low` without code-review.
- **One round.** The builder answers each finding once (fixed at a
  commit, or disputed with a reason). A fresh reviewer re-checks each
  one. The manager decides each finding still open, with the planner's
  weigh-in on a design question; only a disagreement between them goes
  to the owner, as a Decision.
- **Green gains one item:** no blocking finding the manager upheld is
  still open. A blocking finding names its concrete trigger; advisories
  are posted and never hold a merge.
- **The reviewer returns its findings to the manager, which posts
  them.** It writes nothing at all.
- **One reviewer agent for both repos.** `~/.claude/agents` links to this
  repo's `.claude/agents/`, so the agent is available in every project;
  the packet names the repo's ruleset. Dynasty then needs only its
  ruleset skill and its Green item.
- **The process is shared, the rules are per repo.** The process is in
  `session-rules` and its `references/code-review.md`; each repo's
  patterns are in its own ruleset skill.

## Step 0: code-review inside a subagent

The manager ran code-review in a subagent of its own session on closed
PR #109 at three efforts (issuecomment-6730548975):

| Effort | Ran | Recipe it got | Own subagents | Findings |
|---|---|---|---|---|
| low | yes, with the full PR URL | low | none | 1 |
| medium | yes, twice | **high** | none | 10, then 8 |
| high | yes | high | none | 10 |

- It runs as a forked general-purpose agent, so the reviewer's `tools:`
  line may not limit it. The packet's limits bind it through its
  instructions, and the manager checks the first live run.
- The fork starts in the session's primary folder, not the caller's. A
  bare PR number resolved to another repo's issue, so the target is
  always the full PR URL.
- Two medium forks ran `git fetch` in this repo's main checkout and made
  a local branch there. So the reviewer reads only from `gh` and the
  builder's worktree, runs no fetch and no `cd`, and writes nothing.
- Medium got the high recipe both times, so medium is not used until a
  run shows it applies, and the level is always passed first.

## Alternatives rejected

- **The reviewer posts its own PR comment**, as the ticket first had it.
  A reviewer that can write a comment is not read-only; the manager
  posting keeps the line clean.
- **A reviewer agent copy per repo.** The copies would drift; the agent
  link already reaches every project.
- **An exchange of more than one round.** The owner chose one round
  (Q13); the manager decides whatever is left after it.
- **`medium` effort for medium tickets.** Step 0 showed it ran the high
  recipe; the table uses `high` until a run shows otherwise.
- **The ruleset applied by the reviewer alone, with no code-review.**
  Kept only as the fallback, for a fork that strays from the limits.

## Consequences

- Every reviewed PR's thread carries the findings, the builder's
  answers, the re-check and the manager's ruling.
- A review adds a builder turn and two reviewer runs to each reviewed
  PR's re-proof.
- The live agent file in `.claude/agents/` and this repo's Green item in
  `PROJECT-RULES.md` land in a planner PR, since builders may not write
  under `.claude/`.
- Not yet proven: a live run of the reviewer under the manager's
  settings, and whether code-review keeps to the packet's limits. The
  manager checks the first live run.

## Revision 1 (2026-11-11)

The first live run is done, so the check the Step 0 notes and the
Consequences leave pending has been made. Tickets: tools #136, #144.

- **The first live run**, on PR #121 (the manager's record is PR #121
  issuecomment-6809442189; notes on #113 issuecomment-6809450573): the
  code-review fork ran a `cd` against the limits. The reviewer's
  fallback held: it dropped the fork's output and applied the ruleset
  itself at the same effort.
- **The check is now standing** (#136, PR #143). The manager checks every
  review's output for the fallback note, and for any fetch, `cd` or
  write, and records each stray on the PR's ticket. The ruleset is read
  from `origin/main`, never from the PR branch, since a branch cut before
  the ruleset existed does not hold it.
- **Three limits added** by #136's amendment 1, from the next two live
  runs (the #121 re-check and #138's first round):
  - `diff` joins the read-only `git -C <worktree>` verbs: `show`, `log`,
    `grep`, `ls-tree` and `diff`;
  - the Skill tool loads only the ruleset skill the packet names and
    code-review, and no other skill;
  - code-review is run with the effort and the PR URL only, never
    `--comment`, `--fix` or `--post`.

The limits as they now stand are in `session-rules`
`references/code-review.md`. Dropping the code-review fork altogether
stays open for the planner if strays recur.
