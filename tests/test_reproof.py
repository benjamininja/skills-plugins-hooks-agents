"""tools/reproof.py: the argument check, the summary's exit code, that the
repository it runs in gains objects and FETCH_HEAD, never a ref or a file, and
the machine-wide lock (#231).

No network and no real PR: origin is a local bare repository and the PR head
is a ref made by hand under refs/pull/1/head. Every test points the lock at a
temp folder (the autouse fixture below), so the suite never touches the real
lock, which the outer run holds while it runs this file.
"""
import errno
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "reproof.py"
_spec = importlib.util.spec_from_file_location("reproof", SCRIPT)
reproof = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reproof)

SHA = "a" * 40

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}

BUILD_CATALOG = (
    "from pathlib import Path\n"
    "Path(__file__).resolve().parent.parent.joinpath('CATALOG.md').write_bytes(b'{}')\n"
)

BASE = {
    "tools/build_catalog.py": BUILD_CATALOG.format("catalog\\n"),
    "CATALOG.md": "catalog\n",
    "tests/test_base.py": "def test_base():\n    assert True\n",
    "shared.txt": "base\n",
}

MERGED_TEST = (
    "from pathlib import Path\n"
    "def test_main_only():\n"
    "    assert (Path(__file__).resolve().parent.parent / 'MAIN_ONLY.txt').exists()\n"
)


def git(cwd, *args):
    done = subprocess.run(
        ["git", "-c", "core.autocrlf=false", "-c", "core.longpaths=true",
         "-c", "protocol.file.allow=always", *args],
        cwd=cwd, env=GIT_ENV, capture_output=True, text=True, check=True,
    )
    return done.stdout.strip()


def write(root, files):
    for name, text in files.items():
        path = Path(reproof.long_path(Path(root) / name))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))


def commit(work, message):
    git(work, "add", "-A")
    git(work, "commit", "-q", "-m", message)
    return git(work, "rev-parse", "HEAD")


def scenario(tmp_path, pr_files=None, main_files=None, pr_remove=()):
    """A stale clone, an origin whose main has moved on, and PR 1 on origin.

    Returns (clone, head sha of PR 1, sha of the moved main).
    """
    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    clone = tmp_path / "live"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    git(tmp_path, "init", "-q", "-b", "main", str(work))
    git(work, "remote", "add", "origin", str(origin))
    write(work, BASE)
    commit(work, "base")
    git(work, "push", "-q", "origin", "main")
    git(tmp_path, "clone", "-q", str(origin), str(clone))

    git(work, "checkout", "-q", "-b", "pr")
    write(work, {"tests/test_merged.py": MERGED_TEST, **(pr_files or {})})
    for name in pr_remove:
        (work / name).unlink()
    head = commit(work, "pr")
    git(work, "push", "-q", "origin", "HEAD:refs/pull/1/head")

    git(work, "checkout", "-q", "main")
    write(work, {"MAIN_ONLY.txt": "x\n", **(main_files or {})})
    moved = commit(work, "main moves on")
    git(work, "push", "-q", "origin", "main")
    return clone, head, moved


def snapshot(clone):
    return (
        git(clone, "for-each-ref"),
        git(clone, "rev-parse", "HEAD"),
        git(clone, "status", "--porcelain"),
        git(clone, "branch", "--list", "-a"),
    )


@pytest.fixture(autouse=True)
def lock_area(tmp_path, monkeypatch):
    area = tmp_path / "lock-area"
    monkeypatch.setattr(reproof, "LOCK_DIR", area)
    return area


@pytest.fixture
def export_area(tmp_path, monkeypatch):
    area = tmp_path / "export-area"
    area.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(area))
    return area


