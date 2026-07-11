#!/bin/bash
# git-guardrails — adapted from mattpocock/skills' git-guardrails-claude-code
# (github.com/mattpocock/skills/tree/main/skills/misc/git-guardrails-claude-code).
#
# PreToolUse hook intercepting the Bash tool before execution.
#
# What changed from upstream:
#   - `git push` is now branch-aware: blocked only when the target is
#     main/master (by explicit refspec, or by falling back to whatever
#     branch is currently checked out when the command names no branch at
#     all). Upstream blanket-blocks ALL push.
#   - reset --hard / clean -f(d) / branch -D / checkout ./restore . stay
#     blanket-blocked, unchanged from upstream — always destructive
#     regardless of branch.
#   - No jq dependency: the command string is pulled out with sed instead
#     of jq, so this works on machines without jq on PATH — this repo's own
#     continual-learning hook found jq missing here, and this hook is meant
#     to be active today, not gated on the same install decision.
#     ponytail: sed extraction is a naive single-line heuristic that stops
#     at the first `"` — a command containing a literal embedded double
#     quote (e.g. a commit message with a quoted phrase) will parse wrong.
#     Upgrade to jq if that ever bites.
#
# Layered-defense note: this only intercepts Claude Code's own Bash tool
# calls. It does not stop a direct terminal `git push`, another tool, or
# another machine — see hooks/git-guardrails/README.md.

set -euo pipefail

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[[ -z "$COMMAND" ]] && exit 0

block() {
  echo "BLOCKED: '$COMMAND' — $1. The user has prevented you from doing this." >&2
  exit 2
}

# --- Blanket-blocked destructive patterns (unchanged from upstream) ---
BLANKET_PATTERNS=(
  "git reset --hard"
  "git clean -fd"
  "git clean -f"
  "git branch -D"
  "git checkout \."
  "git restore \."
)
for pattern in "${BLANKET_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qE "$pattern"; then
    block "matches blanket-blocked pattern '$pattern'"
  fi
done

# --- Branch-aware push guard ---
if echo "$COMMAND" | grep -qE "git push"; then
  if echo "$COMMAND" | grep -qE '(^|[[:space:]:])(main|master)([[:space:]]|$)'; then
    block "pushes directly to main/master — push a feature branch and open a PR instead"
  fi

  # No explicit main/master target — but does the command name ANY explicit
  # remote/branch (e.g. `git push origin my-feature`), or is it bare
  # (`git push`, `git push origin`, `git push -u origin`) and therefore
  # implicitly targets whatever branch is currently checked out? Count
  # non-flag tokens after "push": 0-1 (just a remote, or nothing) means
  # implicit — fall back to the current branch. 2+ means an explicit
  # non-main branch was named — already cleared by the check above, allow.
  REST=$(echo "$COMMAND" | sed -E 's/^.*git push//')
  NON_FLAG_TOKENS=$(echo "$REST" | tr ' ' '\n' | grep -cvE '^(-|$)' || true)
  if [[ "$NON_FLAG_TOKENS" -lt 2 ]]; then
    PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
    CURRENT_BRANCH=$(git -C "$PROJECT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
    if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
      block "current checked-out branch is '$CURRENT_BRANCH' and the command names no other target — push a feature branch and open a PR instead"
    fi
  fi
fi

exit 0
