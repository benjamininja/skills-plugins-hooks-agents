"""Tests for the session-dispatch plugin's closeout (#250).

Part 1: what git itself does, on the platform the test runs on. Each
`test_q<n>_*` answers one question of the ticket's finding. Every repository
is a throwaway one under pytest's tmp_path.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

GIT_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
    "GIT_CONFIG_NOSYSTEM": "1",
}
WIN = sys.platform == "win32"


def git(root, *args, check=True):
    return subprocess.run(
        ["git", *args], cwd=root, check=check, capture_output=True, text=True,
        env={**os.environ, **GIT_ENV}, timeout=60,
    )


def commit_file(root, name, text, msg):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(root, "add", name)
    git(root, "commit", "-q", "-m", msg)


def make_project(tmp_path):
    """A main checkout on `main` with one commit and the project's ignores."""
    main = tmp_path / "proj"
    main.mkdir()
    git(main, "init", "-q", "-b", "main")
    git(main, "config", "core.autocrlf", "false")
    commit_file(main, ".gitignore", ".claude/worktrees/\n.venv/\nbuilder-state/\n", "init")
    return main


def add_worktree(main, name, branch=None):
    path = main / ".claude" / "worktrees" / name
    branch = branch or f"worktree-{name}"
    git(main, "worktree", "add", "-q", "-b", branch, str(path))
    return path


def add_ignored_content(wt):
    (wt / ".venv" / "Lib" / "site-packages").mkdir(parents=True)
    (wt / ".venv" / "pyvenv.cfg").write_text("home = x\n", encoding="utf-8")
    (wt / ".venv" / "Lib" / "site-packages" / "pkg.py").write_text("x = 1\n", encoding="utf-8")
    (wt / "builder-state").mkdir()
    (wt / "builder-state" / "notes.md").write_text("notes\n", encoding="utf-8")


def make_link(link, target):
    """A directory junction on Windows, a symlink elsewhere."""
    if WIN:
        r = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
    else:
        os.symlink(target, link, target_is_directory=True)


def is_link(path):
    """A symlink or a junction: a name-surrogate reparse point on Windows.

    Cloud-file placeholders (OneDrive) are reparse points too, but not name
    surrogates, so they do not count.
    """
    st = os.lstat(path)
    surrogate = getattr(st, "st_reparse_tag", 0) & 0x20000000
    return bool(surrogate) or os.path.islink(path)


# Q1 ---------------------------------------------------------------------------

def test_q1_ignored_only_worktree_is_removed_whole(tmp_path):
    main = make_project(tmp_path)
    wt = add_worktree(main, "b1")
    add_ignored_content(wt)

    status = git(wt, "status", "--porcelain").stdout
    assert status == ""  # ignored files print nothing

    r = git(main, "worktree", "remove", str(wt), check=False)
    assert r.returncode == 0, r.stderr
    assert not wt.exists()  # the whole folder, ignored content included
    assert not git(main, "worktree", "list", "--porcelain").stdout.count("/b1\n")


def test_q1_untracked_not_ignored_file_refuses(tmp_path):
    main = make_project(tmp_path)
    wt = add_worktree(main, "b1")
    add_ignored_content(wt)
    (wt / "stray.txt").write_text("x\n", encoding="utf-8")

    r = git(main, "worktree", "remove", str(wt), check=False)
    assert r.returncode != 0
    assert "untracked" in r.stderr or "modified" in r.stderr
    assert (wt / "stray.txt").exists() and (wt / ".venv").exists()


