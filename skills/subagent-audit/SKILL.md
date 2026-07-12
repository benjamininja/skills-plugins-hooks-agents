---
name: subagent-audit
description: Structural audit of the current repo to find high-ROI subagent opportunities — the specific architectural boundaries where delegating to an isolated agent improves speed, reliability, or context integrity. Use when the user asks to audit for subagents, find delegation opportunities, asks "where should we use subagents/agents here", or wants .claude/agents/ definitions proposed for a codebase.
---

# Subagent Opportunity Audit

Perform a structural audit of the current repo to find high-ROI
opportunities for **subagents** — not a generic "where could AI help"
brainstorm. Find the specific architectural boundaries where delegating to
an isolated agent improves speed, reliability, or context integrity.

Before proposing anything, hold this line:

- **Hook** = a deterministic, event-triggered script (PreToolUse,
  PostToolUse, etc.) with no LLM judgment involved. It can contain
  branching logic, but no reasoning about ambiguous cases. If a linter,
  formatter, or fixed bash script solves it, it's a hook, not a subagent.
- **Subagent** = an isolated context window with its own system prompt,
  restricted tool access, and (optionally) its own model — used when the
  task needs judgment, adversarial review, a different persona, or would
  otherwise pollute the main conversation with content it doesn't need to
  retain.
- **Skill** = reusable prompt/procedure loaded into the *main* agent's
  context. If the task benefits from the main conversation's accumulated
  context and doesn't flood it, it's a skill, not a subagent.

If a candidate is purely deterministic, flag it as a **hook candidate
instead** and say why. If it's already covered by an available skill, say
so and move on. Don't force either into a subagent recommendation to pad
the list.

Account for current default behavior: subagents run in the background by
default unless the main agent needs the result before continuing, and
background subagents surface permission prompts back to the main session
rather than silently failing. Factor this into your foreground/background
calls — don't treat backgrounding as a rare, manual choice.

## Step 1 — Inventory first (don't recommend what already exists)

1. Check for `.claude/agents/` (project-level) and note what's already
   defined, including any `background: true` frontmatter already in use.
2. Read `CLAUDE.md` and `.claude/settings.json` for existing hooks and
   subagent routing rules. Check `~/.claude/settings.json` too — global
   hooks (e.g. git guardrails, learning capture) already cover some
   deterministic ground.
3. Inventory the skills already reachable from this repo: the repo's own
   `.claude/skills/` plus anything linked from a central catalog (on this
   machine, `skills-plugins-hooks-agents` via `~/.claude/skills/`
   junctions). Don't propose a subagent that duplicates an existing
   skill's job.
4. Identify any configured MCP servers (`.mcp.json`, `claude mcp list`)
   and what tools they expose to the main agent right now.

Note anything already well-covered so you don't propose rebuilding it.

## Step 2 — Scan for candidates by category

### A. Context & Attention Firewall

*Target:* large generated files, legacy logs, raw SQL/schema dumps,
vendored docs, sprawling config — anything that would flood the main
agent's context on a full read.

*Why it matters:* this isn't just a dollar-cost problem (caching only
helps *repeated* reads of unchanged content) — it's a finite-context-window
problem. A 10k-line file consumes the same slice of attention on first
read whether or not it's cached, and dilutes the model's focus on the
actual task at hand.

*Action:* for each candidate, define a subagent whose only job is to read
it and return a structured 5–10 line extract — not raw content — to the
main agent.

### B. Domain Auditor (Adversarial QA)

*Target:* core business logic, data models, auth/payments/permissions
code, concurrency-prone modules.

*Why it matters:* the agent that wrote the code has builder bias — it
assumes its own output is correct and aligned with the project's actual
conventions.

*Action:* propose an auditor persona whose system prompt is grounded in
*this repo's* actual architecture docs (find and name the real ones —
ADRs, design docs, whatever exists — don't assume a filename like
`CONTEXT.md` if it isn't there). It should actively look for edge cases,
race conditions, and deviations from established patterns, not just
re-read the diff approvingly.

