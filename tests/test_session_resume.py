"""plugins/session-dispatch-managers-build-review/scripts/resume_plain.ps1.

No real session is started: the config's "claude" key names a fake claude.cmd
that records its arguments. Windows only: the script is Windows PowerShell.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins" / "session-dispatch-managers-build-review" / "scripts" / "resume_plain.ps1"
POWERSHELL = shutil.which("powershell")

pytestmark = pytest.mark.skipif(
    sys.platform != "win32" or POWERSHELL is None or shutil.which("git") is None,
    reason="resume_plain.ps1 is a Windows PowerShell script",
)

SESSION = "0a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"


@pytest.fixture
def project(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".claude").mkdir()
    fake = tmp_path / "fake-claude.cmd"
    fake.write_text('@echo off\r\necho %* > "%~dp0args.txt"\r\nexit /b 0\r\n', encoding="ascii")
    (tmp_path / ".claude" / "dispatch.json").write_text(
        json.dumps({"claude": str(fake)}), encoding="utf-8"
    )
    (tmp_path / "msg.txt").write_text("Please add the test.\n", encoding="utf-8")
    return tmp_path


def resume(project, session=SESSION, message="msg.txt", worktree=None):
    return subprocess.run(
        [
            POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
            "-File", str(SCRIPT),
            "-Worktree", str(worktree or project),
            "-SessionId", session,
            "-MessageFile", str(project / message),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_an_accepted_call_passes_only_resume_bg_and_the_message(project):
    done = resume(project)

    assert done.returncode == 0, done.stderr
    assert "exit: 0" in done.stdout
    args = (project / "args.txt").read_text(encoding="utf-8", errors="replace").strip()
    assert args == f'"--resume" "{SESSION}" "--bg" "Please add the test."'


def test_a_message_that_starts_with_a_hyphen_is_refused(project):
    (project / "flag.txt").write_text("  --permission-mode bypassPermissions", encoding="utf-8")
    done = resume(project, message="flag.txt")

    assert done.returncode == 2
    assert "the message starts with a hyphen" in done.stderr
    assert not (project / "args.txt").exists()


def test_a_session_id_that_starts_with_a_hyphen_is_refused(project):
    done = resume(project, session="--dangerously-skip-permissions")

    assert done.returncode == 2
    assert "the session id starts with a hyphen" in done.stderr
    assert not (project / "args.txt").exists()


@pytest.mark.parametrize(
    "session",
    ["abc123", SESSION.upper(), SESSION[:-1], SESSION + "0", SESSION.replace("a", "g", 1)],
)
def test_a_session_id_of_the_wrong_shape_is_refused(project, session):
    done = resume(project, session=session)

    assert done.returncode == 2
    assert "is not a session id" in done.stderr
    assert not (project / "args.txt").exists()


def test_a_double_quote_in_the_message_is_refused(project):
    (project / "quoted.txt").write_text('Say "hello".', encoding="utf-8")
    done = resume(project, message="quoted.txt")

    assert done.returncode == 2
    assert "double quote" in done.stderr


def test_a_missing_worktree_is_refused(project):
    done = resume(project, worktree=project / "nowhere")

    assert done.returncode == 2
    assert "no worktree" in done.stderr


def test_there_is_no_claude_parameter(project):
    assert "[string]$Claude" not in SCRIPT.read_text(encoding="utf-8")
    done = subprocess.run(
        [
            POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
            "-File", str(SCRIPT), "-Worktree", str(project), "-SessionId", SESSION,
            "-MessageFile", str(project / "msg.txt"), "-Claude", str(project / "fake-claude.cmd"),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert done.returncode != 0
    assert not (project / "args.txt").exists()
