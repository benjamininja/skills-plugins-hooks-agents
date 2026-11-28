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
    # F1: each figure is an estimate at the turn's mean ratio; only their sum is a bound
    assert "ESTIMATES at the turn's mean chars/token" in out
    # F5: this turn ended with positive growth, so the bound on the sum is claimed
    assert "together the figures are an upper bound" in out and "no bound is claimed" not in out
    assert "~tokens(est at mean)" in out
    assert "growth=200 resultChars=500 chars/token~2.50" in out
    rows = [ln.split() for ln in out.splitlines() if ln.strip().startswith(("1 ", "2 "))]
    assert rows[0][:4] == ["1", "Read", ".md", "160"]
    assert rows[1][:2] == ["1", "mcp"] and "someserver" not in out
    assert rows[2][1:3] == ["(injected", "text)"]
    assert "9999" not in out  # a read after the start-up turn is not in it


def test_reads_claims_no_bound_for_a_turn_that_never_ended(tmp_path, capsys):
    # F5: the result after the last reply is counted, but no growth follows it
    p = write(tmp_path / "s.jsonl", [
        user(PROMPT, T(20)),
        reply("a", T(20), i=0, cr=1000, stop="tool_use", calls=[("u1", "Read", {"file_path": PATH})]),
        result("u1", "x" * 400, T(20)),
        reply("b", T(20), i=0, cr=1200, stop="tool_use", calls=[("u2", "Read", {"file_path": PATH})]),
        result("u2", "x" * 4000, T(20)),
    ])
    out = run(capsys, "reads", str(p))
    assert "no bound is claimed: the turn has no ending reply" in out
    assert "upper bound" not in out


def test_reads_claims_no_bound_when_the_turn_has_no_growth(tmp_path, capsys):
    # F5: growth 0 falls back to an assumed ratio, which bounds nothing
    p = write(tmp_path / "s.jsonl", [
        user(PROMPT, T(20)),
        reply("a", T(20), i=0, cr=1000, stop="tool_use", calls=[("u1", "Read", {"file_path": PATH})]),
        result("u1", "x" * 400, T(20)),
        reply("b", T(20), i=0, cr=1000, stop="end_turn"),
    ])
    out = run(capsys, "reads", str(p))
    assert "no bound is claimed: growth is 0, so 4.0 is assumed" in out
    assert "chars/token~4.00" in out and "upper bound" not in out


def test_reads_claims_no_bound_when_a_compact_falls_inside_the_turn(tmp_path, capsys):
    # F7: the growth after a compact covers only what survived it
    p = write(tmp_path / "s.jsonl", [
        user(PROMPT, T(20)),
        reply("a", T(20), i=0, cr=150_000, stop="tool_use", calls=[("u1", "Read", {"file_path": PATH})]),
        result("u1", "x" * 400, T(20)),
        compact(T(20, "10:00:05")),
        reply("b", T(20, "10:00:06"), i=0, cr=160_000, stop="end_turn"),
    ])
    out = run(capsys, "reads", str(p))
    assert "no bound is claimed: a compact falls inside the turn" in out
    assert "upper bound" not in out


def test_reads_names_the_compact_before_negative_growth(tmp_path, capsys):
    # F9 of #297: an auto-compact inside the start-up leaves negative growth; both are named
    p = write(tmp_path / "s.jsonl", [
        user(PROMPT, T(20)),
        reply("a", T(20), i=0, cr=180_000, stop="tool_use", calls=[("u1", "Read", {"file_path": PATH})]),
        result("u1", "x" * 400, T(20)),
        compact(T(20, "10:00:05")),
        reply("b", T(20, "10:00:06"), i=0, cr=30_000, stop="end_turn"),
    ])
    out = run(capsys, "reads", str(p))
    line = next(ln for ln in out.splitlines() if ln.startswith("no bound is claimed"))
    assert line.startswith("no bound is claimed: a compact falls inside the turn")
    assert "growth is -150000, so 4.0 is assumed" in line


