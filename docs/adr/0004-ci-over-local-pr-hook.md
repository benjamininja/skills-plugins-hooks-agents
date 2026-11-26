# Server-side CI is the enforcement gate; a local pre-PR hook is not a substitute

- Status: accepted; revised 2026-11-25 and 2026-11-26 (Revisions 1 and 2 below: what CI runs)
- Date: 2026-07-11
- Scope: applies to the regression-testing standard's deferred CI item, and
  generally to any future "tests must pass before merge" decision across
  repos this catalog serves

## Context

While scoping a regression-testing standard for `Python-PowerBI-
DynastyFantasyFootball` (no test framework, no CI, no pre-commit exist
there today), the question came up: instead of (or in addition to)
GitHub Actions CI, could a Claude-Code-side hook/subagent that runs a
deterministic scan before a PR is created serve as the quality gate — with
CI kept only as a redundant, rarely-needed backstop?

## Decision

CI (GitHub Actions, or equivalent server-side pipeline) is the
architecturally correct enforcement mechanism. A local pre-PR hook is a
real, legitimate *complement* (fast local feedback before pushing) but is
not a substitute, and framing CI as the rarely-firing backstop inverts
which layer is actually load-bearing.

Applied the `ponytail` YAGNI ladder to the "build a custom hook/subagent
quality gate" option specifically: it fails at "does this need to exist"
(GitHub Actions already solves this, off-the-shelf) and at "existing
dependency solves it" (building custom infrastructure to replicate what CI
does natively, with less coverage, is the smell the ladder exists to
catch).

## Alternatives rejected

- **Build a custom hook + subagent pre-PR gate, keep CI as a "just in
  case" redundancy** — the user's original proposal. Rejected because a
  Claude-Code `PreToolUse`-style hook only fires when *this agent, in this
  tool* is the one calling `gh pr create` — it does not fire for a PR
  opened from the GitHub web UI, a push from another machine/tool, or a
  follow-up commit added to an already-open PR. It also cannot block a
  merge; only GitHub branch protection + a required CI status check can.
  Building it would be more custom code for a strictly weaker guarantee
  than CI already provides for free.
- **Skip both, rely on `pre-commit` alone** — `pre-commit` (already planned:
  `check_sources.py validate`) is real and valuable, but it only runs
  locally on commit, is skippable, and never runs against code already
  pushed by another path.

## Consequences

- CI (GitHub Actions) stays logged as deferred, scoped future work for the
  Dynasty repo (which has zero `.github/workflows/` today) — this ADR
  doesn't build it, it settles *which mechanism* is correct when it's
  eventually prioritized.
- The redundancy the user wanted is already present for free: `pre-commit`
  (local, fast, this pass) + CI (server-side, real gate, deferred) is a
  legitimate two-layer defense — a third custom layer replicating CI's job
  would be over-engineering, not additional safety.
- A cheap, legitimate addition later: adopt "run the test commands +
  `pre-commit run --all-files` before calling `gh pr create`" as a
  procedural habit (or a lightweight local hook doing exactly that) — this
  is a fast-feedback nicety, not a merge gate, and doesn't need a subagent
  to "interrogate" anything.

## Revision 1 (2026-11-25): what CI runs on a pull request and on main

Ticket: tools #283, on the owner's word of 2026-11-25 (the ticket's
Amendment 2). The decision above is unchanged: CI is the gate. This revision
records what the gate runs.

- A pull request runs `pytest (ubuntu-latest)`, the whole suite, and
  `CATALOG.md is current`. No pull request waits for a Windows result.
- A push to main runs the whole suite on both systems, as before. A red
  Windows run on main is reported and fixed forward.
- Windows was about 92% of the job minutes (median 17.7 minutes against 1.2
  on Ubuntu over 25 pull requests). The cost: the tests that run only on
  Windows, and any Windows-only fault in code, are seen after a merge and not
  before it, until #187 makes the Windows run fast enough to return to pull
  requests.
- The rule is one expression in `.github/workflows/test.yml`: the matrix's
  list of systems is Ubuntu alone on a `pull_request` event and both systems
  otherwise. The check names do not change.
- A newer head on a pull request cancels the run on the older head. A run on
  main is never cancelled.

## Revision 2 (2026-11-26): Windows returns to pull requests, in six shards

Ticket: tools #187, on the owner's button of 2026-11-26, "Required, 6
shards". The decision above is unchanged: CI is the gate. This revision
replaces Revision 1's first two points; its cost paragraph is now history.

- A pull request runs `pytest (ubuntu-latest)`, `CATALOG.md is current`
  and `pytest (windows)`. All three are required by the ruleset on main.
- `pytest (windows)` is one reporting job over a scope job and six shard
  jobs that split the suite by position. Measured on 2026-11-26: 4.6 to 4.8
  minutes for the whole run at six shards, 6.5 to 8.1 at four, against 18
  to 20 for the single Windows job before, and 1.4 for Ubuntu.
- Windows is skipped only for a pull request whose changed paths all end in
  `.md` with none under `tests/`. The reporting job passes when the shards
  ran and passed, or when the scope job said skip and they were skipped;
  every other state fails it.
- A push to main runs everything, as before.
- Why it came back: about 56 tests and the hooks run only on Windows, and 2
  of 98 code pull requests failed there alone. A fault of that kind in a
  script that deletes is not undone by a revert, so it earns a gate before
  the merge at this cost.
- The project's table of checks is in `.claude/memory/PROJECT-RULES.md`.
