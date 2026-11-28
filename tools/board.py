"""Projects boards: the one route to a board, with the boards-only token from the credential store.

Usage:
  python tools/board.py items  <owner> <number> [--limit N]
  python tools/board.py fields <owner> <number>
  python tools/board.py views  <owner> <number>
  python tools/board.py add    <owner> <number> <issue or pull request URL>
  python tools/board.py set    <owner> <number> --item <id> --field <id>
                               (--text T | --number N | --date YYYY-MM-DD | --option <id> | --iteration <id>)

<owner> is a GitHub login, or @me. The board is always the viewer's own: a login
given must be the token's own, read once with gh api user, or the script stops
with exit 2 (#307). Every call is the script's own GraphQL query or mutation
through gh api graphql, a fixed text held as a constant, with each value as a
separate -f or -F argument (#328), except set --number, whose request goes to the
child as a JSON body on standard input so a decimal stays a JSON number (#329).
No gh project command is used, since it asks GitHub for
more than the project scope. The token is a classic token holding the
`project` scope alone (#285). It is read from the operating system's credential
store under ENTRY, never from an environment variable or a file, and is handed
to each gh child process alone, in that child's GH_TOKEN. Everything the child
prints is scrubbed of the value before it is shown, and the script prints no
header. A missing entry stops the script with exit 2, naming the entry only.
"""

from __future__ import annotations

import argparse
import json
import math
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
# A plain decimal, with an optional exponent; a finite value alone passes (#329).
VALUE_NUMBER_RE = re.compile(r"-?(?:[0-9]{1,15}(?:\.[0-9]{0,15})?|\.[0-9]{1,15})(?:[eE][-+]?[0-9]{1,3})?")
REPO_RE = re.compile(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+")
# Variables a child must not see: another login, a GitHub Enterprise host, or
# gh's debug output, which prints request headers.
DROP = ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN",
        "GH_HOST", "GH_DEBUG", "DEBUG")
# The token holds the project scope alone (#285); read:project is its read half.
# Any other scope fails D2, not only the repository ones by name.
ALLOWED_SCOPES = ("project", "read:project")
ERROR_NOT_FOUND = 1168  # ERROR_NOT_FOUND from CredReadW
CRED_TYPE_GENERIC = 1
# ---- the fixed query texts (#328) --------------------------------------------
# Each reads or writes ProjectV2 alone, so the project scope covers it. No value
# is ever placed in a text: values go as GraphQL variables, one argument each.
FIELD_NAME = "field { ... on ProjectV2FieldCommon { id name } }"
BOARD_QUERY = "query($number: Int!) { viewer { projectV2(number: $number) { id number } } }"
ITEMS_QUERY = (
    "query($number: Int!, $first: Int!, $after: String) { viewer { projectV2(number: $number) "
    "{ items(first: $first, after: $after) { totalCount pageInfo { hasNextPage endCursor } "
    "nodes { id type isArchived content { __typename "
    "... on DraftIssue { title } "
    "... on Issue { number title url state repository { nameWithOwner } } "
    "... on PullRequest { number title url state repository { nameWithOwner } } } "
    "fieldValues(first: 50) { nodes { __typename "
    f"... on ProjectV2ItemFieldTextValue {{ text {FIELD_NAME} }} "
    f"... on ProjectV2ItemFieldNumberValue {{ number {FIELD_NAME} }} "
    f"... on ProjectV2ItemFieldDateValue {{ date {FIELD_NAME} }} "
    f"... on ProjectV2ItemFieldSingleSelectValue {{ name optionId {FIELD_NAME} }} "
    f"... on ProjectV2ItemFieldIterationValue {{ title iterationId startDate {FIELD_NAME} }} "
    "} } } } } } }"
)
FIELDS_QUERY = (
    "query($number: Int!) { viewer { projectV2(number: $number) { fields(first: 100) "
    "{ totalCount nodes { __typename ... on ProjectV2FieldCommon { id name dataType } "
    "... on ProjectV2SingleSelectField { options { id name } } "
    "... on ProjectV2IterationField { configuration { "
    "iterations { id title startDate duration } "
    "completedIterations { id title startDate duration } } } } } } } }"
)
VIEWS_QUERY = (
    "query($number: Int!) { viewer { projectV2(number: $number) "
    "{ views(first: 50) { totalCount nodes { id number name layout } } } } }"
)
RESOURCE_QUERY = (
    "query($url: URI!) { resource(url: $url) { __typename "
    "... on Issue { id } ... on PullRequest { id } } }"
)
ADD_MUTATION = (
    "mutation($project: ID!, $content: ID!) { addProjectV2ItemById("
    "input: {projectId: $project, contentId: $content}) { item { id } } }"
)


