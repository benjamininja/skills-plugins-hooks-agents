"""tools/token_check.py: the argument check, the throwaway base, cleanup after a
failed call, the error line of a FAIL row, and that no token value is printed.

No network and no GitHub: every call goes to a fake runner.
"""
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "token_check.py"
_spec = importlib.util.spec_from_file_location("token_check", SCRIPT)
token_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(token_check)

REPO = "someone/some-repo"
SHA = "a" * 40
STAMP = "20261124T100000Z"
BASE = f"token-test-{STAMP}-base"
HEAD = f"token-test-{STAMP}-head"


def fixed_now():
    return datetime(2026, 11, 24, 10, 0, 0, tzinfo=timezone.utc)


class Fake:
    """Answers each call from its argument list; `fail` maps a marker to (code, stderr)."""

    def __init__(self, fail=None, leak=None):
        self.calls: list[list[str]] = []
        self.fail = fail or {}
        self.leak = leak

    def __call__(self, argv):
        self.calls.append(list(argv))
        text = " ".join(argv)
        for marker, (code, err) in self.fail.items():
            if marker in text:
                return code, "", err
        if self.leak and argv[:3] == ["gh", "auth", "status"]:
            return 0, f"Token: {self.leak}", ""
        if argv[:3] == ["gh", "pr", "list"]:
            return 0, "7\n", ""
        if argv[:3] == ["gh", "issue", "list"] and "--state" in argv and "all" in argv:
            return 0, "3\n", ""
        if argv[:3] == ["gh", "repo", "view"]:
            return 0, "main\n", ""
        if "git/ref/heads/main" in text:
            return 0, SHA + "\n", ""
        if argv[:3] == ["gh", "issue", "create"]:
            return 0, f"https://github.com/{REPO}/issues/41\n", ""
        if argv[:3] == ["gh", "pr", "create"]:
            return 0, f"https://github.com/{REPO}/pull/42\n", ""
        if "headRefOid" in text:
            return 0, "b" * 40 + "\n", ""
        return 0, "1\n", ""

    def has(self, *words):
        return [c for c in self.calls if all(w in c for w in words)]


def run_main(fake, *extra):
    import io
    from contextlib import redirect_stdout

    out = io.StringIO()
    with redirect_stdout(out):
        code = token_check.main([REPO, *extra], runner=fake, now=fixed_now)
    return code, out.getvalue()


@pytest.mark.parametrize(
    "arg",
    ["", "repo", "a/b/c", "a b/c", "a/b;rm", "a/b$(x)", "../x", "a/..", "/b", "a/", "a/b\n"],
)
def test_bad_repository_argument_is_refused_before_any_call(arg):
    fake = Fake()
    with pytest.raises(SystemExit) as exc:
        token_check.main([arg], runner=fake, now=fixed_now)
    assert exc.value.code == 2
    assert fake.calls == []


def test_missing_and_extra_arguments_are_refused():
    for argv in ([], [REPO, "extra"], [REPO, "--advisory", "nope"], [REPO, "--token", "x"]):
        fake = Fake()
        with pytest.raises(SystemExit):
            token_check.main(argv, runner=fake, now=fixed_now)
        assert fake.calls == []


def test_first_row_is_auth_status_and_a_clean_run_passes():
    fake = Fake()
    code, out = run_main(fake)
    assert code == 0
    rows = [line for line in out.splitlines() if line.startswith("| ")]
    assert rows[1].startswith("| auth |") and "gh auth status" in rows[1]
    assert "FAIL" not in out
    assert "B10" in out and "not run: a write to a real draft advisory" in out
    assert "not run (no --advisory)" in out


def test_advisory_is_read_when_given():
    fake = Fake()
    run_main(fake, "--advisory", "GHSA-abcd-1234-wxyz")
    assert fake.has("api", f"repos/{REPO}/security-advisories/GHSA-abcd-1234-wxyz")


def test_pull_request_base_is_the_throwaway_branch_never_the_default():
    fake = Fake()
    run_main(fake)
    (create,) = fake.has("gh", "pr", "create")
    assert create[create.index("--base") + 1] == BASE
    assert create[create.index("--head") + 1] == HEAD
    assert "main" not in create
    # the merge is pinned to the head it read, and goes to the throwaway base
    (merge,) = fake.has("gh", "pr", "merge")
    assert "--match-head-commit" in merge and "--squash" in merge
    # branches are made from the default branch's head and removed at the end
    pushes = [c for c in fake.calls if c[0] == "git" and "push" in c]
    assert [f"{SHA}:refs/heads/{BASE}"] == [a for a in pushes[0] if a.startswith(SHA)]
    assert pushes[-1][-3:] == ["--delete", HEAD, BASE]