### C. Data Schema Transformer

*Target:* raw JSON/CSV fixtures, loosely-typed API responses, ad hoc SQL,
or anywhere types are hand-maintained against a drifting external shape.

*Action:* define a subagent that takes the messy input format and returns
strict typed output (TypeScript interface, Zod schema, Pydantic model,
etc.) — keep this reasoning out of the main coding thread entirely, it's
a different kind of task.

### D. Dedicated Tool/MCP Wrapper

*Target:* any live database, external API, or MCP server currently
exposed directly to the main agent.

*Why it matters:* broad, direct access to a live external system from the
main agent is both a security risk and a distraction — every tool call
and result lands in the main context whether relevant or not.

*Action:* propose a subagent with *exclusive*, narrowly-scoped access to
the specific read/write operations needed, acting as a secure
intermediary instead of the main agent touching the MCP directly.

### E. Background Specialist (docs, tests, monitoring)

*Target:* stale/missing README or ADR patterns, undocumented modules,
recurring "write tests for this" requests, or log/error-pattern
monitoring.

*Why it matters:* this is a legitimate, commonly-used pattern (docs
proofreaders and test writers are exactly the kind of thing worth
defining once and letting the main agent delegate to automatically) — but
it needs a real guardrail: a background subagent editing the same file
the main agent is actively working in is a conflict, not a convenience.

*Action:* scope each background specialist to files/directories the main
agent isn't concurrently editing, or trigger it on commit boundaries
rather than mid-edit. Specify exactly what git diff scope or event it
watches.

### F. Parallel Independent-File Dispatch

*Target:* a fix, lint-rule migration, or dependency bump that recurs
identically across many *unrelated* files with zero shared state.

*Why it matters:* this is a speed argument, not an isolation argument —
parallel subagents finish this class of work faster than one agent
working serially, since there's no coordination cost.

*Action:* flag these separately from A–E; note the file count/scope and
confirm there's genuinely no cross-file dependency before recommending
parallel dispatch.

## Step 3 — Required output format

For every real candidate found in this codebase, output this table — no
generic/hypothetical entries:

| Field | Value |
|---|---|
| Category | A–F |
| Name | proposed subagent name |
| Trigger | the exact scenario that should cause automatic delegation |
| Tools | minimum required tool set — default to read-only unless write is the point |
| Model | "cheapest model that reliably handles this task" — don't hardcode a specific model name, resolve it against whatever's currently configured/available |
| Dispatch mode | foreground / background, with one-line justification |
| Justification | why this must be a subagent, not a hook, skill, or main-agent task |
| Draft file | a ready-to-drop-in `.claude/agents/<name>.md` definition |

## Step 4 — Risk, redundancy, and final cut

1. Rank all candidates by impact and risk reduction, highest first.
2. **Reject** any pair of candidates that would need to edit the same
   file(s) concurrently — merge those into a single scope or keep it in
   the main agent instead.
3. Cap the final recommendation list at 3–5 well-scoped subagents. A
   sprawling roster degrades automatic delegation reliability more than
   it helps.

## Step 5 — Persist the findings

Draft `.claude/agents/*.md` files alone are not the durable record — the
*reasoning* is. Before ending:

- If the target repo has a memory scaffold (`PLAN.md`, `.claude/memory/`,
  `docs/adr/` — the `project-memory-template` layout), record the audit's
  outcome there: accepted candidates as PLAN items, and any
  architecturally significant accept/reject decision as an ADR.
- Rejected-with-reason candidates (hook-instead, skill-covered,
  not-worth-it) are worth one line each in the same record — they stop
  the next session from re-proposing them.
- If the repo has no memory scaffold, put the summary in the audit's
  final report and suggest `/setup-project-memory`.

Do not output generic categories without evidence. Execute a real scan of
this codebase and cite specific files, directories, or modules for every
candidate you propose.
