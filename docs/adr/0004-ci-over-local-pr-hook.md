# Server-side CI is the enforcement gate; a local pre-PR hook is not a substitute

- Status: accepted; revised 2026-11-25 (Revision 1 below: what CI runs)
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

## Revision 1 (2026-11-25): what CI runs depends on the changed paths

Ticket: tools #283, chosen by the owner by button on 2026-11-25. The
decision above is unchanged: CI is the gate. This revision records what the
gate runs.

- A pull request whose changed paths are all `.md` files, none under a
  `tests` folder, runs three test files on the Windows job:
  `tests/test_skills_frontmatter.py`, `tests/test_agents_frontmatter.py` and
  `tests/test_adr_readme.py`. Any other pull request runs the whole suite.
- The Ubuntu job and every push to main always run the whole suite. Windows
  is about 92% of the job minutes, so the saving is there and only there.
- An empty list, an unreadable list or any error runs the whole suite.
- The rule is decided in one place, `tools/ci_scope.py`, and tested in
  `tests/test_ci_scope.py`. The `pytest` job in `.github/workflows/test.yml`
  calls it and prints the scope it took in one log line. The check names do
  not change, so every job still reports on every pull request.
- A newer head on a pull request cancels the run on the older head. A run on
  main is never cancelled.
