"""Tests for the session-dispatch plugin's closeout (#250).

Part 1: what git itself does, on the platform the test runs on. Each
`test_q<n>_*` answers one question of the ticket's finding. Every repository
is a throwaway one under pytest's tmp_path.
"""
import importlib.util
import json
import os
import shutil
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


# Part 2: scripts/closeout.py ---------------------------------------------------

SCRIPT = (Path(__file__).resolve().parent.parent / "plugins" / "session-dispatch-managers-build-review"
          / "scripts" / "closeout.py")
_spec = importlib.util.spec_from_file_location("closeout", SCRIPT)
closeout = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(closeout)


@pytest.fixture
def proj(tmp_path, monkeypatch):
    """A main checkout with an origin, origin/HEAD set, and a stand-in gh."""
    for k, val in GIT_ENV.items():
        monkeypatch.setenv(k, val)
    main = make_project(tmp_path)
    origin = tmp_path / "origin.git"
    git(tmp_path, "clone", "-q", "--bare", str(main), str(origin))
    git(main, "remote", "add", "origin", str(origin))
    git(main, "fetch", "-q", "origin")
    git(main, "remote", "set-head", "origin", "main")
    fakebin = tmp_path / "fakebin"
    fakebin.mkdir()
    if WIN:
        (fakebin / "gh.cmd").write_text(
            '@echo off\r\nif defined FAKE_GH_RC exit /b %FAKE_GH_RC%\r\ntype "%FAKE_GH_JSON%"\r\n',
            encoding="utf-8")
    else:
        gh = fakebin / "gh"
        gh.write_text('#!/bin/sh\n[ -n "$FAKE_GH_RC" ] && exit "$FAKE_GH_RC"\ncat "$FAKE_GH_JSON"\n',
                      encoding="utf-8")
        gh.chmod(0o755)
    monkeypatch.setenv("PATH", str(fakebin) + os.pathsep + os.environ["PATH"])
    monkeypatch.delenv("FAKE_GH_RC", raising=False)
    prs_file = tmp_path / "prs.json"
    monkeypatch.setenv("FAKE_GH_JSON", str(prs_file))

    class P:
        pass
    p = P()
    p.main, p.tmp, p.root = main, tmp_path, main / ".claude" / "worktrees"
    p.prs = []

    def set_prs(prs):
        p.prs = prs
        prs_file.write_text(json.dumps(prs), encoding="utf-8")
    p.set_prs = set_prs
    set_prs([])
    return p


def builder(p, name, commits=2):
    wt = add_worktree(p.main, name)
    for i in range(commits):
        commit_file(wt, f"{name}-{i}.txt", f"{i}\n", f"{name} {i}")
    add_ignored_content(wt)
    return wt, git(wt, "rev-parse", "HEAD").stdout.strip()


def squash(p, branch):
    squash_merge(p.main, branch)
    git(p.main, "push", "-q", "origin", "main")
    git(p.main, "fetch", "-q", "origin")


def merged_builder(p, name, number=7, commits=2):
    wt, tip = builder(p, name, commits)
    squash(p, f"worktree-{name}")
    p.set_prs(p.prs + [{"number": number, "headRefName": f"worktree-{name}", "headRefOid": tip}])
    return wt, tip


def run_closeout(capsys, *args):
    code = closeout.main([str(a) for a in args])
    return code, capsys.readouterr().out


def has_branch(p, b):
    return git(p.main, "rev-parse", "--verify", "--quiet", f"refs/heads/{b}", check=False).returncode == 0


def snapshot(p):
    tree = sorted(str(x) for x in p.root.rglob("*")) if p.root.exists() else []
    return (git(p.main, "worktree", "list", "--porcelain").stdout,
            git(p.main, "branch", "--list").stdout, tree)


