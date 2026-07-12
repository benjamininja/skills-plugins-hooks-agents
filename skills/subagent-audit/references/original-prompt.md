# Original prompt (provenance)

The verbatim "Subagent Opportunity Audit" prompt this skill was adapted
from, received 2026-07-12 as a paste-in prompt design
(`subagent-opportunity-audit-prompt_turn3_claude.md`). Kept for
diffability, like `vendor-cache/` does for forked vendored skills — this
one has no upstream repo to pin, so the copy lives here instead.

Deliberate divergences in `../SKILL.md`:

1. Step 1 inventory also reads the skills reachable from the target repo
   (its own `.claude/skills/` + central-catalog junctions) so the audit
   doesn't propose subagents that duplicate an existing skill.
2. Added an explicit **skill** definition alongside hook/subagent, and a
   matching escape hatch ("already covered by an available skill → say so
   and move on").
3. Added Step 5 — persist accepted *and* rejected-with-reason candidates
   to the target repo's memory scaffold (`PLAN.md` / ADR /
   `.claude/memory/`), so later sessions don't re-propose them.

---

# Subagent Opportunity Audit — Prompt for Claude Code

Paste this into a Claude Code session at the root of the repository you want audited.

---

## Prompt

You are performing a structural audit of this codebase to find high-ROI opportunities for **subagents** — not a generic "where could AI help" brainstorm. Find the specific architectural boundaries where delegating to an isolated agent improves speed, reliability, or context integrity.

Before proposing anything, hold this line:

- **Hook** = a deterministic, event-triggered script (PreToolUse, PostToolUse, etc.) with no LLM judgment involved. It can contain branching logic, but no reasoning about ambiguous cases. If a linter, formatter, or fixed bash script solves it, it's a hook, not a subagent.
- **Subagent** = an isolated context window with its own system prompt, restricted tool access, and (optionally) its own model — used when the task needs judgment, adversarial review, a different persona, or would otherwise pollute the main conversation with content it doesn't need to retain.

If a candidate is purely deterministic, flag it as a **hook candidate instead** and say why. Don't force it into a subagent recommendation to pad the list.

Account for current default behavior: subagents now run in the background by default unless the main agent needs the result before continuing, and background subagents surface permission prompts back to the main session rather than silently failing. Factor this into your foreground/background calls — don't treat backgrounding as a rare, manual choice.

### Step 1 — Inventory first (don't recommend what already exists)
1. Check for `.claude/agents/` (project-level) and note what's already defined, including any `background: true` frontmatter already in use.
2. Read `CLAUDE.md` and `.claude/settings.json` for existing hooks and subagent routing rules.
3. Identify any configured MCP servers and what tools they expose to the main agent right now.

Note anything already well-covered so you don't propose rebuilding it.

### Step 2 — Scan for candidates by category

**A. Context & Attention Firewall**
*Target:* large generated files, legacy logs, raw SQL/schema dumps, vendored docs, sprawling config — anything that would flood the main agent's context on a full read.
*Why it matters:* this isn't just a dollar-cost problem (caching only helps *repeated* reads of unchanged content) — it's a finite-context-window problem. A 10k-line file consumes the same slice of attention on first read whether or not it's cached, and dilutes the model's focus on the actual task at hand.
*Action:* for each candidate, define a subagent whose only job is to read it and return a structured 5–10 line extract — not raw content — to the main agent.

**B. Domain Auditor (Adversarial QA)**
*Target:* core business logic, data models, auth/payments/permissions code, concurrency-prone modules.
*Why it matters:* the agent that wrote the code has builder bias — it assumes its own output is correct and aligned with the project's actual conventions.
*Action:* propose an auditor persona whose system prompt is grounded in *this repo's* actual architecture docs (find and name the real ones — ADRs, design docs, whatever exists — don't assume a filename like `CONTEXT.md` if it isn't there). It should actively look for edge cases, race conditions, and deviations from established patterns, not just re-read the diff approvingly.

**C. Data Schema Transformer**
*Target:* raw JSON/CSV fixtures, loosely-typed API responses, ad hoc SQL, or anywhere types are hand-maintained against a drifting external shape.
*Action:* define a subagent that takes the messy input format and returns strict typed output (TypeScript interface, Zod schema, Pydantic model, etc.) — keep this reasoning out of the main coding thread entirely, it's a different kind of task.

**D. Dedicated Tool/MCP Wrapper**
*Target:* any live database, external API, or MCP server currently exposed directly to the main agent.
*Why it matters:* broad, direct access to a live external system from the main agent is both a security risk and a distraction — every tool call and result lands in the main context whether relevant or not.
*Action:* propose a subagent with *exclusive*, narrowly-scoped access to the specific read/write operations needed, acting as a secure intermediary instead of the main agent touching the MCP directly.

**E. Background Specialist (docs, tests, monitoring)**
*Target:* stale/missing README or ADR patterns, undocumented modules, recurring "write tests for this" requests, or log/error-pattern monitoring.
*Why it matters:* this is a legitimate, commonly-used pattern (docs proofreaders and test writers are exactly the kind of thing worth defining once and letting the main agent delegate to automatically) — but it needs a real guardrail: a background subagent editing the same file the main agent is actively working in is a conflict, not a convenience.
*Action:* scope each background specialist to files/directories the main agent isn't concurrently editing, or trigger it on commit boundaries rather than mid-edit. Specify exactly what git diff scope or event it watches.

**F. Parallel Independent-File Dispatch**
*Target:* a fix, lint-rule migration, or dependency bump that recurs identically across many *unrelated* files with zero shared state.
*Why it matters:* this is a speed argument, not an isolation argument — parallel subagents finish this class of work faster than one agent working serially, since there's no coordination cost.
*Action:* flag these separately from A–E; note the file count/scope and confirm there's genuinely no cross-file dependency before recommending parallel dispatch.

### Step 3 — Required output format
For every real candidate found in this codebase, output this table — no generic/hypothetical entries:

| Field | Value |
|---|---|
| Category | A–F |
| Name | proposed subagent name |
| Trigger | the exact scenario that should cause automatic delegation |
| Tools | minimum required tool set — default to read-only unless write is the point |
| Model | "cheapest model that reliably handles this task" — don't hardcode a specific model name, resolve it against whatever's currently configured/available |
| Dispatch mode | foreground / background, with one-line justification |
| Justification | why this must be a subagent, not a hook or main-agent task |
| Draft file | a ready-to-drop-in `.claude/agents/<name>.md` definition |

### Step 4 — Risk, redundancy, and final cut
1. Rank all candidates by impact and risk reduction, highest first.
2. **Reject** any pair of candidates that would need to edit the same file(s) concurrently — merge those into a single scope or keep it in the main agent instead.
3. Cap the final recommendation list at 3–5 well-scoped subagents. A sprawling roster degrades automatic delegation reliability more than it helps.

Do not output generic categories without evidence. Execute a real scan of this codebase and cite specific files, directories, or modules for every candidate you propose.