def reproof_run(clone, head, capsys):
    code = reproof.main(["1", head], repo=clone)
    return code, capsys.readouterr().out


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["1"],
        ["1", SHA, "extra"],
        ["0", SHA],
        ["01", SHA],
        ["abc", SHA],
        ["-1", SHA],
        ["1 ", SHA],
        ["1\n", SHA],
        ["١", SHA],
        ["1;ls", SHA],
        ["1234567890", SHA],
        ["pull/1/head:pr1", SHA],
        ["1", "a" * 39],
        ["1", "a" * 41],
        ["1", "A" * 40],
        ["1", "g" * 40],
        ["1", SHA + "\n"],
        ["1", "--upload-pack=x"],
        ["1", "HEAD"],
    ],
)
def test_refuses_bad_arguments(argv, tmp_path, capsys):
    assert reproof.parse_args(argv) is None
    assert reproof.main(argv, repo=tmp_path) == 2
    assert not (tmp_path / ".git").exists()
    assert "usage" in capsys.readouterr().err


def test_accepts_a_number_and_a_sha():
    assert reproof.parse_args(["117", SHA]) == ("117", SHA)


def test_script_refuses_bad_arguments_as_a_command():
    done = subprocess.run(
        [sys.executable, str(SCRIPT), "1;ls", SHA], capture_output=True, text=True
    )
    assert done.returncode == 2
    assert "usage" in done.stderr


def test_green_run_exits_zero_and_changes_nothing_in_the_clone(tmp_path, export_area, capsys):
    clone, head, moved = scenario(tmp_path)
    before = snapshot(clone)
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    assert "RESULT: GREEN" in out
    for step in ("fetch main", "fetch head", "merge", "export", "pytest",
                 "build_catalog", "catalog diff"):
        assert f"PASS  {step}" in out
    assert snapshot(clone) == before
    assert git(clone, "rev-parse", "origin/main") != moved
    assert (clone / ".git" / "FETCH_HEAD").exists()
    assert git(clone, "cat-file", "-t", moved) == "commit"
    assert not (clone / "MAIN_ONLY.txt").exists()
    assert list(export_area.iterdir()) == []


def test_the_timeout_is_an_hour():
    assert reproof.TIMEOUT == 3600


def test_the_pytest_timeout_is_ninety_minutes():
    assert reproof.PYTEST_TIMEOUT == 5400


def spy_on_run(monkeypatch):
    calls = []
    real = reproof.run

    def spy(cmd, cwd=None, timeout=reproof.TIMEOUT):
        calls.append((cmd, timeout))
        return real(cmd, cwd, timeout)

    monkeypatch.setattr(reproof, "run", spy)
    return calls


def is_pytest(cmd):
    return cmd[1:3] == ["-m", "pytest"]


def test_the_pytest_step_gets_its_own_cap_and_every_other_step_keeps_the_hour(
    tmp_path, export_area, monkeypatch, capsys
):
    calls = spy_on_run(monkeypatch)
    clone, head, _ = scenario(tmp_path)
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    pytest_calls = [t for cmd, t in calls if is_pytest(cmd)]
    other_calls = [t for cmd, t in calls if not is_pytest(cmd)]
    assert pytest_calls == [reproof.PYTEST_TIMEOUT]
    assert other_calls
    assert set(other_calls) == {reproof.TIMEOUT}


def test_the_pytest_command_prints_the_durations_table(tmp_path, export_area, monkeypatch, capsys):
    calls = spy_on_run(monkeypatch)
    clone, head, _ = scenario(tmp_path)
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    pytest_cmds = [cmd for cmd, _ in calls if is_pytest(cmd)]
    assert len(pytest_cmds) == 1
    assert "--durations=25" in pytest_cmds[0]
    assert "-q" in pytest_cmds[0]
    assert "slowest 25 durations" in out


def test_a_timeout_names_the_cap_that_applied(monkeypatch):
    def expire(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, kwargs["timeout"])

    monkeypatch.setattr(reproof.subprocess, "run", expire)
    assert reproof.run(["x"]) == (124, "", "timed out after 3600s")
    assert reproof.run(["x"], timeout=reproof.PYTEST_TIMEOUT) == (124, "", "timed out after 5400s")


