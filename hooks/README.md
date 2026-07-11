# hooks/

Reserved for standalone Claude Code hooks (event-triggered shell commands
configured via `settings.json`) that belong to this central repo.

## `continual-learning` — ported and ready to install

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
low hit count). See its own README for install steps and the full list of
what changed porting from Copilot CLI's format.

## `git-guardrails` — adapted and ready to install

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

## Population status

Otherwise empty as of the `skills` → `skills-plugins-hooks` restructure.
Further population is scoped to a later phase of the saturation effort —
see the repo root README's Roadmap section.
