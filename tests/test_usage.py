"""tools/usage.py (#263): the unit, the count-once rule, the window, the start-up
cut (method point 2), the upper-bound reads (method point 1), the tags, and that
nothing printed is transcript text.

Every store here is made up in a temporary folder; no real transcript is read.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "usage.py"
_spec = importlib.util.spec_from_file_location("usage_tool", SCRIPT)
usage = importlib.util.module_from_spec(_spec)
sys.modules["usage_tool"] = usage  # dataclasses look their module up by name
_spec.loader.exec_module(usage)

# Text that must never reach the output.
TITLE = "Secret planner title of a private item"
PROMPT = "PRIVATE-PROMPT-TEXT"
RESULT = "PRIVATE-RESULT-TEXT"
PATH = "C:/Users/someone/private-folder/notes.md"
SLUG_A = "C--proj-alpha"
SLUG_B = "C--proj-beta"
SLUG_W = "C--proj-alpha--claude-worktrees-t901-some-builder"
PRIVATE = (TITLE, PROMPT, RESULT, PATH, "private-folder", "someone", "proj-alpha", "proj-beta",
           "some-builder", "REPLY-TEXT")


def reply(mid, ts, *, model="claude-sonnet-5-5", i=100_000, cw=0, cr=0, out=0, stop="end_turn",
          calls=(), side=False, usage_=True):
    content = [{"type": "text", "text": "REPLY-TEXT"}]
    content += [{"type": "tool_use", "id": cid, "name": name, "input": inp} for cid, name, inp in calls]
    msg = {"id": mid, "model": model, "content": content, "stop_reason": stop}
    if usage_:
        msg["usage"] = {"input_tokens": i, "cache_creation_input_tokens": cw,
                        "cache_read_input_tokens": cr, "output_tokens": out}
    return {"type": "assistant", "timestamp": ts, "isSidechain": side, "message": msg}


def user(text, ts, meta=False):
    return {"type": "user", "timestamp": ts, "isMeta": meta, "message": {"role": "user", "content": text}}


def result(use_id, text, ts):
    return {"type": "user", "timestamp": ts,
            "message": {"content": [{"type": "tool_result", "tool_use_id": use_id, "content": text}]}}


def title(t):
    return {"type": "custom-title", "customTitle": t}


def write(path: Path, records, junk=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(r) for r in records]
    if junk:
        lines.insert(1, "{not json")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run(capsys, *argv):
    assert usage.main(list(argv)) == 0
    out = capsys.readouterr().out
    for word in PRIVATE:
        assert word not in out, f"{word!r} printed"
    return out


def T(day, hms="10:00:00"):
    return f"2026-11-{day:02d}T{hms}.000Z"


@pytest.fixture
def store(tmp_path):
    """Planner in A (11-18), its fork in B with one new reply (11-20), a full copy
    in B, a builder in a worktree slug (11-19) with a subagent, and one session
    outside the window (11-10)."""
    s = tmp_path / "store"
    write(s / SLUG_A / "aaaa1111-0000.jsonl", [
        title(TITLE),
        user(PROMPT, T(18, "09:59:00")),
        reply("m1", T(18), stop="tool_use", calls=[("u1", "Read", {"file_path": PATH})]),
        result("u1", RESULT, T(18, "10:00:01")),
        reply("m2", T(18, "10:00:02")),
        reply("syn", T(18, "10:00:03"), model="<synthetic>"),
        reply("side", T(18, "10:00:04"), side=True),
    ], junk=True)
    write(s / SLUG_B / "bbbb2222-0000.jsonl", [
        title("manager of things"),
        reply("m1", T(18)), reply("m2", T(18, "10:00:02")),
        user(PROMPT, T(20, "09:00:00")),
        reply("m3", T(20)),
    ])
    write(s / SLUG_B / "cccc3333-0000.jsonl", [title("manager copy"), reply("m1", T(18)), reply("m2", T(18))])
    write(s / SLUG_W / "dddd4444-0000.jsonl", [user(PROMPT, T(19)), reply("b1", T(19)), reply("b2", T(19))])
    write(s / SLUG_W / "dddd4444-0000" / "subagents" / "agent-x.jsonl",
          [reply("sa1", T(19), side=True, out=100_000)])
    write(s / SLUG_A / "eeee5555-0000.jsonl", [title("planner old"), reply("old", T(10))])
    return s


# ---- the unit and the count -----------------------------------------------------


def test_unit_is_input_plus_weighted_parts():
    assert usage.eq(1, 1, 1, 1) == pytest.approx(1 + 1.25 + 0.1 + 5)
    r = usage.Reply("x", "", "m", 10, 100, 1000, 5, 0)
    assert r.eq == pytest.approx(10 + 125 + 100 + 25)
    assert r.ctx == 1110


def test_a_reply_is_counted_once_across_files_in_sorted_order(store):
    sessions = {s.sid: s for s in usage.scan(str(store))}
    # A is read first (sorted), so the shared replies count there
    assert [r.mid for r in sessions["aaaa1111-0000"].counted()] == ["m1", "m2"]
    assert [r.mid for r in sessions["bbbb2222-0000"].counted()] == ["m3"]
    # a full copy has nothing of its own, so it has no first reply and joins no window
    assert sessions["cccc3333-0000"].counted() == []
    assert sessions["cccc3333-0000"].first_day() is None


def test_the_order_does_not_depend_on_listing_order(store, monkeypatch):
    real = usage.os.listdir
    monkeypatch.setattr(usage.os, "listdir", lambda p: list(reversed(real(p))))
    sessions = {s.sid: s for s in usage.scan(str(store))}
    assert [r.mid for r in sessions["aaaa1111-0000"].counted()] == ["m1", "m2"]


def test_window_is_by_the_first_counted_reply_inclusive(store):
    rules = [usage.role_rule(x) for x in usage.DEFAULT_ROLES]
    got = {s.sid for _, s, _ in usage.in_window(str(store), "2026-11-18", "2026-11-20", rules)}
    assert got == {"aaaa1111-0000", "bbbb2222-0000", "dddd4444-0000"}
    # the fork's first own reply is 11-20, so a window ending 11-19 leaves it out
    got = {s.sid for _, s, _ in usage.in_window(str(store), "2026-11-18", "2026-11-19", rules)}
    assert got == {"aaaa1111-0000", "dddd4444-0000"}


def test_synthetic_and_sidechain_replies_are_left_out_and_subagents_read_apart(store):
    s = next(x for x in usage.scan(str(store)) if x.sid == "aaaa1111-0000")
    assert "syn" not in [r.mid for r in s.replies]
    assert "side" not in [r.mid for r in s.replies]
    assert s.bad_lines == 1
    b = next(x for x in usage.scan(str(store)) if x.sid == "dddd4444-0000")
    assert [r.mid for x in b.subagents for r in x.counted()] == ["sa1"]
    assert "sa1" not in [r.mid for r in b.replies]


def test_baseline_figures(store, capsys):
    out = run(capsys, "baseline", "--store", str(store), "--from", "2026-11-17", "--to", "2026-11-24")
    assert "session files counted: 3" in out
    lines = {ln.split()[0]: ln.split() for ln in out.splitlines()[2:-1]}
    # planner: 2 replies of 0.1M each; manager (the fork): 1; builder: 2
    assert lines["planner"][1:6] == ["sonnet-5-5", "1", "0", "2", "1"]
    assert lines["manager"][4] == "1"
    assert lines["builder"][4] == "2"
    assert out.strip().endswith("total inEq: 0.5M")


def test_ledger_sums_subagents_apart(store, capsys):
    out = run(capsys, "ledger", "--store", str(store), "--from", "2026-11-17", "--to", "2026-11-24")
    sub = [ln for ln in out.splitlines() if "subagents" in ln and ln.startswith("builder")]
    # 100,000 input + 5 x 100,000 output
    assert sub and "replies=     1" in sub[0] and "inEq=     0.6" in sub[0]
    assert "#1   aaaa1111" in out  # an index and an 8-character prefix, nothing more


# ---- method point 2: the start-up cut -------------------------------------------


def stop_session(tmp_path, records):
    return usage.read_session(str(write(tmp_path / "s.jsonl", records)))


def test_startup_runs_to_the_first_reply_that_ends_the_turn_through_peer_messages(tmp_path):
    s = stop_session(tmp_path, [
        user(PROMPT, T(20)),
        reply("a", T(20), stop="tool_use"),
        user("<cross-session-message from=x>hi</cross-session-message>", T(20)),
        reply("b", T(20), stop="tool_use"),
        reply("c", T(20), stop="end_turn"),
        user(PROMPT, T(20)),
        reply("d", T(20)),
    ])
    start, ended = usage.startup_cut(s.replies)
    assert [r.mid for r in start] == ["a", "b", "c"] and ended
    assert s.openers == ["typed", "peer message", "typed"]


def test_stop_reason_is_read_from_the_last_record_of_an_id(tmp_path):
    first = reply("a", T(20), stop=None, calls=[("u1", "Bash", {"command": "ls"})])
    second = reply("a", T(20), stop="end_turn", usage_=False)
    second["message"]["usage"] = {"input_tokens": 999_999}  # a later record's usage is not taken
    s = stop_session(tmp_path, [first, second, reply("b", T(20))])
    assert len(s.replies) == 2
    a = s.replies[0]
    assert a.stop == "end_turn" and a.inp == 100_000 and [c.name for c in a.calls] == ["Bash"]
    start, ended = usage.startup_cut(s.replies)
    assert [r.mid for r in start] == ["a"] and ended


def test_a_session_with_no_ending_reply_counts_whole_and_says_so(tmp_path, capsys):
    p = write(tmp_path / "s.jsonl", [reply("a", T(20), stop="tool_use"), reply("b", T(20), stop=None)])
    start, ended = usage.startup_cut(usage.read_session(str(p)).replies)
    assert len(start) == 2 and not ended
    out = run(capsys, "replies", str(p))
    assert "no ending reply" in out


def test_startup_subcommand(store, capsys):
    out = run(capsys, "startup", "--store", str(store), "--from", "2026-11-17", "--to", "2026-11-24",
              "--sessions")
    assert "first reply whose stop reason ends the turn" in out
    row = next(ln for ln in out.splitlines() if ln.startswith("planner "))
    # planner: the cut ends at m2 (end_turn): 2 replies, 0.2M = 200k
    assert row.split()[4:6] == ["2", "200"]


# ---- method point 1: reads are upper bounds ----------------------------------------


def test_reads_are_upper_bounds_and_print_only_tool_and_extension(tmp_path, capsys):
    p = write(tmp_path / "s.jsonl", [
        user(PROMPT, T(20)),
        reply("a", T(20), i=0, cr=1000, stop="tool_use", calls=[("u1", "Read", {"file_path": PATH}),
                                                               ("u2", "mcp__someserver__query", {})]),
        result("u1", "x" * 400, T(20)),
        result("u2", "", T(20)),
        user("y" * 100, T(20), meta=True),
        reply("b", T(20), i=0, cr=1200, stop="end_turn"),
        reply("c", T(20), i=0, cr=9000, stop="tool_use", calls=[("u9", "Read", {"file_path": PATH})]),
        result("u9", "z" * 9999, T(20)),
    ])
    out = run(capsys, "reads", str(p))
    assert "UPPER BOUNDS" in out
    assert "growth=200 resultChars=500 chars/token~2.50" in out
    rows = [ln.split() for ln in out.splitlines() if ln.strip().startswith(("1 ", "2 "))]
    assert rows[0][:4] == ["1", "Read", ".md", "160"]
    assert rows[1][:2] == ["1", "mcp"] and "someserver" not in out
    assert rows[2][1:3] == ["(injected", "text)"]
    assert "9999" not in out  # a read after the start-up turn is not in it


def test_the_docstring_carries_both_method_points():
    doc = usage.__doc__
    assert "upper bound" in doc and "Method point 1" in doc
    assert "Method point 2" in doc and "first reply whose stop reason ends the turn" in doc
    assert "counted once" in doc


# ---- tags -----------------------------------------------------------------------


def test_tags_rules_carry_message_in_idle_and_batching(tmp_path, capsys):
    s = tmp_path / "store"
    write(s / "C--x" / "ffff6666-0000.jsonl", [
        title("a manager"),
        user(PROMPT, T(21, "08:00:00")),
        reply("s1", T(21, "08:00:01")),  # start-up, ends at once
        user(PROMPT, T(21, "08:01:00")),
        reply("r1", T(21, "08:01:01"), stop="tool_use",
              calls=[("x1", "Bash", {"command": "python tools/reproof.py 12 abc"})]),
        reply("r2", T(21, "08:01:02"), stop="tool_use", calls=[("x2", "Bash", {"command": "ls"})]),
        reply("r3", T(21, "08:01:03"), stop="end_turn"),
        user("<cross-session-message from=y>hello</cross-session-message>", T(21, "10:00:00")),
        reply("p1", T(21, "10:00:01"), stop="tool_use", calls=[("x3", "SendMessage", {"to": "y"})]),
        reply("p2", T(21, "10:00:02"), stop="end_turn"),
        user("<cross-session-message from=y>again</cross-session-message>", T(21, "10:00:03")),
        reply("q1", T(21, "10:00:04")),
        user(PROMPT, T(21, "10:01:00")),
        reply("z1", T(21, "10:01:01")),
    ])
    sess = usage.scan(str(s))[0]
    rules = [usage.tag_rule(x) for x in usage.DEFAULT_TAGS]
    tags = usage.tag_replies(sess, sess.counted(), rules)
    assert tags == ["start-up", "reproof", "reproof", "reproof", "message out", "message out",
                    "message in", "untagged"]
    out = run(capsys, "tags", "--store", str(s), "--from", "2026-11-21", "--to", "2026-11-21",
              "--idle-gap", "3600")
    assert "== manager: sessions=1 replies=8" in out
    assert "untagged share of inEq: 12%" in out
    # p1 comes 2 h after r3: one idle re-read
    assert "idle re-reads (reply after a gap > 3600s): replies=1" in out
    # r2 is a one-call reply right after the one-call r1 in the same turn
    assert "none=5 one=3 more=0" in out and "same turn=1" in out


def test_custom_tag_and_role_rules_replace_the_defaults(store, capsys):
    out = run(capsys, "tags", "--store", str(store), "--from", "2026-11-17", "--to", "2026-11-24",
              "--role", "lead=title:planner", "--tag", "reading=^Read", "--only", "lead")
    assert "== lead:" in out and "== manager" not in out and "== other" not in out
    assert "reading" in out and "reproof" not in out


@pytest.mark.parametrize("bad", ["planner", "x=title", "x=colour:a", "=title:a", "x=title:("])
def test_a_bad_role_rule_is_refused(store, bad):
    with pytest.raises(SystemExit):
        usage.main(["baseline", "--store", str(store), "--from", "2026-11-17", "--to", "2026-11-24",
                    "--role", bad])


@pytest.mark.parametrize("bad", ["noequals", "start-up=x", "x=("])
def test_a_bad_tag_rule_is_refused(store, bad):
    with pytest.raises(SystemExit):
        usage.main(["tags", "--store", str(store), "--from", "2026-11-17", "--to", "2026-11-24",
                    "--tag", bad])


def test_bad_dates_and_reversed_window_are_refused(store):
    for lo, hi in (("2026-11-1", "2026-11-24"), ("2026-11-25", "2026-11-24")):
        with pytest.raises(SystemExit):
            usage.main(["baseline", "--store", str(store), "--from", lo, "--to", hi])


# ---- compacts, trial, context, fail soft ---------------------------------------------


def compact(ts, pre=150_000, post=20_000):
    return {"type": "system", "subtype": "compact_boundary", "timestamp": ts,
            "compactMetadata": {"trigger": "manual", "preTokens": pre, "postTokens": post, "durationMs": 5}}


def summary(ts):
    return {"type": "user", "timestamp": ts, "isCompactSummary": True, "message": {"content": "S" * 4000}}


@pytest.fixture
def compact_store(tmp_path):
    s = tmp_path / "store"
    # two sessions of different roles under one folder: each keeps its own role
    write(s / SLUG_A / "gggg7777-0000.jsonl", [
        title("the planner"), reply("c1", T(22)), compact(T(22, "11:00:00")), summary(T(22, "11:00:01")),
        reply("c2", T(22, "11:00:02"), i=30_000), reply("c3", T(22, "11:00:03"))])
    write(s / SLUG_A / "hhhh8888-0000.jsonl", [
        title("the manager"), reply("d1", T(22)), compact(T(22, "12:00:00")), reply("d2", T(22, "12:00:02"))])
    return s


def test_compacts_keep_each_files_role(compact_store, capsys):
    out = run(capsys, "compacts", "--store", str(compact_store), "--from", "2026-11-22", "--to", "2026-11-22")
    assert "compacts dated 2026-11-22..2026-11-22: 2" in out
    assert "compactMetadata keys seen: durationMs, postTokens, preTokens, trigger" in out
    planner = next(ln for ln in out.splitlines() if ln.startswith("planner"))
    manager = next(ln for ln in out.splitlines() if ln.startswith("manager"))
    assert planner.split()[1:4] == ["1", "150k", "30k"] and "1.0k" in planner  # 4000 chars / 4
    assert manager.split()[1] == "1"


def test_compacts_none_found(store, capsys):
    out = run(capsys, "compacts", "--store", str(store), "--from", "2026-11-17", "--to", "2026-11-24")
    assert "none found" in out


def test_trial_prints_the_role_and_not_the_folder(compact_store, capsys):
    out = run(capsys, "trial", "--store", str(compact_store), "gggg7777-0000")
    assert "role: planner" in out
    assert "trigger=manual pre=150000 post=20000" in out and "summaryChars=4000" in out
    assert "replies after: 2" in out
    assert "session not found" in run(capsys, "trial", "--store", str(compact_store), "zzzz9999-0000")


@pytest.mark.parametrize("bad", ["*", "../x", "aaaa*", "a/b/c", "short"])
def test_trial_refuses_a_session_id_that_is_not_one(compact_store, bad):
    with pytest.raises(SystemExit):
        usage.main(["trial", "--store", str(compact_store), bad])


def test_context_prints_kinds_and_counts_only_and_fails_soft(tmp_path, capsys):
    p = write(tmp_path / "s.jsonl", [
        {"type": "attachment", "attachment": {"type": "prompt_snapshot", "systemPrompt": "P" * 800}},
        {"type": "attachment", "attachment": {"type": "nested_memory", "path": PATH, "content": "M" * 40}},
        {"type": "api-request-shape", "shape": json.dumps({"model": "x", "tools": [
            {"name": "Read"}, {"name": "mcp__someserver__do"}, {"name": "mcp__other__do"}]})},
    ])
    out = run(capsys, "context", str(p))
    assert "system prompt" in out and "nested memory files" in out
    assert "tools in request: 3; mcp servers: 2" in out
    assert "someserver" not in out and "P" * 50 not in out
    bare = write(tmp_path / "bare.jsonl", [reply("a", T(20))])
    out = run(capsys, "context", str(bare))
    assert "attachment records: none found" in out and "api-request-shape record: none found" in out


# ---- per-file views -------------------------------------------------------------------


def test_turns_and_replies_name_what_opened_each_turn(tmp_path, capsys):
    p = write(tmp_path / "s.jsonl", [
        user(PROMPT, T(20)), reply("a", T(20)),
        user("<task-notification>done</task-notification>", T(20)), reply("b", T(20)),
        user("<system-reminder>r</system-reminder>", T(20)), reply("c", T(20)),
        {"type": "queue-operation", "timestamp": T(20)},
    ])
    out = run(capsys, "turns", str(p))
    kinds = [ln.split()[1] for ln in out.splitlines() if ln[:4].strip().isdigit()]
    assert kinds == ["typed", "app", "system"]
    out = run(capsys, "replies", str(p))
    assert "-- user (app event)" in out and "-- record queue-operation" in out
    assert "stop=end_turn" in out


def test_every_subcommand_prints_no_transcript_text(store, compact_store, capsys):
    w = ["--from", "2026-11-01", "--to", "2026-11-30"]
    for cmd in ("baseline", "ledger", "startup", "tags", "compacts"):
        run(capsys, cmd, "--store", str(store), *w)
        run(capsys, cmd, "--store", str(compact_store), *w)
    f = str(store / SLUG_A / "aaaa1111-0000.jsonl")
    for cmd in ("context", "reads", "replies", "turns"):
        run(capsys, cmd, f)
    run(capsys, "trial", "--store", str(store), "aaaa1111-0000")


def test_the_code_holds_no_machine_path_and_reads_no_environment():
    src = SCRIPT.read_text(encoding="utf-8")
    for word in ("C:\\", "C:/", "/Users/", "/home/", "benha", "os.environ", "getenv", "shell=True"):
        assert word not in src