@pytest.mark.parametrize("partial", [b"tests/a.py ..\ntests/b.py .\n", "tests/a.py ..\ntests/b.py .\n"])
def test_a_timeout_keeps_the_output_printed_so_far(partial, monkeypatch):
    def expire(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, kwargs["timeout"], output=partial)

    monkeypatch.setattr(reproof.subprocess, "run", expire)
    code, out, err = reproof.run(["x"], timeout=5)
    assert code == 124
    assert out == "tests/a.py ..\ntests/b.py .\n"
    assert err == "timed out after 5s"


def test_every_result_line_carries_its_elapsed_seconds(tmp_path, export_area, monkeypatch, capsys):
    ticks = iter(x * 2.5 for x in range(1000))
    monkeypatch.setattr(reproof, "time", types.SimpleNamespace(monotonic=lambda: next(ticks)))
    clone, head, _ = scenario(tmp_path)
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    steps = ("fetch main", "fetch head", "merge", "export", "index", "pytest",
             "build_catalog", "catalog diff")
    for step in steps:
        assert f"== {step}: PASS (2.5s)" in out
        assert f"PASS  {step} 2.5s" in out


def test_a_failing_step_also_carries_its_elapsed_seconds(tmp_path, export_area, capsys):
    clone, head, _ = scenario(
        tmp_path, pr_files={"tests/test_fail.py": "def test_fail():\n    assert False\n"}
    )
    code, out = reproof_run(clone, head, capsys)
    assert code == 1
    assert re.search(r"== pytest: FAIL \(\d+\.\ds\)", out)
    assert re.search(r"^FAIL  pytest \d+\.\ds$", out, re.MULTILINE)


LS_FILES_TEST = (
    "import subprocess\n"
    "def test_export_has_an_index():\n"
    "    out = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, check=True).stdout\n"
    "    assert 'shared.txt' in out.split()\n"
)


def test_the_export_has_a_git_index_for_tests_that_list_files(tmp_path, export_area, capsys):
    clone, head, _ = scenario(tmp_path, pr_files={"tests/test_ls_files.py": LS_FILES_TEST})
    before = snapshot(clone)
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    assert "RESULT: GREEN" in out
    assert "PASS  index" in out
    assert snapshot(clone) == before
    assert list(export_area.iterdir()) == []


def test_failing_pytest_exits_nonzero_and_the_other_steps_still_run(tmp_path, export_area, capsys):
    clone, head, _ = scenario(
        tmp_path, pr_files={"tests/test_fail.py": "def test_fail():\n    assert False\n"}
    )
    code, out = reproof_run(clone, head, capsys)
    assert code == 1
    assert "RESULT: NOT GREEN" in out
    assert "FAIL  pytest" in out
    assert "PASS  build_catalog" in out
    assert "PASS  catalog diff" in out
    assert list(export_area.iterdir()) == []


def test_catalog_drift_exits_nonzero(tmp_path, export_area, capsys):
    clone, head, _ = scenario(
        tmp_path, pr_files={"tools/build_catalog.py": BUILD_CATALOG.format("other\\n")}
    )
    code, out = reproof_run(clone, head, capsys)
    assert code == 1
    assert "PASS  pytest" in out
    assert "PASS  build_catalog" in out
    assert "FAIL  catalog diff" in out
    assert "+other" in out


def test_failing_build_catalog_skips_the_diff_and_exits_nonzero(tmp_path, export_area, capsys):
    clone, head, _ = scenario(
        tmp_path, pr_files={"tools/build_catalog.py": "raise SystemExit(3)\n"}
    )
    code, out = reproof_run(clone, head, capsys)
    assert code == 1
    assert "FAIL  build_catalog" in out
    assert "SKIP  catalog diff" in out


