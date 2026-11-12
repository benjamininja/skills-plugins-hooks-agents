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


def run_hook(command, project_dir=None, tool="Bash", hook_cwd=None):
    body = {
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {"command": command, "description": "test"},
    }
    if hook_cwd is not None:
        # the real key order: session fields and the top-level cwd come before tool_input
        body = {"session_id": "s", "transcript_path": "t.jsonl", "cwd": str(hook_cwd), **body}
    return run_payload(json.dumps(body), project_dir)


def run_payload(payload, project_dir=None):
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


GH_SHIM = """#!/bin/bash
d="$(dirname "$0")"
head=""; state=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --head) head="$2"; shift ;;
    --state) state="$2"; shift ;;
  esac
  shift
done
if [[ -f "$d/mode" ]]; then
  case "$(cat "$d/mode")" in
    fail) echo "gh: boom" >&2; exit 1 ;;
    missing) echo "gh: command not found" >&2; exit 127 ;;
    hang) exec sleep 60 ;;
  esac
fi
if [[ -f "$d/pr.$head.$state" ]]; then cat "$d/pr.$head.$state"; else echo '[]'; fi
"""


@pytest.fixture(autouse=True)
def gh(tmp_path, monkeypatch):
    shim_dir = tmp_path / "gh-shim"
    shim_dir.mkdir()
    shim = shim_dir / "gh"
    shim.write_bytes(GH_SHIM.encode("utf-8"))
    shim.chmod(0o755)
    monkeypatch.setenv("PATH", f"{shim_dir}{os.pathsep}{os.environ['PATH']}")
    return shim_dir


def set_pr(shim_dir, branch, oid, state="merged"):
    (shim_dir / f"pr.{branch}.{state}").write_text(json.dumps([{"headRefOid": oid}]))


def tip(repo, branch):
    return subprocess.run(["git", "rev-parse", f"refs/heads/{branch}"], cwd=repo, check=True,
                          capture_output=True, text=True).stdout.strip()


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
    'git push origin "main"',
    "git push origin 'master'",
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
    # regressions caught in review of the first rewrite
    "git push origin main # git push",
    "git push origin main & git push origin feat",
    "git checkout ./",
    "git restore ./",
    "(git checkout .)",
    "git restore . # --staged",
    "git restore . & echo --staged",
    # a switch to main earlier in the same command, then a bare push
    "git checkout main && git push",
    "git switch main && git merge feat && git push",
    "git checkout main; git push origin",
    "git checkout main && git merge feat && git push origin HEAD",
    "git checkout main && git push -u origin HEAD",
    "git checkout main 2>&1 && git push",
    "git checkout main -q && git push",
    "(git checkout main && git merge feat && git push)",
    # a line continuation must not separate a push from its refspec
    "git push --force-with-lease \\\n  origin main",
    "git push --force-with-lease `\n  origin main",
    "git reset \\\n  --hard",
    # quotes, backticks and parentheses around the command
    "git submodule foreach 'git checkout .'",
    "bash -lc 'cd repo && git restore .'",
    "`git checkout .`",
    "(cd /some/repo && git push origin main)",
    "echo $(git push origin main)",
    "bash -c 'git push origin main'",
    # a redirection must not split a push from its refspec or shield a token
    "git push 2>&1 origin HEAD:main",
    "git push &>/dev/null origin main",
    "git push >| /dev/null origin main",
    "git push>/dev/null origin main",
    "git clean -fd>/dev/null",
    "git reset --hard>/dev/null",
    "git branch -D>/dev/null feature",
    "git checkout .>/dev/null",
    "git restore .>log",
    "git clean -f\\d",
    # other spellings of the whole-tree pathspec
    "git checkout ./.",
    "git checkout ././",
    "git checkout ./*",
    "git checkout ..",
    "git restore ./.",
    # extra whitespace
    "git  push   origin    main",
    "git\tpush origin main",
    # a comment never clears a block
    "git push origin my-feature # not main",
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
    "git checkout .gitignore",
    "git push origin my-feature 2>&1",
    "git push origin my-feature > push.log 2>&1",
    "git push 2>&1 origin my-feature",
    "git status > main",                     # a file named main, not a push
    "git checkout src\\.gitignore",
    "git push origin my-feature # ready for review",
    "git push -u origin HEAD",               # on a feature branch
    "(git fetch && git push)",               # on a feature branch
    "git checkout main && git pull && git checkout -b next && git push -u origin next",
    "git checkout main && git pull && git switch -c next && git push",
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

@pytest.mark.parametrize("command", [
    "git push", "git push origin", "git push -u origin",
    "git push origin HEAD", "git push -u origin @",
    "(git fetch && git push)", "bash -c 'git push'",
    "git push # to origin my-feature",
    "git push -u origin HEAD > push.log",    # the log file is not a refspec
])
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


