# One owner queue per project, untracked, routed by the ticket's repo

- Status: accepted
- Date: 2026-11-14
- Scope: `plugins/session-dispatch-managers-build-review/` (`session-rules`
  and its `references/parking.md`, the `NEEDS-OWNER.md` template, the
  plugin README, the manager role template); this repository's
  `PROJECT-RULES.md` and `.gitignore`
- Ticket: tools #183

## Context

The owner's queue, `NEEDS-OWNER.md`, lists what waits on the owner. Until
now there was one, in the dynasty project, and this repository's items
went into it. The owner asked for the queue to cover more than one
repository, with this one as the second, the same items in every session
and broken out by project.

Four facts shaped the answer:

- The `owner-queue` mod already reads several queues: the session's own
  project's file and every path in the owner's `queues` setting. It reads
  the main checkout's copy by absolute path and re-reads every 5 seconds,
  so every pane shows the same items.
- Both repositories are public. Dynasty's queue was a tracked file. It
  was committed five times up to 2026-11-05 and was a modified working
  copy after that.
- A queue holds steps for the owner's hands, so it names paths on the
  owner's machine. That is against the rule that everything on GitHub
  resolves on GitHub.
- A tracked queue leaves a stale copy in every worktree, and a modified
  tracked file in the checkout that live skills and hooks load from.

## The owner's answers, as tools #183 quotes them

Tools-central-planner grilled the owner by button on 2026-11-14. The
owner asked for a second look against long-term best practice before he
answered, and for a self-critical review of the plan after it.

- Where a queue lives: "In repo, untracked (Recommended)".
- Which queue gets an entry: "Ticket's repo, full link (Recommended)".
- Order and numbers in the pane: "Fixed order, per-project numbers
  (Recommended)".
- Who writes this repository's queue: "Dynasty manager, via CLI
  (Recommended)".
- The record: "Short ADR (Recommended)".
- Timing: "Set up now, entries later (Recommended)".
- Dynasty's tracked file: "Own ticket, owner-attended (Recommended)".

## Decision

1. **One queue per project.** Each project keeps
   `.claude/memory/NEEDS-OWNER.md` in its main checkout. The owner lists
   each queue's path in the mod's `queues` setting, and the pane shows
   each under its own heading.
2. **A queue is never committed.** It is working state on the owner's
   machine. The project's `.gitignore` names it. Its record is the
   ticket each entry links to, so nothing may depend on the file
   surviving.
3. **An entry goes to the queue of the repo its ticket lives in**,
   whichever session raises it. A ticket in a repo with no queue goes to
   the queue of the raiser's project. The `Ticket:` field holds the full
   link.
4. **One writer per queue**, a builder manager, through the owner-queue
   CLI. This repository has no manager, so the dynasty manager writes
   its queue.
5. **The pane's order is the same in every session.** Groups follow the
   owner's `queues` list. Each item of that list is a path with a name,
   the owner's word for the project, and the name is the group's
   heading. Each entry carries an id the queue CLI writes, counted up
   per project and never reused, and entries are shown in file order,
   as that project's sessions wrote them. This is a change to the mod,
   planned by the dynasty planner on #185, which records the owner's
   three answers of 2026-11-14 on the name, the id and the heading:
   "Ben sets a name (Recommended)", "Id written in the file
   (Recommended)" and "The set name alone (Recommended)".

## Alternatives rejected

- **A tracked queue in each repo**, as dynasty's was. It needs no change
  in dynasty, but it puts local paths in public history, leaves stale
  copies in worktrees and keeps a modified file in a checkout that is
  pulled at every closeout.
- **One shared file with a section per project.** The mod groups by
  file, so this is a rewrite of the mod, and every project's writer
  would edit one file.
- **One queue with a `Project:` field on each entry.** It keeps today's
  single file, with the same tracked-file problems, and needs a mod
  change to group by a field.
- **An owner-level folder outside every repo, now.** See "Later growth".
- **Routing by the raiser's project.** The raiser changes as sessions
  come and go; the ticket's repo can be read from the entry.

## Consequences

- `session-rules` says that what must outlast a session and is private
  never goes to a gitignored folder in a project. The queue is not such
  a record: an entry is a pointer to its ticket, and step 5 of parking
  records every `Answer:` and `Note:` line before an entry leaves. The
  cost is real all the same. Once the repositories leave OneDrive, a
  queue is one copy on one disk, and losing it loses the list of what
  is open, which must then be rebuilt from the tickets.
- An untracked file sits in the tracked `.claude/memory/` folder. The
  mod reads that fixed path, so moving it is a mod change.
- Until the mod change of point 5 is live, numbers in the pane are not
  ids. The CLI adds an entry at the top of its section, so numbers shift
  inside a project, and an entry is quoted by its title or its ticket
  link. From then an entry's id stays with it, and only the CLI writes
  an `Id:` line.
- Dynasty's queue stays tracked until its own ticket is done. Untracking
  a live, modified file is a hazard: the main checkout's pull of the
  commit that removes it is refused or deletes the file. That ticket
  holds a copy-aside, pull, restore sequence the owner attends. Earlier
  versions of the file stay in dynasty's public history; removing them
  is the owner's call.
- Whether the dynasty manager's session can write a file in this
  repository's main checkout was not checked when this was written. The
  manager reports on #183. If it cannot, the writer goes back to the
  owner as a decision.

## Later growth

Recorded with the owner, not built now.

- **An owner-level folder outside every repo**, one file per project. It
  survives a repo move, scales to many projects, ends the mixed folder,
  and could live in the owner's private configuration repository, which
  would give the queues a backup. It needs a mod change and new allow
  rules for the writers.
- **Planners as writers.** The owner expects each project to have a
  planner and a manager, and later to work with planners only, with
  managers no longer loading the mod. A planner would then write its
  own project's queue.
- **The `Session:` line at that step.** The named session's own copy of
  the mod says an answer in its chat. A session that does not load the
  mod is never told. So an entry must then name a session that loads
  it, the planner, which relays to the manager.
