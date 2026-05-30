# skills

A collection of reusable [Claude Code](https://claude.ai/code) skills — modular instruction sets that extend Claude's capabilities for specific domains and workflows. Skills are activated in Claude Code via the Skill tool or `/skill-name` slash commands.

---

## Repository Structure

```
skills/
├── caveman/                          # Token-compression communication skill
│   └── SKILL.md
├── benjamininja/                     # User-namespaced skills
│   └── fantasy-football-python/      # Dynasty fantasy football ETL skill
│       ├── SKILL.md
│       └── references/
│           └── data_model.md
└── mbtiusa/                          # MBTI resources (submodule)
    └── awesome-mbti/                 # Curated MBTI links & resources
```

---

## Skills

### `caveman`
**Path:** `caveman/`

Token-compression communication skill. Strips filler, preamble, hedging, and pleasantries while leaving all technical content untouched. Two intensity modes:

| Mode | Behavior |
|------|----------|
| **lite** (default) | Full grammar, no filler words or pleasantries |
| **ultra** | Telegraphic fragments, dropped articles, arrows for causality |

> Technical content (code, file paths, error messages, identifiers) always passes through unmodified.

**Trigger:** `/caveman`, `/caveman ultra`, `/caveman lite`

---

### `fantasy-football-python`
**Path:** `benjamininja/fantasy-football-python/`

Expert Python Data Engineer and Fantasy Sports Architect skill for a 28-team, dual-conference dynasty fantasy football league. Covers the full ETL stack for the [Python-PowerBI-DynastyFantasyFootball](https://github.com/benjamininja/Python-PowerBI-DynastyFantasyFootball) project.

**Key domains:**
- Rookie draft pipelines, combine/pro-day data, expert ranking composites
- Salary cap calculations ($500M cap, 3-year contracts, dead money)
- Fantrax scraping (Playwright for JS-rendered pages, BeautifulSoup4 for static)
- Star-schema Parquet storage: `dim_*` dimensions + `fact_*` tables
- Jupyter notebook conventions (no bare `.py` ETL scripts)

**Trigger:** Automatically activates on any work touching the dynasty league ETL notebooks, nflverse/nflreadpy data, Fantrax ADP, or the star-schema tables.

---

## Submodules

### `mbtiusa/awesome-mbti`
**Source:** [https://github.com/mbtiusa/awesome-mbti](https://github.com/mbtiusa/awesome-mbti)

A curated list of MBTI-related resources, tools, research, and community links.

To initialize after cloning this repo:

```bash
git submodule update --init --recursive
```

---

## Usage

Skills are loaded by Claude Code automatically when a task matches the skill's trigger conditions, or manually via slash commands. Each `SKILL.md` file contains the full instruction set Claude follows when the skill is active.

To install skills from this repo into your Claude Code environment, reference the skill paths in your `.claude/settings.json` or install via the Claude Code skill registry.

---

## Contributing

Skills follow a namespace convention: shared/general skills live at the root (e.g., `caveman/`), while user-specific skills are namespaced under a folder matching the GitHub username (e.g., `benjamininja/`).

Each skill requires a `SKILL.md` at its root with at minimum:
- A name and one-line description
- Trigger conditions
- The full instruction set
