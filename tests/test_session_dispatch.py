"""The dry run of plugins/session-dispatch-managers-build-review/scripts/dispatch.ps1.

Only the dry run is tested: it reads, refuses or prints, and changes nothing.
A real start needs the Claude CLI and a login, so it is proven by hand
(docs/adr/0013). Windows only: the script is Windows PowerShell.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "session-dispatch-managers-build-review"
SCRIPT = PLUGIN / "scripts" / "dispatch.ps1"
POWERSHELL = shutil.which("powershell")

pytestmark = pytest.mark.skipif(
    sys.platform != "win32" or POWERSHELL is None or shutil.which("git") is None,
    reason="dispatch.ps1 is a Windows PowerShell script",
)

DENY = ["PowerShell", "Bash(gh pr merge*)", "Edit(.claude/settings.json)"]


@pytest.fixture
def project(tmp_path):
    """A git checkout with a config, a builders' settings file and a brief."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    claude = tmp_path / ".claude"
    claude.mkdir()
    (claude / "builders.settings.json").write_text(
        json.dumps({"permissions": {"allow": ["Read"], "deny": DENY}}), encoding="utf-8"
    )
    (claude / "dispatch.json").write_text(
        json.dumps(
            {
                "//agent": "a note, not a key",
                "agent": "stage-builder",
                "buildersSettings": ".claude/builders.settings.json",
                "setup": ["python -m venv .venv"],
                "readLine": "Read the project rules first.",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "brief.txt").write_text("Fix the thing. Done when the test passes.", encoding="utf-8")
    return tmp_path


def dispatch(project, *args, prompt="brief.txt"):
    return subprocess.run(
        [
            POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
            "-File", str(SCRIPT),
            "-Name", "fix-42", "-Project", str(project),
            "-PromptFile", str(project / prompt), *args,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_dry_run_prints_the_start_command_and_changes_nothing(project):
    before = sorted(p.name for p in (project / ".claude").iterdir())
    done = dispatch(project, "-Tier", "medium")

    assert done.returncode == 0, done.stderr
    out = done.stdout
    assert "DRY RUN" in out
    assert "would be refused" in out
    assert "git -C" in out and "worktree add .claude/worktrees/fix-42 -b worktree-fix-42" in out
    assert "[in the worktree] python -m venv .venv" in out
    assert "--model claude-sonnet-5-5 --effort high" in out
    assert "--permission-mode dontAsk" in out
    assert "--agent stage-builder" in out
    assert "builders.settings.json" in out
    assert "Read the project rules first." in out
    assert "Or stop after 80 turns." in out
    listed = out.split("--disallowedTools", 1)[1]
    for rule in DENY:
        assert rule in listed
    assert sorted(p.name for p in (project / ".claude").iterdir()) == before


def test_the_start_command_names_this_plugin(project):
    # A --bg session did not get the plugin from CLAUDE_CODE_PLUGIN_DIRS: its
    # transcript said "Unknown skill: session-rules".
    out = dispatch(project, "-Tier", "medium").stdout
    start = next(line for line in out.splitlines() if "--bg" in line)
    assert str(PLUGIN) in start.split("--plugin-dir", 1)[1].split("--agent", 1)[0]


def test_the_dry_run_prints_the_whole_of_step_8(project):
    out = dispatch(project, "-Tier", "medium").stdout
    lines = [line for line in out.splitlines() if "agents --json" in line]

    assert len(lines) == 3, out
    first, poll, again = lines
    assert out.index(first) < out.index("worktree add") < out.index("--bg") < out.index(poll)
    assert "nothing is started" in first
    assert "every 2 s, up to 30 s" in poll and "a pid, a status and the worktree as cwd" in poll
    assert "up to 10 s" in again and "the row is gone" in again
    stop = next(line for line in out.splitlines() if " stop " in line and "<short-id>" in line)
    assert out.index(poll) < out.index(stop) < out.index(again)


def test_a_turn_cap_and_no_setup_are_taken(project):
    out = dispatch(project, "-Tier", "low", "-TurnCap", "12", "-NoSetup").stdout

    assert "Or stop after 12 turns." in out
    assert "--model claude-sonnet-5-5 --effort medium" in out
    assert "(no setup: -NoSetup)" in out
    assert "python -m venv" not in out


FULL = "python -m venv .venv-full"


def with_setup_full(project, value):
    """Set the config's setupFull to value, or remove the key when value is None."""
    path = project / ".claude" / "dispatch.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config.pop("setupFull", None)
    if value is not None:
        config["setupFull"] = value
    path.write_text(json.dumps(config), encoding="utf-8")


def test_the_default_runs_the_setup_list(project):
    with_setup_full(project, [FULL])
    done = dispatch(project, "-Tier", "medium")

    assert done.returncode == 0, done.stderr
    assert "[in the worktree] python -m venv .venv" in done.stdout
    assert FULL not in done.stdout


def test_full_setup_runs_the_setup_full_list(project):
    with_setup_full(project, [FULL])
    done = dispatch(project, "-Tier", "medium", "-FullSetup")

    assert done.returncode == 0, done.stderr
    assert f"[in the worktree] {FULL}" in done.stdout
    assert "[in the worktree] python -m venv .venv\n" not in done.stdout


@pytest.mark.parametrize("value", [[], None], ids=["empty", "no-key"])
def test_full_setup_without_a_setup_full_list_is_refused_and_makes_no_worktree(project, value):
    with_setup_full(project, value)
    for args in (("-FullSetup",), ("-FullSetup", "-Apply")):
        done = dispatch(project, "-Tier", "medium", *args)

        assert done.returncode == 2
        assert "dispatch refused: -FullSetup was passed" in done.stderr
        assert "setupFull" in done.stderr
        assert "DRY RUN" not in done.stdout
        assert not (project / ".claude" / "worktrees").exists()


def test_no_setup_wins_over_full_setup_and_runs_neither(project):
    with_setup_full(project, [FULL])
    done = dispatch(project, "-Tier", "medium", "-NoSetup", "-FullSetup")

    assert done.returncode == 0, done.stderr
    assert "setup:     none (-NoSetup)" in done.stdout
    assert "(no setup: -NoSetup)" in done.stdout
    assert "[in the worktree]" not in done.stdout


def test_the_dry_run_names_the_list_it_would_run(project):
    with_setup_full(project, [FULL, "python -m pip --version"])

    default = dispatch(project, "-Tier", "medium").stdout
    full = dispatch(project, "-Tier", "medium", "-FullSetup").stdout

    assert "setup:     setup (1 line)" in default
    assert "setup:     setupFull (2 lines, by -FullSetup)" in full
    assert "[in the worktree] python -m pip --version" in full


def with_setup(project, value):
    """Set the config's setup list to value."""
    path = project / ".claude" / "dispatch.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config["setup"] = value
    path.write_text(json.dumps(config), encoding="utf-8")


def test_a_setup_full_of_one_blank_space_line_is_refused_and_makes_no_worktree(project):
    with_setup_full(project, ["   "])
    for args in (("-FullSetup",), ("-FullSetup", "-Apply")):
        done = dispatch(project, "-Tier", "medium", *args)

        assert done.returncode == 2
        assert "dispatch refused: -FullSetup was passed" in done.stderr
        assert "DRY RUN" not in done.stdout
        assert not (project / ".claude" / "worktrees").exists()


def test_a_setup_with_an_empty_line_and_a_real_line_runs_the_real_line_only(project):
    with_setup(project, ["", "python -m venv .venv"])
    done = dispatch(project, "-Tier", "medium")

    assert done.returncode == 0, done.stderr
    assert "setup:     setup (1 line)" in done.stdout
    listed = [line for line in done.stdout.splitlines() if "[in the worktree]" in line]
    assert listed == ["  [in the worktree] python -m venv .venv"]


def test_the_dry_run_prints_no_empty_line_for_either_list(project):
    with_setup(project, ["  ", "python -m venv .venv", "\t"])
    with_setup_full(project, ["", FULL, " "])

    for args in ((), ("-FullSetup",)):
        done = dispatch(project, "-Tier", "medium", *args)

        assert done.returncode == 0, done.stderr
        listed = [line for line in done.stdout.splitlines() if "[in the worktree]" in line]
        assert len(listed) == 1, done.stdout
        assert all(line.split("[in the worktree]", 1)[1].strip() for line in listed)


@pytest.mark.parametrize("cap", ["0", "-3", "81"])
def test_a_turn_cap_that_is_not_a_lowering_is_refused(project, cap):
    done = dispatch(project, "-Tier", "medium", "-TurnCap", cap)

    assert done.returncode == 2
    assert "dispatch refused: -TurnCap" in done.stderr
    assert "DRY RUN" not in done.stdout


def test_a_turn_cap_equal_to_the_tiers_cap_is_taken(project):
    out = dispatch(project, "-Tier", "medium", "-TurnCap", "80").stdout

    assert "Or stop after 80 turns." in out


def test_the_cap_a_config_override_sets_is_the_bound(project):
    path = project / ".claude" / "dispatch.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config["tiers"] = {"low": {"turnCap": 10}}
    path.write_text(json.dumps(config), encoding="utf-8")

    assert dispatch(project, "-Tier", "low", "-TurnCap", "11").returncode == 2
    assert "Or stop after 10 turns." in dispatch(project, "-Tier", "low", "-TurnCap", "10").stdout


def test_the_dry_run_without_origin_prints_the_base_and_does_not_fail(project):
    done = dispatch(project, "-Tier", "medium")

    assert done.returncode == 0, done.stderr
    out = done.stdout
    assert "base:      origin/main (not found yet; -Apply fetches first" in out
    assert "git -C" in out and "fetch --quiet origin" in out
    add = next(line for line in out.splitlines() if "worktree add" in line)
    assert add.endswith("-b worktree-fix-42 --no-track refs/remotes/origin/main")
    assert out.index("fetch --quiet origin") < out.index("worktree add")


def _origin_main(project):
    """Give the project an origin/main ref at one commit, with no remote."""
    subprocess.run(
        ["git", "-C", str(project), "-c", "user.name=t", "-c", "user.email=t@example.com",
         "commit", "-q", "--allow-empty", "-m", "base"],
        check=True,
    )
    sha = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "-C", str(project), "update-ref", "refs/remotes/origin/main", sha], check=True)
    subprocess.run(["git", "-C", str(project), "update-ref", "refs/remotes/origin/stack", sha], check=True)
    return sha


def test_the_dry_run_names_the_base_commit_and_does_not_fetch(project):
    sha = _origin_main(project)
    before = sorted(p.name for p in (project / ".git" / "refs" / "remotes" / "origin").iterdir())

    out = dispatch(project, "-Tier", "medium").stdout

    assert f"base:      origin/main at {sha} (as of the last fetch; -Apply fetches first)" in out
    assert sorted(p.name for p in (project / ".git" / "refs" / "remotes" / "origin").iterdir()) == before


def test_a_base_is_taken_and_printed(project):
    sha = _origin_main(project)

    out = dispatch(project, "-Tier", "medium", "-Base", "origin/stack").stdout

    assert f"base:      origin/stack at {sha}" in out
    assert "--no-track refs/remotes/origin/stack" in out


def test_a_local_tag_or_branch_named_like_the_base_does_not_hide_the_remote_ref(project):
    sha = _origin_main(project)
    git = ["git", "-C", str(project), "-c", "user.name=t", "-c", "user.email=t@example.com"]
    subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "later"], check=True)
    later = subprocess.run(
        [*git, "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    assert later != sha
    subprocess.run([*git, "tag", "origin/main", later], check=True)
    subprocess.run([*git, "branch", "origin/stack", later], check=True)

    out = dispatch(project, "-Tier", "medium").stdout
    stacked = dispatch(project, "-Tier", "medium", "-Base", "origin/stack").stdout

    assert f"base:      origin/main at {sha} " in out
    assert f"base:      origin/stack at {sha} " in stacked
    assert later not in out + stacked


def test_a_worktree_already_there_is_not_fetched_for(project):
    (project / ".claude" / "worktrees" / "fix-42").mkdir(parents=True)

    out = dispatch(project, "-Tier", "medium").stdout

    assert "(already there)" in out
    assert "the worktree is already there; it is left as it is" in out
    assert "fetch --quiet origin" not in out
    assert "worktree add" not in out


def test_apply_runs_the_one_worktree_command_the_dry_run_prints():
    # -Apply cannot run in a test: it needs the owner's list in the user
    # profile and the claude CLI. So the executed command is the printed
    # array, and no second spelling of it may stand in the script.
    text = SCRIPT.read_text(encoding="utf-8")

    assert text.count("'worktree', 'add'") == 1
    assert "worktree add" not in text
    assert "$addArgs = $addWorktree[1..($addWorktree.Count - 1)]" in text
    assert "& git @addArgs" in text
    assert "--no-track" in text and "$baseRef" in text


@pytest.mark.parametrize(
    "base",
    ["main", "origin/", "origin/-x", "-origin/main", "origin/a..b", "origin/x.lock", "upstream/main", "origin/a b"],
)
def test_a_base_that_is_not_an_origin_branch_is_refused(project, base):
    done = dispatch(project, "-Tier", "medium", "-Base", base)

    assert done.returncode == 2
    assert "dispatch refused: -Base must be origin/<branch>" in done.stderr
    assert "DRY RUN" not in done.stdout


def test_the_config_may_override_a_tier(project):
    path = project / ".claude" / "dispatch.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config["tiers"] = {"high": {"effort": "high"}}
    path.write_text(json.dumps(config), encoding="utf-8")

    out = dispatch(project, "-Tier", "high").stdout

    assert "--model claude-opus-5-5 --effort high" in out
    assert "Or stop after 200 turns." in out


def test_no_tier_is_refused(project):
    done = dispatch(project)

    assert done.returncode == 2
    assert "no tier, no dispatch" in done.stderr


def test_an_unknown_tier_is_refused(project):
    done = dispatch(project, "-Tier", "max")

    assert done.returncode == 2
    assert "haiku, low, medium or high" in done.stderr


def test_a_haiku_tier_takes_the_haiku_settings(project):
    out = dispatch(project, "-Tier", "haiku").stdout

    assert "tier:      haiku (claude-haiku-5-5, effort medium, turn cap 15)" in out
    assert "--model claude-haiku-5-5 --effort medium" in out
    assert "Or stop after 15 turns." in out


def test_no_config_is_refused(project):
    (project / ".claude" / "dispatch.json").unlink()
    done = dispatch(project, "-Tier", "low")

    assert done.returncode == 2
    assert "no config file" in done.stderr


def test_a_double_quote_in_the_prompt_is_refused(project):
    (project / "quoted.txt").write_text('Say "hello".', encoding="utf-8")
    done = dispatch(project, "-Tier", "low", prompt="quoted.txt")

    assert done.returncode == 2
    assert "double quote" in done.stderr


def test_a_settings_file_without_deny_rules_is_refused(project):
    (project / ".claude" / "builders.settings.json").write_text(
        json.dumps({"permissions": {"allow": ["Read"], "deny": []}}), encoding="utf-8"
    )
    done = dispatch(project, "-Tier", "low")

    assert done.returncode == 2
    assert "no deny rule" in done.stderr


def test_a_value_that_could_pass_for_a_flag_is_refused(project):
    settings = project / ".claude" / "builders.settings.json"
    settings.write_text(
        json.dumps({"permissions": {"deny": ["PowerShell", "--dangerously-skip-permissions"]}}),
        encoding="utf-8",
    )
    done = dispatch(project, "-Tier", "low")

    assert done.returncode == 2
    assert "starts with a hyphen" in done.stderr

    settings.write_text(json.dumps({"permissions": {"deny": DENY}}), encoding="utf-8")
    path = project / ".claude" / "dispatch.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config["readLine"] = ""
    path.write_text(json.dumps(config), encoding="utf-8")
    (project / "flag.txt").write_text("--permission-mode bypassPermissions", encoding="utf-8")
    done = dispatch(project, "-Tier", "low", prompt="flag.txt")

    assert done.returncode == 2
    assert "the prompt starts with a hyphen" in done.stderr


def test_apply_is_refused_in_a_project_the_owner_has_not_listed(project):
    done = dispatch(project, "-Tier", "low", "-NoSetup", "-Apply")

    assert done.returncode == 2
    assert "not on the owner's list" in done.stderr
    assert not (project / ".claude" / "worktrees").exists()


def test_no_mode_can_be_passed_in(project):
    done = dispatch(project, "-Tier", "low", "-PermissionMode", "bypassPermissions")

    assert done.returncode != 0
    assert "bypassPermissions" not in done.stdout


def test_the_template_config_is_read_by_the_script(project):
    shutil.copy(PLUGIN / "templates" / "dispatch.json", project / ".claude" / "dispatch.json")
    done = dispatch(project, "-Tier", "low")

    assert done.returncode == 0, done.stderr
    assert "--agent stage-builder" in done.stdout
    assert "setup:     setup (0 lines)" in done.stdout


def test_the_template_config_shows_both_setup_lists():
    config = json.loads((PLUGIN / "templates" / "dispatch.json").read_text(encoding="utf-8"))

    assert config["setup"] == [] and config["setupFull"] == []
    assert "light" in config["//setup"]
    assert "-FullSetup" in config["//setupFull"]


RESEARCH = {
    "allow": ["WebSearch", "Edit(builder-state/**)", "Bash(gh issue view *)"],
    "deny": ["Bash(gh pr *)"],
}


def with_profiles(project, profiles, key=".claude/builder-profiles.json"):
    path = project / ".claude" / "dispatch.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config["buildersProfiles"] = key
    path.write_text(json.dumps(config), encoding="utf-8")
    (project / ".claude" / "builder-profiles.json").write_text(
        json.dumps({"profiles": profiles}), encoding="utf-8"
    )


def start_line(out):
    # The prompt spans lines, so the start command runs from --bg to the poll line.
    begin = out.index("--bg")
    return out[begin:out.index("\n  [every", begin)]


def test_a_profile_adds_its_allows_and_denies_to_the_start_command(project):
    with_profiles(project, {"//research": "a note", "research": RESEARCH})
    done = dispatch(project, "-Tier", "medium", "-Profile", "research")

    assert done.returncode == 0, done.stderr
    start = start_line(done.stdout)
    assert "--settings" in start and "builders.settings.json" in start
    prompt_end = start.index("Or stop after 80 turns.")
    allowed = start.split("--allowedTools", 1)[1].split("--disallowedTools", 1)[0]
    assert start.index("--allowedTools") > prompt_end
    for rule in RESEARCH["allow"]:
        assert rule in allowed
    denied = start.split("--disallowedTools", 1)[1]
    for rule in DENY + RESEARCH["deny"]:
        assert rule in denied


def test_the_header_prints_the_profile_and_its_rules(project):
    with_profiles(project, {"research": RESEARCH})
    out = dispatch(project, "-Tier", "medium", "-Profile", "research").stdout

    assert "profile:   research (3 allow, 1 deny; the shared deny rules still apply)" in out
    for rule in RESEARCH["allow"]:
        assert f"  allow:   {rule}" in out
    assert "  deny:    Bash(gh pr *)" in out


def test_no_profile_leaves_the_start_command_as_it_was(project):
    with_profiles(project, {"research": RESEARCH})
    out = dispatch(project, "-Tier", "medium").stdout

    assert "profile:   none" in out
    start = start_line(out)
    assert "--allowedTools" not in start
    assert "Bash(gh pr *)" not in start


def test_no_profile_removes_a_shared_deny(project):
    # A profile that allows a shared deny rule exactly still gets the shared
    # deny passed; deny wins over allow in Claude Code.
    with_profiles(project, {"wide": {"allow": ["PowerShell", "Bash(gh pr merge*)"]}})
    start = start_line(dispatch(project, "-Tier", "low", "-Profile", "wide").stdout)

    denied = start.split("--disallowedTools", 1)[1]
    for rule in DENY:
        assert rule in denied


def test_an_unknown_profile_is_refused_and_the_known_ones_named(project):
    with_profiles(project, {"//research": "a note", "research": RESEARCH})
    done = dispatch(project, "-Tier", "low", "-Profile", "admin")

    assert done.returncode == 2
    assert "unknown profile: admin" in done.stderr
    assert "has: research" in done.stderr
    assert "//research" not in done.stderr


def test_a_note_key_is_not_a_profile(project):
    with_profiles(project, {"//research": {"allow": ["Read"]}})
    done = dispatch(project, "-Tier", "low", "-Profile", "research")

    assert done.returncode == 2
    assert "unknown profile" in done.stderr


def test_a_profile_without_a_profiles_file_in_the_config_is_refused(project):
    done = dispatch(project, "-Tier", "low", "-Profile", "research")

    assert done.returncode == 2
    assert "names no buildersProfiles file" in done.stderr


def test_a_missing_profiles_file_is_refused(project):
    with_profiles(project, {"research": RESEARCH}, key=".claude/elsewhere.json")
    done = dispatch(project, "-Tier", "low", "-Profile", "research")

    assert done.returncode == 2
    assert "no profiles file" in done.stderr


def test_a_profiles_file_that_is_not_json_is_refused(project):
    with_profiles(project, {})
    (project / ".claude" / "builder-profiles.json").write_text("{ not json", encoding="utf-8")
    done = dispatch(project, "-Tier", "low", "-Profile", "research")

    assert done.returncode == 2
    assert "not valid JSON" in done.stderr


def test_a_profile_with_no_rule_is_refused(project):
    with_profiles(project, {"empty": {"allow": [], "deny": []}})
    done = dispatch(project, "-Tier", "low", "-Profile", "empty")

    assert done.returncode == 2
    assert "has no rule" in done.stderr


def test_a_bad_profile_name_is_refused(project):
    with_profiles(project, {"research": RESEARCH})
    done = dispatch(project, "-Tier", "low", "-Profile", "Research")

    assert done.returncode == 2
    assert "profile name must be" in done.stderr


@pytest.mark.parametrize(
    "profile, why",
    [
        ({"allow": ["--dangerously-skip-permissions"]}, "an allow rule starts with a hyphen"),
        ({"deny": ["-x"]}, "a deny rule starts with a hyphen"),
        ({"allow": ['Bash(echo "hi")']}, "holds a double quote"),
        ({"allow": [["Read", "--permission-mode", "bypassPermissions"]]}, "is not a string"),
        ({"allow": ["Bash(ls C:\\some dir\\"]}, "ends in a backslash"),
    ],
)
def test_a_profile_rule_that_could_break_the_command_is_refused(project, profile, why):
    with_profiles(project, {"bad": profile})
    done = dispatch(project, "-Tier", "low", "-Profile", "bad")

    assert done.returncode == 2
    assert why in done.stderr


def write_base(project, deny, name="research.settings.json"):
    (project / ".claude" / name).write_text(
        json.dumps({"permissions": {"allow": ["Read"], "deny": deny}}), encoding="utf-8"
    )


def test_a_base_file_takes_the_shared_files_place_and_the_shared_denies_still_pass(project):
    write_base(project, DENY + ["Bash(curl*)"])
    with_profiles(project, {"research": {**RESEARCH, "baseSettings": ".claude/research.settings.json"}})
    done = dispatch(project, "-Tier", "medium", "-Profile", "research")

    assert done.returncode == 0, done.stderr
    start = start_line(done.stdout)
    settings = start.split("--settings", 1)[1].split("--plugin-dir", 1)[0]
    assert "research.settings.json" in settings
    assert "builders.settings.json" not in settings
    denied = start.split("--disallowedTools", 1)[1]
    for rule in DENY:
        assert rule in denied
    header = next(line for line in done.stdout.splitlines() if line.startswith("settings:"))
    assert "research.settings.json" in header
    assert "the profile's base file, in place of" in header and "builders.settings.json" in header


def test_a_base_file_alone_is_a_profile(project):
    write_base(project, DENY)
    with_profiles(project, {"narrow": {"baseSettings": ".claude/research.settings.json"}})
    done = dispatch(project, "-Tier", "low", "-Profile", "narrow")

    assert done.returncode == 0, done.stderr
    assert "--allowedTools" not in start_line(done.stdout)


def test_a_base_file_that_lacks_a_shared_deny_is_refused(project):
    write_base(project, DENY[:-1])
    with_profiles(project, {"research": {**RESEARCH, "baseSettings": ".claude/research.settings.json"}})
    done = dispatch(project, "-Tier", "low", "-Profile", "research")

    assert done.returncode == 2
    assert "lacks 1 shared deny rules, first: Edit(.claude/settings.json)" in done.stderr


def test_a_missing_base_file_is_refused(project):
    with_profiles(project, {"research": {**RESEARCH, "baseSettings": ".claude/nowhere.json"}})
    done = dispatch(project, "-Tier", "low", "-Profile", "research")

    assert done.returncode == 2
    assert "no base settings file for the profile research" in done.stderr


def test_a_base_file_that_is_not_json_is_refused(project):
    (project / ".claude" / "research.settings.json").write_text("{ not json", encoding="utf-8")
    with_profiles(project, {"research": {**RESEARCH, "baseSettings": ".claude/research.settings.json"}})
    done = dispatch(project, "-Tier", "low", "-Profile", "research")

    assert done.returncode == 2
    assert "base settings file of the profile research is not valid JSON" in done.stderr


def test_the_template_profiles_and_base_files_are_read_by_the_script(project):
    with_profiles(project, {})
    templates = PLUGIN / "templates"
    shutil.copy(templates / "builder-profiles.example.json", project / ".claude" / "builder-profiles.json")
    shutil.copy(templates / "research.settings.example.json", project / ".claude" / "research.settings.json")
    shutil.copy(templates / "builders.settings.example.json", project / ".claude" / "builders.settings.json")
    done = dispatch(project, "-Tier", "medium", "-Profile", "research")

    assert done.returncode == 0, done.stderr
    assert "  allow:   Edit(builder-state/**)" in done.stdout
    assert "  allow:   Write" not in done.stdout
    base = json.loads((templates / "research.settings.example.json").read_text(encoding="utf-8"))
    assert not {"Edit", "Write"} & set(base["permissions"]["allow"])


PROBE_RULE = "Bash(.venv/Scripts/python.exe builder-state/probe.py)"


def test_the_template_probe_profile_holds_one_fixed_path_rule(project):
    with_profiles(project, {})
    templates = PLUGIN / "templates"
    shutil.copy(templates / "builder-profiles.example.json", project / ".claude" / "builder-profiles.json")
    profiles = json.loads((templates / "builder-profiles.example.json").read_text(encoding="utf-8"))["profiles"]

    assert profiles["probe"] == {"allow": [PROBE_RULE]}
    others = [rule for name, p in profiles.items() if name != "probe" and isinstance(p, dict)
              for rule in p.get("allow", [])]
    assert not [rule for rule in others if "probe" in rule or rule.startswith("Bash(python")]
    done = dispatch(project, "-Tier", "medium", "-Profile", "probe")

    assert done.returncode == 0, done.stderr
    assert "profile:   probe (1 allow, 0 deny" in done.stdout
    allowed = start_line(done.stdout).split("--allowedTools", 1)[1].split("--disallowedTools", 1)[0]
    assert "builder-state/probe.py" in allowed
