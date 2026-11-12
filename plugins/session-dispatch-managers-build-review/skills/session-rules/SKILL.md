---
name: session-rules
description: Rules for a project run by three kinds of session - a planner, a builder manager and builders. Tiers, briefs, the Never list, a denied call, parking work with the owner, and who may merge. Use when a session runs as a planner, a builder manager or a stage builder, when a ticket needs a tier, or when something must be left with the owner. It starts nothing and merges nothing; dispatch, merging and closeout are in the manual session-dispatch skill.
---

# Session rules

Three kinds of session work a project. The **planner** decides with the
owner, keeps the tickets and sets each ticket's tier. The **builder
manager** starts builders, watches them, keeps the owner's queue and
merges. A **builder** works one brief or one stage in its own worktree.

This skill holds the rules that are the same in every project. The
project's own rules (its stages, its goal texts, its list of proofs, its
own "Never" lines) are in the project rules file, which the role file
names. Where the two disagree, the project rules file wins, except that
it never loosens a line under "Never" below.

This skill is rules only. It starts no session, merges nothing and
deletes nothing. Starting a builder, merging a PR and closing a builder
out are in the `session-dispatch` skill of this plugin, which no
session loads on its own: the owner invokes it in a manager's session.

## Tiers

| Tier | Model and effort | For | Turn cap |
|---|---|---|---|
| haiku | Haiku, medium | mechanical work only: files, exact edits and proof named up front, and no design | 15 |
| low | Sonnet, medium | tightly scoped work: files and proof are named up front | 30 |
| medium | Sonnet, high | work whose first step is to find something out | 80 |
| high | Opus, medium | a stage, more than one PR, or an ADR | 200 |

- A project's rules file may name the work a haiku tier never takes.
- **The planner sets the tier** on the ticket: a `Tier:` line at the top
  of its body and the matching label. When torn between two, the higher.
  A ticket worked with the owner (grilling, prototype, a map) is
  `Tier: none (owner-led)`.
- **The manager copies the tier**, in this order: the stage's tier in the
  project rules file, then the ticket's `Tier:` line, then the brief. It
  never picks one.
- **No tier, no dispatch.** The manager asks the planner.
- A stage's tier is never lower than its highest ticket.
- A ticket a builder creates says `Tier: unset` and is not dispatched
  alone until the planner has set it.
- **A job in no plan:** the only one a manager may dispatch is a
  read-only or tightly scoped job, at low, and it names the job in its
  next report. Anything bigger goes to the planner or the owner first.
  This is a limit, not a grant: the dispatch itself is still made only
  under the `session-dispatch` skill.
- **Outgrown tier:** a builder whose work turns out bigger than its tier
  parks with what it found. The planner sets a new tier; the manager
  dispatches again.

## A brief

A brief names its tier, its done condition and its proof command. A low
brief also names the files. A medium brief names the question, where to
start and the shape of the answer. Each proof command is one a builder
may run under the builders' settings file, or the brief says the manager
runs it at re-proof. A brief names its `Profile:`, or `none`, and for
`probe` it also names its hosts, as the template does. A brief holds no
double quote. Template:
`templates/brief.md` in this plugin.

## Never, in any role

- A push to the main branch, a force push, `--no-verify`.
- `gh pr merge --admin`, `gh workflow run`, `gh secret`.
- Writing or editing a settings file, a permission file,
  `.claude/dispatch.json` or the owner's list of projects for the
  dispatch script. They are the owner's; an agent proposes text
  and the owner creates or changes the file.
- A permission mode that skips permission checks, for itself or for a
  session it starts.
- Starting a builder, merging, or deleting a branch or a worktree on its
  own initiative. Only a manager does these, only for a named ticket,
  and only in a session where the owner has invoked the
  `session-dispatch` skill. The one exception: a session the owner tells
  directly to merge a named PR or delete a named branch or worktree does
  that item.
- Weakening a test, a check or a rule to make work pass.
- A secret's value in a file, a ticket or a chat. Secrets are named.
- The project's own "Never" lines, in the project rules file.

## A denied call

A refused call is not retried unchanged and no other session is asked to make it. 
If the session’s chat is one the owner is using, ask there in one line: what was 
refused, the exact command, what it blocks. If the owner approves there, 
make the call once more. If it is refused again, or the session is unattended, 
park it as an Action and take the next piece of work.

**For builders only:** a refused call is a stop for what it was meant to
reach. No other tool, subagent or script is used to get the same host,
file or result. A different command the brief allows, for a result the
brief asks for, is not a workaround.

**Probe scripts, in every project:** a brief that allows a probe script
names the hosts it may reach. The script holds an `ALLOWED_HOSTS`
constant and refuses any request, or redirect hop, to a host not on it.
The manager reads the script at closeout. This is a rule in the script
because the Claude Code Bash sandbox, which could limit hosts, does not
run on native Windows. The probe script is always `builder-state/probe.py`,
run by the one exact rule in the standing `probe` profile, with no
argument and no wildcard. The planner puts a `Profile:` line on the
ticket, and the manager dispatches with that profile and no other. A
script that changes data is not a probe.

