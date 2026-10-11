# owner-queue

A Claude Code mod that shows what is waiting on the owner: the decisions and
by-hand actions listed in a project's `.claude/memory/NEEDS-OWNER.md`.

- A band above the prompt gives the counts and a `Show queue` / `Hide queue`
  button.
- The pane lists each item, collapsed by default. An open item has `Copy`
  (plain text of the title and detail) and `Mark done` (removes the item from
  the file).
- `/owner` opens the pane and prints the counts.
- In a project with no `NEEDS-OWNER.md` the mod stays hidden.

## File format it reads

```markdown
## Decisions
### [ ] Short title
- Ticket: #123
- Context: ...

## Actions
### [ ] Short title
- Steps: ...
```

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
