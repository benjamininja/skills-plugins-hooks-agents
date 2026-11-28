"""tools/board.py: the one route to a Projects board (#285).

No test needs the real token and none reaches GitHub: the credential-store read
and every child process go to fakes. The one real call is a Windows read of an
entry that does not exist, which proves the CredReadW path without a secret.
"""
import importlib.util
import io
import json
import os
import re
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
CONTENT_ID = "I_kwDOabc123"

ACTIONS = [
    ["items", OWNER, NUMBER],
    ["items", OWNER, NUMBER, "--limit", "5"],
    ["fields", OWNER, NUMBER],
    ["views", OWNER, NUMBER],
    ["views", "@me", NUMBER],
    ["add", OWNER, NUMBER, URL],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--text", "hello"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "25"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--date", "2026-12-01"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--option", "f75ad846"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--iteration", "abc123"],
]


class Fake:
    """A child-process runner: records (argv, token) and answers from the argv."""

    def __init__(self, code=0, out="", err="", leak=None, raises=None):
        self.calls: list[tuple[list[str], str]] = []
        self.inputs: list[str | None] = []  # each call's standard input, in step with calls
        self.code, self.out, self.err = code, out, err
        self.leak = leak
        self.raises = raises

    def __call__(self, argv, token, stdin=None):
        self.calls.append((list(argv), token))
        self.inputs.append(stdin)
        if self.raises:
            raise self.raises
        if argv == board.LOGIN_CALL:
            return 0, OWNER + "\n", ""
        if f"query={board.BOARD_QUERY}" in argv:
            return 0, PROJECT_ID + "\n", ""
        if f"query={board.RESOURCE_QUERY}" in argv:
            return 0, CONTENT_ID + "\n", ""
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
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "@file"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "nan"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "NaN"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "inf"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number=-inf"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "infinity"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "1e999"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "1_000"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "0x10"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "2,5"],
    ["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", " 2.5"],
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


def gql(query, *values):
    return ["gh", "api", "graphql", "-f", f"query={query}", *values]


BOARD_ID_CALL = gql(board.BOARD_QUERY, "-F", f"number={NUMBER}") + [
    "--jq", ".data.viewer.projectV2.id"]


def test_each_action_makes_its_graphql_calls_with_the_token():
    expected = {
        "items": [gql(board.ITEMS_QUERY, "-F", f"number={NUMBER}", "-F", "first=100")],
        "fields": [gql(board.FIELDS_QUERY, "-F", f"number={NUMBER}")],
        "views": [gql(board.VIEWS_QUERY, "-F", f"number={NUMBER}")],
        "add": [BOARD_ID_CALL,
                gql(board.RESOURCE_QUERY, "-f", f"url={URL}") + [
                    "--jq", ".data.resource.id // empty"],
                gql(board.ADD_MUTATION, "-f", f"project={PROJECT_ID}", "-f",
                    f"content={CONTENT_ID}")],
    }
    for action, argvs in expected.items():
        fake = Fake(out="{}\n")
        args = [action, OWNER, NUMBER] + ([URL] if action == "add" else [])
        assert board.main(args, runner=fake, read=reader()) == 0
        assert fake.calls == [(board.LOGIN_CALL, SECRET)] + [(a, SECRET) for a in argvs]


@pytest.mark.parametrize("argv", ACTIONS)
def test_no_action_builds_a_gh_project_call(argv):
    # #328: gh project asks GitHub for more than the project scope
    fake = Fake(out="{}\n")
    board.main(argv, runner=fake, read=reader())
    graphql_calls = [(call, body) for (call, _), body in zip(fake.calls, fake.inputs)
                     if call != board.LOGIN_CALL]
    assert graphql_calls
    for call, body in graphql_calls:
        assert "project" not in call[:2]
        if body is not None:  # set --number: the fixed text goes in the JSON body (#329)
            assert call == board.BODY_CALL
            assert json.loads(body)["query"] in board.QUERIES
            continue
        assert call[:4] == ["gh", "api", "graphql", "-f"]
        assert call[4].removeprefix("query=") in board.QUERIES
        assert not any(a.startswith("query=") for a in call[5:])


