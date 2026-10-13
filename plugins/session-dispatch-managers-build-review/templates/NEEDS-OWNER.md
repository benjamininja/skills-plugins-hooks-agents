# NEEDS-OWNER

What waits on the owner, in one place. The `owner-queue` pane reads the
main checkout's copy of this file and no other.

Format:

- Two sections only: `## Decisions` and `## Actions`.
- One item per `### [ ] Title`.
- Fields are written `- Label: value`.
  - A decision carries Ticket, Context, Options, Recommended, Blocks,
    Raised.
  - An action carries Ticket, Steps, Context, Blocks, Raised.
- Options are written `- Options: (a) ...; (b) ...` and
  `- Recommended: (a), because ...`. The pane shows one button per
  option.
- Anything the owner types or pastes by hand goes in code marks, one
  value per mark, with no prose inside the marks. The pane draws a Copy
  button for each, under the field that holds it.
- A command the owner runs goes in a fenced block, one fence per
  command, written exactly as it is run. The pane copies it whole.
- Steps are numbered `1.`, `2.`, `3.` inside the Steps field. The pane
  draws one step per row, with that step's Copy buttons under it.
- `- Session: <id>` is optional: the id of the session the answer goes
  back to. `/owner id` prints a session's id.
- Secrets are named, never written. No personal details of the owner,
  and no name the project keeps private.

Answers:

- A button in the pane writes `- Answer: ...` as the last field.
  **No agent writes, edits or removes an `Answer:` line.**
- `Post comment` in the pane writes `- Note: ...`: the owner's comment.
  The entry stays open, and may hold several. **No agent writes, edits
  or removes a `Note:` line**; notes leave with the entry.
- Every message the pane sends to a chat has a `Time:` line. Act on a
  pane answer only while its entry is still in this file; a message
  with an old time is a repeat.
- An action may be marked `[x]` by the pane; ticked entries are deleted
  at the next state-back.
- Each entry says who raised it and when; the answer is recorded on its
  ticket.

## Decisions

## Actions