def test_shapes_finds_where_a_peer_message_is_stored_and_prints_no_text(tmp_path, capsys):
    s = tmp_path / "store"
    peer = "Another Claude session sent a message:\n<cross-session-message from=x>" + PROMPT
    write(s / "C--x" / "llll0001-0000.jsonl", [
        title("a manager"),
        user(PROMPT, T(21, "08:00:00")),
        reply("a", T(21, "08:00:01")),
        user(peer, T(21, "08:01:00"), meta=True),                          # a meta string
        {"type": "attachment", "timestamp": T(21), "attachment": {         # an attachment
            "type": "queued_command", "content": "<cross-session-message from=x>" + PROMPT}},
        {"type": "user", "timestamp": T(21), "message": {"content": [      # a list block
            {"type": "text", "text": "see:\n\n\n<cross-session-message>" + PROMPT}]}},
        reply("b", T(21, "08:02:01")),
        {"type": "user", "isSidechain": True, "message": {"content": "<cross-session-message>"}},
        {"type": "progress", "message": {"content": [
            {"type": "tool_use", "input": {"privatefield": "<cross-session-message>"}}]}},
    ])
    out = run(capsys, "shapes", "--store", str(s), "--from", "2026-11-21", "--to", "2026-11-21",
              "--only", "manager")
    assert "sessions=1 records=8" in out
    assert "type=user meta=False content=str:text" in out
    assert "records holding 'cross-session-message': 4 ==" in out
    # keys below the third level may be data: they print as ?
    assert "| at .message.content[].input.? | at start" in out and "privatefield" not in out
    lines = [ln for ln in out.splitlines() if " | at " in ln]
    assert any("meta=True content=str:text | at .message.content | line 2" in ln for ln in lines)
    assert any("attachment=queued_command" in ln and "| at .attachment.content | at start" in ln for ln in lines)
    assert any("content=list[text:text] | at .message.content[].text | line 3 or later" in ln for ln in lines)
    # user record key names, with counts; the sidechain record is left out
    assert "isMeta=2 message=3 timestamp=3 type=3" in out and "isSidechain" not in out
    assert "Another Claude" not in out and "from=x" not in out


def test_shapes_hides_a_name_keyed_map_at_depth_one(tmp_path, capsys):
    # F1 of #301: a data map keyed by names right under the record prints "?"
    s = tmp_path / "store"
    write(s / "C--x" / "mmmm0001-0000.jsonl", [
        title("a manager"), user(PROMPT, T(21)), reply("a", T(21)),
        {"type": "user", "toolUseResult": {"secret-branch-name": "<cross-session-message>"}},
        {"type": "user", "toolUseResult": {"stdout": "<cross-session-message>"}},
    ])
    out = run(capsys, "shapes", "--store", str(s), "--from", "2026-11-21", "--to", "2026-11-21")
    assert "| at .toolUseResult.? | at start" in out and "secret-branch-name" not in out
    assert "| at .toolUseResult.stdout | at start" in out


def test_needle_places_positions_and_shape_helpers():
    # F2 of #301: a CRLF lead is still at the start
    assert list(usage.needle_places({"content": "\r\n<cross-session-message>"}, "cross-session-message")) == [
        (".content", "at start")]
    # F3 of #301: the branches no other test runs
    assert list(usage.needle_places({"content": "hi <cross-session-message>"}, "cross-session-message")) == [
        (".content", "line 1, after text")]
    assert list(usage.needle_places({"content": "a\nb\nc<cross-session-message>"}, "cross-session-message")) == [
        (".content", "line 3 or later")]
    # #312: a top-level key that is not a known word prints "?"
    assert list(usage.needle_places({"c": "<cross-session-message>"}, "cross-session-message")) == [
        (".?", "at start")]
    assert list(usage.needle_places({"cross-session-message": 1}, "cross-session-message")) == []
    assert usage.lead_of("  ") == "empty" and usage.lead_of("<1x>") == "<?>" and usage.lead_of("hi") == "text"
    assert usage.lead_of("<task-notification>x") == "<task-notification>"
    assert usage.content_kind(None) == "none" and usage.content_kind(5) == "?"
    assert usage.content_kind(["x", {"type": "a b"}]) == "list[?]"
    assert usage.safe(None) == "-" and usage.safe("a/b") == "?" and usage.safe(3) == "?"
    att = {"type": "attachment", "attachment": {"type": "queued_command", "content": "<task-notification>z"}}
    assert usage.shape_of(att) == ("type=attachment attachment=queued_command meta=False "
                                   "attachment.content=str:<task-notification>")
    assert usage.lead_of("<x-y>z") == "<?>"  # a tag name that is not a known word (#312)