def test_q1_held_open_file(tmp_path):
    main = make_project(tmp_path)
    wt = add_worktree(main, "b1")
    add_ignored_content(wt)
    held = wt / ".venv" / "Lib" / "site-packages" / "pkg.py"
    admin = Path(git(wt, "rev-parse", "--absolute-git-dir").stdout.strip())

    probe = wt.with_name(wt.name + ".probe")
    with open(held, "rb"):
        # a pre-flight: a folder whose file is open cannot be renamed on Windows
        try:
            os.rename(wt, probe)
            os.rename(probe, wt)
            renamed = True
        except OSError:
            renamed = False
        r = git(main, "worktree", "remove", str(wt), check=False)
        left = sorted(str(p.relative_to(wt)).replace(os.sep, "/") for p in wt.rglob("*")) if wt.exists() else None
        listed = any(line.startswith("worktree ") and line.endswith("/b1")
                     for line in git(main, "worktree", "list", "--porcelain").stdout.splitlines())

    report = (f"renamed={renamed} rc={r.returncode} stderr={r.stderr.strip()!r} left={left} "
              f"listed={listed} admin_exists={admin.exists()}")
    print(report)
    if WIN:
        # The rename pre-flight sees the open file before git touches anything.
        assert not renamed, report
        # git stops at the first file it cannot delete, yet still drops its own
        # record: the folder is left behind, unknown to git, without its .git file.
        assert r.returncode != 0, report
        assert held.exists() and ".git" not in left, report
        assert not listed and not admin.exists(), report
    else:
        # POSIX renames and unlinks an open file: the removal finishes.
        assert renamed, report
        assert r.returncode == 0, report
        assert not wt.exists(), report


def test_q1_process_cwd_inside_blocks_rename(tmp_path):
    """A session still running in the worktree holds it, like an open file."""
    main = make_project(tmp_path)
    wt = add_worktree(main, "b1")
    marker = tmp_path / "started"
    proc = subprocess.Popen(
        [sys.executable, "-c", f"import time; open({str(marker)!r}, 'w').close(); time.sleep(30)"],
        cwd=wt)
    try:
        deadline = time.monotonic() + 20
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.1)
        assert marker.exists()
        try:
            os.rename(wt, wt.with_name("b1.probe"))
            os.rename(wt.with_name("b1.probe"), wt)
            renamed = True
        except OSError:
            renamed = False
    finally:
        proc.kill()
        proc.wait()
    assert renamed is not WIN


# Q2 ---------------------------------------------------------------------------

def squash_merge(main, branch, msg="squash"):
    git(main, "merge", "-q", "--squash", branch)
    git(main, "commit", "-q", "-m", msg)


def is_ancestor(root, a, b):
    return git(root, "merge-base", "--is-ancestor", a, b, check=False).returncode


def test_q2_cherry_after_squash_of_several_commits(tmp_path):
    main = make_project(tmp_path)
    wt = add_worktree(main, "b2")
    commit_file(wt, "a.txt", "a\n", "one")
    commit_file(wt, "b.txt", "b\n", "two")
    commit_file(wt, "a.txt", "a2\n", "three")
    squash_merge(main, "worktree-b2")

    cherry = git(main, "cherry", "main", "worktree-b2").stdout.split()
    # every commit of the branch shows as missing: cherry cannot see a squash
    assert cherry.count("+") == 3 and "-" not in cherry


def test_q2_cherry_after_squash_of_one_commit(tmp_path):
    main = make_project(tmp_path)
    wt = add_worktree(main, "b2")
    commit_file(wt, "a.txt", "a\n", "one")
    squash_merge(main, "worktree-b2")

    cherry = git(main, "cherry", "main", "worktree-b2").stdout.split()
    assert cherry == ["-", cherry[1]]  # one commit: same patch id, shown as present


