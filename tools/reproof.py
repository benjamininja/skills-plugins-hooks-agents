"""Re-proof of a tools PR: the Green items of PROJECT-RULES that a script can run.

Usage:  python tools/reproof.py <pr number> <40-character lowercase head sha>

Run it from the live clone (merged main, never edited by hand), with the
interpreter the permission rule names: the steps run with that same
interpreter (sys.executable), and it must have pytest.

  0. take the machine's one re-proof lock (~/.claude-reproof/reproof.lock,
     #231; the home folder is the account's, USERPROFILE on Windows and HOME
     elsewhere, so a run whose home variable was changed takes a different
     lock; the script has no option, argument or variable of its own that
     skips or moves it) before anything else; if another run holds it, start nothing,
     print who holds it and exit 75. The operating system frees the lock
     when its process ends, so a killed run never leaves a stale one. A
     killed run's pytest child may still be running after its lock is free.
  1. fetch origin's main and the PR head into FETCH_HEAD, one at a time; the
     head must equal the sha given
  2. git merge-tree the head onto main (a conflict fails)
  3. export the merged tree to a temp folder outside OneDrive
  4. in the export: pytest -q tests, tools/build_catalog.py, and a check that
     the build left CATALOG.md as committed
     then, only if the merge changes a path under plugins/owner-queue/:
     claude plugin test plugins/owner-queue
  5. remove the export, print one summary, exit non-zero if any step failed
     (the printed text is also kept as result-<pr>-<head12>.txt beside the lock)

The repository it runs in gains objects and FETCH_HEAD, never a ref, a branch
or a working-tree file. CI's read and the check-in-hygiene report are not run.

Exit codes: 0 green, 1 not green, 2 bad arguments, 75 the lock is held.
"""

from __future__ import annotations

import contextlib
import datetime
import difflib
import errno
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROJECT = "tools"
LOCK_DIR = Path.home() / ".claude-reproof"
LOCK_NAME = "reproof.lock"
HELD = 75
RECORD = 512
LOCK_AT = 4096
BLANK = b" " * (RECORD - 1) + b"\n"
HELD_ERRNOS = {errno.EACCES, errno.EAGAIN, errno.EWOULDBLOCK, errno.EDEADLK}

PR_RE = re.compile(r"[1-9][0-9]{0,8}")
SHA_RE = re.compile(r"[0-9a-f]{40}")
GIT_OPTS = ["-c", "gc.auto=0", "-c", "maintenance.auto=false", "-c", "core.autocrlf=false"]
TIMEOUT = 3600
PLUGIN_DIR = "plugins/owner-queue"
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


def remove_tree(path: Path) -> None:
    for folder, _, names in os.walk(long_path(path)):
        for name in names:
            try:
                os.chmod(os.path.join(folder, name), stat.S_IWRITE)
            except OSError:
                pass
    shutil.rmtree(long_path(path), ignore_errors=True)


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


def show(name: str, status: str, text: str, elapsed: float = 0.0) -> None:
    print(f"== {name}: {status} ({elapsed:.1f}s)")
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


def lock_record(pr: str, head: str) -> bytes:
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = json.dumps(
        {"v": 1, "project": PROJECT, "pid": os.getpid(), "pr": pr, "head": head, "started": started},
        separators=(",", ":"),
    )
    return body.encode("ascii").ljust(RECORD - 1, b" ") + b"\n"