@pytest.fixture
def worktree_on_feature(on_main):
    wt = on_main.parent / "wt-feature"
    git(on_main, "worktree", "add", "-q", "-b", "wt-branch", str(wt))
    return wt


@pytest.mark.parametrize("command", ["git push", "git push origin", "git push -u origin", "git push origin HEAD"])
def test_bare_push_from_a_worktree_on_a_feature_branch_passes(command, on_main, worktree_on_feature):
    # CLAUDE_PROJECT_DIR names the main checkout (on main); the hook input's
    # cwd names the worktree, whose branch is the one that gets pushed.
    result = run_hook(command, project_dir=on_main, hook_cwd=worktree_on_feature)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize("command", ["git push", "git push -u origin", "git push origin HEAD"])
def test_bare_push_from_a_worktree_on_main_blocks(command, on_main, tmp_path):
    other_main = make_repo(tmp_path / "wt-on-main", "main")
    result = run_hook(command, project_dir=on_main, hook_cwd=other_main)
    assert result.returncode == 2, result.stderr.decode()
    assert b"current checked-out branch is 'main'" in result.stderr
    # and the cwd, not the project dir, decides when the project dir is on a feature branch
    feature_project = make_repo(tmp_path / "project-on-feature", "my-feature")
    result = run_hook(command, project_dir=feature_project, hook_cwd=other_main)
    assert result.returncode == 2, result.stderr.decode()


def test_bare_push_in_the_main_checkout_still_blocks_with_its_cwd(on_main):
    result = run_hook("git push", project_dir=on_main, hook_cwd=on_main)
    assert result.returncode == 2, result.stderr.decode()
    assert b"current checked-out branch is 'main'" in result.stderr


def test_bare_push_without_a_cwd_field_reads_the_project_dir(on_main, on_feature):
    assert run_hook("git push", project_dir=on_main).returncode == 2
    assert run_hook("git push", project_dir=on_feature).returncode == 0


@pytest.mark.parametrize("hook_cwd", ["", "/no/such/folder"])
def test_bare_push_with_an_empty_or_unusable_cwd_falls_through_to_the_project_dir(hook_cwd, on_main, on_feature):
    assert run_hook("git push", project_dir=on_main, hook_cwd=hook_cwd).returncode == 2
    assert run_hook("git push", project_dir=on_feature, hook_cwd=hook_cwd).returncode == 0


def test_dash_C_path_still_wins_over_the_cwd(on_main, on_feature, worktree_on_feature):
    result = run_hook(f'git -C "{on_main.as_posix()}" push', project_dir=on_feature, hook_cwd=worktree_on_feature)
    assert result.returncode == 2, result.stderr.decode()


def test_explicit_main_target_still_blocks_from_a_feature_worktree(on_main, worktree_on_feature):
    result = run_hook("git push origin main", project_dir=on_main, hook_cwd=worktree_on_feature)
    assert result.returncode == 2, result.stderr.decode()


def test_switch_to_main_still_blocks_a_bare_push_from_a_feature_worktree(on_main, worktree_on_feature):
    result = run_hook("git checkout main && git push", project_dir=on_main, hook_cwd=worktree_on_feature)
    assert result.returncode == 2, result.stderr.decode()


MOVES_GIT_COMMANDS = [
    # a directory change anywhere in the command
    "cd {main} && git push",
    "git status && cd {main} && git push",
    "(cd {main} && git push)",
    "bash -c 'cd {main} && git push'",
    'bash -c "cd {main} && git push"',
    "git push; cd {main}",
    "pushd {main} && git push",
    "popd && git push",
    "chdir {main} && git push",
    "Set-Location {main}; git push",
    "set-location {main}; git push",
    "sl {main}; git push",
    "Push-Location {main}; git push",
    "Pop-Location; git push",
    "env -C {main} git push",
    "env --chdir {main} git push",
    "env --chdir={main} git push",
    "echo cd # not a real cd\ngit push",
    "c''d {main} && git push",
    'c"d" {main} && git push',
    # a git-dir or work-tree override
    "git --git-dir={main}/.git push",
    "git --git-dir {main}/.git push",
    "git --work-tree={main} push",
    "GIT_DIR={main}/.git git push",
    "GIT_WORK_TREE={main} git push",
    "export GIT_DIR={main}/.git; git push",
    "$env:GIT_DIR='{main}/.git'; git push",
    "git -c core.worktree={main} push",
]


@pytest.mark.parametrize("command", MOVES_GIT_COMMANDS)
def test_cwd_is_not_used_when_the_command_moves_git(command, on_main, worktree_on_feature):
    # cwd (the worktree, on a feature branch) would allow the push, but the
    # command may push from somewhere else: fall back to CLAUDE_PROJECT_DIR (main)
    result = run_hook(command.format(main=on_main.as_posix()), project_dir=on_main, hook_cwd=worktree_on_feature)
    assert result.returncode == 2, result.stderr.decode()
    assert b"current checked-out branch is 'main'" in result.stderr


