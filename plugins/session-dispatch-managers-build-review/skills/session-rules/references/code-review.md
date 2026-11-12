# The code review at re-proof

The manager starts a read-only reviewer on a builder's PR before it
posts the re-proof. The reviewer finds, the builder answers once, a
fresh reviewer re-checks, and the manager decides. The reviewer is the
`pr-code-reviewer` agent (`templates/agents/pr-code-reviewer.md` in this
plugin). Each repo has its own ruleset skill, which the packet names.
Why it is built this way: tools ADR-0015.

## Which PRs

| PR | Review |
|---|---|
| A builder PR that touches a path the ruleset counts as code | Full, at the tier's effort. Rule and skill text inside it is checked too, against the rules the ruleset names for text. |
| A builder PR that changes only rule or skill text | Light, if the ruleset asks for one; otherwise none. |
| A planner or manager PR, a state-back, a sync, a data PR the ruleset skips | None. |

## Effort

| Ticket tier | Full review | Light review |
|---|---|---|
| haiku | `low` | `low` |
| low | `low` | `low` |
| medium | `high` | `low` |
| high | `high` | `low` |

- `medium` is not used until a run shows code-review applies it. In
  tools #113's Step 0 (issuecomment-6730548975) it ran the `high` recipe.
- The level is always passed first, before the target:
  `code-review <level> <full PR URL>`. Without it, code-review reuses the
  last level typed.
- A light review checks the diff only against the rules the ruleset
  names for it, at `low`, and does not run code-review.

## The packet

The manager writes one for each review, and the reviewer sees only the
packet, never the builder's reasoning.

- **PR:** the full PR URL, never a bare number. The code-review fork
  starts in the session's primary folder, where a bare number can
  resolve to another repo's issue.
- **Head:** the PR's head commit sha.
- **Ticket:** the full issue URL.
- **Tier**, and the **kind** (full or light) and **effort** it sets.
- **Files:** the files the PR changes.
- **Worktree:** the builder's worktree, which is at the PR's head during
  re-proof.
- **Ruleset:** the repo's ruleset skill, by name, and its path in the
  repo (for example `skills/tools-code-review`). It is read from
  `origin/main`, never from the PR branch.
- **Round:** first, or re-check. A re-check also carries the first
  findings, the builder's answer to each and the new head.
- **Returns:** the findings, as below. Nothing else is posted or written.
- **Limits**, copied into every packet. They bind the code-review fork
  too, because that fork is a general-purpose agent the reviewer's
  `tools:` line may not limit:
  - read with `gh pr view` and `gh pr diff` on the PR URL; with
    `git -C <worktree>` for `show`, `log`, `grep`, `ls-tree` and `diff`;
    and with Read, Grep and Glob in the worktree;
  - the Skill tool loads only the ruleset skill the packet names and
    code-review, and no other skill;
  - code-review is run with the effort and the PR URL only, never
    `--comment`, `--fix` or `--post`;
  - no `git fetch`, no `cd` into any checkout, no script and no test;
  - no write of any kind: no file, ref, branch, comment, commit or push.

If the fork strays from the limits, the reviewer drops code-review and
applies the ruleset itself at the same effort. The manager checks every
review's output for the fallback note, and for any fetch, `cd` or write,
and records each stray on the PR's ticket.

## A finding

Each finding has an id (`F1`, `F2`…), the file and line, the ruleset
pattern it falls under (or `code-review` for one outside the ruleset),
its class, and one sentence on the defect.

- **Blocking** names the concrete input or state that triggers it. A
  finding of a blocking class with no concrete trigger is advisory.
- **Advisory** is everything else the ruleset names. Advisories are
  posted and never hold a merge.
- **Not a finding:** style, anything CI already gates, and design the
  ticket settled.

The ruleset says which patterns are blocking in its repo.

## The round, once

1. **The review.** The reviewer returns its findings to the manager. The
   manager posts them on the PR as one comment, and tells the builder.
   No findings: the manager says so on the PR, and the round is over.
2. **The builder's answer**, once, as one comment on the PR, one line per
   finding: `F1 fixed at <sha>`, or `F1 disputed: <reason>`. It pushes
   its fixes, then messages the manager.
3. **The re-check.** A fresh reviewer, never the first one, gets the
   packet, the findings, the answers and the new head. For each finding
   it returns `accepted` (the fix holds, or the dispute does) or `still
   open`, with one sentence. It re-checks those findings only.
4. **The manager's ruling** on each finding still open: upheld or
   closed. On a design question it asks the planner to weigh in first.
   If they disagree, it goes to the owner as a Decision.

There is no second round. A blocking finding upheld after the round
sends the PR back, as a PR that is not green does.

## How the manager records it

One comment on the PR, before the re-proof, with one row per finding:

| Finding | Class | Builder | Re-check | Ruling | Why |
|---|---|---|---|---|---|

- The ruling is `upheld` or `closed`. A planner weigh-in or an owner
  Decision is linked in its row.
- Advisories still open are listed again in the re-proof comment. A
  merge with advisories open is allowed.
- The deferred advisories the manager and builder agree on go in one
  ticket per PR, `Tier: unset`. A disputed advisory is closed or kept by
  the manager's ruling, with no ticket.

**The Green item:** no blocking finding the manager upheld is still
open.

## Updating a ruleset

When a fix PR lands for a bug a review missed, the manager drafts a
ruleset line from it and the planner reads it. A low-tier builder lands
the read lines in batches, and the manager merges. A repo's project
rules file may add its own promotion rule.
