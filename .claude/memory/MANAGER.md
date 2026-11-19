# MANAGER: state-back of the builder manager session

Where the work stands, so a new session can resume from the repository
alone. Rules are in the `session-rules` skill and in
`PROJECT-RULES.md`; this file is state.

## START HERE

Written 2026-11-19 by the tools manager (session Tools-builder-manager),
its first state file, after the relaunch at the new main checkout path
(#235). `origin/main`, the main checkout and the live clone were all at
`f1ff785` on one read.

**Role in full.** PR #230 merged as `f1ff785`; "Hand-over done" is on #228
(issuecomment-7017901725). Ben invoked `session-dispatch` in this session
on 2026-11-19; it must be typed again after every clear.

**Step 7 of the #235 cutover is done for this repository**: every
`~/.claude` link points at the new main checkout path, the main
checkout's worktree list has nothing prunable, and the owner's dispatch
list names the new path (Claude's own check, 2026-11-19; record on #235).

Next, in order:

1. **#231 is dispatched**: builder `t231-reproof-lock`, session
   `8506434b-7326-4099-93ee-68c02a26c635`, branch
   `worktree-t231-reproof-lock` (issues/231 issuecomment-7024077556). Ben
   restarted the app right after; check `claude agents --json` for it.
   It parked at Part 1 (its probe script was refused); the Decision is
   in the queue. Relay Ben's answer word for word, or the planner's
   ruling on #231. If the session is gone, resume it with
   `resume_plain.ps1` on the same ticket.
2. **#236** (this file): re-prove, then ask Ben for the merge word.
3. **#233**, then **#232**, each go asked of Ben again by button.
4. The open PR line, below.
5. The Tools planner's brief for the tools path PR (#235 step 9).

## What this session answers for

As the role file `.claude/agents/tools-central-builder-manager.md`
says: dispatch, the owner's queue (`.claude/memory/NEEDS-OWNER.md` in the
main checkout), re-proof and the code review, the merge (each merge word
asked of Ben by button at the re-proved head), closeout and the closeout
pulls of the main checkout and the live clone, and this file.

## Builders running

| Builder | Ticket | Tier | Session | Stage |
|---|---|---|---|---|
| `t231-reproof-lock` | #231 | medium | `8506434b` | parked at Part 1: its probe script was refused; Decision in the queue |

## Open PRs

One re-proof and one merge at a time, each read again first. Open on
2026-11-19, number and head:

| PR | Head | Subject |
|---|---|---|
| #227 | `63c6445` | machine layout and cold setup (#223); needs the new path too |
| #222 | `f85a7b4` | one plugin source (#195) |
| #216 | `3e99496` | ruleset setup guide (#193) |
| #214 | `a6d7a6c` | resume_plain.ps1 input checks (#207) |
| #211 | `7c1bafb` | git-guardrails git name (#168) |
| #210 | `dce2100` | reset prompt is a pointer (#161) |
| #208 | `0f1e1a1` | git restore command form |
| #205 | `bb80384` | ADR-0018 threat model (#190) |
| #198 | `e7148b3` | planner state-back, clears 11 and 12 |
| #197 | `b7ef918` | owner-queue clear prep (#161) |
| #196 | `7b8f1e9` | owner-queue Answer hold (#179) |
| #184 | `05f2a7f` | one queue per project (#183) |
| #182 | `5632555` | re-proof one script, one rule (#175) |
| #181 | `148c9d1` | planner state-back, clear 10 |

Lists and needs: issues/228 issuecomment-7016915434 and
issuecomment-6900047255.

## Dispatch, as proven

- 2026-11-19, #231 dry run from the new main checkout: tier medium
  (Sonnet, effort high, turn cap 80), Profile none, builder settings with
  56 deny rules, mode `dontAsk`, plugin folder from the live clone. Apply
  refused at first: the project was not on the owner's dispatch list at
  its new path. After Ben fixed the list, a fresh dry run passed and the
  apply started the builder (setup made the worktree's `.venv`).

## Waiting on the owner (pointer to NEEDS-OWNER.md)

The queue file is empty. The owner-queue mod gave this session no queue
id after the relaunch; the Tools planner takes that to Ben.

## Queue entries raised

- 2026-11-19, Decision: #231 builder parked at Part 1, how its finding
  gets its probes (probe profile, the planner drops the tried
  requirement, or hold until #233). Recommended: the planner drops it.

## Decided since

- 2026-11-19: Ben's go for #231 after the repair
  (issues/231 issuecomment-7023959064).
- 2026-11-19: Ben chose that the Tools planner leads the move repair, not
  a queue Action.
- 2026-11-19: #231 dispatched under that go, once both its conditions
  held (issues/231 issuecomment-7024077556).

## Lessons

- Until #231's lock is live: message the dynasty manager
  (dff-central-builder-manager) before and after every full test run and
  wait for its answer. It does the same. Its re-proof of dynasty PR #617
  ended not Green from a local venv fault; it owes a re-run after the
  restart and sends a notice first.
- Peers: Tools-central-planner, dff-central-planner,
  dff-central-builder-manager. Find them with ListAgents by name; ids
  change at a relaunch.
