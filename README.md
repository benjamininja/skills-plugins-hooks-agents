# skills-plugins-hooks-agents

The central repository for [Claude Code](https://claude.ai/code) skills, plugins, and hooks — modular instruction sets, bundled plugin packages, and event-triggered automations. Every skill lives at a flat, loadable path (`skills/<name>/SKILL.md`) so the whole collection can be dropped straight into a Claude Code skills directory.

Some skills are authored here; others are vendored from upstream projects and credited below. Attribution lives in this README and in each skill's `SKILL.md` — not in the folder names.

---

## Repository Structure

```
.
├── manifest.json                               # top-level inventory: skills / plugins / hooks membership
├── vendor-skills.json                          # manifest: pins each vendored skill's upstream commit + forks
├── vendor-cache/                               # pristine, never-loaded mirrors of forked skills (diff target)
│   └── code-review/                            # upstream mirror of engineering/code-review
├── tools/
│   └── update-vendor-skills.ipynb              # checks upstream for newer versions & re-pins
├── skills/                                     # every folder here gets symlinked/loaded as one library
│   ├── caveman/                                # token-compression communication (prose)
│   ├── ponytail/                                # YAGNI/minimal-diff discipline for code generation (pairs with caveman)
│   ├── ponytail-debt/                           # harvest `ponytail:` shortcut comments into a ledger
│   ├── fantasy-football-python/                # dynasty fantasy football ETL
│   │   └── references/data-model.md
│   ├── frontend-design/                        # production-grade frontend UI (+ LICENSE.txt)
│   ├── azure-resource-manager-playwright-dotnet/   # Azure Playwright Testing ARM SDK (.NET)
│   ├── everything-claude-code/                 # Claude Code conventions reference
│   ├── grill-me/                               # stress-test a plan via interview (no codebase)
│   ├── grilling/                               # sequential interview discipline (grill-with-docs dependency)
│   ├── domain-modeling/                        # CONTEXT.md/ADR discipline (grill-with-docs dependency)
│   ├── grill-with-docs/                        # thin pointer: runs /grilling using /domain-modeling
│   ├── handoff/                                # compact a session into a handoff doc
│   ├── ask-matt/                               # router over the idea→ship engineering flow below
│   ├── codebase-design/                        # deep-module vocabulary (module/interface/depth/seam)
│   ├── diagnosing-bugs/                        # diagnosis loop for hard bugs/perf regressions
│   ├── implement/                              # build a spec/ticket via /tdd, closes with /two-axis-code-review
│   ├── improve-codebase-architecture/          # scan for deepening opportunities, visual HTML report
│   ├── prototype/                              # throwaway code to answer a design question
│   ├── resolving-merge-conflicts/              # resolve an in-progress git merge/rebase conflict
│   ├── setup-matt-pocock-skills/               # bootstrap: issue tracker, triage labels, doc layout
│   ├── setup-project-memory/                   # full bootstrap: memory tier + setup-matt-pocock-skills + pre-commit/check-in-hygiene
│   ├── subagent-audit/                         # structural audit: where a repo should delegate to subagents (vs hooks/skills)
│   ├── tdd/                                    # red-green-refactor discipline, seam-based testing
│   ├── to-spec/                                # synthesize the conversation into a spec/PRD
│   ├── to-tickets/                             # break a spec into tracer-bullet tickets with blocking edges
│   ├── triage/                                 # state machine for incoming issues/external PRs
│   ├── two-axis-code-review/                   # FORK of code-review: Standards+Spec review (see below)
│   ├── wayfinder/                              # chart huge, foggy efforts as a shared ticket map
│   ├── teach/                                  # multi-session teaching workspace for any topic
│   ├── writing-great-skills/                   # reference for authoring skills well
│   ├── microsoft-docs/                         # query official Microsoft Learn docs (MCP + CLI fallback)
│   ├── semantic-model-authoring/                # DAX/TMDL/PBIP semantic model authoring
│   ├── powerbi-report-authoring/               # PBIR/PBIP report file mechanics
│   ├── powerbi-report-design/                  # report archetypes, layout, theming, accessibility
│   ├── powerbi-report-management/              # Fabric report item CRUD via REST API
│   ├── powerbi-report-planning/                # requirements, page plan, approval gate
│   └── _powerbi-authoring-common/              # NOT a skill (no SKILL.md) — shared reference docs
│       ├── COMMON-CLI.md                       #   for the powerbi-authoring family above
│       ├── COMMON-CORE.md
│       └── ITEM-DEFINITIONS-CORE.md
├── plugins/
│   └── fabric-collection/                      # manifest-only: fabric-authoring/operations/skills (see plugins/README.md)
└── hooks/                                      # standalone event-triggered hooks — continual-learning + git-guardrails + skill-catalog-health, all installed and active (see hooks/README.md)
```

`manifest.json` tracks *membership* (what's in this repo, by category). `vendor-skills.json` tracks *provenance* (upstream repo/commit for vendored skills, plus a `forks[]` list for skills that diverged from a faithful vendor copy) — the two are separate and both authoritative for their own concern.

### Forked skills

A **fork** happens when we need a skill to diverge from its upstream vendor copy — usually a rename to avoid a naming collision — while still being able to diff against upstream later. The pattern: keep a pristine, untouched mirror in `vendor-cache/<name>/` (git-tracked, pinned in `vendor-skills.json` like any normal vendor, but **never symlinked** since `skills/` is loaded wholesale), and put the actual usable, edited version in `skills/<fork-name>/`. `vendor-skills.json`'s `forks[]` array links the two. First (and so far only) case: `two-axis-code-review`, forked from `mattpocock/skills`' `engineering/code-review` to avoid colliding with this repo's existing general-purpose `code-review` skill.

---

## Installation

Claude Code discovers skills **one level deep only** — `~/.claude/skills/<name>/SKILL.md` (personal) or `<repo>/.claude/skills/<name>/SKILL.md` (project-local). It does **not** scan nested subdirectories, so a single symlink pointing `~/.claude/skills/library` at this repo's `skills/` folder will not work — skills would sit two levels deep (`library/<name>/SKILL.md`) and never be found.

Link each skill individually instead. On Windows, `New-Item -ItemType SymbolicLink` needs admin (or Developer Mode enabled to skip elevation) — if neither is available, use a **directory junction** instead (`-ItemType Junction`), which needs no special privilege and behaves the same for local skill discovery:

```powershell
$source = "C:\Users\benha\OneDrive\Documents\GitHub\skills\skills"
Get-ChildItem $source -Directory | ForEach-Object {
    New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\$($_.Name)" -Target $_.FullName
}
```

(Swap `Junction` for `SymbolicLink` if running elevated / Developer Mode is on — true symlinks support cross-volume and relative targets, which junctions don't, but that doesn't matter for a same-drive local install.)

**Junction caveat**: junctions pin an absolute local path baked in at creation time. If this repo's folder is ever moved or renamed, every junction breaks silently (skills stop resolving, no error until Claude Code fails to load them) — re-run the command above to relink.

Re-run this after pulling new skills into the central repo — it's idempotent for existing links (re-run will error on already-linked names; delete stale links first if a skill was renamed/removed centrally). Each `skills/<name>/SKILL.md` is also self-contained and loadable on its own if you only want one.

### Cross-tool discovery (VS Code Agents window / GitHub Copilot)

The same `~/.claude/skills/` symlinks above also feed VS Code's native
Agents-window Skills panel — per its
[Agent Skills docs](https://code.visualstudio.com/docs/agent-customization/agent-skills),
it discovers project skills from `.github/skills/`, `.claude/skills/`, and
`.agents/skills/`, and personal skills from `~/.copilot/skills/`,
`~/.claude/skills/`, and `~/.agents/skills/` — built on the
[agentskills.io](https://agentskills.io) open standard, which GitHub Copilot
also reads. No separate distribution step needed for that surface.

For a **project-scoped subset** (a repo that should only see some skills,
not the whole library) — not a pattern used yet, but natively
supported whenever it's needed: symlink individual skill folders into that
repo's `.claude/skills/<name>/` the same way, instead of (or in addition to)
the personal `~/.claude/skills/`.

---

## Skills

### Authored / maintained here

| Skill | Description | Trigger |
|-------|-------------|---------|
| **caveman** | Token-compression communication. Strips filler, preamble, hedging, and pleasantries; technical content passes through untouched. Two modes: **lite** (default, full grammar) and **ultra** (telegraphic fragments). *Modified from [juliusbrussee/caveman](https://github.com/juliusbrussee/caveman).* | `/caveman`, `/caveman ultra`, `/caveman lite` |
| **fantasy-football-python** | Python Data Engineer / Fantasy Sports Architect for a 28-team, dual-conference dynasty league. Rookie draft pipelines, combine data, salary cap ($500M / 3-yr contracts), Fantrax scraping, star-schema Parquet, Jupyter conventions. | Auto-activates on dynasty league ETL, nflverse/nflreadpy, Fantrax ADP, or the star-schema tables |
| **setup-project-memory** | Full project bootstrap in one pass: memory-tier scaffold (from `project-memory-template`), `setup-matt-pocock-skills` config, and `check-in-hygiene` pre-commit wiring. See [ADR-0005](docs/adr/0005-skill-routing-and-drift-detection.md). | `/setup-project-memory` (explicit invocation only) |
| **subagent-audit** | Structural audit of a repo for high-ROI subagent opportunities across six categories (context firewall, adversarial auditor, schema transformer, MCP wrapper, background specialist, parallel dispatch) — with a hard hook-vs-skill-vs-subagent boundary and a 3–5 candidate cap. Outputs ready-to-drop-in `.claude/agents/*.md` drafts and persists reasoning to the target repo's memory scaffold. *Adapted from a community audit-prompt design.* | "audit for subagents", "where should we use subagents", `/subagent-audit` |

### Vendored from upstream

**Code-generation discipline** (pairs with `caveman`, doesn't compete with it — caveman governs prose, ponytail governs what gets built):

| Skill | Description | Source |
|-------|-------------|--------|
| **ponytail** | YAGNI ladder for any coding task: does this need to exist → reuse what's here → stdlib → native → existing dependency → one line → minimum code. Auto-active every response, default intensity `full`. | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) |
| **ponytail-debt** | Harvests `ponytail:` shortcut-comment markers (deliberate simplifications with a named ceiling/upgrade path) into one tracked ledger. | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) |

**Idea → ship engineering flow** (see `ask-matt` for the full map):

| Skill | Description | Source |
|-------|-------------|--------|
| **grill-with-docs** | Thin orchestrator: runs a `/grilling` session using the `/domain-modeling` skill. Start here when you have a codebase. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **grill-me** | Same relentless interview, but stateless — for when you have no codebase. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **grilling** | Sequential, one-question-at-a-time interview discipline: withhold execution until shared understanding is reached. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **domain-modeling** | Active discipline for building/sharpening a project's domain model: challenge terminology, stress-test with scenarios, maintain `CONTEXT.md` and ADRs inline. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **to-spec** | Synthesize the current conversation into a spec/PRD, publish to the issue tracker. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **to-tickets** | Break a spec/plan into tracer-bullet tickets, each declaring its blocking edges. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **implement** | Build a ticket via `/tdd` at pre-agreed seams, close out with `/two-axis-code-review`. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **tdd** | Red-green-refactor discipline: what a good test is, seams, anti-patterns. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **two-axis-code-review** *(forked)* | Standards + Spec review of a diff against a fixed point, in parallel sub-agents. Forked from upstream `code-review` — renamed to avoid colliding with this repo's general-purpose `code-review` skill. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **triage** | Move incoming issues/external PRs through a state machine: categorize, verify, grill if needed, write agent-ready briefs. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **diagnosing-bugs** | Diagnosis loop for hard bugs/perf regressions — tight feedback loop, then fix with a regression test. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **wayfinder** | Chart a huge, foggy effort as a shared map of investigation tickets, resolved one at a time. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **improve-codebase-architecture** | Scan for deepening opportunities, present as a visual HTML report, grill through the chosen one. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **codebase-design** | Deep-module vocabulary (module, interface, depth, seam, adapter, leverage, locality). | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **prototype** | Small, throwaway program that answers one design question. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **resolving-merge-conflicts** | Resolve an in-progress git merge/rebase conflict. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **ask-matt** | Router: which skill or flow fits your situation, given everything above. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **setup-matt-pocock-skills** | Bootstrap: configures the issue tracker (GitHub/GitLab/local-markdown), triage labels, and domain doc layout the flow above assumes. Run once first. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **handoff** | Compact the current conversation into a handoff document for another agent to pick up. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **teach** | Multi-session teaching workspace for any topic — not engineering-specific. | [mattpocock/skills](https://github.com/mattpocock/skills) |
| **writing-great-skills** | Reference for writing and editing skills well. | [mattpocock/skills](https://github.com/mattpocock/skills) |

**Power BI / Microsoft Fabric** (from `powerbi-authoring`, one of four `skills-for-fabric` bundles — see `plugins/README.md` for why only this one is fully vendored):

| Skill | Description | Source |
|-------|-------------|--------|
| **semantic-model-authoring** | DAX/TMDL/PBIP semantic model authoring — modeling guidelines, naming conventions, DAX perf patterns, Direct Lake. | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) |
| **powerbi-report-planning** | Requirements, page plan, approval gate — first step of the report flow. | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) |
| **powerbi-report-design** | Archetype routing, layout, theme, accessibility. | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) |
| **powerbi-report-authoring** | PBIR/PBIP file mechanics, Desktop reload/screenshot. | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) |
| **powerbi-report-management** | Fabric report item CRUD via REST API. | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) |
| **microsoft-docs** | Query official Microsoft Learn documentation (Azure, .NET, Fabric, Power Platform, etc.) via MCP, with a CLI fallback. | [microsoft/skills](https://github.com/microsoft/skills) |

**Other:**

| Skill | Description | Source |
|-------|-------------|--------|
| **frontend-design** | Create distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. | [anthropics/claude-code](https://github.com/anthropics/claude-code) |
| **azure-resource-manager-playwright-dotnet** | Azure Resource Manager SDK for Microsoft Playwright Testing in .NET — management-plane ops (workspaces, quotas, name availability). | [microsoft/skills](https://github.com/microsoft/skills) |
| **everything-claude-code** | Development conventions and patterns reference generated from the everything-claude-code project. | [affaan-m/ECC](https://github.com/affaan-m/ECC) |

**Deliberately not vendored:**
- Pocock's `research` skill (thin background-agent-reads-primary-sources tool) — the existing `deep-research` skill already covers this with more rigor (multi-source fan-out, adversarial claim verification).
- `skills-for-fabric`'s `check-updates` skill — redundant with this repo's own `vendor-skills.json` / `update-vendor-skills.ipynb` mechanism.
- `skills-for-fabric`'s `fabric-authoring`, `fabric-operations`, and `fabric-skills` bundles beyond their manifests — ~30 skills for Fabric workloads (Spark, Warehouse, KQL/Eventhouse, Eventstreams, Activator, migrations) unused by any project in this repo. See `plugins/README.md`.
- `ponytail-review`/`ponytail-audit` (diff/repo-wide over-engineering scans) — overlap the existing `code-review` (reuse/simplification cleanups, `--fix`) and `simplify` skills. `ponytail-gain`/`ponytail-help` — low-value scoreboard/reference card.

---

## Routing: which skill, when

Cross-cut of the Skills catalog above by **process stage** (Pocock's
idea→ship flow: Plan → Crystallize → Execute) and **domain**, so a session
knows what to reach for without re-deriving it. `ask-matt` is the router if
none of this is obvious in the moment — it's built for exactly that.

**Plan** — before code exists, resolving what to build:

| Skill | Reach for it when |
|-------|-------------------|
| **ask-matt** | Unsure which skill fits — start here |
| **grill-with-docs** / **grill-me** | Stress-test a plan by interview (with codebase / without) |
| **grilling** | The interview discipline itself (used by `grill-with-docs`) |
| **to-spec** | Synthesize the conversation into a spec/PRD |
| **to-tickets** | Break a spec into tracer-bullet tickets |
| **wayfinder** | The effort is huge and foggy — chart it as investigation tickets |
| **triage** | An incoming issue/external PR needs categorizing |
| **prototype** | Need throwaway code to answer one design question |
| **improve-codebase-architecture** | Scan for deepening opportunities before committing to a design |
| **subagent-audit** | Deciding where a repo should delegate to subagents vs hooks/skills/main agent |
| **setup-matt-pocock-skills** | One-time bootstrap — run before using the flow at all |
| **setup-project-memory** | One-time bootstrap — memory scaffold + skills config + pre-commit, in one pass |

**Crystallize** — pinning down the model, during/after Plan:

| Skill | Reach for it when |
|-------|-------------------|
| **domain-modeling** | Terminology needs sharpening, or an ADR/`CONTEXT.md` needs updating |
| **codebase-design** | Talking about module depth, seams, or interfaces |
| **writing-great-skills** | Authoring or editing a `SKILL.md` |
| **teach** | Building a multi-session teaching workspace on any topic |
| **handoff** | Compacting the session into a doc for another agent to pick up |

**Execute** — building/fixing:

| Skill | Reach for it when |
|-------|-------------------|
| **implement** | Building a ticket — drives `/tdd`, closes with `/two-axis-code-review` |
| **tdd** | Writing tests — red-green-refactor, seam discipline |
| **diagnosing-bugs** | Something's broken/throwing/slow and the cause isn't obvious |
| **resolving-merge-conflicts** | An in-progress git merge/rebase has conflicts |
| **two-axis-code-review** | Closing out a ticket-tracked change — Standards + Spec review |
| **ponytail** | Every code-writing turn — YAGNI ladder, auto-active by design |
| **ponytail-debt** | Periodically / end of session — harvest `ponytail:` shortcut markers |

**Domain: Power BI / Microsoft Fabric** — its own internal
Plan→Design→Author→Manage pipeline, not the general one above:

| Skill | Domain stage |
|-------|--------------|
| **powerbi-report-planning** | Plan — requirements, page plan, approval gate |
| **powerbi-report-design** | Design — archetype, layout, theme, accessibility |
| **powerbi-report-authoring** | Author — PBIR/PBIP file mechanics |
| **powerbi-report-management** | Manage — Fabric REST API item CRUD |
| **semantic-model-authoring** | Author (model layer) — DAX/TMDL, Direct Lake |
| **microsoft-docs** | Any stage — "how does X work" research, not Power BI-specific |
| **azure-resource-manager-playwright-dotnet** | Execute-equivalent — Azure Playwright Testing management-plane ops |

**Domain: this user's repos**

| Skill | Domain |
|-------|--------|
| **fantasy-football-python** | `Python-PowerBI-DynastyFantasyFootball` ETL/data-model work |
| **frontend-design** | Any frontend/UI build |

**Cross-cutting / always-on** — not stage-bound:

| Skill | Why it's cross-cutting |
|-------|------------------------|
| **caveman** | Standing communication-style preference, not tied to any stage |
| **everything-claude-code** | Reference doc for Claude Code conventions, consulted as needed |

---

## Sources & Credits

Vendored skills are static copies of a single skill folder from each upstream repo. The authoritative pins live in [`vendor-skills.json`](vendor-skills.json); the table below mirrors it for readability. To check for and apply updates, run [`tools/update-vendor-skills.ipynb`](tools/update-vendor-skills.ipynb) (see **Maintaining vendored skills** below).

| Skill | Upstream repo | Pinned ref | Source path within repo |
|-------|---------------|-----------|-------------------------|
| frontend-design | `anthropics/claude-code` | `295dee8` (v2.1.158) | `plugins/frontend-design/skills/frontend-design/` |
| azure-resource-manager-playwright-dotnet | `microsoft/skills` | `684313b` | `.github/plugins/azure-sdk-dotnet/skills/azure-resource-manager-playwright-dotnet/` |
| everything-claude-code | `affaan-m/ECC` | `64cd1ba` | `.claude/skills/everything-claude-code/` |
| grill-me | `mattpocock/skills` | `e3b90b5` | `skills/productivity/grill-me/` |
| grilling | `mattpocock/skills` | `391a270` | `skills/productivity/grilling/` |
| domain-modeling | `mattpocock/skills` | `391a270` | `skills/engineering/domain-modeling/` |
| grill-with-docs | `mattpocock/skills` | `391a270` | `skills/engineering/grill-with-docs/` |
| handoff | `mattpocock/skills` | `e3b90b5` | `skills/productivity/handoff/` |
| ask-matt | `mattpocock/skills` | `391a270` | `skills/engineering/ask-matt/` |
| codebase-design | `mattpocock/skills` | `391a270` | `skills/engineering/codebase-design/` |
| diagnosing-bugs | `mattpocock/skills` | `391a270` | `skills/engineering/diagnosing-bugs/` |
| implement | `mattpocock/skills` | `391a270` | `skills/engineering/implement/` |
| improve-codebase-architecture | `mattpocock/skills` | `391a270` | `skills/engineering/improve-codebase-architecture/` |
| prototype | `mattpocock/skills` | `391a270` | `skills/engineering/prototype/` |
| resolving-merge-conflicts | `mattpocock/skills` | `391a270` | `skills/engineering/resolving-merge-conflicts/` |
| setup-matt-pocock-skills | `mattpocock/skills` | `391a270` | `skills/engineering/setup-matt-pocock-skills/` |
| tdd | `mattpocock/skills` | `391a270` | `skills/engineering/tdd/` |
| to-spec | `mattpocock/skills` | `391a270` | `skills/engineering/to-spec/` |
| to-tickets | `mattpocock/skills` | `391a270` | `skills/engineering/to-tickets/` |
| triage | `mattpocock/skills` | `391a270` | `skills/engineering/triage/` |
| wayfinder | `mattpocock/skills` | `391a270` | `skills/engineering/wayfinder/` |
| teach | `mattpocock/skills` | `391a270` | `skills/productivity/teach/` |
| writing-great-skills | `mattpocock/skills` | `391a270` | `skills/productivity/writing-great-skills/` |
| code-review *(pristine mirror — see `forks[]`)* | `mattpocock/skills` | `391a270` | `skills/engineering/code-review/` → `vendor-cache/code-review/` |
| microsoft-docs | `microsoft/skills` | `c33193b` | `.github/skills/microsoft-docs/` |
| semantic-model-authoring | `microsoft/skills-for-fabric` | `b961296` | `plugins/powerbi-authoring/skills/semantic-model-authoring/` |
| powerbi-report-authoring | `microsoft/skills-for-fabric` | `b961296` | `plugins/powerbi-authoring/skills/powerbi-report-authoring/` |
| powerbi-report-design | `microsoft/skills-for-fabric` | `b961296` | `plugins/powerbi-authoring/skills/powerbi-report-design/` |
| powerbi-report-management | `microsoft/skills-for-fabric` | `b961296` | `plugins/powerbi-authoring/skills/powerbi-report-management/` |
| powerbi-report-planning | `microsoft/skills-for-fabric` | `b961296` | `plugins/powerbi-authoring/skills/powerbi-report-planning/` |
| powerbi-authoring-common *(→ `skills/_powerbi-authoring-common/`)* | `microsoft/skills-for-fabric` | `b961296` | `plugins/powerbi-authoring/common/` |
| ponytail | `DietrichGebert/ponytail` | `14a0d79` | `.openclaw/skills/ponytail/` |
| ponytail-debt | `DietrichGebert/ponytail` | `14a0d79` | `.openclaw/skills/ponytail-debt/` |

Manifest-only entries (`fabric-authoring`, `fabric-operations`, `fabric-skills`) live under a separate `plugin_manifests_only[]` array in `vendor-skills.json` — see `plugins/README.md`.

### Related (not a skill)

- [mbtiusa/awesome-mbti](https://github.com/mbtiusa/awesome-mbti) — a curated list of MBTI resources, tools, and research.

---

## Maintaining vendored skills

[`tools/update-vendor-skills.ipynb`](tools/update-vendor-skills.ipynb) reads [`vendor-skills.json`](vendor-skills.json) and, for each vendored skill, queries the GitHub API for the latest commit touching its source path:

1. **Check** — running all cells prints a status table (pinned vs latest commit, with a `compare` link for anything out of date).
2. **Update** — `update_skill("<name>", apply=True)` re-downloads that skill's folder from the latest upstream commit, replaces the local copy, and re-pins `vendor-skills.json`. It's a dry run unless `apply=True`.
3. Review the resulting `git diff` before committing — upstream skills can change structure or licensing.

> Set a `GITHUB_TOKEN` environment variable to lift the GitHub API rate limit from 60 to 5,000 requests/hour.

To add a new vendored skill, copy its folder into `skills/` and add a matching entry to `vendor-skills.json`.

---

## Conventions

- One skill per folder under `skills/`, named for the skill, each with a `SKILL.md` at its root.
- `SKILL.md` frontmatter carries `name` and `description` (and a trigger hint in the description).
- Authored skills and vendored copies live side by side; provenance is tracked in **Sources & Credits**, not in the directory layout.

---

## Roadmap

`hooks/` is scaffolded but intentionally empty; `plugins/` now holds manifest-only Fabric bundles. Status:

- ~~**Vendor drift fix**: `grill-with-docs` had diverged from upstream.~~ **Done** — both dependencies (`grilling`, `domain-modeling`) vendored, `grill-with-docs` realigned to upstream's thin pointer.
- ~~**Saturate `mattpocock/skills`**: evaluate the full `productivity`/`engineering` catalog.~~ **Done** — adopted the full idea→ship engineering flow (see Skills table above) using its local-markdown tracker mode. Skipped `research` (redundant with `deep-research`). Forked `code-review` → `two-axis-code-review` (naming collision with the existing general-purpose `code-review` skill) using the `vendor-cache/` pristine-mirror pattern documented above.
- ~~**mattpocock/skills hooks check**~~ **Done** — no `hooks/` directory exists upstream; nothing left behind.
- ~~**microsoft-docs skill**~~ **Done** — vendored for Microsoft research/planning scoping.
- ~~**continual-learning hook review**~~ **Done, not vendored as-is** — see `hooks/README.md`: a real SQLite-backed learning-capture pattern, but built for GitHub Copilot CLI's hook format, not Claude Code's. Flagged as Goal 3 input (port, don't copy).
- ~~**skills-for-fabric plugins**~~ **Done** — `powerbi-authoring` fully vendored (5 skills + `common/`, real Power BI/Fabric usage in this user's projects); `fabric-authoring`/`fabric-operations`/`fabric-skills` kept manifest-only (~30 unused-workload skills, heavily overlapping each other) — see `plugins/README.md`.
- ~~**ponytail evaluation**~~ **Done, and corrected a prior claim** — earlier research called ponytail "a direct competitor to caveman"; reading the actual upstream skill disproved that. Ponytail governs code generation (YAGNI ladder), caveman governs prose — they're designed to pair, not compete (ponytail's own SKILL.md says so). Vendored `ponytail` + `ponytail-debt`; skipped `ponytail-review`/`ponytail-audit` (redundant with `code-review`/`simplify`) and `ponytail-gain`/`ponytail-help` (low value). The `plugin.json`/`marketplace.json` reference-pattern goal is superseded by `skills-for-fabric`'s more mature real-world example, already captured above.

**Goal 2 (saturate skills-plugins-hooks) is complete.** Remaining work moves to Goal 3:

- **`update-vendor-skills.ipynb` rework**: still has no drift-detection (only staleness-of-pinned-commit) and no incoming/outgoing manifest concept. Fork-handling now has a real first case (`two-axis-code-review`) to design against — currently a manual process (see `forks[]` in `vendor-skills.json`). Also needs to learn about `plugin_manifests_only[]` (manifest-tracked-but-not-vendored entries).
- **`project-memory-template`**: synthesize a reusable project memory-architecture template from `Python-PowerBI-DynastyFantasyFootball`, informed by the engineering flow now vendored above and the `continual-learning` hook pattern.
- **Regression-testing standard** (raised 2026-07-11, no Pocock skill covers this directly): `Python-PowerBI-DynastyFantasyFootball` has no regression-testing discipline today. Building blocks exist — `tdd` (test discipline), `diagnosing-bugs` (regression-test-on-every-fix), `powerbi-report-authoring/references/screenshot-review.md` (seed for dashboard visual-regression) — but need synthesis into a Python-flavored standard (pytest + `pre-commit` + `check_sources.py`, which that repo's own `PLAN.md` already lists as a deferred pre-commit item) as part of `project-memory-template`, then retrofitted into the Dynasty repo. Especially load-bearing once dashboarding work starts there.
- ~~**Git guardrail — never push directly to `main`**~~ **Done** (raised 2026-07-11, shipped 2026-07-12): `git-guardrails` — adapted from `mattpocock/skills/misc/git-guardrails-claude-code`, branch-aware (blocks only `main`/`master` targets, allows feature branches) — is built, merged, and active on this machine via `~/.claude/settings.json`'s global `PreToolUse` hooks. See `hooks/README.md` for the full writeup and the layered-defense caveat (a Claude Code hook alone doesn't stop a direct terminal push or a different machine).
- **Enforcement**: hooks/subagents that scan repo structure on check-in for compliance with the agreed template, and flag any skill/plugin/hook checked in from a non-central source.
- **Live-vs-central drift detection** (raised 2026-07-11): the distribution verification pass found `~/.claude/skills/` holding real (non-symlinked) copies of `caveman`, `grill-me`, `grill-with-docs`, `fantasy-football-python` that had silently diverged from this repo's copies in both directions (`fantasy-football-python`'s live copy was more current than central; `grill-with-docs`'s live copy was stale). A future hook/subagent should diff live `~/.claude/skills/<name>/` against `skills-plugins-hooks/skills/<name>/` on some cadence (check-in, or a scheduled check) and flag divergence before it's silently overwritten in either direction.
- **Skill distribution beyond manual symlink** (raised 2026-07-11, during `project-memory-template` planning; narrowed 2026-07-11 after confirming `.claude/skills/` is natively shared across Claude Code CLI, the VS Code extension, and VS Code's own Agents-window Skills panel — see Installation above): the remaining gap is just **new-machine bootstrap** — the symlink loop still has to be run manually once per machine. A setup script (or a `setup-project-memory`-style skill) that runs it as part of onboarding a new dev environment is future work.
- ~~**Skill-stage/domain routing map**~~ **Done** (raised and closed 2026-07-11) — see the **Routing: which skill, when** section above: all 34 skills cross-cut by process stage (Plan/Crystallize/Execute) and domain (Power BI's own Plan→Design→Author→Manage pipeline, this user's repos, cross-cutting/always-on). `project-memory-template`'s `CLAUDE.md` should reference this section once that template starts seeing real use.
- **Orphan project-skill detection** (raised 2026-07-11): the reverse direction of "Enforcement" above — a hook/subagent that scans a *consuming* project's own `.claude/skills/` (or `.github/skills/`, `.agents/skills/`) for skills that exist there but aren't in this central catalog. Flags candidates for promotion (a genuinely reusable skill someone built one-off in a project repo) vs. skills that are legitimately project-scoped and should stay local (e.g. `discord-bot-github-fetch`, which is intentionally Dynasty-repo-only). The check's manifest of "what's known-local-and-intentional" would live per-project, not globally, since scoping is a per-repo decision.
