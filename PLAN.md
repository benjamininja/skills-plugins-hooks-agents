
Scratchpad for active/upcoming work. Expected to drift — completed items
collapse to one-liners once their durable signal lands in an ADR or
`.claude/memory/`. Blow-by-blow does NOT live here.

## Open question (2026-07-18, unanswered): stage/commit/PR outstanding work?

Three repos have uncommitted changes from this session's work (root-memory
propagation hook/agent + ADR-0010, ADR-0011 design docs, and the earlier
token-gating-loop compact-budget propagation): this repo, root `~/.claude`,
and `Python-PowerBI-DynastyFantasyFootball`. Asked once ("Want me to stage
and open PRs?"), not yet answered — do not assume declined or approved.
Note: `Python-PowerBI-DynastyFantasyFootball`'s `git status` also shows a
large number of modified/untracked files (parquet data, notebooks, backend
routers, `docs/DATA_MODEL.md`, etc.) **unrelated to this session's edits**
— pre-existing work-in-progress in that repo, not something this session
touched or should sweep into any commit.

## Shipped (2026-07-18): unified distribution architecture design

Grilling session (`/grill-with-docs`) resolved and written up as
[ADR-0011](docs/adr/0011-unified-distribution-architecture.md) —
**design only, implementation not started.** Also produced this repo's
first `CONTEXT.md`. Summary: one `distribution-registry.json` + one
`tools/manage_distribution.py` (`--check`/`--bless`/`--apply`) covering
all 4 artifact types bidirectionally; agents and hooks move to ADR-0003's
junction mechanism (currently copy-based); plugins go project-scoped via
downstream `.claude/settings.json`; `root-memory-propagation` (ADR-0010)
stays separate, not absorbed.

**Next build steps (not started):**
- `distribution-registry.json` — create empty/seeded with the
  `frontend-design@claude-plugins-official` test case (this repo +
  `Python-PowerBI-DynastyFantasyFootball`).
- `tools/manage_distribution.py` — `--apply` (junction/settings-merge
  install), `--check` (distribution drift + upstream check-in scan),
  `--bless` (mark a divergence intentional).
- Migrate existing hook installs
  (`~/.claude/hooks/root-memory-propagation/`, `~/.claude/hooks/
  git-guardrails/`, etc.) from physical copies to junctions once
  `--apply` exists.
- First real distribution target for agents: get
  `root-memory-propagation-auditor` (and the other 3) reachable from
  `Python-PowerBI-DynastyFantasyFootball`.

<details>
<summary>Grilling session decision log (resolved 2026-07-18, kept for
traceability — see ADR-0011 for the authoritative write-up)</summary>

1. **Scope: all 4 artifact types** — skills, plugins, hooks, agents. Plugins
   explicitly in scope despite `plugins/` being nearly empty today (only
   manifest-only `fabric-collection` cataloged, nothing physically vendored)
   — user wants a real downstream flow for it, and upstream check-in for
   plugins built in a downstream repo (e.g. a future fantasy-football
   plugin flowing back here).
2. **One unified registry + verb set**, not 4 separate mechanisms and not
   one fully-uniform file-copy mechanism. Reuses the
   `known_local_edits[]`/`--check`/`--bless`/`--apply` *shape* from
   `vendor-skills.json`/`tools/update_vendor_skills.py` — but note that
   existing tool solves the **opposite direction** (external upstream → this
   repo); the new registry is this-repo-as-upstream → downstream project
   repos, plus the reverse (downstream local edit → flows back here).
   Type-specific adapters underneath one CLI, because Claude Code discovers
   each type differently: skills/agents = filesystem dir-scan one level
   deep; hooks = explicit `settings.json` pointer + script file; plugins =
   `settings.json` `enabledPlugins`/`extraKnownMarketplaces` entries, not a
   file tree at all.
3. **Plugin distribution = project-scoped**, not global. A downstream
   repo's own (currently nonexistent — neither repo has one yet)
   `.claude/settings.json` gets its own `enabledPlugins`/marketplace
   entries propagated in, tracked per-repo in the registry. Rejected
   global-only enablement in `~/.claude/settings.json`: it can't express
   "this plugin belongs in these 2 repos, not the other N" — confirmed by
   the concrete driving example below.

**Concrete test case carried through the design:** user wants
`frontend-design@claude-plugins-official` (a real plugin, already
registered as a marketplace in `~/.claude/settings.json`'s
`extraKnownMarketplaces`/`enabledPlugins`) enabled in *both*
`skills-plugins-hooks-agents` (tool library) and
`Python-PowerBI-DynastyFantasyFootball` (for web app dev work there) — but
not necessarily anywhere else. Note: this is a different artifact from the
already-vendored `frontend-design` **skill** (`vendor-skills.json`, from
`anthropics/claude-code`'s `plugins/frontend-design/skills/frontend-design`)
— same name, different type, don't conflate them when building the example
into a test fixture later.

4. **Agents and hooks move to junction/symlink** (ADR-0003's mechanism),
   replacing hooks' copy-and-manually-re-copy pattern. Agents: one junction
   per `.md` file. Hooks: junction the script file; the `settings.json`
   registration entry still needs an explicit merge (can't symlink into a
   JSON object).
5. **"Downstream local edit" = two cases**: (a) a wholly new artifact built
   downstream, never linked from central; (b) a junction broken/replaced
   with a standalone copy that's now diverged. Both are in scope for
   upstream check-in detection.
6. **Detection = on-demand `--check` CLI verb**, not a background subagent
   or auto-triggering hook — manual invocation, same model as
   `update_vendor_skills.py` today.
7. **Registry = single new `distribution-registry.json`**, sibling to (not
   merged with) `vendor-skills.json`, split by artifact type internally.
8. **`root-memory-propagation` (ADR-0010) stays separate**, not absorbed —
   different domain (prose-diff-and-judge vs. link/copy + new-artifact
   detection).
9. **Tool name: `tools/manage_distribution.py`**, verb set
   `--check`/`--bless`/`--apply`.

Session used `/grilling` + `/domain-modeling` (via `/grill-with-docs`).
</details>

## Working state (2026-07-12, end of second session — compact checkpoint)

**Everything in flight is shipped and merged; zero open PRs across all
four repos** (`skills-plugins-hooks-agents` #22–#30, `project-memory-
template` #9/#10, Dynasty #21; `dotclaude` direct-to-main). All repos
clean on `main`. Session detail checkpointed in
`.claude/memory/program-status.md` "2026-07-12 (second session)".

Live infrastructure a fresh session should know exists:

- `/subagent-audit` (authored skill, junctioned) — Dynasty carries the
  first `.claude/agents/` roster (its ADR-0009).
- **Plan gate** in root `CLAUDE.md` — request→plan→confirm→write for
  non-trivial changes, plan mode by default; mirrored in
  `project-memory-template` tiers with sync markers.

## Shipped (2026-07-18)

- **`root-memory-propagation` hook + `root-memory-propagation-auditor`
  agent** (ADR-0010): `PostToolUse` nudge on root-memory edits, paired
  subagent sweeps a registry of downstream repos for stale duplicated
  content, judging genuine matches apart from coincidental ones. Fourth
  agent in this repo's `.claude/agents/`.
- Root tier is git-versioned: private `benjamininja/dotclaude`
  (allowlist; RESTORE.md; manual cadence — offer commit after any
  root-tier edit, per preferences.md nudge).
- `CATALOG.md` generated by `tools/build_catalog.py` (tags in
  manifest.json); `tools/update_vendor_skills.py` = staleness + drift
  (known/NEW two-bucket, `--bless`, `--apply` reapply ritual). Catalog is
  fully current with upstream as of today; 7 known edits blessed.

## ➡ NEXT

Nothing actively sequenced — pick from Deferred below. Likeliest
candidates, in rough value order: (1) hygiene-hook robust fix (strip
inline-code spans — kills false-positive classes 2–4) in
`project-memory-template`; (2) orphan project-skill detection (Dynasty's
`skills/Instructions-PowerBI-Visuals-Deneb-HTML.md` is a live specimen);
(3) fresh-environment `/setup-project-memory` test.

## [ ] Deferred

- [x] ~~`update-vendor-skills.ipynb` rework~~ — done 2026-07-12 as
  `tools/update_vendor_skills.py` (drift detection via blob-SHA tree
  compare, forks[] hand-merge flagging, `plugin_manifests_only[]` checks;
  notebook retired). First live run: all 34 vendored paths have upstream
  updates; 6 skills carry deliberate-but-unrecorded local edits
  (fork-rename pointers in ask-matt/implement/tdd, `common/` path rewrites
  in semantic-model-authoring/powerbi-report-management, frontend-design's
  added LICENSE.txt). **Both open decisions grilled and resolved
  2026-07-12**: (a) three-state ontology (faithful /
  vendored-with-known-edits / fork) via per-entry `known_local_edits`
  annotations (file + reason + local_sha), two-bucket reporting
  (known/NEW), `--bless`, stale-annotation policing, git-based reapply
  ritual on `--apply` — built, seeded for all 6 skills, verified (0 NEW /
  7 known files; planted edits surface as NEW); (b) family-batched update
  PRs — all four batches done same day, catalog fully current (see
  Shipped).
- [ ] Skill-stage/domain routing map maintenance — keep in sync if the
  skill catalog churns (flagged as a Divergent-Change risk in review).
  **Partially closed 2026-07-12**: stage/domain now lives as tags in
  `manifest.json` and `tools/build_catalog.py` fails on membership/tag
  drift when regenerating `CATALOG.md`; remaining gap is only the README
  routing *tables* themselves (narrative view, still hand-maintained).
- [ ] Orphan project-skill detection — hook/subagent scanning consuming
  repos' own `.claude/skills/` for skills not in this central catalog.
- [ ] Apply `project-memory-template` to a fresh environment as a test
  case, now via `/setup-project-memory` — not yet run.

## Shipped (one-liners; full detail in ADR / `.claude/memory/`)

- **2026-07-17 (cont'd, second addition)**: `/security-review` required
  before opening a PR (ADR-0009) — added to this repo's `CLAUDE.md` and all
  three `project-memory-template` tier `CLAUDE.md`s' `## Git` section;
  cross-referenced in `skill-safety-auditor.md`. It's a Claude-Code-built-in
  skill (no local `SKILL.md`), so nothing to vendor — doc instruction only,
  since neither `pre-commit`/CI nor `check-in-hygiene` can invoke a skill
  (ADR-0004's boundary, extended).
- **2026-07-17 (cont'd)**: `/subagent-audit` run against `project-memory-
  template` found almost no real subagent surface there (it never dogfoods
  its own scaffold — `docs/adr/`/`PLAN.md`/`CONTEXT.md` only exist as
  unfilled `tiers/*/` template content, not live project state), except one
  real gap: the tiers' distilled plan-gate paraphrase vs. root `dotclaude`
  CLAUDE.md's plan gate has no sync enforcement (text-diff can't check it —
  the tiers are deliberately reworded, not copied). Added
  `plan-gate-sync-auditor` (ADR-0008) here rather than in either subject
  repo, since neither has an `.claude/agents/` home yet and this repo is
  the one every project already links from. `check-in-hygiene`'s deferred
  staleness/delete-offer features were considered and explicitly deemed
  out of scope for that audit — no live scaffold instance to judge
  staleness of in `project-memory-template` itself; belongs in a consuming
  repo if ever built.
- **2026-07-17**: blast-radius-tiered model-invocation (ADR-0006) — flipped
  `disable-model-invocation` off for `grill-me`, `grill-with-docs`, `teach`,
  `writing-great-skills`, `ask-matt` via `known_local_edits` (not a full
  fork); `triage`/`wayfinder` initially proposed but moved back to manual on
  closer read (both write to the external issue tracker). Followed by
  `/subagent-audit`: first `.claude/agents/` roster (ADR-0007) —
  `vendor-sync-reapply` (background, handles the `--apply` reapply-ritual
  judgment call) and `skill-safety-auditor` (foreground, adversarial
  blast-radius review before future invocation-tier changes) — both a
  direct response to gaps this same session exposed (a near-miss
  mis-tiering of `triage`/`wayfinder`, and the unenforced reapply ritual).
- **2026-07-12 second session** (PRs #22–#30 here + template #9/#10 +
  Dynasty #21 + dotclaude): `subagent-audit` skill + first Dynasty agent
  roster; plan gate (root CLAUDE.md + template tiers + sync markers);
  root tier versioned as `dotclaude`; manifest tags + generated
  `CATALOG.md`; vendor tooling rewrite + three-state drift ontology; all
  vendored content brought fully current (real behavioral surface: 3
  files); hygiene-hook DAX false-positive fixed. Full detail in
  `.claude/memory/program-status.md` "2026-07-12 (second session)".
- **Goal 1**: renamed `skills` → `skills-plugins-hooks`, added
  `plugins/`/`hooks/` scaffolding.
- **Goal 2**: saturated the catalog (Pocock's idea→ship flow, ponytail,
  Power BI/Fabric skills) — merged PR #4.
- **Goal 3, done**: `project-memory-template` scaffold; skill-distribution
  bugs found and fixed; skill-stage/domain routing map; two-axis review of
  both repos' shipped work + fixes; this repo's own `common/` relocation
  (→ `skills/_powerbi-authoring-common/`) and full memory architecture
  (`CLAUDE.md`/`PLAN.md`/`.claude/memory/`/4 ADRs); `continual-learning`
  hook port and activation (`sqlite3`/`jq` installed via `winget`, hooks
  merged into `~/.claude/settings.json`, verified persisting real rows);
  `git-guardrails` hook (built and activated); `check-in-hygiene` hook;
  regression-testing standard (general doc + Dynasty retrofit, ADR-0008)
  — all merged to `main` across all three repos. Full detail in
  `.claude/memory/program-status.md`.
- **Repo renamed** `skills-plugins-hooks` → `skills-plugins-hooks-agents`
  (2026-07-12, `gh repo rename` + local remote + in-repo references).
- **Post-Goal-3 audit, all 4 gaps fixed**: `continual-learning` re-verified
  live post-restart (real harness-fired `tool_log` rows) and grilled
  against upstream `microsoft/skills` source (two known limitations
  confirmed inherited, not port bugs — see `hooks/continual-learning/README.md`);
  Dynasty's `pre-commit install` activated (`Python-PowerBI-DynastyFantasyFootball#20`);
  `check-in-hygiene` adopted by a real consumer for the first time ever
  (Dynasty + this repo), which surfaced and fixed two genuine cross-platform
  packaging bugs (`project-memory-template#6`); stale docs (`hooks/README.md`,
  root `README.md`) corrected.
- **Skill routing + junction drift detection** (ADR-0005): discovered
  every `~/.claude/skills/` junction on this machine was broken (pointed
  at the repo's pre-Goal-1 name, silently stranding every Pocock-flow
  skill for weeks) — all 34 relinked. New `hooks/skill-catalog-health/`
  (`SessionStart`) injects a self-generated routing index (mirrors
  upstream `mattpocock/skills`' README Reference-table format) so
  `disable-model-invocation: true` router skills still get surfaced, and
  flags future broken junctions instead of failing silently. New
  `skills/setup-project-memory` orchestrates the three previously
  uncoordinated bootstrap steps (memory tier, `setup-matt-pocock-skills`,
  `check-in-hygiene` pre-commit) in one pass — resolves the "apply
  `project-memory-template` to a fresh environment" deferred item below
  (not yet run as a live test).