def test_q2_merged_pr_head_ancestor_test(tmp_path):
    """The proposed test: local tip is the merged PR's head or an ancestor of it."""
    main = make_project(tmp_path)
    wt = add_worktree(main, "b2")
    commit_file(wt, "a.txt", "a\n", "one")
    commit_file(wt, "b.txt", "b\n", "two")
    commit_file(main, "m.txt", "m\n", "main moves on")
    git(wt, "merge", "-q", "-m", "merge main in", "main")  # a builder merges main in
    commit_file(wt, "c.txt", "c\n", "three")
    head = git(wt, "rev-parse", "HEAD").stdout.strip()
    squash_merge(main, "worktree-b2")

    # equal to the head
    assert is_ancestor(main, "worktree-b2", head) == 0
    # #215: local tip two commits behind the head
    git(wt, "reset", "-q", "--hard", "HEAD~2")
    assert is_ancestor(main, "worktree-b2", head) == 0
    # one commit the PR lacks
    commit_file(wt, "d.txt", "d\n", "after the PR")
    assert is_ancestor(main, "worktree-b2", head) == 1
    # a head object that is not local: git errors (128), so the test fails closed
    assert is_ancestor(main, "worktree-b2", "0123456789abcdef0123456789abcdef01234567") == 128


# Q3 ---------------------------------------------------------------------------

def test_q3_detached_worktree_cases(tmp_path):
    main = make_project(tmp_path)
    commit_file(main, "m.txt", "m\n", "on main")
    on_main = git(main, "rev-parse", "HEAD").stdout.strip()

    path = main / ".claude" / "worktrees" / "d1"
    git(main, "worktree", "add", "-q", "--detach", str(path), on_main)
    porcelain = git(main, "worktree", "list", "--porcelain").stdout
    blocks = [b for b in porcelain.split("\n\n") if b.strip()]
    block = [b for b in blocks if b.splitlines()[0].endswith("/d1")][0]
    assert "detached" in block and "branch " not in block
    assert is_ancestor(main, "HEAD", "main") == 0  # on main: removable

    commit_file(path, "x.txt", "x\n", "detached work")
    tip = git(path, "rev-parse", "HEAD").stdout.strip()
    assert is_ancestor(main, tip, "main") == 1  # its own commit: refused


# Q4 ---------------------------------------------------------------------------

def outside_sentinel(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep.txt").write_text("keep\n", encoding="utf-8")
    return outside


def test_q4_git_worktree_remove_and_a_link_out(tmp_path):
    main = make_project(tmp_path)
    wt = add_worktree(main, "b4")
    add_ignored_content(wt)
    outside = outside_sentinel(tmp_path)
    link = wt / "builder-state" / "out"
    make_link(link, outside)
    assert is_link(link)
    assert git(wt, "status", "--porcelain").stdout == ""  # an ignored link is invisible to status

    r = git(main, "worktree", "remove", str(wt), check=False)
    version = git(main, "--version").stdout.strip()
    left = sorted(str(p.relative_to(wt)).replace(os.sep, "/") for p in wt.rglob("*")) if wt.exists() else None
    report = (f"{version} rc={r.returncode} stderr={r.stderr.strip()!r} left={left} "
              f"outside_exists={outside.exists()} keep_exists={(outside / 'keep.txt').exists()}")
    print(report)
    if WIN:
        # Git for Windows never removes it cleanly. Seen so far, by version: it
        # follows the junction and deletes what it points to, or it exits 0
        # and leaves the worktree folder behind.
        clean = not wt.exists() and (outside / "keep.txt").exists()
        assert not clean, report
    else:
        # git unlinks the symlink and does not descend: the target survives
        assert (outside / "keep.txt").exists(), report


def find_links(root):
    """Every symlink or junction under root, found without following any."""
    found, stack = [], [str(root)]
    while stack:
        with os.scandir(stack.pop()) as it:
            for entry in it:
                if is_link(entry.path):
                    found.append(entry.path)
                elif entry.is_dir(follow_symlinks=False):
                    stack.append(entry.path)
    return found


def test_q4_scan_finds_link_without_following(tmp_path):
    main = make_project(tmp_path)
    wt = add_worktree(main, "b4")
    add_ignored_content(wt)
    outside = outside_sentinel(tmp_path)
    (outside / "deep").mkdir()
    (outside / "deep" / "x.txt").write_text("x\n", encoding="utf-8")
    make_link(wt / ".venv" / "out", outside)

    links = find_links(wt)
    assert [os.path.basename(p) for p in links] == ["out"]
    assert (outside / "deep" / "x.txt").exists()