def test_merge_conflict_exits_nonzero_before_the_export(tmp_path, export_area, capsys):
    clone, head, _ = scenario(
        tmp_path, pr_files={"shared.txt": "pr\n"}, main_files={"shared.txt": "main\n"}
    )
    code, out = reproof_run(clone, head, capsys)
    assert code == 1
    assert "FAIL  merge" in out
    assert "merge conflict" in out
    assert "pytest" not in out.split("== summary")[1]
    assert list(export_area.iterdir()) == []


def test_a_moved_head_is_refused(tmp_path, export_area, capsys):
    clone, head, moved = scenario(tmp_path)
    code, out = reproof_run(clone, moved, capsys)
    assert code == 1
    assert "FAIL  fetch head" in out
    assert "PASS  merge" not in out


def test_an_unknown_pr_is_refused(tmp_path, export_area, capsys):
    clone, head, _ = scenario(tmp_path)
    before = snapshot(clone)
    code = reproof.main(["2", head], repo=clone)
    out = capsys.readouterr().out
    assert code == 1
    assert "FAIL  fetch head" in out
    assert snapshot(clone) == before


def test_a_path_past_260_characters_exports_and_is_removed(tmp_path, export_area, capsys):
    deep = "/".join(["d" * 50] * 6) + "/f.txt"
    clone, head, _ = scenario(tmp_path, pr_files={deep: "x\n"})
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    assert list(export_area.iterdir()) == []


OWNER_QUEUE_FILE = {"plugins/owner-queue/note.txt": "x\n"}


def stub_claude(monkeypatch, result):
    calls = []
    real = reproof.run

    def fake(cmd, cwd=None, timeout=reproof.TIMEOUT):
        if cmd[0] == "claude":
            calls.append((cmd, cwd))
            return result
        return real(cmd, cwd, timeout)

    monkeypatch.setattr(reproof, "run", fake)
    return calls


def test_no_owner_queue_path_records_no_plugin_test(tmp_path, export_area, monkeypatch, capsys):
    calls = stub_claude(monkeypatch, (1, "", "should not run"))
    clone, head, _ = scenario(tmp_path)
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    assert "RESULT: GREEN" in out
    assert "plugin test" not in out
    assert calls == []


def test_owner_queue_path_and_exit_zero_passes(tmp_path, export_area, monkeypatch, capsys):
    calls = stub_claude(monkeypatch, (0, "ok\n", ""))
    clone, head, _ = scenario(tmp_path, pr_files=OWNER_QUEUE_FILE)
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    assert "PASS  plugin test" in out
    assert "RESULT: GREEN" in out
    assert [c for c, _ in calls] == [["claude", "plugin", "test", "plugins/owner-queue"]]


def test_owner_queue_path_and_exit_one_fails(tmp_path, export_area, monkeypatch, capsys):
    stub_claude(monkeypatch, (1, "", "bad manifest\n"))
    clone, head, _ = scenario(tmp_path, pr_files=OWNER_QUEUE_FILE)
    code, out = reproof_run(clone, head, capsys)
    assert code == 1
    assert "FAIL  plugin test" in out
    assert "bad manifest" in out
    assert "RESULT: NOT GREEN" in out


def test_owner_queue_path_and_claude_missing_fails(tmp_path, export_area, monkeypatch, capsys):
    stub_claude(monkeypatch, (127, "", "[WinError 2] The system cannot find the file"))
    clone, head, _ = scenario(tmp_path, pr_files=OWNER_QUEUE_FILE)
    code, out = reproof_run(clone, head, capsys)
    assert code == 1
    assert "FAIL  plugin test" in out
    assert "SKIP  plugin test" not in out


def test_moving_a_file_out_of_owner_queue_still_runs_the_plugin_test(
    tmp_path, export_area, monkeypatch, capsys
):
    monkeypatch.setitem(BASE, "plugins/owner-queue/src/x.js", "x\n")
    calls = stub_claude(monkeypatch, (0, "", ""))
    clone, head, _ = scenario(
        tmp_path,
        pr_files={"tools/x.js": "x\n"},
        pr_remove=["plugins/owner-queue/src/x.js"],
    )
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    assert "PASS  plugin test" in out
    assert len(calls) == 1


