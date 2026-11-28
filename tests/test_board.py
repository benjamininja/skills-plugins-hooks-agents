"""tools/board.py: the one route to a Projects board (#285).

No test needs the real token and none reaches GitHub: the credential-store read
and every child process go to fakes. The one real call is a Windows read of an
entry that does not exist, which proves the CredReadW path without a secret.
"""
import importlib.util
import io
import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "board.py"
_spec = importlib.util.spec_from_file_location("board", SCRIPT)
board = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(board)

# Not token-shaped: only the exact-value scrub can catch it.
SECRET = "plain-secret-value-0451"
# Token-shaped: the pattern scrub catches it where the value is not known.
SHAPED = "ghp_" + "Qw7" * 12
OWNER, NUMBER = "someone", "3"
ITEM, FIELD = "PVTI_lADOabc123", "PVTSSF_lADOabc123"
URL = "https://github.com/someone/some-repo/issues/12"
PROJECT_ID = "PVT_kwHOabc123"

ACTIONS = [
    ["items", OWNER, NUMBER],
    ["items", OWNER, NUMBER, "--limit", "5"],
    ["fields", OWNER, NUMBER],
    ["views", OWNER, NUMBER],
    ["views", "@me", NUMBER],
    ["add", OWNER, NUMBER, URL],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--text", "hello"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "2.5"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--date", "2026-12-01"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--option", "f75ad846"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--iteration", "abc123"],
]


class Fake:
    """A child-process runner: records (argv, token) and answers from the argv."""

    def __init__(self, code=0, out="", err="", leak=None, raises=None):
        self.calls: list[tuple[list[str], str]] = []
        self.code, self.out, self.err = code, out, err
        self.leak = leak
        self.raises = raises

    def __call__(self, argv, token):
        self.calls.append((list(argv), token))
        if self.raises:
            raise self.raises
        if argv == board.LOGIN_CALL:
            return 0, OWNER + "\n", ""
        if argv[:3] == ["gh", "project", "view"] and ".id" in argv:
            return 0, PROJECT_ID + "\n", ""
        out, err = self.out, self.err
        if self.leak:
            out = f"{out}token={self.leak} header Authorization: token {self.leak}\n"
            err = f"{err}error near {self.leak}\n"
        return self.code, out, err


def reader(value=SECRET):
    def read(entry):
        assert entry == board.ENTRY
        return value
    return read


def never_read(entry):
    raise AssertionError("the store was read")


# ---- arguments --------------------------------------------------------------


