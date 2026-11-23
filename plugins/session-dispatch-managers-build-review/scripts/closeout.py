"""Close out a builder: check its worktree, remove it when that is safe, say why when not.

    closeout.py <main checkout> <builder name> [--branch <name>]... [--apply]
    closeout.py <main checkout> --list

Python 3.8 or later, standard library only, so any project's interpreter runs it.

Without --apply it is a dry run: it prints what it would do and changes nothing.
--list takes no builder name, changes nothing, prints every worktree under
<main checkout>/.claude/worktrees with its verdict, and ends with one count line.

It acts only on a worktree that `git worktree list --porcelain` names and that
sits directly under <main checkout>/.claude/worktrees. A worktree is removed
only when all of these hold:

- its branch is merged: the tip is the head of a merged PR or an ancestor of
  one, or the tip (a detached HEAD included) is an ancestor of the remote main
  branch and so holds no commit of its own; a detached HEAD also passes when
  it is exactly a merged PR's head;
- `git status --porcelain` prints nothing for it;
- it is not locked;
- it holds no folder link (junction or folder symlink) that points out of it,
  no link that cannot be resolved, and its own top folder is not a link;
- on Windows, at apply time, no file in it is open and no process runs in it
  (the folder is renamed to a sibling and back).

There is no force option of any kind. The only deletes are
`git worktree remove` without --force and, after it, `git branch -D` of the
builder's local branch on the same merged test. It never fetches, pushes,
deletes a remote ref or prunes, and deletes no file itself.

Exit codes: 0 all done (or would be); 1 something refused or unknown;
2 the run itself is refused (bad arguments, not a main checkout);
3 a removal or the in-use check did not finish: the output says what is left.
"""
import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time

WIN = sys.platform == "win32"
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
INUSE_SUFFIX = ".closeout-inuse"
PR_LIMIT = 1000
NAME_SURROGATE = 0x20000000  # IsReparseTagNameSurrogate: junctions and symlinks
FILE_ATTRIBUTE_DIRECTORY = 0x10

MERGED, EMPTY, UNKNOWN, REFUSED = "merged", "no commit of its own", "unknown", "refused"


# ---- plumbing -----------------------------------------------------------------

def run(args, cwd):
    """Run a command; never raise. Returns (code, stdout, stderr)."""
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", stdin=subprocess.DEVNULL, timeout=300)
        return r.returncode, r.stdout, r.stderr
    except (OSError, subprocess.SubprocessError) as e:
        return 127, "", str(e)


def git(cwd, *args):
    return run(["git", *args], cwd)


def norm(path):
    return os.path.normcase(os.path.realpath(path))


def literal(path):
    """A path's key: its parent resolved, its own last part not (it may be a link)."""
    path = os.path.abspath(path).rstrip("/\\")
    return os.path.join(norm(os.path.dirname(path)), os.path.normcase(os.path.basename(path)))


def is_link(path):
    """A symlink or a junction, judged by lstat alone: never follows."""
    st = os.lstat(path)
    if stat.S_ISLNK(st.st_mode):
        return True
    return bool(getattr(st, "st_reparse_tag", 0) & NAME_SURROGATE)


def is_folder_link(path):
    """For a link: does it name a folder? On Windows, by lstat's directory bit."""
    if WIN:
        return bool(os.lstat(path).st_file_attributes & FILE_ATTRIBUTE_DIRECTORY)
    return stat.S_ISDIR(os.stat(path).st_mode)


def inside(path, top):
    try:
        return os.path.commonpath([path, top]) == top
    except ValueError:  # another drive
        return False


def scan_links(top):
    """Problems with links under top, found without following any. [] means none."""
    problems, top_real, stack = [], norm(top), [top]
    while stack:
        folder = stack.pop()
        try:
            entries = list(os.scandir(folder))
        except OSError as e:
            return problems + [f"scan error at {folder}: {e.strerror or e}"]
        for entry in entries:
            try:
                if is_link(entry.path):
                    target = os.path.realpath(entry.path)
                    if not os.path.exists(target):
                        problems.append(f"link {entry.path} cannot be resolved")
                    elif is_folder_link(entry.path) and not inside(os.path.normcase(target), top_real):
                        problems.append(f"folder link {entry.path} points out to {target}")
                elif entry.is_dir(follow_symlinks=False):
                    stack.append(entry.path)
            except OSError as e:
                problems.append(f"scan error at {entry.path}: {e.strerror or e}")
    return problems


