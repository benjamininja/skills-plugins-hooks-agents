# Parking and the owner's queue

One file holds everything that waits on the owner: `NEEDS-OWNER.md` in
the main checkout. The `owner-queue` pane reads that copy and no other.
The format head is `templates/NEEDS-OWNER.md` in this plugin.

## The five steps

1. Stop work on the ticket. Do not answer the owner's side.
2. Write an entry, in the format of the file's head: under
   `## Decisions` for a choice, under `## Actions` for work by the
   owner's hand. Give the evidence, the options with one recommended,
   and what it blocks. Each option stands alone: it says in full what
   happens, and never refers to another option by its letter. Add `- Session: <id>` so the answer comes back to
   the session that raised it. A value the owner pastes goes in code
   marks, a command the owner runs in a fenced block, and steps are
   numbered.
   - The manager writes the main checkout's copy.
   - A builder never writes the queue. Its message to the manager
     holds the ready entry, and the manager writes it at once. The
     builder adds one line to its ticket: parked, and why.
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
   queue. An action found done is removed at once.

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
entry. **No agent writes, edits or removes an `Answer:` line.** A pane
answer is the owner's wherever it lands. With a `Session:` field it is
said in the raising session's chat; without one, in the session whose
pane was pressed.

## The Note line and the Time line

`Post comment` in the pane writes `- Note: ...` to an entry and says
the text in the raising session's chat. It is the owner's comment: the
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