def test_shapes_counts_a_needle_only_in_a_key_as_not_in_a_value(tmp_path, capsys):
    s = tmp_path / "store"
    write(s / "C--x" / "nnnn0001-0000.jsonl", [
        title("a manager"), user(PROMPT, T(21)), reply("a", T(21)),
        {"type": "progress", "cross-session-message": 1},
    ])
    out = run(capsys, "shapes", "--store", str(s), "--from", "2026-11-21", "--to", "2026-11-21")
    assert "| at (not in a string value) | -" in out


def queued(ts, prompt):
    return {"type": "attachment", "timestamp": ts, "attachment": {"type": "queued_command", "prompt": prompt}}


def test_shapes_counts_source_keys_overlap_and_turn_position(tmp_path, capsys):
    # step 3, part 1: the probe that settles how a peer message is stored
    peer = "Another Claude session sent a message:\n<cross-session-message from=x>" + PROMPT
    meta_peer = {**user(peer, T(21, "08:00:04"), meta=True),
                 "origin": {"kind": "peer", "name": "a private name with spaces"}, "turnOrigin": "x" * 30}
    typed = {**user(PROMPT, T(21, "08:00:00")), "promptSource": "sdk"}
    s = tmp_path / "store"
    write(s / "C--x" / "oooo0001-0000.jsonl", [
        title("a manager"),
        typed,
        reply("r1", T(21, "08:00:01"), stop="tool_use", calls=[("u1", "Bash", {"command": "ls"})]),
        queued(T(21, "08:00:02"), "<cross-session-message from=x>" + PROMPT),   # inside a running turn
        meta_peer,                                                             # the same message, again
        result("u1", RESULT, T(21, "08:00:05")),
        reply("r2", T(21, "08:00:06"), stop="end_turn"),
        user(peer, T(21, "08:01:00"), meta=True),                              # after an ended turn, alone
        queued(T(21, "08:01:01"), "<cross-session-message from=x>" + PROMPT),   # no meta record follows
        reply("r3", T(21, "08:01:02"), stop="end_turn"),
        queued(T(21, "08:02:00"), "<cross-session-message from=x>" + PROMPT),   # the file ends
    ])
    out = run(capsys, "shapes", "--store", str(s), "--from", "2026-11-21", "--to", "2026-11-21")
    lines = out.splitlines()

    def count(text):
        (ln,) = [x for x in lines if x.endswith(text) or f"  {text} |" in x or x.strip().endswith(text)]
        return int(ln.split()[0])

    # source keys, by what the record is: an object prints its keys, a long or spaced value prints ?
    assert count("meta, tag on line 1-2 | origin={kind=peer,name=?} turnOrigin=? promptSource=-") == 1
    assert count("meta, tag on line 1-2 | origin=- turnOrigin=- promptSource=-") == 1
    assert count("non-meta typed | origin=- turnOrigin=- promptSource=sdk") == 1
    assert count("tool result | origin=- turnOrigin=- promptSource=-") == 1
    # overlap
    assert count("queued command, then a meta record before the next reply") == 1
    assert count("meta record, no queued command since the last reply") == 1
    assert count("queued command, no meta record before the next reply") == 1
    assert count("queued command, no meta record before the end of the file") == 1
    # where they land
    assert count("tagged queued command | inside a running turn") == 1
    assert count("tagged queued command | after a reply that ended its turn") == 2
    assert count("tagged meta record | inside a running turn") == 1
    assert count("tagged meta record | after a reply that ended its turn") == 1
    assert "private name" not in out and "xxxxxxxxxx" not in out


LEAD_PEER = "Another Claude session sent a message:\n<cross-session-message from=x>" + PROMPT


def peer_meta(ts, origin=True):
    rec = user(LEAD_PEER, ts, meta=True)
    if origin:
        rec.update(origin={"kind": "peer", "from": "some-session", "name": "a-nameplate"},
                   turnOrigin="peer", promptSource="system")
    return rec


