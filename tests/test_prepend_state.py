"""prepend_state.py: block goes before the first CURRENT STATE bullet, the rest
is unchanged, and a file without that line fails cleanly."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins" / "session-dispatch-managers-build-review" / "scripts" / "prepend_state.py"
FIXTURE = ROOT / "tests" / "fixtures" / "state_file.md"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True)


def test_inserts_before_first_marker(tmp_path):
    block = tmp_path / "block.md"
    block.write_bytes(b"- **CURRENT STATE, new.** Fresh.\n- Second line.\n")
    out = tmp_path / "out.md"
    r = run(FIXTURE, block, out)
    assert r.returncode == 0, r.stderr
    assert "inserted 2 lines at line 5" in r.stdout
    old = FIXTURE.read_bytes().decode("utf-8").split("\n")
    new = out.read_bytes().decode("utf-8").split("\n")
    assert new[:4] == old[:4]
    assert new[4:6] == ["- **CURRENT STATE, new.** Fresh.", "- Second line."]
    assert new[6:] == old[4:]


def test_in_place(tmp_path):
    state = tmp_path / "state.md"
    state.write_bytes(FIXTURE.read_bytes())
    block = tmp_path / "block.md"
    block.write_text("- **CURRENT STATE, x.**", encoding="utf-8")
    assert run(state, block, state).returncode == 0
    assert state.read_text(encoding="utf-8").splitlines()[4] == "- **CURRENT STATE, x.**"


def test_no_marker_fails_cleanly(tmp_path):
    state = tmp_path / "state.md"
    state.write_text("# Title\n\nNo bullet here.\n", encoding="utf-8")
    block = tmp_path / "block.md"
    block.write_text("x\n", encoding="utf-8")
    out = tmp_path / "out.md"
    r = run(state, block, out)
    assert r.returncode == 1
    assert "no line starting with" in r.stderr
    assert "Traceback" not in r.stderr
    assert not out.exists()


def test_missing_file_fails_cleanly(tmp_path):
    r = run(tmp_path / "nope.md", FIXTURE, tmp_path / "out.md")
    assert r.returncode == 1
    assert "Traceback" not in r.stderr


def test_wrong_arg_count():
    r = run(FIXTURE)
    assert r.returncode == 2
    assert "usage" in r.stderr