def parse_worktrees(text):
    out = []
    for block in text.split("\n\n"):
        lines = [x for x in block.splitlines() if x]
        if not lines or not lines[0].startswith("worktree "):
            continue
        wt = {"path": lines[0][len("worktree "):], "branch": None, "detached": False,
              "locked": None, "head": None, "bare": False}
        for line in lines[1:]:
            key, _, val = line.partition(" ")
            if key == "HEAD":
                wt["head"] = val
            elif key == "branch":
                wt["branch"] = val[len("refs/heads/"):] if val.startswith("refs/heads/") else val
            elif key == "detached":
                wt["detached"] = True
            elif key == "locked":
                wt["locked"] = val or "no reason given"
            elif key == "bare":
                wt["bare"] = True
        out.append(wt)
    return out


# ---- the project --------------------------------------------------------------

class Refusal(Exception):
    pass


class Project:
    def __init__(self, main):
        self.main = os.path.abspath(main)
        code, top, _ = git(self.main, "rev-parse", "--show-toplevel")
        if code != 0 or norm(top.strip()) != norm(self.main):
            raise Refusal(f"{main} is not the top of a git checkout")
        _, gdir, _ = git(self.main, "rev-parse", "--absolute-git-dir")
        _, cdir, _ = git(self.main, "rev-parse", "--git-common-dir")
        cdir = cdir.strip()
        if not os.path.isabs(cdir):
            cdir = os.path.join(self.main, cdir)
        if norm(gdir.strip()) != norm(cdir):
            raise Refusal(f"{main} is a linked worktree, not the main checkout")
        self.root = os.path.join(self.main, ".claude", "worktrees")
        self.root_key = os.path.join(norm(self.main), ".claude", "worktrees")
        if os.path.lexists(self.root) and norm(self.root) != self.root_key:
            raise Refusal(f"{self.root} is, or sits under, a link; nothing is acted on")
        code, ref, _ = git(self.main, "rev-parse", "--abbrev-ref", "refs/remotes/origin/HEAD")
        ref = ref.strip()
        if code != 0 or not ref.startswith("origin/"):
            raise Refusal("cannot tell the main branch: refs/remotes/origin/HEAD is not set "
                          f"(git -C {self.main} remote set-head origin --auto sets it)")
        self.main_ref = ref
        code, out, err = git(self.main, "worktree", "list", "--porcelain")
        if code != 0:
            raise Refusal("git worktree list failed: " + err.strip())
        self.worktrees = parse_worktrees(out)
        self.prs = None
        self.pr_note = ""

    def under_root(self, wt):
        p = literal(wt["path"])
        return os.path.dirname(p) == self.root_key and p != literal(self.main)

    def load_prs(self):
        exe = shutil.which("gh")
        if exe is None:
            self.pr_note = "gh not found"
            return
        code, out, err = run([exe, "pr", "list", "--state", "merged", "--limit", str(PR_LIMIT),
                              "--json", "number,headRefName,headRefOid"], self.main)
        if code != 0:
            self.pr_note = "gh failed: " + (err.strip().splitlines() or ["exit %d" % code])[-1]
            return
        try:
            prs = json.loads(out)
            self.prs = [p for p in prs if isinstance(p, dict) and p.get("headRefOid")]
        except ValueError:
            self.pr_note = "gh printed no JSON"
            return
        if len(prs) >= PR_LIMIT:
            self.pr_note = f"the merged PR list stopped at {PR_LIMIT} and may be cut"

    def oid(self, rev):
        code, out, _ = git(self.main, "rev-parse", "--verify", "--quiet", rev + "^{commit}")
        return out.strip() if code == 0 else None

    def ancestor(self, a, b):
        return git(self.main, "merge-base", "--is-ancestor", a, b)[0] == 0

    def merge_state(self, tip, branch):
        """(state, detail) for a commit: MERGED, EMPTY, UNKNOWN or REFUSED."""
        if tip is None:
            return REFUSED, "its commit cannot be read"
        if self.prs is not None:
            mine = [p for p in self.prs if p["headRefOid"] == tip]
            if mine:
                return MERGED, f"PR #{mine[0]['number']}"
        if self.ancestor(tip, self.main_ref):
            return EMPTY, f"tip is on {self.main_ref}"
        if branch is None:
            if self.prs is None:
                return UNKNOWN, self.pr_note
            return REFUSED, f"detached at {tip[:12]}: not on {self.main_ref} and not a merged PR's head"
        if self.prs is None:
            return UNKNOWN, self.pr_note
        named = [p for p in self.prs if p.get("headRefName") == branch]
        missing = []
        for p in named:
            if self.oid(p["headRefOid"]) is None:
                missing.append(p)
            elif self.ancestor(tip, p["headRefOid"]):
                return MERGED, f"PR #{p['number']}"
        if missing:
            n = missing[0]["number"]
            return UNKNOWN, (f"PR #{n} head not local; bring it with: "
                             f"git -C {self.main} fetch origin pull/{n}/head")
        if named:
            return REFUSED, f"commits after merged PR #{named[0]['number']}"
        note = f" ({self.pr_note})" if self.pr_note else ""
        return REFUSED, "no merged PR" + note


