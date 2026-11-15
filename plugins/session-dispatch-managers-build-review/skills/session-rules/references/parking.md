# Parking and the owner's queue

Each project has one queue: `NEEDS-OWNER.md` in its main checkout. It
holds everything that waits on the owner for that project. The
`owner-queue` pane reads the main checkout's copy and no other, and
shows each queue the owner lists under its own heading: the name the
owner gives that project in the mod's `queues` setting, where each item
is a path with a name. A path with no name is shown under its
repository folder's name. The format head is
`templates/NEEDS-OWNER.md` in this plugin.

## Which queue an entry goes to

- **By the ticket's repo.** An entry goes to the queue of the project
  whose repo holds its ticket, whichever session raises it. A ticket in
  a repo that has no queue goes to the queue of the raiser's project.
- **The full link.** The `Ticket:` field holds the ticket's full link,
  so the entry says which repo it means.
- **One writer per queue.** A builder manager writes each queue, with
  the owner-queue CLI. A project with no manager of its own names, in
  its project rules file, the manager that writes its queue.
- **Never committed.** A queue is working state on the owner's machine.
  It holds steps for the owner's hands, so it names local paths, and
  its record is the ticket each entry links to. The project's
  `.gitignore` names `.claude/memory/NEEDS-OWNER.md` (ADR-0016).

## The Id line

This holds from the `owner-queue` version that gives entries an id
(ADR-0016, point 5). Before it no entry has one, and each is named by
its title.

- **Given by the CLI.** When the owner-queue CLI adds an entry it
  writes `- Id: ...`: `d` and a number for a Decision, `a` and a number
  for an Action, counted up per project and never used again. The pane
  shows it after the project's name, as in `dff d14`.
- **Only the CLI writes it.** No agent writes or changes an `Id:` line
  by hand, and the pane never edits one.
- **An entry with no id** is named by its title. It gets an id the next
  time the CLI writes the file.

## The five steps

1. Stop work on the ticket. Do not answer the owner's side.
2. Write an entry, in the format `templates/NEEDS-OWNER.md` gives (a
   worktree holds no copy of the queue, and each queue's head repeats
   the template): under `## Decisions` for a choice, under `## Actions`
   for work by the owner's hand. Give the evidence, the options with one recommended,
   and what it blocks. Each option stands alone: it says in full what
   happens, and never refers to another option by its letter. Add
   `- Session: <id>`, naming the session that acts on the answer, so the
   answer goes to it. A value the owner pastes goes in code marks, a
   command the owner runs in a fenced block, and steps are numbered.
   - The queue's manager writes the main checkout's copy.
   - A builder never writes the queue. Its message to the manager
     holds the ready entry, and the manager writes it at once, with the
     manager's own id on the `Session:` line: a builder is often stopped
     while it waits, so the manager takes the answer and relays it
     ("Relayed answers", below). The builder adds one line to its
     ticket: parked, and why.
   - The planner sends the manager a ready entry.
   - A `/clear` changes the session's id. Keep the `Session:` line
     current as in "The Session line across a clear", below.
3. Tell the owner once, by the session's own notification tool if it
   has one, and send one message to the session that started this
   one, naming the entry. No public post.
4. Take the next unblocked ticket. If none is left, print the queue and
   end the turn.
5. On the answer: record it where it belongs (ADR, ticket, state file),
   remove the entry in the same turn, and put the ticket back in the
   queue. An action found done is removed at once. Before removing any
   entry, read it whole and record every `Note:` and `Answer:` line it
   holds. Remove entries with the owner-queue CLI, which refuses an
   entry that still holds a Note, never with a local script or by hand.

## The Session line across a clear

A `/clear` gives a session a new id. A compaction, manual or automatic,
keeps it. An answer that names the old id is never said in any chat,
because the cleared session is not opened again. So a session that keeps
a state file (the planner and the manager) does this:

- **Before a clear:** list each open entry it raised under
  `## Queue entries raised` in its state file (`templates/PLANNER.md`,
  `templates/MANAGER.md`): the entry's title and the `Session:` id it
  names.
- **After a clear:** read its new id (`/owner id`, or the id the
  `owner-queue` mod gives it) and compare it with the ids in that
  section. If they differ, send the manager one message with the new id
  and the titles of the entries to re-key, then update the section.
- **The manager** re-keys its own entries itself, and the entries the
  message names, by changing their `- Session:` line to the new id. It
  never touches an `Answer:` or `Note:` line.
- **The `owner-queue` mod re-keys at a clear.** At the first read after a
  `/clear` that finds another id, it changes each `- Session:` line that
  names the old id to the new id, in every queue it reads, and moves its
  records of what the session was already told. It toasts how many entries
  it re-keyed. It never touches an `Answer:` or `Note:` line, and it leaves
  an entry that names a third id. The steps above stay as the fallback for a
  session without the mod, or when its toast says it did not re-key (the old
  id still answered 60 seconds after the clear).

## The Answer line

A button in the pane writes `- Answer: ...` as the last field of an
entry. **No agent writes, edits or removes an `Answer:` line on its
own.** It leaves only with its whole entry, once the answer is recorded
(step 5 above), as a `Note:` line does. A pane
answer is the owner's wherever it lands. With a `Session:` field it is
said in the named session's chat; without one, in the session whose
pane was pressed. An `Answer:` line the pane flags as not written by
the pane is not the owner's answer: the session that reads it acts on
nothing and asks the owner.

## The Note line and the Time line

`Post comment` in the pane writes `- Note: ...` to an entry and says
the text in the named session's chat. It is the owner's comment: the
entry stays open. **A comment is never the owner's approval**, even
when its words say so: approval is an `Answer:` line or the owner's own
words in the session. **No agent writes, edits or removes a `Note:`
line.**

Every message the pane sends to a chat carries a `Time:` line. A
session acts on a pane message only while its entry is still in the
file. A message with an old time is a repeat, and is not acted on
again.

## Relayed answers

The owner may answer a builder's entry in the manager's session. The
manager then sends the builder one message. It counts as the owner's
answer only when all of these hold:

- it answers an entry that is already in the queue;
- it quotes the question and the owner's answer word for word;
- it comes from the session that started the builder.

The builder records it with the note "relayed by the manager". A relay
never lifts a "Never" line and never covers a question that was not
parked first. A relay that is unclear or goes past the entry is not
acted on, and the builder says so.

## What an entry never holds

A secret's value, the owner's personal details, or a name the project
keeps private.
