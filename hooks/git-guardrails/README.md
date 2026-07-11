# git-guardrails

A Claude-Code-native `PreToolUse` hook adapted from
[mattpocock/skills](https://github.com/mattpocock/skills)'
[`skills/misc/git-guardrails-claude-code`](https://github.com/mattpocock/skills/tree/main/skills/misc/git-guardrails-claude-code).
Intercepts the Bash tool and blocks dangerous git commands before they
execute. No porting needed here (unlike `continual-learning`) — upstream's
hook format already matches Claude Code's; this is a behavior adaptation.

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
- **`reset --hard` / `clean -f(d)` / `branch -D` / `checkout .` / `restore .`
  stay blanket-blocked, unchanged** — these are destructive regardless of
  branch, so no branch-aware logic applies (kept per explicit decision when
  this hook was built, 2026-07-11).
- **No `jq` dependency.** Upstream's script requires `jq` to parse
  `tool_input.command`. This repo's own `continual-learning` hook found
  `jq` missing on this machine's Git Bash — since this hook is meant to be
  active *today*, not parked behind the same install decision, command
  extraction uses `sed` instead.
  **ponytail-flagged limitation**: the `sed` extraction stops at the first
  literal `"` in the JSON value — a command containing an embedded double
  quote (rare for git commands, but possible in e.g. a commit message
  passed inline) will parse wrong. Upgrade to `jq` if that ever bites.

## Layered-defense note

This hook only intercepts when **Claude Code itself** runs git via the Bash
tool. It does not stop a direct terminal `git push`, another tool, or
another machine — an absolute "never push to `main`" guarantee needs at
least one more layer (a `.git/hooks/pre-push` check and/or GitHub branch
protection on `main`, which can't be bypassed locally at all). This hook is
one layer, not the whole guarantee.

## Install (global — one machine-wide install, works in every repo)

1. Copy the script to a fixed, machine-wide location:
   ```bash
   mkdir -p "$HOME/.claude/hooks/git-guardrails"
   cp block-dangerous-git.sh "$HOME/.claude/hooks/git-guardrails/block-dangerous-git.sh"
   chmod +x "$HOME/.claude/hooks/git-guardrails/block-dangerous-git.sh"
   ```
2. Merge `settings-snippet.json`'s `hooks.PreToolUse` entry into
   `~/.claude/settings.json` (merge into the existing `PreToolUse` array if
   one is already there — don't overwrite other hooks or settings).
3. No other dependencies — works with the shell tools already present in
   Claude Code's Bash environment.

## Verify

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | ./block-dangerous-git.sh
# exit 2, BLOCKED message on stderr

echo '{"tool_input":{"command":"git push origin my-feature-branch"}}' | ./block-dangerous-git.sh
# exit 0, silent
```