def test_a_meta_peer_record_with_origin_opens_a_peer_turn(tmp_path):
    # step 3: the stored shape, read from origin.kind
    s = stop_session(tmp_path, [
        {**user(PROMPT, T(21)), "origin": {"kind": "human"}, "turnOrigin": "human"},
        reply("a", T(21)),
        peer_meta(T(21, "10:01:00")),
        reply("b", T(21, "10:01:01")),
    ])
    assert s.openers == ["typed", "peer message"]
    assert s.opener_of(s.replies[1]) == "peer message"


def test_a_meta_peer_record_without_origin_falls_back_to_its_text(tmp_path):
    s = stop_session(tmp_path, [user(PROMPT, T(21)), reply("a", T(21)),
                                peer_meta(T(21, "10:01:00"), origin=False), reply("b", T(21, "10:01:01"))])
    assert s.openers == ["typed", "peer message"]


def test_other_meta_records_still_open_no_turn(tmp_path):
    s = stop_session(tmp_path, [
        user(PROMPT, T(21)), reply("a", T(21)),
        user("<system-reminder>r</system-reminder>", T(21), meta=True),
        {**user("x", T(21), meta=True), "turnOrigin": "system", "promptSource": "system"},
        reply("b", T(21)),
    ])
    assert s.openers == ["typed"]


def test_sources_by_field_name_each_turn(tmp_path):
    s = stop_session(tmp_path, [
        {**user("<task-notification>x", T(21)), "origin": {"kind": "task-notification"}}, reply("a", T(21)),
        {**user(PROMPT, T(21)), "origin": {"kind": "plugin", "name": "q"}, "turnOrigin": "system"},
        reply("b", T(21)),
        {**user(PROMPT, T(21)), "turnOrigin": "human"}, reply("c", T(21)),
        {**user(PROMPT, T(21)), "origin": {"kind": "brand-new"}}, reply("d", T(21)),
    ])
    assert s.openers == ["app event", "plugin", "typed", "other source"]


def test_a_queued_peer_message_inside_a_turn_tags_the_next_reply_message_in(tmp_path):
    # step 3: a queued_command attachment arrives inside a running turn and opens none
    st = tmp_path / "store"
    write(st / "C--x" / "pppp0001-0000.jsonl", [
        title("a manager"),
        user(PROMPT, T(21, "08:00:00")), reply("s1", T(21, "08:00:01")),
        user(PROMPT, T(21, "08:01:00")),
        reply("r1", T(21, "08:01:01"), stop="tool_use",
              calls=[("x1", "Bash", {"command": "python tools/reproof.py 1 a"})]),
        queued(T(21, "08:01:02"), "<cross-session-message from=x>" + PROMPT),
        reply("r2", T(21, "08:01:03"), stop="tool_use", calls=[("x2", "Bash", {"command": "ls"})]),
        reply("r3", T(21, "08:01:04"), stop="end_turn"),
        api_blob := {"type": "api-request-blob", "message": {"content": [
            {"type": "text", "text": "<system-reminder>\n\n<cross-session-message>"}]}},
    ])
    sess = usage.scan(str(st))[0]
    assert len(sess.openers) == 2  # the queued message opens no turn; the context copy is ignored
    tags = usage.tag_replies(sess, sess.counted(), [usage.tag_rule(x) for x in usage.DEFAULT_TAGS])
    assert tags == ["start-up", "reproof", "message in", "message in"]
    assert api_blob["type"] == "api-request-blob"


def test_a_message_queued_and_then_stored_as_meta_counts_once(tmp_path):
    s = stop_session(tmp_path, [
        user(PROMPT, T(21)), reply("a", T(21), stop="tool_use"),
        queued(T(21), "<cross-session-message from=x>" + PROMPT),
        peer_meta(T(21)),  # the same message, before the next reply
        reply("b", T(21)),
    ])
    assert s.openers == ["typed"]
    assert s.replies[1].after_peer


