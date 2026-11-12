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
#     all). Upstream blanket-blocks ALL push. The checked-out branch is read
#     in this order: the command's own -C path; then the top-level `cwd` of
#     the hook input (the worktree, in a worktree session), which skips the
#     CLAUDE_PROJECT_DIR lookup (the main checkout in a worktree session) but
#     only when the whole command is exactly a plain push (rule B, below);
#     then CLAUDE_PROJECT_DIR, then $PWD. A network path in -C, or in a `cwd`
#     that is used, blocks and is never given to git.
#   - reset --hard / clean -f / checkout . / restore . stay blanket-blocked
#     — always destructive regardless of branch.
#   - A force branch delete (-D, -d -f, --delete --force, ... any spelling)
#     is blocked unless every branch it names has a merged PR whose head
#     commit is the branch's local tip (`gh pr list --head <b> --state merged`,
#     10 s cap). No branch named, a pattern, `$`, a backtick, or a missing or
#     failing gh all block.
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

# The top-level `cwd` of the hook input: the folder the tool call starts in.
# In a worktree session it is the worktree, while CLAUDE_PROJECT_DIR stays the
# main checkout. Only a string-valued key named cwd directly inside the
# outermost object counts: a cwd key nested in tool_input, or the text "cwd"
# inside the command (which arrives escaped), is skipped. Empty when the field
# is missing. The JSON escapes \\ and \/ are decoded; \x01 stands in for a
# literal backslash while \/ is handled.
HOOK_CWD=$(printf '%s' "$INPUT" | tr '\n\t\r' '   ' | awk '{
  s = $0; n = length(s); depth = 0; i = 1
  while (i <= n) {
    c = substr(s, i, 1)
    if (c == "{" || c == "[") { depth++; i++ }
    else if (c == "}" || c == "]") { depth--; i++ }
    else if (c == "\"") {
      j = i + 1
      while (j <= n) { d = substr(s, j, 1); if (d == "\\") j += 2; else if (d == "\"") break; else j++ }
      key = substr(s, i + 1, j - i - 1); i = j + 1
      if (depth == 1 && key == "cwd") {
        k = i; while (substr(s, k, 1) == " ") k++
        if (substr(s, k, 1) == ":") {
          k++; while (substr(s, k, 1) == " ") k++
          if (substr(s, k, 1) == "\"") {
            m = k + 1
            while (m <= n) { d = substr(s, m, 1); if (d == "\\") m += 2; else if (d == "\"") break; else m++ }
            print substr(s, k + 1, m - k - 1); exit
          }
        }
      }
    }
    else i++
  }
}' | sed -e 's/\\\\/\x01/g' -e 's/\\\//\//g' -e 's/\x01/\\/g')

# Rule B (an allowlist, fail-closed): the hook input's cwd is used for the
# implicit-push branch lookup only when the WHOLE command is exactly a plain
# push: `git push`, then optionally `-u` or `--set-upstream`, then optionally
# one bare remote name (letters, digits, `.`, `_`, `-`, not starting with `-`
# or a dot). One segment, so no `;`, `&&`, `||`, `|`, `&` or newline (a
# newline is already `;` here); no wrapper, subshell, substitution, backtick,
# variable, `$` or env prefix; no global git option, no other push flag and no
# refspec. Anything else, even a command close to a plain push, uses the
# lookup as before: the command's own -C, then CLAUDE_PROJECT_DIR, then $PWD.
# The same for the Bash and the PowerShell tool.
PLAIN_PUSH='^[[:space:]]*git[[:space:]]+push([[:space:]]+(-u|--set-upstream))?([[:space:]]+[A-Za-z0-9_][A-Za-z0-9._-]*)?[[:space:]]*$'
USE_HOOK_CWD=""
[[ "$COMMAND" =~ $PLAIN_PUSH ]] && USE_HOOK_CWD=1

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

GH_CAP=10

