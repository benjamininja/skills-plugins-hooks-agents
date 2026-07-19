# root-memory-propagation

A `PostToolUse` hook + companion subagent pair. Root memory
(`~/.claude/memory/*.md`, `~/.claude/CLAUDE.md`) is auto-loaded into every
session, but downstream repos have been found hand-duplicating its content
anyway (see `docs/adr/0010-root-memory-propagation-audit.md`) — and a plan
that names specific files to fix can still miss copies it never enumerated.
This pair turns that from a manual afterthought into a standing check.

## Two pieces, two jobs

- **`nudge.sh`** (the hook) — deterministic. Fires on every `Edit`/`Write`,
  checks if the touched file is under root's `.claude/memory/` or is root's
  `CLAUDE.md` (anchored on `$HOME/.claude`, so it does **not** fire on any
  project repo's own local `.claude/memory/`), and if so prints a one-line
  reminder. Never blocks (`exit 0` always) — this is a nudge, not a gate.
- **`root-memory-propagation-auditor`** (`.claude/agents/root-memory-propagation-auditor.md`)
  — judgment. Diffs root memory (`git -C ~/.claude diff`) to see exactly
  what text changed, greps every repo in `known-downstream-repos.json` for
  the old text, and for each hit reads context to decide: genuine stale
  duplicate (flag it) or coincidental match on the same characters but
  unrelated meaning (ignore). That judgment call is why this half is a
  subagent, not more shell script — a hook can detect "this string appears
  elsewhere," it can't tell "market value 35%" apart from "compact budget
  35%" the way a reader can.

## Registry

`known-downstream-repos.json` — a flat list of repo paths known to
duplicate root memory content. Seeded with the one confirmed case
(`Python-PowerBI-DynastyFantasyFootball`). Not exhaustive on day one — add
an entry whenever a new duplicate turns up, same as this hook's own
motivating incident.

## Install (global — one machine-wide install)

1. Copy the script to a fixed, machine-wide location:
   ```bash
   mkdir -p "$HOME/.claude/hooks/root-memory-propagation"
   cp nudge.sh known-downstream-repos.json "$HOME/.claude/hooks/root-memory-propagation/"
   chmod +x "$HOME/.claude/hooks/root-memory-propagation/nudge.sh"
   ```
2. Merge `settings-snippet.json`'s `hooks.PostToolUse` entry into
   `~/.claude/settings.json` (append to the existing `PostToolUse` array —
   don't overwrite the `continual-learning` entry already there).
3. No other dependencies — no `jq` needed, same reasoning as
   `hooks/git-guardrails`.

## Verify

```bash
echo '{"tool_input":{"file_path":"C:\\Users\\benha\\.claude\\memory\\token-gating-loop.md"}}' | ./nudge.sh
# prints the reminder

echo '{"tool_input":{"file_path":"C:\\Users\\benha\\OneDrive\\Documents\\GitHub\\some-repo\\.claude\\memory\\MEMORY.md"}}' | ./nudge.sh
# silent — project-local memory, not root
```

## Boundaries

- The hook only fires when **Claude Code itself** performs the edit via the
  `Edit`/`Write` tools — a direct filesystem edit outside the harness won't
  trigger it. Same layered-defense caveat as `hooks/git-guardrails`.
- The subagent is read-only — it reports findings, it never edits a
  downstream repo itself. The session decides what to fix, same as
  `plan-gate-sync-auditor`.
