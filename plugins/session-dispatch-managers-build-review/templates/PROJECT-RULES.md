# PROJECT-RULES

This project's own rules for planner, builder manager and builders. The
rules that are the same in every project are in the `session-rules`
skill; this file adds to them and never loosens its "Never" lines.

## Green means all of

The proofs a PR must pass, each a command a builder may run under the
builders' settings file, or marked "manager runs it".

- every CI check passing on one read of
  `gh pr view <n> --json mergeStateStatus,statusCheckRollup`;
- `<the project's test command>`;
- `<each further check, one per line>`.

## Never, in this project

- `<a command, a source or a file this project fences off>`

## Always parks, in this project

- `<a checkpoint only the owner may pass>`

## Stages

| Stage | Tier | Tickets, in order | Waits on |
|---|---|---|---|
| A. <name> | medium | #1 then #2 | nothing |

A stage's tier is never lower than its highest ticket.

## Goal texts

One per stage, in this shape:

    /goal <what is true when the stage is done>. Met when <the proof>.
    Or stop after <N> turns.

## Notes per stage

- **A.** <what a builder must know that the tickets do not say>