def test_a_non_ascii_owner_queue_name_runs_the_plugin_test(
    tmp_path, export_area, monkeypatch, capsys
):
    calls = stub_claude(monkeypatch, (0, "", ""))
    clone, head, _ = scenario(tmp_path, pr_files={"plugins/owner-queue/é.json": "{}\n"})
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    assert "PASS  plugin test" in out
    assert len(calls) == 1


def test_a_failing_path_diff_runs_the_plugin_test_and_says_why(
    tmp_path, export_area, monkeypatch, capsys
):
    calls = stub_claude(monkeypatch, (0, "", ""))
    real_git = reproof.git

    def fake_git(repo, *args):
        if args[:2] == ("diff", "--quiet"):
            return 128, "", "fatal: boom"
        return real_git(repo, *args)

    monkeypatch.setattr(reproof, "git", fake_git)
    clone, head, _ = scenario(tmp_path)
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    assert "PASS  plugin test" in out
    assert "git diff exited 128, ran as a precaution: fatal: boom" in out
    assert len(calls) == 1


def test_an_export_folder_inside_onedrive_is_refused(tmp_path, monkeypatch, capsys):
    area = tmp_path / "OneDrive" / "tmp"
    area.mkdir(parents=True)
    monkeypatch.setattr(tempfile, "tempdir", str(area))
    clone, head, _ = scenario(tmp_path)
    code, out = reproof_run(clone, head, capsys)
    assert code == 1
    assert "FAIL  export" in out
    assert "inside OneDrive" in out
    assert list(area.iterdir()) == []


LOCK_FILE = reproof.LOCK_NAME

DRIVER = """
import importlib.util, os, sys, time
from pathlib import Path

script, lock_dir, gate, ready, head = sys.argv[1:6]
spec = importlib.util.spec_from_file_location("reproof", script)
reproof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reproof)
reproof.LOCK_DIR = Path(lock_dir)


def stub_fetch(repo, ref):
    tmp = ready + ".tmp"
    Path(tmp).write_text(str(os.getpid()))
    os.replace(tmp, ready)
    deadline = time.time() + 120
    while not Path(gate).exists() and time.time() < deadline:
        time.sleep(0.05)
    return None, "stub"


reproof.fetch_sha = stub_fetch
sys.exit(reproof.main(["1", head], repo=Path(lock_dir)))
"""


