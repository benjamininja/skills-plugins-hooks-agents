"""CI scope: which pytest arguments a pull request needs (#283).

Usage:  git diff --name-only --no-renames <base>...<head> | python tools/ci_scope.py

Reads the changed paths from standard input, one per line, and prints one line:
the pytest arguments to run. Only the three text test files run when the list
is not empty and every path ends in `.md` and none is under a `tests` folder.
In every other case it prints `tests`. An empty list, input that cannot be
read and any error also print `tests`: when in doubt, everything runs.
"""

from __future__ import annotations

import sys

TEXT_TESTS = (
    "tests/test_skills_frontmatter.py "
    "tests/test_agents_frontmatter.py "
    "tests/test_adr_readme.py"
)
FULL = "tests"


def is_text_only(paths: list[str]) -> bool:
    if not paths:
        return False
    for path in paths:
        if not path.endswith(".md"):
            return False
        if "tests" in path.replace("\\", "/").split("/")[:-1]:
            return False
    return True


def scope(paths: list[str]) -> str:
    return TEXT_TESTS if is_text_only(paths) else FULL


def parse(data: bytes) -> list[str]:
    lines = data.decode("utf-8").split("\n")
    return [line[:-1] if line.endswith("\r") else line for line in lines if line.strip()]


def main() -> int:
    try:
        result = scope(parse(sys.stdin.buffer.read()))
    except Exception:
        result = FULL
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