@pytest.mark.parametrize("argv", [
    [],
    ["items"],
    ["items", "bad owner", NUMBER],
    ["items", "-x", NUMBER],
    ["items", OWNER, "three"],
    ["items", OWNER, NUMBER, "--limit", "0"],
    ["items", OWNER, NUMBER, "--limit", "5000"],
    ["add", OWNER, NUMBER, "https://example.com/a/b/issues/1"],
    ["add", OWNER, NUMBER, URL + ";rm"],
    ["set", OWNER, NUMBER, "--item", "nope", "--field", FIELD, "--text", "x"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", "nope", "--text", "x"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--text", "x", "--date", "2026-01-01"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--date", "tomorrow"],
    ["delete", OWNER, NUMBER],
    ["items", OWNER, NUMBER, "--token", "x"],
])
def test_bad_arguments_stop_before_the_store_and_any_call(argv):
    fake = Fake()
    with pytest.raises(SystemExit) as exc:
        board.main(argv, runner=fake, read=never_read)
    assert exc.value.code == 2
    assert fake.calls == []


def test_only_the_five_actions_exist():
    parser_actions = {"items", "fields", "views", "add", "set"}
    for action in parser_actions:
        with pytest.raises(SystemExit) as exc:
            board.parse_args([action, "--help"])
        assert exc.value.code == 0
    for other in ("delete", "archive", "create", "copy", "close", "api", "edit"):
        with pytest.raises(SystemExit) as exc:
            board.parse_args([other, OWNER, NUMBER])
        assert exc.value.code == 2


# ---- the calls made ---------------------------------------------------------


def test_each_action_makes_its_gh_call_with_the_token():
    expected = {
        "items": ["gh", "project", "item-list", NUMBER, "--owner", "@me", "--format", "json",
                  "--limit", "100"],
        "fields": ["gh", "project", "field-list", NUMBER, "--owner", "@me", "--format", "json"],
        "add": ["gh", "project", "item-add", NUMBER, "--owner", "@me", "--url", URL,
                "--format", "json"],
    }
    for action, argv in expected.items():
        fake = Fake(out="{}\n")
        args = [action, OWNER, NUMBER] + ([URL] if action == "add" else [])
        assert board.main(args, runner=fake, read=reader()) == 0
        assert fake.calls == [(board.LOGIN_CALL, SECRET), (argv, SECRET)]


def test_views_is_one_fixed_graphql_read():
    fake = Fake(out="{}\n")
    board.main(["views", OWNER, NUMBER], runner=fake, read=reader())
    ((argv, _),) = fake.calls
    assert argv[:3] == ["gh", "api", "graphql"]
    assert f"query={board.VIEWS_QUERY}" in argv and f"login={OWNER}" in argv
    assert "mutation" not in board.VIEWS_QUERY and "mutation" not in board.VIEWS_QUERY_ME
    fake = Fake(out="{}\n")
    board.main(["views", "@me", NUMBER], runner=fake, read=reader())
    ((argv, _),) = fake.calls
    assert f"query={board.VIEWS_QUERY_ME}" in argv and not any(a.startswith("login=") for a in argv)


@pytest.mark.parametrize("flag,value,expected", [
    ("--text", "-starts-with-a-dash", "--text=-starts-with-a-dash"),
    ("--number", "-3", "--number=-3"),
    ("--date", "2026-12-01", "--date=2026-12-01"),
    ("--option", "f75ad846", "--single-select-option-id=f75ad846"),
    ("--iteration", "abc123", "--iteration-id=abc123"),
])
def test_set_reads_the_board_id_then_edits_one_field(flag, value, expected):
    fake = Fake()
    code = board.main(["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, f"{flag}={value}"],
                      runner=fake, read=reader())
    assert code == 0
    (login, _), (lookup, _), (edit, token) = fake.calls
    assert login == board.LOGIN_CALL
    assert lookup[:4] == ["gh", "project", "view", NUMBER] and ".id" in lookup
    assert lookup[4:6] == ["--owner", "@me"]
    assert edit == ["gh", "project", "item-edit", "--id", ITEM, "--project-id", PROJECT_ID,
                    "--field-id", FIELD, expected]
    assert token == SECRET


def test_set_stops_when_the_board_id_is_not_found():
    class NoBoard(Fake):
        def __call__(self, argv, token):
            self.calls.append((list(argv), token))
            if argv == board.LOGIN_CALL:
                return 0, OWNER + "\n", ""
            return 1, "", "Could not resolve to a ProjectV2"

    fake = NoBoard()
    code = board.main(["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--text", "x"],
                      runner=fake, read=reader())
    assert code == 1
    assert len(fake.calls) == 2


PROJECT_ACTIONS = [a for a in ACTIONS if a[0] != "views"]


@pytest.mark.parametrize("argv", PROJECT_ACTIONS)
def test_every_project_call_goes_as_at_me_after_the_login_check(argv):
    fake = Fake()
    assert board.main(argv, runner=fake, read=reader()) == 0
    assert fake.calls[0] == (board.LOGIN_CALL, SECRET)
    for call, _ in fake.calls[1:]:
        assert call[:2] == ["gh", "project"]
        assert OWNER not in call
        if "--owner" in call:
            assert call[call.index("--owner") + 1] == "@me"
    assert sum(call == board.LOGIN_CALL for call, _ in fake.calls) == 1


class OtherLogin(Fake):
    def __init__(self, login="someone-else", code=0, err=""):
        super().__init__()
        self.login, self.login_code, self.login_err = login, code, err

    def __call__(self, argv, token):
        if argv == board.LOGIN_CALL:
            self.calls.append((list(argv), token))
            return self.login_code, self.login + "\n", self.login_err
        return super().__call__(argv, token)


@pytest.mark.parametrize("argv", PROJECT_ACTIONS)
def test_another_owner_stops_with_exit_2_before_any_project_call(argv, capsys):
    fake = OtherLogin()
    assert board.main(argv, runner=fake, read=reader()) == 2
    assert [call for call, _ in fake.calls] == [board.LOGIN_CALL]
    err = capsys.readouterr().err
    assert "boards of another owner are not supported" in err
    assert "someone-else" not in err


def test_a_failed_login_read_stops_before_any_project_call(capsys):
    fake = OtherLogin(login="", code=1, err=f"HTTP 401 near {SECRET}\n")
    assert board.main(["items", OWNER, NUMBER], runner=fake, read=reader()) == 1
    assert [call for call, _ in fake.calls] == [board.LOGIN_CALL]
    assert SECRET not in capsys.readouterr().err


def test_the_login_is_compared_without_case():
    fake = OtherLogin(login=OWNER.upper())
    assert board.main(["items", OWNER, NUMBER], runner=fake, read=reader()) == 0


def test_at_me_skips_the_login_read():
    fake = Fake()
    assert board.main(["items", "@me", NUMBER], runner=fake, read=reader()) == 0
    assert [call[:3] for call, _ in fake.calls] == [["gh", "project", "item-list"]]


def test_views_makes_no_login_read():
    fake = OtherLogin()
    board.main(["views", OWNER, NUMBER], runner=fake, read=reader())
    assert board.LOGIN_CALL not in [call for call, _ in fake.calls]


def test_calls_are_argument_lists_never_shell_strings():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "shell=True" not in source and "os.system" not in source
    for argv in ACTIONS:
        fake = Fake()
        board.main(argv, runner=fake, read=reader())
        for call, _ in fake.calls:
            assert isinstance(call, list) and all(isinstance(a, str) for a in call)
            assert SECRET not in " ".join(call)


def test_the_child_exit_code_is_the_script_exit_code():
    assert board.main(["items", OWNER, NUMBER], runner=Fake(code=4, err="boom"), read=reader()) == 4


# ---- no output path holds the token ------------------------------------------


@pytest.mark.parametrize("argv", ACTIONS)
@pytest.mark.parametrize("code", [0, 1])
def test_no_output_holds_the_token_on_success_or_error(argv, code, capsys):
    fake = Fake(code=code, out="result\n", err="note\n", leak=SECRET)
    board.main(argv, runner=fake, read=reader())
    captured = capsys.readouterr()
    assert SECRET not in captured.out + captured.err
    assert "***" in captured.out + captured.err


@pytest.mark.parametrize("argv", ACTIONS)
def test_a_runner_that_raises_with_the_token_prints_it_scrubbed(argv, capsys):
    fake = Fake(raises=RuntimeError(f"connection reset, token {SECRET}"))
    code = board.main(argv, runner=fake, read=reader())
    captured = capsys.readouterr()
    assert code == 1
    assert SECRET not in captured.out + captured.err
    assert "RuntimeError" in captured.err


def test_a_store_error_is_exit_2_and_names_the_entry_only(capsys):
    def broken(entry):
        raise board.StoreError(f"no entry named {entry}; stray {SHAPED}")

    fake = Fake()
    code = board.main(["items", OWNER, NUMBER], runner=fake, read=broken)
    captured = capsys.readouterr()
    assert code == 2
    assert fake.calls == []
    assert board.ENTRY in captured.err
    assert SHAPED not in captured.out + captured.err


def test_token_shaped_text_is_scrubbed_even_when_it_is_not_the_value(capsys):
    fake = Fake(out=f"other login {SHAPED}\n")
    board.main(["items", OWNER, NUMBER], runner=fake, read=reader())
    assert SHAPED not in capsys.readouterr().out


@pytest.mark.parametrize("action", ["items", "fields"])
def test_board_text_outside_cp1252_prints_through_a_cp1252_pipe(action, monkeypatch):
    # #307: a piped stdout on Windows encodes as cp1252 unless the script says otherwise
    title = "Board \U0001F680 todo → done"
    out = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    err = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    fake = Fake(out=f'{{"title": "{title}"}}\n', err=f"note {title}\n")
    assert board.main([action, OWNER, NUMBER], runner=fake, read=reader()) == 0
    out.flush()
    err.flush()
    assert title in out.buffer.getvalue().decode("utf-8")
    assert title in err.buffer.getvalue().decode("utf-8")


def test_every_print_in_the_script_goes_through_scrub():
    # the four places that print: the store error, the other error, stdout, stderr
    source = SCRIPT.read_text(encoding="utf-8")
    writes = [line.strip() for line in source.splitlines()
              if "print(" in line or ".write(" in line]
    for line in writes:
        assert "scrub(" in line or line.startswith('print(f"board.py: the boards token is read'), line


# ---- the child process ---------------------------------------------------------


def test_child_env_carries_this_token_alone_and_no_debug():
    base = {"PATH": "x", "GITHUB_TOKEN": "other", "GH_TOKEN": "other", "GH_ENTERPRISE_TOKEN": "e",
            "GITHUB_ENTERPRISE_TOKEN": "e", "GH_HOST": "ghe.example", "GH_DEBUG": "api",
            "DEBUG": "1", "gh_debug": "api"}
    env = board.child_env(SECRET, base)
    assert env == {"PATH": "x", "GH_TOKEN": SECRET}
    assert "GH_TOKEN" not in base or base["GH_TOKEN"] == "other"


def test_run_hands_the_token_to_the_child_only(monkeypatch):
    seen = {}

    def fake_run(argv, **kw):
        seen["argv"], seen["env"] = argv, kw["env"]
        assert "shell" not in kw
        return subprocess.CompletedProcess(argv, 0, "ok", "")

    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.setattr(board.subprocess, "run", fake_run)
    assert board.run(["gh", "project", "list"], SECRET) == (0, "ok", "")
    assert seen["env"]["GH_TOKEN"] == SECRET
    assert "GH_TOKEN" not in os.environ  # the caller's environment is not changed
    assert SECRET not in seen["argv"]


def test_the_script_reads_no_token_from_the_environment_or_a_file():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "getenv" not in source and "environ[" not in source and "environ.get" not in source
    assert "open(" not in source and "read_text" not in source


# ---- the credential store ------------------------------------------------------


def test_decode_blob_reads_utf16_and_utf8():
    assert board.decode_blob("ghp_abc".encode("utf-16-le")) == "ghp_abc"
    assert board.decode_blob(b"ghp_abc") == "ghp_abc"
    assert board.decode_blob(b"ab") == "ab"


@pytest.mark.parametrize("platform,argv", [
    ("darwin", ["security", "find-generic-password", "-s", board.ENTRY, "-w"]),
    ("linux", ["secret-tool", "lookup", "service", board.ENTRY]),
])
def test_the_fallback_outside_windows(platform, argv):
    seen = []

    def store(call):
        seen.append(call)
        return 0, f"  {SECRET}\n"

    assert board.read_token(board.ENTRY, platform=platform, runner=store) == SECRET
    assert seen == [argv]


def test_a_fallback_failure_names_the_entry_and_never_the_output():
    def store(call):
        return 44, f"partial {SECRET}"

    with pytest.raises(board.StoreError) as exc:
        board.read_token(board.ENTRY, platform="linux", runner=store)
    assert board.ENTRY in str(exc.value) and SECRET not in str(exc.value)


def test_an_unknown_platform_and_an_empty_entry_are_store_errors():
    with pytest.raises(board.StoreError):
        board.read_token(board.ENTRY, platform="plan9", runner=lambda c: (0, SECRET))
    with pytest.raises(board.StoreError):
        board.read_token(board.ENTRY, platform="linux", runner=lambda c: (0, "  \n"))


@pytest.mark.skipif(sys.platform != "win32", reason="CredReadW is Windows only")
def test_credreadw_on_an_entry_that_does_not_exist_is_a_store_error():
    entry = f"skills-plugins-hooks-agents/test-missing-{uuid.uuid4().hex}"
    with pytest.raises(board.StoreError) as exc:
        board.read_token(entry)
    assert "no generic entry named" in str(exc.value) and entry in str(exc.value)


# ---- the token-check rows -----------------------------------------------------------


class CheckFake:
    """Answers the three D calls; each answer can be swapped."""

    def __init__(self, board_code=0, scopes="project", secrets=(1, "", "gh: Resource not accessible by personal access token (HTTP 403)"), leak=None,
                 login=(0, OWNER + "\n", "")):
        self.calls = []
        self.login = login
        self.board_code = board_code
        self.scopes = scopes
        self.secrets = secrets
        self.leak = leak

    def __call__(self, argv, token):
        self.calls.append((list(argv), token))
        if argv == board.LOGIN_CALL:
            return self.login
        if argv[:3] == ["gh", "project", "view"]:
            return self.board_code, "3\n", "" if self.board_code == 0 else f"not found {self.leak or ''}"
        if argv[:3] == ["gh", "api", "-i"]:
            head = "HTTP/2.0 200 OK\nAuthorization: token " + (self.leak or "x") + "\n"
            if self.scopes is not None:
                head += f"X-Oauth-Scopes: {self.scopes}\n"
            return 0, head + "\n{\"resources\": {}}\n", ""
        return self.secrets


def rows_of(fake, read=None):
    return board.boards_rows(OWNER, NUMBER, "someone/some-repo", runner=fake, read=read or reader())


def test_a_boards_only_token_passes_d1_and_both_d2_rows():
    fake = CheckFake()
    rows = rows_of(fake)
    assert [(r[0], r[2]) for r in rows] == [("D1 board", "PASS"), ("D2 scopes", "PASS"),
                                            ("D2 refused", "PASS")]
    assert rows[1][3] == "scopes: project"
    assert rows[2][3] == "refused (HTTP 403)"
    assert all(token == SECRET for _, token in fake.calls)
    assert fake.calls[0][0] == board.LOGIN_CALL
    assert fake.calls[1][0] == ["gh", "project", "view", NUMBER, "--owner", "@me", "--format",
                                "json", "--jq", ".number"]
    assert fake.calls[3][0] == ["gh", "api", "repos/someone/some-repo/actions/secrets",
                                "--jq", ".total_count"]


def test_d1_fails_on_another_login_without_a_project_call_or_the_login():
    fake = CheckFake(login=(0, "someone-else\n", ""))
    rows = rows_of(fake)
    assert rows[0][2:] == ("FAIL", "boards of another owner are not supported")
    assert "someone-else" not in repr(rows)
    assert not [c for c, _ in fake.calls if c[:2] == ["gh", "project"]]
    assert [r[0] for r in rows] == ["D1 board", "D2 scopes", "D2 refused"]


def test_d1_fails_on_a_failed_login_read_with_the_error_scrubbed():
    fake = CheckFake(login=(1, "", f"HTTP 401 near {SECRET}"))
    rows = rows_of(fake)
    assert rows[0][2] == "FAIL" and "HTTP 401" in rows[0][3]
    assert SECRET not in repr(rows)
    assert not [c for c, _ in fake.calls if c[:2] == ["gh", "project"]]


@pytest.mark.parametrize("scopes", ["project, repo", "public_repo, project", "project, workflow",
                                    "project, delete_repo", "admin:repo_hook, project",
                                    "project, repo:status", "project, gist", "project, read:org",
                                    "read:project", ""])
def test_any_scope_besides_project_or_a_missing_one_fails_d2(scopes):
    rows = rows_of(CheckFake(scopes=scopes))
    assert rows[1][2] == "FAIL"


def test_project_with_its_read_half_passes_d2():
    assert rows_of(CheckFake(scopes="project, read:project"))[1][2] == "PASS"


def test_no_scope_header_fails_d2():
    assert rows_of(CheckFake(scopes=None))[1][2:] == ("FAIL", "no scope list in the answer")


def test_a_secrets_read_let_through_fails_and_its_answer_is_dropped():
    rows = rows_of(CheckFake(secrets=(0, f"5 {SECRET}", "")))
    assert rows[2][2:] == ("FAIL", "the token was let through")
    assert SECRET not in repr(rows)


def test_a_404_is_refused_and_another_error_is_a_fail():
    assert rows_of(CheckFake(secrets=(1, "", "gh: Not Found (HTTP 404)")))[2][2] == "PASS"
    assert rows_of(CheckFake(secrets=(1, "", "error connecting to api.github.com")))[2][2] == "FAIL"


def test_a_board_not_reached_fails_d1():
    assert rows_of(CheckFake(board_code=1))[0][2] == "FAIL"


def test_no_row_holds_the_token_or_a_header():
    rows = rows_of(CheckFake(board_code=1, leak=SECRET, secrets=(1, f"{SECRET}", f"bad {SECRET}")))
    text = repr(rows)
    assert SECRET not in text and "Authorization" not in text


def test_a_store_error_is_one_d0_row_and_no_call():
    def broken(entry):
        raise board.StoreError(f"no entry named {entry}")

    fake = CheckFake()
    rows = rows_of(fake, read=broken)
    assert [r[:3] for r in rows] == [("D0 store", f"credential store entry {board.ENTRY}", "FAIL")]
    assert fake.calls == []


def test_boards_rows_check_their_arguments():
    for owner, number, repo in (("bad owner", NUMBER, "a/b"), (OWNER, "x", "a/b"),
                                (OWNER, NUMBER, "a/b;rm")):
        with pytest.raises(ValueError):
            board.boards_rows(owner, number, repo, runner=CheckFake(), read=never_read)
