# owner-queue

A Claude Code mod that shows what is waiting on the owner: the decisions and
by-hand actions listed in a project's `.claude/memory/NEEDS-OWNER.md`.
A decision is answered by pressing one of its options, and nothing is
written until `Submit`.

- A band above the prompt gives the counts and a `Show queue` / `Hide queue`
  button.
- The pane's first line gives the mod's version. Its footer names the file
  it read and links to it.
- The pane lists each item, collapsed by default. An open item has
  `Copy name` (one line: its place, title and ticket), `Copy all` (the title
  and detail as plain text), `Print in chat` (the same text as a notice in
  the transcript, where the mouse can select it; the model does not receive
  it), one `Copy: ...` button for each `code` span, directly under the
  entry's text, and, on a row of its own, `Mark done`.
- Message back: an entry may carry `- Session: <id>`, the session its
  answer goes back to. That session's own copy of the mod sees the
  pane-written `Answer:` line (or the item marked done) at its next read
  and says it in its own chat as the owner's words, once; a closed session
  gets it when it is next opened. Submit says in the pressing session only
  the entries that name it or name no session. The mod tells each session
  its id in the system prompt, and `/owner id` prints it.
- A fenced code block inside an entry is one chunk: the pane draws one
  `Copy block N` button for it and copies it with its line breaks. An
  entry that has a block gets no button for its inline `code` spans, so
  put everything meant for one paste inside one fence.
- An open decision draws each option in full as text, with a short
  `Choose (a)` button under it, the recommended one marked, and a
  `Copy: ...` button beside it for each `code` span of that option.
- A pressed option or `Mark done` is only staged. The row says so in green,
  and pressing the same button again takes it back. `Submit (N)` then
  writes everything staged in one pass: an `Answer:` line per decision, a
  ticked box per item marked done, and one message to the session's chat
  as the owner's words. `Clear` drops what is staged.
- `Other...` puts a draft in the prompt box instead. An answered decision
  moves to "Answered, waiting for pickup", where `Change answer` opens it
  again.
- The pane keeps its own record of the `Answer:` lines it wrote. A line it
  did not write is flagged, so an answer typed into the file by anything
  else is not taken for the owner's.
- One queue for every session: from a git worktree the pane reads the main
  checkout's file. When it cannot find the main checkout it reads the
  session's own copy and says so in bold.
- `Refresh` reads the file now. It is also read every 5 seconds and after
  each tool call.
- `/owner` opens the pane and prints the counts. `/owner show` prints every
  entry into the transcript, and `/owner show a2` or `/owner show d1` one
  entry. A pane's text cannot be selected with the mouse; the transcript's
  can.
- In a project with no `NEEDS-OWNER.md` the mod stays hidden.
- A session loads the mod once, at launch. A session started before an
  update keeps the old copy; the version line shows which one is drawing.

## File format it reads

```markdown
## Decisions
### [ ] Short title
- Ticket: #123
- Context: ...
- Options: (a) one way; (b) another way
- Recommended: (a), because ...

## Actions
### [ ] Short title
- Steps: ...
```

Options written `One; Two` are read too, lettered a, b, c by place. Only the
pane writes the `Answer:` line.

## Install (one shared copy, read at every launch)

This folder is the only copy. Name it in the `env` block of
`~/.claude/settings.json`; every session then loads it straight from here,
and an edit here reaches each session on its next launch.

```json
"env": {
  "CLAUDE_CODE_PLUGIN_DIRS": "C:\\Users\\<you>\\...\\skills-plugins-hooks-agents\\plugins\\owner-queue"
}
```

## Develop

```bash
claude plugin validate plugins/owner-queue
```

```bash
claude plugin test plugins/owner-queue
```

`.claude-plugin/types/` is written by the engine at load and is not tracked.
