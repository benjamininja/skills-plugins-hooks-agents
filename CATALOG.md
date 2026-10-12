# Catalog

> **Generated file — do not hand-edit.** Rebuild with
> `python tools/build_catalog.py`. Descriptions come from each
> skill's `SKILL.md` frontmatter, provenance from
> `vendor-skills.json`, membership + tags from `manifest.json`.

## What's in this repo

- **Skills** (38 loadable: 4 authored, 33 vendored, 1 forked) — one folder per skill under `skills/`, each with a `SKILL.md`; junctioned into `~/.claude/skills/` per machine.
- **Plugins** (3, manifest-only) — cataloged upstream bundles whose ~30 skills are deliberately not vendored (unused Fabric workloads). See `plugins/README.md` / ADR-0002.
- **Hooks** (3, all installed on this machine) — deterministic event-triggered scripts under `hooks/`, registered in `~/.claude/settings.json`. See `hooks/README.md`.
- **Vendor cache** (1) — pristine, never-loaded upstream mirrors of forked skills, for diffing. See ADR-0001.
- **Agents** (3 here: root-memory-propagation-auditor, skill-safety-auditor, vendor-sync-reapply) — see each agent's own frontmatter `description`, and `docs/adr/` for the decision record behind it.

## Skills

Tags follow the routing-map axes (see README "Routing: which skill, when"): stage = plan / crystallize / execute / cross-cutting; domain = engineering-flow / powerbi-fabric / dynasty / frontend / comms / reference / meta. Invocation: `model` = reachable without a slash command (default); `user` = `disable-model-invocation: true`, slash-command only.

