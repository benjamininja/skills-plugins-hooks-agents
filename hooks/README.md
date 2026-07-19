# hooks/

Reserved for standalone Claude Code hooks (event-triggered shell commands
configured via `settings.json`) that belong to this central repo.

## `continual-learning` — ported, installed, and active

[`continual-learning/`](continual-learning/) is a Claude Code port of
[microsoft/skills](https://github.com/microsoft/skills)'
[`hooks/continual-learning`](https://github.com/microsoft/skills/tree/main/hooks/continual-learning)
(built for GitHub Copilot CLI's hook format — ported, not copied, onto
Claude Code's actual `settings.json`/`SessionStart`/`PostToolUse`/
`PostToolUseFailure`/`SessionEnd` event system). SQLite-backed, two-tier
scope (global `~/.claude/learnings.db` for cross-project tool patterns,
local `<repo>/.claude/learnings.db` per repo) — surfaces prior learnings at
session start, logs tool outcomes silently, detects repeated tool-failure
patterns and decays stale/low-value learnings at session end (60-day TTL,
low hit count). **Installed and verified live on this machine (2026-07-12)**
— `sqlite3`/`jq` on `PATH` via winget, hooks merged into
`~/.claude/settings.json`, confirmed writing real `tool_log` rows from
harness-fired events. See its own README for install steps, the full list
of what changed porting from Copilot CLI's format, and known limitations
inherited from upstream (failure-pattern grouping is tool-name-only; the
`mistake`/`preference`/`pattern` learning categories have no write path in
either upstream's script or this port — accepted as-is, not a porting bug).

## `git-guardrails` — adapted and active

[`git-guardrails/`](git-guardrails/) adapts
[mattpocock/skills/misc/git-guardrails-claude-code](https://github.com/mattpocock/skills/tree/main/skills/misc/git-guardrails-claude-code)
(already Claude-Code-native — no format porting needed, unlike
`continual-learning`). A `PreToolUse` hook intercepting the Bash tool:
`git push` is now **branch-aware** — blocked only when the target is
`main`/`master`, feature-branch pushes are allowed (upstream blanket-blocks
all push); `reset --hard`/`clean -f(d)`/`branch -D`/`checkout .`/`restore .`
stay blanket-blocked, unchanged. No `jq` dependency (uses `sed`), so it
works today regardless of the `continual-learning` activation gate. See its
own README for the full adaptation rationale, the layered-defense caveat
(only intercepts Claude Code's own Bash-tool git calls, not a direct
terminal push or another machine), and install steps.

## `skill-catalog-health` — installed and active

[`skill-catalog-health/`](skill-catalog-health/) is a `SessionStart` hook
with two jobs: inject a compact routing index of every installed skill
(surfacing router skills that are deliberately `disable-model-invocation:
true` and would otherwise only get used if someone remembers `/ask-matt`
exists), and flag any `~/.claude/skills/*` junction/symlink broken by a
renamed or moved source-repo folder — the exact failure mode that
silently stranded every skill in this catalog for several weeks before
this hook existed. See [ADR-0005](../docs/adr/0005-skill-routing-and-drift-detection.md)
and its own README for the full reasoning and install steps.

## `root-memory-propagation` — installed and active

[`root-memory-propagation/`](root-memory-propagation/) is a `PostToolUse`
hook + companion subagent. Root memory (`~/.claude/memory/*.md`,
`~/.claude/CLAUDE.md`) is auto-loaded into every session, but downstream
repos have been found hand-duplicating it anyway — a plan naming specific
files to fix can still miss copies it never enumerated (the exact
near-miss recorded in [ADR-0010](../docs/adr/0010-root-memory-propagation-audit.md)).
The hook (`nudge.sh`) deterministically detects "a root memory file just
changed" and points at the `root-memory-propagation-auditor` subagent,
which diffs root memory, greps a registry of known downstream repos for
the old text, and judges genuine stale duplicates apart from coincidental
matches. See its own README for install steps and the registry format.

## Population status

All four hooks above are installed and active on this machine, wired
into `~/.claude/settings.json`.

**Distribution note (2026-07-18):** per [ADR-0011](../docs/adr/0011-unified-distribution-architecture.md),
hooks are slated to move from copy-and-manually-re-copy to junction-linked
installs, the same mechanism skills already use (ADR-0003), managed by a
future `tools/manage_distribution.py`. Design-only for now — the hooks
above stay installed as physical copies until that tool exists and
`--apply` is run against them.
