import copy
import importlib.util
import json
import sys
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "update_vendor_skills", ROOT / "tools" / "update_vendor_skills.py"
)
tus = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tus)

OLD = "a" * 40
NEW = "b" * 40
SKILL_PATH = "skills/s"
BUNDLE_PATH = "plugins/m/plugin.json"


def not_found(url):
    return urllib.error.HTTPError(url, 404, "Not Found", {}, None)


class FakeGitHub:
    def __init__(self):
        self.latest = {}
        self.contents = {}
        self.blobs = {}
        self.trees = {}
        self.calls = []

    def api(self, path, params=None):
        self.calls.append((path, params))
        if path.endswith("/commits"):
            sha = self.latest.get(params["path"])
            if sha is None:
                return []
            return [{"sha": sha, "commit": {"committer": {"date": "2026-11-01T00:00:00Z"}}}]
        if "/contents/" in path:
            key = path.split("/contents/", 1)[1]
            if key not in self.contents:
                raise not_found(path)
            return self.contents[key]
        if "/git/trees/" in path:
            return {"tree": self.trees[path.rsplit("/", 1)[1]], "truncated": False}
        raise AssertionError(f"unmocked GitHub call: {path}")

    def fetch_bytes(self, url):
        return self.blobs[url]


def file_item(path, blob_key):
    return {
        "type": "file",
        "name": path.rsplit("/", 1)[1],
        "path": path,
        "download_url": blob_key,
    }


