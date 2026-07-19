#!/bin/bash
# root-memory-propagation — PostToolUse hook on Edit|Write.
#
# Root memory files (~/.claude/memory/*.md, ~/.claude/CLAUDE.md) are
# auto-loaded into every session, but at least one downstream repo has been
# found hand-duplicating their content (Python-PowerBI-DynastyFantasyFootball's
# own docs/adr/0001-*.md + CLAUDE.md + PLAN.md + .claude/memory/MEMORY.md all
# restated the token-gating compact budget). A plan that names specific
# downstream files to fix is not enough — 2026-07-18 caught 2 more files in
# that same repo carrying the same stale figure only via an ad hoc full-repo
# grep after the fact, not because anything mechanical flagged it.
#
# This hook is deliberately dumb: it only detects "a root memory file just
# changed" (a path check) and nudges toward running the
# root-memory-propagation-auditor subagent, which does the actual
# git-diff + grep + judgment work. No jq dependency — same reasoning as
# hooks/git-guardrails/block-dangerous-git.sh (jq isn't reliably on PATH on
# this machine), and a bare path check needs nothing more than sed anyway.
#
# Non-blocking: always exits 0. This is a reminder, not a gate.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(printf '%s' "$INPUT" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[[ -z "$FILE_PATH" ]] && exit 0

# Normalize backslashes to forward slashes and lowercase for a reliable
# prefix match (tool_input paths on Windows arrive with either separator,
# and drive-letter casing isn't guaranteed).
NORMALIZED=$(printf '%s' "$FILE_PATH" | tr '\\' '/' | tr '[:upper:]' '[:lower:]')
ROOT=$(printf '%s' "${USERPROFILE:-$HOME}/.claude" | tr '\\' '/' | tr '[:upper:]' '[:lower:]')

# Anchor on $ROOT specifically — every project repo also has its own
# .claude/memory/ for project-local memory, which this hook must NOT fire
# on. Only the machine-wide root tier (auto-loaded into every session) is
# in scope here.
case "$NORMALIZED" in
  "$ROOT"/memory/*.md|"$ROOT"/claude.md)
    echo "Root memory changed: $FILE_PATH — downstream repos may hold stale copies of this content. Consider running the root-memory-propagation-auditor subagent (skills-plugins-hooks-agents/.claude/agents/root-memory-propagation-auditor.md) before treating this as done."
    ;;
esac

exit 0