def test_a_different_peer_message_after_a_queued_one_still_opens_a_turn(tmp_path):
    # F1 of #308: message A is queued, the owner interrupts, then a different message B
    # arrives as a meta record before the next reply. B is not A: it opens a turn.
    b = {**user("Another Claude session sent a message:\n<cross-session-message from=y>B-TEXT", T(21),
                meta=True), "origin": {"kind": "peer"}, "turnOrigin": "peer"}
    s = stop_session(tmp_path, [
        user(PROMPT, T(21)),
        reply("a", T(21), stop="tool_use", calls=[("u1", "Bash", {"command": "ls"})]),
        queued(T(21), "<cross-session-message from=x>A-TEXT"),
        result("u1", RESULT, T(21)),
        user("[Request interrupted by user]", T(21)),
        b,
        reply("b", T(21)),
    ])
    assert s.openers == ["typed", "typed", "peer message"]
    assert s.opener_of(s.replies[1]) == "peer message" and s.replies[1].after_peer


def test_tags_counts_messages_in_by_how_they_arrive(tmp_path, capsys):
    st = tmp_path / "store"
    write(st / "C--x" / "qqqq0001-0000.jsonl", [
        title("a manager"),
        user(PROMPT, T(21, "08:00:00")), reply("a", T(21, "08:00:01"), stop="tool_use"),
        queued(T(21, "08:00:02"), "<cross-session-message from=x>" + PROMPT),
        reply("b", T(21, "08:00:03")),
        peer_meta(T(21, "08:01:00")), reply("c", T(21, "08:01:01")),
    ])
    out = run(capsys, "tags", "--store", str(st), "--from", "2026-11-21", "--to", "2026-11-21")
    assert "turns opened by: typed=1 peer-message=1" in out
    assert "peer messages inside a running turn=1" in out


def test_word_hides_ids_under_origin(tmp_path, capsys):
    # the assistant's finding on the probe at 8b7084b: from=, runId= and name= held ids
    o = {"kind": "peer", "from": "agent-abc", "runId": "run-123", "name": "a-nameplate",
         "fromSession": "s", "msg_id": "m", "fromMode": "prompting", "producer": "session-task",
         "handback": True}
    w = usage.word(o)
    for secret in ("agent-abc", "run-123", "a-nameplate"):
        assert secret not in w
    assert "kind=peer" in w and "fromMode=prompting" in w and "producer=session-task" in w
    assert "handback=true" in w and "from=?" in w and "runId=?" in w and "name=?" in w


def test_word_prints_only_known_words_and_keys():
    # a value prints only when the store was seen to hold it; a short id or name does not
    assert usage.word("peer") == "peer" and usage.word("sdk") == "sdk"
    assert usage.word("a b") == "?" and usage.word("x" * 25) == "?" and usage.word("ab12cd34ef") == "?"
    assert usage.word(None) == "-" and usage.word(True) == "true" and usage.word(3) == "number"
    assert usage.word([1]) == "?" and usage.word({"kind": {"n": 1}}) == "{kind=?}"
    # inside an object: keys from the known set, else ?; values only under kind, producer or fromMode
    assert usage.word({f"k{i:02}": "v" for i in range(12)}) == "{" + ",".join(
        "?=?" for _ in range(10)) + ",...}"
    assert usage.word({"kind": "peer", "abc123": "v"}) == "{?=?,kind=peer}"
    assert usage.word({"producer": "a-plugin-name"}) == "{producer=?}"
    assert usage.word({"producer": "session-task"}) == "{producer=session-task}"


def test_shapes_refuses_a_needle_that_is_not_a_name(store):
    for bad in ("a b", "<x>", "x"):
        with pytest.raises(SystemExit):
            usage.main(["shapes", "--store", str(store), "--from", "2026-11-17", "--to", "2026-11-24",
                        "--needle", bad])


def test_tags_counts_openers_by_kind_with_ambiguous_apart(tmp_path, capsys):
    # F8: step 2 reads this line to check the stored lead of a peer message
    s = tmp_path / "store"
    write(s / "C--x" / "kkkk0001-0000.jsonl", [
        title("a manager"),
        user(PROMPT, T(21, "08:00:00")), reply("a", T(21, "08:00:01")),
        user("<cross-session-message from=y>hi</cross-session-message>", T(21, "08:01:00")),
        reply("b", T(21, "08:01:01")),
        user("Some lead the script does not know:\n<cross-session-message from=y>hi</cross-session-message>",
             T(21, "08:02:00")),
        reply("c", T(21, "08:02:01")),
        user("<task-notification>done</task-notification>", T(21, "08:03:00")), reply("d", T(21, "08:03:01")),
    ])
    out = run(capsys, "tags", "--store", str(s), "--from", "2026-11-21", "--to", "2026-11-21")
    assert ("turns opened by: typed=1 peer-message=1 app-event=1 plugin=0 system=0 system-reminder=0 "
            "ambiguous=1 other-source=0; peer messages inside a running turn=0" in out)


