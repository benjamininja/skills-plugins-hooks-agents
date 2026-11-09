---
name: tools-code-review
description: The code-review ruleset for the skills-plugins-hooks-agents repo, for the pr-code-reviewer agent at the builder manager's re-proof only. Names which paths count as code, which findings block a merge, and the bug patterns this repo has fixed. Load it only when a reviewer packet names it, never for a general review request.
---

# tools-code-review

This repo's ruleset for the code review at re-proof. The process (the
packet, the effort per tier, the one round, the manager's record) is in
the `session-rules` skill, `references/code-review.md`. This skill holds
only what is particular to this repo.

Built from the 22 bug-fix PRs among this repo's 63 merged PRs to
2026-11-09 (6, 26, 28, 32, 41, 42, 62, 63, 64, 65, 66, 67, 74, 75, 76, 86,
89, 96, 100, 102, 103, 109). Each pattern names the PRs it came from.
Record: tools #113 (the draft, issuecomment-6730689017, and the reads
after it).

## 1. What is reviewed

**Code:** any changed file that is not Markdown (scripts, the
owner-queue mod's source and tests, `hooks/`, `tools/`, `tests/`,
`.github/workflows/`, and every `.json`, including `manifest.json`,
`vendor-skills.json`, `plugin.json` and the settings and profile
examples under `templates/`), and any edited frontmatter block of a
Markdown file (a `SKILL.md`'s or an agent file's, its `tools:` line
included).

**Rule or skill text:** the Markdown body outside frontmatter: a
`SKILL.md` body and its `references/`, agent bodies, the Markdown
templates, READMEs and `docs/`.

- **A builder PR that touches code:** the full review, at its
  tier's effort. The reviewer reads the diff and the code each hunk
  calls; for a script, the whole step it edits. Rule and skill text in
  the same PR is checked against P10 and P2.
- **A builder PR that changes only rule or skill text:** the light
  review, at `low`, checked only against P10 (a contradiction, or a
  loosened Never or denied-call line) and P2 (a tool a body asks for but
  is not given).
- **Skipped:** planner and manager PRs (state-backs, syncs) and
  docs-only state-backs.

## 2. Blocking and advisory

As dynasty's ruling on its own ruleset (dynasty #490,
issuecomment-6730448396), so the manager runs one process in both repos:

- **Blocking:** a finding with a concrete trigger that can bypass a
  guard, widen a permission, leave a session running unchecked, lose or
  half-write a file or manifest, break a `~/.claude` link, or show the
  owner a wrong result. A blocking finding names the input that triggers
  it; a blocking-class finding with no concrete trigger is advisory.
- **Advisory:** everything else a pattern below names. Each advisory is
  answered once. The manager may merge with advisories open and lists
  them in the re-proof comment. The agreed, deferred ones go in one
  ticket per PR. A disputed advisory is closed or kept by the manager's
  ruling, with no ticket.
- **Not a finding:** style, anything CI already gates (pytest,
  `CATALOG.md is current`), and design the ticket settled.

## 3. Bug patterns this repo has fixed