def test_removes_merged_clean_worktree(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 0, out
    assert out.splitlines()[0].startswith("closeout: git version")
    assert "b1: removed (merged, PR #7)" in out
    assert "branch worktree-b1 deleted" in out
    assert not wt.exists() and not has_branch(proj, "worktree-b1")


def test_dry_run_changes_nothing(proj, capsys):
    merged_builder(proj, "b1")
    before = snapshot(proj)
    code, out = run_closeout(capsys, proj.main, "b1")
    assert code == 0, out
    assert "b1: would remove (merged, PR #7)" in out
    assert "would delete branch worktree-b1" in out
    assert ("in-use check runs at apply time" in out) is WIN
    assert snapshot(proj) == before


def test_refuses_unmerged_branch(proj, capsys):
    wt, _ = builder(proj, "b1")
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1
    assert "b1: refused: no merged PR" in out
    assert "refused, for the owner queue:" in out
    assert wt.exists() and has_branch(proj, "worktree-b1")


def test_refuses_commits_after_merged_pr(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    commit_file(wt, "late.txt", "late\n", "after the PR")
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1 and "commits after merged PR #7" in out and wt.exists()


def test_refuses_tracked_change(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    (wt / "b1-0.txt").write_text("changed\n", encoding="utf-8")
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1 and "uncommitted: 1 line(s)" in out and "b1-0.txt" in out
    assert wt.exists()


def test_refuses_untracked_file_not_ignored(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    (wt / "stray.txt").write_text("x\n", encoding="utf-8")
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1 and "uncommitted" in out and "stray.txt" in out
    assert wt.exists()


def test_refuses_locked(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    git(proj.main, "worktree", "lock", "--reason", "kept", str(wt))
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1 and "locked: kept" in out and wt.exists()


@pytest.mark.parametrize("name", ["..", "../x", "a/b", "B1", "-x"])
def test_refuses_path_outside_the_folder(proj, capsys, name):
    code, out = run_closeout(capsys, proj.main, name, "--apply")
    assert code == 2


def test_never_acts_on_a_worktree_outside_the_folder(proj, capsys):
    elsewhere = proj.tmp / "elsewhere"
    git(proj.main, "worktree", "add", "-q", "-b", "worktree-b5", str(elsewhere))
    code, out = run_closeout(capsys, proj.main, "b5", "--apply")
    assert code == 1 and "no worktree of that name" in out and elsewhere.exists()
    code, out = run_closeout(capsys, proj.main, "--list")
    assert "1 worktree(s) outside" in out


def test_refuses_folder_git_does_not_know(proj, capsys):
    ghost = proj.root / "ghost"
    ghost.mkdir(parents=True)
    (ghost / "f.txt").write_text("x\n", encoding="utf-8")
    code, out = run_closeout(capsys, proj.main, "ghost", "--apply")
    assert code == 1 and "unknown to git: listed, never removed" in out
    assert (ghost / "f.txt").exists()


def test_refuses_folder_link_out(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    outside = outside_sentinel(proj.tmp)
    make_link(wt / "builder-state" / "out", outside)
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1 and "folder link" in out and "points out to" in out
    assert str(outside) in out or os.path.realpath(outside) in out
    assert wt.exists() and (outside / "keep.txt").exists()


def test_folder_link_inside_passes_the_scan(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    make_link(wt / "builder-state" / "in", wt / ".venv")
    code, out = run_closeout(capsys, proj.main, "b1")
    assert code == 0 and "b1: would remove" in out, out


def test_file_link_out_is_removed_as_a_link(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    outside = outside_sentinel(proj.tmp)
    try:
        os.symlink(outside / "keep.txt", wt / "builder-state" / "f-link")
    except OSError as e:
        pytest.skip(f"this platform cannot make a file symlink here: {e}")
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 0, out
    assert "b1: removed" in out and not wt.exists()
    assert (outside / "keep.txt").read_text(encoding="utf-8") == "keep\n"


def test_refuses_dangling_link(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    gone = proj.tmp / "gone"
    gone.mkdir()
    make_link(wt / "builder-state" / "dead", gone)
    gone.rmdir()
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1 and "cannot be resolved" in out and wt.exists()


def test_refuses_planted_git_file_and_runs_nothing_from_it(proj, capsys):
    """A builder's .git file that names a repository of its own is never followed."""
    wt, _ = merged_builder(proj, "b1")
    evil = wt / "builder-state" / "evil"
    git(proj.tmp, "init", "-q", "--bare", str(evil))
    marker = proj.tmp / "ran.txt"
    git(evil, "config", "core.fsmonitor", f"echo ran > '{marker.as_posix()}'")
    with open(wt / ".git", "r+", encoding="utf-8") as f:  # r+: Windows refuses "w" on a hidden file
        f.write(f"gitdir: {evil.as_posix()}\n")
        f.truncate()
    for args in (("b1", "--apply"), ("--list",)):
        code, out = run_closeout(capsys, proj.main, *args)
        assert "does not point to the main checkout's worktree record" in out, out
    assert not marker.exists()
    assert wt.exists() and has_branch(proj, "worktree-b1")


def test_refuses_top_folder_that_is_a_link(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    moved = proj.tmp / "moved-b1"
    os.rename(wt, moved)
    make_link(wt, moved)
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1 and "top folder is a link" in out
    assert (moved / "b1-0.txt").exists()


@pytest.mark.skipif(not WIN, reason="an open file blocks a delete only on Windows")
def test_refuses_in_use_and_deletes_nothing(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    held = wt / ".venv" / "pyvenv.cfg"
    with open(held, "rb"):
        code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1 and "in use" in out and "Close any terminal" in out
    assert (wt / "b1-0.txt").exists() and (wt / ".git").exists() and has_branch(proj, "worktree-b1")


def test_in_use_check_refuses_when_sibling_exists(tmp_path):
    wt = tmp_path / "b1"
    wt.mkdir()
    (tmp_path / ("b1" + closeout.INUSE_SUFFIX)).mkdir()
    ok, msg, fatal = closeout.in_use_check(str(wt))
    assert not ok and not fatal and "already exists" in msg and wt.exists()


def test_in_use_check_rename_back_fails(tmp_path, monkeypatch):
    wt = tmp_path / "b1"
    wt.mkdir()
    real, calls = os.rename, []

    def rename(a, b):
        calls.append((a, b))
        if len(calls) > 1:
            raise OSError("held")
        real(a, b)
    monkeypatch.setattr(closeout.os, "rename", rename)
    monkeypatch.setattr(closeout.time, "sleep", lambda s: None)
    ok, msg, fatal = closeout.in_use_check(str(wt))
    monkeypatch.undo()
    sibling = str(wt) + closeout.INUSE_SUFFIX
    assert not ok and fatal and len(calls) == 6
    assert "Rename" in msg and sibling in msg and "Nothing was deleted" in msg
    assert os.path.isdir(sibling) and not wt.exists()


def test_git_reports_success_but_leaves_the_folder(proj, capsys, monkeypatch):
    wt, _ = merged_builder(proj, "b1")
    real = closeout.git

    def fake(cwd, *args):
        if args[:2] == ("worktree", "remove"):
            return 0, "", ""
        return real(cwd, *args)
    monkeypatch.setattr(closeout, "git", fake)
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 3
    assert "removal did not finish (git exit 0)" in out and "git still lists it" in out
    assert "left:" in out and "b1: removed" not in out
    assert has_branch(proj, "worktree-b1")


def test_merged_pr_head_not_local_is_unknown(proj, capsys):
    wt, _ = builder(proj, "b1")
    proj.set_prs([{"number": 9, "headRefName": "worktree-b1", "headRefOid": "ab" * 20}])
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1
    assert "unknown: PR #9 head not local" in out
    assert f"git -C {os.path.abspath(proj.main)} fetch origin pull/9/head" in out
    assert wt.exists()


def test_local_tip_behind_merged_head_215(proj, capsys):
    wt, tip = merged_builder(proj, "b1", commits=3)
    git(wt, "reset", "-q", "--hard", "HEAD~2")
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 0 and "b1: removed (merged, PR #7)" in out, out


def test_no_commit_of_its_own_is_removable(proj, capsys):
    wt = add_worktree(proj.main, "b1")
    add_ignored_content(wt)
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 0 and "b1: removed (no commit of its own" in out, out
    assert not wt.exists() and not has_branch(proj, "worktree-b1")


def test_detached_worktrees(proj, capsys):
    on_main = git(proj.main, "rev-parse", "HEAD").stdout.strip()
    d1 = proj.root / "d1"
    git(proj.main, "worktree", "add", "-q", "--detach", str(d1), on_main)
    d2 = proj.root / "d2"
    git(proj.main, "worktree", "add", "-q", "--detach", str(d2), on_main)
    commit_file(d2, "x.txt", "x\n", "detached work")
    d3 = proj.root / "d3"
    git(proj.main, "worktree", "add", "-q", "--detach", str(d3), on_main)
    commit_file(d3, "y.txt", "y\n", "detached PR head")
    head3 = git(d3, "rev-parse", "HEAD").stdout.strip()
    proj.set_prs([{"number": 11, "headRefName": "other", "headRefOid": head3}])

    code, out = run_closeout(capsys, proj.main, "d1", "--apply")
    assert code == 0 and "d1: removed (no commit of its own" in out
    code, out = run_closeout(capsys, proj.main, "d2", "--apply")
    assert code == 1 and "detached at" in out and d2.exists()
    code, out = run_closeout(capsys, proj.main, "d3", "--apply")
    assert code == 0 and "d3: removed (merged, PR #11)" in out


def test_gh_failure_removes_nothing(proj, capsys, monkeypatch):
    wt = add_worktree(proj.main, "b1")  # no commit of its own: would pass without gh
    monkeypatch.setenv("FAKE_GH_RC", "1")
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 1 and "unknown: gh failed" in out and wt.exists()


def test_pr_list_at_the_limit_says_it_may_be_cut(proj, capsys, monkeypatch):
    wt, _ = builder(proj, "b1")
    monkeypatch.setattr(closeout, "PR_LIMIT", 1)
    proj.set_prs([{"number": 1, "headRefName": "other", "headRefOid": "cd" * 20}])
    code, out = run_closeout(capsys, proj.main, "b1")
    assert code == 1 and "no merged PR (the merged PR list stopped at 1 and may be cut)" in out


def test_main_checkout_in_another_case_and_slash(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    arg = str(proj.main)
    arg = arg.replace("\\", "/").upper() if WIN else arg + "/"
    code, out = run_closeout(capsys, arg, "b1", "--apply")
    assert code == 0 and "b1: removed" in out, out
    assert not wt.exists()


def test_extra_branches(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    git(wt, "branch", "feat-merged")
    git(wt, "branch", "feat-open", "HEAD")
    commit_file(wt, "z.txt", "z\n", "more")  # moves worktree-b1 only
    git(wt, "branch", "-f", "feat-open", "HEAD")
    git(wt, "reset", "-q", "--hard", "HEAD~1")
    code, out = run_closeout(capsys, proj.main, "b1", "--apply", "--branch", "feat-merged",
                             "--branch", "feat-open")
    assert "b1: removed" in out
    assert "branch feat-merged deleted (merged, PR #7)" in out
    assert "kept: branch feat-open" in out and code == 1
    assert not has_branch(proj, "feat-merged") and has_branch(proj, "feat-open")


def test_list_mode(proj, capsys):
    merged_builder(proj, "m1", number=1)
    w2 = add_worktree(proj.main, "e1")  # no commit of its own
    builder(proj, "u1")
    proj.set_prs(proj.prs + [{"number": 3, "headRefName": "worktree-u1", "headRefOid": "ef" * 20}])
    dirty, _ = merged_builder(proj, "m2", number=2)
    (dirty / "stray.txt").write_text("x\n", encoding="utf-8")
    ghost = proj.root / "ghost"
    ghost.mkdir()
    outside = outside_sentinel(proj.tmp)
    make_link(ghost / "out", outside)
    (proj.root / ("e1" + closeout.INUSE_SUFFIX)).mkdir()
    gone = add_worktree(proj.main, "g1")
    shutil.rmtree(gone)

    before = snapshot(proj)
    code, out = run_closeout(capsys, proj.main, "--list")
    assert code == 0, out
    assert "m1: would remove (merged, PR #1)" in out
    assert "e1: would remove (no commit of its own" in out
    assert "u1: refused: unknown: PR #3 head not local" in out
    assert "m2: refused: uncommitted" in out
    assert "ghost: unknown to git: listed, never removed; folder link" in out
    assert f"e1{closeout.INUSE_SUFFIX}: an interrupted in-use check of e1" in out
    assert "g1: refused: git record only: the folder is gone" in out
    assert out.rstrip().splitlines()[-1] == \
        "count: merged and still there 2; no commit of its own 1; unknown 1"
    assert snapshot(proj) == before and w2.exists()


def test_list_takes_no_builder(proj, capsys):
    code, out = run_closeout(capsys, proj.main, "b1", "--list")
    assert code == 2


def test_refuses_a_linked_worktree_as_main(proj, capsys):
    wt, _ = merged_builder(proj, "b1")
    code, out = run_closeout(capsys, wt, "b1")
    assert code == 2 and "not the main checkout" in out


def test_refuses_without_origin_head(proj, capsys):
    merged_builder(proj, "b1")
    git(proj.main, "remote", "set-head", "origin", "--delete")
    code, out = run_closeout(capsys, proj.main, "b1", "--apply")
    assert code == 2 and "cannot tell the main branch" in out
