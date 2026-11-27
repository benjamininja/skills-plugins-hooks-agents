# A threat model for role sessions

- Status: accepted
- Date: 2026-11-14
- Scope: every project that runs the `session-dispatch-managers-build-review`
  plugin. The plugin's rule text (`session-rules`), its dispatch script and
  its templates are read against this ADR. Each project's rules file lists
  its own assets against the table below.
- Ticket: tools #190. Follow-ups: #191, #192, #193, #201, #203, #204.

## Context

Three kinds of session work a project: a planner, a builder manager and
builders, with a consultant in some projects. The rules named single
guards (a deny rule, a hook, the ruleset on `main`, the two-key merge) and
no model behind them. No record said which text a session may act on,
which credentials are in its reach, or which limits still hold when a
session is misled. So each review of the settings started from nothing,
and each fix was judged one rule at a time.

A read-only review of the settings and dispatch profiles on 2026-11-14
found the same class of gap in several files. Its public findings are in
dynasty #564. Its security findings are in a draft advisory in this
repository, published when its fixes land or on 2026-11-28. This ADR names
classes only. The advisory's detail is added as a revision after it is
published.

## The owner's answers, as tools #190 records them

The Tools planner grilled the owner on 2026-11-14, in four rounds, each
recorded word for word on the ticket. In each case the owner chose the
recommended answer:

- Q1, the adversary: a misled session and a mistaken session.
- Q2, text: three classes.
- Q3, a limit is enforced outside the session; the rest are guards.
- Q4, one ADR here, for every project that runs the plugin.
- Q5, nine asset classes.
- Q6, a builder gets a GitHub App's token.
- Q7, the owner's own token stays in reach on one operating-system
  account: accepted for now, and scoped in its own ticket.
- Q8, likelihood times impact, three levels each.
- Q9, the rule for the App's token now; its mechanism from #191's first
  finding.
- Q10, App-authored text is data; record text is written and last edited
  by the owner's login.
