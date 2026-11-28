"""Login test: runs the calls #204 lists with the calling window's login and prints one table.

Usage:  python tools/token_check.py <owner>/<repo> [--advisory <GHSA id>] [--stored-git-credential]

Reads (A1 to A9) run against the newest open pull request, or the newest merged
one. Writes (B1 to B9, C2, C4, C5) run on throwaway objects this run makes: an
issue, a label, two branches, one commit and a pull request into the throwaway
base branch, never the default branch. Every name starts with token-test- and a
UTC timestamp, and a `finally` closes or deletes what is left.

The script never reads a token or any environment variable. Its first row is
`gh auth status`, which masks the token. Git calls that reach GitHub take their
credential from `gh` for this window; --stored-git-credential leaves that out.
Output is also scrubbed of token-shaped text, as a second guard.

--boards <login>/<number> adds rows D1 and D2 for the boards-only token (#285):
it reaches that board, holds no repository scope, and is refused a read of the
repository's Actions secrets. Those calls go through tools/board.py, which alone
reads that token from the credential store; without --boards nothing reads it.
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BOARD_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[0-9]{1,6}")
REPO_RE = re.compile(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+")
ADVISORY_RE = re.compile(r"GHSA(-[A-Za-z0-9]{4}){3}")
NUMBER_RE = re.compile(r"/([0-9]+)\s*$")
TOKEN_RE = re.compile(r"(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{8,}")
GIT_CREDENTIAL = ["-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential"]
TIMEOUT = 300
PASS, FAIL = "PASS", "FAIL"
NOT_RUN = "not run"
NOTE = "note"


def scrub(text: str) -> str:
    return TOKEN_RE.sub("***", text)


def run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
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


def repo_arg(text: str) -> str:
    parts = text.split("/")
    if not REPO_RE.fullmatch(text) or any(set(part) == {"."} for part in parts):
        raise argparse.ArgumentTypeError("expected <owner>/<repo> (letters, digits, . _ - only)")
    return text


def advisory_arg(text: str) -> str:
    if not ADVISORY_RE.fullmatch(text):
        raise argparse.ArgumentTypeError("expected an advisory id such as GHSA-xxxx-xxxx-xxxx")
    return text


def board_arg(text: str) -> str:
    if not BOARD_RE.fullmatch(text):
        raise argparse.ArgumentTypeError("expected <login>/<board number>")
    return text


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="token_check.py", description=__doc__.splitlines()[0])
    parser.add_argument("repo", type=repo_arg)
    parser.add_argument("--advisory", type=advisory_arg, default=None)
    parser.add_argument("--stored-git-credential", action="store_true")
    parser.add_argument("--boards", type=board_arg, default=None)
    return parser.parse_args(argv)


def load_board():
    """tools/board.py, loaded only when --boards is given."""
    spec = importlib.util.spec_from_file_location("board", Path(__file__).with_name("board.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def cell(text: str) -> str:
    return scrub(text).replace("|", "\\|").replace("\n", " ")


class Check:
    def __init__(self, repo: str, runner, stamp: str, stored_git: bool, advisory: str | None):
        self.repo = repo
        self.runner = runner
        self.stamp = stamp
        self.stored_git = stored_git
        self.advisory = advisory
        self.rows: list[tuple[str, str, str, str]] = []
        self.base = f"token-test-{stamp}-base"
        self.head = f"token-test-{stamp}-head"
        self.label = f"token-test-{stamp}"
        # What this run made and has not yet removed; cleanup works from these.
        self.issue: str | None = None
        self.pr: str | None = None
        self.label_made = False
        self.branches: list[str] = []

    # ---- one call -------------------------------------------------------

    def step(self, rid: str, argv: list[str], shown: list[str] | None = None,
             ok_if: str | None = None) -> tuple[bool, str]:
        try:
            code, out, err = self.runner(argv)
        except Exception as exc:  # a runner that raises is a failed call, not a crash
            code, out, err = 1, "", f"{type(exc).__name__}: {exc}"
        ok = code == 0
        detail = "" if ok else first_line(err) or first_line(out) or f"exit {code}"
        if not ok and ok_if and ok_if in f"{err}\n{out}":
            # the call worked and the answer is "nothing there", e.g. no check run yet
            ok, detail = True, detail + " (the call was answered)"
        self.rows.append((rid, shlex.join(shown or argv), PASS if ok else FAIL, detail))
        return ok, out

    def skip(self, rid: str, command: str, why: str) -> None:
        self.rows.append((rid, command, NOT_RUN, why))

    def gh(self, rid: str, *args: str) -> tuple[bool, str]:
        return self.step(rid, ["gh", *args])

    def git(self, rid: str, *args: str) -> tuple[bool, str]:
        argv = ["git", *([] if self.stored_git else GIT_CREDENTIAL), *args]
        return self.step(rid, argv, ["git", *args])

    def lookup(self, *args: str) -> str | None:
        """A call whose output later calls need. Only a failure leaves a row."""
        try:
            code, out, err = self.runner(["gh", *args])
        except Exception as exc:
            code, out, err = 1, "", f"{type(exc).__name__}: {exc}"
        if code != 0:
            detail = first_line(err) or first_line(out) or f"exit {code}"
            self.rows.append(("lookup", shlex.join(["gh", *args]), FAIL, detail))
            return None
        return out.strip()

    # ---- reads ----------------------------------------------------------

    def reads(self) -> None:
        r = self.repo
        n = self.lookup("pr", "list", "-R", r, "--state", "open", "--limit", "1",
                        "--json", "number", "--jq", ".[0].number // empty")
        if not n:
            n = self.lookup("pr", "list", "-R", r, "--state", "merged", "--limit", "1",
                            "--json", "number", "--jq", ".[0].number // empty")
        issue = self.lookup("issue", "list", "-R", r, "--state", "all", "--limit", "1",
                            "--json", "number", "--jq", ".[0].number // empty")
        if n:
            self.pr_reads(n)
            self.gh("A4 diff", "pr", "diff", n, "-R", r, "--name-only")
            self.gh("A6 pr", "pr", "view", n, "-R", r, "--json", "state", "--jq", ".state")
            self.gh("A3 pr", "pr", "view", n, "-R", r, "--json", "comments",
                    "--jq", ".comments | length")
        else:
            self.skip("A1-A4, A6", "gh pr view / checks / diff", "no pull request to read")
        if issue:
            self.gh("A3 issue", "issue", "view", issue, "-R", r, "--json", "comments",
                    "--jq", ".comments | length")
            self.gh("A6 issue", "issue", "view", issue, "-R", r, "--json", "state",
                    "--jq", ".state")
        else:
            self.skip("A3, A6 issue", "gh issue view", "no issue to read")
        self.gh("A5 issues", "issue", "list", "-R", r, "--state", "open", "--limit", "3",
                "--json", "number", "--jq", "length")
        self.gh("A5 prs", "pr", "list", "-R", r, "--limit", "3", "--json", "number",
                "--jq", "length")
        self.gh("A7", "api", f"repos/{r}/rulesets", "--jq", "length")
        self.gh("A8", "label", "list", "-R", r, "--limit", "3", "--json", "name",
                "--jq", "length")
        if self.advisory:
            self.gh("A9", "api", f"repos/{r}/security-advisories/{self.advisory}",
                    "--jq", ".state")
        else:
            self.skip("A9", "gh api repos/<repo>/security-advisories/<id>",
                      "not run (no --advisory)")

    def pr_reads(self, n: str, tag: str = "") -> None:
        r = self.repo
        self.gh(f"A1{tag}", "pr", "view", n, "-R", r, "--json", "mergeStateStatus,statusCheckRollup",
                "--jq", "[.mergeStateStatus, (.statusCheckRollup | length)] | @tsv")
        # Right after a pull request opens it has no check run, and gh exits 1 with this text.
        self.step(f"A2{tag}", ["gh", "pr", "checks", n, "-R", r, "--json", "state",
                               "--jq", "length"], ok_if="no checks reported")

    # ---- writes ---------------------------------------------------------

    def writes(self) -> bool:
        """Returns False when a call the rest depends on failed."""
        r = self.repo
        default = self.lookup("repo", "view", r, "--json", "defaultBranchRef",
                              "--jq", ".defaultBranchRef.name")
        sha = default and self.lookup("api", f"repos/{r}/git/ref/heads/{default}",
                                      "--jq", ".object.sha")
        if not default or not sha:
            return False
        # git pushes the sha from this checkout: it must hold that commit, and an
        # origin that is not https tests that transport's key, not the window's login.
        ok, _ = self.step("C4 precheck", ["git", "cat-file", "-e", f"{sha}^{{commit}}"])
        if not ok:
            self.rows[-1] = (*self.rows[-1][:3],
                             "this checkout lacks the default branch head: run git fetch origin first")
            return False
        code, url, _ = self.runner(["git", "remote", "get-url", "origin"])
        if code == 0 and not url.strip().startswith("https://") and not self.stored_git:
            self.rows.append(("C4 note", "git remote get-url origin", NOTE,
                              "origin is not https: git tests that transport's key, not the window's login"))
        for name in (self.base, self.head):
            ok, _ = self.git("C4", "push", "origin", f"{sha}:refs/heads/{name}")
            if not ok:
                return False
            self.branches.append(name)
        content = base64.b64encode(f"token test {self.stamp}\n".encode()).decode()
        ok, _ = self.gh("commit", "api", "-X", "PUT", f"repos/{r}/contents/{self.label}.txt",
                        "-f", f"message={self.label}", "-f", f"content={content}",
                        "-f", f"branch={self.head}")
        if not ok:
            return False

        ok, out = self.gh("B5", "issue", "create", "-R", r, "--title", self.label,
                          "--body", "Throwaway issue from tools/token_check.py.")
        match = NUMBER_RE.search(out)
        if not ok or not match:
            return False
        self.issue = match.group(1)
        self.gh("B6", "issue", "comment", self.issue, "-R", r, "--body", "token test comment")
        self.gh("B7 body", "issue", "edit", self.issue, "-R", r, "--body", "token test, edited")
        ok, _ = self.gh("B9 create", "label", "create", self.label, "-R", r)
        if ok:
            self.label_made = True
            self.gh("B7 add label", "issue", "edit", self.issue, "-R", r, "--add-label", self.label)
            self.gh("B7 remove label", "issue", "edit", self.issue, "-R", r,
                    "--remove-label", self.label)
        ok, _ = self.gh("B8", "issue", "close", self.issue, "-R", r)
        if ok:
            self.issue = None
        if self.label_made:
            ok, _ = self.gh("B9 delete", "label", "delete", self.label, "-R", r, "--yes")
            if ok:
                self.label_made = False

        ok, out = self.gh("B1", "pr", "create", "-R", r, "--base", self.base,
                          "--head", self.head, "--title", self.label,
                          "--body", "Throwaway pull request from tools/token_check.py.")
        match = NUMBER_RE.search(out)
        if not ok or not match:
            return False
        self.pr = pr = match.group(1)
        self.gh("B2", "pr", "comment", pr, "-R", r, "--body", "token test comment")
        self.gh("B3", "pr", "edit", pr, "-R", r, "--body", "token test, edited")
        self.pr_reads(pr, " (throwaway)")
        pin = self.lookup("pr", "view", pr, "-R", r, "--json", "headRefOid", "--jq", ".headRefOid")
        if not pin:
            return False
        ok, _ = self.gh("B4", "pr", "merge", pr, "-R", r, "--squash", "--match-head-commit", pin)
        if not ok:
            return False
        self.pr = None
        self.git("C2", "fetch", "--refmap=", "--no-tags", "--no-recurse-submodules",
                 "origin", f"refs/heads/{self.base}")
        for name in (self.head, self.base):  # one call each: one gone already must not hide the other
            ok, _ = self.git("C5", "push", "origin", "--delete", name)
            if ok and name in self.branches:
                self.branches.remove(name)
        return True

    # ---- cleanup --------------------------------------------------------

    def cleanup(self) -> None:
        r = self.repo
        if self.issue:
            ok, _ = self.gh("cleanup issue", "issue", "close", self.issue, "-R", r)
            self.left(ok, f"issue #{self.issue} may still be open")
        if self.label_made:
            ok, _ = self.gh("cleanup label", "label", "delete", self.label, "-R", r, "--yes")
            self.left(ok, f"label {self.label} may still exist")
        if self.pr:
            ok, _ = self.gh("cleanup pr", "pr", "close", self.pr, "-R", r)
            self.left(ok, f"pull request #{self.pr} may still be open")
        for name in list(self.branches):
            ok, _ = self.git("cleanup branch", "push", "origin", "--delete", name)
            self.left(ok, f"branch {name} may still exist")

    def left(self, ok: bool, what: str) -> None:
        if not ok:
            rid, cmd, status, detail = self.rows[-1]
            self.rows[-1] = (rid, cmd, status, f"{detail} | left: {what}")


def render(repo: str, rows: list[tuple[str, str, str, str]]) -> str:
    lines = [f"Login test of {repo}", "", "| Call | Command | Result | Error |", "|---|---|---|---|"]
    for rid, cmd, status, detail in rows:
        lines.append(f"| {cell(rid)} | `{cell(cmd)}` | {cell(status)} | {cell(detail)} |")
    return "\n".join(lines)


def main(argv: list[str], runner=run, now=None) -> int:
    args = parse_args(argv)
    moment = now() if now else datetime.now(timezone.utc)
    check = Check(args.repo, runner, moment.strftime("%Y%m%dT%H%M%SZ"),
                  args.stored_git_credential, args.advisory)
    check.gh("auth", "auth", "status")
    check.reads()
    try:
        if not check.writes():
            check.skip("writes", "B1-B9, C2, C4, C5", "ended early: a call the rest needs failed")
    finally:
        check.cleanup()
    check.skip("B10", "gh api -X PATCH repos/<repo>/security-advisories/<id>",
               "not run: a write to a real draft advisory")
    if args.boards:
        owner, number = args.boards.split("/")
        try:
            check.rows.extend(load_board().boards_rows(owner, number, args.repo))
        except Exception as exc:
            check.rows.append(("D", "tools/board.py", FAIL, f"{type(exc).__name__}: {exc}"))
    print(render(args.repo, check.rows))
    return 1 if any(row[2] == FAIL for row in check.rows) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