def _set_mutation(gql_type: str, key: str) -> str:
    return ("mutation($project: ID!, $item: ID!, $field: ID!, $value: " + gql_type + ") "
            "{ updateProjectV2ItemFieldValue(input: {projectId: $project, itemId: $item, "
            "fieldId: $field, value: {" + key + ": $value}}) { projectV2Item { id } } }")


# the set flag's name in the arguments -> (its fixed mutation, the gh api flag for its value;
# None: the request goes as a JSON body on standard input, #329)
SET_MUTATIONS = {
    "text": (_set_mutation("String!", "text"), "-f"),
    "value_number": (_set_mutation("Float!", "number"), None),
    "date": (_set_mutation("Date!", "date"), "-f"),
    "option": (_set_mutation("String!", "singleSelectOptionId"), "-f"),
    "iteration": (_set_mutation("String!", "iterationId"), "-f"),
}
QUERIES = (BOARD_QUERY, ITEMS_QUERY, FIELDS_QUERY, VIEWS_QUERY, RESOURCE_QUERY, ADD_MUTATION,
           *(m for m, _ in SET_MUTATIONS.values()))
PAGE = 100  # GitHub's largest page
# what a lookup of an issue the token cannot read answers
REFUSED_RE = re.compile(r"INSUFFICIENT_SCOPES|FORBIDDEN|NOT_FOUND|Could not resolve|"
                        r"requires one of the following scopes|HTTP 40[34]")


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


def run(argv: list[str], token: str, stdin: str | None = None) -> tuple[int, str, str]:
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=TIMEOUT, env=child_env(token), input=stdin)
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


def number_arg(text: str) -> float:
    """A decimal that is a finite number: nan, inf and an overflow stop here (#329)."""
    if not VALUE_NUMBER_RE.fullmatch(text) or not math.isfinite(float(text)):
        raise argparse.ArgumentTypeError("expected a finite number")
    return float(text)


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
    value.add_argument("--number", dest="value_number", type=number_arg)
    value.add_argument("--date", type=pattern(DATE_RE, "a date YYYY-MM-DD"))
    value.add_argument("--option", type=pattern(OPTION_RE, "a single-select option id"))
    value.add_argument("--iteration", type=pattern(OPTION_RE, "an iteration id"))
    return parser.parse_args(argv)


# ---- the calls -------------------------------------------------------------


def graphql(query: str, *values: str) -> list[str]:
    """One gh api graphql call: the fixed text, then each value as its own argument
    (-f for a string, -F for a number the script has checked)."""
    return ["gh", "api", "graphql", "-f", f"query={query}", *values]


def board_call(number: str, jq: str) -> list[str]:
    return graphql(BOARD_QUERY, "-F", f"number={number}") + ["--jq", jq]


def items_call(number: str, first: int, after: str | None = None) -> list[str]:
    argv = graphql(ITEMS_QUERY, "-F", f"number={number}", "-F", f"first={first}")
    if after:
        argv += ["-f", f"after={after}"]
    return argv