def start_run(tmp_path, name, lock_dir, open_gate=False):
    """A real second process running reproof.main, held at its first fetch until its gate opens."""
    driver = tmp_path / "driver.py"
    if not driver.exists():
        driver.write_text(DRIVER, encoding="utf-8")
    gate = tmp_path / f"{name}.gate"
    ready = tmp_path / f"{name}.ready"
    if open_gate:
        gate.write_text("go")
    proc = subprocess.Popen(
        [sys.executable, str(driver), str(SCRIPT), str(lock_dir), str(gate), str(ready), SHA],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    return proc, gate, ready


def wait_for_ready(proc, ready):
    deadline = time.time() + 90
    while not ready.exists():
        assert proc.poll() is None, proc.communicate()[0]
        assert time.time() < deadline, "the run never reached its first fetch"
        time.sleep(0.05)
    return int(ready.read_text())


def record_of(lock_dir):
    return (lock_dir / LOCK_FILE).read_bytes()[: reproof.RECORD]


def assert_lock_is_free(lock_dir):
    fd = reproof.take_lock(lock_dir / LOCK_FILE, reproof.lock_record("1", SHA))
    assert fd is not None, "the lock is still held"
    reproof.release_lock(fd)


def test_the_record_is_512_bytes_of_one_json_line():
    rec = reproof.lock_record("231", SHA)
    assert len(rec) == reproof.RECORD == 512
    assert rec.endswith(b"\n")
    assert rec.count(b"\n") == 1
    data = json.loads(rec)
    assert set(data) == {"v", "project", "pid", "pr", "head", "started"}
    assert data["v"] == 1
    assert data["project"] == "tools"
    assert data["pid"] == os.getpid()
    assert data["pr"] == "231"
    assert data["head"] == SHA
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", data["started"])
    assert reproof.BLANK == b" " * 511 + b"\n"
    assert len(reproof.BLANK) == 512
    assert reproof.HELD == 75


def test_bad_arguments_exit_before_the_lock_folder_is_made(tmp_path, lock_area):
    assert reproof.main(["1"], repo=tmp_path) == 2
    assert not lock_area.exists()


def test_a_free_lock_adds_one_line_and_leaves_a_blank_record(tmp_path, export_area, lock_area, capsys):
    clone, head, _ = scenario(tmp_path)
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    lines = [line for line in out.splitlines() if line.startswith("lock: ")]
    assert len(lines) == 1
    assert str(lock_area / LOCK_FILE) in lines[0]
    assert record_of(lock_area) == reproof.BLANK
    assert_lock_is_free(lock_area)


def test_the_printed_text_is_kept_as_a_result_file_per_pr_and_head(
    tmp_path, export_area, lock_area, capsys
):
    clone, head, _ = scenario(tmp_path)
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    kept = (lock_area / f"result-1-{head[:12]}.txt").read_text(encoding="utf-8")
    assert kept == out
    assert "RESULT: GREEN" in kept


def test_a_failed_result_write_is_ignored(tmp_path, export_area, lock_area, capsys):
    clone, head, _ = scenario(tmp_path)
    lock_area.mkdir()
    (lock_area / f"result-1-{head[:12]}.txt").mkdir()
    code, out = reproof_run(clone, head, capsys)
    assert code == 0, out
    assert "RESULT: GREEN" in out


def test_a_lock_folder_inside_onedrive_is_refused(tmp_path, monkeypatch, capsys):
    area = tmp_path / "OneDrive" / "lock"
    monkeypatch.setattr(reproof, "LOCK_DIR", area)
    code = reproof.main(["1", SHA], repo=tmp_path)
    out = capsys.readouterr().out
    assert code == 1
    assert "inside OneDrive" in out
    assert not area.exists()


def test_the_lock_is_released_when_a_step_raises(tmp_path, lock_area, monkeypatch):
    def boom(repo, ref):
        raise RuntimeError("boom")

    monkeypatch.setattr(reproof, "fetch_sha", boom)
    with pytest.raises(RuntimeError):
        reproof.main(["1", SHA], repo=tmp_path)
    assert record_of(lock_area) == reproof.BLANK
    assert_lock_is_free(lock_area)


def test_the_lock_is_released_when_a_step_times_out(tmp_path, export_area, lock_area, monkeypatch, capsys):
    real = reproof.run

    def fake(cmd, cwd=None, timeout=reproof.TIMEOUT):
        if cmd[1:3] == ["-m", "pytest"]:
            return 124, "", "timed out after 3600s"
        return real(cmd, cwd, timeout)

    monkeypatch.setattr(reproof, "run", fake)
    clone, head, _ = scenario(tmp_path)
    code, out = reproof_run(clone, head, capsys)
    assert code == 1
    assert "timed out after 3600s" in out
    assert record_of(lock_area) == reproof.BLANK
    assert_lock_is_free(lock_area)


def test_two_runs_started_together_one_runs_and_the_other_exits_at_once(tmp_path, lock_area):
    first, gate, ready = start_run(tmp_path, "first", lock_area)
    try:
        holder_pid = wait_for_ready(first, ready)
        second, _, second_ready = start_run(tmp_path, "second", lock_area)
        out, _ = second.communicate(timeout=60)
        assert second.returncode == reproof.HELD == 75, out
        assert "reproof lock held by tools" in out
        assert f"pid {holder_pid}," in out
        assert f"PR 1 head {SHA[:12]}" in out
        assert "since 20" in out
        assert not second_ready.exists()
        assert not (lock_area / f"result-1-{SHA[:12]}.txt").exists()
        assert json.loads(record_of(lock_area))["pid"] == holder_pid
    finally:
        gate.write_text("go")
        first_out, _ = first.communicate(timeout=90)
    assert first.returncode == 1, first_out
    assert "lock: " in first_out
    assert "FAIL  fetch main" in first_out
    assert record_of(lock_area) == reproof.BLANK
    third, _, _ = start_run(tmp_path, "third", lock_area, open_gate=True)
    third_out, _ = third.communicate(timeout=90)
    assert third.returncode == 1, third_out
    assert "lock: " in third_out


def test_a_lock_left_by_a_killed_run_is_taken_by_the_next_run(tmp_path, lock_area):
    first, gate, ready = start_run(tmp_path, "first", lock_area)
    killed_pid = wait_for_ready(first, ready)
    os.kill(killed_pid, getattr(signal, "SIGKILL", signal.SIGTERM))
    first.communicate(timeout=90)
    left = json.loads(record_of(lock_area))
    assert left["pid"] == killed_pid
    deadline = time.time() + 30
    while True:
        try:
            assert_lock_is_free(lock_area)
            break
        except AssertionError:
            assert time.time() < deadline, "the killed run's lock was never freed"
            time.sleep(0.2)
    nxt, nxt_gate, nxt_ready = start_run(tmp_path, "next", lock_area)
    try:
        nxt_pid = wait_for_ready(nxt, nxt_ready)
        assert nxt_pid != killed_pid
        assert json.loads(record_of(lock_area))["pid"] == nxt_pid
    finally:
        nxt_gate.write_text("go")
        out, _ = nxt.communicate(timeout=90)
    assert nxt.returncode == 1, out
    assert "lock: " in out
    assert record_of(lock_area) == reproof.BLANK


def test_a_failed_record_write_gives_up_the_lock_and_fails(tmp_path, lock_area, monkeypatch, capsys):
    real = os.write

    def fake(fd, data):
        if data.startswith(b"{"):
            raise OSError(errno.ENOSPC, "no space left on device")
        return real(fd, data)

    with monkeypatch.context() as patch:
        patch.setattr(reproof.os, "write", fake)
        code = reproof.main(["1", SHA], repo=tmp_path)
    out = capsys.readouterr().out
    assert code == 1
    assert "cannot take the lock" in out
    assert "no space left on device" in out
    assert record_of(lock_area) == reproof.BLANK
    assert_lock_is_free(lock_area)


def test_a_held_lock_with_an_unreadable_record_still_exits_held(tmp_path, lock_area, capsys):
    lock_area.mkdir()
    fd = reproof.take_lock(lock_area / LOCK_FILE, b"x" * 511 + b"\n")
    assert fd is not None
    try:
        code = reproof.main(["1", SHA], repo=tmp_path)
    finally:
        reproof.release_lock(fd)
    out = capsys.readouterr().out
    assert code == reproof.HELD
    assert "not readable" in out
    assert "FAIL" not in out


@pytest.mark.parametrize(
    "name", ["REPROOF_LOCK", "REPROOF_LOCK_DIR", "REPROOF_NO_LOCK", "SKIP_LOCK", "TMPDIR", "TEMP", "TMP"]
)
def test_no_variable_of_the_scripts_own_skips_or_moves_the_lock(name, tmp_path, lock_area, monkeypatch, capsys):
    lock_area.mkdir()
    fd = reproof.take_lock(lock_area / LOCK_FILE, reproof.lock_record("9", SHA))
    assert fd is not None
    monkeypatch.setenv(name, str(tmp_path / "elsewhere"))
    try:
        code = reproof.main(["1", SHA], repo=tmp_path)
    finally:
        reproof.release_lock(fd)
    assert code == reproof.HELD
    assert "PR 9" in capsys.readouterr().out
