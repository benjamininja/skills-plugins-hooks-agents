"""Re-proof of a tools PR: the Green items of PROJECT-RULES that a script can run.

Usage:  python tools/reproof.py <pr number> <40-character lowercase head sha>

Run it from the live clone (merged main, never edited by hand), with the
interpreter the permission rule names: the steps run with that same
interpreter (sys.executable), and it must have pytest.

  1. fetch origin's main and the PR head into FETCH_HEAD, one at a time; the
     head must equal the sha given
  2. git merge-tree the head onto main (a conflict fails)
  3. export the merged tree to a temp folder outside OneDrive
  4. in the export: pytest -q tests, tools/build_catalog.py, and a check that
     the build left CATALOG.md as committed
  5. remove the export, print one summary, exit non-zero if any step failed

The repository it runs in gains objects and FETCH_HEAD, never a ref, a branch
or a working-tree file. CI's read and the check-in-hygiene report are not run.
"""

from __future__ import annotations

import difflib
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PR_RE = re.compile(r"[1-9][0-9]{0,8}")
SHA_RE = re.compile(r"[0-9a-f]{40}")
GIT_OPTS = ["-c", "gc.auto=0", "-c", "maintenance.auto=false", "-c", "core.autocrlf=false"]
TIMEOUT = 1800
PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


def parse_args(argv: list[str]) -> tuple[str, str] | None:
    if len(argv) != 2:
        return None
    pr, head = argv
    if PR_RE.fullmatch(pr) and SHA_RE.fullmatch(head):
        return pr, head
    return None


def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {TIMEOUT}s"
    except OSError as exc:
        return 127, "", str(exc)
    return p.returncode, p.stdout, p.stderr


def git(repo: Path, *args: str) -> tuple[int, str, str]:
    return run(["git", "-C", str(repo), *GIT_OPTS, *args])


def long_path(path: Path | str) -> str:
    text = str(path)
    if sys.platform == "win32" and not text.startswith("\\\\?\\"):
        return "\\\\?\\" + text
    return text


def tail(text: str, count: int) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines[-count:])


def fetch_sha(repo: Path, ref: str) -> tuple[str | None, str]:
    code, _, err = git(
        repo, "fetch", "--refmap=", "--no-tags", "--no-recurse-submodules", "origin", ref
    )
    if code != 0:
        return None, tail(err, 5) or f"git fetch exited {code}"
    code, out, err = git(repo, "rev-parse", "--verify", "FETCH_HEAD")
    sha = out.strip()
    if code != 0 or not SHA_RE.fullmatch(sha):
        return None, tail(err, 5) or "FETCH_HEAD is not a commit"
    return sha, ""


def export_tree(repo: Path, tree: str, work: Path) -> tuple[Path | None, str]:
    archive = work / "tree.tar"
    code, _, err = git(repo, "archive", "--format=tar", "-o", str(archive), tree)
    if code != 0:
        return None, tail(err, 5) or f"git archive exited {code}"
    dest = work / "x"
    dest.mkdir()
    with tarfile.open(archive) as tf:
        try:
            tf.extractall(long_path(dest), filter="data")
        except TypeError:
            tf.extractall(long_path(dest))
    return dest, ""


def show(name: str, status: str, text: str) -> None:
    print(f"== {name}: {status}")
    if text:
        print(text)


def check_catalog(dest: Path, before: bytes | None, build_ok: bool) -> tuple[str, str]:
    if not build_ok:
        return SKIP, "build_catalog did not pass"
    catalog = dest / "CATALOG.md"
    if before is None or not catalog.exists():
        return FAIL, "CATALOG.md is missing from the merged tree"
    after = catalog.read_bytes()
    if after == before:
        return PASS, ""
    diff = difflib.unified_diff(
        before.decode("utf-8", "replace").splitlines(),
        after.decode("utf-8", "replace").splitlines(),
        "CATALOG.md (committed)",
        "CATALOG.md (rebuilt)",
        lineterm="",
        n=1,
    )
    lines = list(diff)[:40]
    return FAIL, "\n".join(lines) if lines else "CATALOG.md differs in line endings only"


def main(argv: list[str], repo: Path = ROOT) -> int:
    parsed = parse_args(argv)
    if parsed is None:
        print(
            "usage: reproof.py <pr number> <40-character lowercase head sha>",
            file=sys.stderr,
        )
        return 2
    pr, head = parsed
    results: list[tuple[str, str]] = []

    def record(name: str, status: str, text: str = "") -> bool:
        results.append((name, status))
        show(name, status, text)
        return status == PASS

    def finish() -> int:
        print("== summary")
        for name, status in results:
            print(f"{status:<5} {name}")
        green = all(status == PASS for _, status in results)
        print("RESULT: " + ("GREEN" if green else "NOT GREEN"))
        return 0 if green else 1

    base, err = fetch_sha(repo, "refs/heads/main")
    if not record("fetch main", PASS if base else FAIL, f"main={base[:12]}" if base else err):
        return finish()

    fetched, err = fetch_sha(repo, f"refs/pull/{pr}/head")
    if fetched is None:
        record("fetch head", FAIL, err)
        return finish()
    if fetched != head:
        record("fetch head", FAIL, f"PR {pr} head is {fetched[:12]}, not {head[:12]}")
        return finish()
    record("fetch head", PASS, f"head={head[:12]}")

    code, out, err = git(repo, "merge-tree", "--write-tree", base, head)
    tree = out.splitlines()[0].strip() if out.strip() else ""
    if code != 0 or not SHA_RE.fullmatch(tree):
        record("merge", FAIL, "merge conflict" if code == 1 else tail(err, 5))
        return finish()
    record("merge", PASS, f"tree={tree[:12]}")

    work = Path(tempfile.mkdtemp(prefix="rp-")).resolve()
    try:
        if "onedrive" in str(work).lower():
            record("export", FAIL, f"temp folder {work} is inside OneDrive")
            return finish()
        dest, err = export_tree(repo, tree, work)
        if dest is None:
            record("export", FAIL, err)
            return finish()
        record("export", PASS)

        catalog = dest / "CATALOG.md"
        before = catalog.read_bytes() if catalog.exists() else None

        code, out, err = run([sys.executable, "-m", "pytest", "-q", "tests"], str(dest))
        text = out + err
        record("pytest", PASS if code == 0 else FAIL, tail(text, 3 if code == 0 else 40))

        code, out, err = run([sys.executable, "tools/build_catalog.py"], str(dest))
        text = out + err
        build_ok = record(
            "build_catalog", PASS if code == 0 else FAIL, tail(text, 2 if code == 0 else 40)
        )

        status, text = check_catalog(dest, before, build_ok)
        record("catalog diff", status, text)
    finally:
        shutil.rmtree(long_path(work), ignore_errors=True)
        print("export removed" if not work.exists() else f"export NOT removed: {work}")
    return finish()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
