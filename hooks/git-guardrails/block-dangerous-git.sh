#!/bin/bash
# git-guardrails — adapted from mattpocock/skills' git-guardrails-claude-code
# (github.com/mattpocock/skills/tree/main/skills/misc/git-guardrails-claude-code).
#
# PreToolUse hook intercepting shell tool calls (Bash and PowerShell) before
# execution. Both tools pass the command as tool_input.command.
#
# What changed from upstream:
#   - `git push` is branch-aware: blocked only when the target is
#     main/master (by explicit refspec, or by falling back to whatever
#     branch is currently checked out when the command names no branch at
#     all). Upstream blanket-blocks ALL push.
#   - reset --hard / clean -f / branch -D / checkout . / restore . stay
#     blanket-blocked — always destructive regardless of branch.
#   - git's global options are stripped before matching, so
#     `git -C <path> push origin main`, `git -c k=v reset --hard` and
#     `git --git-dir=<dir> clean -fd` are seen as what they are.
#   - Each `&&` / `||` / `;` / `|` segment is checked on its own, so a
#     branch name in one segment cannot clear or condemn another.
#   - No jq dependency: the command string is pulled out of the hook JSON
#     with sed, honoring escaped quotes (jq isn't reliably on PATH here).
#
# Tests: tests/test_git_guardrails.py (run in CI).
#
# Layered-defense note: this is a text match on one tool call. It does not
# see git run from inside a script, `gh api`, an alias, a direct terminal
# push, or another machine — see hooks/git-guardrails/README.md. The
# GitHub ruleset on `main` is the layer that cannot be bypassed locally.

set -uo pipefail

INPUT=$(cat)

# tool_input.command, as a JSON string body: any run of escaped chars (\x)
# or non-quote/non-backslash chars, up to the closing unescaped quote.
RAW=$(printf '%s' "$INPUT" | tr '\n' ' ' \
  | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(\(\\.\|[^"\\]\)*\)".*/\1/p')
[[ -z "$RAW" ]] && exit 0

# JSON-unescape what matters for matching: \n \r \t -> space, \" -> ",
# \\ -> \ (order matters: protect \\ first).
COMMAND=$(printf '%s' "$RAW" | sed -e 's/\\\\/\x01/g' \
  -e 's/\\[nrt]/ /g' -e 's/\\"/"/g' -e 's/\\\//\//g' -e 's/\x01/\\/g')

block() {
  echo "BLOCKED: '$COMMAND' — $1. The user has prevented you from doing this." >&2
  exit 2
}

# A value for a global option: "quoted", 'quoted', or a bare word.
VAL="(\"[^\"]*\"|'[^']*'|[^[:space:]]+)"
# git's global options that can sit between `git` and the subcommand.
GLOBAL_OPT="[[:space:]]+((-C|-c|--git-dir|--work-tree|--namespace|--exec-path|--super-prefix)([[:space:]]+|=)${VAL}|--no-pager|--paginate|-p|-P|--bare|--no-replace-objects|--literal-pathspecs|--no-optional-locks|--exec-path)"

check_segment() {
  local seg="$1"

  # Not a git invocation at all? Nothing to do.
  echo "$seg" | grep -qE '(^|[^[:alnum:]_.-])git(\.exe)?([[:space:]]|$)' || return 0

  # Remember the first -C path (used to find the checked-out branch).
  local cdir
  cdir=$(echo "$seg" | sed -nE "s/.*git(\.exe)?[[:space:]]+(.*[[:space:]])?-C[[:space:]]+${VAL}.*/\3/p" \
    | sed -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'\$/\1/")

  # Canonical form: `git <subcommand> ...` with global options removed.
  local norm
  norm=$(echo "$seg" | sed -E "s/git(\.exe)?(${GLOBAL_OPT})+[[:space:]]+/git /g; s/git\.exe[[:space:]]+/git /g")

  # --- Blanket-blocked destructive commands ---
  if echo "$norm" | grep -qE 'git reset([[:space:]]+[^[:space:]]+)*[[:space:]]+--hard'; then
    block "matches blanket-blocked pattern 'git reset --hard'"
  fi
  if echo "$norm" | grep -qE 'git clean([[:space:]]+[^[:space:]]+)*[[:space:]]+(-[[:alnum:]]*f[[:alnum:]]*|--force)'; then
    block "matches blanket-blocked pattern 'git clean -f'"
  fi
  if echo "$norm" | grep -qE 'git branch([[:space:]]+[^[:space:]]+)*[[:space:]]+-[[:alnum:]]*D'; then
    block "matches blanket-blocked pattern 'git branch -D'"
  fi
  if echo "$norm" | grep -qE 'git checkout([[:space:]]+[^[:space:]]+)*[[:space:]]+\.([[:space:]]|$)'; then
    block "matches blanket-blocked pattern 'git checkout .'"
  fi
  if echo "$norm" | grep -qE 'git restore([[:space:]]+[^[:space:]]+)*[[:space:]]+\.([[:space:]]|$)'; then
    # `git restore --staged .` only unstages; the working tree is untouched.
    if ! echo "$norm" | grep -qE -- '--staged|[[:space:]]-S([[:space:]]|$)' \
       || echo "$norm" | grep -qE -- '--worktree|[[:space:]]-W([[:space:]]|$)'; then
      block "matches blanket-blocked pattern 'git restore .'"
    fi
  fi

  # --- Branch-aware push guard ---
  if echo "$norm" | grep -qE 'git push([[:space:]]|$)'; then
    local rest
    rest=$(echo "$norm" | sed -E 's/^.*git push//')

    # An explicit main/master target: `main`, `HEAD:main`, `:main`,
    # `+main`, `refs/heads/main`.
    # Quotes around the ref are stripped first (`git push origin "main"`).
    if echo "$rest" | tr -d "\"'" | grep -qE '(^|[[:space:]:+]|refs/heads/)(main|master)([[:space:]]|$)'; then
      block "pushes directly to main/master — push a feature branch and open a PR instead"
    fi

    # No explicit main/master. Count non-flag tokens after "push": 0-1
    # (nothing, or just a remote) means the push implicitly targets the
    # checked-out branch — look it up. 2+ means an explicit non-main
    # branch was named — already cleared above, allow.
    local non_flag
    non_flag=$(echo "$rest" | tr ' ' '\n' | grep -cvE '^(-|$)' || true)
    if [[ "$non_flag" -lt 2 ]]; then
      # Never open a network path named by the command just to look up a
      # branch (on Windows that can send credentials to the named host).
      case "$cdir" in
        [/\\][/\\]*|[/\\]\?\?[/\\]*) block "bare push with -C pointing at a network path — name the branch explicitly" ;;
      esac
      local dir="${cdir:-${CLAUDE_PROJECT_DIR:-$PWD}}"
      local branch
      branch=$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
      if [[ "$branch" == "main" || "$branch" == "master" ]]; then
        block "current checked-out branch is '$branch' and the command names no other target — push a feature branch and open a PR instead"
      fi
    fi
  fi

  return 0
}

# Split on shell separators and check each segment on its own.
while IFS= read -r segment; do
  [[ -z "${segment// /}" ]] && continue
  check_segment "$segment"
done < <(printf '%s\n' "$COMMAND" | sed -E 's/(&&|\|\||;|\|)/\n/g')

exit 0
