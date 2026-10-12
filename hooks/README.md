# hooks/

Reserved for standalone Claude Code hooks (event-triggered shell commands
configured via `settings.json`) that belong to this central repo.

## `git-guardrails` — adapted and active

[`git-guardrails/`](git-guardrails/) adapts
[mattpocock/skills/misc/git-guardrails-claude-code](https://github.com/mattpocock/skills/tree/main/skills/misc/git-guardrails-claude-code)
(already Claude-Code-native — no format porting needed). A `PreToolUse` hook intercepting the Bash tool:
`git push` is now **branch-aware** — blocked only when the target is
`main`/`master`, feature-branch pushes are allowed (upstream blanket-blocks
all push); `reset --hard`/`clean -f(d)`/`branch -D`/`checkout .`/`restore .`
stay blanket-blocked, unchanged. No `jq` dependency (uses `sed`). See its
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

All three hooks above are installed and active on this machine, wired
into `~/.claude/settings.json` and linked from the live clone by
`tools/relink_live.ps1` (see the repo README's Installation section and
[ADR-0011](../docs/adr/0011-unified-distribution-architecture.md)).

`continual-learning` was retired on 2026-10-12 — see
[ADR-0012](../docs/adr/0012-retire-continual-learning.md).
