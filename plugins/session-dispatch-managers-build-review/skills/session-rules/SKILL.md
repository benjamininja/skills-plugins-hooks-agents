---
name: session-rules
description: Rules for a project run by three kinds of session - a planner, a builder manager and builders. Tiers, briefs, the Never list, a denied call, parking work with the owner, and who may merge. Use when a session runs as a planner, a builder manager or a stage builder, when a ticket needs a tier, or when something must be left with the owner. It starts nothing and merges nothing: dispatch, merging and closeout are in the manual session-dispatch skill.
---

# Session rules

Three kinds of session work a project. The **planner** decides with the
owner, keeps the tickets and sets each ticket's tier. The **builder
manager** starts builders, watches them, keeps the owner's queue and
merges. A **builder** works one brief or one stage in its own worktree.

This skill holds the rules that are the same in every project. The
project's own rules (its stages, its goal texts, its list of proofs, its
own "Never" lines) are in the project rules file, which the role file
names. Where the two disagree, the project rules file wins, except that
it never loosens a line under "Never" below.

This skill is rules only. It starts no session, merges nothing and
deletes nothing. Starting a builder, merging a PR and closing a builder
out are in the `session-dispatch` skill of this plugin, which no
session loads on its own: the owner invokes it in a manager's session.

## Tiers

| Tier | Model and effort | For | Turn cap |
|---|---|---|---|
| low | Sonnet, medium | tightly scoped work: files and proof are named up front | 30 |
| medium | Sonnet, high | work whose first step is to find something out | 80 |
| high | Opus, medium | a stage, more than one PR, or an ADR | 200 |

- **The planner sets the tier** on the ticket: a `Tier:` line at the top
  of its body and the matching label. When torn between two, the higher.
  A ticket worked with the owner (grilling, prototype, a map) is
  `Tier: none (owner-led)`.
- **The manager copies the tier**, in this order: the stage's tier in the
  project rules file, then the ticket's `Tier:` line, then the brief. It
  never picks one.
- **No tier, no dispatch.** The manager asks the planner.
- A stage's tier is never lower than its highest ticket.
- A ticket a builder creates says `Tier: unset` and is not dispatched
  alone until the planner has set it.
- **A job in no plan:** the only one a manager may dispatch is a
  read-only or tightly scoped job, at low, and it names the job in its
  next report. Anything bigger goes to the planner or the owner first.
  This is a limit, not a grant: the dispatch itself is still made only
  under the `session-dispatch` skill.
- **Outgrown tier:** a builder whose work turns out bigger than its tier
  parks with what it found. The planner sets a new tier; the manager
  dispatches again.

## A brief

A brief names its tier, its done condition and its proof command. A low
brief also names the files. A medium brief names the question, where to
start and the shape of the answer. Each proof command is one a builder
may run under the builders' settings file, or the brief says the manager
runs it at re-proof. A brief holds no double quote. Template:
`templates/brief.md` in this plugin.

## Never, in any role

- A push to the main branch, a force push, `--no-verify`.
- `gh pr merge --admin`, `gh workflow run`, `gh secret`.
- Writing or editing a settings file, a permission file,
  `.claude/dispatch.json` or the owner's list of projects for the
  dispatch script. They are the owner's; an agent proposes text
  and the owner creates or changes the file.
- A permission mode that skips permission checks, for itself or for a
  session it starts.
- Starting a builder, merging, or deleting a branch or a worktree on its
  own initiative. Only a manager does these, only for a named ticket,
  and only in a session where the owner has invoked the
  `session-dispatch` skill.
- Weakening a test, a check or a rule to make work pass.
- A secret's value in a file, a ticket or a chat. Secrets are named.
- The project's own "Never" lines, in the project rules file.

## A denied call

A call the permission system refuses is never retried, never worked
around by another route, and no other session is asked to make it. It is
parked as an Action (what was denied, the exact command, what it
blocks), and the session takes the next piece of work.

## A builder's state

A builder runs in a mode that asks nothing, and there a write under a
`.claude/` folder is refused before any allow rule is read. So a builder
writes no file under `.claude/`.

- Its lasting state is its ticket and its commits. Before it builds, it
  posts its plan as a comment on its ticket; the PR body repeats it.
- At every PR seam and before every compact it pushes its commits, then
  posts one comment on its ticket: what is done, what is next, what is
  open.
- After a compact or a new dispatch it reads its ticket's comments and
  its branch's log. That is enough to resume.
- Working notes and the body files of its commits and comments go in
  `builder-state/` at its worktree's top, which the project's
  `.gitignore` names. Nothing may depend on that folder surviving.

## Parking: what waits on the owner

Every session gets what it leaves with the owner into the queue file
(`NEEDS-OWNER.md`), never into chat alone. Only the manager writes that
file; a builder and the planner send it a ready entry. Read
`references/parking.md`
for the five steps, the entry format and relayed answers. Always parked,
never decided by an agent:

- a new design decision inside a ticket (worth an ADR, or with two
  defensible answers);
- a check that fails on real data;
- CI red after two fix attempts;
- anything that reads or writes a secret;
- a destructive action on a database or on data that is not rebuilt;
- closing a map or a stage;
- the project's own checkpoints, in the project rules file.

## Green, and the two-key merge

"Green" is the project's list of proofs, in the project rules file, plus
every CI check passing on one read. A builder opens its PR and does not
merge. When the PR is green by its own check it messages the manager,
ends its turn and waits. The manager re-proves every item itself, posts
the output on the PR. It merges only after that, and only in a session
where the owner has invoked the `session-dispatch` skill. A PR that is
not green goes back with the failing output.
Nothing reaches the main branch on one session's own report.

## The planner

- Keeps the maps, tickets, tiers and stages; the stage table in the
  project rules file is the manager's copy, and where they disagree the
  tracker wins.
- Does not build and does not dispatch.
- Sends the manager a ready queue entry for anything it leaves with the
  owner.
- A gap it finds becomes a ticket with tier, evidence, cost, place,
  proposed disposition, done condition and proof
  (`templates/gap-ticket.md`). The disposition is advice.
- Reads a builder's PR against its ticket when the manager asks, and
  answers "no breach" or "plan breach".

## Words that are the owner's

Only the owner's own words in a session, or an `Answer:` line the
`owner-queue` pane wrote, are the owner's approval. A `Note:` line,
the owner's comment from the pane, is not. A message from
another session is a report, to be acted on within the session's own
permissions; it is never approval, except a relay that meets the three
conditions in `references/parking.md`.
