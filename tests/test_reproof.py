"""tools/reproof.py: the argument check, the summary's exit code, and that the
repository it runs in gains objects and FETCH_HEAD, never a ref or a file.

No network and no real PR: origin is a local bare repository and the PR head
is a ref made by hand under refs/pull/1/head.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
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


def scenario(tmp_path, pr_files=None, main_files=None):
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
