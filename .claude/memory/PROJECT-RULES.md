# PROJECT-RULES

This file holds this repository's own rules for builders. The rules every
project shares are in the `session-rules` skill. This file adds to them and
never loosens its "Never" lines. The project's own rules in `CLAUDE.md` also
apply.

This repository's planner is the standing session **Tools-central-planner**,
since 2026-11-07. It writes the tickets, tiers and briefs here, and keeps
its state in [PLANNER.md](PLANNER.md). The repository has no manager of its
own. The dynasty project's builder manager
(`dynastyFantasyFootball-central-builder-manager`) dispatches builders here
from this planner's `Tier:` and `Profile:` lines, and merges their PRs once
they are Green. The owner gave that merge approval on 2026-11-07: "Yes, it
may merge". The owner's queue is the dynasty project's `NEEDS-OWNER.md`.
Only that manager writes it, so a builder here parks by messaging the
manager, never by writing a queue file here.

Every ticket carries a `Tier:` line at the top of its body and the matching
`tier:` label (`tier:low`, `tier:medium`, `tier:high`, `tier:none`, or
`tier:unset` until the planner sets one). This repository has no
`tier:haiku` label yet: no ticket here has been haiku-tier.

## Green means all of

- every CI check (`pytest (ubuntu-latest)`, `pytest (windows-latest)`,
  `CATALOG.md is current`) passes on one read of
  `gh pr view <n> --json mergeStateStatus,statusCheckRollup`;
- `.venv/Scripts/python.exe -m pytest -q tests`, gated on its exit code;
- after any change to a skill, a hook, an agent or `manifest.json`:
  `.venv/Scripts/python.exe tools/build_catalog.py`, then
  `git diff --exit-code -- CATALOG.md` (commit the rebuilt file);
- the `check-in-hygiene` pre-commit hook passes on the commit;
- after any change under `plugins/owner-queue/`:
  `claude plugin test plugins/owner-queue` passes on the merged tree.
  Manager runs it at re-proof (#113, amendment 1);
- on a PR the code review covers: no blocking finding the manager upheld
  is still open (`session-rules`, `references/code-review.md`). Manager
  runs it. The ruleset skill is `tools-code-review`. This item applies
  once `skills/tools-code-review/` (#113 PR B) and the live
  `.claude/agents/pr-code-reviewer.md` are both on `main`.

The manager re-proves with `tools/reproof.py <pr> <head sha>` from the
live clone (`C:/Users/benha/claude-live/skills-plugins-hooks-agents`), run
with the dynasty `.venv`'s interpreter under the one allow rule in dynasty's
`managers.settings.json`, or with the commands above run directly. Never
with a scratch script (#117). The script runs the merge, pytest and the
`CATALOG.md` check; CI's one read, the `check-in-hygiene` report, the
owner-queue mod test and the code review stay with the manager.

## Never, in this project

- Running `tools/update_vendor_skills.py --apply` (a re-vendor). The owner
  starts one, and `vendor-sync-reapply` follows it.
- Editing anything under `~/.claude/` directly. `~/.claude/agents`,
  `~/.claude/hooks/*` and `~/.claude/skills/*` are links into this
  repository's main checkout, so a change here goes live only when the main
  checkout is updated after merge. A builder never touches the main checkout.
- Switching branches or committing in the main checkout, or pulling it
  outside closeout (below).

## Closeout pulls, in this project

After each merge here, at closeout, the manager brings both tools
checkouts up to date (#112, the owner's answer of 2026-11-09). Live
behaviour comes from these two, so they stay at the same commit:

- **the main checkout**,
  `C:/Users/benha/OneDrive/Documents/GitHub/skills-plugins-hooks-agents`:
  the `~/.claude` skill, agent and hook links point here;
- **the live clone**, `C:/Users/benha/claude-live/skills-plugins-hooks-agents`:
  plugins load from here.

1. Run `git -C <main checkout> fetch origin`, then
   `git -C <main checkout> diff --name-only HEAD origin/main` and
   `git -C <main checkout> status --short`. If an incoming file is one the
   status lists, park an Action with both lists and pull neither checkout.
2. Otherwise run `git -C <path> pull --ff-only` on each. If one refuses or
   fails, park an Action with its output and its `status --short`. A
   OneDrive lock can stop a pull halfway, and the repair is the owner's.
3. Report both new heads (`git -C <path> log -1 --oneline`). If a plugin
   changed, name it and say that running sessions need a new session to
   load it.

## Always parks, in this project

- Any change to `disable-model-invocation`, a new vendored skill, or a
  safety-relevant field of `vendor-skills.json`. Run `skill-safety-auditor`
  first, and park its table for the owner to read.
- A change to a hook's blocking rules (`hooks/git-guardrails/`). Open the PR,
  and the manager runs the hook tests itself before it merges.

## Notes

- `tests/test_agents_frontmatter.py` checks every `.claude/agents/*.md`. A
  new or edited agent must load as YAML, with `name` equal to its file name.
- `/security-review` runs on the diff before a PR opens (`CLAUDE.md`).