def test_the_docstring_carries_both_method_points():
    doc = " ".join(usage.__doc__.split())
    assert "Method point 1" in doc and "an estimate at that mean ratio" in doc
    assert "For a turn that ended with positive growth" in doc and "taken together they are an upper bound" in doc
    assert "No bound is claimed for a turn with no ending reply" in doc
    assert "One result alone is never bounded" in doc
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
    for cmd in ("baseline", "ledger", "startup", "tags", "compacts", "shapes"):
        run(capsys, cmd, "--store", str(store), *w)
        run(capsys, cmd, "--store", str(compact_store), *w)
    f = str(store / SLUG_A / "aaaa1111-0000.jsonl")
    for cmd in ("context", "reads", "replies", "turns"):
        run(capsys, cmd, f)
    run(capsys, "trial", "--store", str(store), "aaaa1111-0000")


def test_a_compact_copied_into_a_resumed_file_counts_once(tmp_path, capsys):
    # F2: the fork copies the history, compact record included; with a uuid and without one
    s = tmp_path / "store"
    for name, extra in (("uuid", {"uuid": "cmp-1"}), ("bare", {})):
        cp = {**compact(T(22, "11:00:00")), **extra}
        write(s / f"C--{name}" / "iiii0001-0000.jsonl",
              [title("the planner"), reply(f"{name}1", T(22)), cp, reply(f"{name}2", T(22, "11:00:02"))])
        write(s / f"C--{name}" / "iiii0002-0000.jsonl",
              [title("the planner"), reply(f"{name}1", T(22)), cp, reply(f"{name}2", T(22, "11:00:02")),
               reply(f"{name}3", T(23))])
    out = run(capsys, "compacts", "--store", str(s), "--from", "2026-11-22", "--to", "2026-11-22")
    assert "compacts dated 2026-11-22..2026-11-22: 2" in out
    out = run(capsys, "baseline", "--store", str(s), "--from", "2026-11-17", "--to", "2026-11-24")
    planner = next(ln for ln in out.splitlines() if ln.startswith("planner"))
    assert planner.split()[2:4] == ["4", "2"]  # four session files, two compacts


@pytest.mark.parametrize("text,kind", [
    (PROMPT, "typed"),
    ("<cross-session-message from=x>hi</cross-session-message>", "peer message"),
    # the exact lead line the app writes
    ("Another Claude session sent a message:\n<cross-session-message from=x>hi</cross-session-message>",
     "peer message"),
    # F3: any other lead, one line and a single newline included, is not a peer message
    ("Look at this one:\n<cross-session-message from=x>hi</cross-session-message>", "ambiguous"),
    ("Another session sent a message:\n<cross-session-message from=x>hi</cross-session-message>",
     "ambiguous"),
    ("Look at what came in:\n\n<cross-session-message from=x>hi</cross-session-message>", "ambiguous"),
    ("please read this <cross-session-message from=x>hi</cross-session-message>", "ambiguous"),
    # F3: a peer message after a long system reminder is a peer message
    ("<system-reminder>" + "r" * 2000 + "</system-reminder>\n<cross-session-message from=x>hi"
     "</cross-session-message>", "peer message"),
    ("<system-reminder>r</system-reminder>\nAnother Claude session sent a message:\n"
     "<cross-session-message from=x>hi</cross-session-message>", "peer message"),
    ("<system-reminder>only</system-reminder>  ", "system reminder"),
    ("<system-reminder>unclosed", "system reminder"),
    ("<system-reminder>r</system-reminder>\n" + PROMPT, "typed"),
    ("<task-notification>done</task-notification>", "app event"),
    ("x" * 200 + "<task-notification>", "ambiguous"),
])
def test_the_opener_is_judged_at_the_start_of_the_text(text, kind):
    assert usage.opener_kind(text) == kind


