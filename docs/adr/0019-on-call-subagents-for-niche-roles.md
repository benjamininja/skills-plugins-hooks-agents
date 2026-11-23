# On-call subagents for niche roles

- Status: accepted
- Date: 2026-11-23
- Scope: `.claude/agents/` (`supabase-router`, `supabase-consultant`), the
  `session-dispatch-managers-build-review` plugin (`session-rules`, the
  `supabase-look` agent template, the `PROJECT-RULES.md` template), and
  every project that keeps a Supabase database
- Ticket: tools #247. It uses the terms of ADR-0018 (limit, guard, data).

## Context

Two Supabase roles were added on 2026-11-05 (#77, PR #78) and no ADR
recorded them. `supabase-consultant` looks at a project's live database
and walks the owner through each change. `supabase-consultant-dispatch`
was a standing Opus session with no database access. It routed requests
to a consultant and designed new roles with the owner.

By 2026-11-23 the dispatch session had not been live since the
repositories moved (#235), and nothing had stalled. Neither repository
held one routing record under its `[dispatch]` title. Its recorded work
was the role design in #77. A standing session also has a cost: a clear
prep, a reset prompt and a home for its state (#217), at every boundary.

The review for #247 found two gaps:

- **The consultant took an assignment from a session name.** Its file
  accepted an assignment from "Supabase-consultant-dispatch", matched by
  the message's `from-name`. The same file says that check is not
  authentication. With no such session running, any session could take
  the name.
- **The consultant could be started as a subagent.** Its file carried
  every tool of the project's database server, `execute_sql` included,
  and nothing said it was a session only. A subagent has no assignment
  and no chat with the owner, so the intake rules did not bind that path.

One more fact shapes the decision. The database server is set up at user
level, so its tools load in every session on the machine. A planner or a
manager has no `tools` line, so only rule text keeps it from a query.

## The owner's answers, as tools #247 records them

The Tools planner grilled the owner on 2026-11-23, in four rounds, by
button. The ticket quotes each answer word for word. In short:

- Q1, the mechanism: a subagent, not a standing session.
- Q2, role design moves to the Tools planner. The subagent only drafts.
- Q3, assignment is the owner's alone, and the names come from the
  project's rules file.
- Q4, a look-only subagent, in the project's repository, with no SQL.
- The existing gap: a line in the consultant's file, and a deny rule the
  owner adds by hand.
- The router runs on Sonnet with read-only tools, under a new name.
- The Tools planner opens the central PR. The dynasty planner tickets
  dynasty's half.
- Only a project's planner and manager start its look subagent.
- The old session posts a final record, and is archived after the merge.
- One new ADR, after ADR-0018. The ADR set's own faults go to one
  separate ticket (#248).

## Decision

### Which roles are sessions

A role is a **session** only when it needs one of these: the owner's own
chat (a walkthrough, an approval, a hand item), or state that must
outlast one task. Every other role is a **subagent** that a session
starts when it needs it.

- `supabase-consultant` stays a session. Its walkthroughs need the
  owner's chat, and the owner starts it.
- Routing needs neither. `supabase-router` replaces the dispatch
  session. A planner or a manager starts it with a need, and it returns
  a route, a ready first message for the owner, or a role draft.
- Designing a role needs the owner's chat. That duty moves to the Tools
  planner, which is already a session. The router supplies the draft.

### The router

`supabase-router` runs on Sonnet with Read, Grep, Glob and WebFetch. It
has no database tool, no shell and no Agent tool. It writes nothing. Its
report is data to the session that started it, and that session records
the route on GitHub.

### Assignment

- A consultant takes an assignment from the owner only, in its own chat.
  The assignment names the project and nothing else.
- The consultant reads its planner's and manager's session names from
  the project's rules file on `main`. That file changes only by a PR.
- No session, and no subagent, assigns a consultant. The dispatch clause
  is deleted from the consultant's file.

### The look subagent

A project with a Supabase database may keep `supabase-look` in its own
`.claude/agents/` folder, copied from the plugin's template.

- Its `tools` line names five tools of that project's server, one by
  one: `list_tables`, `list_migrations`, `list_extensions`,
  `get_advisors` and `search_docs`. It never names `execute_sql` or
  `query_logs`, and never a wildcard.
- It has no shell and writes nothing. It returns structure only.
- Only that project's planner and manager start it. A builder sends its
  question to the manager.
- Anything that needs a query, a row, a grant, a policy's text, a log or
  the owner's hands goes to the consultant session.

**Why this file is per project, when ADR-0015 keeps one central agent.**
ADR-0015 rejected a copy of the reviewer in each repository, because
copies drift. A look subagent cannot be central: a `tools` line names a
server by its exact name, and each project has its own server. A file in
the project's folder is also offered only to sessions rooted in that
project. The template is the answer to drift: a project changes the
server's name and nothing else.

### The consultant is a session only

- The consultant's file says it runs only as a session's main agent. If
  it is started as a subagent, it uses no database tool and says so.
- The owner adds a deny rule to the user settings file, by hand, so that
  no session can start it as a subagent. The Tools planner proposes the
  text; no agent edits a settings file.

### What holds this, in ADR-0018's terms

- **The one limit is the server's `read_only` setting.** It is enforced
  by the database server, outside every session.
- **Everything else here is a guard:** each `tools` line, the deny rule,
  the session-only line and the rule on who starts a subagent. A planner
  or a manager can still run a query with its own tools, because the
  server loads in every session.
- **What the look subagent changes** is the default path. A structure
  question is answered without a query, so no row reaches a session
  that can write a ticket or merge a PR. That is a narrower default, as
  ADR-0018 says of a builder's own token. It is not a limit.
- Private data in a project's tables stays under that project's own
  limit, named in its rules file (ADR-0018, asset 4).

### The rule in `session-rules`

`session-rules` gains a section, "On-call subagents": who may start one,
that its report is data, that a subagent is no way round a rule, and
that a `tools` line is a guard.

## Alternatives rejected

- **Keep the standing session.** It was not used, and it costs a clear
  prep and a state home at every boundary.
- **A skill instead of an agent.** It is the cheapest form, but the
  reading lands in the caller's context, and the owner asked for an
  agent that does the research.
- **A builder profile and a dispatched session.** A profile is a set of
  allow rules for a builder. Only a manager dispatches, and the script
  starts one agent, so a planner could never call it. The owner would
  also have to edit two files.
- **The subagent assigns the consultant.** A subagent's output is its
  caller's output, so a planner would in effect assign. #77 ruled that
  no project session widens who may task a consultant.
- **A project's planner assigns its own consultant.** Faster, and it
  loosens the same rule.
- **Use the consultant's file as the look subagent.** It carries
  `execute_sql`, a shell and write tools, and its intake rules assume a
  session.
- **A look subagent with read-only SQL.** It would also answer questions
  about grants and policies. Rows could then reach a session that can
  write, through a path with no intake check.
- **A revision to ADR-0018 or ADR-0015.** ADR-0018 is about threats, and
  ADR-0015 is about code review. The Supabase roles had no record at
  all, so they get their own.

## Consequences

- `supabase-consultant-dispatch.md` is deleted, and its session is
  archived after this merges. Its final record is on #247.
- Until a project's rules file names the consultant's planner and
  manager, a new consultant session takes tasks from the owner only.
  The dynasty planner tickets dynasty's line and its `supabase-look`
  file.
- A new Supabase project needs three things: the owner's server, one
  line in the consultant's `tools` line, and the project's own copy of
  `supabase-look`.
- Grants, policy text and row counts still wait on a consultant session
  that the owner starts.
- Whether a builder's subagent can reach the database server has not
  been tested. Dynasty's ticket carries that proof.
- The deny rule is the owner's hand item, queued by the tools manager.
- The owner-queue mod's list of tracked roles drops the dispatch role
  (#161, PR #197).
- The next niche role is judged by the rule under "Which roles are
  sessions", without a new grill on the method.