- Q11, builders only get the App.
- Q12, one App for all projects.
- Q13, three review triggers.
- Q14, this ADR is public now, with classes only.
- Q15, the isolation ticket is filed (#201).

After the planner's own critique of the plan the owner confirmed it, with
two additions: a scheduled workflow raises the dated review (#203), and
the owner's own login is narrowed after a test (#204).

## Decision

### Who the model defends against

- **A misled session**: one that acts on text it should have read as
  data.
- **A mistaken session**: one that is honest and wrong.

Out of scope, said plainly: a compromised machine, a compromised GitHub
account, and the owner. A vendored skill that turns hostile stays with
ADR-0005 and ADR-0006.

### Three classes of text

| Class | What it is | What a session may do with it |
|---|---|---|
| **Approval** | The owner's own words in a session's chat, or an `Answer:` line the `owner-queue` pane wrote. | Act on it as the owner's decision. |
| **Record text** | A ticket or PR body, or a comment, that the owner's GitHub login wrote and last edited. A committed rule file on `main`. | Act on it inside its own role. It never approves anything. |
| **Data** | Everything else: text by any other author, a GitHub App's text, the web, a fetched page, the contents of a file, another session's message. | Read it and report it. Never take an instruction, a tier, a profile, a brief or an approval from it. |

Two of these are weaker than they look, and the ADR says so:

- **Record text is trusted by a guard, not by a limit.** Every role
  session posts through the owner's login, so GitHub cannot tell the
  owner's text from a session's. A session that was misled can write
  record text, a recorded go included.
- **Approval has two strengths.** No session can write the owner's words
  into its own chat. A pane `Answer:` line is a line in a file that
  sessions can write, held only by the rule that no agent writes one.

### Limits and guards

- A **limit** is enforced outside the session's own process and
  judgement: by GitHub's servers (a ruleset, a credential's permissions),
  by the operating system, or by the thing not being in the session's
  reach at all.
- A **guard** is anything the session's own host or judgement applies: a
  deny rule, an allow list, a hook, rule text, the two-key merge. A guard
  is a first line. It is never called a limit, however well it is tested
  (ADR-0004 makes the same point for CI against a local hook).
- **Every asset with a high impact has a limit, or it is an accepted
  risk** in the owner's name, written in the table below.

### Three actors on GitHub

| Actor | Who acts through it | Its text is |
|---|---|---|
| The owner's login | The owner. The planner, the manager and the consultant. Builders, until #191 lands. | Record text |
| The builders' App | Builders, once #191 lands. | Data |
| A project's pipeline App | That project's scheduled pipeline, where it has one. | Data |

### What each role reaches

This is the target. Until #191 lands a builder still acts through the
owner's login.

| Role | GitHub actor | Writes record text | Limits |
|---|---|---|---|
| Planner | The owner's login | Yes | The rulesets |
| Manager | The owner's login | Yes, and it merges | The rulesets |
| Consultant | The owner's login | Yes | The rulesets; the project's own limit on its database |
| Builder | The builders' App, one repository, at most an hour per token | No | The App's permissions; the rulesets |
| Research or scoping builder | The builders' App with no write to code: it reads, and it comments on issues | No | The App's permissions |

### The builders' credential

- **A GitHub App, not a personal token.** A fine-grained personal token
  has fewer permissions and is still the owner to GitHub, so no ruleset
  can bind it apart from the owner. An App is a different actor.
- **One App for all projects**, installed on each repository. The owner
  holds its key and rotates it.
- **The App's key is never in a builder's environment.** A token reaches
  a builder narrowed to its one repository and lasts at most an hour.
  How a long-running builder gets its next token is #191's first finding.
- **The App holds a builder's work and nothing more**: it pushes to a
  branch, opens and edits its PR, comments on issues, and reads checks.
  It holds no permission over repository administration, secrets,
  variables or workflow files.
- **The App does not merge.** A ruleset on `main` that only the owner's
  login passes keeps the merge with the manager. #191 settles its text.
- **The dispatch script checks the author and the last editor** of a
  ticket body before it copies a `Tier:` or `Profile:` line. An App with
  write access to issues can edit a body the owner's login wrote, and the
  author field does not change.

### The assets

Likelihood and impact are each low, medium or high, for the adversary
above. "Today" is 2026-11-14.

| # | Asset | Limit today | Limit planned | Rating | Accepted risk |
|---|---|---|---|---|---|
| 1 | A project's `main`, and through it the skills, hooks, agents and plugins every session loads after a pull | The ruleset on `main`: a PR is required, no force push, no deletion. It binds the owner too. | #191: the App cannot merge. | low × high | Who merges is a guard: any session on the owner's login can merge a PR. |
| 2 | Repository settings: rulesets, secrets, variables, workflow files, starting a workflow | None for a session on the owner's login | #191, for builders | low × high | The role sessions keep this reach. |
| 3 | Secret values: an environment file, the credential store, an App's key | GitHub never returns a stored secret's value. Local values: none. | #201 | low × high | Local secret values are in reach of any process of the owner's operating-system user. |
| 4 | Private data: tables that hold personal details, the private repository | The project's own, named in its rules file | #204, for the private repository | low × high | As the project's rules file records. |
| 5 | Data that is not rebuilt | The project's own, named in its rules file | #201, for local files | low × high | Local destructive commands meet guards only. |
| 6 | The owner's settings, permission and dispatch files, and the root configuration folder | None | #201 | low × high | These files define the guards, and guards protect them. |
| 7 | The owner's GitHub reach outside the project's repositories | None | #191, for builders. #204, for the role sessions. | low × high | Until #204 is decided. |
| 8 | The record: ticket text, tier lines, the owner's queue | GitHub records each text's author, and no session can change that field. | #191: a builder's text carries the App's name, and the script checks the last editor. | medium × medium | A role session can write record text. A pane `Answer:` line is a guard. A forged answer can release only a PR that already passed CI, the re-proof and the code review. |
| 9 | Other sessions' branches and worktrees | None beyond `main` | #193: no force push on any branch; deletion once builders are a different actor. #201, for local worktrees. | medium × medium | Until #193 lands. |

### What this model does not claim

- **A builder is not sandboxed.** It may edit files and run tests, and
  it runs as the owner's operating-system user. The owner's own
  credentials are in that user's credential store. A builder's own token
  changes what it uses by default; it does not put the owner's token out
  of reach. Against a mistaken builder that is enough. Against a misled
  builder it is a narrower default plus guards. The owner accepted this
  on 2026-11-14, rated low × high; #201 scopes real isolation.
- **GitHub's limits protect what is on GitHub.** A local file, a local
  worktree and a local database connection are protected by guards until
  #201 lands, or by the project's own limit.
- **The three classes of text are a rule, not a limit**, for any session
  on the owner's login.

### When the model is read again

1. **On a change** to a settings or profile template, the dispatch
   script, or the App's permissions. Each project's code-review ruleset
   carries a line for it, so the re-proof checks it.
2. **After every advisory.**
3. **Every three months**, raised by a scheduled workflow that opens an
   issue (#203). A session's memory does not last that long.

A review fills the asset table again: for each row, is the limit still
there, is the planned limit built, and does the owner still accept what
is left.

## Considered and rejected

- **Two classes of text, instruction and data.** A `Tier:` line an agent
  wrote through the owner's login would then count as much as the owner's
  own words.
- **A tested guard counts as a limit.** It still rests on the session's
  own host, and it contradicts ADR-0004.
- **No accepted risks.** The ADR could not merge until #191, #193 and
  #201 were built, and the gaps would stay unwritten meanwhile.
- **A fine-grained personal token for builders.** Simplest, and GitHub
  still sees the owner.
- **A second GitHub account for builders.** A different actor with no
  refresh problem, at the cost of another account to secure and a
  long-lived token.
- **A separate operating-system account, or cloud builders, now.** Each
  is a real limit. Each means rebuilding dispatch first, so each is
  scoped in #201 instead of holding #191.
- **One App per project, or the pipeline's App reused.** More keys to
  hold, or two jobs sharing one set of permissions.
- **One ADR per project.** The model would be copied, and the copies
  would drift.

## Consequences

- #191 is rewritten to this ADR and built after it merges: the App, the
  token rule, the ruleset that keeps the merge with the owner's login,
  and the script's author and last-editor check.
- `session-rules`, "Whose text counts on a ticket", gains a line for the
  App's login when #191 lands: its text is data.
- #192's later checks are specified against the asset table. A fault in
  a guard on a row with high impact fails the build; the rest warn.
- #193's second item (restricting deletion) waits for #191.
- Each project's rules file gains a short list of its own assets for
  rows 4 and 5, with the limit on each. The dynasty planner writes
  dynasty's.
- Each project's code-review ruleset gains the line in "When the model
  is read again", by that ADR's own route: the manager drafts it and a
  builder lands it.
