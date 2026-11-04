# PROJECT-RULES

This file holds this repository's own rules for builders. The rules every
project shares are in the `session-rules` skill. This file adds to them and
never loosens its "Never" lines. The project's own rules in `CLAUDE.md` also
apply.

This repository has no planner or manager of its own. The dynasty project's
planner writes the tickets and briefs, and its builder manager dispatches
builders here and merges their PRs. The owner's queue is that project's
`NEEDS-OWNER.md`: a builder here parks by messaging the manager, never by
writing a queue file here.

## Green means all of

- every CI check (`pytest (ubuntu-latest)`, `pytest (windows-latest)`,
  `CATALOG.md is current`) passes on one read of
  `gh pr view <n> --json mergeStateStatus,statusCheckRollup`;
- `.venv/Scripts/python.exe -m pytest -q tests`, gated on its exit code;
- after any change to a skill, a hook, an agent or `manifest.json`:
  `.venv/Scripts/python.exe tools/build_catalog.py`, then
  `git diff --exit-code -- CATALOG.md` (commit the rebuilt file);
- the `check-in-hygiene` pre-commit hook passes on the commit.

## Never, in this project

- Running `tools/update_vendor_skills.py --apply` (a re-vendor). The owner
  starts one, and `vendor-sync-reapply` follows it.
- Editing anything under `~/.claude/` directly. `~/.claude/agents`,
  `~/.claude/hooks/*` and `~/.claude/skills/*` are links into this
  repository's main checkout, so a change here goes live only when the main
  checkout is updated after merge. A builder never touches the main checkout.
- Switching branches, committing or pulling in the main checkout.

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