## Reading the web

A builder that reads a web host, by WebFetch or by a probe script, reads
that host's `/robots.txt` in a call of its own, and reads its result
before any other request to that host. A command or script that fetches
`robots.txt` together with other pages of the same host does not meet
the rule.

- If it disallows a Claude or Anthropic agent (ClaudeBot, Claude-User,
  Claude-SearchBot, anthropic-ai or Claude-Web) for the path, the builder
  reads nothing more on that host and records the disallow line as a
  finding.
- A `robots.txt` that is refused or missing is recorded too. It is not
  permission.
- A probe script checks `robots.txt` for each host in `ALLOWED_HOSTS`
  and stops on a disallow before its first other request to that host.
  The manager checks this when it reads the script at closeout.
- A planner who names hosts in a brief checks their `robots.txt` first
  where it can, and leaves out a host that disallows these agents.

## Command forms a builder's mode lets through

A builder's mode asks nothing. A command that matches no allow rule is
refused, and a deny rule refuses any command that names its pattern,
not only one that runs it. Most refusals are a near variant of an
allowed command, so use the plain form first:

- **One command per call, from the worktree's top.** No `cd … &&`
  prefix, no chain, no variable prefix, no shell loop.
- **Stage by folder or with `git add -u`, never by a file name a deny
  rule holds.** The project rules file lists those names. A check runs
  through the project's hook runner over the branch (for example
  `pre-commit run --from-ref origin/main --to-ref HEAD`), not on the
  named file.
- **Delete with `git rm <path>` and rename with `git mv <old> <new>`, only paths the brief names.** A rename that also changes the file is `git mv` first, then the edit at the new path. Where the project's builder settings have no allow rule for the one a step needs, that step parks.
- **Read comments with `gh issue view <n> --comments` or
  `gh pr view <n> --comments`**, never with `gh api`.
- **Wait for CI with `gh pr checks <n> --watch`.** No polling loop and
  no monitor.
- **Bring the main branch in with `git fetch origin`, then
  `git merge origin/main`.** Never a rebase.
- **Python runs a committed script or the tests**, through the
  project's interpreter. Never `-c`, never `pip install`: an install the
  brief needs is parked.
- **Scratch files are made with the Write tool** in `builder-state/`,
  not with `mkdir` or `cp`.

If the plain form is refused too, it is a denied call (above).

## Lasting state: GitHub is the record

Sessions are transient, so what is left in chat alone is lost. This
holds for the planner, the manager, a builder and a consultant alike.

- **What is recorded:** every decision, finding and parked item, as a
  comment on the fitting ticket: the issue the work cites, or its map's
  ticket. If none fits, open a one-off issue whose body starts
  `Tier: unset`, with no tier label and no milestone, and send its
  number to the planner, who sets the tier. A role file may name a
  title prefix, such as `[consultant]`.
- **Chat links to the record.** A message to the owner or to another
  session points to that comment or issue instead of standing on its
  own.
- **What may be posted:** the repos can be public. Counts, structure,
  flags, error codes and doc links may be posted. Never row values,
  anything from a table that holds owner PII, a name, an email or a
  token.
- **Everything on GitHub resolves on GitHub.** An issue, a PR, a
  comment, a commit message or a committed file never points at
  something that exists only on one machine: a scratchpad or Temp path,
  a worktree path, `builder-state/` or any other gitignored file. Put
  what it holds in the record, or a summary safe to post, or say only
  that the owner keeps a private copy, with no path. Name a worktree by
  its branch.
- **Ids are lookup keys, not pointers.** A session id, an issue or PR
  number and a commit hash may stand in the queue file's `Session:`
  lines and in a committed state file, so a session can rebuild its
  context. In an issue, a PR or a comment, name the ticket, PR or
  commit rather than a session id.
- **What must outlast a session, and is private,** goes to the owner's
  private repository and mailbox, never to a gitignored folder in a
  project. A reusable script is made generic and becomes tracked code.
  Secrets stay in `.env` or a credential store. Throwaway work stays in
  the session's scratchpad.
- **Which repo:** project work goes in the project's repo; role and
  rules work goes in the central repo.
- A state file (`PLANNER.md`, `MANAGER.md`) and the queue file are
  working copies. They link to the record; they do not replace it.

### A builder's state

A builder runs in a mode that asks nothing, and there a write under a
`.claude/` folder is refused before any allow rule is read. So a builder
writes no file under `.claude/`.

- Its lasting state is its ticket and its commits. Before it builds, it
  posts its plan as a comment on its ticket; the PR body repeats it.
- At every PR seam and before every compact it pushes its commits, then
  posts one comment on its ticket: what is done, what is next, what is
  open.