| # | Pattern | From | Check on the diff | Class |
|---|---|---|---|---|
| P1 | Frontmatter that silently fails to load | #62, #63, #41 | Any edited frontmatter value with an unquoted `: ` parses under `yaml.safe_load`; a model alias is real; the file falls inside a test's glob. | Blocking |
| P2 | A body asks for a tool the session is not given | #76, #89, #66 | Every tool, skill or plugin a body, `readLine` or brief names is in `tools:` or `allow`, and `--plugin-dir` is passed. A tool *added* to `tools:` or `allow` is justified only when the PR names the ticket line that asks for it. | Advisory for a missing tool; blocking for an added one until justified |
| P3 | Guard bypass by a command variant | #42, #74, #86 | Each new or changed block rule has test cases for `-C`/`-c`, quotes, `bash -c`, `&&` `;` `\|`, a `2>&1` between tokens, long, abbreviated and combined flags, `HEAD`/`@`, the PowerShell matcher and a `#` comment; it fails closed when a helper (`gh`) is missing, fails or times out. | Blocking |
| P4 | A side effect reported but never checked | #109, #102, #64/#65, #42 | After any stop, kill, delete or resume, the code re-reads state and reports a failure as a failure. The PR's proof lines match its final commit. | Blocking when a session may be left running |
| P5 | One early read of async state | #109 | A check after a background start polls to a deadline and keeps "not yet" apart from "wrong". | Blocking |
| P6 | A path no test or CI runs | #66, #109, #96, #65 | The PR names which changed lines no test runs and how they were proven. A version bump greps every pinned copy (`VERSION`, `plugin.json`, test regexes). CI runs pytest only, never `claude plugin test`, so a mod change names its `claude plugin test plugins/owner-queue` run; until that is a Green item, the reviewer flags a mod change with no mod-test run. | Advisory; blocking for a guard |
| P7 | Windows, OneDrive and junction filesystem behaviour | #26, #28 | No `rmtree`, `rename` or `move` of a directory that may be a junction target; staging outside OneDrive; path compares normalise `/` and `\`, a trailing separator and case. | Blocking |
| P8 | Uneven error handling across sibling paths | #96 | Every network call handles the same errors as its sibling, and the code exits before its first write. | Blocking where a manifest could be half-written |
| P9 | CLI JSON parsed with no error handling | #116, PR #120 | A parse of `claude ... --json` output is wrapped, checks `$LASTEXITCODE`, and on failure reports the session as started but unchecked; the same file's config parses already do this. | Blocking |
| P10 | Rule text that contradicts or quietly loosens another file | #67 then #86, #66 then #102, #6, #103 | Grep session-rules, the stage-builder template, dispatch.md, manager.md, PROJECT-RULES and the READMEs for the same claim. A deleted never or denied-call phrase needs a stated reason. | Blocking if a Never or denied-call line is loosened, unless the PR cites the owner's decision on its ticket; else advisory |
| P11 | A parser of owner-written text guesses at ambiguous input | #100, #97 | Delimiters count only at boundaries; ambiguous input is flagged malformed, not guessed; each owner-reported render bug gets a fixture. | Blocking |
| P12 | Vendored upstream text changes a skill's safety tier | #103, #41 | On a re-vendor diff, grep the new text for delete, deploy or permission verbs; if the skill is model-invocable, skill-safety-auditor runs (an Always-park). | Blocking |
| P13 | A mod write to a queue file | #81, #100, #110, #111 | The write changes only the lines it targets, and a test proves the rest of the file is byte-identical; a `Session:` re-key never touches an `Answer:` or `Note:` line; a staged choice writes nothing before Submit. | Blocking |
| P14 | Text said in a chat as the owner's words | the pane's record rule (`plugins/owner-queue/README.md`, the bullet "The pane keeps its own record") | Only what the owner pressed or typed is submitted as the owner's words (`$.prompt.submit` with `asUser`). Text from the queue file that the pane did not write, such as an entry's body, which an agent wrote, goes in as quoted entry content, never as the owner's words. | Blocking |

Two more, advisory:

- An always-on hook or UI behaviour that costs context or takes focus
  must be silent on the happy path (#32, #64).
- A `/security-review` that reported an empty or unrelated diff (#100,
  #102, #103) is noted, since `CLAUDE.md` already asks to confirm the
  reported diff.

## 4. This repo's rules the reviewer checks against

- **PROJECT-RULES Always-parks** (P12, P3): a `disable-model-invocation`
  change, a new vendored skill or a safety field of `vendor-skills.json`
  goes to skill-safety-auditor first; a hook's blocking rules get the
  manager's own hook-test run.
- **PROJECT-RULES Never** (P7, P10): no `--apply`, nothing under
  `~/.claude/` directly, no branch switch or commit in the main
  checkout, pulls only at closeout. That file "never loosens its Never
  lines".
- **Frontmatter** (P1): a `SKILL.md` carries `name` and `description`;
  an agent "must load as YAML, with `name` equal to its file name".
- **CI** (P6): `.github/workflows/test.yml` runs
  `python -m pytest -q tests` on Ubuntu and Windows, plus the
  `CATALOG.md` check. It does not run the mod tests, so the reviewer
  flags a mod change with no mod-test run.
- **Links** (P7): ADR-0003, junctions are the default.

## 5. Updating this ruleset

A pattern caught on two PRs becomes a one-line rule. The manager drafts
it and the Tools planner reads it. It lands in
`.claude/memory/PROJECT-RULES.md`, not `CLAUDE.md`, in a planner PR,
since builders may not write under `.claude/`. A fix PR for a bug a
review missed gets a pattern line drafted the same way, and a low-tier
builder lands the read lines here in batches.