# ---- verdicts -----------------------------------------------------------------

class Verdict:
    def __init__(self, name, path, branch=None):
        self.name, self.path, self.branch = name, path, branch
        self.state, self.detail, self.reasons = None, "", []
        self.removed = False

    @property
    def removable(self):
        return self.state in (MERGED, EMPTY) and not self.reasons


def judge(project, wt):
    name = os.path.basename(wt["path"].rstrip("/\\"))
    v = Verdict(name, wt["path"], wt["branch"])
    path = wt["path"]
    if not os.path.lexists(path):
        v.reasons.append("git record only: the folder is gone "
                         "(pruning it is the manager's command)")
        return v
    try:
        if is_link(path):
            v.reasons.append(f"the worktree's top folder is a link to {os.path.realpath(path)}")
            return v
    except OSError as e:
        v.reasons.append(f"scan error at {path}: {e.strerror or e}")
        return v
    if wt["locked"]:
        v.reasons.append(f"locked: {wt['locked']}")
    v.reasons.extend(scan_links(path))
    code, out, err = git(path, "status", "--porcelain")
    if code != 0:
        v.reasons.append("git status failed: " + err.strip())
    elif out.strip():
        lines = out.rstrip("\n").splitlines()
        shown = ", ".join(x.strip() for x in lines[:5]) + (" ..." if len(lines) > 5 else "")
        v.reasons.append(f"uncommitted: {len(lines)} line(s) of git status: {shown}")
    if wt["bare"]:
        v.reasons.append("a bare entry")
        return v
    tip = project.oid("refs/heads/" + wt["branch"]) if wt["branch"] else project.oid(wt["head"] or "")
    v.state, v.detail = project.merge_state(tip, wt["branch"])
    return v


def describe(v, apply):
    head = f"{v.name}:"
    if v.removed:
        return f"{head} removed ({v.state}, {v.detail})"
    if v.state is None or v.reasons or v.state in (UNKNOWN, REFUSED):
        reasons = list(v.reasons)
        if v.state == UNKNOWN:
            reasons.insert(0, "unknown: " + v.detail)
        elif v.state == REFUSED:
            reasons.insert(0, v.detail)
        elif v.state in (MERGED, EMPTY):
            reasons.append(f"({v.state}, {v.detail})")
        return f"{head} refused: " + "; ".join(reasons)
    extra = "; the in-use check runs at apply time" if WIN and not apply else ""
    return f"{head} would remove ({v.state}, {v.detail}){extra}"


# ---- acting -------------------------------------------------------------------

def leftover(path):
    found = []
    for folder, dirs, files in os.walk(path):
        for x in dirs + files:
            found.append(os.path.relpath(os.path.join(folder, x), path).replace(os.sep, "/"))
    found.sort()
    return f"{len(found)} entries" + (": " + ", ".join(found[:10]) if found else "") + \
        (" ..." if len(found) > 10 else "")