@pytest.fixture
def world(tmp_path, monkeypatch):
    manifest = {
        "skills": [
            {
                "name": "s",
                "repo": "o/r",
                "branch": "main",
                "pinned_ref": OLD[:7],
                "pinned_commit": OLD,
                "source_path": SKILL_PATH,
                "local_path": "skills/s",
            }
        ],
        "plugin_manifests_only": [
            {
                "name": "m",
                "repo": "o/r",
                "branch": "main",
                "pinned_ref": OLD[:7],
                "pinned_commit": OLD,
                "source_path": BUNDLE_PATH,
                "local_path": "plugins/m.plugin.json",
            }
        ],
    }
    manifest_path = tmp_path / "vendor-skills.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (tmp_path / "skills" / "s").mkdir(parents=True)
    (tmp_path / "skills" / "s" / "SKILL.md").write_bytes(b"old")
    (tmp_path / "plugins").mkdir()
    (tmp_path / "plugins" / "m.plugin.json").write_bytes(b"old-bundle")

    gh = FakeGitHub()
    monkeypatch.setattr(tus, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(tus, "MANIFEST_PATH", manifest_path)
    monkeypatch.setattr(tus, "api", gh.api)
    monkeypatch.setattr(tus, "fetch_bytes", gh.fetch_bytes)
    monkeypatch.setattr(tus, "_tree_cache", {})
    gh.root = tmp_path
    gh.manifest_path = manifest_path
    gh.manifest = manifest
    return gh


def removed_upstream(gh):
    gh.latest[SKILL_PATH] = NEW
    gh.latest[BUNDLE_PATH] = NEW


@pytest.mark.parametrize(
    "name, path",
    [("s", SKILL_PATH), ("m", BUNDLE_PATH)],
)
def test_apply_reports_removed_upstream_and_changes_nothing(world, name, path):
    removed_upstream(world)
    before = world.manifest_path.read_bytes()
    with pytest.raises(SystemExit) as exc:
        tus.apply_update(name)
    assert exc.value.code == f"REMOVED upstream: {path}"
    assert world.manifest_path.read_bytes() == before
    assert (world.root / "skills" / "s" / "SKILL.md").read_bytes() == b"old"
    assert (world.root / "plugins" / "m.plugin.json").read_bytes() == b"old-bundle"


def test_apply_path_never_on_upstream_is_also_removed(world):
    with pytest.raises(SystemExit) as exc:
        tus.apply_update("s")
    assert exc.value.code == f"REMOVED upstream: {SKILL_PATH}"


def test_apply_removed_exits_nonzero_through_main(world, monkeypatch):
    removed_upstream(world)
    monkeypatch.setattr(sys, "argv", ["update_vendor_skills.py", "--apply", "m"])
    with pytest.raises(SystemExit) as exc:
        tus.main()
    assert exc.value.code not in (0, None)


def test_apply_backstop_when_download_hits_404(world, monkeypatch):
    world.latest[SKILL_PATH] = NEW
    world.contents[SKILL_PATH] = [file_item("skills/s/SKILL.md", "u:skill")]
    world.trees[OLD] = [
        {"path": "skills/s/SKILL.md", "type": "blob", "sha": tus.blob_sha(b"old")}
    ]

    def gone(*args, **kwargs):
        raise not_found("contents")

    monkeypatch.setattr(tus, "download_tree", gone)
    with pytest.raises(SystemExit) as exc:
        tus.apply_update("s")
    assert exc.value.code == f"REMOVED upstream: {SKILL_PATH}"
    assert (world.root / "skills" / "s" / "SKILL.md").read_bytes() == b"old"


def test_check_reports_removed_instead_of_update(world, capsys):
    removed_upstream(world)
    tus.check(with_drift=False)
    out = capsys.readouterr().out
    assert f"REMOVED upstream: {SKILL_PATH}" in out
    assert f"REMOVED upstream: {BUNDLE_PATH}" in out
    assert "UPDATE available" not in out
    assert "Compare links" not in out


def test_check_still_reports_a_real_update(world, capsys):
    world.latest[SKILL_PATH] = NEW
    world.contents[SKILL_PATH] = [file_item("skills/s/SKILL.md", "u:skill")]
    world.latest[BUNDLE_PATH] = OLD
    tus.check(with_drift=False)
    out = capsys.readouterr().out
    assert "UPDATE available" in out
    assert "REMOVED" not in out


def test_apply_manifest_entry_downloads_file_and_moves_pin(world):
    world.latest[BUNDLE_PATH] = NEW
    world.contents[BUNDLE_PATH] = file_item(BUNDLE_PATH, "u:bundle")
    world.blobs["u:bundle"] = b"new-bundle"
    skills_before = copy.deepcopy(world.manifest["skills"])

    tus.apply_update("m")

    assert (world.root / "plugins" / "m.plugin.json").read_bytes() == b"new-bundle"
    saved = json.loads(world.manifest_path.read_text(encoding="utf-8"))
    entry = saved["plugin_manifests_only"][0]
    assert entry["pinned_commit"] == NEW
    assert entry["pinned_ref"] == NEW[:7]
    assert entry["source_path"] == BUNDLE_PATH
    assert entry["local_path"] == "plugins/m.plugin.json"
    assert saved["skills"] == skills_before
    assert (world.root / "skills" / "s" / "SKILL.md").read_bytes() == b"old"


def test_apply_manifest_entry_already_at_pin_writes_nothing(world, capsys):
    world.latest[BUNDLE_PATH] = OLD
    before = world.manifest_path.read_bytes()

    tus.apply_update("m")

    assert "nothing to do" in capsys.readouterr().out
    assert world.manifest_path.read_bytes() == before
    assert (world.root / "plugins" / "m.plugin.json").read_bytes() == b"old-bundle"


def test_apply_unknown_name_names_both_sections(world):
    with pytest.raises(SystemExit) as exc:
        tus.apply_update("nope")
    assert "plugin_manifests_only" in exc.value.code


def test_apply_skill_still_re_vendors_and_re_pins(world):
    world.latest[SKILL_PATH] = NEW
    world.contents[SKILL_PATH] = [file_item("skills/s/SKILL.md", "u:skill")]
    world.blobs["u:skill"] = b"new"
    world.trees[OLD] = [
        {"path": "skills/s/SKILL.md", "type": "blob", "sha": tus.blob_sha(b"old")}
    ]

    tus.apply_update("s")

    assert (world.root / "skills" / "s" / "SKILL.md").read_bytes() == b"new"
    saved = json.loads(world.manifest_path.read_text(encoding="utf-8"))
    assert saved["skills"][0]["pinned_commit"] == NEW
    assert saved["plugin_manifests_only"][0]["pinned_commit"] == OLD
