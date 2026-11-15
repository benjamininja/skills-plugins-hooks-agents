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
#   5. Each segment is also read the way Bash and PowerShell read it (#168):
#      quotes removed and joined, escapes resolved, and a word whose last
#      path part is git (any case, .exe/.cmd/.bat/.com) becomes `git`. So
#      `"git"`, `g''it`, `Git` and `& "C:\...\git.exe"` read as `git`. Quoted
#      text is read again, up to 3 passes, for `bash -c '...'`. A word the
#      hook cannot read (`$`, a glob) right before a guarded verb or a dash
#      word is tried as `git`. Every reading is judged; any one blocks.
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

# Set while a reading that tries an unreadable word as `git` is judged.
VIEW_NOTE=""

block() {
  echo "BLOCKED: '$COMMAND' — $1${VIEW_NOTE}. The user has prevented you from doing this." >&2
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

# True when the text holds a `#` inside quotes or right after a backslash
# or a backtick.
quoted_hash() {
  local s="$1" q="" i c
  [[ "$s" == *'#'* ]] || return 1
  for ((i = 0; i < ${#s}; i++)); do
    c="${s:i:1}"
    if [[ -n "$q" ]]; then
      [[ "$c" == '#' ]] && return 0
      [[ "$c" == "$q" ]] && q=""
      continue
    fi
    case "$c" in
      '\'|'`') [[ "${s:i+1:1}" == '#' ]] && return 0; ((i++)) ;;
      '"'|"'") q="$c" ;;
    esac
  done
  return 1
}

GH_CAP=10
# "<dir>|<branch>" lines already passed, so each reading of a segment does
# not ask gh again.
GH_PASSED=$'\n'

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
  # A `#` inside quotes or after an escape is not a comment, so the names
  # after it are real: block rather than guess which ones git deletes.
  if quoted_hash "$pre"; then
    block "force branch delete with a quoted or escaped # — name each branch literally"
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
    [[ "$GH_PASSED" == *$'\n'"$dir|$n"$'\n'* ]] && continue
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
    GH_PASSED+="$dir|$n"$'\n'
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
  # comment: text after a `#` can set the switch.
  local sw_all
  sw_all=$(echo "$pre" | tr -d "\"'\`\\\\" | tr '(){}$\t' '      ' | tr -s ' ')
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
    # Nothing here clears the switch: once an earlier segment of the command
    # switches to main, a later bare push is held, whatever comes between,
    # because the hook cannot see whether a create succeeded (owner's ruling
    # on #135). A push that names its target is unaffected.
    if [[ -n "$set_hit" ]]; then
      SWITCHED_TO_MAIN="$set_switch"
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

# The readings of each segment (#168), one per line as `<note>\x1f<text>`:
# the segment as it is, then for Bash and for PowerShell up to 3 passes of
# shell reading (quotes removed and joined, escapes resolved, a git-named
# word turned into `git`, the word after `git` lowercased, a word holding
# spaces quoted again so -C paths survive), each pass reading the quoted
# text of the one before. A word the hook cannot read (it holds `$` or an
# unquoted `*`, `?`, `[`) that comes right before a guarded verb or a dash
# word gives one more reading with that word as `git`, and <note> names it.
# Readings equal up to whitespace are printed once, and a reading with no
# `git` word (which the gate in check_segment would pass over) is not printed.
VIEWS_AWK='
BEGIN { SQ = "\047"; DQ = "\042"; BS = "\\"; BT = "`"; US = "\037"
        VERBS = " push reset clean checkout restore branch switch "
        VALOPT = " -C -c --git-dir --work-tree --namespace --exec-path --super-prefix --config-env --attr-source "
        LDQ1 = "\342\200\234"; LDQ2 = "\342\200\235"; LDQ3 = "\342\200\236"
        LSQ1 = "\342\200\230"; LSQ2 = "\342\200\231"; LSQ3 = "\342\200\232"; LSQ4 = "\342\200\233" }
function flush() { if (cur != "") { n++; W[n] = cur; F[n] = flag } cur = ""; flag = 0 }
function addq(ch) { cur = cur (ch == "#" ? BS "#" : ch) }
function group(s, i, op, cl, mode,    j, e, depth, q) {
  q = ""; depth = 0
  for (j = (op == cl) ? i + 1 : i; j <= L; j++) {
    e = substr(s, j, 1)
    if (q != "") {
      if (e == q) q = ""
      else if (q == DQ && ((mode == "bash" && e == BS) || (mode == "ps" && e == BT))) j++
      continue
    }
    if (mode == "bash" && e == BS) { j++; continue }
    if (mode == "ps" && e == BT) { j++; continue }
    if (op == cl && e == cl) return j
    if (e == SQ || e == DQ) { q = e; continue }
    if (op != cl) {
      if (e == op) depth++
      else if (e == cl) { depth--; if (depth == 0) return j }
    }
  }
  return L + 1
}
function dollar(s, i, mode,    d, j, e) {
  flag = 1; d = substr(s, i + 1, 1)
  if (d == "(") {
    j = group(s, i + 1, "(", ")", mode)
    cur = cur "$" substr(s, i + 1, j - i)
    return j + 1
  }
  cur = cur "$"
  if (d == "{") {
    j = i + 1
    while (j <= L) { e = substr(s, j, 1); cur = cur e; j++; if (e == "}") break }
    return j
  }
  if (d == SQ && mode == "bash") {
    cur = cur SQ; j = i + 2
    while (j <= L) { e = substr(s, j, 1)
      if (e == BS) { cur = cur e substr(s, j + 1, 1); j += 2; continue }
      cur = cur e; j++; if (e == SQ) break }
    return j
  }
  return i + 1
}
function lex(s, mode,    i, c, d, q, j, e, k, inner, suf, pre, np, a, A) {
  if (mode == "ps") {
    gsub(LDQ1, DQ, s); gsub(LDQ2, DQ, s); gsub(LDQ3, DQ, s)
    gsub(LSQ1, SQ, s); gsub(LSQ2, SQ, s); gsub(LSQ3, SQ, s); gsub(LSQ4, SQ, s)
    gsub(/\\u201[cdeCDE]/, DQ, s); gsub(/\\u201[89abAB]/, SQ, s)
  }
  n = 0; cur = ""; flag = 0; q = ""; L = length(s); i = 1
  while (i <= L) {
    c = substr(s, i, 1)
    if (q == SQ) {
      if (c == SQ) {
        if (mode == "ps" && substr(s, i + 1, 1) == SQ) { cur = cur SQ; i += 2; continue }
        q = ""; i++; continue
      }
      addq(c); i++; continue
    }
    if (q == DQ) {
      if (c == DQ) {
        if (mode == "ps" && substr(s, i + 1, 1) == DQ) { cur = cur DQ; i += 2; continue }
        q = ""; i++; continue
      }
      if (mode == "bash" && c == BS) {
        d = substr(s, i + 1, 1)
        if (d == "$" || d == BT || d == DQ || d == BS) { addq(d); i += 2; continue }
        cur = cur c; i++; continue
      }
      if (mode == "ps" && c == BT) { addq(substr(s, i + 1, 1)); i += 2; continue }
      if (c == "$") { i = dollar(s, i, mode); continue }
      if (mode == "bash" && c == BT) flag = 1
      addq(c); i++; continue
    }
    if (mode == "bash" && c == BT) {
      j = group(s, i, BT, BT, mode)
      cur = cur substr(s, i + 1, j - i - 1); flag = 1; i = j + 1; continue
    }
    if (mode == "ps" && c == "(") {
      j = group(s, i, "(", ")", mode)
      cur = cur substr(s, i + 1, j - i - 1); flag = 1; i = j + 1; continue
    }
    if (mode == "bash" && c == "{") {
      for (j = i + 1; j <= L; j++) {
        e = substr(s, j, 1)
        if (e == "}") break
        if (index(" \t{;&|()<>`$" SQ DQ BS, e)) { j = 0; break }
      }
      if (j && j <= L) {
        inner = substr(s, i + 1, j - i - 1)
        if (index(inner, "..")) { cur = cur substr(s, i, j - i + 1); flag = 1; i = j + 1; continue }
        if (index(inner, ",")) {
          for (k = j + 1; k <= L && !index(" \t;&|()<>{}`$" SQ DQ BS, substr(s, k, 1)); k++) ;
          suf = substr(s, j + 1, k - j - 1); pre = cur; cur = ""
          np = split(inner, A, ",")
          for (a = 1; a <= np; a++) { cur = pre A[a] suf; flag = 1; flush() }
          i = k; continue
        }
      }
    }
    if (c == "<" || c == ">") {
      if (cur !~ /^[0-9]+$/) flush()
      for (j = i; j <= L && index("<>", substr(s, j, 1)); j++) ;
      cur = cur substr(s, i, j - i); flush(); i = j; continue
    }
    if (index(" \t(){}", c)) { flush(); i++; continue }
    if (c == SQ || c == DQ) { q = c; i++; continue }
    if ((mode == "bash" && c == BS) || (mode == "ps" && c == BT)) { addq(substr(s, i + 1, 1)); i += 2; continue }
    if (c == "$") { i = dollar(s, i, mode); continue }
    if (index("*?[", c)) flag = 1
    cur = cur c; i++
  }
  flush()
  return n
}
function norm(w,    k, c, b) {
  for (k = length(w); k > 0; k--) { c = substr(w, k, 1); if (c == "/" || c == BS) break }
  b = tolower(substr(w, k + 1))
  if (b ~ /\.(exe|cmd|bat|com)$/) b = substr(b, 1, length(b) - 4)
  if (b == "git") return "git"
  if (b ~ /^git-(push|reset|clean|checkout|restore|branch|switch)$/) return "git " substr(b, 5)
  return w
}
function render(cnt, r, quote, x,    k, w, o, out, sawgit, ag, skip) {
  out = ""; sawgit = 0; ag = 0; skip = 0
  for (k = 1; k <= cnt; k++) {
    w = (k == r) ? "git" : W[k]
    o = norm(w)
    if (o != w && sawgit && k != x) o = w
    if (o == "git" || o ~ /^git /) { sawgit = 1; ag = (o == "git") }
    else if (ag) {
      if (skip) skip = 0
      else if (substr(w, 1, 1) == "-") { if (index(VALOPT, " " w " ")) skip = 1 }
      else { if (o == w && !index(w, " ") && !index(w, "\t")) o = tolower(w); ag = 0 }
    }
    if (quote && o == w && (index(w, " ") || index(w, "\t"))) {
      if (!index(w, DQ)) o = DQ w DQ; else if (!index(w, SQ)) o = SQ w SQ
    }
    out = out (out == "" ? "" : " ") o
  }
  return out
}
function collapse(t) { gsub(/[ \t]+/, " ", t); sub(/^ /, "", t); sub(/ $/, "", t); return t }
function emit(note, text,    key) {
  key = collapse(text)
  if (key == "" || key in seen) return
  if (text !~ /(^|[^A-Za-z0-9_.-])git(\.exe)?([ \t]|$)/) return
  seen[key] = 1
  print note US text
}
function readings(seg, v0,    m, mode, s, pass, cnt, k, nx, r) {
  if (seg ~ /^[ \t]*$/) return
  split("", seen)
  seen[collapse(seg)] = 1
  if (v0) print US seg
  for (m = 1; m <= 2; m++) {
    mode = (m == 1) ? "bash" : "ps"
    s = seg
    for (pass = 1; pass <= 3; pass++) {
      cnt = lex(s, mode)
      emit("", render(cnt, 0, 1, 0))
      for (k = 1; k < cnt; k++) {
        nx = tolower(W[k + 1])
        if (F[k] && (index(VERBS, " " nx " ") || substr(nx, 1, 1) == "-")) emit(W[k], render(cnt, k, 1, 0))
        if (norm(W[k]) != W[k] && index(VERBS, " " nx " ")) emit("", render(cnt, 0, 1, k))
      }
      r = render(cnt, 0, 0, 0)
      if (r == s) break
      s = r
    }
  }
}
function toplevel(s,    i, c, q, depth, bt, start, L2) {
  nt = 0; q = ""; depth = 0; bt = 0; start = 1; L2 = length(s)
  for (i = 1; i <= L2; i++) {
    c = substr(s, i, 1)
    if (q != "") { if (c == q) q = ""; else if (q == DQ && c == BS) i++; continue }
    if (c == BS) { i++; continue }
    if (c == SQ || c == DQ) { q = c; continue }
    if (c == BT) { bt = !bt; continue }
    if (c == "(") { depth++; continue }
    if (c == ")") { if (depth > 0) depth--; continue }
    if (depth || bt) continue
    if (c == ";" || c == "&" || c == "|") {
      T[++nt] = substr(s, start, i - start)
      if ((c == "&" || c == "|") && substr(s, i + 1, 1) == c) i++
      start = i + 1
    }
  }
  T[++nt] = substr(s, start)
}
{
  toplevel($0)
  for (t = 1; t <= nt; t++) {
    tt = T[t]
    gsub(/(&&|\|\||;|\||&)/, "\n", tt)
    np = split(tt, P, "\n")
    for (p = 1; p <= np; p++) readings(P[p], 1)
    if (np > 1) readings(T[t], 0)
  }
}'

# Split on shell separators (&&, ||, ;, |, &) and check each segment on its
# own. The `&` and `|` of a redirection (`2>&1`, `&>file`, `>|file`) are not
# separators: reduce those to a plain `>` first, so `git push 2>&1 origin
# main` stays one segment. Each reading of a segment is checked in turn.
# The readings are built first: if awk is missing or fails, or prints
# nothing for a command that is not blank, the hook blocks rather than
# check nothing.
# The awk program splits each command twice: on every separator, as before
# (each piece judged as it is and by its readings), and only on separators
# outside quotes, parentheses and backticks (a piece that holds more than
# one of the first kind is also read whole).
views_of() {
  printf '%s\n' "$1" | sed -E -e 's/&>/>/g' -e 's/>&/>/g' -e 's/>\|/>/g' \
    | LC_ALL=C awk "$VIEWS_AWK"
}
VIEWS=$(views_of "$COMMAND") || block "the hook could not read the command (awk failed)"
if [[ -z "$VIEWS" && -n "${COMMAND//[[:space:];&|]/}" ]]; then
  block "the hook could not read the command (no readings)"
fi
# Bash removes a backslash-newline and joins the words around it. The text
# above reads it as a space; the joined text is read as well.
COMMAND_JOINED=$(printf '%s' "$RAW" | sed -e 's/\\\\/\x01/g' \
  -e 's/\x01\(\\r\)\{0,1\}\\n//g' -e 's/`\(\\r\)\{0,1\}\\n/ /g' \
  -e 's/\\[nr]/;/g' -e 's/\\t/ /g' -e 's/\\"/"/g' -e 's/\\\//\//g' \
  -e 's/\x01/\\/g')
if [[ "$COMMAND_JOINED" != "$COMMAND" ]]; then
  MORE=$(views_of "$COMMAND_JOINED") || block "the hook could not read the command (awk failed)"
  VIEWS+=$'\n'"$MORE"
fi
while IFS=$'\x1f' read -r note view; do
  VIEW_NOTE=""
  [[ -n "$note" ]] && VIEW_NOTE=" (cannot tell whether '$note' is git — name git literally)"
  check_segment "$view"
done <<< "$VIEWS"

exit 0
