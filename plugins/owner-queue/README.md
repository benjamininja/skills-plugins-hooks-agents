# owner-queue

A Claude Code mod that shows what is waiting on the owner: the decisions and
by-hand actions listed in a project's `.claude/memory/NEEDS-OWNER.md`.
A decision is answered by pressing one of its options.

- A band above the prompt gives the counts and a `Show queue` / `Hide queue`
  button.
- The pane lists each item, collapsed by default. An open item has
  `Copy name` (one line: its place, title and ticket), `Copy all` (the title
  and detail as plain text) and `Mark done` (removes the item from the file).
- An open decision has one button per option, the recommended one marked.
  Pressing one writes an `Answer:` line into the entry and sends the answer
  to the session's chat as the owner's words. `Other...` puts a draft in the
  prompt box instead. An answered decision moves to "Answered, waiting for
  pickup", where `Change answer` opens it again.
- The pane keeps its own record of the `Answer:` lines it wrote. A line it
  did not write is flagged, so an answer typed into the file by anything
  else is not taken for the owner's.
- One queue for every session: from a git worktree the pane reads the main
  checkout's file, and its footer names the file it read.
- `Refresh` reads the file now. It is also read every 5 seconds and after
  each tool call.
- `/owner` opens the pane and prints the counts.
- In a project with no `NEEDS-OWNER.md` the mod stays hidden.

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
