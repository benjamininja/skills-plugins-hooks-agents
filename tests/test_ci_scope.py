"""tools/ci_scope.py: which pytest arguments a pull request runs (#283).

Only a non-empty list of `.md` paths, none under a `tests` folder, gets the
three text test files. Everything else, and any doubt, gets `tests`.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "ci_scope.py"
_spec = importlib.util.spec_from_file_location("ci_scope", SCRIPT)
ci_scope = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ci_scope)

TEXT = (
    "tests/test_skills_frontmatter.py "
    "tests/test_agents_frontmatter.py "
    "tests/test_adr_readme.py"
)
FULL = "tests"


def run(data: bytes) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT)],
        input=data,
        capture_output=True,
        timeout=60,
    )


def scope_of(text: str) -> str:
    return ci_scope.scope(ci_scope.parse(text.encode("utf-8")))


def test_only_md_files_gives_the_text_list():
    assert scope_of("README.md\ndocs/adr/0004-x.md\nskills/a/SKILL.md\n") == TEXT


def test_one_md_file_gives_the_text_list():
    assert scope_of("README.md\n") == TEXT


def test_no_final_newline_still_gives_the_text_list():
    assert scope_of("README.md") == TEXT


def test_windows_line_endings_give_the_text_list():
    assert scope_of("README.md\r\ndocs/a.md\r\n") == TEXT


def test_one_py_among_md_gives_tests():
    assert scope_of("README.md\ntools/x.py\ndocs/a.md\n") == FULL


def test_md_under_tests_gives_tests():
    assert scope_of("README.md\ntests/notes.md\n") == FULL


def test_md_under_a_nested_tests_folder_gives_tests():
    assert scope_of("plugins/x/tests/notes.md\n") == FULL


def test_md_under_tests_with_backslashes_gives_tests():
    assert scope_of("tests\\notes.md\n") == FULL


def test_a_folder_named_like_tests_is_not_tests():
    assert scope_of("docs/tests-notes/a.md\ndocs/mytests/b.md\n") == TEXT


def test_workflow_file_gives_tests():
    assert scope_of(".github/workflows/test.yml\n") == FULL


def test_workflow_file_with_md_gives_tests():
    assert scope_of("README.md\n.github/workflows/test.yml\n") == FULL


def test_json_template_gives_tests():
    assert scope_of("templates/brief.json\n") == FULL


def test_empty_list_gives_tests():
    assert scope_of("") == FULL


def test_blank_only_list_gives_tests():
    assert scope_of("\n\n  \n") == FULL


def test_path_with_a_space_gives_the_text_list():
    assert scope_of("docs/my notes.md\n") == TEXT


def test_path_with_a_space_and_another_extension_gives_tests():
    assert scope_of("docs/my notes.txt\n") == FULL


def test_upper_case_extension_is_not_text():
    assert scope_of("README.MD\n") == FULL


def test_mixed_case_extension_is_not_text():
    assert scope_of("README.Md\n") == FULL


def test_a_path_with_no_extension_gives_tests():
    assert scope_of("LICENSE\n") == FULL


def test_a_path_that_only_contains_md_gives_tests():
    assert scope_of("docs/a.md.bak\ndocs/md\n") == FULL


def test_a_quoted_path_gives_tests():
    assert scope_of('"docs/caf\\303\\251.md"\n') == FULL


def test_the_command_line_prints_the_text_list():
    result = run(b"README.md\ndocs/a.md\n")
    assert result.returncode == 0
    assert result.stdout.decode().splitlines() == [TEXT]


def test_the_command_line_prints_tests_for_code():
    result = run(b"README.md\ntools/x.py\n")
    assert result.returncode == 0
    assert result.stdout.decode().splitlines() == [FULL]


def test_the_command_line_prints_tests_for_an_empty_list():
    result = run(b"")
    assert result.returncode == 0
    assert result.stdout.decode().splitlines() == [FULL]


@pytest.mark.parametrize(
    "data",
    [b"\xff\xfe\x00README.md\n", b"README.md\n\x80\x81.md\n", b"docs/\xc3\x28.md\n"],
)
def test_unreadable_input_gives_tests(data):
    result = run(data)
    assert result.returncode == 0
    assert result.stdout.decode().splitlines() == [FULL]


def test_a_failure_inside_the_decision_gives_tests(monkeypatch):
    def boom(_paths):
        raise RuntimeError("boom")

    monkeypatch.setattr(ci_scope, "scope", boom)

    class Stdin:
        buffer = type("B", (), {"read": staticmethod(lambda: b"README.md\n")})()

    monkeypatch.setattr(sys, "stdin", Stdin())
    printed = []
    monkeypatch.setattr("builtins.print", lambda *a, **k: printed.append(a[0]))
    assert ci_scope.main() == 0
    assert printed == [FULL]


def test_the_three_text_test_files_exist():
    names = TEXT.split()
    assert len(names) == 3
    for name in names:
        assert (ROOT / name).is_file(), name
