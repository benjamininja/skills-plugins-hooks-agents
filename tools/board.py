"""Projects boards: the one route to a board, with the boards-only token from the credential store.

Usage:
  python tools/board.py items  <owner> <number> [--limit N]
  python tools/board.py fields <owner> <number>
  python tools/board.py views  <owner> <number>
  python tools/board.py add    <owner> <number> <issue or pull request URL>
  python tools/board.py set    <owner> <number> --item <id> --field <id>
                               (--text T | --number N | --date YYYY-MM-DD | --option <id> | --iteration <id>)

<owner> is a GitHub login, or @me. The token is a classic token holding the
`project` scope alone (#285). It is read from the operating system's credential
store under ENTRY, never from an environment variable or a file, and is handed
to each gh child process alone, in that child's GH_TOKEN. Everything the child
prints is scrubbed of the value before it is shown, and the script prints no
header. A missing entry stops the script with exit 2, naming the entry only.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

ENTRY = "skills-plugins-hooks-agents/boards-token"
TIMEOUT = 120
TOKEN_RE = re.compile(r"(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{8,}")
OWNER_RE = re.compile(r"@me|[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
NUMBER_RE = re.compile(r"[0-9]{1,6}")
URL_RE = re.compile(r"https://github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/(?:issues|pull)/[0-9]+")
ITEM_RE = re.compile(r"PVTI_[A-Za-z0-9_-]{1,64}")
FIELD_RE = re.compile(r"PVT[A-Z]*F_[A-Za-z0-9_-]{1,64}")
OPTION_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")
DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
VALUE_NUMBER_RE = re.compile(r"-?[0-9]+(?:\.[0-9]+)?")
REPO_RE = re.compile(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+")
# Variables a child must not see: another login, a GitHub Enterprise host, or
# gh's debug output, which prints request headers.
DROP = ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN",
        "GH_HOST", "GH_DEBUG", "DEBUG")
WIDE_SCOPES = ("repo", "public_repo", "workflow")
ERROR_NOT_FOUND = 1168  # ERROR_NOT_FOUND from CredReadW
CRED_TYPE_GENERIC = 1
VIEWS_QUERY = (
    "query($login: String!, $number: Int!) { user(login: $login) { projectV2(number: $number) "
    "{ views(first: 50) { nodes { id number name layout } } } } }"
)
VIEWS_QUERY_ME = (
    "query($number: Int!) { viewer { projectV2(number: $number) "
    "{ views(first: 50) { nodes { id number name layout } } } } }"
)


class StoreError(Exception):
    """The credential store gave no token. The message names the entry, never a value."""


# ---- the credential store ------------------------------------------------


def decode_blob(blob: bytes) -> str:
    """cmdkey and the Credential Manager store UTF-16-LE; other tools store UTF-8."""
    if len(blob) % 2 == 0 and blob[1::2] and not any(blob[1::2]):
        return blob.decode("utf-16-le")
    return blob.decode("utf-8", errors="replace")


def read_windows(entry: str) -> str:
    import ctypes
    from ctypes import wintypes

    class CREDENTIAL(ctypes.Structure):
        _fields_ = [
            ("Flags", wintypes.DWORD),
            ("Type", wintypes.DWORD),
            ("TargetName", wintypes.LPWSTR),
            ("Comment", wintypes.LPWSTR),
            ("LastWritten", wintypes.FILETIME),
            ("CredentialBlobSize", wintypes.DWORD),
            ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)),
            ("Persist", wintypes.DWORD),
            ("AttributeCount", wintypes.DWORD),
            ("Attributes", ctypes.c_void_p),
            ("TargetAlias", wintypes.LPWSTR),
            ("UserName", wintypes.LPWSTR),
        ]

    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    cred_read = advapi.CredReadW
    cred_read.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                          ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
    cred_read.restype = wintypes.BOOL
    cred_free = advapi.CredFree
    cred_free.argtypes = [ctypes.c_void_p]
    cred_free.restype = None

    found = ctypes.POINTER(CREDENTIAL)()
    if not cred_read(entry, CRED_TYPE_GENERIC, 0, ctypes.byref(found)):
        code = ctypes.get_last_error()
        if code == ERROR_NOT_FOUND:
            raise StoreError(f"no generic entry named {entry} in the Windows Credential Manager")
        raise StoreError(f"CredReadW could not read {entry}: Windows error {code}")
    try:
        cred = found.contents
        blob = ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize)
    finally:
        cred_free(found)
    return decode_blob(blob)


def store_argv(entry: str, platform: str) -> list[str] | None:
    """The fallback outside Windows: one store tool whose stdout is the value."""
    if platform == "darwin":
        return ["security", "find-generic-password", "-s", entry, "-w"]
    if platform.startswith("linux"):
        return ["secret-tool", "lookup", "service", entry]
    return None


def store_run(argv: list[str]) -> tuple[int, str]:
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, type(exc).__name__
    return p.returncode, p.stdout


def read_token(entry: str = ENTRY, platform: str | None = None, runner=store_run) -> str:
    platform = platform or sys.platform
    if platform == "win32":
        value = read_windows(entry)
    else:
        argv = store_argv(entry, platform)
        if argv is None:
            raise StoreError(f"no credential store is known on {platform}")
        code, out = runner(argv)
        if code != 0:
            # the tool's output is never shown: on a failure it can hold nothing
            # useful, and on a partial success it could hold the value
            raise StoreError(f"{argv[0]} found no entry named {entry} (exit {code})")
        value = out
    value = value.strip()
    if not value:
        raise StoreError(f"the entry {entry} is empty")
    return value


# ---- one child process per call --------------------------------------------


def child_env(token: str, base: dict[str, str] | None = None) -> dict[str, str]:
    env = {k: v for k, v in (os.environ if base is None else base).items()
           if k.upper() not in DROP}
    env["GH_TOKEN"] = token
    return env


def run(argv: list[str], token: str) -> tuple[int, str, str]:
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=TIMEOUT, env=child_env(token))
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {TIMEOUT}s"
    except OSError as exc:
        return 127, "", str(exc)
    return p.returncode, p.stdout, p.stderr


def scrub(text: str, token: str | None = None) -> str:
    if token:
        text = text.replace(token, "***")
    return TOKEN_RE.sub("***", text)


def first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


# ---- arguments -------------------------------------------------------------


def pattern(regex: re.Pattern, what: str):
    def check(text: str) -> str:
        if not regex.fullmatch(text):
            raise argparse.ArgumentTypeError(f"expected {what}")
        return text
    return check


def limit_arg(text: str) -> str:
    if not NUMBER_RE.fullmatch(text) or not 1 <= int(text) <= 1000:
        raise argparse.ArgumentTypeError("expected a number from 1 to 1000")
    return str(int(text))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="board.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="action", required=True)

    def board(p):
        p.add_argument("owner", type=pattern(OWNER_RE, "a GitHub login or @me"))
        p.add_argument("number", type=pattern(NUMBER_RE, "a board number"))
        return p

    items = board(sub.add_parser("items", help="list the board's items"))
    items.add_argument("--limit", type=limit_arg, default="100")
    board(sub.add_parser("fields", help="list the board's fields"))
    board(sub.add_parser("views", help="list the board's views"))
    add = board(sub.add_parser("add", help="add an issue or a pull request"))
    add.add_argument("url", type=pattern(URL_RE, "an issue or pull request URL on github.com"))
    edit = board(sub.add_parser("set", help="set one field of one item"))
    edit.add_argument("--item", required=True, type=pattern(ITEM_RE, "an item id (PVTI_...)"))
    edit.add_argument("--field", required=True, type=pattern(FIELD_RE, "a field id (PVT..F_...)"))
    value = edit.add_mutually_exclusive_group(required=True)
    value.add_argument("--text")
    value.add_argument("--number", dest="value_number", type=pattern(VALUE_NUMBER_RE, "a number"))
    value.add_argument("--date", type=pattern(DATE_RE, "a date YYYY-MM-DD"))
    value.add_argument("--option", type=pattern(OPTION_RE, "a single-select option id"))
    value.add_argument("--iteration", type=pattern(OPTION_RE, "an iteration id"))
    return parser.parse_args(argv)


def value_flag(args: argparse.Namespace) -> str:
    # one --flag=value argument, so a value that starts with a dash stays a value
    if args.text is not None:
        return f"--text={args.text}"
    if args.value_number is not None:
        return f"--number={args.value_number}"
    if args.date is not None:
        return f"--date={args.date}"
    if args.option is not None:
        return f"--single-select-option-id={args.option}"
    return f"--iteration-id={args.iteration}"


# ---- the actions -----------------------------------------------------------


def calls(args: argparse.Namespace, project_id: str | None = None) -> list[str]:
    o, n = args.owner, args.number
    if args.action == "items":
        return ["gh", "project", "item-list", n, "--owner", o, "--format", "json",
                "--limit", args.limit]
    if args.action == "fields":
        return ["gh", "project", "field-list", n, "--owner", o, "--format", "json"]
    if args.action == "add":
        return ["gh", "project", "item-add", n, "--owner", o, "--url", args.url,
                "--format", "json"]
    if args.action == "views":
        if o == "@me":
            return ["gh", "api", "graphql", "-f", f"query={VIEWS_QUERY_ME}", "-F", f"number={n}"]
        return ["gh", "api", "graphql", "-f", f"query={VIEWS_QUERY}", "-f", f"login={o}",
                "-F", f"number={n}"]
    if args.action == "set":
        return ["gh", "project", "item-edit", "--id", args.item, "--project-id", project_id,
                "--field-id", args.field, value_flag(args)]
    raise ValueError(args.action)


def act(args: argparse.Namespace, token: str, runner) -> tuple[int, str, str]:
    if args.action == "set":
        # item-edit takes the board's node id, not its number
        code, out, err = runner(["gh", "project", "view", args.number, "--owner", args.owner,
                                 "--format", "json", "--jq", ".id"], token)
        project_id = out.strip()
        if code != 0 or not project_id:
            return code or 1, "", err or "the board's id was not found"
        return runner(calls(args, project_id), token)
    return runner(calls(args), token)


def main(argv: list[str], runner=run, read=read_token) -> int:
    args = parse_args(argv)
    token = None
    try:
        token = read(ENTRY)
        code, out, err = act(args, token, runner)
    except StoreError as exc:
        print(f"board.py: {scrub(str(exc))}", file=sys.stderr)
        print(f"board.py: the boards token is read from the credential store entry {ENTRY}; "
              "the owner makes it by hand (#285).", file=sys.stderr)
        return 2
    except Exception as exc:  # any other error is shown scrubbed, never raw
        print(f"board.py: {type(exc).__name__}: {scrub(str(exc), token)}", file=sys.stderr)
        return 1
    if out:
        sys.stdout.write(scrub(out, token))
    if err:
        sys.stderr.write(scrub(err, token))
    return code


# ---- the token-check rows (tools/token_check.py --boards) -------------------


def scopes_from_headers(text: str) -> list[str] | None:
    """The X-OAuth-Scopes header of a `gh api -i` answer; None when it is absent."""
    for line in text.splitlines():
        if not line.strip():
            break  # the end of the headers
        name, _, value = line.partition(":")
        if name.strip().lower() == "x-oauth-scopes":
            return [s.strip() for s in value.split(",") if s.strip()]
    return None


def boards_rows(owner: str, number: str, repo: str, runner=run,
                read=read_token) -> list[tuple[str, str, str, str]]:
    """D1: the token reaches the board. D2: it holds no repository scope, and a
    read only a repository scope may make is refused. Rows carry PASS or FAIL,
    scope names and a scrubbed first error line, never a value or a header."""
    if not OWNER_RE.fullmatch(owner) or not NUMBER_RE.fullmatch(number) or not REPO_RE.fullmatch(repo):
        raise ValueError("expected a login, a board number and <owner>/<repo>")
    try:
        token = read(ENTRY)
    except StoreError as exc:
        return [("D0 store", f"credential store entry {ENTRY}", "FAIL", scrub(str(exc)))]

    def call(argv):
        try:
            return runner(argv, token)
        except Exception as exc:
            return 1, "", f"{type(exc).__name__}: {exc}"

    def error(code, out, err):
        return scrub(first_line(err) or first_line(out) or f"exit {code}", token)

    rows = []
    argv = ["gh", "project", "view", number, "--owner", owner, "--format", "json", "--jq", ".number"]
    code, out, err = call(argv)
    rows.append(("D1 board", " ".join(argv), "PASS" if code == 0 else "FAIL",
                 "" if code == 0 else error(code, out, err)))

    argv = ["gh", "api", "-i", "rate_limit"]
    code, out, err = call(argv)
    if code != 0:
        rows.append(("D2 scopes", " ".join(argv), "FAIL", error(code, out, err)))
    else:
        scopes = scopes_from_headers(out)
        if scopes is None:
            rows.append(("D2 scopes", " ".join(argv), "FAIL", "no scope list in the answer"))
        else:
            wide = [s for s in scopes if s in WIDE_SCOPES]
            ok = "project" in scopes and not wide
            rows.append(("D2 scopes", " ".join(argv), "PASS" if ok else "FAIL",
                         "scopes: " + (", ".join(scopes) or "none")))

    argv = ["gh", "api", f"repos/{repo}/actions/secrets", "--jq", ".total_count"]
    code, out, err = call(argv)
    if code == 0:
        # let through: the answer is dropped unprinted
        rows.append(("D2 refused", " ".join(argv), "FAIL", "the token was let through"))
    else:
        text = f"{err}\n{out}"
        refused = re.search(r"HTTP (403|404)", text)
        rows.append(("D2 refused", " ".join(argv), "PASS" if refused else "FAIL",
                     f"refused (HTTP {refused.group(1)})" if refused else error(code, out, err)))
    return rows


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