def in_use_check(path):
    """Windows: rename the folder to a sibling and back. Returns (ok, message, fatal)."""
    sibling = path.rstrip("/\\") + INUSE_SUFFIX
    if os.path.lexists(sibling):
        return False, f"in-use check: {sibling} already exists; nothing renamed", False
    try:
        os.rename(path, sibling)
    except OSError:
        return False, ("in use: a file in it is open or a process runs in it. Close any terminal "
                       "or editor in the folder, check that the builder's session has ended, "
                       "and run again"), False
    for attempt in range(5):
        try:
            os.rename(sibling, path)
            return True, "", False
        except OSError:
            time.sleep(0.5 * (attempt + 1))
    return False, (f"in-use check did not finish: the folder is at {sibling}. "
                   f"Rename {sibling} back to {path} to put it back. Nothing was deleted"), True


def still_listed(project, path):
    code, out, _ = git(project.main, "worktree", "list", "--porcelain")
    if code != 0:
        return True
    return any(literal(w["path"]) == literal(path) for w in parse_worktrees(out))


def delete_branch(project, branch, worktrees):
    """Delete a local branch on the merged test. Returns (deleted, reason)."""
    if any(w["branch"] == branch for w in worktrees):
        return False, f"branch {branch} is checked out in a worktree"
    tip = project.oid("refs/heads/" + branch)
    if tip is None:
        return False, f"branch {branch} not found"
    state, detail = project.merge_state(tip, branch)
    if state not in (MERGED, EMPTY):
        return False, f"branch {branch}: {state}: {detail}"
    code, _, err = git(project.main, "branch", "-D", branch)
    if code != 0:
        return False, f"branch {branch}: git branch -D failed: {err.strip()}"
    return True, f"branch {branch} deleted ({state}, {detail})"


def remove(project, v):
    """Remove one judged, removable worktree. Returns an exit code contribution."""
    if WIN:
        ok, msg, fatal = in_use_check(v.path)
        if not ok:
            v.reasons.append(msg)
            print(describe(v, True))
            return 3 if fatal else 1
    code, _, err = git(project.main, "worktree", "remove", v.path)
    gone = not os.path.lexists(v.path)
    listed = still_listed(project, v.path)
    if gone and not listed:
        v.removed = True
        print(describe(v, True))
        return 0
    parts = [f"{v.name}: removal did not finish (git exit {code}{': ' + err.strip() if err.strip() else ''})"]
    parts.append(f"left: {leftover(v.path)}" if not gone else "the folder is gone")
    parts.append("git still lists it" if listed else "git no longer lists it")
    print("; ".join(parts))
    return 3


# ---- modes --------------------------------------------------------------------

def list_mode(project):
    project.load_prs()
    counts = {MERGED: 0, EMPTY: 0, UNKNOWN: 0}
    refused, known, outside = [], set(), 0
    for wt in project.worktrees:
        if literal(wt["path"]) == literal(project.main):
            continue
        if not project.under_root(wt):
            outside += 1
            continue
        known.add(literal(wt["path"]))
        v = judge(project, wt)
        line = describe(v, False)
        print(line)
        if v.state in counts:
            counts[v.state] += 1
        if not v.removable:
            refused.append(line)
    if os.path.isdir(project.root):
        for entry in sorted(os.listdir(project.root)):
            path = os.path.join(project.root, entry)
            if literal(path) in known:
                continue
            note = "unknown to git: listed, never removed"
            if entry.endswith(INUSE_SUFFIX):
                base = entry[: -len(INUSE_SUFFIX)]
                note = (f"an interrupted in-use check of {base}: rename it back to "
                        f"{os.path.join(project.root, base)}")
            try:
                if is_link(path):
                    note += f"; it is itself a link to {os.path.realpath(path)}"
                elif os.path.isdir(path):
                    links = scan_links(path)
                    note += ("; " + "; ".join(links)) if links else "; no link points out"
            except OSError as e:
                note += f"; scan error: {e.strerror or e}"
            line = f"{entry}: {note}"
            print(line)
            refused.append(line)
    if outside:
        print(f"{outside} worktree(s) outside {project.root} are not looked at")
    print_refused(refused)
    print(f"count: merged and still there {counts[MERGED]}; "
          f"no commit of its own {counts[EMPTY]}; unknown {counts[UNKNOWN]}")
    if project.prs is None:
        print(f"note: {project.pr_note}")
        return 1
    return 0


