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


def test_a_turn_cap_and_no_setup_are_taken(project):
    out = dispatch(project, "-Tier", "low", "-TurnCap", "12", "-NoSetup").stdout

    assert "Or stop after 12 turns." in out
    assert "--model claude-sonnet-5-5 --effort medium" in out
    assert "(no setup: -NoSetup)" in out
    assert "python -m venv" not in out


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
    # The prompt spans lines, so the start command runs from --bg to the check.
    return out[out.index("--bg"):out.index("agents --json")]


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
