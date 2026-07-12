# skill-catalog-health

A `SessionStart` hook with two jobs, both driven by the same scan of
`~/.claude/skills/` (see [ADR-0005](../../docs/adr/0005-skill-routing-and-drift-detection.md)
for the full reasoning):

1. **Routing index** — injects a compact list of every installed skill
   (name + one-line trigger, generated from each `SKILL.md`'s frontmatter
   `description`), split **User-invoked** (`disable-model-invocation: true`
   — needs an explicit `/command`) vs **Model-invoked** (Claude Code can
   already reach for it on its own). Mirrors the format upstream
   `mattpocock/skills`' own `README.md` Reference section already uses.
   This doesn't change any skill's invocation mode — router skills stay
   exactly as manual as they were — it just makes their existence and
   trigger conditions ambient at the start of every session, so a
   deliberately-manual skill (`wayfinder`, `to-spec`, `triage`, ...) can
   still get suggested instead of silently forgotten.
2. **Drift detection** — flags any `~/.claude/skills/*` junction/symlink
   whose target no longer exists (broken by a renamed or moved source
   repo folder — exactly what happened to every skill in this catalog for
   several weeks, undetected, before this hook existed). Reports only;
   does not attempt to auto-relink, since guessing the new path risks
   silently linking to the wrong repo.

Generated at runtime, not hand-maintained — the index can't go stale the
way the junction targets did, because it's re-derived from the actual
`SKILL.md` files on every session start.

## Install (global — one machine-wide install, works in every repo)

1. Copy the script to a fixed, machine-wide location:
   ```bash
   mkdir -p "$HOME/.claude/hooks/skill-catalog-health"
   cp check.sh "$HOME/.claude/hooks/skill-catalog-health/check.sh"
   ```
2. Merge `settings-snippet.json`'s `hooks.SessionStart` array into
   `~/.claude/settings.json` — **append** to the array if a `SessionStart`
   hook already exists there (e.g. from `continual-learning`), don't
   replace it. Claude Code runs every entry in the array; their outputs
   concatenate into context.

No `sqlite3`/`jq` dependency — pure `bash`/`awk`, works regardless of
`continual-learning`'s activation state.

## Disable

```bash
export SKIP_SKILL_CATALOG_HEALTH=true
```

## Scope

Global (`~/.claude/skills/`) only — project-local `.claude/skills/`
installs aren't scanned in this first pass, since the failure mode this
hook exists to catch (a renamed central-repo folder breaking every
junction) is specific to the machine-wide install path.