def print_refused(lines):
    if lines:
        print("refused, for the owner queue:")
        for line in lines:
            print("- " + line)


def builder_mode(project, name, branches, apply):
    path = os.path.join(project.root, name)
    match = [w for w in project.worktrees if literal(w["path"]) == literal(path)]
    if not match:
        if os.path.lexists(path):
            line = f"{name}: refused: unknown to git: listed, never removed"
        else:
            line = f"{name}: refused: no worktree of that name under {project.root}"
        print(line)
        print_refused([line])
        return 1
    wt = match[0]
    project.load_prs()
    v = judge(project, wt)
    code = 0
    if project.prs is None:
        # nothing is removed when gh did not answer
        if v.state in (MERGED, EMPTY):
            v.state, v.detail = UNKNOWN, project.pr_note
        print(describe(v, apply))
        print_refused([describe(v, apply)])
        return 1
    if not v.removable:
        print(describe(v, apply))
        code = 1
    elif not apply:
        print(describe(v, apply))
    else:
        code = remove(project, v)
    refused = [] if (v.removed or (v.removable and not apply)) else [describe(v, apply)]
    # the branch goes only after its worktree is gone, on the same merged test
    todo = ([wt["branch"]] if wt["branch"] else []) + [b for b in branches if b != wt["branch"]]
    if apply and v.removed:
        _, out, _ = git(project.main, "worktree", "list", "--porcelain")
        current = parse_worktrees(out)
        for b in todo:
            ok, msg = delete_branch(project, b, current)
            print(("" if ok else "kept: ") + msg)
            if not ok:
                refused.append(msg)
                code = max(code, 1)
    elif apply:
        for b in todo:
            print(f"kept: branch {b}: its worktree was not removed")
    else:
        for b in todo:
            if b == wt["branch"]:
                print(f"would delete branch {b} after its worktree" if v.removable
                      else f"kept: branch {b}")
                continue
            ok, msg = check_branch(project, b, wt["branch"])
            print(msg)
            if not ok:
                refused.append(msg)
    print_refused(refused)
    return code


def check_branch(project, branch, own):
    """Dry-run view of an extra branch."""
    tip = project.oid("refs/heads/" + branch)
    if tip is None:
        return False, f"kept: branch {branch} not found"
    if any(w["branch"] == branch and w["branch"] != own for w in project.worktrees):
        return False, f"kept: branch {branch} is checked out in a worktree"
    state, detail = project.merge_state(tip, branch)
    if state in (MERGED, EMPTY):
        return True, f"would delete branch {branch} ({state}, {detail})"
    return False, f"kept: branch {branch}: {state}: {detail}"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="closeout.py", description="Close out a builder's worktree.")
    ap.add_argument("main_checkout")
    ap.add_argument("builder", nargs="?")
    ap.add_argument("--branch", action="append", default=[],
                    help="another local branch of this builder, deleted on the same test")
    ap.add_argument("--apply", action="store_true", help="act; without it, a dry run")
    ap.add_argument("--list", action="store_true", help="list every worktree; changes nothing")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:  # argparse has printed the usage
        return e.code if isinstance(e.code, int) else 2

    _, version, _ = git(None, "--version")
    mode = "list" if args.list else ("apply" if args.apply else "dry run")
    print(f"closeout: {version.strip() or 'git version unknown'}; {mode}")

    if args.list and (args.builder or args.apply or args.branch):
        print("closeout refused: --list takes no builder name, --branch or --apply")
        return 2
    if not args.list:
        if not args.builder or not NAME.match(args.builder):
            print("closeout refused: a builder name is lower-case letters, digits and hyphens")
            return 2
        bad = [b for b in args.branch if not b or b.startswith("-") or ".." in b]
        if bad:
            print(f"closeout refused: not a branch name: {bad[0]}")
            return 2
    try:
        project = Project(args.main_checkout)
    except Refusal as e:
        print(f"closeout refused: {e}")
        return 2
    if args.list:
        return list_mode(project)
    return builder_mode(project, args.builder, args.branch, args.apply)


if __name__ == "__main__":
    sys.exit(main())