def fields_call(number: str) -> list[str]:
    return graphql(FIELDS_QUERY, "-F", f"number={number}")


def views_call(number: str) -> list[str]:
    return graphql(VIEWS_QUERY, "-F", f"number={number}")


def resource_call(url: str) -> list[str]:
    return graphql(RESOURCE_QUERY, "-f", f"url={url}") + ["--jq", ".data.resource.id // empty"]


def add_call(project_id: str, content_id: str) -> list[str]:
    return graphql(ADD_MUTATION, "-f", f"project={project_id}", "-f", f"content={content_id}")


BODY_CALL = ["gh", "api", "graphql", "--input", "-"]


def set_call(args: argparse.Namespace, project_id: str) -> tuple[list[str], str | None]:
    """The child's argv, and the JSON body for its standard input or None."""
    for name, (mutation, flag) in SET_MUTATIONS.items():
        value = getattr(args, name)
        if value is None:
            continue
        if flag is None:
            # the fixed text and a variables object, built by the json module: the
            # value is a JSON number, and nothing is joined into the text (#329)
            body = json.dumps({"query": mutation, "variables": {
                "project": project_id, "item": args.item, "field": args.field, "value": value}},
                allow_nan=False)
            return list(BODY_CALL), body
        # one value=... argument, so a value that starts with a dash stays a value
        return graphql(mutation, "-f", f"project={project_id}", "-f", f"item={args.item}",
                       "-f", f"field={args.field}", flag, f"value={value}"), None
    raise ValueError("no value to set")


# ---- the actions -----------------------------------------------------------


class OwnerError(Exception):
    """The token's login is not the board's owner. The message names neither."""


class ContentError(Exception):
    """The token cannot read the issue or pull request to add. The message names neither."""


LOGIN_CALL = ["gh", "api", "user", "--jq", ".login"]


def check_owner(owner: str, token: str, runner) -> tuple[int, str]:
    """The board is always the viewer's own, so a login given must be the token's
    own (#307). Returns (0, "") when it is, or the failed lookup."""
    if owner == "@me":
        return 0, ""
    code, out, err = runner(LOGIN_CALL, token)
    login = out.strip()
    if code != 0 or not login:
        return code or 1, err or "the token's login was not found"
    if login.lower() != owner.lower():
        raise OwnerError("boards of another owner are not supported")
    return 0, ""


def items(args: argparse.Namespace, token: str, runner) -> tuple[int, str, str]:
    """Pages of up to 100 until --limit, printed as one {"totalCount", "items"} object.
    An answer that cannot be read as a page is passed on as it came."""
    limit, nodes, after, total = int(args.limit), [], None, 0
    while len(nodes) < limit:
        code, out, err = runner(items_call(args.number, min(PAGE, limit - len(nodes)), after), token)
        if code != 0:
            return code, out, err
        try:
            page = json.loads(out)["data"]["viewer"]["projectV2"]["items"]
            total, info = page["totalCount"], page["pageInfo"]
            nodes += page["nodes"]
        except (ValueError, KeyError, TypeError):
            return code, out, err
        if not page["nodes"] or not info.get("hasNextPage") or not info.get("endCursor"):
            break
        after = info["endCursor"]
    text = json.dumps({"totalCount": total, "items": nodes[:limit]}, ensure_ascii=False)
    return 0, text + "\n", ""


def board_id(number: str, token: str, runner) -> tuple[int, str, str]:
    code, out, err = runner(board_call(number, ".data.viewer.projectV2.id"), token)
    project_id = out.strip()
    if code != 0 or not project_id:
        return code or 1, "", err or "the board's id was not found"
    return 0, project_id, ""


def add(args: argparse.Namespace, project_id: str, token: str, runner) -> tuple[int, str, str]:
    code, out, err = runner(resource_call(args.url), token)
    if code != 0 and not REFUSED_RE.search(f"{err}\n{out}"):
        return code, out, err
    content_id = out.strip() if code == 0 else ""
    if not content_id:
        # no fallback to another token (#328)
        raise ContentError("the boards token cannot read that repository's issue or pull request")
    return runner(add_call(project_id, content_id), token)