def test_no_gh_project_command_is_left_in_the_script():
    source = SCRIPT.read_text(encoding="utf-8")
    assert not re.search(r'"gh",\s*"project"', source)
    assert "gh project" not in source.split('"""', 2)[2]  # after the module's docstring


def test_the_queries_are_fixed_texts_and_only_add_and_set_write():
    reads = (board.BOARD_QUERY, board.ITEMS_QUERY, board.FIELDS_QUERY, board.VIEWS_QUERY,
             board.RESOURCE_QUERY)
    assert all(q.startswith("query(") and "mutation" not in q for q in reads)
    writes = [board.ADD_MUTATION, *(m for m, _ in board.SET_MUTATIONS.values())]
    assert all(q.startswith("mutation(") for q in writes)
    for q in reads[:4]:
        assert "viewer { projectV2(number: $number)" in q
    for q in board.QUERIES:
        assert "organization" not in q and "user(" not in q and "discussion" not in q.lower()


@pytest.mark.parametrize("flag,value,kind,gh_flag", [
    ("--text", "-starts-with-a-dash", "text", "-f"),
    ("--date", "2026-12-01", "date", "-f"),
    ("--option", "f75ad846", "option", "-f"),
    ("--iteration", "abc123", "iteration", "-f"),
])
def test_set_reads_the_board_id_then_edits_one_field(flag, value, kind, gh_flag):
    fake = Fake()
    code = board.main(["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, f"{flag}={value}"],
                      runner=fake, read=reader())
    assert code == 0
    (login, _), (lookup, _), (edit, token) = fake.calls
    assert login == board.LOGIN_CALL
    assert lookup == BOARD_ID_CALL
    assert edit == gql(board.SET_MUTATIONS[kind][0], "-f", f"project={PROJECT_ID}",
                       "-f", f"item={ITEM}", "-f", f"field={FIELD}", gh_flag, f"value={value}")
    assert token == SECRET


def test_set_sends_the_number_as_a_float_and_everything_else_as_a_string():
    kinds = {k: m for k, (m, _) in board.SET_MUTATIONS.items()}
    assert "$value: Float!" in kinds["value_number"] and "value: {number: $value}" in kinds["value_number"]
    assert "$value: Date!" in kinds["date"]
    assert "value: {singleSelectOptionId: $value}" in kinds["option"]
    assert "value: {iterationId: $value}" in kinds["iteration"]
    flags = {k: flag for k, (_, flag) in board.SET_MUTATIONS.items()}
    assert flags.pop("value_number") is None  # the JSON body on standard input (#329)
    assert set(flags.values()) == {"-f"}


@pytest.mark.parametrize("value,number", [
    ("2.5", 2.5), ("0.5", 0.5), ("-3", -3), ("25", 25), (".75", 0.75), ("-1.25e2", -125),
    ("3.", 3),
])
def test_set_number_sends_a_json_body_with_the_value_as_a_json_number(value, number):
    fake = Fake()
    code = board.main(["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, f"--number={value}"],
                      runner=fake, read=reader())
    assert code == 0
    (login, _), (lookup, _), (edit, token) = fake.calls
    assert login == board.LOGIN_CALL and lookup == BOARD_ID_CALL
    assert fake.inputs[:2] == [None, None]
    assert edit == ["gh", "api", "graphql", "--input", "-"] and token == SECRET
    body = fake.inputs[2]
    sent = json.loads(body)
    assert sent == {"query": board.SET_MUTATIONS["value_number"][0], "variables": {
        "project": PROJECT_ID, "item": ITEM, "field": FIELD, "value": number}}
    assert isinstance(sent["variables"]["value"], float)  # a JSON number, never a string
    assert re.search(r'"value": -?[0-9.]+(?:e[-+]?[0-9]+)?\}', body)
    assert value not in sent["query"] and "$value" in sent["query"]
    assert SECRET not in body


def test_the_number_body_holds_no_token_even_a_token_shaped_one():
    fake = Fake()
    board.main(["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--number", "0.5"],
               runner=fake, read=reader(SHAPED))
    body = fake.inputs[-1]
    assert SHAPED not in body and "ghp_" not in body and "GH_TOKEN" not in body


def test_run_passes_the_body_to_the_child_on_standard_input(monkeypatch):
    seen = {}

    def fake_run(argv, **kw):
        seen.update(kw)
        return subprocess.CompletedProcess(argv, 0, "ok", "")

    monkeypatch.setattr(board.subprocess, "run", fake_run)
    assert board.run(list(board.BODY_CALL), SECRET, stdin='{"a": 1}') == (0, "ok", "")
    assert seen["input"] == '{"a": 1}'
    assert board.run(["gh", "api", "user"], SECRET) == (0, "ok", "")
    assert seen["input"] is None


@pytest.mark.parametrize("text", ['say "hi" {x}', '{"a": 1}', "a } { b", "$value", "x=y"])
def test_a_value_with_quotes_or_braces_reaches_the_child_as_one_argument(text):
    fake = Fake()
    assert board.main(["set", OWNER, NUMBER, "--item", ITEM, "--field", FIELD, "--text", text],
                      runner=fake, read=reader()) == 0
    edit = fake.calls[-1][0]
    assert edit[-2:] == ["-f", f"value={text}"]
    assert edit[4] == f"query={board.SET_MUTATIONS['text'][0]}"
    assert sum(text in a for a in edit[5:]) == 1  # the values after the fixed text


def test_a_url_and_a_cursor_are_never_in_the_query_text():
    cursor = 'Y3Vyc29y"}{'
    page = {"data": {"viewer": {"projectV2": {"items": {
        "totalCount": 2, "pageInfo": {"hasNextPage": True, "endCursor": cursor},
        "nodes": [{"id": "PVTI_a"}]}}}}}

    class Pages(Fake):
        def __call__(self, argv, token):
            self.calls.append((list(argv), token))
            if argv == board.LOGIN_CALL:
                return 0, OWNER + "\n", ""
            return 0, json.dumps(page), ""

    fake = Pages()
    board.main(["items", OWNER, NUMBER, "--limit", "2"], runner=fake, read=reader())
    second = fake.calls[2][0]
    assert second[-2:] == ["-f", f"after={cursor}"] and cursor not in second[4]
    fake = Fake()
    board.main(["add", OWNER, NUMBER, URL], runner=fake, read=reader())
    assert all(URL not in call[4] for call, _ in fake.calls[1:])


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


PROJECT_ACTIONS = [a for a in ACTIONS if a[1] == OWNER]


@pytest.mark.parametrize("argv", PROJECT_ACTIONS)
def test_every_board_call_is_the_viewers_after_the_login_check(argv):
    fake = Fake()
    assert board.main(argv, runner=fake, read=reader()) == 0
    assert fake.calls[0] == (board.LOGIN_CALL, SECRET)
    for call, _ in fake.calls[1:]:
        assert call[:3] == ["gh", "api", "graphql"]
        values = [a for a in call if a != f"url={URL}"]  # the URL holds its repository's owner
        assert not any(OWNER in a for a in values) and not any(a.startswith("login=") for a in call)
    assert sum(call == board.LOGIN_CALL for call, _ in fake.calls) == 1


class OtherLogin(Fake):
    def __init__(self, login="someone-else", code=0, err=""):
        super().__init__()
        self.login, self.login_code, self.login_err = login, code, err

    def __call__(self, argv, token, stdin=None):
        if argv == board.LOGIN_CALL:
            self.calls.append((list(argv), token))
            self.inputs.append(stdin)
            return self.login_code, self.login + "\n", self.login_err
        return super().__call__(argv, token, stdin)


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
    assert [call[:5] for call, _ in fake.calls] == [
        gql(board.ITEMS_QUERY)]


def page_of(ids, has_next, cursor="c1", total=None):
    return json.dumps({"data": {"viewer": {"projectV2": {"items": {
        "totalCount": len(ids) if total is None else total,
        "pageInfo": {"hasNextPage": has_next, "endCursor": cursor},
        "nodes": [{"id": i, "content": {"title": f"title {i}"}} for i in ids]}}}}})


class Paged(Fake):
    """Answers item pages in order."""

    def __init__(self, pages):
        super().__init__()
        self.pages = list(pages)

    def __call__(self, argv, token):
        self.calls.append((list(argv), token))
        if argv == board.LOGIN_CALL:
            return 0, OWNER + "\n", ""
        return self.pages.pop(0)


def test_items_pages_until_the_limit_and_prints_one_object(capsys, monkeypatch):
    fake = Paged([(0, page_of(["a", "b"], True, "c1", 5), ""),
                  (0, page_of(["c", "d"], True, "c2", 5), "")])
    monkeypatch.setattr(board, "PAGE", 2)
    assert board.main(["items", OWNER, NUMBER, "--limit", "3"], runner=fake, read=reader()) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["totalCount"] == 5
    assert [n["id"] for n in printed["items"]] == ["a", "b", "c"]
    calls = [call for call, _ in fake.calls[1:]]
    assert "first=2" in calls[0] and not any(a.startswith("after=") for a in calls[0])
    assert "first=1" in calls[1] and "after=c1" in calls[1]


def test_items_stops_at_the_last_page():
    fake = Paged([(0, page_of(["a"], False), "")])
    assert board.main(["items", OWNER, NUMBER], runner=fake, read=reader()) == 0
    assert len(fake.calls) == 2


def test_items_stops_on_an_empty_page_that_says_there_is_more():
    fake = Paged([(0, page_of([], True), "")])
    assert board.main(["items", OWNER, NUMBER], runner=fake, read=reader()) == 0
    assert len(fake.calls) == 2


def test_a_failed_page_is_passed_on_with_its_exit_code(capsys):
    fake = Paged([(0, page_of(["a"], True), ""), (1, "", "gh: HTTP 502\n")])
    assert board.main(["items", OWNER, NUMBER], runner=fake, read=reader()) == 1
    captured = capsys.readouterr()
    assert captured.out == "" and "HTTP 502" in captured.err


def test_add_stops_with_exit_2_when_the_token_cannot_read_the_issue(capsys):
    class Private(Fake):
        def __call__(self, argv, token):
            if f"query={board.RESOURCE_QUERY}" in argv:
                self.calls.append((list(argv), token))
                return 0, "", ""  # resource is null: the --jq answer is empty
            return super().__call__(argv, token)

    fake = Private()
    assert board.main(["add", OWNER, NUMBER, URL], runner=fake, read=reader()) == 2
    assert not [c for c, _ in fake.calls if f"query={board.ADD_MUTATION}" in c]
    err = capsys.readouterr().err
    assert err.strip() == ("board.py: the boards token cannot read that repository's "
                           "issue or pull request")


@pytest.mark.parametrize("err,code", [
    ("gh: Your token has not been granted the required scopes (INSUFFICIENT_SCOPES)", 2),
    ("gh: Could not resolve to a Repository with the name 'x'.", 2),
    ("gh: Resource not accessible (HTTP 403)", 2),
    ("error connecting to api.github.com", 1),
])
def test_a_refused_lookup_is_exit_2_and_another_failure_is_passed_on(err, code):
    class Lookup(Fake):
        def __call__(self, argv, token):
            if f"query={board.RESOURCE_QUERY}" in argv:
                self.calls.append((list(argv), token))
                return 1, "", err
            return super().__call__(argv, token)

    fake = Lookup()
    assert board.main(["add", OWNER, NUMBER, URL], runner=fake, read=reader()) == code
    assert not [c for c, _ in fake.calls if f"query={board.ADD_MUTATION}" in c]


def test_calls_are_argument_lists_never_shell_strings():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "shell=True" not in source and "os.system" not in source
    for argv in ACTIONS:
        fake = Fake()
        board.main(argv, runner=fake, read=reader())
        for (call, _), body in zip(fake.calls, fake.inputs):
            assert isinstance(call, list) and all(isinstance(a, str) for a in call)
            assert SECRET not in " ".join(call)
            assert body is None or SECRET not in body


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


COUNTS = {"ITEMS": "4", "FIELDS": "9", "VIEWS": "2"}


class CheckFake:
    """Answers the D calls; each answer can be swapped."""

    def __init__(self, board_code=0, scopes="project", secrets=(1, "", "gh: Resource not accessible by personal access token (HTTP 403)"), leak=None,
                 login=(0, OWNER + "\n", ""), board_out=NUMBER + "\n", reads=None):
        self.calls = []
        self.login = login
        self.board_code = board_code
        self.board_out = board_out
        self.scopes = scopes
        self.secrets = secrets
        self.leak = leak
        self.reads = {name: (0, f"{count}\n", "") for name, count in COUNTS.items()}
        self.reads.update(reads or {})

    def __call__(self, argv, token):
        self.calls.append((list(argv), token))
        if argv == board.LOGIN_CALL:
            return self.login
        if f"query={board.BOARD_QUERY}" in argv:
            return (self.board_code, self.board_out,
                    "" if self.board_code == 0 else f"not found {self.leak or ''}")
        for name in COUNTS:
            if f"query={getattr(board, name + '_QUERY')}" in argv:
                return self.reads[name]
        if argv[:3] == ["gh", "api", "-i"]:
            head = "HTTP/2.0 200 OK\nAuthorization: token " + (self.leak or "x") + "\n"
            if self.scopes is not None:
                head += f"X-Oauth-Scopes: {self.scopes}\n"
            return 0, head + "\n{\"resources\": {}}\n", ""
        return self.secrets


def rows_of(fake, read=None):
    return board.boards_rows(OWNER, NUMBER, "someone/some-repo", runner=fake, read=read or reader())


def row(rows, rid):
    (found,) = [r for r in rows if r[0] == rid]
    return found


D_ROWS = ["D1 board", "D1 items", "D1 fields", "D1 views", "D2 scopes", "D2 refused"]


def test_a_boards_only_token_passes_every_d_row():
    fake = CheckFake()
    rows = rows_of(fake)
    assert [(r[0], r[2]) for r in rows] == [(rid, "PASS") for rid in D_ROWS]
    assert row(rows, "D1 board")[1] == f"gh api graphql BOARD_QUERY number={NUMBER}"
    assert row(rows, "D1 items")[3] == "count: 4"
    assert row(rows, "D1 fields")[3] == "count: 9"
    assert row(rows, "D1 views")[3] == "count: 2"
    assert row(rows, "D2 scopes")[3] == "scopes: project"
    assert row(rows, "D2 refused")[3] == "refused (HTTP 403)"
    assert all(token == SECRET for _, token in fake.calls)
    calls = [c for c, _ in fake.calls]
    assert calls[0] == board.LOGIN_CALL
    assert calls[1] == gql(board.BOARD_QUERY, "-F", f"number={NUMBER}") + [
        "--jq", ".data.viewer.projectV2.number"]
    assert calls[2] == gql(board.ITEMS_QUERY, "-F", f"number={NUMBER}", "-F", "first=100") + [
        "--jq", ".data.viewer.projectV2.items.totalCount"]
    assert calls[3] == gql(board.FIELDS_QUERY, "-F", f"number={NUMBER}") + [
        "--jq", ".data.viewer.projectV2.fields.totalCount"]
    assert calls[4] == gql(board.VIEWS_QUERY, "-F", f"number={NUMBER}") + [
        "--jq", ".data.viewer.projectV2.views.totalCount"]
    assert calls[6] == ["gh", "api", "repos/someone/some-repo/actions/secrets",
                        "--jq", ".total_count"]
    assert not [c for c in calls if c[:2] == ["gh", "project"]]


def test_each_read_row_runs_the_actions_own_query():
    fake = CheckFake()
    rows_of(fake)
    sent = [c[4] for c, _ in fake.calls if c[:3] == ["gh", "api", "graphql"]]
    for query in (board.ITEMS_QUERY, board.FIELDS_QUERY, board.VIEWS_QUERY):
        assert f"query={query}" in sent


@pytest.mark.parametrize("name,rid", [("ITEMS", "D1 items"), ("FIELDS", "D1 fields"),
                                      ("VIEWS", "D1 views")])
def test_a_read_row_prints_a_count_only(name, rid):
    title = "Secret plan title"
    rows = rows_of(CheckFake(reads={name: (0, f'{{"title": "{title}"}}\n', "")}))
    assert row(rows, rid)[2:] == ("FAIL", "no count in the answer")
    assert title not in repr(rows)


@pytest.mark.parametrize("name,rid", [("ITEMS", "D1 items"), ("FIELDS", "D1 fields"),
                                      ("VIEWS", "D1 views")])
def test_a_refused_read_fails_its_row_with_the_error_scrubbed_and_no_output(name, rid):
    err = f"gh: The 'title' field requires one of the following scopes: ['repo'] {SECRET}"
    rows = rows_of(CheckFake(reads={name: (1, "Item title in the body", err)}))
    found = row(rows, rid)
    assert found[2] == "FAIL" and "requires one of the following scopes" in found[3]
    assert SECRET not in repr(rows) and "Item title" not in repr(rows)
    assert [r[2] for r in rows if r[0] != rid and r[0].startswith("D1")] == ["PASS", "PASS", "PASS"]


def test_d1_fails_on_another_login_without_a_board_call_or_the_login():
    fake = CheckFake(login=(0, "someone-else\n", ""))
    rows = rows_of(fake)
    assert rows[0][2:] == ("FAIL", "boards of another owner are not supported")
    assert "someone-else" not in repr(rows)
    assert not [c for c, _ in fake.calls if c[:3] == ["gh", "api", "graphql"]]
    assert [r[0] for r in rows] == D_ROWS
    assert [r[2] for r in rows[1:4]] == ["not run"] * 3


def test_d1_fails_on_a_failed_login_read_with_the_error_scrubbed():
    fake = CheckFake(login=(1, "", f"HTTP 401 near {SECRET}"))
    rows = rows_of(fake)
    assert rows[0][2] == "FAIL" and "HTTP 401" in rows[0][3]
    assert SECRET not in repr(rows)
    assert not [c for c, _ in fake.calls if c[:3] == ["gh", "api", "graphql"]]


@pytest.mark.parametrize("scopes", ["project, repo", "public_repo, project", "project, workflow",
                                    "project, delete_repo", "admin:repo_hook, project",
                                    "project, repo:status", "project, gist", "project, read:org",
                                    "read:project", ""])
def test_any_scope_besides_project_or_a_missing_one_fails_d2(scopes):
    rows = rows_of(CheckFake(scopes=scopes))
    assert row(rows, "D2 scopes")[2] == "FAIL"


def test_project_with_its_read_half_passes_d2():
    assert row(rows_of(CheckFake(scopes="project, read:project")), "D2 scopes")[2] == "PASS"


def test_no_scope_header_fails_d2():
    assert row(rows_of(CheckFake(scopes=None)), "D2 scopes")[2:] == (
        "FAIL", "no scope list in the answer")


def test_a_secrets_read_let_through_fails_and_its_answer_is_dropped():
    rows = rows_of(CheckFake(secrets=(0, f"5 {SECRET}", "")))
    assert row(rows, "D2 refused")[2:] == ("FAIL", "the token was let through")
    assert SECRET not in repr(rows)


def test_a_404_is_refused_and_another_error_is_a_fail():
    refused = CheckFake(secrets=(1, "", "gh: Not Found (HTTP 404)"))
    assert row(rows_of(refused), "D2 refused")[2] == "PASS"
    other = CheckFake(secrets=(1, "", "error connecting to api.github.com"))
    assert row(rows_of(other), "D2 refused")[2] == "FAIL"


def test_a_board_not_reached_fails_d1():
    assert rows_of(CheckFake(board_code=1))[0][2] == "FAIL"


def test_another_board_number_back_fails_d1():
    assert rows_of(CheckFake(board_out="7\n"))[0][2:] == (
        "FAIL", "the board's number did not come back")


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