# A force branch delete passes only when every branch it names has a merged
# PR whose head commit is the branch's local tip. $1 = flattened segment,
# $2 = the segment before quotes and `$` were flattened, $3 = the -C path.
check_force_branch_delete() {
  local flat="$1" pre="$2" cdir="$3"
  local rest="${flat#*git branch}"

  # Delete and force, read from the whole text (a comment can only add to it).
  local all del="" frc="" t body
  read -ra all <<< "$rest"
  for t in "${all[@]}"; do
    case "$t" in
      --*)
        body="${t#--}"; body="${body%%=*}"
        [[ -n "$body" && "delete" == "$body"* ]] && del=1
        [[ -n "$body" && "force" == "$body"* ]] && frc=1 ;;
      -*)
        [[ "$t" == *[dD]* ]] && del=1
        [[ "$t" == *[fD]* ]] && frc=1 ;;
    esac
  done
  [[ -n "$del" && -n "$frc" ]] || return 0

  if [[ "$pre" == *'$'* || "$pre" == *'`'* ]]; then
    block "force branch delete with \$ or a backtick — name each branch literally"
  fi

  # The branches it names: words that are not flags, comment excluded.
  local names=() n
  read -ra all <<< "$(uncommented "$rest")"
  for n in "${all[@]}"; do
    [[ "$n" == -* ]] && continue
    case "$n" in
      *'*'*|*'?'*|*'['*|*']'*) block "force branch delete of a pattern '$n' — name each branch literally" ;;
    esac
    names+=("$n")
  done
  [[ ${#names[@]} -eq 0 ]] && block "force branch delete names no branch"

  case "$cdir" in
    [/\\][/\\]*|[/\\]\?\?[/\\]*) block "force branch delete with -C pointing at a network path" ;;
  esac
  local dir="${cdir:-${CLAUDE_PROJECT_DIR:-$PWD}}"

  local out oids tip
  for n in "${names[@]}"; do
    out=$(cd "$dir" 2>/dev/null && timeout "$GH_CAP" gh pr list --head "$n" --state merged --json headRefOid 2>/dev/null) \
      || block "cannot check '$n' against a merged PR: gh is missing, failed or took longer than ${GH_CAP}s"
    oids=$(printf '%s' "$out" \
      | grep -oE '"headRefOid"[[:space:]]*:[[:space:]]*"[0-9a-fA-F]+"' \
      | sed -E 's/.*"([0-9a-fA-F]+)"$/\1/')
    [[ -z "$oids" ]] && block "no merged PR for '$n'"
    tip=$(git -C "$dir" rev-parse --verify -q "refs/heads/$n" 2>/dev/null || echo "")
    [[ -z "$tip" ]] && block "no local branch '$n' to check against its merged PR"
    if ! printf '%s\n' "$oids" | grep -qxF "$tip"; then
      block "'$n' has commits after its merged PR (local tip ${tip:0:7} is not the head of any merged PR)"
    fi
  done
  return 0
}

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
  local pre flat
  pre=$(echo "$seg" \
    | sed -E "s/git(\.exe)?(${GLOBAL_OPT})+[[:space:]]+/git /g; s/git\.exe([[:space:]]|$)/git /g" \
    | sed -E 's/[0-9]*(>>?|<)[[:space:]]*[^[:space:]]*/ /g')
  flat=$(echo "$pre" \
    | tr -d '\\' | tr "\"'\`(){}\$\t" '         ' | tr -s ' ')

  # --- Blanket-blocked destructive commands ---
  if echo "$flat" | grep -qE "git reset${ARGS}--hard${END}"; then
    block "matches blanket-blocked pattern 'git reset --hard'"
  fi
  if echo "$flat" | grep -qE "git clean${ARGS}(-[[:alnum:]]*f[[:alnum:]]*|--force)${END}"; then
    block "matches blanket-blocked pattern 'git clean -f'"
  fi
  if echo "$flat" | grep -qE "git branch${END}"; then
    check_force_branch_delete "$flat" "$pre" "$cdir"
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
  # The text here has its quotes and backslashes deleted, not turned into
  # spaces, so a split name (`ma''in`) reads as `main`. `sw_all` keeps a
  # comment: text after a `#` can set the switch, never clear it. `sw_code`
  # drops the comment and is the only text a create flag may clear from.
  local sw_all sw_code
  sw_all=$(echo "$pre" | tr -d "\"'\`\\\\" | tr '(){}$\t' '      ' | tr -s ' ')
  sw_code=$(uncommented "$sw_all")
  if echo "$sw_all" | grep -qE "git (checkout|switch)${END}"; then
    local create='(-[[:alpha:]]*[bBcC]|--create|--force-create|--orphan)'
    local named='(main|master)'
    local set_switch t set_hit=""
    set_switch=$(echo "$sw_all" | sed -nE 's/.*git ((checkout|switch).*)/\1/p' | sed -E 's/[[:space:]]+$//')
    # Setting reads the text both ways, quotes deleted (`ma''in`) and quotes
    # spaced (`"$x"main`, where deleting the quotes first would fuse `$x` and
    # `main`): either one matching sets the switch, which fails closed.
    # A new branch named main or master: `-c main`, `-B main`, `-bmain`, a
    # cluster such as `-fb main` or `-fbmain`, `--create=main`, any option
    # spelled short with `=` (`--cre=main`, `--force-c=main`, `--orph=main`),
    # any other option in between: a later push is on main. Set the switch.
    for t in "$sw_all" "$flat"; do
      if echo "$t" | grep -qE "git (checkout|switch)${ARGS}(${create}[[:space:]]+${named}${END}|-[[:alpha:]]*[bBcC]${named}${END}|--[[:alpha:]-]+=${named}${END})"; then
        set_hit=1
      fi
    done
    # Any other new branch clears it, as before. Clearing is the loosening
    # side: it reads only the quote-deleted text with the comment dropped and
    # everything from `--` on cut off (a pathspec is not an option), and
    # accepts only the create letters each subcommand really has: checkout
    # -b and -B, switch -c and -C, each with the flags that can share a
    # cluster (`-fb`).
    local sw_opts
    sw_opts=$(echo "$sw_code" | sed -E 's/[[:space:]]--([[:space:]].*)?$//')
    if [[ -n "$set_hit" ]]; then
      SWITCHED_TO_MAIN="$set_switch"
    elif echo "$sw_opts" | grep -qE "git checkout${ARGS}(-[qfmtl]*[bB][^[:space:]]*|--orphan|--orphan=[^[:space:]]*)${END}" \
       || echo "$sw_opts" | grep -qE "git switch${ARGS}(-[fmqt]*[cC][^[:space:]]*|--create|--force-create|--orphan|--(create|force-create|orphan)=[^[:space:]]*)${END}"; then
      SWITCHED_TO_MAIN=""
    else
      for t in "$sw_all" "$flat"; do
        if echo "$t" | grep -qE "git (checkout|switch)${ARGS}${named}${END}"; then
          SWITCHED_TO_MAIN="$set_switch"
        fi
      done
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
      # The hook input's cwd, when it is used (see USE_HOOK_CWD), gets the
      # same rule as a -C path: a network path is never handed to git.
      local cwd_dir=""
      [[ -z "$cdir" && -n "$USE_HOOK_CWD" ]] && cwd_dir="$HOOK_CWD"
      case "$cwd_dir" in
        [/\\][/\\]*|[/\\]\?\?[/\\]*) block "push from a folder on a network path and no branch named — name the branch explicitly" ;;
      esac
      # Where the branch is read, in order: the command's own -C path; the
      # hook input's `cwd`, only under rule B (the whole command is exactly a
      # plain push), which then replaces the CLAUDE_PROJECT_DIR lookup; then
      # CLAUDE_PROJECT_DIR (or $PWD). A `cwd` that gives no branch falls
      # through to the next one.
      local branch="" dir
      for dir in "$cdir" "$cwd_dir" "${CLAUDE_PROJECT_DIR:-$PWD}"; do
        [[ -z "$dir" ]] && continue
        branch=$(git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
        [[ -n "$branch" ]] && break
        [[ -n "$cdir" ]] && break   # a -C path is final, as before
      done
      if [[ "$branch" == "main" || "$branch" == "master" ]]; then
        local why=""
        # Say why the hook input's cwd was not read, so a feature worktree is
        # not told its own branch is main.
        if [[ -z "$cdir" && -n "$HOOK_CWD" && -z "$USE_HOOK_CWD" ]]; then
          why=" (read from CLAUDE_PROJECT_DIR or the hook's folder, not the hook input's cwd, because the command is not exactly a plain push)"
        fi
        block "current checked-out branch is '$branch'${why} and the command names no other target — push a feature branch and open a PR instead"
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
