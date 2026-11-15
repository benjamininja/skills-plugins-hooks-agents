# PLAN

This file is a pointer. It holds no plan and no state.

- **Live state** is the planner's state file,
  [.claude/memory/PLANNER.md](.claude/memory/PLANNER.md). Its newest copy
  can be on the planner's open state PR; `gh pr list` shows it.
- **The work itself** is the open issues, each with its `tier:` label:
  `gh issue list --state open`.
- **The rules** are in the `session-rules` skill and in
  [.claude/memory/PROJECT-RULES.md](.claude/memory/PROJECT-RULES.md).

The file is kept so that a session told to read `PLAN.md` finds where the
plan lives. Do not write a plan here (#221).
