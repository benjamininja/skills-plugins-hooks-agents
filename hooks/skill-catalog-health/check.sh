#!/bin/bash
# skill-catalog-health — SessionStart hook.
# Injects a compact routing index (mirrors mattpocock/skills' own README
# Reference section format) so router skills that are deliberately
# disable-model-invocation: true still get surfaced as suggestions, and
# reports any broken ~/.claude/skills/* junction/symlink so a repo-folder
# rename can't silently strand every skill again (see docs/adr/0005).
#
# Usage: check.sh sessionStart

set -uo pipefail

[[ "${SKIP_SKILL_CATALOG_HEALTH:-}" == "true" ]] && exit 0

SKILLS_DIR="$HOME/.claude/skills"
[[ -d "$SKILLS_DIR" ]] || exit 0

broken=()
user_invoked=()
model_invoked=()

for entry in "$SKILLS_DIR"/*; do
  name=$(basename "$entry")
  [[ "$name" == .* ]] && continue          # dotfiles/dirs (e.g. .claude)
  [[ "$name" == *.skill ]] && continue     # packaged .skill files, not folders

  if [[ -L "$entry" && ! -e "$entry" ]]; then
    broken+=("$name")
    continue
  fi

  skill_md="$entry/SKILL.md"
  [[ -f "$skill_md" ]] || continue

  # Frontmatter is the block between the first two '---' lines.
  frontmatter=$(awk '/^---$/{c++; next} c==1' "$skill_md")

  # `description:` may be a plain scalar on the same line, or a YAML block
  # scalar (`|`/`>`/`>-`) whose text is on the following indented lines.
  description=$(echo "$frontmatter" | awk '
    /^description:/ {
      line=$0
      sub(/^description: */, "", line)
      if (line ~ /^[|>][-+]?[ \t]*$/) { collecting=1; buf=""; next }
      gsub(/^"|"$/, "", line)
      print line
      exit
    }
    collecting {
      if ($0 ~ /^[ \t]+/) {
        t=$0
        sub(/^[ \t]+/, "", t)
        buf = (buf=="" ? t : buf " " t)
      } else { print buf; collecting=0; exit }
    }
    END { if (collecting && buf != "") print buf }
  ')
  [[ -z "$description" ]] && continue

  line="- **${name}** — ${description}"

  if echo "$frontmatter" | grep -q '^disable-model-invocation: *true'; then
    user_invoked+=("$line")
  else
    model_invoked+=("$line")
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

if [[ ${#user_invoked[@]} -gt 0 || ${#model_invoked[@]} -gt 0 ]]; then
  output+="Available skill routing (user-invoked skills need an explicit /command; model-invoked skills you can already reach for on your own judgment):\n\nUser-invoked:\n"
  for l in "${user_invoked[@]}"; do
    output+="${l}\n"
  done
  output+="\nModel-invoked:\n"
  for l in "${model_invoked[@]}"; do
    output+="${l}\n"
  done
fi

[[ -n "$output" ]] && echo -e "$output"
exit 0
