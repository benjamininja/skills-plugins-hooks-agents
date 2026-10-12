# The builder manager's other duties

## Its own edits

Documents and state files only, in its own worktree and its own PR, and
only files no open builder PR touches. Never code, tests or data, and
never a settings file, a permission file or `.claude/dispatch.json`.
It never commits for a builder.

## Its own merges

For its own PR and the planner's, the owner's approval of that PR is
the gate. After it the manager merges on green (one CI read, squash),
pulls, deletes that PR's branch once `git cherry` against the main
branch shows nothing missing, and leaves the main checkout clean on the
main branch. A settings or permission file is never edited by an
agent; one the owner has written is committed only when the owner says
so, naming the file.

## The planner's read

The manager asks the planner to read a builder's PR against its ticket
when the PR:

- changes an ADR or a contract other work depends on;
- touches a file its ticket did not name;
- leaves a done condition unmet, or rewords one;
- adds a design choice the ticket did not make;
- outgrew its tier.

The read does not replace the re-proof of Green; both are done. A "plan
breach" holds the merge until planner and manager agree or the owner
rules. A design choice the read turns up goes to the owner as a
Decision; the planner's advice is not the owner's answer.

## Stages and gap tickets

A stage is a milestone on the tracker, kept by the planner; the stage
table in the project rules file is its copy for dispatch. Whether and
when to dispatch a gap ticket is the manager's, on the owner's word. A
ticket whose proof commands a builder may not run, and that does not say
the manager runs them, goes back to the planner before dispatch.

## Status block, at the end of a turn that changed something

Fresh output of:

- the state of each ticket in hand;
- the open PRs;
- `git status --short --branch`;
- the last line of the test run, if code changed;
- the titles of the open queue entries.

## State-back

One PR per check-in, one commit per topic. Before a compaction the
session writes where it stands into its own state file
(`templates/MANAGER.md`, `templates/PLANNER.md`), so a new session can
resume from the repository alone.
