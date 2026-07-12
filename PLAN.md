# PLAN.md

Scratchpad for active/upcoming work. Expected to drift — completed items
collapse to one-liners once their durable signal lands in an ADR or
`.claude/memory/`. Blow-by-blow does NOT live here.

## Working state (2026-07-12)

**Goal 3 is fully shipped, including activation.** All four re-sequenced
items landed and merged to `main` on every repo touched
(`skills-plugins-hooks-agents`, `project-memory-template`,
`Python-PowerBI-DynastyFantasyFootball`) — zero open PRs anywhere. The
`continual-learning` hook is now installed and live on this machine (see
Shipped below). Full detail in `.claude/memory/program-status.md`.

**2026-07-12 rename**: repo renamed `skills-plugins-hooks` →
`skills-plugins-hooks-agents` on GitHub (`gh repo rename`) and locally
(folder renamed by user, `origin` remote updated to match). In-repo
references to the old name updated in `CLAUDE.md`, `README.md`, `PLAN.md`,
`.claude/memory/MEMORY.md`; historical mentions of the Goal-1
`skills`→`skills-plugins-hooks` rename left as accurate history. No
`agents/` directory exists yet — the name anticipates future scope, not
yet scaffolded; revisit when agent content actually lands.

## ➡ NEXT

**Post-Goal-3 audit (2026-07-12) — grill + fix pass, not yet started.**
A critical review of both repos (quality/distribution/logical-consistency)
found that "merged" and "documented" repeatedly outran "actually running."
Session was paused here for a Claude Code restart (needed for
`continual-learning`'s hooks to take effect in a live session — it was
wired into `~/.claude/settings.json` mid-session and hadn't been exercised
by the harness itself yet). Resume with:

1. ~~Grill `continual-learning`'s spec~~ — **done, 2026-07-12.**
   - **Wiring**: confirmed hook fires as real harness `PostToolUse` events
     (Read/Bash/PowerShell rows landed in `tool_log` this session,
     timestamped, not a manual invocation) — the restart-session PATH
     blocker is fully resolved.
   - **`project-memory-template` integration**: the template's silence on
     `continual-learning` in `CLAUDE.md` is *correct* — it's global machine
     infra (like `git-guardrails`), not a per-repo install step, so a
     per-repo scaffold shouldn't document it. The real gap was elsewhere:
     none of the template's 3 tiers shipped a `.gitignore`, so the
     hook's per-repo `.claude/learnings.db` (auto-created on first session
     in any repo) was one commit away from landing in git. Fixed — `.gitignore`
     added to `tiers/{full,standard,minimal}/` with `.claude/learnings.db` +
     OS noise.
   - **Scope**: pulled upstream's actual `microsoft/skills/hooks/
     continual-learning/learn.sh` and diff'd it against this port. Two
     things the schema promises but the implementation doesn't deliver
     (failure-pattern grouping is tool-name-only so signal reads as noise;
     `mistake`/`preference`/`pattern` learning categories have no write
     path, only `tool_insight` does) are **both present in upstream's
     original script, not introduced by the port** — confirmed by direct
     comparison. Decision: leave as-is, matching upstream exactly; revisit
     only if the auto-captured `tool_insight` signal proves valuable enough
     to justify building further. Documented in `hooks/continual-learning/README.md`.
2. **Fix the four gaps found in the audit** — 3 of 4 done this session:
   - ~~Stale `hooks/README.md`~~ — **done**, now says installed/active for
     both hooks, includes the inherited-limitation note above.
   - ~~`project-memory-template/tiers/full/CLAUDE.md` bullet-list bug~~ —
     **done**, regression-testing-standard pointer renested as a proper
     sub-bullet.
   - ~~Dynasty: `pre-commit install` never run~~ — **done**
     (`Python-PowerBI-DynastyFantasyFootball#20`): added `pre-commit` to
     `requirements.txt`, installed the git hook, documented setup in
     `CONTRIBUTING.md`, verified firing on a real commit (not manual).
   - ~~`check-in-hygiene` zero adoption~~ — **done**. Wired into Dynasty
     (`#20`, natural fit — real scaffold, pre-commit already active there)
     and, per an explicit choice to bootstrap it, into this repo too
     (`#19`, first Python/pre-commit tooling this repo has ever needed).
     First real adoption anywhere surfaced two genuine packaging bugs in
     the hook itself, both fixed (`project-memory-template#6`):
     `language: python` failed outright (repo wasn't pip-installable, no
     `setup.py`/`pyproject.toml`); the interim `language: script` fix
     failed on Windows (relies on POSIX shebang execution). Landed on a
     minimal `pyproject.toml` + `project.scripts` console-entry-point
     instead — verified via scratch-venv install and by confirming the
     hook actually blocks a deliberately-broken test ADR in both Dynasty
     and this repo.
   - ~~Root `README.md` stale~~ — **done**: tree diagram now reflects
     both active hooks; Roadmap's git-guardrail entry updated from "open
     decision, not resolved yet" to shipped/active.
3. **Bigger logical-consistency question, still open**: neither repo
   currently has one bootstrap step that wires skills + both global hooks +
   `pre-commit` install together for a brand-new project — each is a
   separate manual step today, and Dynasty (the most mature real example)
   already proves this gets missed even when the rest is done right. Decide
   whether that's worth solving now or staying deferred.

## [ ] Deferred

- [ ] `update-vendor-skills.ipynb` rework — drift detection, fork-handling
  automation, `plugin_manifests_only[]` awareness.
- [ ] Skill-stage/domain routing map maintenance — keep in sync if the
  skill catalog churns (flagged as a Divergent-Change risk in review).
- [ ] Orphan project-skill detection — hook/subagent scanning consuming
  repos' own `.claude/skills/` for skills not in this central catalog.
- [ ] Apply `project-memory-template` to a fresh environment as a test
  case — after the above, not yet chosen.

## Shipped (one-liners; full detail in ADR / `.claude/memory/`)

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