| Skill | Stage | Domain | Invocation | Source | Summary |
|---|---|---|---|---|---|
| **ask-matt** | plan | engineering-flow | model | [mattpocock/skills](https://github.com/mattpocock/skills) | Ask which skill or flow fits your situation. |
| **azure-resource-manager-playwright-dotnet** | execute | powerbi-fabric | model | [microsoft/skills](https://github.com/microsoft/skills) | Azure Resource Manager SDK for Microsoft Playwright Testing in .NET. |
| **caveman** | cross-cutting | comms | model | authored here | Token-compression communication skill. |
| **codebase-design** | crystallize | engineering-flow | model | [mattpocock/skills](https://github.com/mattpocock/skills) | Shared vocabulary for designing deep modules. |
| **diagnosing-bugs** | execute | engineering-flow | model | [mattpocock/skills](https://github.com/mattpocock/skills) | Diagnosis loop for hard bugs and performance regressions. |
| **domain-modeling** | crystallize | engineering-flow | model | [mattpocock/skills](https://github.com/mattpocock/skills) | Build and sharpen a project's domain model. |
| **everything-claude-code** | cross-cutting | reference | model | [affaan-m/ECC](https://github.com/affaan-m/ECC) | Development conventions and patterns for everything-claude-code. |
| **fantasy-football-python** | cross-cutting | dynasty | model | authored here | Expert Python Data Engineer and Fantasy Sports Architect for a 28-team, dual-conference dynasty fantasy football league. |
| **frontend-design** | execute | frontend | model | [anthropics/claude-code](https://github.com/anthropics/claude-code) | Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. |
| **grill-me** | plan | engineering-flow | model | [mattpocock/skills](https://github.com/mattpocock/skills) | A relentless interview to sharpen a plan or design. |
| **grill-with-docs** | plan | engineering-flow | model | [mattpocock/skills](https://github.com/mattpocock/skills) | A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go. |
| **grilling** | plan | engineering-flow | model | [mattpocock/skills](https://github.com/mattpocock/skills) | Grill the user relentlessly about a plan, decision, or idea. |
| **handoff** | crystallize | engineering-flow | user | [mattpocock/skills](https://github.com/mattpocock/skills) | Compact the current conversation into a handoff document for another agent to pick up. |
| **implement** | execute | engineering-flow | user | [mattpocock/skills](https://github.com/mattpocock/skills) | Implement a piece of work based on a spec or set of tickets. |
| **improve-codebase-architecture** | plan | engineering-flow | user | [mattpocock/skills](https://github.com/mattpocock/skills) | Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick. |
| **microsoft-docs** | cross-cutting | powerbi-fabric | model | [microsoft/skills](https://github.com/microsoft/skills) | Understand Microsoft technologies by querying official documentation. |
| **ponytail** | execute | engineering-flow | model | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Lazy senior dev mode for any coding task: the smallest change that fully solves it, and a reply a busy human understands in one read. |
| **ponytail-debt** | execute | engineering-flow | model | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Harvest every shortcut: comment into one debt ledger, so deferrals get tracked instead of forgotten. |
| **powerbi-report-authoring** | execute | powerbi-fabric | model | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) | Create and modify Power BI report files in PBIR/PBIP format using the `powerbi-report-author` and `powerbi-desktop` CLIs. |
| **powerbi-report-design** | plan | powerbi-fabric | model | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) | Generate Power BI report visual design guidance before PBIR files are written. |
| **powerbi-report-management** | execute | powerbi-fabric | model | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) | Manage Power BI report workspace items and PBIR definitions in Microsoft Fabric via `az rest` CLI against the Fabric REST API. |
| **powerbi-report-planning** | plan | powerbi-fabric | model | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) | Build a guided requirements-to-implementation workflow for new Power BI reports and dashboards from semantic models, datasets, or PBIP projects. |
| **prototype** | plan | engineering-flow | model | [mattpocock/skills](https://github.com/mattpocock/skills) | Build a throwaway prototype to answer a design question. |
| **read-the-damn-docs** | cross-cutting | engineering-flow | model | [BuilderIO/skills](https://github.com/BuilderIO/skills) | Use when implementing, integrating, upgrading, debugging, or answering anything involving third-party APIs, libraries, frameworks, CLIs, cloud services, model/provider SDKs, fast-moving product behavior, user requests f… |
| **resolving-merge-conflicts** | execute | engineering-flow | model | [mattpocock/skills](https://github.com/mattpocock/skills) | Use when you need to resolve an in-progress git merge/rebase conflict. |
| **semantic-model-authoring** | execute | powerbi-fabric | model | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) | Manages Power BI semantic models, including tables, columns, measures, relationships, field parameters, DAX, Import, DirectQuery and Direct Lake designs, sources, connections, permissions, refresh, and deployment. |
| **setup-matt-pocock-skills** | plan | meta | user | [mattpocock/skills](https://github.com/mattpocock/skills) | Configure this repo for the engineering skills: set up its issue tracker, triage label vocabulary, and domain doc layout. |
| **setup-project-memory** | plan | meta | user | authored here | Fully wire a brand-new (or partially-wired) project — memory scaffold, engineering-skills config, and pre-commit hooks — in one pass instead of three separate manual steps. |
| **stay-within-limits** | plan | engineering-flow | model | [BuilderIO/skills](https://github.com/BuilderIO/skills) | Use when long-running or parallel agent work must respect 5-hour and weekly usage limits by checking usage between waves, pausing near the cap, and resuming only when the window is clear. |
| **subagent-audit** | plan | meta | model | authored here | Structural audit of the current repo to find high-ROI subagent opportunities — the specific architectural boundaries where delegating to an isolated agent improves speed, reliability, or context integrity. |
| **tdd** | execute | engineering-flow | model | [mattpocock/skills](https://github.com/mattpocock/skills) | Test-driven development. |
| **teach** | crystallize | reference | model | [mattpocock/skills](https://github.com/mattpocock/skills) | Teach the user a new skill or concept, within this workspace. |
| **to-spec** | plan | engineering-flow | user | [mattpocock/skills](https://github.com/mattpocock/skills) | Turn the current conversation into a spec and publish it to the project issue tracker: no interview, just synthesis of what you've already discussed. |
| **to-tickets** | plan | engineering-flow | user | [mattpocock/skills](https://github.com/mattpocock/skills) | Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker (edges as text in one file per ticket locally, or native blocki… |
| **triage** | plan | engineering-flow | user | [mattpocock/skills](https://github.com/mattpocock/skills) | Move issues and external PRs through a state machine of triage roles, categorise, verify, grill if needed, and write agent-ready briefs. |
| **two-axis-code-review** | execute | engineering-flow | model | forked from [mattpocock/skills](https://github.com/mattpocock/skills) | Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes: Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating is… |
| **wayfinder** | plan | engineering-flow | user | [mattpocock/skills](https://github.com/mattpocock/skills) | Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear. |
| **writing-great-skills** | crystallize | meta | model | [mattpocock/skills](https://github.com/mattpocock/skills) | Reference for writing and editing skills well — the vocabulary and principles that make a skill predictable. |

## Plugins (manifest-only)

| Plugin | Upstream | Note |
|---|---|---|
| **fabric-authoring** | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) | Manifest only — the ~12 skills it references are not physically vendored (unused Fabric workloads: Spark, Warehouse, Eventhouse, Eventstream, Activator, medallion). |
| **fabric-operations** | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) | Manifest only — see plugins/README.md. |
| **fabric-skills** | [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric) | Manifest only — the full bundle (~30 skills), largely superset of fabric-authoring/fabric-operations. |

## Hooks

| Hook | Summary |
|---|---|
| **git-guardrails** | A Claude-Code-native `PreToolUse` hook adapted from [mattpocock/skills](https://github.com/mattpocock/skills)' [`skills/misc/git-guardrails-claude-code`](https://github.com/mattpocock/skills/tree/main/skills/misc/git-gu… |
| **root-memory-propagation** | A `PostToolUse` hook + companion subagent pair. |
| **skill-catalog-health** | A `SessionStart` hook with two jobs, both driven by the same scan of `~/.claude/skills/` (see [ADR-0005](docs/adr/0005-skill-routing-and-drift-detection.md) for the full reasoning): |
