# git-guardrails

A Claude-Code-native `PreToolUse` hook adapted from
[mattpocock/skills](https://github.com/mattpocock/skills)'
[`skills/misc/git-guardrails-claude-code`](https://github.com/mattpocock/skills/tree/main/skills/misc/git-guardrails-claude-code).
Intercepts the Bash and PowerShell tools and blocks dangerous git commands
before they execute. Upstream's hook format already matches Claude Code's;
this is a behavior adaptation.

## What changed from upstream, and why

- **`git push` is branch-aware, not blanket-blocked.** Upstream blocks
  every `git push`. This repo's actual need (see the direct-to-`main`
  incident this hook exists to prevent) is narrower: block pushes that
  *target* `main`/`master`, allow feature-branch pushes through. Detection:
  - An explicit `main`/`master` token anywhere in the command (covers
    `git push origin main`, `git push origin HEAD:main`,
    `git push origin :main` (delete), `git push origin feature:main`) →
    blocked regardless of what's currently checked out.
  - No explicit branch named at all (`git push`, `git push origin`,
    `git push -u origin`) → implicitly targets whatever's checked out;
    falls back to `git rev-parse --abbrev-ref HEAD` and blocks only if
    that's `main`/`master`. The branch is read in this order: the
    command's own `-C` path; then the top-level `cwd` field of the hook
    input, which is the folder the tool call starts in (the worktree, in a
    worktree session); then `CLAUDE_PROJECT_DIR` (the main checkout in a
    worktree session), then `$PWD`. So a plain push from a worktree on a
    feature branch passes while the main checkout sits on `main`, and the
    same push from a worktree on `main` still blocks.
  - **Rule B, an allowlist (owner's decision on #135, replacing a word
    list that kept finding new spellings).** The `cwd` is used, and so the
    `CLAUDE_PROJECT_DIR` lookup skipped, only when the whole command is
    exactly a plain push: one segment (no `;`, `&&`, `||`, `|`, `&`, no
    newline), no wrapper, subshell, substitution, backtick, variable, `$`
    or env prefix, and the words are `git push`, then optionally `-u` or
    `--set-upstream`, then optionally one bare remote name (letters,
    digits, `.`, `_`, `-`, not starting with `-` or `.`). No global git
    option (`-c`, `-C`, `--git-dir`, `--work-tree`, any other), no other
    push flag (`--mirror`, `--all`, `--tags`, `-f`...) and no refspec.
    Anything else, even a command close to a plain push, falls back to the
    old lookup (`-C`, then `CLAUDE_PROJECT_DIR`, then `$PWD`). The Bash and
    the PowerShell tool get the same rule. A directory change is never
    parsed, so a `cd` built any way at all falls back.
  - Only a string-valued `cwd` directly inside the outermost JSON object
    counts, not one nested in `tool_input`. JSON `\\` decodes to a
    backslash. A missing or empty `cwd`, or one that is not a repo, falls
    through to `CLAUDE_PROJECT_DIR`. A `cwd` that is used and is on a
    network path blocks, as a network `-C` path does, and is never given
    to git. Needs `awk` (Git Bash and Linux have it). Source: the Claude
    Code docs, [worktrees](https://code.claude.com/docs/en/worktrees.md)
    and [hooks](https://code.claude.com/docs/en/hooks.md) (#135).
  - An explicit non-main branch named (`git push origin my-feature`) →
    always allowed, even if `main` happens to be checked out locally.
- **`reset --hard` / `clean -f` / `checkout .` / `restore .` stay
  blanket-blocked** — these are destructive regardless of branch, so no
  branch-aware logic applies (kept per explicit decision when this hook was
  built, 2026-07-11). Matching is by meaning, not by one spelling: any flag
  cluster containing `f` on `clean` (`-df`, `-xdf`, `--force`), `--hard`
  anywhere after `reset`, `checkout -- .`. `git restore --staged .` is
  allowed (it only unstages).
- **A force branch delete is allowed only after its PR merged** (owner
  decision 2026-11-03; the repo squash-merges, so plain `-d` always refuses
  a merged branch). Any spelling counts: `-D`, bundles like `-Dq`, `-df`,
  `-fd`, `--delete --force`, `-d --force`, `-d -f`. It passes only when
  every branch it names has a merged PR
  (`gh pr list --head <branch> --state merged --json headRefOid`, run in the
  `-C` dir when one is given, 10 s cap) and the branch's local tip
  (`rev-parse refs/heads/<branch>`) equals that PR's `headRefOid`, so a
  commit made after the PR's last push stays blocked. It blocks when `gh` is
  missing, fails or times out, when no branch is named, when a name is a
  pattern or the segment holds `$` or a backtick, and when `-C` is a network
  path. The message says why (`no merged PR for 'x'`, `'x' has commits after
  its merged PR`). Text after a `#` never adds a name. Deleting the checked-out
  branch stays git's own refusal; `push --delete` is unchanged (the push rules
  cover it). Needs `gh` on `PATH` and a GitHub remote in the repo.
- **Global options are stripped before matching** (2026-10-12).
  `git -C <path> push origin main`, `git -c k=v reset --hard` and
  `git --git-dir=<dir> clean -fd` used to pass because the match was on the
  literal text `git push` / `git clean -f`. A bare push with `-C <path>`
  looks up the branch checked out in that path, not in the session's repo.
- **Each `&&` / `||` / `;` / `|` / `&` segment is checked on its own**, and
  a line continuation (`\` or a PowerShell backtick before a newline) is
  joined first, so a push cannot be separated from its refspec.
- **Shell punctuation is read as spaces.** Quotes, backticks, parentheses,
  braces and `$` become spaces before matching, so `(git push)`,
  `bash -c 'git restore .'` and `git submodule foreach 'git checkout .'`
  are judged like the plain command.
- **Redirections are dropped before matching.** `2>&1`, `&>file`, `>file`
  and `<file` are removed with their target, so `git push 2>&1 origin main`
  and `git clean -fd>/dev/null` are judged like the plain command, and a
  log file is never mistaken for a refspec.
- **Every spelling of the whole tree is blocked** for `checkout` / `restore`:
  `.`, `./`, `./.`, `./*`, `..`.
- **`HEAD` and `@` count as "whatever is checked out"**, so
  `git push origin HEAD` gets the same branch lookup as a bare `git push`.
- **A switch to `main` earlier in the same command blocks a later bare
  push** (`git checkout main && git merge x && git push`), because the
  lookup would otherwise see the branch from before the command ran. So
  does a create flag whose new branch is `main` or `master`
  (`git switch -c main`, `git checkout -B main`, `-bmain`, `--create=main`,
  `--ignore-other-worktrees -C main`); a create flag for any other branch
  clears it.
- **When in doubt it blocks.** Text after a `#` still counts toward a
  block and never toward an exemption, so
  `git push origin my-feature # not main` is blocked. Reword the comment.
- **No `jq` dependency.** Upstream's script requires `jq` to parse
  `tool_input.command`; `jq` is not reliably on `PATH` in this machine's Git
  Bash, so extraction uses `sed`. It honors escaped quotes, so a command
  containing `"` (a quoted path, a commit message) is read in full — the
  original extraction stopped at the first quote and missed everything after
  it.

## Layered-defense note

This hook is a text match on one tool call made by **Claude Code itself**.
It does not see:

- git run from inside a script, a Makefile, or a shell alias/function
- `gh api` or any other tool that writes to the remote without `git push`
- a `cd` in an earlier tool call, or one built at run time. A bare
  `git push` is judged against the folder the hook input's `cwd` names
  (where the tool call starts) unless `-C <path>` is given or the command
  is not exactly a plain push (rule B above), which falls back to
  `CLAUDE_PROJECT_DIR`
- a direct terminal `git push`, or another machine

The layer that cannot be bypassed locally is the GitHub ruleset on `main`
(require a pull request, no direct pushes). This hook is the seatbelt in
front of it, and the only layer covering the local-only destructive
commands (`reset --hard`, `clean -f`, ...).

The force-delete exemption trusts `gh`'s answer for the current repo's remote;
it does not see a branch deleted from a script, an alias or a terminal.

## Install (global — one machine-wide install, works in every repo)

1. Link this folder into `~/.claude/hooks/git-guardrails` with
   `tools/relink_live.ps1` (see the repo README's Installation section).
2. Merge `settings-snippet.json`'s `hooks.PreToolUse` entry into
   `~/.claude/settings.json` (merge into the existing `PreToolUse` array if
   one is already there — don't overwrite other hooks or settings). The
   matcher is `Bash|PowerShell`: both tools pass the command as
   `tool_input.command`.
3. No other dependencies — works with the shell tools already present in
   Claude Code's Bash environment (`sed`, `grep`, `awk`).

## Tests

`tests/test_git_guardrails.py` feeds the hook the JSON a `PreToolUse` hook
receives and asserts blocked (exit 2) or allowed (exit 0) for every pattern
and every bypass found so far; `gh` is a PATH shim there, so no network and no
branch is touched. It runs in CI on Ubuntu and Windows
(`.github/workflows/test.yml`). Locally: `pip install pytest pyyaml`, then
`python -m pytest -q tests`. A new bypass lands as a pinned case alongside
its fix.

## Verify

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | ./block-dangerous-git.sh
# exit 2, BLOCKED message on stderr

echo '{"tool_input":{"command":"git push origin my-feature-branch"}}' | ./block-dangerous-git.sh
# exit 0, silent
```