@pytest.mark.parametrize("command", [
    "git fetch && git push",
    "git push -u origin HEAD",
    "git status; git log --oneline -1; git push",
    "echo abcd && git push",                # contains the letters cd, not the word
    "git push # from the worktree",
])
def test_cwd_is_used_when_nothing_moves_git(command, on_main, worktree_on_feature):
    result = run_hook(command, project_dir=on_main, hook_cwd=worktree_on_feature)
    assert result.returncode == 0, result.stderr.decode()


def test_a_cwd_with_spaces(on_main):
    wt = on_main.parent / "my work tree"
    git(on_main, "worktree", "add", "-q", "-b", "spaced", str(wt))
    assert run_hook("git push", project_dir=on_main, hook_cwd=wt).returncode == 0
    spaced_main = make_repo(on_main.parent / "main with spaces", "main")
    result = run_hook("git push", project_dir=on_main, hook_cwd=spaced_main)
    assert result.returncode == 2, result.stderr.decode()


@pytest.mark.skipif(sys.platform == "win32", reason="a backslash cannot be part of a Windows folder name")
def test_a_posix_cwd_with_a_literal_backslash(on_main):
    odd = make_repo(on_main.parent / "back\\slash", "my-feature")
    assert run_hook("git push", project_dir=on_main, hook_cwd=odd).returncode == 0


def test_only_the_top_level_cwd_key_counts(on_main, worktree_on_feature):
    def payload(top_first):
        tool_input = {"command": "git push", "cwd": on_main.as_posix()}
        top = {"cwd": str(worktree_on_feature)}
        rest = {"tool_name": "Bash", "tool_input": tool_input}
        return json.dumps({**top, **rest} if top_first else {**rest, **top})
    # a cwd key inside tool_input must not stand in for the real one, before or after it
    for top_first in (True, False):
        result = run_payload(payload(top_first), project_dir=on_main)
        assert result.returncode == 0, result.stderr.decode()


def test_text_that_looks_like_a_cwd_key_inside_the_command_is_not_one(on_main, on_feature):
    # no cwd field at all: the lookup must read CLAUDE_PROJECT_DIR (a feature
    # branch), not the main checkout the command text names
    decoy = json.dumps({"tool_name": "Bash",
                        "tool_input": {"command": f'echo "cwd": "{on_main.as_posix()}"; git push'}})
    result = run_payload(decoy, project_dir=on_feature)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize("hook_cwd", [
    "//some-host/share",
    r"\\some-host\share",
    r"\\?\UNC\some-host\share",
    "/??/UNC/some-host/share",
])
def test_bare_push_never_opens_a_network_cwd(hook_cwd, on_feature):
    result = run_hook("git push", project_dir=on_feature, hook_cwd=hook_cwd)
    assert result.returncode == 2, result.stderr.decode()
    assert b"network path" in result.stderr


def test_a_network_cwd_does_not_block_a_push_that_names_its_branch(on_feature):
    result = run_hook("git push origin my-feature", project_dir=on_feature, hook_cwd="//some-host/share")
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize("command", [
    "git -C //some-host/share push",
    r"git -C /\some-host\share push",
    "git -C /??/UNC/some-host/share push",
    r"git -C \\some-host\share push origin",
])
def test_bare_push_never_opens_a_network_path(command, on_feature):
    result = run_hook(command, project_dir=on_feature)
    assert result.returncode == 2, result.stderr.decode()
    assert b"network path" in result.stderr


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


# --- force branch delete: allowed only after its PR merged --------------------

FORCE_DELETES = [
    "git branch -D {b}",
    "git branch -Dq {b}",
    "git branch -D -q {b}",
    "git branch --delete --force {b}",
    "git branch -d --force {b}",
    "git branch -d -f {b}",
    "git branch -df {b}",
    "git branch -fd {b}",
    "git branch --force --delete {b}",
    "git branch --del --forc {b}",
    "git -C {repo} branch -D {b}",
    "git --no-pager branch -D {b} 2>&1",
    'git branch -D "{b}"',
]


@pytest.fixture
def repo_with_branch(on_feature):
    git(on_feature, "branch", "done-branch")
    return on_feature


def fmt(command, repo):
    return command.format(b="done-branch", repo=repo.as_posix())


@pytest.mark.parametrize("command", FORCE_DELETES)
def test_force_delete_allowed_after_merged_pr(command, repo_with_branch, gh):
    set_pr(gh, "done-branch", tip(repo_with_branch, "done-branch"))
    result = run_hook(fmt(command, repo_with_branch), project_dir=repo_with_branch)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize("command", FORCE_DELETES)