def act(args: argparse.Namespace, token: str, runner) -> tuple[int, str, str]:
    code, err = check_owner(args.owner, token, runner)
    if code != 0:
        return code, "", err
    if args.action == "items":
        return items(args, token, runner)
    if args.action == "fields":
        return runner(fields_call(args.number), token)
    if args.action == "views":
        return runner(views_call(args.number), token)
    # add and set take the board's node id, not its number
    code, project_id, err = board_id(args.number, token, runner)
    if code != 0:
        return code, "", err
    if args.action == "add":
        return add(args, project_id, token, runner)
    if args.action == "set":
        argv, body = set_call(args, project_id)
        if body is None:
            return runner(argv, token)
        return runner(argv, token, stdin=body)
    raise ValueError(args.action)


def utf8_streams() -> None:
    """A piped stream on Windows encodes as cp1252, and board text may hold any character (#307)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str], runner=run, read=read_token) -> int:
    utf8_streams()
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
    except (OwnerError, ContentError) as exc:
        print(f"board.py: {scrub(str(exc), token)}", file=sys.stderr)
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
    """D1: the token reaches the board, and each read action's own query answers
    (#328). D2: it holds the project scope and no other, and a read only a repository
    scope may make is refused. Rows carry PASS, FAIL or not run, a count, scope names
    and a scrubbed first error line, never a title, a value or a header."""
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
    # each read row: its name, the command as shown, the action's own call, the count's path
    reads = [
        ("D1 items", f"gh api graphql ITEMS_QUERY number={number} first={PAGE}",
         items_call(number, PAGE), ".data.viewer.projectV2.items.totalCount"),
        ("D1 fields", f"gh api graphql FIELDS_QUERY number={number}",
         fields_call(number), ".data.viewer.projectV2.fields.totalCount"),
        ("D1 views", f"gh api graphql VIEWS_QUERY number={number}",
         views_call(number), ".data.viewer.projectV2.views.totalCount"),
    ]
    try:
        code, err = check_owner(owner, token, lambda argv, _token: call(argv))
    except OwnerError as exc:
        code, err = 2, str(exc)
    if code != 0:
        rows.append(("D1 board", " ".join(LOGIN_CALL), "FAIL", error(code, "", err)))
        rows += [(rid, shown, "not run", "the login check failed") for rid, shown, _, _ in reads]
    else:
        code, out, err = call(board_call(number, ".data.viewer.projectV2.number"))
        ok = code == 0 and out.strip() == str(int(number))
        rows.append(("D1 board", f"gh api graphql BOARD_QUERY number={number}",
                     "PASS" if ok else "FAIL",
                     "" if ok else error(code, "", err) if code != 0
                     else "the board's number did not come back"))
        for rid, shown, argv, path in reads:
            # the count alone leaves the child: no title or value reaches a row
            code, out, err = call(argv + ["--jq", path])
            count = out.strip()
            if code != 0:
                rows.append((rid, shown, "FAIL", error(code, "", err)))
            elif not count.isdigit():
                rows.append((rid, shown, "FAIL", "no count in the answer"))
            else:
                rows.append((rid, shown, "PASS", f"count: {count}"))

    argv = ["gh", "api", "-i", "rate_limit"]
    code, out, err = call(argv)
    if code != 0:
        rows.append(("D2 scopes", " ".join(argv), "FAIL", error(code, out, err)))
    else:
        scopes = scopes_from_headers(out)
        if scopes is None:
            rows.append(("D2 scopes", " ".join(argv), "FAIL", "no scope list in the answer"))
        else:
            ok = "project" in scopes and all(s in ALLOWED_SCOPES for s in scopes)
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
