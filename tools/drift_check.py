"""Drift check (#219): a copy against its source of truth, read-only.

Usage:  python tools/drift_check.py [--remote] [--home <folder>]

Prints a header, then one line per pair:

    P7  builders deny entries [project]: differs 2 deny entries
    P1  tools main checkout vs origin/main [repo]: same
    P4  plugin folder [owner-queue]: unreadable no live clone
    P6  research.settings.example.json: skipped optional, no real file

Exit 0: every pair is same (or skipped). Exit 1: any pair differs. Exit 2: a
side could not be read and no pair differs.

What it never does. It writes no file and changes no setting. Every git call
goes through one helper that accepts only read subcommands. It reads
origin/main as last fetched and prints that ref's age; --remote adds one pair
that asks the remote for its main (a network read). A line names a pair, a
folder's last part and a count: never a path, never a line or a rule of a
settings file, never the name of a missing entry.

Where the sides come from (no path is written here):
  - the tools main checkout: from this script's own location, through git
  - every project's main checkout: the owner's list of projects in the user
    configuration folder (the file the dispatch script reads)
  - the user configuration folder: the user profile folder plus .claude
  - the live clone: the CLAUDE_CODE_PLUGIN_DIRS entries of the user settings
    file (that one key is read, no rule)
  - a source of truth in git: origin/main, never a working file

Known gap (pair P9). A role file is compared by its front-matter keys, its
tools list and its headings. A changed sentence under an unchanged heading is
not seen.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ORIGIN = "origin/main"
SAME, DIFFERS, UNREADABLE, SKIPPED = "same", "differs", "unreadable", "skipped"

# The only git subcommands this script may run. None of them writes.
GIT_READ_ONLY = frozenset(
    {"rev-parse", "rev-list", "show", "ls-tree", "ls-files", "diff", "status", "ls-remote", "log"}
)

# Template basename -> (real basename, mode, where it lives, optional)
TEMPLATE_MAP = {
    "builders.settings.example.json": ("builders.settings.json", "settings", "user+project", False),
    "managers.settings.example.json": ("managers.settings.json", "settings", "user+project", False),
    "research.settings.example.json": ("research.settings.json", "settings", "user+project", True),
    "builder-profiles.example.json": ("builder-profiles.json", "keys", "project", True),
    "dispatch.json": ("dispatch.json", "keys", "project", False),
    "dispatch-projects.json": ("dispatch-projects.json", "keys", "user", False),
}
BUILDERS_TEMPLATE = "builders.settings.example.json"
SETTINGS_FILE_RE = re.compile(
    r"(^|.*[.-])(settings|dispatch|dispatch-projects|builder-profiles)(\.local)?\.json$"
)
ABS_PATH_RE = re.compile(r"^([A-Za-z]:[\\/]|\\\\|/\S*$)")


class GitError(Exception):
    pass


class Unreadable(Exception):
    """A side of a pair is absent. The message is a fixed phrase, never a path."""


@dataclass
class Result:
    pair: str
    label: str
    status: str
    count: int = 0
    unit: str = ""
    reason: str = ""

    def line(self) -> str:
        if self.status == DIFFERS:
            tail = f"differs {self.count} {self.unit}".rstrip()
            if self.reason:
                tail += f" ({self.reason})"
        elif self.status in (UNREADABLE, SKIPPED):
            tail = f"{self.status} {self.reason}".rstrip()
        else:
            tail = "same"
        return f"{self.pair:<4}{self.label}: {tail}"


def same_or_differs(pair: str, label: str, count: int, unit: str, reason: str = "") -> Result:
    if count:
        return Result(pair, label, DIFFERS, count, unit, reason)
    return Result(pair, label, SAME)


def unreadable(pair: str, label: str, reason: str) -> Result:
    return Result(pair, label, UNREADABLE, reason=reason)


# ---------------------------------------------------------------- helpers


def git(repo: Path | str, *args: str) -> str:
    if not args or args[0] not in GIT_READ_ONLY:
        raise GitError("subcommand not allowed")
    done = subprocess.run(
        ["git", "--no-optional-locks", "-c", "core.quotepath=false", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    if done.returncode != 0:
        raise GitError(args[0])
    return done.stdout


def norm(path: Path | str) -> str:
    return os.path.normcase(os.path.normpath(str(path)))


def within(path: Path | str, root: Path | str) -> bool:
    p, r = norm(path), norm(root)
    return p == r or p.startswith(r + os.sep)


def real(path: Path | str) -> str:
    return norm(os.path.realpath(str(path)))


def name_of(path: Path | str) -> str:
    return Path(path).name or "folder"


def toplevel(folder: Path | str) -> Path | None:
    try:
        return Path(git(folder, "rev-parse", "--show-toplevel").strip())
    except (GitError, OSError):
        return None


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        raise Unreadable("no such file")
    except (OSError, ValueError):
        raise Unreadable("not readable as JSON")


def show(repo: Path, rel: str) -> str:
    return git(repo, "show", f"{ORIGIN}:{rel}")


def head_of(repo: Path) -> str:
    return git(repo, "rev-parse", "HEAD").strip()


def modified_files(repo: Path, *paths: str) -> int:
    out = git(repo, "status", "--porcelain", "--untracked-files=no", *(["--", *paths] if paths else []))
    return len([ln for ln in out.splitlines() if ln.strip()])


def behind_ahead(repo: Path) -> tuple[int, int]:
    left, right = git(repo, "rev-list", "--left-right", "--count", f"{ORIGIN}...HEAD").split()
    return int(left), int(right)


def rel_real(path: Path | str, root: Path | str) -> str:
    """The path under root, case kept, with forward slashes: a git argument."""
    return os.path.relpath(os.path.realpath(str(path)), os.path.realpath(str(root))).replace(os.sep, "/")


def is_link(path: Path) -> bool:
    parent = Path(os.path.realpath(str(path.parent)))
    return real(path) != norm(parent / path.name)


# ---------------------------------------------------------------- the world


@dataclass
class World:
    home: Path
    cfg: Path
    tools_main: Path | None
    projects: list[Path] | None
    plugin_entries: list[Path] | None
    live_clones: list[Path]
    bad_projects: list[str] = field(default_factory=list)  # listed, but not a git checkout here

    @classmethod
    def find(cls, home: Path, tools_dir: Path) -> "World":
        cfg = home / ".claude"
        tools_main = None
        try:
            common = Path(git(tools_dir, "rev-parse", "--path-format=absolute", "--git-common-dir").strip())
            if common.name == ".git":
                tools_main = common.parent
        except (GitError, OSError):
            pass

        projects = None
        bad_projects: list[str] = []
        try:
            listed = read_json(cfg / "dispatch-projects.json")
            entries = listed.get("projects") if isinstance(listed, dict) else None
            if isinstance(entries, list):
                projects = []
                for entry in entries:
                    if isinstance(entry, str) and entry.strip() and (Path(entry) / ".git").exists():
                        projects.append(Path(entry))
                    else:
                        bad_projects.append(name_of(entry) if isinstance(entry, str) and entry.strip() else "entry")
        except Unreadable:
            projects = None

        plugin_entries = None
        live: list[Path] = []
        try:
            settings = read_json(cfg / "settings.json")
            env = settings.get("env") if isinstance(settings, dict) else None
            value = env.get("CLAUDE_CODE_PLUGIN_DIRS") if isinstance(env, dict) else None
            if isinstance(value, str) and value.strip():
                parts = value.split(";") if ";" in value else [value]
                plugin_entries = [Path(p.strip()) for p in parts if p.strip()]
                for entry in plugin_entries:
                    top = toplevel(entry) if entry.exists() else None
                    if top is not None and norm(top) not in [norm(x) for x in live]:
                        live.append(top)
        except Unreadable:
            plugin_entries = None
        return cls(home, cfg, tools_main, projects, plugin_entries, live, bad_projects)

    def config_repo(self) -> Path | None:
        return self.cfg if (self.cfg / ".git").exists() else None


# ---------------------------------------------------------------- P1 to P4: which commit


def commit_pair(pair: str, label: str, repo: Path) -> Result:
    try:
        behind, ahead = behind_ahead(repo)
        modified = modified_files(repo)
    except (GitError, OSError):
        return unreadable(pair, label, "no origin/main ref")
    return same_or_differs(pair, label, behind + ahead + modified, "commits+files")


def p1(w: World) -> list[Result]:
    if w.tools_main is None:
        return [unreadable("P1", "tools main checkout vs origin/main", "no tools main checkout")]
    return [commit_pair("P1", f"tools main checkout vs origin/main [{name_of(w.tools_main)}]", w.tools_main)]


def p2(w: World) -> list[Result]:
    if not w.live_clones:
        return [unreadable("P2", "live clone vs origin/main", "no live clone")]
    return [commit_pair("P2", f"live clone vs origin/main [{name_of(c)}]", c) for c in w.live_clones]


def p3(w: World) -> list[Result]:
    label = "live clone vs main checkout"
    if w.tools_main is None or not w.live_clones:
        return [unreadable("P3", label, "needs the main checkout and a live clone")]
    out = []
    for clone in w.live_clones:
        try:
            a, b = head_of(w.tools_main), head_of(clone)
            if a == b:
                out.append(Result("P3", f"{label} [{name_of(clone)}]", SAME))
                continue
            try:
                left, right = git(w.tools_main, "rev-list", "--left-right", "--count", f"{a}...{b}").split()
                out.append(same_or_differs("P3", f"{label} [{name_of(clone)}]", int(left) + int(right), "commits"))
            except GitError:
                out.append(Result("P3", f"{label} [{name_of(clone)}]", DIFFERS, 1, "heads"))
        except (GitError, OSError):
            out.append(unreadable("P3", f"{label} [{name_of(clone)}]", "no HEAD"))
    return out


def p4(w: World) -> list[Result]:
    if w.plugin_entries is None:
        return [unreadable("P4", "plugin folder", "no plugin folder setting")]
    out = []
    for entry in w.plugin_entries:
        label = f"plugin folder [{name_of(entry)}]"
        if not entry.exists():
            out.append(Result("P4", label, DIFFERS, 1, "files", "missing"))
            continue
        top = toplevel(entry)
        if top is None or not any(norm(top) == norm(c) for c in w.live_clones):
            out.append(Result("P4", label, DIFFERS, 1, "files", "not in the live clone"))
            continue
        rel = rel_real(entry, top)
        try:
            out.append(same_or_differs("P4", label, modified_files(top, rel), "files"))
        except (GitError, OSError):
            out.append(unreadable("P4", label, "git could not read it"))
    return out


# ---------------------------------------------------------------- P5: version of the mod


def plugin_version(path: Path) -> tuple[str, str] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return str(data.get("name", "")), str(data.get("version", ""))
    except (OSError, ValueError, AttributeError):
        return None


def other_copies(cfg: Path, name: str, skip: list[str]) -> list[tuple[Path, str]]:
    found = []
    for sub in ("mods", "dev-mods", "plugins"):
        base = cfg / sub
        if not base.is_dir():
            continue
        depth0 = len(base.parts)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
            if len(Path(dirpath).parts) - depth0 >= 6:
                dirnames[:] = []
            if Path(dirpath).name == ".claude-plugin" and "plugin.json" in filenames:
                got = plugin_version(Path(dirpath) / "plugin.json")
                if got and got[0] == name and not any(within(dirpath, s) for s in skip):
                    found.append((Path(dirpath).parent, got[1]))
    return found


def p5(w: World) -> list[Result]:
    if w.plugin_entries is None or not w.live_clones:
        return [unreadable("P5", "plugin version", "no live clone")]
    out = []
    for entry in w.plugin_entries:
        got = plugin_version(entry / ".claude-plugin" / "plugin.json")
        if got is None:
            out.append(unreadable("P5", f"plugin version [{name_of(entry)}]", "no plugin.json"))
            continue
        name, running = got
        label = f"plugin version [{name}]"
        top = toplevel(entry)
        if top is None:
            out.append(unreadable("P5", label, "not a git folder"))
            continue
        rel = rel_real(entry, top)
        try:
            data = json.loads(show(top, f"{rel}/.claude-plugin/plugin.json"))
            source = str(data.get("version", ""))
        except (GitError, ValueError, OSError):
            out.append(unreadable("P5", label, "no source on origin/main"))
            continue
        count = int(running != source)
        count += sum(1 for _, v in other_copies(w.cfg, name, [str(entry)]) if v != source)
        out.append(same_or_differs("P5", label, count, "copies"))
    return out


# ---------------------------------------------------------------- P6, P7: settings and templates


def canon(value: object) -> str:
    if isinstance(value, str):
        return "<path>" if ABS_PATH_RE.match(value) else value
    return json.dumps(value, sort_keys=True)


def flatten(node: object, prefix: str = "", keys_depth: int | None = None, depth: int = 0) -> set[str]:
    items: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if str(key).startswith("//"):
                continue
            path = f"{prefix}.{key}"
            items.add(f"key:{path}")
            if keys_depth is None or depth + 1 < keys_depth:
                items |= flatten(value, path, keys_depth, depth + 1)
    elif keys_depth is None:
        if isinstance(node, list):
            for entry in node:
                items.add(f"{prefix}[]={canon(entry)}")
        else:
            items.add(f"{prefix}={canon(node)}")
    return items


def settings_difference(template: object, realfile: object, mode: str) -> int:
    if mode == "keys":
        return len(flatten(template, keys_depth=1) ^ flatten(realfile, keys_depth=1))
    t, r = flatten(template), flatten(realfile)
    allow_marker = ".permissions.allow[]="
    t_allow = {i for i in t if i.startswith(allow_marker)}
    r_allow = {i for i in r if i.startswith(allow_marker)}
    others = (t - t_allow) ^ (r - r_allow)
    return len(others) + len(t_allow - r_allow)


def template_files(tools: Path) -> dict[str, str]:
    tree = git(tools, "ls-tree", "-r", "--name-only", ORIGIN).splitlines()
    return {
        Path(p).name: p
        for p in tree
        if Path(p).name in TEMPLATE_MAP and Path(p).parent.name == "templates"
    }


def real_locations(w: World, real_name: str, where: str) -> list[tuple[str, Path]]:
    places: list[tuple[str, Path]] = []
    if "user" in where:
        places.append(("user", w.cfg / real_name))
    if "project" in where:
        for project in w.projects or []:
            places.append((name_of(project), project / ".claude" / real_name))
    return places


def p6(w: World) -> list[Result]:
    if w.tools_main is None:
        return [unreadable("P6", "settings templates", "no tools main checkout")]
    try:
        templates = template_files(w.tools_main)
    except (GitError, OSError):
        return [unreadable("P6", "settings templates", "no origin/main ref")]
    out = []
    for tname, (rname, mode, where, optional) in TEMPLATE_MAP.items():
        label = f"{tname}"
        if tname not in templates:
            out.append(unreadable("P6", label, "no template on origin/main"))
            continue
        if "project" in where and w.projects is None:
            out.append(unreadable("P6", label, "no list of projects"))
            continue
        try:
            template = json.loads(show(w.tools_main, templates[tname]))
        except (GitError, ValueError):
            out.append(unreadable("P6", label, "template not readable"))
            continue
        existing = [(who, p) for who, p in real_locations(w, rname, where) if p.is_file()]
        if not existing:
            if optional:
                out.append(Result("P6", label, SKIPPED, reason="optional, no real file"))
            elif where == "project":
                for who, _ in real_locations(w, rname, where):
                    out.append(unreadable("P6", f"{label} [{who}]", "no real file"))
            else:
                out.append(unreadable("P6", label, "no real file"))
            continue
        have = {who for who, _ in existing}
        for who, _ in real_locations(w, rname, where):
            if who in have:
                continue
            if where == "project" and not optional:
                out.append(unreadable("P6", f"{label} [{who}]", "no real file"))
            elif where == "user+project":
                # the file may live at either place; a line says this place holds none
                out.append(Result("P6", f"{label} [{who}]", SKIPPED, reason="no copy here, another place holds it"))
        for who, path in existing:
            try:
                count = settings_difference(template, read_json(path), mode)
            except Unreadable as exc:
                out.append(unreadable("P6", f"{label} [{who}]", str(exc)))
                continue
            out.append(same_or_differs("P6", f"{label} [{who}]", count, "entries"))
    return out


def deny_set(data: object) -> set[str]:
    perms = data.get("permissions") if isinstance(data, dict) else None
    deny = perms.get("deny") if isinstance(perms, dict) else None
    return {str(x).strip() for x in deny} if isinstance(deny, list) else set()


def builders_file_of(project: Path) -> Path:
    rel = ".claude/builders.settings.json"
    try:
        data = read_json(project / ".claude" / "dispatch.json")
        if isinstance(data, dict) and isinstance(data.get("buildersSettings"), str) and data["buildersSettings"]:
            rel = data["buildersSettings"]
    except Unreadable:
        pass
    return project / rel


def p7(w: World) -> list[Result]:
    label = "builders deny entries"
    if w.tools_main is None:
        return [unreadable("P7", label, "no tools main checkout")]
    try:
        templates = template_files(w.tools_main)
        required = deny_set(json.loads(show(w.tools_main, templates[BUILDERS_TEMPLATE])))
    except (GitError, ValueError, KeyError, OSError):
        return [unreadable("P7", label, "no builders template on origin/main")]
    places: list[tuple[str, Path]] = []
    if (w.cfg / "builders.settings.json").is_file():
        places.append(("user", w.cfg / "builders.settings.json"))
    if w.projects is None:
        out = [unreadable("P7", label, "no list of projects")]
    else:
        out = []
        places += [(name_of(p), builders_file_of(p)) for p in w.projects]
    for who, path in places:
        try:
            missing = len(required - deny_set(read_json(path)))
        except Unreadable as exc:
            out.append(unreadable("P7", f"{label} [{who}]", str(exc)))
            continue
        out.append(same_or_differs("P7", f"{label} [{who}]", missing, "deny entries"))
    return out


# ---------------------------------------------------------------- P8: tracked file against its live copy


def tracked_settings(repo: Path, top_level_only: bool) -> list[str]:
    files = [f for f in git(repo, "ls-files", "-z").split("\0") if f]
    keep = []
    for f in files:
        if not SETTINGS_FILE_RE.match(Path(f).name):
            continue
        if top_level_only and "/" in f:
            continue
        if not top_level_only and not f.startswith(".claude/"):
            continue
        keep.append(f)
    return keep


def numstat_lines(repo: Path, rel: str, *flags: str) -> int:
    total = 0
    for ln in git(repo, "diff", *flags, "--ignore-cr-at-eol", "--numstat", "--", rel).splitlines():
        a, d, *_ = ln.split("\t")
        total += (int(a) + int(d)) if a.isdigit() and d.isdigit() else 1
    return total


def p8(w: World) -> list[Result]:
    repos: list[tuple[str, Path, bool]] = []
    out: list[Result] = []
    if w.projects is None:
        out.append(unreadable("P8", "tracked settings vs live copy", "no list of projects"))
    else:
        repos += [(name_of(p), p, False) for p in w.projects]
    cfg_repo = w.config_repo()
    if cfg_repo is None:
        out.append(unreadable("P8", "tracked settings vs live copy [user]", "no configuration repository"))
    else:
        repos.append(("user", cfg_repo, True))
    for who, repo, top_only in repos:
        try:
            files = tracked_settings(repo, top_only)
            if not files:
                out.append(Result("P8", f"tracked settings vs live copy [{who}]", SAME))
            for rel in files:
                label = f"{Path(rel).name} [{who}]"
                total = numstat_lines(repo, rel, "HEAD")
                out.append(same_or_differs("P8", f"tracked vs live {label}", total, "lines", "uncommitted"))
        except (GitError, OSError):
            out.append(unreadable("P8", f"tracked settings vs live copy [{who}]", "git could not read it"))
    return out


# ---------------------------------------------------------------- P9: role files against templates


def split_tools(value: str) -> set[str]:
    return {t.strip() for t in value.strip().strip("[]").split(",") if t.strip()}


def role_structure(text: str) -> tuple[set[str], set[str], set[str]]:
    lines = text.replace("\r\n", "\n").split("\n")
    front: list[str] = []
    body = lines
    if lines and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            front, body = lines[1:end], lines[end + 1:]
    keys: set[str] = set()
    tools: set[str] = set()
    current = ""
    for ln in front:
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", ln)
        if m:
            current = m.group(1)
            keys.add(current)
            if current == "tools":
                tools |= split_tools(m.group(2))
            continue
        m = re.match(r"^\s*-\s*(.+)$", ln)
        if m and current == "tools":
            tools.add(m.group(1).strip())
    headings: set[str] = set()
    fenced = False
    for ln in body:
        if ln.lstrip().startswith("```"):
            fenced = not fenced
            continue
        m = None if fenced else re.match(r"^#{1,6}\s+(.*\S)", ln)
        if m:
            headings.add(re.sub(r"\s+", " ", m.group(1)).lower())
    return keys, tools, headings


def p9(w: World) -> list[Result]:
    label = "role files vs templates"
    if w.tools_main is None:
        return [unreadable("P9", label, "no tools main checkout")]
    if w.projects is None:
        return [unreadable("P9", label, "no list of projects")]
    try:
        tree = git(w.tools_main, "ls-tree", "-r", "--name-only", ORIGIN).splitlines()
    except (GitError, OSError):
        return [unreadable("P9", label, "no origin/main ref")]
    templates = {
        Path(p).stem: p
        for p in tree
        if p.endswith(".md") and Path(p).parent.name == "agents" and Path(p).parent.parent.name == "templates"
    }
    if not templates:
        return [unreadable("P9", label, "no role templates on origin/main")]
    out = []
    for project in w.projects:
        agents = project / ".claude" / "agents"
        if not agents.is_dir():
            out.append(unreadable("P9", f"{label} [{name_of(project)}]", "no agents folder"))
            continue
        for role in sorted(agents.glob("*.md")):
            match = next((t for t in templates if role.stem == t or role.stem.endswith("-" + t)), None)
            if match is None:
                continue
            try:
                a = role_structure(role.read_text(encoding="utf-8-sig"))
                b = role_structure(show(w.tools_main, templates[match]))
            except (OSError, GitError):
                out.append(unreadable("P9", f"{role.name} [{name_of(project)}]", "not readable"))
                continue
            count = sum(len(x ^ y) for x, y in zip(a, b))
            out.append(same_or_differs("P9", f"{role.name} [{name_of(project)}]", count, "headings and keys"))
    return out


# ---------------------------------------------------------------- P10, P11: links


def tracked_through_links(top: Path) -> int:
    root = real(top)
    cache: dict[str, bool] = {}
    count = 0
    for rel in [f for f in git(top, "ls-files", "-z").split("\0") if f]:
        folder = os.path.dirname(rel)
        if folder not in cache:
            cache[folder] = not within(real(top / folder) if folder else root, root)
        if cache[folder]:
            count += 1
            continue
        path = top / rel
        if os.path.islink(path) and not within(real(path), root):
            count += 1
    return count


def p10(w: World) -> list[Result]:
    repos: list[tuple[str, Path]] = []
    out: list[Result] = []
    if w.projects is None:
        out.append(unreadable("P10", "tracked paths through links", "no list of projects"))
    else:
        repos += [(name_of(p), p) for p in w.projects]
    cfg_repo = w.config_repo()
    if cfg_repo is None:
        out.append(unreadable("P10", "tracked paths through links [user]", "no configuration repository"))
    else:
        repos.append(("user", cfg_repo))
    for who, repo in repos:
        try:
            out.append(same_or_differs("P10", f"tracked paths through links [{who}]", tracked_through_links(repo), "tracked files"))
        except (GitError, OSError):
            out.append(unreadable("P10", f"tracked paths through links [{who}]", "git could not read it"))
    return out


def p11(w: World) -> list[Result]:
    label = "config folder links vs checkouts"
    if w.tools_main is None:
        return [unreadable("P11", label, "no tools main checkout")]
    if not w.cfg.is_dir():
        return [unreadable("P11", label, "no configuration folder")]
    candidates: list[Path] = []
    if (w.cfg / "agents").exists():
        candidates.append(w.cfg / "agents")
    for sub in ("hooks", "skills"):
        folder = w.cfg / sub
        if folder.is_dir():
            candidates += sorted(folder.iterdir())
    # A good target is inside the main checkout or a live clone the script lists,
    # and its folder holds a tracked file on origin/main in that checkout.
    roots = [w.tools_main] + [c for c in w.live_clones if norm(c) != norm(w.tools_main)]
    bad = 0
    try:
        for entry in candidates:
            if not is_link(entry):
                continue
            target = Path(os.path.realpath(str(entry)))
            holder = next((r for r in roots if within(target, real(r))), None)
            if not target.exists() or holder is None:
                bad += 1
                continue
            rel = rel_real(target, holder)
            spec = [] if rel == "." else ["--", rel + "/"]
            if not git(holder, "ls-tree", "-r", "--name-only", ORIGIN, *spec).strip():
                bad += 1
    except (GitError, OSError):
        return [unreadable("P11", label, "git could not read it")]
    return [same_or_differs("P11", label, bad, "links")]


# ---------------------------------------------------------------- the run


def p0(w: World) -> list[Result]:
    label = "origin/main vs the remote"
    if w.tools_main is None:
        return [unreadable("P0", label, "no tools main checkout")]
    try:
        asked = git(w.tools_main, "ls-remote", "origin", "refs/heads/main").splitlines()
        local = git(w.tools_main, "rev-parse", ORIGIN).strip()
    except (GitError, OSError, subprocess.TimeoutExpired):
        return [unreadable("P0", label, "the remote could not be asked")]
    # a pattern matches the tail of a ref name, so keep only the exact branch
    heads = [ln.split("\t")[0] for ln in asked if ln.split("\t")[-1].strip() == "refs/heads/main"]
    if not heads:
        return [unreadable("P0", label, "the remote has no main")]
    return [same_or_differs("P0", label, int(heads[0] != local), "heads")]


PAIRS = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11]
PROJECT_PAIRS = (p6, p7, p8, p9, p10)  # the pairs that walk the owner's list of projects


def fetch_age(w: World) -> str:
    if w.tools_main is None:
        return "unknown"
    try:
        path = Path(git(w.tools_main, "rev-parse", "--path-format=absolute", "--git-path", "FETCH_HEAD").strip())
        seconds = max(0, int(time.time() - path.stat().st_mtime))
    except (GitError, OSError):
        return "never fetched, or unknown"
    for size, word in ((86400, "day"), (3600, "hour"), (60, "minute")):
        if seconds >= size:
            return f"{seconds // size} {word}(s) ago"
    return "under a minute ago"


def run(home: Path, tools_dir: Path, remote: bool = False) -> tuple[str, list[Result]]:
    try:
        world = World.find(home, tools_dir)
    except Exception:  # a malformed file never stops the run: every pair then says unreadable
        world = World(home, home / ".claude", None, None, None, [])
    results: list[Result] = []
    pairs = ([p0] if remote else []) + PAIRS
    for fn in pairs:
        try:
            results += fn(world)
            if fn in PROJECT_PAIRS:
                results += [unreadable(fn.__name__.upper(), f"listed project [{n}]", "not a git checkout")
                            for n in world.bad_projects]
        except Exception as exc:  # one pair failing never stops the others
            results.append(unreadable(fn.__name__.upper(), "pair", type(exc).__name__))
    return fetch_age(world), results


def exit_code(results: list[Result]) -> int:
    if any(r.status == DIFFERS for r in results):
        return 1
    if any(r.status == UNREADABLE for r in results):
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--remote", action="store_true", help="also ask the remote for its main (a network read)")
    parser.add_argument("--home", default=None, help="the user profile folder; for tests")
    args = parser.parse_args(argv)
    home = Path(args.home) if args.home else Path.home()
    age, results = run(home, Path(__file__).resolve().parent, args.remote)
    print(f"drift_check: origin/main as last fetched: {age}")
    for r in results:
        print(r.line())
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
