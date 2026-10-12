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
#   - No jq dependency: the command string is pulled out of the hook JSON
#     with sed, honoring escaped quotes (jq isn't reliably on PATH here).
#
# How a command is read (each step exists because a real bypass got through
# without it — see tests/test_git_guardrails.py):
#   1. Line continuations are joined; remaining newlines act as `;`.
#   2. The command is split on && || ; | & and each segment judged alone.
#   3. git's global options (-C <path>, -c k=v, --git-dir=…) are removed, so
#      `git -C x push` is seen as `git push`.
#   4. Quotes, backticks, parentheses, braces and `$` become spaces, and
#      whitespace is collapsed, so `(git push)`, `bash -c 'git restore .'`
#      and `git  push` all read as plain words.
# When in doubt the hook blocks: text after a `#` still counts toward a
# block, and never toward an exemption.
#
# Layered-defense note: this is a text match on one tool call. It does not
# see git run from inside a script file, `gh api`, an alias, a direct
# terminal push, or another machine — see hooks/git-guardrails/README.md.
# The GitHub ruleset on `main` is the layer that cannot be bypassed locally.

set -uo pipefail

INPUT=$(cat)

# tool_input.command, as a JSON string body: any run of escaped chars (\x)
# or non-quote/non-backslash chars, up to the closing unescaped quote.
RAW=$(printf '%s' "$INPUT" | tr '\n' ' ' \
  | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(\(\\.\|[^"\\]\)*\)".*/\1/p')
[[ -z "$RAW" ]] && exit 0

# JSON-unescape what matters for matching. \x01 stands in for a literal
# backslash while the other escapes are handled. A backslash or backtick
# right before a newline is a line continuation: join the lines. Any other
# newline separates commands, like `;`.
COMMAND=$(printf '%s' "$RAW" | sed -e 's/\\\\/\x01/g' \
  -e 's/\x01\(\\r\)\{0,1\}\\n/ /g' -e 's/`\(\\r\)\{0,1\}\\n/ /g' \
  -e 's/\\[nr]/;/g' -e 's/\\t/ /g' -e 's/\\"/"/g' -e 's/\\\//\//g' \
  -e 's/\x01/\\/g')

block() {
  echo "BLOCKED: '$COMMAND' — $1. The user has prevented you from doing this." >&2
  exit 2
}

# A value for a global option: "quoted", 'quoted', or a bare word.
VAL="(\"[^\"]*\"|'[^']*'|[^[:space:]]+)"
# git's global options that can sit between `git` and the subcommand.
GLOBAL_OPT="[[:space:]]+((-C|-c|--git-dir|--work-tree|--namespace|--exec-path|--super-prefix)([[:space:]]+|=)${VAL}|--no-pager|--paginate|-p|-P|--bare|--no-replace-objects|--literal-pathspecs|--no-optional-locks|--exec-path)"

# Zero or more arguments, then the one named: `<sub>( <arg>)* <wanted>`.
ARGS='([[:space:]]+[^[:space:]]+)*[[:space:]]+'
END='([[:space:]]|$)'

# Set when an earlier segment of the same command switches to main/master.
SWITCHED_TO_MAIN=""

# Text up to a `#` that starts a word (a shell comment), for exemptions and
# for counting what a push names. Blocking patterns never use this.
uncommented() { echo "$1" | sed -E 's/(^|[[:space:]])#.*$//'; }

check_segment() {
  local seg="$1"

  # Not a git invocation at all? Nothing to do.
  echo "$seg" | grep -qE '(^|[^[:alnum:]_.-])git(\.exe)?([[:space:]]|$)' || return 0

  # Remember the first -C path (used to find the checked-out branch).
  local cdir
  cdir=$(echo "$seg" | sed -nE "s/.*git(\.exe)?[[:space:]]+(.*[[:space:]])?-C[[:space:]]+${VAL}.*/\3/p" \
    | sed -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'\$/\1/")

  # `git <subcommand> ...` with global options removed, redirections
  # (`>file`, `2>>file`, `<file`) and backslashes dropped, then every shell
  # delimiter turned into a space and whitespace collapsed.
  local flat
  flat=$(echo "$seg" \
    | sed -E "s/git(\.exe)?(${GLOBAL_OPT})+[[:space:]]+/git /g; s/git\.exe([[:space:]]|$)/git /g" \
    | sed -E 's/[0-9]*(>>?|<)[[:space:]]*[^[:space:]]*/ /g' \
    | tr -d '\\' | tr "\"'\`(){}\$\t" '         ' | tr -s ' ')

  # --- Blanket-blocked destructive commands ---
  if echo "$flat" | grep -qE "git reset${ARGS}--hard${END}"; then
    block "matches blanket-blocked pattern 'git reset --hard'"
  fi
  if echo "$flat" | grep -qE "git clean${ARGS}(-[[:alnum:]]*f[[:alnum:]]*|--force)${END}"; then
    block "matches blanket-blocked pattern 'git clean -f'"
  fi
  if echo "$flat" | grep -qE "git branch${ARGS}-[[:alnum:]]*D[[:alnum:]]*${END}"; then
    block "matches blanket-blocked pattern 'git branch -D'"
  fi
  # `.` and its other spellings: `./`, `./.`, `./*`, `..`
  if echo "$flat" | grep -qE "git checkout${ARGS}\.[./*]*${END}"; then
    block "matches blanket-blocked pattern 'git checkout .'"
  fi
  if echo "$flat" | grep -qE "git restore${ARGS}\.[./*]*${END}"; then
    # `git restore --staged .` only unstages; the working tree is untouched.
    local args
    args=$(uncommented "$flat")
    if ! echo "$args" | grep -qE -- "[[:space:]](--staged|-S)${END}" \
       || echo "$args" | grep -qE -- "[[:space:]](--worktree|-W)${END}"; then
      block "matches blanket-blocked pattern 'git restore .'"
    fi
  fi

  # --- Remember a switch to main/master for a later bare push ---
  if echo "$flat" | grep -qE "git (checkout|switch)${END}"; then
    if echo "$flat" | grep -qE "git (checkout|switch)${ARGS}(-b|-B|-c|-C|--create|--force-create|--orphan)${END}"; then
      SWITCHED_TO_MAIN=""   # a new branch is created; a later push is not on main
    elif echo "$flat" | grep -qE "git (checkout|switch)${ARGS}(main|master)${END}"; then
      SWITCHED_TO_MAIN=$(echo "$flat" | sed -nE 's/.*git ((checkout|switch).*)/\1/p' | sed -E 's/[[:space:]]+$//')
    fi
  fi

  # --- Branch-aware push guard ---
  if echo "$flat" | grep -qE "git push${END}"; then
    local rest="${flat#*git push}"   # text after the FIRST `git push`

    # An explicit main/master target: `main`, `HEAD:main`, `:main`,
    # `+main`, `refs/heads/main`.
    if echo "$rest" | grep -qE "(^|[[:space:]:+]|refs/heads/)(main|master)${END}"; then
      block "pushes directly to main/master — push a feature branch and open a PR instead"
    fi

    # No explicit main/master. What does the push name? Drop flags; the
    # first word left is the remote, the rest are refspecs. No refspec, or
    # only HEAD / @ (which mean "whatever is checked out"), is an implicit
    # push of the current branch.
    local refs
    refs=$(uncommented "$rest" | tr ' ' '\n' | grep -vE '^(-|$)' | tail -n +2 \
      | grep -vE '^\+?(HEAD|@)$' || true)
    if [[ -z "$refs" ]]; then
      if [[ -n "$SWITCHED_TO_MAIN" ]]; then
        block "an earlier 'git $SWITCHED_TO_MAIN' in this command puts this push on main/master — push a feature branch and open a PR instead"
      fi
      # Never open a network path named by the command just to look up a
      # branch (on Windows that can send credentials to the named host).
      case "$cdir" in
        [/\\][/\\]*|[/\\]\?\?[/\\]*) block "push with -C pointing at a network path and no branch named — name the branch explicitly" ;;
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

# Split on shell separators (&&, ||, ;, |, &) and check each segment on its
# own. The `&` and `|` of a redirection (`2>&1`, `&>file`, `>|file`) are not
# separators: reduce those to a plain `>` first, so `git push 2>&1 origin
# main` stays one segment.
while IFS= read -r segment; do
  [[ -z "${segment// /}" ]] && continue
  check_segment "$segment"
done < <(printf '%s\n' "$COMMAND" \
  | sed -E -e 's/&>/>/g' -e 's/>&/>/g' -e 's/>\|/>/g' -e 's/(&&|\|\||;|\||&)/\n/g')

exit 0