def test_an_unreadable_timestamp_is_no_gap(tmp_path, capsys):
    # F4: seconds() returns None on a bad time, and no idle re-read is counted from it
    assert usage.seconds("not a time") is None and usage.seconds("") is None
    s = tmp_path / "store"
    write(s / "C--x" / "jjjj0001-0000.jsonl", [
        title("a manager"), reply("a", T(21, "08:00:00")), reply("b", "2026-11-21Tbroken"),
        reply("c", T(21, "12:00:00"))])
    out = run(capsys, "tags", "--store", str(s), "--from", "2026-11-21", "--to", "2026-11-21")
    # c is 4 h after a, the last readable time: one idle re-read, none from the broken one
    assert "replies=1 " in next(ln for ln in out.splitlines() if ln.startswith("idle re-reads"))


def test_context_reads_a_shape_stored_as_a_string_and_fails_soft_on_bad_json(tmp_path, capsys):
    # F4: the string-JSON branch, both ways
    good = write(tmp_path / "g.jsonl", [{"type": "api-request-shape", "shape": json.dumps({"tools": []})}])
    assert "tools in request: 0; mcp servers: 0" in run(capsys, "context", str(good))
    bad = write(tmp_path / "b.jsonl", [{"type": "api-request-shape", "shape": "{not json"}])
    assert "api-request-shape record: none found" in run(capsys, "context", str(bad))


# ---- #312: every printed store value is a known word ---------------------------------

PLANT = "plantedname"  # name-like, short, and in no known list: it must never print


def test_shapes_prints_no_unknown_type_key_block_or_tag(tmp_path, capsys):
    s = tmp_path / "store"
    write(s / "C--x" / "rrrr0001-0000.jsonl", [
        title("a manager"), user(PROMPT, T(21)), reply("a", T(21)),
        {"type": PLANT, "subtype": PLANT, "x": 1},
        {"type": "attachment", "attachment": {"type": PLANT}},
        {"type": "user", "timestamp": T(21), PLANT: 1, "message": {"content": [{"type": PLANT}]}},
        {"type": "user", "timestamp": T(21), "message": {"content": "<" + PLANT + ">x"}},
        {"type": "user", "timestamp": T(21), PLANT: "<cross-session-message>"},
    ])
    out = run(capsys, "shapes", "--store", str(s), "--from", "2026-11-21", "--to", "2026-11-21")
    assert PLANT not in out
    assert "type=? subtype=? meta=False" in out and "attachment=? meta=False" in out
    assert "content=list[?]" in out and "content=str:<?>" in out
    assert "| at .? | at start" in out
    keys = next(ln for ln in out.splitlines() if ln.startswith("?="))
    assert keys.startswith("?=2 ")  # the two planted keys, counted under one label


def test_model_names_print_only_when_known(tmp_path, capsys):
    s = tmp_path / "store"
    write(s / "C--x" / "ssss0001-0000.jsonl", [
        title("a planner"), user(PROMPT, T(21)),
        reply("a", T(21), model="claude-" + PLANT), reply("b", T(21), model="claude-" + PLANT),
        reply("c", T(21), model="claude-opus-5-5"),
    ])
    w = ["--store", str(s), "--from", "2026-11-21", "--to", "2026-11-21"]
    out = run(capsys, "baseline", *w)
    assert PLANT not in out
    row = next(ln for ln in out.splitlines() if ln.startswith("planner") and " other " in ln)
    assert row.split()[4] == "2"  # its two replies still count
    assert any(ln.startswith("planner") and "opus-5-5" in ln for ln in out.splitlines())
    out = run(capsys, "ledger", *w)
    assert PLANT not in out and "replies=     2" in next(ln for ln in out.splitlines() if ln.startswith("other "))
    assert PLANT not in run(capsys, "startup", *w, "--sessions")
    f = str(s / "C--x" / "ssss0001-0000.jsonl")
    assert "model other" in run(capsys, "turns", f)


