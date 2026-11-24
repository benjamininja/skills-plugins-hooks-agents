"""tools/drift_check.py: each pair `same` and `differs`, the three limits of the
planner's ruling on #219 (output safe to post, reads only, an absent side is
`unreadable` and the other pairs still run), and the exit codes.

No network and no real file: origin is a local bare repository, home is a
temporary folder.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "drift_check.py"
_spec = importlib.util.spec_from_file_location("drift_check", SCRIPT)
dc = importlib.util.module_from_spec(_spec)
sys.modules["drift_check"] = dc
_spec.loader.exec_module(dc)

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.com",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.com",
}


def git(cwd, *args):
    done = subprocess.run(
        ["git", "-c", "core.autocrlf=false", "-c", "protocol.file.allow=always", *args],
        cwd=cwd, env=GIT_ENV, capture_output=True, text=True, check=True,
    )
    return done.stdout.strip()


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, data):
    write(path, json.dumps(data, indent=2) + "\n")


def commit_all(repo, message="c"):
    git(repo, "add", "-A")
    git(repo, "commit", "-m", message)


def make_link(link: Path, target: Path) -> bool:
    link.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.symlink(target, link, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        pass
    if sys.platform == "win32":
        done = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
        return done.returncode == 0
    return False


BUILDERS = {
    "//": "a note",
    "permissions": {"allow": ["Read", "Edit"], "deny": ["PowerShell", "Bash(gh pr merge*)", "Bash(gh api*)"]},
}
MANAGERS = {"permissions": {"allow": ["Read"], "deny": ["Bash(gh secret *)"]}}
DISPATCH = {"//": "n", "agent": "stage-builder", "buildersSettings": ".claude/builders.settings.json",
            "setup": [], "tiers": {}}
PROJECTS_TEMPLATE = {"//": "n", "projects": ["C:/path/to/the/main/checkout"]}
ROLE = (
    "---\nname: stage-builder\ntools: Read, Edit, Bash\nmodel: sonnet\n---\n"
    "# Role\n\n## How you work\n\ntext\n\n```\n# not a heading\n```\n\n## Hard lines\n"
)
PLUGIN = {"name": "owner-queue", "version": "1.0.0"}
PD = "plugins/disp/templates"


class World:
    pass


@pytest.fixture
def world(tmp_path):
    w = World()
    w.tmp = tmp_path
    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "--bare", "-b", "main", str(origin))
    seed = tmp_path / "seed"
    seed.mkdir()
    git(seed, "init", "-b", "main")
    write(seed / "tools" / "keep.txt", "x\n")
    write_json(seed / PD / "builders.settings.example.json", BUILDERS)
    write_json(seed / PD / "managers.settings.example.json", MANAGERS)
    write_json(seed / PD / "research.settings.example.json", MANAGERS)
    write_json(seed / PD / "builder-profiles.example.json", {"profiles": {}})
    write_json(seed / PD / "dispatch.json", DISPATCH)
    write_json(seed / PD / "dispatch-projects.json", PROJECTS_TEMPLATE)
    write(seed / PD / "agents" / "stage-builder.md", ROLE)
    write_json(seed / "plugins" / "owner-queue" / ".claude-plugin" / "plugin.json", PLUGIN)
    write(seed / "hooks" / "git-guardrails" / "hook.txt", "h\n")
    commit_all(seed)
    git(seed, "remote", "add", "origin", str(origin))
    git(seed, "push", "origin", "main")
    w.tools = tmp_path / "tools-main"
    w.live = tmp_path / "live-clone"
    git(tmp_path, "clone", str(origin), str(w.tools))
    git(tmp_path, "clone", str(origin), str(w.live))
    w.origin, w.seed = origin, seed

    w.proj = tmp_path / "proj-one"
    w.proj.mkdir()
    git(w.proj, "init", "-b", "main")
    write_json(w.proj / ".claude" / "dispatch.json", DISPATCH)
    write_json(w.proj / ".claude" / "builders.settings.json",
               {"permissions": {"allow": ["Read", "Edit", "Bash(pytest*)"], "deny": BUILDERS["permissions"]["deny"]}})
    write(w.proj / ".claude" / "agents" / "stage-builder.md", ROLE)
    commit_all(w.proj)

    w.home = tmp_path / "home"
    w.cfg = w.home / ".claude"
    write_json(w.cfg / "dispatch-projects.json", {"projects": [str(w.proj)]})
    write_json(w.cfg / "settings.json",
               {"env": {"CLAUDE_CODE_PLUGIN_DIRS": str(w.live / "plugins" / "owner-queue")},
                "permissions": {"allow": ["Read"], "deny": ["secret-rule-text"]}})
    write_json(w.cfg / "builders.settings.json", BUILDERS)
    write_json(w.cfg / "managers.settings.json", MANAGERS)
    (w.cfg / "skills").mkdir()
    git(w.cfg, "init", "-b", "main")
    git(w.cfg, "add", "settings.json", "builders.settings.json", "managers.settings.json", "dispatch-projects.json")
    git(w.cfg, "commit", "-m", "c")
    w.linked = make_link(w.cfg / "hooks" / "git-guardrails", w.tools / "hooks" / "git-guardrails")
    return w


def results(w, remote=False):
    _, res = dc.run(w.home, w.tools / "tools", remote)
    return res


def by(res, pair):
    return [r for r in res if r.pair == pair]


def one(res, pair):
    got = by(res, pair)
    assert len(got) == 1, [r.line() for r in got]
    return got[0]


def advance_origin(w, name="more.txt"):
    write(w.seed / name, "m\n")
    commit_all(w.seed)
    git(w.seed, "push", "origin", "main")


# ---------------------------------------------------------------- baseline


def test_baseline_is_all_same(world):
    res = results(world)
    bad = [r.line() for r in res if r.status not in (dc.SAME, dc.SKIPPED)]
    assert bad == []
    assert dc.exit_code(res) == 0
    skipped = {r.label for r in res if r.status == dc.SKIPPED}
    assert "research.settings.example.json" in skipped


def test_every_pair_prints_a_line(world):
    pairs = {r.pair for r in results(world)}
    assert pairs == {f"P{n}" for n in range(1, 12)}


# ---------------------------------------------------------------- P1 to P4


def test_p1_behind_origin_counts_commits(world):
    advance_origin(world)
    git(world.tools, "fetch", "origin")
    r = one(results(world), "P1")
    assert (r.status, r.count, r.unit) == (dc.DIFFERS, 1, "commits+files")


def test_p1_modified_tracked_file_counts(world):
    write(world.tools / "tools" / "keep.txt", "changed\n")
    r = one(results(world), "P1")
    assert (r.status, r.count) == (dc.DIFFERS, 1)


def test_p2_live_clone_behind_origin(world):
    advance_origin(world)
    git(world.live, "fetch", "origin")
    res = results(world)
    assert (one(res, "P2").status, one(res, "P2").count) == (dc.DIFFERS, 1)
    assert one(res, "P1").status == dc.SAME


def test_p3_heads_apart(world):
    advance_origin(world)
    git(world.tools, "pull", "--ff-only")
    r = one(results(world), "P3")
    assert (r.status, r.count, r.unit) == (dc.DIFFERS, 1, "commits")


def test_p4_missing_plugin_folder(world):
    import shutil
    shutil.rmtree(world.live / "plugins" / "owner-queue")
    r = one(results(world), "P4")
    assert (r.status, r.count, r.reason) == (dc.DIFFERS, 1, "missing")


def test_p4_modified_file_in_plugin_folder(world):
    write(world.live / "plugins" / "owner-queue" / ".claude-plugin" / "plugin.json", "{}\n")
    r = one(results(world), "P4")
    assert (r.status, r.count, r.unit) == (dc.DIFFERS, 1, "files")


def test_p4_entry_outside_live_clone(world):
    elsewhere = world.tmp / "elsewhere"
    elsewhere.mkdir()
    write_json(world.cfg / "settings.json", {"env": {"CLAUDE_CODE_PLUGIN_DIRS": str(elsewhere)}})
    res = results(world)
    assert one(res, "P4").status == dc.DIFFERS
    assert one(res, "P2").status == dc.UNREADABLE


# ---------------------------------------------------------------- P5


def test_p5_running_version_differs_from_source(world):
    write_json(world.live / "plugins" / "owner-queue" / ".claude-plugin" / "plugin.json",
               {"name": "owner-queue", "version": "0.7.2"})
    r = one(results(world), "P5")
    assert (r.status, r.count, r.unit) == (dc.DIFFERS, 1, "copies")


def test_p5_hand_copy_elsewhere_counts(world):
    write_json(world.cfg / "mods" / "owner-queue" / ".claude-plugin" / "plugin.json",
               {"name": "owner-queue", "version": "0.7.2"})
    r = one(results(world), "P5")
    assert (r.status, r.count) == (dc.DIFFERS, 1)


def test_p5_other_plugin_copy_is_ignored(world):
    write_json(world.cfg / "mods" / "x" / ".claude-plugin" / "plugin.json", {"name": "other", "version": "9"})
    assert one(results(world), "P5").status == dc.SAME


# ---------------------------------------------------------------- P6, P7


def test_p6_template_lags_real_file(world):
    real = json.loads(json.dumps(BUILDERS))
    real["permissions"]["deny"].append("a-new-rule")
    real["extraKey"] = 1
    write_json(world.cfg / "builders.settings.json", real)
    rows = [r for r in by(results(world), "P6") if r.label.startswith("builders.settings.example.json [user]")]
    assert len(rows) == 1
    # the extra key, its value, and the extra deny entry
    assert (rows[0].status, rows[0].count, rows[0].unit) == (dc.DIFFERS, 3, "entries")


def test_p6_extra_allow_in_real_file_is_not_drift(world):
    real = json.loads(json.dumps(BUILDERS))
    real["permissions"]["allow"].append("Bash(own*)")
    write_json(world.cfg / "builders.settings.json", real)
    rows = [r for r in by(results(world), "P6") if r.label.startswith("builders.settings.example.json [user]")]
    assert rows[0].status == dc.SAME


def test_p6_template_allow_missing_from_real_counts(world):
    real = json.loads(json.dumps(BUILDERS))
    real["permissions"]["allow"].remove("Edit")
    write_json(world.cfg / "builders.settings.json", real)
    rows = [r for r in by(results(world), "P6") if r.label.startswith("builders.settings.example.json [user]")]
    assert (rows[0].status, rows[0].count) == (dc.DIFFERS, 1)


def test_p6_machine_path_values_are_not_compared(world):
    tpl = json.loads(json.dumps(DISPATCH))
    assert dc.canon("C:/one/path") == dc.canon("D:\\other\\path") == "<path>"
    assert dc.settings_difference({"a": "C:/x"}, {"a": "/home/y"}, "settings") == 0
    assert tpl


def test_p6_dispatch_compares_key_names_only(world):
    write_json(world.proj / ".claude" / "dispatch.json", {**DISPATCH, "agent": "other-value", "newKey": 1})
    rows = [r for r in by(results(world), "P6") if r.label.startswith("dispatch.json [proj-one]")]
    assert (rows[0].status, rows[0].count) == (dc.DIFFERS, 1)


def test_p6_note_keys_are_ignored(world):
    write_json(world.cfg / "managers.settings.json", {**MANAGERS, "//note": "anything"})
    rows = [r for r in by(results(world), "P6") if r.label.startswith("managers")]
    assert rows[0].status == dc.SAME


def test_p6_required_template_without_real_file_is_unreadable(world):
    (world.cfg / "managers.settings.json").unlink()
    rows = [r for r in by(results(world), "P6") if r.label.startswith("managers")]
    assert (rows[0].status, rows[0].reason) == (dc.UNREADABLE, "no real file")


def test_p7_missing_deny_entries_counted_never_named(world):
    write_json(world.proj / ".claude" / "builders.settings.json",
               {"permissions": {"allow": ["Read"], "deny": ["PowerShell"]}})
    rows = [r for r in by(results(world), "P7") if "[proj-one]" in r.label]
    assert (rows[0].status, rows[0].count, rows[0].unit) == (dc.DIFFERS, 2, "deny entries")
    text = " ".join(r.line() for r in results(world))
    assert "gh pr merge" not in text and "gh api" not in text


def test_p7_follows_the_dispatch_file_key(world):
    write_json(world.proj / ".claude" / "dispatch.json", {**DISPATCH, "buildersSettings": "elsewhere/b.json"})
    write_json(world.proj / "elsewhere" / "b.json", {"permissions": {"deny": []}})
    rows = [r for r in by(results(world), "P7") if "[proj-one]" in r.label]
    assert (rows[0].status, rows[0].count) == (dc.DIFFERS, 3)


# ---------------------------------------------------------------- P8


def test_p8_hand_edit_not_committed(world):
    write_json(world.proj / ".claude" / "builders.settings.json", {"permissions": {"allow": ["Read"], "deny": []}})
    rows = [r for r in by(results(world), "P8") if r.label.startswith("tracked vs live builders.settings.json [proj-one]")]
    assert rows[0].status == dc.DIFFERS and rows[0].unit == "lines" and rows[0].reason == "uncommitted"
    assert rows[0].count > 0


def test_p8_user_repo_edit_counts(world):
    write(world.cfg / "settings.json", "{}\n")
    rows = [r for r in by(results(world), "P8") if r.label.startswith("tracked vs live settings.json [user]")]
    assert rows[0].status == dc.DIFFERS


def test_p8_line_endings_ignored(world):
    path = world.proj / ".claude" / "dispatch.json"
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    rows = [r for r in by(results(world), "P8") if "dispatch.json [proj-one]" in r.label]
    assert rows[0].status == dc.SAME


# ---------------------------------------------------------------- P9


def test_p9_heading_and_key_differences(world):
    write(world.proj / ".claude" / "agents" / "stage-builder.md",
          ROLE.replace("## Hard lines", "## Other lines").replace("model: sonnet\n", ""))
    rows = [r for r in by(results(world), "P9") if r.label.startswith("stage-builder.md")]
    assert (rows[0].status, rows[0].count, rows[0].unit) == (dc.DIFFERS, 3, "headings and keys")


def test_p9_prose_change_is_not_seen(world):
    write(world.proj / ".claude" / "agents" / "stage-builder.md", ROLE.replace("text", "different words"))
    rows = [r for r in by(results(world), "P9") if r.label.startswith("stage-builder.md")]
    assert rows[0].status == dc.SAME


def test_p9_prefixed_role_name_matches_template(world):
    (world.proj / ".claude" / "agents" / "stage-builder.md").rename(world.proj / ".claude" / "agents" / "dyn-stage-builder.md")
    rows = by(results(world), "P9")
    assert [r.status for r in rows] == [dc.SAME]


def test_p9_help_names_the_gap():
    assert "changed sentence under an unchanged heading" in dc.__doc__


def test_role_structure_ignores_fenced_hash_lines():
    keys, tools, heads = dc.role_structure(ROLE)
    assert keys == {"name", "tools", "model"}
    assert tools == {"Read", "Edit", "Bash"}
    assert heads == {"role", "how you work", "hard lines"}


# ---------------------------------------------------------------- P10, P11


def test_p10_no_link_is_same(world):
    assert [r.status for r in by(results(world), "P10")] == [dc.SAME, dc.SAME]


def test_p10_counts_files_whose_folder_is_a_link_outside(world, tmp_path):
    if not world.linked:
        pytest.skip("cannot make a link here")
    outside = tmp_path / "outside"
    write(outside / "x.txt", "1\n")
    write(outside / "y.txt", "2\n")
    # the configuration repository tracks these two files, then the folder becomes a link
    write(world.cfg / "old" / "x.txt", "1\n")
    write(world.cfg / "old" / "y.txt", "2\n")
    git(world.cfg, "add", "old")
    git(world.cfg, "commit", "-m", "old")
    import shutil
    shutil.rmtree(world.cfg / "old")
    if not make_link(world.cfg / "old", outside):
        pytest.skip("cannot make a link here")
    rows = [r for r in by(results(world), "P10") if "[user]" in r.label]
    assert (rows[0].status, rows[0].count, rows[0].unit) == (dc.DIFFERS, 2, "tracked files")


def test_p11_link_to_folder_without_tracked_files(world):
    if not world.linked:
        pytest.skip("cannot make a link here")
    (world.tools / "hooks" / "continual-learning").mkdir()
    (world.tools / "hooks" / "continual-learning" / "untracked.txt").write_text("u\n")
    if not make_link(world.cfg / "hooks" / "continual-learning", world.tools / "hooks" / "continual-learning"):
        pytest.skip("cannot make a link here")
    r = one(results(world), "P11")
    assert (r.status, r.count, r.unit) == (dc.DIFFERS, 1, "links")


def test_p11_broken_link_counts(world):
    if not world.linked:
        pytest.skip("cannot make a link here")
    gone = world.tmp / "gone"
    gone.mkdir()
    if not make_link(world.cfg / "hooks" / "dead", gone):
        pytest.skip("cannot make a link here")
    gone.rmdir()
    r = one(results(world), "P11")
    assert (r.status, r.count) == (dc.DIFFERS, 1)


def test_p11_good_link_is_same(world):
    if not world.linked:
        pytest.skip("cannot make a link here")
    assert one(results(world), "P11").status == dc.SAME


# ---------------------------------------------------------------- the three limits


def test_limit_1_output_holds_no_path_and_no_rule(world):
    # make several pairs differ so every line type is exercised
    write_json(world.proj / ".claude" / "builders.settings.json", {"permissions": {"allow": [], "deny": []}})
    write(world.cfg / "settings.json", '{"permissions": {"deny": ["secret-rule-text"]}}\n')
    text = "\n".join(r.line() for r in results(world))
    assert str(world.tmp) not in text and str(world.home) not in text
    assert "secret-rule-text" not in text
    assert not re.search(r"[A-Za-z]:[\\/]", text)
    assert "PowerShell" not in text and "gh pr merge" not in text


def test_limit_1_script_run_against_a_fake_home_prints_no_path(tmp_path):
    home = tmp_path / "fakehome"
    (home / ".claude").mkdir(parents=True)
    done = subprocess.run([sys.executable, str(SCRIPT), "--home", str(home)],
                          capture_output=True, text=True, cwd=tmp_path)
    assert str(home) not in done.stdout + done.stderr
    assert str(tmp_path) not in done.stdout
    assert done.returncode == 2
    assert done.stdout.startswith("drift_check: origin/main as last fetched:")


def test_limit_2_source_has_no_git_write_subcommand():
    source = SCRIPT.read_text(encoding="utf-8")
    banned = "fetch pull checkout merge reset commit push clean add rm gc switch restore stash update-ref config".split()
    for word in banned:
        assert not re.search(rf"""["']{word}["']""", source), word
    assert dc.GIT_READ_ONLY == {"rev-parse", "rev-list", "show", "ls-tree", "ls-files", "diff", "status", "ls-remote", "log"}


def test_limit_2_git_helper_refuses_a_write_subcommand(world):
    with pytest.raises(dc.GitError):
        dc.git(world.tools, "fetch", "origin")


def test_limit_2_a_run_leaves_every_repository_as_it_was(world):
    before = {p: git(p, "status", "--porcelain=v1") + git(p, "rev-parse", "HEAD") for p in (world.tools, world.live, world.proj)}
    results(world)
    after = {p: git(p, "status", "--porcelain=v1") + git(p, "rev-parse", "HEAD") for p in (world.tools, world.live, world.proj)}
    assert before == after


def test_limit_3_an_empty_home_is_unreadable_and_every_pair_still_runs(tmp_path):
    clone_tools = tmp_path / "t"
    clone_tools.mkdir()
    git(clone_tools, "init", "-b", "main")
    write(clone_tools / "tools" / "k.txt", "x\n")
    commit_all(clone_tools)
    home = tmp_path / "empty-home"
    home.mkdir()
    _, res = dc.run(home, clone_tools / "tools")
    assert {r.pair for r in res} == {f"P{n}" for n in range(1, 12)}
    assert not [r for r in res if r.status == dc.DIFFERS]
    assert dc.exit_code(res) == 2
    assert all(r.reason for r in res if r.status == dc.UNREADABLE)


def test_limit_3_a_pair_that_raises_does_not_stop_the_others(world, monkeypatch):
    def boom(w):
        raise RuntimeError("secret path C:/x")
    monkeypatch.setattr(dc, "PAIRS", [boom, dc.p1])
    _, res = dc.run(world.home, world.tools / "tools")
    assert res[0].status == dc.UNREADABLE and res[0].reason == "RuntimeError"
    assert res[1].pair == "P1"


# ---------------------------------------------------------------- exit codes, --remote


def test_exit_codes():
    same = dc.Result("P1", "x", dc.SAME)
    diff = dc.Result("P2", "x", dc.DIFFERS, 1, "files")
    unread = dc.Result("P3", "x", dc.UNREADABLE, reason="r")
    skip = dc.Result("P4", "x", dc.SKIPPED, reason="r")
    assert dc.exit_code([same, skip]) == 0
    assert dc.exit_code([same, diff, unread]) == 1
    assert dc.exit_code([same, unread]) == 2


def test_remote_flag_adds_p0(world):
    res = results(world, remote=True)
    assert one(res, "P0").status == dc.SAME
    advance_origin(world)
    assert one(results(world, remote=True), "P0").status == dc.DIFFERS


def test_default_run_has_no_p0(world):
    assert by(results(world), "P0") == []


def test_header_reports_the_fetch_age(world):
    age, _ = dc.run(world.home, world.tools / "tools")
    assert age
    assert "/" not in age and "\\" not in age
