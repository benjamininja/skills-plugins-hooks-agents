# owner-queue

A Claude Code mod that shows what is waiting on the owner: the decisions and
by-hand actions listed in a project's `.claude/memory/NEEDS-OWNER.md`.
A decision is answered by pressing one of its options, or by typing an
answer, and `Submit`. `Post comment` stages typed words, as a comment or as
the answer; nothing is written or sent until `Submit`.

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
- A pressed option, `Mark done`, a typed comment and a typed answer are
  only staged. The row says so in green, and pressing the same option or
  `Mark done` again takes it back. `Submit (N)` then writes everything
  staged in one pass: a `Note:` line per comment, an `Answer:` line per
  decision, a ticked box per item marked done, and one message to the
  session's chat as the owner's words. `N` counts each staged option,
  answer, done mark and comment. `Clear` drops all that is staged. Until
  `Submit`, the file holds no line for it and no chat has heard of it.
- Every message the pane sends to a chat has a `Time:` line, the moment
  the owner pressed or typed. A message with an old time is a repeat.
- An answered decision moves to "Answered, waiting for pickup", where
  `Change answer` opens it again.
- `Post comment`, on every open entry, sits on the last row beside
  `Mark done` and opens a one-line field under that row, below a line,
  with `Cancel` beside it and a box that shows what is typed in full. What
  is typed is staged, as an option is: it waits for `Submit`.
  - `Write in editor`, beside `Post comment`, is for a longer text: it
    opens a draft file in the system's text editor. What is saved there
    shows in the box within 5 seconds, and the send buttons stage it, as one
    line, on the same path as typed text. The draft files are in the mod's
    own `drafts` folder, outside any repository; a staged or cancelled
    draft is emptied. `Copy path` gives the file's path where no editor
    could be opened.
  - `Send comment`, or Enter in the field: the comment is staged, drawn in
    green as "Comment, not submitted: <text>", and the box closes. An entry
    may hold several, beside a chosen option or a done mark. On `Submit` the
    pane adds `- Note: <text> | pane, <day> <time>, session <id>` to the
    entry, which stays open and shows "You said, <time>: <text>". The time
    is that of `Submit`.
  - `Send as answer`, on an open decision: the typed text is staged as the
    decision's `(other)` choice, drawn as "Chosen, not submitted: (other)
    <text>". It replaces a pressed option, and a pressed option or a later
    typed answer replaces it. On `Submit` the pane writes
    `- Answer: (other) <text> | pane, ...` and the decision moves to
    "Answered, waiting for pickup".
  - `Cancel` closes the field and drops what was typed. Empty text is
    refused. A staged comment is dropped by `Clear`, or when its entry
    leaves the queue file; it stays on an entry that has been answered.
  - On `Submit` the text is said in the pressing session's chat when the
    entry names that session or names none. Otherwise the session the entry
    names says it in its own chat at its next read, once, as for an
    option's answer.
  - Typed text is kept as one line; a code fence in it is dropped.
- The pane keeps its own record of the `Answer:` and `Note:` lines it
  wrote. A line it did not write is flagged and is never carried to a
  session, so text typed into the file by anything else is not taken for
  the owner's.
- One queue for every session of a project: from a git worktree the pane
  reads the main checkout's file. When it cannot find the main checkout it
  reads the session's own copy and says so in bold. Other projects' queues
  the owner lists are read too (see "One queue per project, many in one
  pane").
- `Refresh` reads the file now. It is also read every 5 seconds and after
  each tool call.
- The pane never opens by itself: `Show queue` or `/owner` opens it, and a new entry only updates the status line and shows a toast.
- `/owner` opens the pane and prints the counts. `/owner show` prints every
  entry into the transcript, and `/owner show a2` or `/owner show d1` one
  entry. A pane's text cannot be selected with the mouse; the transcript's
  can.
- With no `NEEDS-OWNER.md` anywhere, the project's own and every listed
  one, the mod stays hidden.
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

Options written `One; Two` are read too, lettered a, b, c by place. A key
such as `(a)` counts only at the start of the Options line or right after a
`;`; anywhere else it is part of the option's text, so `(b) the rest as in
(a)` is one option. If one key starts two options, the pane draws no options
for that entry and says the Options line is malformed. Write each option so
that it stands alone.

Only the pane writes an `Answer:` or a `Note:` line; no agent writes, edits
or removes one.

## Install (one shared copy, read at every launch)

Name the folder in the `env` block of `~/.claude/settings.json`. Point it at
the live clone of this repository, pinned to `main`, and not at a hand copy
(ADR-0011, revision 2): `<live clone>\plugins\owner-queue`. A hand copy, such
as one in `~/.claude/mods/owner-queue`, is never updated by a pull. An edit
that is merged reaches a session after the owner pulls the clone and starts a
new session.

```json
"env": {
  "CLAUDE_CODE_PLUGIN_DIRS": "<live clone>\\plugins\\owner-queue"
}
```

### One queue per project, many in one pane

Each project has one queue, `.claude/memory/NEEDS-OWNER.md` in its main
checkout, and one writer: that project's builder manager. Every project whose
sessions raise entries needs its own, started from
`plugins/session-dispatch-managers-build-review/templates/NEEDS-OWNER.md`.

The pane reads its own project's queue and, beside it, every queue the owner
lists in the plugin's `queues` setting. A session in a project with no queue
of its own, such as this repository's, shows the listed queues, is told its
id, and receives an answer to an entry that names it. The mod stays hidden
only when none of the files exists.

- **The setting.** It is the plugin's `userConfig` field `queues`: a list of
  absolute paths, each to one `NEEDS-OWNER.md`. The owner sets it, in
  `/config` as `owner-queue.queues` or in `~/.claude/settings.json`; no
  agent writes it. A path that is not absolute is ignored, and so is a
  path that names the session's own queue again. For example:

  ```json
  "pluginConfigs": {
    "owner-queue": {
      "options": {
        "queues": ["C:/Users/you/path/to/dynasty/.claude/memory/NEEDS-OWNER.md"]
      }
    }
  }
  ```

- **Grouped by project.** With more than one queue the pane puts a heading
  on each group, the queue's repo folder name (the folder above `.claude`),
  and numbers entries across all groups, so `d2` is the same entry in the
  pane and in `/owner show d2`.
- **Written where it came from.** Submit, `Change answer` and `Mark done`
  write into the file the entry was read from. The pane's record of the lines
  it wrote is kept under the file's path plus the entry, so a line in one
  queue is never taken for a line in another.

### The problems log

When the parser cannot draw an entry (today: an Options line that uses a key
twice), the pane adds one line to `~/.claude/owner-queue/problems.log`:
`<day> <time> | <queue file> | <entry title> | <kind of problem>`. It holds
no field value. An entry with the same problem is logged once, not on every
5-second read; it is logged again if it is fixed and then breaks again. The
mod creates the file when it first has a line to write. It is the owner's, to
read or delete.

### The `Session:` line

An entry's `- Session:` line is the id of the session that raises it, as
`/owner id` prints it in that session. A wrong id sends the answer to
another session.

## Develop

```bash
claude plugin validate plugins/owner-queue
```

```bash
claude plugin test plugins/owner-queue
```

Every render bug the owner reports becomes a test fixture in
`hooks/*.test.ts`, holding structure only, in the PR that fixes it.

`.claude-plugin/types/` is written by the engine at load and is not tracked.
