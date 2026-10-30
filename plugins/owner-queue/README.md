# owner-queue

A Claude Code mod that shows what is waiting on the owner: the decisions and
by-hand actions listed in a project's `.claude/memory/NEEDS-OWNER.md`.
A decision is answered by pressing one of its options and `Submit`.
`Post comment` sends typed words at once to the session that raised an
entry, as a comment or as the answer.

- A band above the prompt gives the counts and a `Show queue` / `Hide queue`
  button.
- The pane's first line gives the mod's version. Its footer names the file
  it read and links to it.
- The pane lists each item, collapsed by default. An open item has
  `Copy name` (one line: its place, title and ticket), `Copy all` (the title
  and detail as plain text) and, on the last row, `Mark done`. Every `code`
  span has a `Copy: ...` button directly under the field that holds it. A
  field written `1. ... 2. ... 3. ...` is drawn as a list, one step per row,
  and each step's buttons sit under that step. A
  line separates the entry's text and options from these buttons.
  `/owner show` prints an entry in the chat, where the mouse can select it.
- Message back: an entry may carry `- Session: <id>`, the session its
  answer goes back to. That session's own copy of the mod sees the
  pane-written `Answer:` line (or the item marked done) at its next read
  and says it in its own chat as the owner's words, once; a closed session
  gets it when it is next opened. Submit says in the pressing session only
  the entries that name it or name no session. The mod tells each session
  its id in the system prompt, and `/owner id` prints it.
- A fenced code block inside an entry is one chunk: the pane draws it
  under the field or step that holds it, with one `Copy block N` button
  that copies it with its line breaks.
- For whoever writes an entry: anything the owner types or pastes by hand
  goes in code marks, one value per mark, with no prose inside; a command
  the owner runs goes in a fenced block; steps are numbered `1.`, `2.`.
- An open decision draws every option in full as text, then one row of
  short `Choose (a)` buttons, the recommended one marked, then a row of
  `Copy: ...` buttons, one for each `code` span of the options.
- A pressed option or `Mark done` is only staged. The row says so in green,
  and pressing the same button again takes it back. `Submit (N)` then
  writes everything staged in one pass: an `Answer:` line per decision, a
  ticked box per item marked done, and one message to the session's chat
  as the owner's words. `Clear` drops what is staged.
- Every message the pane sends to a chat has a `Time:` line, the moment
  the owner pressed or typed. A message with an old time is a repeat.
- An answered decision moves to "Answered, waiting for pickup", where
  `Change answer` opens it again.
- `Post comment`, on every open entry, sits on the last row beside
  `Mark done` and opens a one-line field under that row, below a line,
  with `Cancel` beside it and a box that shows what is typed in full. What is typed goes out at once; it does not wait for `Submit`.
  - `Write in editor`, beside `Post comment`, is for a longer text: it
    opens a draft file in the system's text editor. What is saved there
    shows in the box within 5 seconds, and the send buttons send it, as one
    line. The draft files are in the mod's own `drafts` folder, outside
    any repository; a sent or cancelled draft is emptied. `Copy path` gives
    the file's path where no editor could be opened.
  - `Send comment`, or Enter in the field: the pane adds
    `- Note: <text> | pane, <day> <time>, session <id>` to the entry, which
    stays open and shows "You said, <time>: <text>". An entry may hold
    several.
  - `Send as answer`, on an open decision: the pane writes
    `- Answer: (other) <text> | pane, ...` and the decision moves to
    "Answered, waiting for pickup".
  - `Cancel` closes the field and drops what was typed. Empty text is
    refused.
  - The text is said in the pressing session's chat when the entry names
    that session or names none. Otherwise the session the entry names says
    it in its own chat at its next read, once, as for an option's answer.
  - Typed text is kept as one line; a code fence in it is dropped.
- The pane keeps its own record of the `Answer:` and `Note:` lines it
  wrote. A line it did not write is flagged and is never carried to a
  session, so text typed into the file by anything else is not taken for
  the owner's.
- One queue for every session: from a git worktree the pane reads the main
  checkout's file. When it cannot find the main checkout it reads the
  session's own copy and says so in bold.
- `Refresh` reads the file now. It is also read every 5 seconds and after
  each tool call.
- The pane never opens by itself: `Show queue` or `/owner` opens it, and a new entry only updates the status line and shows a toast.
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
pane writes an `Answer:` or a `Note:` line; no agent writes, edits or
removes one.

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
