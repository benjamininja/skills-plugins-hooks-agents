"""Regression tests for hooks/git-guardrails/block-dangerous-git.sh.

Each case feeds the hook the JSON Claude Code sends to a PreToolUse hook and
checks the exit code: 2 = blocked, 0 = allowed. Every bypass found in real use
is pinned here (2026-10-12: `git -C <path> ...` and commands containing quotes
both slipped past the original literal-string match).
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "git-guardrails" / "block-dangerous-git.sh"

GIT_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}


def find_bash():
    """Git Bash on Windows (never System32's WSL launcher), plain bash elsewhere."""
    if sys.platform == "win32":
        git = shutil.which("git")
        if git:
            for parent in Path(git).resolve().parents:
                candidate = parent / "bin" / "bash.exe"
                if candidate.exists():
                    return str(candidate)
        pytest.skip("Git Bash not found")
    return shutil.which("bash") or pytest.skip("bash not found")


BASH = find_bash()


def run_hook(command, project_dir=None, tool="Bash"):
    payload = json.dumps({
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {"command": command, "description": "test"},
    })
    env = {**os.environ, **GIT_ENV}
    if project_dir is not None:
        env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    else:
        env.pop("CLAUDE_PROJECT_DIR", None)
    return subprocess.run(
        [BASH, str(HOOK)], input=payload.encode("utf-8"), capture_output=True,
        env=env, cwd=str(project_dir) if project_dir else None, timeout=30,
    )


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                   env={**os.environ, **GIT_ENV})


def make_repo(path, branch):
    path.mkdir(parents=True)
    git(path, "init", "-q")
    git(path, "checkout", "-q", "-b", branch)
    git(path, "commit", "-q", "--allow-empty", "-m", "init")
    return path


@pytest.fixture
def on_main(tmp_path):
    return make_repo(tmp_path / "on-main", "main")


@pytest.fixture
def on_feature(tmp_path):
    return make_repo(tmp_path / "on-feature", "my-feature")


# --- always blocked, whatever is checked out ---------------------------------

@pytest.mark.parametrize("command", [
    # explicit push to main/master
    "git push origin main",
    "git push origin master",
    "git push --dry-run origin main",
    "git push origin HEAD:main",
    "git push origin :main",
    "git push origin +main",
    "git push origin feature:main",
    "git push origin refs/heads/main",
    "git push -u origin main",
    # blanket-blocked destructive commands
    "git reset --hard",
    "git reset --hard HEAD~1",
    "git reset HEAD~1 --hard",
    "git clean -f",
    "git clean -fd",
    "git clean -fdn",
    "git clean -df",
    "git clean -xdf",
    "git clean --force",
    "git branch -D old-branch",
    "git checkout .",
    "git checkout -- .",
    "git restore .",
    "git restore --staged --worktree .",
    # global options between `git` and the subcommand (the 2026-10-12 bypass)
    "git -C /some/repo push origin main",
    'git -C "C:/Users/me/My Repo" push --dry-run origin main',
    "git -C 'C:/Users/me/My Repo' clean -fdn",
    "git -c user.name=x reset --hard",
    "git --git-dir=/r/.git --work-tree=/r clean -fd",
    "git --no-pager -C /r branch -D gone",
    "git -C /a -C b push origin main",
    # other spellings of the binary
    "git.exe push origin main",
    "/usr/bin/git push origin main",
    # dangerous command in a later segment
    "cd /some/repo && git push origin main",
    "git status; git reset --hard",
    "git fetch origin || git clean -fd",
    "echo ok | git push origin main",
    # a quoted argument earlier in the command must not hide what follows
    'git commit -m "wip" && git push origin main',
    'echo "done" ; git reset --hard',
])
def test_blocked(command, on_feature):
    result = run_hook(command, project_dir=on_feature)
    assert result.returncode == 2, result.stderr.decode()
    assert b"BLOCKED" in result.stderr


@pytest.mark.parametrize("command", [
    "git push origin main",
    "git -C C:/repo clean -fd",
    "git reset --hard; Write-Output done",
])
def test_blocked_from_the_powershell_tool(command, on_feature):
    result = run_hook(command, project_dir=on_feature, tool="PowerShell")
    assert result.returncode == 2, result.stderr.decode()


# --- always allowed -----------------------------------------------------------

@pytest.mark.parametrize("command", [
    "git status",
    "git push origin my-feature",
    "git push -u origin my-feature",
    "git push origin --delete my-feature",
    "git -C /some/repo push origin my-feature",
    "git push origin maintenance",          # contains "main" but is not main
    "git push origin fix/main-menu",
    "git clean -n",                          # dry run without force
    "git clean -dn",
    "git reset --soft HEAD~1",
    "git reset HEAD file.txt",
    "git branch -d merged-branch",          # safe delete: refuses if unmerged
    "git checkout main",
    "git checkout -b new-branch",
    "git restore file.txt",
    "git restore --staged .",               # unstage only
    "git log --oneline main",
    "git diff main...HEAD",
    "git merge --ff-only origin/main",
    "git fetch origin main",
    "gh pr merge 12 --merge",
    "ls -la",
    "echo git is great",
    "",
])
def test_allowed(command, on_feature):
    result = run_hook(command, project_dir=on_feature)
    assert result.returncode == 0, result.stderr.decode()


def test_branch_name_in_another_segment_does_not_block(on_feature):
    result = run_hook("git push origin my-feature && echo main", project_dir=on_feature)
    assert result.returncode == 0, result.stderr.decode()


# --- bare push falls back to the checked-out branch ---------------------------

@pytest.mark.parametrize("command", ["git push", "git push origin", "git push -u origin"])
def test_bare_push_blocked_on_main(command, on_main):
    result = run_hook(command, project_dir=on_main)
    assert result.returncode == 2, result.stderr.decode()
    assert b"current checked-out branch is 'main'" in result.stderr


@pytest.mark.parametrize("command", ["git push", "git push origin", "git push -u origin"])
def test_bare_push_allowed_on_feature(command, on_feature):
    assert run_hook(command, project_dir=on_feature).returncode == 0


def test_bare_push_uses_the_dash_C_repo_not_the_session_repo(on_main, on_feature):
    # session sits in a feature-branch repo, but the push targets a repo on main
    result = run_hook(f'git -C "{on_main.as_posix()}" push', project_dir=on_feature)
    assert result.returncode == 2, result.stderr.decode()
    # and the reverse: session on main, push targets a feature-branch repo
    result = run_hook(f'git -C "{on_feature.as_posix()}" push', project_dir=on_main)
    assert result.returncode == 0, result.stderr.decode()


# --- input handling -----------------------------------------------------------

def test_non_shell_tool_input_is_ignored():
    payload = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "x"}})
    result = subprocess.run([BASH, str(HOOK)], input=payload.encode(), capture_output=True, timeout=30)
    assert result.returncode == 0


def test_multiline_command_is_checked(on_feature):
    result = run_hook("git status\ngit reset --hard", project_dir=on_feature)
    assert result.returncode == 2, result.stderr.decode()


def test_pretty_printed_json_is_parsed(on_feature):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push origin main"}}, indent=2)
    result = subprocess.run([BASH, str(HOOK)], input=payload.encode(), capture_output=True,
                            cwd=str(on_feature), timeout=30)
    assert result.returncode == 2, result.stderr.decode()
