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
- Text the owner must paste goes in a fenced block, one fence per
  paste. Inline code is for names only.
- `- Session: <id>` is optional: the id of the session the answer goes
  back to. `/owner id` prints a session's id.
- Secrets are named, never written. No personal details of the owner,
  and no name the project keeps private.

Answers:

- A button in the pane writes `- Answer: ...` as the last field.
  **No agent writes, edits or removes an `Answer:` line.**
- An action may be marked `[x]` by the pane; ticked entries are deleted
  at the next state-back.
- Each entry says who raised it and when; the answer is recorded on its
  ticket.

## Decisions

## Actions
