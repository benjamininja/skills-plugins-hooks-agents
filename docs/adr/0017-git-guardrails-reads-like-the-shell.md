# git-guardrails reads commands by the shell's rules, and tries what it can't read as git

- Status: proposed. The decision text below is a draft for Ben to accept
  at PR review, before merge (Ben's ruling on #168, question 4).
- Date: 2026-11-14
- Scope: `hooks/git-guardrails/block-dangerous-git.sh`, its README and
  `tests/test_git_guardrails.py`
- Ticket: tools #168; the design is #168 issuecomment-6885270333, and Ben's
  rulings are issuecomment-6885492170

## Context

The hook judges the text of one shell tool call. Its is-it-git gate and
every check matched the literal lowercase word `git`, followed by
whitespace. So `"git" reset --hard`, `g''it clean -f`, PowerShell
`Git checkout .` and `& "C:\Program Files\Git\cmd\git.exe" push origin
main` skipped every check, not only the push check (F5, found in the
review of PR #159). The server ruleset on `main` stops a push however it
is spelled, but it never sees the local destructive commands.

The obvious fix, adding those four spellings to the gate, is the pattern
#135 had to abandon. Rule A's word list of directory changes (PR #140) was
bypassed one spelling at a time (`$'\x63d'`, `$(printf c)d`, `${v}d`), and
Rule B replaced it with an allowlist. A gate list of git spellings has the
same next spellings waiting: `g\it`, `$'\x67it'`, `/usr/bin/g?t`,
`/usr/lib/git-core/git-push`.

## Decision

- **Read, don't list.** Each segment is read the way Bash reads it and the
  way PowerShell reads it: quotes removed and joined, escapes resolved. A
  word whose last path part is `git` in any case, with an optional
  `.exe`, `.cmd`, `.bat` or `.com`, is `git`. Both readings run for both
  tools.
- **The whole segment is read**, not only the git name (Ben, question 1).
  So a quoted refspec such as `HEAD:ma''in` reads `main` and blocks.
- **What the hook can't read is tried as git.** A word holding `$` or an
  unquoted glob, right before a guarded verb or a dash word, gets a
  reading with that word as `git`. If that reading blocks, the command
  blocks with "cannot tell whether '<word>' is git".
- **Add readings, never replace them.** The literal reading the hook had
  before still runs, and a block from any reading stands. So no earlier
  block can weaken, and an exemption holds only when it holds in every
  reading.
- **A future bypass of the same kind is fixed in the reading**, not by
  adding a form to a list.

## Alternatives rejected

- **A list of git spellings for the gate.** It is bypassed one spelling
  at a time, as #135's Rule A was.
- **Refuse instead of read**: block any segment with a guarded verb whose
  git-like word isn't plain lowercase `git`. It still needs a lexer to
  spot `g''it`. It also blocks ordinary PowerShell, such as
  `& "C:\Program Files\Git\cmd\git.exe" push origin my-feature`.
- **The reading for the git name only** (question 1, option 2). The hook
  would read the name one way and the refspec another, which is the
  mismatch F4 came from.

## Consequences

- The four F5 spellings, and the others of their class, are judged as
  git for every guarded command. Each has a test in Bash and PowerShell.
- The hook gains one `awk` program, the lexer. A command with quotes or
  a spelled name runs the checks once for each distinct reading (at most
  a few). A force-delete name is asked of `gh` once per command.
- Case-folding is stricter than Bash on Linux, where `GIT` is not git.
  That is the fail-closed side.
- Still out of reach: a refspec built at run time, F13,
  `git switch -c "$x"main`, a name built at run time that does not sit
  before a guarded verb, and unknown git global options (#200). The
  ruleset covers these only when they push to `main`. For the local
  destructive commands (`reset --hard`, `clean -f`, `checkout .`,
  `restore .`, a force branch delete) nothing behind the hook covers them.
- The reader is not a full shell parser: shell syntax it does not parse is
  tracked on #295.