def test_force_delete_blocked_without_merged_pr(command, repo_with_branch):
    result = run_hook(fmt(command, repo_with_branch), project_dir=repo_with_branch)
    assert result.returncode == 2, result.stderr.decode()
    assert b"no merged PR for 'done-branch'" in result.stderr


def test_force_delete_blocked_when_tip_moved_after_the_pr(repo_with_branch, gh):
    set_pr(gh, "done-branch", "a" * 40)
    result = run_hook("git branch -D done-branch", project_dir=repo_with_branch)
    assert result.returncode == 2
    assert b"has commits after its merged PR" in result.stderr


def test_force_delete_blocked_when_only_a_closed_pr(repo_with_branch, gh):
    set_pr(gh, "done-branch", tip(repo_with_branch, "done-branch"), state="closed")
    result = run_hook("git branch -D done-branch", project_dir=repo_with_branch)
    assert result.returncode == 2
    assert b"no merged PR" in result.stderr


@pytest.mark.parametrize("mode", ["fail", "missing", "hang"])
def test_force_delete_blocked_when_gh_cannot_answer(mode, repo_with_branch, gh):
    set_pr(gh, "done-branch", tip(repo_with_branch, "done-branch"))
    (gh / "mode").write_text(mode)
    result = run_hook("git branch -D done-branch", project_dir=repo_with_branch)
    assert result.returncode == 2, result.stderr.decode()
    assert b"gh is missing, failed or took longer" in result.stderr


def test_force_delete_of_two_branches_needs_both(repo_with_branch, gh):
    git(repo_with_branch, "branch", "other-branch")
    set_pr(gh, "done-branch", tip(repo_with_branch, "done-branch"))
    result = run_hook("git branch -D done-branch other-branch", project_dir=repo_with_branch)
    assert result.returncode == 2
    assert b"'other-branch'" in result.stderr
    set_pr(gh, "other-branch", tip(repo_with_branch, "other-branch"))
    result = run_hook("git branch -D done-branch other-branch", project_dir=repo_with_branch)
    assert result.returncode == 0, result.stderr.decode()


@pytest.mark.parametrize("command", [
    "git branch -D",
    "git branch --delete --force",
    "git branch -D -q",
    "git branch -D 'done-*'",
    "git branch -D done-bran?h",
    "git branch -D [d]one-branch",
    "git branch -D $BRANCH",
    "git branch -D `echo done-branch`",
    "git branch -D $(echo done-branch)",
    "git branch -D done-branch $OTHER",
    "git branch -D # done-branch",
])
def test_force_delete_blocked_when_branch_is_not_literal(command, repo_with_branch, gh):
    set_pr(gh, "done-branch", tip(repo_with_branch, "done-branch"))
    result = run_hook(command, project_dir=repo_with_branch)
    assert result.returncode == 2, result.stderr.decode()


def test_comment_after_a_hash_does_not_add_a_name_or_break_the_exemption(repo_with_branch, gh):
    set_pr(gh, "done-branch", tip(repo_with_branch, "done-branch"))
    result = run_hook("git branch -D done-branch # merged in the PR", project_dir=repo_with_branch)
    assert result.returncode == 0, result.stderr.decode()


def test_force_delete_looks_in_the_dash_C_repo(on_main, repo_with_branch, gh):
    set_pr(gh, "done-branch", tip(repo_with_branch, "done-branch"))
    ok = run_hook(f'git -C "{repo_with_branch.as_posix()}" branch -D done-branch', project_dir=on_main)
    assert ok.returncode == 0, ok.stderr.decode()
    no_branch_here = run_hook("git branch -D done-branch", project_dir=on_main)
    assert no_branch_here.returncode == 2
    assert b"no local branch" in no_branch_here.stderr


@pytest.mark.parametrize("command", [
    "git -C //some-host/share branch -D done-branch",
    r"git -C \\some-host\share branch -D done-branch",
])
def test_force_delete_never_opens_a_network_path(command, repo_with_branch, gh):
    set_pr(gh, "done-branch", tip(repo_with_branch, "done-branch"))
    result = run_hook(command, project_dir=repo_with_branch)
    assert result.returncode == 2
    assert b"network path" in result.stderr


@pytest.mark.parametrize("command", [
    "git branch",
    "git branch -a",
    "git branch -d done-branch",
    "git branch -m done-branch renamed",
    "git branch -f done-branch HEAD",
    "git branch --list 'done-*'",
    "git branch new-branch",
])
def test_branch_commands_that_are_not_a_force_delete_pass(command, repo_with_branch):
    result = run_hook(command, project_dir=repo_with_branch)
    assert result.returncode == 0, result.stderr.decode()
