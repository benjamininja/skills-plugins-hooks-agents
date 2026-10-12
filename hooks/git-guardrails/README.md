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
    that's `main`/`master`.
  - An explicit non-main branch named (`git push origin my-feature`) →
    always allowed, even if `main` happens to be checked out locally.
- **`reset --hard` / `clean -f` / `branch -D` / `checkout .` / `restore .`
  stay blanket-blocked** — these are destructive regardless of branch, so no
  branch-aware logic applies (kept per explicit decision when this hook was
  built, 2026-07-11). Matching is by meaning, not by one spelling: any flag
  cluster containing `f` on `clean` (`-df`, `-xdf`, `--force`), `--hard`
  anywhere after `reset`, `checkout -- .`. `git restore --staged .` is
  allowed (it only unstages).
- **Global options are stripped before matching** (2026-10-12).
  `git -C <path> push origin main`, `git -c k=v reset --hard` and
  `git --git-dir=<dir> clean -fd` used to pass because the match was on the
  literal text `git push` / `git clean -f`. A bare push with `-C <path>`
  looks up the branch checked out in that path, not in the session's repo.
- **Each `&&` / `||` / `;` / `|` segment is checked on its own.**
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
- a `cd` in an earlier tool call (a bare `git push` is judged against the
  session's repo unless `-C <path>` is given)
- a direct terminal `git push`, or another machine

The layer that cannot be bypassed locally is the GitHub ruleset on `main`
(require a pull request, no direct pushes). This hook is the seatbelt in
front of it, and the only layer covering the local-only destructive
commands (`reset --hard`, `clean -f`, ...).

## Install (global — one machine-wide install, works in every repo)

1. Link this folder into `~/.claude/hooks/git-guardrails` with
   `tools/relink_live.ps1` (see the repo README's Installation section).
2. Merge `settings-snippet.json`'s `hooks.PreToolUse` entry into
   `~/.claude/settings.json` (merge into the existing `PreToolUse` array if
   one is already there — don't overwrite other hooks or settings). The
   matcher is `Bash|PowerShell`: both tools pass the command as
   `tool_input.command`.
3. No other dependencies — works with the shell tools already present in
   Claude Code's Bash environment (GNU `sed`, `grep`).

## Tests

`tests/test_git_guardrails.py` feeds the hook the JSON a `PreToolUse` hook
receives and asserts blocked (exit 2) or allowed (exit 0) for every pattern
and every bypass found so far. It runs in CI on Ubuntu and Windows
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
