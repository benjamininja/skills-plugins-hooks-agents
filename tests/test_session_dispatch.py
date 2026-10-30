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
    assert "low, medium or high" in done.stderr


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
