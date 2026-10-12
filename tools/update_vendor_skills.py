"""Check vendored skills against upstream and (optionally) pull updates.

Successor to tools/update-vendor-skills.ipynb (retired). Single source of
truth is vendor-skills.json at the repo root — nothing here hardcodes
skill metadata. Report-only by design: drift and available updates are
surfaced, never auto-resolved.

Modes:
  python tools/update_vendor_skills.py                 # full check report
  python tools/update_vendor_skills.py --no-drift      # skip local-drift scan
  python tools/update_vendor_skills.py --apply NAME    # re-vendor one skill
                                                       # from latest upstream
                                                       # and re-pin the manifest
  python tools/update_vendor_skills.py --bless NAME    # recompute local_sha
                                                       # for NAME's
                                                       # known_local_edits

Known-intentional drift (three-state ontology, grilled 2026-07-12):
faithful vendor / vendored-with-known-edits / fork. A skills[] entry may
carry known_local_edits: [{file, reason, local_sha}] — deliberate local
deviations that must survive updates. Drift then reports in two buckets:
"known" (compact, quiet — file matches its blessed local_sha) and "NEW"
(loud — unannotated drift, or an annotated file whose content moved past
its blessing). An annotation whose file is NOT drifted is flagged stale.
After every --apply + manual reapply of known edits, run --bless.

The check covers, per vendor-skills.json section:
  skills[]                — pinned vs latest upstream commit on source_path,
                            plus local-drift: local files hash-compared
                            against the pinned upstream tree (catches silent
                            forks like the 2026-07 grill-with-docs incident).
  forks[]                 — whether the pristine vendor-cache mirror has
                            advanced past forked_at_commit (hand-merge due).
  plugin_manifests_only[] — pinned vs latest commit on each manifest file.

Drift detection costs one git-trees API call per unique (repo, commit)
pair — local files are compared by locally computed git blob SHAs (with a
CRLF-normalized second try, since Windows checkouts may re-line-end text
files), so no file downloads happen during a check.

GitHub rate limits: unauthenticated = 60/hr. Set GITHUB_TOKEN, or have
`gh` authenticated (its token is picked up automatically), for 5,000/hr.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GITHUB_API = "https://api.github.com"


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "vendor-skills.json").exists():
            return candidate
    raise FileNotFoundError("vendor-skills.json not found above this script")


REPO_ROOT = find_repo_root()
MANIFEST_PATH = REPO_ROOT / "vendor-skills.json"


def github_token() -> str | None:
    if tok := os.environ.get("GITHUB_TOKEN"):
        return tok
    try:
        out = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.TimeoutExpired):
        return None


TOKEN = github_token()


def api(path: str, params: dict | None = None):
    url = f"{GITHUB_API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "vendor-skill-updater",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def latest_commit(repo: str, path: str, branch: str) -> dict:
    data = api(f"/repos/{repo}/commits", {"path": path, "sha": branch, "per_page": 1})
    if not data:
        return {"sha": None, "date": None}
    return {"sha": data[0]["sha"], "date": data[0]["commit"]["committer"]["date"]}


# ---------------------------------------------------------------- drift ----

_tree_cache: dict[tuple[str, str], dict[str, str]] = {}


def upstream_tree(repo: str, commit: str) -> dict[str, str]:
    """Map of path -> blob sha for a repo@commit (one API call, cached)."""
    key = (repo, commit)
    if key not in _tree_cache:
        data = api(f"/repos/{repo}/git/trees/{commit}", {"recursive": "1"})
        if data.get("truncated"):
            print(f"  note: tree listing truncated for {repo}@{commit[:7]}", file=sys.stderr)
        _tree_cache[key] = {
            item["path"]: item["sha"] for item in data["tree"] if item["type"] == "blob"
        }
    return _tree_cache[key]


def blob_sha(content: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(content) + content).hexdigest()


def local_blob_sha(local_file: Path) -> str:
    """Blob sha of a local file, CRLF-normalized for text so blessed hashes
    survive checkout line-ending rewrites across machines."""
    raw = local_file.read_bytes()
    if b"\0" not in raw:
        raw = raw.replace(b"\r\n", b"\n")
    return blob_sha(raw)


def local_matches(local_file: Path, upstream_sha: str) -> bool:
    raw = local_file.read_bytes()
    if blob_sha(raw) == upstream_sha:
        return True
    if b"\0" not in raw:  # text: retry with Windows checkout line endings undone
        return blob_sha(raw.replace(b"\r\n", b"\n")) == upstream_sha
    return False


def drift_report(entry: dict) -> tuple[list[str], list[str], list[str]]:
    """Compare the local copy against the pinned upstream tree.

    Returns (new, known, stale):
      new   — loud, actionable drift lines (unannotated, or annotated but
              the file's content moved past its blessed local_sha)
      known — quiet one-liners for annotated drift at its blessed content
      stale — annotations whose file is not drifted at all
    """
    local_root = REPO_ROOT / entry["local_path"]
    if not local_root.exists():
        return (["local path missing"], [], [])
    annotations = {a["file"]: a for a in entry.get("known_local_edits", [])}
    prefix = entry["source_path"].rstrip("/") + "/"
    upstream = {
        p[len(prefix):]: sha
        for p, sha in upstream_tree(entry["repo"], entry["pinned_commit"]).items()
        if p.startswith(prefix)
    }
    local = {
        p.relative_to(local_root).as_posix(): p
        for p in local_root.rglob("*")
        if p.is_file()
    }
    drifted: list[tuple[str, str]] = []  # (kind, rel)
    for rel, sha in upstream.items():
        if rel not in local:
            drifted.append(("missing locally", rel))
        elif not local_matches(local[rel], sha):
            drifted.append(("modified", rel))
    drifted.extend(("local-only", rel) for rel in sorted(set(local) - set(upstream)))

    new, known = [], []
    for kind, rel in drifted:
        note = annotations.get(rel)
        if note is None:
            new.append(f"{kind}: {rel}")
        elif kind == "missing locally":
            new.append(f"{kind}: {rel} (annotated as a known edit but the file is gone)")
        elif local_blob_sha(local[rel]) == note.get("local_sha"):
            known.append(f"{rel} — {note['reason']}")
        else:
            new.append(f"{kind}: {rel} (annotated, but content changed since "
                       "its --bless — re-review, then re-bless if intended)")
    stale = [
        f"{rel} — annotated but not drifted (upstream caught up or the edit "
        "was reverted; remove the annotation)"
        for rel in annotations
        if rel not in {r for _, r in drifted}
    ]
    return (new, known, stale)


# ---------------------------------------------------------------- check ----

def check(with_drift: bool = True) -> None:
    manifest = load_manifest()
    print(f"{'skill':42} {'pinned':8} {'latest':8} status")
    print("-" * 78)
    outdated, new_drift, known_drift, stale_notes = [], [], [], []
    for s in manifest["skills"]:
        try:
            latest = latest_commit(s["repo"], s["source_path"], s["branch"])
            if latest["sha"] is None:
                status = "path not found upstream"
            elif latest["sha"] == s["pinned_commit"]:
                status = "up to date"
            else:
                status = f"UPDATE available ({latest['date'][:10]})"
                outdated.append(s)
        except urllib.error.HTTPError as e:
            latest = {"sha": None}
            status = f"error: HTTP {e.code}"
        if with_drift:
            new, known, stale = drift_report(s)
            if new:
                status += f"  NEW DRIFT ({len(new)} file(s))"
                new_drift.append((s["name"], new))
            if known:
                status += f"  [{len(known)} known edit(s)]"
                known_drift.append((s["name"], known))
            if stale:
                stale_notes.append((s["name"], stale))
        print(f"{s['name']:42} {s['pinned_commit'][:7]:8} "
              f"{(latest['sha'] or '')[:7]:8} {status}")

    print("\n== plugin manifests (manifest-only bundles) ==")
    for p in manifest.get("plugin_manifests_only", []):
        latest = latest_commit(p["repo"], p["source_path"], p["branch"])
        state = ("up to date" if latest["sha"] == p["pinned_commit"]
                 else f"UPDATE available ({(latest['date'] or '')[:10]})")
        print(f"{p['name']:42} {p['pinned_commit'][:7]:8} "
              f"{(latest['sha'] or '')[:7]:8} {state}")

    print("\n== forks ==")
    mirrors = {s["name"]: s for s in manifest["skills"]}
    for f in manifest.get("forks", []):
        mirror = mirrors[f["forked_from"]]
        if mirror["pinned_commit"] == f["forked_at_commit"]:
            print(f"{f['name']:42} in sync with mirror "
                  f"({f['forked_at_commit'][:7]})")
        else:
            print(f"{f['name']:42} HAND-MERGE due: mirror "
                  f"{mirror['local_path']} advanced "
                  f"{f['forked_at_commit'][:7]} -> {mirror['pinned_commit'][:7]}; "
                  f"diff it against {f['local_path']}, port what applies, then "
                  f"update forked_at_commit.")

    if outdated:
        print("\nCompare links for available updates:")
        for s in outdated:
            latest = latest_commit(s["repo"], s["source_path"], s["branch"])
            print(f"  {s['name']}: https://github.com/{s['repo']}/compare/"
                  f"{s['pinned_commit'][:7]}...{latest['sha'][:7]}")
    if new_drift:
        print("\nNEW drift (local copy vs pinned upstream — decide revert, "
              "annotate in known_local_edits + --bless, or promote to "
              "forks[], see ADR-0001):")
        for name, problems in new_drift:
            print(f"  {name}:")
            for p in problems:
                print(f"    - {p}")
    if known_drift:
        print("\nKnown edits (annotated + blessed — informational):")
        for name, notes in known_drift:
            for n in notes:
                print(f"  {name}: {n}")
    if stale_notes:
        print("\nSTALE annotations (clean these up):")
        for name, notes in stale_notes:
            for n in notes:
                print(f"  {name}: {n}")


# ---------------------------------------------------------------- apply ----

def download_tree(repo: str, path: str, ref: str, dest: Path) -> int:
    items = api(f"/repos/{repo}/contents/{path}", {"ref": ref})
    if isinstance(items, dict):
        items = [items]
    count = 0
    for item in items:
        if item["type"] == "dir":
            count += download_tree(repo, item["path"], ref, dest / item["name"])
        elif item["type"] == "file":
            dest.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(
                item["download_url"], headers={"User-Agent": "vendor-skill-updater"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                (dest / item["name"]).write_bytes(resp.read())
            count += 1
    return count


def apply_update(name: str) -> None:
    manifest = load_manifest()
    entry = next((s for s in manifest["skills"] if s["name"] == name), None)
    if entry is None:
        sys.exit(f"{name!r} is not in vendor-skills.json skills[]")
    if any(f["name"] == name for f in manifest.get("forks", [])):
        sys.exit(f"{name!r} is a fork — update its vendor-cache mirror instead, "
                 "then hand-merge (see forks[] _comment).")

    new, known, _ = drift_report(entry)
    if new:
        print(f"WARNING: {name} has NEW (unannotated) drift — applying will "
              "overwrite these local changes:")
        for p in new:
            print(f"  - {p}")
    if known:
        print(f"NOTE: applying will overwrite {len(known)} known edit(s) "
              "that must be reapplied afterwards:")
        for n in known:
            print(f"  - {n}")

    latest = latest_commit(entry["repo"], entry["source_path"], entry["branch"])
    if latest["sha"] is None:
        sys.exit(f"source path not found upstream for {name}")
    if latest["sha"] == entry["pinned_commit"] and not (new or known):
        print(f"{name} already at latest ({latest['sha'][:7]}); nothing to do.")
        return

    local = REPO_ROOT / entry["local_path"]
    print(f"{name}: {entry['pinned_commit'][:7]} -> {latest['sha'][:7]} "
          f"({latest['date']})")
    # Stage in the system temp dir, NOT next to the skill: skills/ sits in
    # a OneDrive sync root where Python's os.rmdir is persistently denied
    # (WinError 5), so a repo-local staging dir can never be cleaned up.
    staging = Path(tempfile.mkdtemp(prefix=f"vendor-{name}-"))
    n = download_tree(entry["repo"], entry["source_path"], latest["sha"], staging)
    # Sync at FILE level — never delete or rename directories. On this
    # machine the skill folders are junction targets inside a OneDrive
    # sync root: renaming the folder would break ~/.claude/skills/
    # junctions, and Python's os.rmdir is persistently denied (WinError 5)
    # on OneDrive directories even after retries. Files unlink fine; empty
    # leftover directories are pruned best-effort and harmless if they
    # survive.
    def unlink_retry(p: Path, attempts: int = 5) -> None:
        for i in range(attempts):
            try:
                p.unlink()
                return
            except PermissionError:
                if i == attempts - 1:
                    raise
                time.sleep(0.5 * (i + 1))

    local.mkdir(exist_ok=True)
    upstream_files = {p.relative_to(staging) for p in staging.rglob("*") if p.is_file()}
    for rel in upstream_files:
        dest = local / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            unlink_retry(dest)
        shutil.move(str(staging / rel), dest)
    for p in list(local.rglob("*")):
        if p.is_file() and p.relative_to(local) not in upstream_files:
            unlink_retry(p)
    for d in sorted((p for p in local.rglob("*") if p.is_dir()), reverse=True):
        try:
            d.rmdir()  # only succeeds when empty; leftovers are harmless
        except OSError:
            pass
    try:
        shutil.rmtree(staging)
    except OSError:
        print(f"  note: could not remove staging dir {staging} — delete it manually.")
    entry["pinned_commit"] = latest["sha"]
    entry["pinned_ref"] = latest["sha"][:7]
    save_manifest(manifest)
    print(f"wrote {n} file(s), re-pinned manifest to {latest['sha'][:7]}. "
          "Review `git diff` before committing.")
    if known:
        print("\nReapply ritual for the known edits listed above:")
        print(f"  1. git diff HEAD -- {entry['local_path']}   "
              "(your edits are the removed lines)")
        print("  2. Reapply each edit — run the `vendor-sync-reapply` agent "
              "(it does steps 2-3 and reports any edit it could not "
              "reapply cleanly).")
        print(f"  3. python tools/update_vendor_skills.py --bless {name}")
        print("  4. If the diff touches `disable-model-invocation` or adds a "
              "skill, run the `skill-safety-auditor` agent before committing.")
        print("  5. Review the full diff, then commit.")


def bless(name: str) -> None:
    manifest = load_manifest()
    entry = next((s for s in manifest["skills"] if s["name"] == name), None)
    if entry is None:
        sys.exit(f"{name!r} is not in vendor-skills.json skills[]")
    edits = entry.get("known_local_edits", [])
    if not edits:
        sys.exit(f"{name!r} has no known_local_edits to bless — add "
                 "{{file, reason}} entries first.")
    for note in edits:
        f = REPO_ROOT / entry["local_path"] / note["file"]
        if not f.is_file():
            sys.exit(f"annotated file missing: {f}")
        note["local_sha"] = local_blob_sha(f)
        print(f"blessed {note['file']} -> {note['local_sha'][:12]}")
    save_manifest(manifest)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", metavar="NAME", help="re-vendor one skill from latest upstream")
    ap.add_argument("--bless", metavar="NAME", help="recompute local_sha for NAME's known_local_edits")
    ap.add_argument("--no-drift", action="store_true", help="skip the local-drift scan")
    args = ap.parse_args()
    if args.bless:
        bless(args.bless)
        return
    print("authenticated (5,000/hr)" if TOKEN else "unauthenticated (60/hr) — "
          "set GITHUB_TOKEN or `gh auth login`", file=sys.stderr)
    if args.apply:
        apply_update(args.apply)
    else:
        check(with_drift=not args.no_drift)


if __name__ == "__main__":
    main()
