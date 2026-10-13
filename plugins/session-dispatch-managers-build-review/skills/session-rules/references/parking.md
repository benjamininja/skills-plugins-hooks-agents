# Parking and the owner's queue

One file holds everything that waits on the owner: `NEEDS-OWNER.md` in
the main checkout. The `owner-queue` pane reads that copy and no other.
The format head is `templates/NEEDS-OWNER.md` in this plugin.

## The five steps

1. Stop work on the ticket. Do not answer the owner's side.
2. Write an entry, in the format of the file's head: under
   `## Decisions` for a choice, under `## Actions` for work by the
   owner's hand. Give the evidence, the options with one recommended,
   and what it blocks. Add `- Session: <id>` so the answer comes back to
   the session that raised it. A value the owner pastes goes in code
   marks, a command the owner runs in a fenced block, and steps are
   numbered.
   - The manager writes the main checkout's copy.
   - A builder writes its worktree's copy and messages the manager, who
     copies the entry across at once.
   - The planner sends the manager a ready entry.
3. Tell the owner once, by the session's own notification tool if it
   has one, and send one message to the session that started this
   one, naming the entry. No public post.
4. Take the next unblocked ticket. If none is left, print the queue and
   end the turn.
5. On the answer: record it where it belongs (ADR, ticket, state file),
   remove the entry in the same turn, and put the ticket back in the
   queue. An action found done is removed at once.

## The Answer line

A button in the pane writes `- Answer: ...` as the last field of an
entry. **No agent writes, edits or removes an `Answer:` line.** A pane
answer is the owner's wherever it lands. With a `Session:` field it is
said in the raising session's chat; without one, in the session whose
pane was pressed.

## The Note line and the Time line

`Post comment` in the pane writes `- Note: ...` to an entry and says
the text in the raising session's chat. It is the owner's comment: the
entry stays open, and the comment is acted on as far as its words go.
**No agent writes, edits or removes a `Note:` line.**

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