def test_compact_trigger_and_keys_print_only_when_known(tmp_path, capsys):
    s = tmp_path / "store"
    cp = compact(T(22, "11:00:00"))
    cp["compactMetadata"].update(trigger=PLANT, **{PLANT: 1})
    cp2 = {**compact(T(22, "12:00:00")), "uuid": "c2"}
    cp2["compactMetadata"]["trigger"] = PLANT
    write(s / SLUG_A / "tttt0001-0000.jsonl", [
        title("the planner"), reply("c1", T(22)), cp, reply("c2", T(22, "11:00:02")),
        cp2, reply("c3", T(22, "12:00:02"))])
    out = run(capsys, "compacts", "--store", str(s), "--from", "2026-11-22", "--to", "2026-11-22")
    assert PLANT not in out
    assert "triggers: {'other': 2}" in out
    assert "compactMetadata keys seen: durationMs, other, postTokens, preTokens, trigger" in out
    out = run(capsys, "trial", "--store", str(s), "tttt0001-0000")
    assert PLANT not in out and "trigger=other pre=150000 post=20000 durationMs=5" in out


def test_context_prints_only_known_shape_keys_with_a_count_for_the_rest(tmp_path, capsys):
    p = write(tmp_path / "s.jsonl", [{"type": "api-request-shape", "shape": json.dumps(
        {"model": "x", "tools": [], PLANT: 1, PLANT + "2": 2})}])
    out = run(capsys, "context", str(p))
    assert PLANT not in out and "top keys: model, other=2, tools" in out


def test_reads_and_replies_print_only_known_tool_stop_and_record_names(tmp_path, capsys):
    p = write(tmp_path / "s.jsonl", [
        user(PROMPT, T(20)),
        reply("a", T(20), i=0, cr=1000, stop="tool_use",
              calls=[("u1", PLANT, {"file_path": PATH}), ("u2", "Read", {"file_path": PATH})]),
        result("u1", "x" * 400, T(20)),
        result("u2", "x" * 400, T(20)),
        {"type": PLANT, "timestamp": T(20)},
        reply("b", T(20), i=0, cr=1200, stop=PLANT),
    ])
    out = run(capsys, "reads", str(p))
    assert PLANT not in out
    rows = [ln.split() for ln in out.splitlines() if ln.strip().startswith("1 ")]
    assert [r[1] for r in rows] == ["other", "Read"]
    out = run(capsys, "replies", str(p))
    assert PLANT not in out
    assert "stop=other" in out and "stop=tool_use" in out and "-- record other" in out


def test_shapes_skips_a_sidechain_reply_before_the_landing_count(tmp_path, capsys):
    # F3 of #308: a sidechain reply that ends its turn, between a main reply that called a
    # tool and a queued peer message, does not move where that message lands
    s = tmp_path / "store"
    write(s / "C--x" / "uuuu0001-0000.jsonl", [
        title("a manager"), user(PROMPT, T(21, "08:00:00")),
        reply("r1", T(21, "08:00:01"), stop="tool_use", calls=[("u1", "Bash", {"command": "ls"})]),
        reply("side", T(21, "08:00:02"), stop="end_turn", side=True),
        queued(T(21, "08:00:03"), "<cross-session-message from=x>" + PROMPT),
        result("u1", RESULT, T(21, "08:00:04")),
        reply("r2", T(21, "08:00:05"), stop="end_turn"),
    ])
    out = run(capsys, "shapes", "--store", str(s), "--from", "2026-11-21", "--to", "2026-11-21")
    assert any(ln.split()[:1] == ["1"] and ln.endswith("tagged queued command | inside a running turn")
               for ln in out.splitlines())
    assert "after a reply that ended its turn" not in out


def test_a_queued_message_and_its_meta_copy_match_across_whitespace(tmp_path):
    # F4 of the re-check on PR #308: other line endings and spacing, the same message
    meta = {**user("Another Claude session sent a message:\r\n<cross-session-message  from=x>\r\nA  B\r\n",
                   T(21), meta=True), "origin": {"kind": "peer"}, "turnOrigin": "peer"}
    s = stop_session(tmp_path, [
        user(PROMPT, T(21)), reply("a", T(21), stop="tool_use"),
        queued(T(21), "<cross-session-message from=x>\nA B"),
        meta,
        reply("b", T(21)),
    ])
    assert s.openers == ["typed"]
    assert s.replies[1].after_peer


def test_the_code_holds_no_machine_path_and_reads_no_environment():
    src = SCRIPT.read_text(encoding="utf-8")
    for word in ("C:\\", "C:/", "/Users/", "/home/", "benha", "os.environ", "getenv", "shell=True"):
        assert word not in src