def test_every_name_made_starts_with_token_test_and_the_timestamp():
    fake = Fake()
    run_main(fake)
    (issue,) = fake.has("gh", "issue", "create")
    assert issue[issue.index("--title") + 1] == f"token-test-{STAMP}"
    (label,) = fake.has("gh", "label", "create")
    assert label[3] == f"token-test-{STAMP}"
    # only the issue and the pull request this run made are touched
    for c in fake.has("gh", "issue", "close") + fake.has("gh", "pr", "merge"):
        assert c[3] in ("41", "42")


def test_git_calls_take_the_credential_from_gh_unless_told_otherwise():
    fake = Fake()
    run_main(fake)
    git_calls = [c for c in fake.calls if c[0] == "git"]
    assert git_calls
    for c in git_calls:
        assert c[1:5] == ["-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential"]
    fake2 = Fake()
    run_main(fake2, "--stored-git-credential")
    for c in (c for c in fake2.calls if c[0] == "git"):
        assert "credential.helper=" not in c


def test_calls_are_argument_lists_never_shell_strings():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "shell=True" not in source
    fake = Fake()
    run_main(fake)
    assert all(isinstance(c, list) and all(isinstance(a, str) for a in c) for c in fake.calls)


def test_cleanup_runs_after_a_failed_call():
    # the pull request cannot be opened: the issue and both branches are already made
    fake = Fake(fail={"gh pr create": (1, "GraphQL: Resource not accessible\nsecond line")})
    code, out = run_main(fake)
    assert code == 1
    assert fake.has("gh", "pr", "create")
    # nothing after the failure that needs a pull request ran
    assert not fake.has("gh", "pr", "merge")
    # and the branches this run pushed are deleted, last
    assert fake.calls[-1][0] == "git"
    assert fake.calls[-1][-3:] == ["--delete", BASE, HEAD] or fake.calls[-1][-3:] == ["--delete", HEAD, BASE]
    assert "ended early" in out


def test_cleanup_closes_what_is_still_open_after_a_failed_close_and_merge():
    fake = Fake(fail={"gh issue close 41": (1, "boom")})
    # the first close fails; cleanup tries once more and names what is left
    code, out = run_main(fake)
    closes = fake.has("gh", "issue", "close")
    assert len(closes) == 2
    assert "left: issue #41 may still be open" in out
    assert code == 1


def test_a_failed_merge_leaves_the_pr_to_cleanup():
    fake = Fake(fail={"gh pr merge": (1, "merge refused")})
    code, out = run_main(fake)
    assert fake.has("gh", "pr", "close", "42")
    assert fake.calls[-1][0] == "git" and "--delete" in fake.calls[-1]
    assert code == 1


def test_runner_that_raises_is_a_failed_call_and_cleanup_still_runs():
    class Boom(Fake):
        def __call__(self, argv):
            if argv[:3] == ["gh", "pr", "create"]:
                self.calls.append(list(argv))
                raise RuntimeError("network gone")
            return super().__call__(argv)

    fake = Boom()
    code, out = run_main(fake)
    assert code == 1
    assert "RuntimeError: network gone" in out
    assert fake.calls[-1][0] == "git" and "--delete" in fake.calls[-1]


def test_fail_row_carries_the_first_error_line_only():
    fake = Fake(fail={"api repos/someone/some-repo/rulesets": (1, "\n  HTTP 403: forbidden\nsecond line\n")})
    code, out = run_main(fake)
    (row,) = [l for l in out.splitlines() if l.startswith("| A7 ")]
    assert row.endswith("| FAIL | HTTP 403: forbidden |")
    assert "second line" not in out
    assert code == 1


def test_no_row_and_no_output_holds_a_gh_token_value(monkeypatch, capsys):
    secret = "ghp_" + "Zx9" * 12
    monkeypatch.setenv("GH_TOKEN", secret)
    # the fake leaks the value in a success body and in an error line
    fake = Fake(fail={"label list": (1, f"bad credentials for {secret}")}, leak=secret)
    code, out = run_main(fake)
    captured = capsys.readouterr()
    assert secret not in out + captured.out + captured.err
    assert "***" in out
    # nothing in a call carries it either
    assert all(secret not in " ".join(c) for c in fake.calls)
    # and the script reads no environment variable at all
    source = SCRIPT.read_text(encoding="utf-8")
    assert "os.environ" not in source and "getenv" not in source
    assert "GITHUB_TOKEN" not in source and "GH_TOKEN" not in source


def test_the_argument_parser_takes_no_token():
    with pytest.raises(SystemExit):
        token_check.main([REPO, "--token", "x"], runner=Fake(), now=fixed_now)
