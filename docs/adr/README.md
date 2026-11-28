# Architecture decision records

One file per decision, named `NNNN-short-title.md`. This index lists every
merged ADR. A row is added in the same PR that adds the ADR
(`tests/test_adr_readme.py` fails when a file has no row).

## Index

| No. | Title | Status | Date | Revised or superseded by |
|---|---|---|---|---|
| [0001](0001-vendor-cache-fork-pattern.md) | Forked skills get a pristine mirror in `vendor-cache/` | accepted | 2026-07-11 | none |
| [0002](0002-plugin-manifests-only.md) | Large unused plugin bundles get manifest-only cataloging | accepted | 2026-07-11 | none |
| [0003](0003-junction-vs-symlink-fallback.md) | Directory junctions as the practical Windows install mechanism | accepted | 2026-07-11 | none |
| [0004](0004-ci-over-local-pr-hook.md) | Server-side CI is the enforcement gate | accepted, revised | 2026-07-11 | Revision 1 (2026-11-25); Revision 2 (2026-11-26) |
| [0005](0005-skill-routing-and-drift-detection.md) | Skill routing nudges, junction drift detection, bootstrap skill | accepted, partly superseded | 2026-07-12 | 0006 (for five router skills) |
| [0006](0006-blast-radius-tiered-model-invocation.md) | Blast-radius-tiered model invocation | accepted, revised | 2026-07-17 | Revision 1 (2026-11-14); Revision 2 (2026-11-23) |
| [0007](0007-first-subagents-vendor-sync-and-safety-audit.md) | First subagents: vendor sync and safety audit | accepted | 2026-07-17 | none |
| [0008](0008-plan-gate-sync-auditor.md) | plan-gate-sync-auditor | superseded, no successor | 2026-07-17 | retired 2026-10-12; recorded in 0011 Revision 2 |
| [0009](0009-security-review-at-pr-time.md) | `/security-review` before opening a PR | accepted | 2026-07-17 | Amendment (2026-07-17); the Status line does not mention it |
| [0010](0010-root-memory-propagation-audit.md) | Root-memory propagation check | accepted | 2026-07-18 | none |
| [0011](0011-unified-distribution-architecture.md) | Unified bidirectional distribution architecture | revised | 2026-07-18 | Revision, Revision 2, Revision 3 (current, 2026-11-11) |
| [0012](0012-retire-continual-learning.md) | Retire the continual-learning hook | accepted, revised | 2026-10-12 | Revision 1 (2026-11-23) |
| [0013](0013-session-dispatch-plugin.md) | A plugin for dispatching builder sessions | accepted, amended, revised | 2026-10-12 | Amendment (2026-11-07); Revision 1 (2026-11-23) |
| 0014 | unused | none | none | The number was never used. There is no file. |
| [0015](0015-code-review-at-re-proof.md) | A code review at re-proof | accepted, revised | 2026-11-09 | Revision 1 (2026-11-11); Revision 2 (2026-11-12, current: it reverses the original decision in place, before the reversal rule below) |
| [0016](0016-one-owner-queue-per-project.md) | One owner queue per project, untracked, routed by the ticket's repo | accepted | 2026-11-14 | none (brought up to date on 2026-11-23, before it merged) |
| [0017](0017-git-guardrails-reads-like-the-shell.md) | git-guardrails reads commands by the shell's rules, and tries what it can't read as git | proposed | 2026-11-14 | none |
| [0018](0018-threat-model-for-role-sessions.md) | A threat model for role sessions | accepted | 2026-11-14 | none |
| [0019](0019-on-call-subagents-for-niche-roles.md) | On-call subagents for niche roles | accepted | 2026-11-23 | none |
| [0020](0020-builder-environment-lifetime.md) | A builder's environment: light at dispatch, removed at closeout by one script | accepted | 2026-11-23 | none |

An ADR on an open pull request (0016, 0017, 0018, 0020) adds its own row in that
pull request, so `tests/test_adr_readme.py` passes on the merged tree.

## How a decision changes

- **A correction or refinement** goes in the same file, as a dated
  `## Revision N (YYYY-MM-DD)` section at the end. The old text is never
  rewritten: it is history, and the section says what is now current. Update
  the file's `Status` line to point at it.
- **A reversal** of a decision, from 2026-11-23, is a new ADR. The old ADR's
  status becomes `superseded by NNNN`, and the new one names what it
  replaces. Earlier changes stand as they were made (ADR-0015 Revision 2).
- **"Amendment"** (ADR-0009, ADR-0013) means the same as "Revision". Those
  headings stay as they are; new changes use "Revision".
- The tickets that decided a change go on a `Ticket:` or `Tickets:` line.

## Roles and their record

Each agent file in `.claude/agents/`, with the record of its decision.

| Agent file | Decided by |
|---|---|
| `vendor-sync-reapply` | ADR-0007 |
| `skill-safety-auditor` | ADR-0007 |
| `root-memory-propagation-auditor` | ADR-0010 |
| `pr-code-reviewer` | ADR-0015 |
| `stage-builder` | ADR-0013 (the builder role); no ADR of its own |
| `tools-central-builder-manager` | ADR-0013 (the manager role), set up by the owner's answers on tools #228 (PR #230); no ADR of its own |
| `supabase-router` | ADR-0019 (it replaces `supabase-consultant-dispatch`, which has no agent file now) |
| `supabase-consultant` | ADR-0019 |

`plan-gate-sync-auditor` (ADR-0008) is retired and has no agent file.