def take_lock(path: Path, record: bytes) -> int | None:
    fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0), 0o600)
    try:
        if os.name == "nt":
            import msvcrt

            os.lseek(fd, LOCK_AT, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        os.close(fd)
        if exc.errno in HELD_ERRNOS:
            return None
        raise
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        if os.write(fd, record) != len(record):
            raise OSError(errno.EIO, "short write of the lock record")
    except OSError:
        release_lock(fd)
        raise
    return fd


def release_lock(fd: int) -> None:
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        os.write(fd, BLANK)
        if os.name == "nt":
            import msvcrt

            os.lseek(fd, LOCK_AT, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    except OSError:
        pass
    finally:
        os.close(fd)


def read_holder(path: Path) -> dict | None:
    try:
        with open(path, "rb", buffering=0) as f:
            raw = f.read(RECORD)
        holder = json.loads(raw)
    except (OSError, ValueError):
        return None
    return holder if isinstance(holder, dict) else None


def describe_holder(holder: dict | None) -> str:
    if holder is None:
        return "reproof lock held; the holder's record is not readable yet"
    def field(key: str) -> str:
        return str(holder.get(key, "?"))[:60]
    return (
        f"reproof lock held by {field('project')}, pid {field('pid')}, "
        f"PR {field('pr')} head {field('head')[:12]}, since {field('started')}"
    )


class Tee:
    def __init__(self, out) -> None:
        self.out = out
        self.parts: list[str] = []

    def write(self, text: str) -> int:
        self.parts.append(text)
        return self.out.write(text)

    def flush(self) -> None:
        self.out.flush()

    def text(self) -> str:
        return "".join(self.parts)


def save_result(folder: Path, pr: str, head: str, text: str) -> None:
    try:
        (folder / f"result-{pr}-{head[:12]}.txt").write_text(text, encoding="utf-8", errors="replace")
    except OSError:
        pass


def main(argv: list[str], repo: Path = ROOT) -> int:
    parsed = parse_args(argv)
    if parsed is None:
        print(
            "usage: reproof.py <pr number> <40-character lowercase head sha>",
            file=sys.stderr,
        )
        return 2
    pr, head = parsed
    folder = LOCK_DIR
    if "onedrive" in str(folder.resolve()).lower():
        print(f"== lock: FAIL\nlock folder {folder} is inside OneDrive")
        return 1
    path = folder / LOCK_NAME
    try:
        folder.mkdir(parents=True, exist_ok=True)
        fd = take_lock(path, lock_record(pr, head))
    except OSError as exc:
        print(f"== lock: FAIL\ncannot take the lock at {path}: {exc}")
        return 1
    if fd is None:
        print(describe_holder(read_holder(path)))
        return HELD
    tee = Tee(sys.stdout)
    try:
        with contextlib.redirect_stdout(tee):
            print(f"lock: {path} taken by {PROJECT}, pid {os.getpid()}")
            return run_steps(pr, head, repo)
    finally:
        save_result(folder, pr, head, tee.text())
        release_lock(fd)


def run_steps(pr: str, head: str, repo: Path) -> int:
    results: list[tuple[str, str, float]] = []
    mark = time.monotonic()

    def record(name: str, status: str, text: str = "") -> bool:
        nonlocal mark
        now = time.monotonic()
        elapsed = now - mark
        mark = now
        results.append((name, status, elapsed))
        show(name, status, text, elapsed)
        return status == PASS

    def finish() -> int:
        print("== summary")
        for name, status, elapsed in results:
            print(f"{status:<5} {name} {elapsed:.1f}s")
        green = all(status == PASS for _, status, _ in results)
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

    code, _, err = git(repo, "diff", "--quiet", base, tree, "--", PLUGIN_DIR)
    plugin_changed = code != 0
    plugin_note = ""
    if code not in (0, 1):
        plugin_note = f"git diff exited {code}, ran as a precaution: {tail(err, 3)}\n"

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

        for step in (("init", "-q"), ("add", "-A")):
            code, _, err = git(dest, "-c", "core.longpaths=true", *step)
            if code != 0:
                record("index", FAIL, tail(err, 5) or f"git {step[0]} exited {code}")
                return finish()
        record("index", PASS)

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

        if plugin_changed:
            code, out, err = run(["claude", "plugin", "test", PLUGIN_DIR], str(dest))
            text = out + err
            record(
                "plugin test",
                PASS if code == 0 else FAIL,
                plugin_note + tail(text, 3 if code == 0 else 40),
            )
    finally:
        remove_tree(work)
        print("export removed" if not work.exists() else f"export NOT removed: {work}")
    return finish()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
