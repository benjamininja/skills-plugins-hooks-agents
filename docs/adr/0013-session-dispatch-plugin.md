# A plugin for dispatching builder sessions

- Status: accepted; amended 2026-11-07 (builder profiles)
- Date: 2026-10-12
- Scope: `plugins/session-dispatch-managers-build-review/`, `tests/test_session_dispatch.py`
- Amendments: builder profiles, 2026-11-07 (below)

## Context

One project (the Dynasty repository) is worked by three kinds of session:
a planner, a builder manager and builders. Starting a builder meant that
the manager typed one long `claude` command from six steps in a runbook:
the tier's model and effort, the settings file, the permission mode and a
deny list that was kept in step by hand in two places. The rules that
would fit any project sat in the same 400-line file as that project's
stages and goal texts, so every session read all of it and no other
project could use any of it.

## Decision

Ship a plugin with a script, two skills and templates.

- **A script for the fixed steps.** `scripts/dispatch.ps1` makes the
  worktree, runs the project's setup lines, starts the session and checks
  it. It is a dry run unless `-Apply` is given, as `tools/relink_live.ps1`
  is. It reads the deny list from the builders' settings file, so the
  list lives in one place.
- **The permission mode is fixed in the script** (`dontAsk`). No
  parameter and no config key sets it, so a session cannot dispatch a
  builder in a mode that skips permission checks.
- **One config file, the owner's.** `.claude/dispatch.json` in the main
  checkout holds the agent, the settings file, the setup lines and the
  read line. Its setup lines run as written, so it is treated like a
  settings file: an agent proposes text, the owner writes the file, and
  the example settings files deny edits to it. Without it the script
  refuses.
- **`-Apply` acts only in a project the owner has listed.** The config
  sits in the project, so a session that may run the script could make
  a folder of its own with its own config and settings file. The
  script therefore checks the main checkout against
  `<user profile>/.claude/dispatch-projects.json`, which the owner
  writes, and reads the profile folder from the system rather than from
  an environment variable. A dry run works anywhere.
- **No value can pass for a flag.** An agent name, model, effort,
  prompt or deny rule that starts with a hyphen is refused.
- **Two skills, split by blast radius (ADR-0006).** `session-rules` is
  rules only (tiers, briefs, the "Never" list, parking, who may merge)
  and any session may load it. `session-dispatch` tells a session to
  start sessions, merge and delete, so it is
  `disable-model-invocation: true`: the owner invokes it in a manager's
  session. The `skill-safety-auditor` judged a single combined skill as
  manual-only; the split keeps the rules loadable without loosening
  that.
- **Templates for a new project.** Role files, the config, the queue
  file, the project rules file, state files, example settings files, a
  brief and a gap ticket. They name no project.
- **These are the first skills that live inside a plugin** rather than in
  `skills/`. They are not vendored and not in `vendor-skills.json`;
  `CATALOG.md` does not list them, because its plugin table is for
  upstream manifests only (ADR-0002).

## Alternatives rejected

- **A skill alone, with the command as text.** That is the runbook
  again: the session still assembles the command, and the deny list is
  still copied by hand.
- **A script alone.** The rules of who may dispatch, park and merge
  would stay in each project's own runbook.
- **One skill.** It could not be both loadable by any session and safe
  under ADR-0006.
- **Trusting the config file alone.** Then the allow rule for the
  script is as wide as an allow rule for any PowerShell line.
- **No allow rule, the owner approves each `-Apply`.** Safe, but every
  dispatch waits on a click.
- **The permission mode as a config key.** A key can be set to a bypass
  mode by whoever can write the file.
- **The skills in `skills/`.** They are useless without the script and
  the templates, and would be linked into every session by ADR-0011's
  junction.

## Consequences

- A project that adopts the plugin keeps only its own rules in its own
  file; the generic rules have one copy.
- The owner has by-hand steps at adoption: the config file, the list
  of projects, the role files, the two settings files and the plugin folder in
  `CLAUDE_CODE_PLUGIN_DIRS`.
- Windows only for now. The tests are skipped on other systems.
- Follow-up and closeout are text in a reference file, not script
  steps.
- Not yet proven: a real start with `-Apply`, and whether
  `--disallowedTools` takes path-scoped rules. The builders' settings
  file enforces those rules either way.

## Amendment, 2026-11-07: builder profiles (tools #83)

### Context

Widening one builder's access meant the owner editing the shared
builders' settings file, which widened it for every builder running at
the time. The owner made seven such edits in one day and asked for a
path that needs none.

### Decision

- **Named profiles in an owner-written file.** `dispatch.json` may name
  a `buildersProfiles` file. `dispatch.ps1 -Profile <name>` passes the
  profile's `allow` rules with `--allowedTools` and its `deny` rules
  after the shared ones with `--disallowedTools`. An unknown profile is
  refused, and the dispatch header prints the profile and every rule.
  No agent writes the profiles file; the plugin ships a template only.
- **No profile removes a shared deny.** The shared deny list is always
  passed, and a deny wins over any allow.
- **A profile may name its own base settings file** (`baseSettings`),
  passed on `--settings` in place of the shared file. The script
  refuses one that is missing or lacks any shared deny rule, prints its
  path in the header, and still passes the shared denies by flag.
  Owner's choice, option A, relayed from the planner on #83.
- **Writes are scoped with `Edit(path)`**, never `Write(path)`, which
  matches nothing.

Evidence, on tools issue #83: the doc facts (issuecomment-6710787604);
the planner's amendment (issuecomment-6710795767); the manager's
throwaway-session test (issuecomment-6710894252), which showed that
`--allowedTools` adds to the `--settings` allow list under `dontAsk`,
that a settings-file deny beats an exact `--allowedTools` allow, and
that a relative `Edit(builder-state/**)` passed by flag anchors at the
working directory and covers the Write tool. The same test showed
that while the shared file allows bare `Edit` and `Write`, a profile
cannot narrow writes, which is why a base file exists.

### Alternatives rejected

- **The owner drops bare `Edit`/`Write` from the shared file**, and
  every building profile adds them back. Every dispatch would then need
  a profile, and the change moves the fence of every running builder.
- **Accept it**: the research profile adds tools only, and the brief
  keeps writes in `builder-state/`. No mechanical backstop.
- **A per-session settings file generated by the script.** The script
  would then write a settings file, which no agent and no agent-run
  script may do.

### Consequences

- One ticket's wider access is a profile name in its brief, not a
  settings edit. The owner still writes each profile, once.
- A base file must carry the whole shared deny list and be kept in
  step with it; the script refuses one that falls behind.
- Probes get one standing profile, `probe`, with one exact rule for a
  fixed path, `Bash(.venv/Scripts/python.exe builder-state/probe.py)`:
  no argument, no wildcard. The script keeps its own `ALLOWED_HOSTS`
  on every request and redirect hop; the brief names the hosts and the
  manager reads the script against them at closeout. A script that
  changes data is not a probe. (Planner's second amendment on #83,
  issuecomment-6711061289.)
