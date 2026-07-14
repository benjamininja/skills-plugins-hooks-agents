#!/bin/bash
# skill-catalog-health — SessionStart hook.
# Reports any broken ~/.claude/skills/* junction/symlink so a repo-folder
# rename can't silently strand every skill again (see docs/adr/0005). Silent
# on the happy path — Claude Code's own SessionStart already surfaces the
# skill catalog natively, so this hook doesn't re-dump it.
#
# Usage: check.sh sessionStart

set -uo pipefail

[[ "${SKIP_SKILL_CATALOG_HEALTH:-}" == "true" ]] && exit 0

SKILLS_DIR="$HOME/.claude/skills"
[[ -d "$SKILLS_DIR" ]] || exit 0

broken=()

for entry in "$SKILLS_DIR"/*; do
  name=$(basename "$entry")
  [[ "$name" == .* ]] && continue          # dotfiles/dirs (e.g. .claude)
  [[ "$name" == *.skill ]] && continue     # packaged .skill files, not folders

  if [[ -L "$entry" && ! -e "$entry" ]]; then
    broken+=("$name")
  fi
done

output=""

if [[ ${#broken[@]} -gt 0 ]]; then
  output+="⚠️ skill-catalog-health: broken skill link(s) in ~/.claude/skills/ — probably a renamed/moved source repo (see docs/adr/0005-skill-routing-and-drift-detection.md):\n"
  for b in "${broken[@]}"; do
    output+="  - ${b}\n"
  done
  output+="Relink via the Installation section of the skill source repo's README once you've confirmed its current path.\n\n"
fi

[[ -n "$output" ]] && echo -e "$output"
exit 0
