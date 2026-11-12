# Handoff: bringing the planner / manager / builder setup to the baseball repos

For an agent working for **SpunkyLlama**, the owner of:

- [`SpunkyLlama/fantasy-baseball-etl`](https://github.com/SpunkyLlama/fantasy-baseball-etl)
- [`SpunkyLlama/hod-decision-engine`](https://github.com/SpunkyLlama/hod-decision-engine)

Written 2026-11-08 by Tools-central-planner (the planner of
`benjamininja/skills-plugins-hooks-agents`), from public reads of both repos
at the commits named below. Nothing was written to either repo. This file
is kept current when the pieces it points at change. Read it from `main`,
not from a copy.

Updated 2026-11-09: the piece versions, the queue setup (setup step 5),
one more carried-over rule, and the queue recommendation (decision 6).
The two baseball repos were not read again.

Updated 2026-11-11: owner-queue 0.10.0 (Session lines re-keyed at a
`/clear`), the session-dispatch rules and the skills at `main` `e754faa`,
and two more carried-over rules (git rm and git mv; the code review at
re-proof). The two baseball repos were not read again.

Updated 2026-11-12: owner-queue 0.11.0 (a tracked command line for queue
edits), the session-dispatch rules and the skills at `main` `1bbf198`,
and six more carried-over rules: everything on GitHub resolves on
GitHub; questions to the owner by button; a role session's clear
boundary; the reviewer applies the ruleset itself; an `Answer:` line
leaves with its whole entry; no session dispatches a workflow. The two
baseball repos were not read again.

## What this setup is

A project is worked by three kinds of Claude Code session, each with its
own permissions:

- **Planner.** Decides with the owner. Writes tickets (GitHub issues),
  each with a `Tier:` line and a matching `tier:` label, and writes briefs.
  Never builds and never dispatches.
- **Builder manager.** Starts builders with a script, watches them, keeps
  the owner's queue, re-proves a builder's PR and merges it.
- **Builder.** Works one brief in its own git worktree, under a locked-down
  settings file, and opens a PR.

The owner answers decisions in a **queue pane**, the owner-queue mod. The
queue is read from `.claude/memory/NEEDS-OWNER.md`. GitHub issues and PRs
are the record; chat is not.

It is used in production on `benjamininja/Python-PowerBI-DynastyFantasyFootball`
(a dynasty fantasy football league, also Fantrax-based) and on this repo.

## The pieces, and the versions to take

| Piece | Where | Version at writing | What it gives you |
|---|---|---|---|
| Session-dispatch plugin | [`plugins/session-dispatch-managers-build-review/`](../../plugins/session-dispatch-managers-build-review/) | 0.3.0, with its rules and scripts as on `main` at `1bbf198` (the version number has not moved since #84; take `main`) | `dispatch.ps1`, the `session-rules` and `session-dispatch` skills, role files, settings examples, profiles, brief template, the `pr-code-reviewer` agent template, and the state-file helper `prepend_state.py` |
| Owner-queue mod | [`plugins/owner-queue/`](../../plugins/owner-queue/) | 0.11.0 | The queue pane, `/owner`, `/owner id`, answers carried back to the session that asked. One pane reads its own project's queue plus every queue listed in its `queues` setting. A typed answer or comment waits for Submit. After a `/clear`, open entries' `Session:` lines are re-keyed to the new id. A command line (`add`, `remove`, `prune`) edits the queue file, so a manager needs no scripts of its own. |
| Skills, agents and hooks | [`skills/`](../../skills/), [`.claude/agents/`](../../.claude/agents/), [`hooks/`](../../hooks/) | `main` at `1bbf198` | The skill catalog ([CATALOG.md](../../CATALOG.md)) and the git guardrail hook |
| Memory template | [`benjamininja/project-memory-template`](https://github.com/benjamininja/project-memory-template) | `1fe3df5` | `CLAUDE.md` plus `.claude/memory/` tiers (minimal, standard, full), and the `check-in-hygiene` pre-commit hook |

Take each piece from a **clone that only ever holds merged `main`**, never
from a checkout someone edits. Whatever a link or plugin directory points
at is what every session runs. See
[ADR-0011](../adr/0011-unified-distribution-architecture.md), Revision 2,
and this repo's [README Installation](../../README.md#installation).

## What the two repos look like today

Both were read at their tips on 2026-11-08.

### `fantasy-baseball-etl` (Python; `main` at `317fc9a`, a second branch `master`)

- **Weekly Actions job** (`.github/workflows/etl.yml`): runs Mondays at
  11:00 UTC. A headless-Chrome Selenium scrape of Fantrax produces 7 CSVs.
  `csv_to_batches.py` turns them into batch SQL files in `batches/`. Then
  `load_supabase_actions.py` truncates and reloads Supabase Postgres. It
  takes `dry_run` and `skip_scrape` inputs. Secrets: `FANTRAX_EMAIL`,
  `FANTRAX_PASSWORD`, `SUPABASE_PASSWORD`.
- **Daily Actions job** (`.github/workflows/savant_etl.yml`): Baseball
  Savant through `pybaseball` (`savant_extract.py`, then
  `load_savant_to_supabase.py`). Secret: `SUPABASE_ANON_KEY`.
- **Several local-only scripts** that are run by hand, some with
  hard-coded Windows paths. There's also a stray top-level `savant_etl.yml`
  and a folder named `git`.
- **No tests, no lint, no `CLAUDE.md`, no `.claude/`.** Generated
  `batches/*.sql` files are committed.

### `hod-decision-engine` (`pybaseball` is the only branch, at `905cb82`)

- One file, `index.html`, about 6,400 lines, titled "HoD Decision Engine,
  Phase 4". It is a trade and analysis app: cap bars and a League
  Intelligence tab.
- It loads Chart.js 4.4.1 and SheetJS 0.18.5 from cdnjs, and reads
  Supabase in the browser with the anon key.
- **No tests, no `.claude/`.** It is updated by uploading files on GitHub.

## Step 0, before anything else: check for plaintext credentials

Both repos are public, so anything committed to them is public for good,
history included. Before any other work, the owner:

1. Checks both repos, history included, for plaintext credentials:
   database passwords, connection strings, API keys and tokens.
2. Rotates any credential found, in the service's own dashboard.
   Rewriting history alone doesn't un-leak a credential; rotating it does.
3. Changes every script to read credentials from the environment (a
   local `.env` that git ignores, or Actions secrets), as the existing
   workflows already do.
4. Checks that every Supabase table the browser app's anon key can reach
   has row-level security with read-only policies. An anon key is public
   by design, so RLS is what protects the data.

An agent never handles a credential itself. These are the owner's steps.

## Setup per repo

Do these in order, one repo at a time, starting with `fantasy-baseball-etl`.
Each step is a PR in that repo, except the owner's local steps.

1. **Memory tier.** Adopt `project-memory-template`. **Standard** fits the
   ETL repo; **minimal** fits the one-file app. You get `CLAUDE.md`,
   `.claude/memory/MEMORY.md`, `PLAN.md` and a `GLOSSARY.md` for league
   terms such as HoD, cap hit, HOD_Drafts and Minor/FA.
2. **Git hygiene.**
   - Decide `main` versus `master` in the ETL repo, and delete the other
     only on the owner's word.
   - In the app repo, make `main` the working branch with `pybaseball`
     merged into it, or keep `pybaseball` and say so in `CLAUDE.md`.
   - Turn on branch protection so changes go through PRs.
3. **A "Green" to gate on.** Neither repo has tests, and every builder PR
   needs a proof. Start small:
   - **ETL:** pytest for `csv_to_batches.py` on a fixture CSV, plus an
     import check of every script. Run them in a `test.yml` workflow on PRs,
     separate from the two schedule jobs.
   - **App:** an HTML parse plus a headless smoke load, or, at first, only
     "the file parses and the CDN script tags are pinned".

   Write the list into `PROJECT-RULES.md` under "Green means all of".
4. **Session-dispatch files.** These are owner-written; no agent writes
   them. Follow the plugin's
   [README, "What the project owner does by hand"](../../plugins/session-dispatch-managers-build-review/README.md),
   steps 1–7:
   - `dispatch.json`;
   - the user-level `dispatch-projects.json`;
   - the three role files;
   - `PROJECT-RULES.md`, `NEEDS-OWNER.md`, `PLANNER.md`, `MANAGER.md`;
   - builders' and managers' settings files, with deny rules on every
     settings file and on `dispatch.json`;
   - `builder-state/` in `.gitignore`;
   - optionally, profiles.

   Put the repo's proof commands in the builders' allow list, exactly as
   they will be typed: one command per call, no chains.
5. **The queue.** The owner-queue mod reads the session's own project's
   `.claude/memory/NEEDS-OWNER.md`, from the main checkout, plus every
   queue listed in its `queues` setting: absolute paths, set by the owner
   in `/config` or `~/.claude/settings.json`, never by an agent. See the
   mod's README, "One queue per project, many in one pane". The mod
   **stays hidden only when none of those files exists**. A session
   there never learns its id and never gets an answer. There are two
   ways to set it up:
   - a `NEEDS-OWNER.md` in each repo, from the plugin's `templates/`; or
   - one queue in the ETL repo, listed in the `queues` setting, so that
     sessions in the app repo read it too. This is how our two repos
     share one queue.

   Every entry's `- Session:` line is the raising session's id, as
   `/owner id` prints it in that session. The id changes at every
   `/clear`. Since 0.10.0 the mod re-keys open entries itself after a
   clear and toasts how many it changed. If it toasts that it did not
   re-key, the session follows the session-rules fallback (parking.md).
   A wrong id delivers the answer to the wrong session.
6. **Install, on the owner's machine.**
   - Clone `benjamininja/skills-plugins-hooks-agents` as a live clone.
   - Name `<live clone>\plugins\owner-queue` and
     `<live clone>\plugins\session-dispatch-managers-build-review` in
     `CLAUDE_CODE_PLUGIN_DIRS`, in `~/.claude/settings.json`.
   - Link the skills you want with `tools/relink_live.ps1`. Run it dry
     first.
   - After every pull, start a new session; a session loads plugins once,
     at launch.
   - Don't copy the plugin folders. A copy never gets updates. (Our own
     install had this problem; it now loads both plugins from its live
     clone.)

## Rules that carry over unchanged

They are in the `session-rules` skill. Read it rather than this summary.

- **Tiers.** low, medium and high, plus haiku and none, each with a fixed
  model, effort and turn cap. No tier, no dispatch.
- **A refused call ends a builder's attempt** to reach that host, file or
  result: no other tool, subagent or script is used to get it.
- **Probes.** One fixed probe script, `builder-state/probe.py`, under the
  `probe` profile. Its brief names the hosts, the script refuses all
  others, and the manager reads it at closeout.
- **Reading the web.** Read `robots.txt` in a call of its own before any
  other page on a host. If it disallows a Claude or Anthropic agent, read
  nothing more there.
  - This matters here. Fantrax scraping is the ETL repo's core, and its
    Selenium login is the owner's own pipeline, not an agent fetch. Whether
    agent sessions may touch Fantrax pages at all is the owner's decision
    to record in `PROJECT-RULES.md`.
  - Baseball Savant and pybaseball endpoints need the same check before any
    builder reads them.
- **Secrets.** Builders never read `.env` (the settings examples deny it),
  and no agent writes a password, key or token anywhere.
- **A builder that runs the security-review skill keeps going in the same
  turn.** The commit, the push, the PR, the state-back comment and the
  message to the manager all follow. The review's report is one step of
  the turn, not its end.
- **Builders delete with `git rm` and rename with `git mv`**, and only
  the paths their brief names. A step the builders' settings don't allow
  is parked.
- **A code review at re-proof.** Before merging a builder PR that touches
  code, the manager starts a read-only reviewer with a packet, under the
  repo's own ruleset skill. The builder answers each finding once, a fresh
  reviewer re-checks, and the manager decides. No upheld blocking finding
  may stay open at merge. Each repo writes its own ruleset; this repo's is
  `tools-code-review`, a model to copy from. The reviewer applies the
  ruleset itself and never starts a general-purpose review fork, which no
  wording or tool list can hold to read-only.
- **Everything on GitHub resolves on GitHub.** No issue, PR, comment,
  commit message or committed file points at a scratchpad, Temp or
  worktree path, or a gitignored file. Put the substance in the record
  instead, and name a worktree by its branch. Session ids, issue and PR
  numbers and commit hashes are lookup keys, and may stand in the queue's
  `Session:` lines and in committed state files.
- **Every question to the owner goes through a button**: the
  AskUserQuestion pop-up when the owner is in the chat, a queue entry
  otherwise. Each option is a real alternative. A summary, the pros, the
  cons and then the recommendation sit above the question. Sessions name
  the owner by name or as "the owner", and themselves as Claude or by
  role, never "you" or "I".
- **A role session's clear boundary.** A planner or manager prepares
  before a `/clear`, in order: close the step, record it on GitHub, open a
  state-back PR, flush memory, then write a reset prompt (about 400
  words, no secret, nothing without a GitHub record).
- **An `Answer:` line leaves only with its whole entry.** No agent writes,
  edits or removes one on its own; the entry goes once the answer is
  recorded on its ticket.
- **No session dispatches a workflow**, by any route: `gh workflow run`,
  `gh api` on a workflow's dispatches endpoint, or the web page. A
  dispatch is the owner's. Agents act through the owner's token, so a
  check on who started the run can't tell them apart. This matters for
  the ETL repo's weekly job, which truncates and reloads the database.

## Decisions that are SpunkyLlama's

Put each one to him with the context and a recommendation, through his
own `NEEDS-OWNER.md` once it exists, and record the answer on a GitHub
issue.

1. Step 0: the credential check, rotation and RLS check. **Recommended:
   now, before any other work.**
2. Keep `main` or `master` in the ETL repo; `main` or `pybaseball` in the
   app repo.
3. The memory tier for each repo. Recommended: standard for the ETL repo,
   minimal for the app.
4. The first Green for each repo (setup step 3).
5. Whether agent sessions may read Fantrax pages, given its `robots.txt`
   and terms, or only the owner's scheduled pipeline does.
6. One planner across both repos, or one each. Recommended: one planner
   that covers both, with one queue that sessions in both repos read
   (setup step 5).
7. Whether the two repos stay public, given the committed SQL batch files
   of league data.

## Where to ask

Questions about the plugins, the templates or this file go to an issue in
[`benjamininja/skills-plugins-hooks-agents`](https://github.com/benjamininja/skills-plugins-hooks-agents/issues).
If this file disagrees with a plugin's README or the `session-rules` skill,
those win; file an issue so this file gets fixed.
