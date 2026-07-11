# plugins/

Reserved for Claude Code plugins (bundles of skills, hooks, and/or MCP
config shipped together) that belong to this central repo.

## fabric-collection (manifest-only)

`fabric-collection/*.plugin.json` are the upstream `.github/plugin/plugin.json`
manifests from [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric)
for `fabric-authoring`, `fabric-operations`, and `fabric-skills` — three of its
four published bundles. These are **manifest-only**: the manifests are stored
so we know what upstream offers and can pull the real content on demand, but
the ~30 skill folders they reference (Spark, KQL/Eventhouse, Eventstreams,
Warehouse, Activator, migration tooling) are **not physically vendored** here,
because none of it is used by any project in this repo today.

The fourth bundle, `powerbi-authoring`, **is** fully vendored — its 5 skills
live in `skills/` (`semantic-model-authoring`, `powerbi-report-authoring`,
`powerbi-report-design`, `powerbi-report-management`, `powerbi-report-planning`),
with shared reference docs in `skills/_powerbi-authoring-common/`
(`COMMON-CLI.md`, `COMMON-CORE.md`, `ITEM-DEFINITIONS-CORE.md`) — not itself
a skill (no `SKILL.md`, never loaded/linked on its own), nested inside
`skills/` rather than at repo root so relative links from the skills above
stay short — because Power BI/semantic
models is a real, active workload (see `fantasy-football-python`'s Power BI
semantic model work). Its own manifest isn't duplicated here since it's
already fully represented by real skill folders; see `vendor-skills.json`.

Skipped from the vendor: upstream's `check-updates` skill (a self-update
checker for skills-for-fabric's own releases) — redundant with this repo's
own `vendor-skills.json` / `update-vendor-skills.ipynb` mechanism.

If a Fabric workload beyond Power BI becomes relevant, use the matching
`*.plugin.json`'s `skills` list to know exactly what to pull from upstream
(same repo, same pinned approach as everything else in `vendor-skills.json`).

## Population status

Empty otherwise as of the `skills` → `skills-plugins-hooks` restructure.
Further population is scoped to a later phase of the saturation effort —
see the repo root README's Roadmap section.