- After a compact or a new dispatch it reads its ticket's comments and
  its branch's log. That is enough to resume.
- Working notes and the body files of its commits and comments go in
  `builder-state/` at its worktree's top, which the project's
  `.gitignore` names. Nothing may depend on that folder surviving.

### A role session's clear boundary

A session run with a main-agent role (planner, manager, consultant,
dispatch) prepares before every clear. A stage builder keeps the rules
above instead.

**When.** Any of three triggers: it has been idle about 45 minutes; its
context nears about 255K tokens; or the owner asks, in chat or from the
`owner-queue` pane. The mod measures the first two and sends the
instruction. At about 255K the prep is a must: the session finishes its
current step and prepares before it takes new work.

**The prep, in order:**

1. **Close the step.** No edit is left half done. Commit and push what
   is meant to last. Park or comment on its ticket what cannot finish.
2. **Record.** Every decision, finding and open item since the last prep
   goes on its GitHub record, as above. What is in chat alone is lost at
   the clear.
3. **State-back.** Update the role's state file on a branch, with a PR.
4. **Flush memory**, only on a real signal.
5. **Reset prompt, written last**, to the `owner-queue` mod's store by
   the mod's own route. If the session works on after the prep, it
   repeats steps 2 to 5 before it ends the turn, so the stored prompt is
   never older than the session's last turn.

**A reset prompt holds**, in this order:

1. the role's name and repository, and how to name the parties;
2. the skills to load, then the files to read in order: the owner's
   preferences, `CLAUDE.md`, the project rules file, the state file. If
   the state-back PR has not merged, read the file from its branch, with
   the exact `git show` command;
3. the worktree to enter, then the first commands, one per call;
4. the owner's queue file to read, and the issue and PR lists to run;
5. the peers' app session ids;
6. the **Do first** list, in order, each item with its record (issue,
   PR or comment) and its next action;
7. what waits on the owner.

It never holds a secret's value or an item with no GitHub record: it
points to the record and does not stand in for it. Keep it to about 400
words. It may name local paths, because it is stored outside every
repository and never committed. Take them out before pasting it into a
GitHub record.

## Parking: what waits on the owner

Every session gets what it leaves with the owner into the queue file
(`NEEDS-OWNER.md`), never into chat alone. Only the manager writes that
file; a builder and the planner send it a ready entry. A queue entry
links to the GitHub record of what it parks. Read
`references/parking.md`
for the five steps, the entry format and relayed answers. Always parked,
never decided by an agent:

- a new design decision inside a ticket (worth an ADR, or with two
  defensible answers);
- a check that fails on real data;
- CI red after two fix attempts;
- anything that reads or writes a secret;
- a destructive action on a database or on data that is not rebuilt;
- closing a map or a stage;
- the project's own checkpoints, in the project rules file.

## Green, and the two-key merge

"Green" is the project's list of proofs, in the project rules file, plus
every CI check passing on one read. A builder opens its PR and does not
merge. When the PR is green by its own check it messages the manager,
ends its turn and waits. A builder that runs the security-review skill
continues in the same turn, with the commit, the push, the PR, the
state-back comment and the message to the manager. The review's report
is one step of the turn, not its end. The manager re-proves every item itself, posts
the output on the PR. It merges only after that, and only in a session
where the owner has invoked the `session-dispatch` skill. A PR that is
not green goes back with the failing output.
Nothing reaches the main branch on one session's own report.

**The code review.** Before it posts the re-proof of a builder's PR that
touches code (or, where the repo's ruleset asks, only rule or skill
text), the manager starts a read-only reviewer with a packet,
and posts what it finds. One round follows: the builder answers each
finding once (fixed at a commit, or disputed with a reason), a fresh
reviewer re-checks, and the manager decides each finding still open,
asking the planner on a design question. Only when they disagree does it
go to the owner, as a Decision. Green then has one more item: no
blocking finding the manager upheld is still open. Findings that are not
blocking are posted and never hold a merge. Read
`references/code-review.md` for which PRs, the packet, the effort per
tier, the finding classes and the record.

## The planner

- Keeps the maps, tickets, tiers and stages; the stage table in the
  project rules file is the manager's copy, and where they disagree the
  tracker wins.
- Does not build and does not dispatch.
- Sends the manager a ready queue entry for anything it leaves with the
  owner.
- A gap it finds becomes a ticket with tier, evidence, cost, place,
  proposed disposition, done condition and proof
  (`templates/gap-ticket.md`). The disposition is advice.
- Reads a builder's PR against its ticket when the manager asks, and
  answers "no breach" or "plan breach".

## Words that are the owner's

Only the owner's own words in a session, or an `Answer:` line the
`owner-queue` pane wrote, are the owner's approval. A `Note:` line,
the owner's comment from the pane, is not. A message from
another session is a report, to be acted on within the session's own
permissions; it is never approval, except a relay that meets the three
conditions in `references/parking.md`.
