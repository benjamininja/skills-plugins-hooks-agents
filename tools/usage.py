"""Usage figures from a local Claude Code transcript store. Counts only (#263).

Usage:
  python tools/usage.py baseline --store DIR --from YYYY-MM-DD --to YYYY-MM-DD [--role ...]
  python tools/usage.py ledger   --store DIR --from ... --to ... [--role ...] [--top N]
  python tools/usage.py startup  --store DIR --from ... --to ... [--role ...] [--sessions]
  python tools/usage.py tags     --store DIR --from ... --to ... [--role ...] [--tag ...]
                                 [--only ROLE] [--idle-gap SECONDS]
  python tools/usage.py compacts --store DIR --from ... --to ... [--role ...]
  python tools/usage.py trial    --store DIR SESSION_ID [--role ...]
  python tools/usage.py context  TRANSCRIPT.jsonl
  python tools/usage.py reads    TRANSCRIPT.jsonl
  python tools/usage.py replies  TRANSCRIPT.jsonl [--max N]
  python tools/usage.py turns    TRANSCRIPT.jsonl

The store is a folder of project folders, each holding one `<session id>.jsonl`
per session and, one level deeper (`<session id>/...`), that session's subagent
files. The record names read here (assistant, user, system/compact_boundary,
attachment, api-request-shape, custom-title, agent-name) are what the store held
in November 2026, not a documented format: a kind that is missing is reported
as not found, never a crash.

The rules of the count, the same in every subcommand:

- Unit: input-equivalent tokens = input + 1.25 x cache write + 0.1 x cache read
  + 5 x output. Model prices are not applied.
- A reply is counted once, by its message id, across the whole store: a resumed
  or forked session copies its history into a new file. Folders and files are
  read in sorted order, so a shared reply always counts in the same file. A
  compact record is counted once the same way, by its uuid.
- One reply may be stored as several records with the same id, one per content
  block. Its usage comes from the first record; its stop reason from the last
  record that holds one; its tool calls from all of them.
- Replies whose model is `<synthetic>` are left out. Sidechain records are left
  out of a session's own figures; subagent files are read and summed apart.
- Window: a session belongs to the window when the date (UTC) of its first
  counted reply falls between --from and --to, both inclusive.
- Role: the first --role rule that matches the session decides it, else
  `other`. A rule is ROLE=KIND:REGEX, KIND one of title, agent, slug; the match
  is a case-insensitive search. Given rules replace the defaults.

Method point 2, the start-up turn: from the first reply up to and including the
first reply whose stop reason ends the turn (any stop reason but `tool_use`).
A peer message, an app event or a system reminder arrives as a user record and
is not a typed prompt, so cutting at the second typed prompt runs on through
them. A session with no ending reply counts whole and is reported.

Method point 1, per-read sizes (`reads`): only the turn's context growth is
measured. Each tool result is sized in characters and turned into tokens at the
turn's mean ratio, result characters over that growth, so each per-read figure
is an estimate at that mean ratio, not a measurement. The figures add up to
the whole growth, which also holds the replies' own output and text the app
injects, so taken together they are an upper bound on what the reads cost. One
result alone is not bounded: a result denser than the mean (minified JSON,
non-ASCII text) is shown below its real size, and a result cut or stored
outside the context adds characters but no growth, which lowers the rest.

Nothing printed is transcript text: no title, no path, no project folder name,
no prompt or result. A session is shown by an index and an 8-character id
prefix; a read by its tool's name and its file's extension.
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import statistics
import sys
from dataclasses import dataclass, field
from datetime import datetime

W_IN, W_CW, W_CR, W_OUT = 1.0, 1.25, 0.1, 5.0
SYNTHETIC = "<synthetic>"
TOOL_USE = "tool_use"
PEER_MARK = "<cross-session-message"
APP_MARKS = ("<task-notification", "<side-sessions-event")
REMINDER_MARK = "<system-reminder"
REMINDER_END = "</system-reminder>"
LEAD = 120  # the longest lead line allowed before a peer or app tag
QUIET_RECORDS = ("assistant", "user", "file-history-snapshot", "attachment", "progress")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
SID_RE = re.compile(r"[A-Za-z0-9-]{8,64}")
EXT_RE = re.compile(r"\.[A-Za-z0-9]{1,8}")
DEFAULT_ROLES = [
    "planner=title:planner",
    "manager=title:manager",
    "assistant=title:assistant",
    "consultant=title:consultant",
    "consultant=title:supabase",
    r"builder=slug:--claude-worktrees-[bt]\d",
]
# Matched against "<tool name> <command or subagent type>" of each tool call, in order.
DEFAULT_TAGS = [
    r"review=^(Agent|Task) .*review",
    r"reproof=reproof\.py|pre_commit run|gh pr checks",
    r"merge=gh pr merge",
    r"closeout=closeout\.py|pull --ff-only|claude rm",
    r"dispatch=dispatch\.ps1|resume_plain\.ps1",
    r"message out=^SendMessage",
]
START_UP, MESSAGE_IN, UNTAGGED = "start-up", "message in", "untagged"


def eq(i: float, cw: float, cr: float, out: float) -> float:
    return i * W_IN + cw * W_CW + cr * W_CR + out * W_OUT


def num(u: dict, key: str) -> int:
    v = u.get(key)
    return v if isinstance(v, int) else 0


@dataclass
class Call:
    name: str
    detail: str  # command or subagent type: matched, never printed
    ext: str  # a file's extension, or ""
    use_id: str


@dataclass
class Reply:
    mid: str
    ts: str
    model: str
    inp: int
    cw: int
    cr: int
    out: int
    turn: int
    stop: str | None = None
    calls: list[Call] = field(default_factory=list)
    counted: bool = True

    @property
    def ctx(self) -> int:
        return self.inp + self.cw + self.cr

    @property
    def eq(self) -> float:
        return eq(self.inp, self.cw, self.cr, self.out)


@dataclass
class Compact:
    ts: str
    trigger: str | None
    pre: int | None
    post: int | None
    ms: int | None
    at: int  # replies before it
    keys: list[str]
    key: str = ""  # the record's uuid, else its time, trigger and size: a copied compact keeps it
    summary_chars: int = 0
    counted: bool = True


@dataclass
class Session:
    path: str
    slug: str = ""
    sid: str = ""
    title: str | None = None
    agent: str | None = None
    replies: list[Reply] = field(default_factory=list)
    openers: list[str] = field(default_factory=list)  # kind of each user record that opens a turn
    events: list[tuple] = field(default_factory=list)
    compacts: list[Compact] = field(default_factory=list)
    attach: collections.Counter = field(default_factory=collections.Counter)
    shape: object = None
    kinds: collections.Counter = field(default_factory=collections.Counter)
    bad_lines: int = 0
    subagents: list["Session"] = field(default_factory=list)

    def counted(self) -> list[Reply]:
        return [r for r in self.replies if r.counted]

    def first_day(self) -> str | None:
        c = self.counted()
        return c[0].ts[:10] if c else None

    def main_model(self) -> str:
        n = collections.Counter(r.model for r in self.counted())
        return n.most_common(1)[0][0] if n else "?"

    def opener_of(self, r: Reply) -> str | None:
        return self.openers[r.turn - 1] if r.turn > 0 else None


def text_of(o: dict) -> str | None:
    """The text of a user record that is not a tool result, else None."""
    c = (o.get("message") or {}).get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        if any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
            return None
        parts = [x.get("text") or "" for x in c if isinstance(x, dict) and x.get("type") == "text"]
        return "".join(parts) if parts else None
    return None


def opener_kind(text: str) -> str:
    """What opened a turn, judged at the start of the text, never by a mark quoted later.

    Leading system-reminder blocks are set aside first: with nothing after them the
    opener is a system reminder, else the rest decides. A peer message or an app event
    is one whose tag opens the rest, after at most one short lead line with no markup
    (the line the app may put before a peer message). Anything else is typed."""
    t = text.lstrip()
    while t.startswith(REMINDER_MARK):
        end = t.find(REMINDER_END)
        if end < 0:
            return "system reminder"
        t = t[end + len(REMINDER_END):].lstrip()
        if not t:
            return "system reminder"
    for kind, marks in (("peer message", (PEER_MARK,)), ("app event", APP_MARKS)):
        for m in marks:
            pos = t.find(m)
            lead = t[:pos]
            one_line = lead == "" or (lead.rstrip(" \t").endswith("\n") and lead.count("\n") == 1)
            if 0 <= pos <= LEAD and one_line and "<" not in lead:
                return kind
    return "typed"


def size(c) -> int:
    if isinstance(c, str):
        return len(c)
    if isinstance(c, list):
        return sum(size(x.get("text") or x.get("content") or "") if isinstance(x, dict) else len(str(x))
                   for x in c)
    return 0 if c is None else len(str(c))


def file_ext(inp: dict) -> str:
    p = inp.get("file_path") or inp.get("notebook_path")
    if not isinstance(p, str):
        return ""
    ext = os.path.splitext(p)[1]
    return ext.lower() if EXT_RE.fullmatch(ext) else ""


def note_attachment(s: Session, a: dict) -> None:
    k = a.get("type")
    if k == "skill_listing":
        s.attach["skill listing"] = max(s.attach["skill listing"], len(str(a.get("content", ""))))
    elif k == "prompt_snapshot":
        s.attach["system prompt"] = max(s.attach["system prompt"], len(str(a.get("systemPrompt", ""))))
    elif k == "agent_listing_delta":
        s.attach["agent type listing"] += len(json.dumps(a.get("addedLines")))
    elif k == "deferred_tools_delta":
        s.attach["deferred tool names"] += len(json.dumps(a.get("addedLines")))
    elif k == "mcp_instructions_delta":
        s.attach["MCP server instructions"] += len(json.dumps(a.get("addedBlocks")))
    elif k == "nested_memory":
        s.attach["nested memory files"] += len(str(a.get("content", "")))
    elif k == "instructions":
        s.attach["instruction files"] += len(json.dumps(a.get("files")))
    elif k == "hook_success":
        s.attach["hook output"] += len(str(a.get("content", "")))


def read_session(path: str, sidechain: bool = False) -> Session:
    """One transcript file. Replies are deduplicated within the file only."""
    s = Session(path)
    by_id: dict[str, Reply | None] = {}
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                o = json.loads(line)
            except ValueError:
                s.bad_lines += 1
                continue
            if not isinstance(o, dict):
                s.bad_lines += 1
                continue
            t = o.get("type")
            s.kinds[t] += 1
            if t in ("custom-title", "agent-name"):
                for k in ("customTitle", "title", "agentName"):
                    if isinstance(o.get(k), str):
                        s.title = o[k]
            if isinstance(o.get("agentSetting"), str):
                s.agent = o["agentSetting"]
            if o.get("isSidechain") and not sidechain:
                continue
            msg = o.get("message") if isinstance(o.get("message"), dict) else {}
            ts = o.get("timestamp") if isinstance(o.get("timestamp"), str) else ""
            if t == "assistant":
                read_reply(s, by_id, o, msg, ts)
            elif t == "user":
                read_user(s, o, msg, ts)
            elif t == "system" and o.get("subtype") == "compact_boundary":
                md = o.get("compactMetadata") if isinstance(o.get("compactMetadata"), dict) else {}
                pre = md.get("preTokens") or md.get("pre_tokens")
                key = o.get("uuid") or f"{ts}|{md.get('trigger')}|{pre}"
                s.compacts.append(Compact(ts, md.get("trigger"), pre, md.get("postTokens"),
                                          md.get("durationMs"), len(s.replies), sorted(md), str(key)))
                s.events.append(("record", "compact_boundary", ts))
            elif t == "attachment":
                if isinstance(o.get("attachment"), dict):
                    note_attachment(s, o["attachment"])
            elif t == "api-request-shape":
                if s.shape is None:
                    s.shape = o.get("shape")
            elif t not in QUIET_RECORDS:
                s.events.append(("record", str(t), ts))
    return s


def read_reply(s: Session, by_id: dict, o: dict, msg: dict, ts: str) -> None:
    mid = msg.get("id") or o.get("uuid")
    if not mid:
        return
    if mid not in by_id:
        u = msg.get("usage")
        if not isinstance(u, dict):
            return
        model = msg.get("model") or "?"
        if model == SYNTHETIC:
            by_id[mid] = None
            return
        r = Reply(mid, ts, model, num(u, "input_tokens"), num(u, "cache_creation_input_tokens"),
                  num(u, "cache_read_input_tokens"), num(u, "output_tokens"), len(s.openers))
        by_id[mid] = r
        s.replies.append(r)
        s.events.append(("reply", r))
    r = by_id[mid]
    if r is None:
        return
    if msg.get("stop_reason"):
        r.stop = msg["stop_reason"]
    c = msg.get("content")
    for x in c if isinstance(c, list) else []:
        if isinstance(x, dict) and x.get("type") == TOOL_USE:
            inp = x.get("input") if isinstance(x.get("input"), dict) else {}
            detail = inp.get("command") or inp.get("subagent_type") or ""
            r.calls.append(Call(str(x.get("name") or "?"), str(detail), file_ext(inp), str(x.get("id") or "")))


def read_user(s: Session, o: dict, msg: dict, ts: str) -> None:
    c = msg.get("content")
    meta = bool(o.get("isMeta"))
    if o.get("isCompactSummary"):
        if s.compacts:
            s.compacts[-1].summary_chars = len(c if isinstance(c, str) else json.dumps(c))
        return
    if isinstance(c, list):
        for x in c:
            if isinstance(x, dict) and x.get("type") == "tool_result":
                s.events.append(("result", str(x.get("tool_use_id") or ""), size(x.get("content"))))
            elif isinstance(x, dict) and x.get("type") == "text" and meta:
                s.events.append(("injected", len(x.get("text") or "")))
    elif isinstance(c, str) and meta:
        s.events.append(("injected", len(c)))
    text = text_of(o)
    if text is None:
        return
    kind = opener_kind(text)
    s.events.append(("user", kind, meta, len(text), ts))
    if not meta:
        s.openers.append(kind)


def scan(store: str) -> list[Session]:
    """Every session file of the store, with one seen-set of message ids for all of
    them, and one of compact records: a copied history copies its compacts too."""
    seen: set[str] = set()
    seen_compacts: set[str] = set()
    out = []
    for slug in sorted(os.listdir(store)):
        folder = os.path.join(store, slug)
        if not os.path.isdir(folder):
            continue
        for f in sorted(os.listdir(folder)):
            path = os.path.join(folder, f)
            if not f.endswith(".jsonl") or not os.path.isfile(path):
                continue
            s = read_session(path)
            s.slug, s.sid = slug, f[: -len(".jsonl")]
            mark(s.replies, seen)
            for cp in s.compacts:
                cp.counted = cp.key not in seen_compacts
                seen_compacts.add(cp.key)
            sub_dir = os.path.join(folder, s.sid)
            for p in sorted(glob.glob(os.path.join(glob.escape(sub_dir), "**", "*.jsonl"), recursive=True)):
                sub = read_session(p, sidechain=True)
                mark(sub.replies, seen)
                s.subagents.append(sub)
            out.append(s)
    return out


def mark(replies: list[Reply], seen: set[str]) -> None:
    for r in replies:
        r.counted = r.mid not in seen
        seen.add(r.mid)


# ---- rules ----------------------------------------------------------------


def role_rule(text: str) -> tuple[str, str, re.Pattern]:
    role, sep, rest = text.partition("=")
    kind, sep2, rx = rest.partition(":")
    if not sep or not sep2 or not role.strip() or kind not in ("title", "agent", "slug") or not rx:
        raise argparse.ArgumentTypeError("expected ROLE=KIND:REGEX with KIND title, agent or slug")
    try:
        return role.strip(), kind, re.compile(rx, re.I)
    except re.error as exc:
        raise argparse.ArgumentTypeError(f"bad regex: {exc}") from None


def tag_rule(text: str) -> tuple[str, re.Pattern]:
    name, sep, rx = text.partition("=")
    if not sep or not name.strip() or not rx:
        raise argparse.ArgumentTypeError("expected NAME=REGEX")
    if name.strip() in (START_UP, MESSAGE_IN, UNTAGGED):
        raise argparse.ArgumentTypeError(f"{name.strip()} is a built-in tag")
    try:
        return name.strip(), re.compile(rx)
    except re.error as exc:
        raise argparse.ArgumentTypeError(f"bad regex: {exc}") from None


def role_of(s: Session, rules) -> str:
    for role, kind, rx in rules:
        value = {"title": s.title, "agent": s.agent, "slug": s.slug}[kind]
        if value and rx.search(value):
            return role
    return "other"


def startup_cut(replies: list[Reply]) -> tuple[list[Reply], bool]:
    """Method point 2: up to and including the first reply whose stop reason ends the turn."""
    for k, r in enumerate(replies):
        if r.stop and r.stop != TOOL_USE:
            return replies[: k + 1], True
    return list(replies), False


def tag_of(r: Reply, rules) -> str | None:
    for name, rx in rules:
        if any(rx.search(f"{c.name} {c.detail}") for c in r.calls):
            return name
    return None


def tag_replies(s: Session, replies: list[Reply], rules) -> list[str]:
    """One tag per reply: start-up, a rule's tag, the tag carried from the reply
    before it in the same turn, message in (a turn a peer message opened), or untagged."""
    start, _ = startup_cut(replies)
    tags: list[str] = []
    for k, r in enumerate(replies):
        if k < len(start):
            tags.append(START_UP)
            continue
        tag = tag_of(r, rules)
        if tag is None and k > len(start) and replies[k - 1].turn == r.turn and tags[-1] != UNTAGGED:
            tag = tags[-1]
        if tag is None and s.opener_of(r) == "peer message":
            tag = MESSAGE_IN
        tags.append(tag or UNTAGGED)
    return tags


def seconds(ts: str) -> float | None:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


# ---- helpers ----------------------------------------------------------------


def short_model(m: str) -> str:
    return m[len("claude-"):] if m.startswith("claude-") else m


def med(xs) -> float:
    return statistics.median(xs) if xs else 0


def pct(a: float, b: float) -> str:
    return f"{a / b:.0%}" if b else "-"


def in_window(store: str, lo: str, hi: str, rules) -> list[tuple[int, Session, str]]:
    rows = []
    for s in scan(store):
        day = s.first_day()
        if day and lo <= day <= hi:
            rows.append((len(rows) + 1, s, role_of(s, rules)))
    return rows


def label(idx: int, s: Session) -> str:
    return f"#{idx:<3} {s.sid[:8]}"


# ---- subcommands -------------------------------------------------------------


def cmd_baseline(a) -> None:
    agg: dict = collections.defaultdict(collections.Counter)
    days: dict = collections.defaultdict(set)
    rows = in_window(a.store, a.lo, a.hi, a.roles)
    for _, s, role in rows:
        for r in s.counted():
            k = (role, short_model(r.model))
            agg[k]["eq"] += r.eq
            agg[k]["cr"] += r.cr * W_CR
            agg[k]["n"] += 1
        k = (role, short_model(s.main_model()))
        agg[k]["sessions"] += 1
        agg[k]["compacts"] += sum(cp.counted for cp in s.compacts)
        days[k] |= {r.ts[:10] for r in s.counted()}
    print(f"window: sessions whose first reply is {a.lo}..{a.hi}; session files counted: {len(rows)}; "
          "subagent usage not included")
    print("role        model             sessions compacts replies activeDays replies/day  inEq(M) "
          "cacheReadShare inEq/reply(k)")
    tot = 0.0
    for (role, model), c in sorted(agg.items()):
        nd = len(days[(role, model)]) or 1
        tot += c["eq"]
        print(f"{role:11} {model:17} {c['sessions']:8} {c['compacts']:8} {c['n']:7} {nd:10} "
              f"{c['n'] / nd:11.0f} {c['eq'] / 1e6:8.1f} {pct(c['cr'], c['eq']):>14} "
              f"{(c['eq'] / c['n'] / 1000 if c['n'] else 0):13.0f}")
    print(f"total inEq: {tot / 1e6:.1f}M")


def cmd_ledger(a) -> None:
    rows = in_window(a.store, a.lo, a.hi, a.roles)
    print(f"window: sessions whose first reply is {a.lo}..{a.hi}; sessions: {len(rows)}")
    by_model: dict = collections.defaultdict(collections.Counter)
    by_rm: dict = collections.defaultdict(collections.Counter)
    sess_rm: dict = collections.defaultdict(set)
    per = []
    by_day: collections.Counter = collections.Counter()
    for idx, s, role in rows:
        sub = [r for x in s.subagents for r in x.counted()]
        c = s.counted()
        total = sum(r.eq for r in c)
        per.append((total, idx, s, role, sum(r.eq for r in sub), max((r.ctx for r in c), default=0)))
        by_day[c[-1].ts[:10]] += total
        for r in c:
            for d in (by_model[short_model(r.model)], by_rm[(role, short_model(r.model))]):
                d["n"] += 1
                d["in"] += r.inp
                d["cw"] += r.cw
                d["cr"] += r.cr
                d["out"] += r.out
                d["eq"] += r.eq
            sess_rm[(role, short_model(r.model))].add(idx)
        for r in sub:
            by_rm[(role, "subagents")]["n"] += 1
            by_rm[(role, "subagents")]["eq"] += r.eq
            sess_rm[(role, "subagents")].add(idx)
    M = 1e6
    print("\n== by model (millions; main sessions only) ==")
    for m, d in sorted(by_model.items(), key=lambda x: -x[1]["eq"]):
        print(f"{m:24} replies={d['n']:6} in={d['in'] / M:7.2f} cacheWrite={d['cw'] / M:8.2f} "
              f"cacheRead={d['cr'] / M:9.2f} out={d['out'] / M:6.2f} inEq={d['eq'] / M:8.1f}")
    print("\n== by role and model (inEq millions; share by part; subagents summed apart) ==")
    for (role, m), d in sorted(by_rm.items(), key=lambda x: -x[1]["eq"]):
        e = d["eq"]
        parts = "" if m == "subagents" else (
            f" cacheRead={pct(d['cr'] * W_CR, e):>4} cacheWrite={pct(d['cw'] * W_CW, e):>4} "
            f"out={pct(d['out'] * W_OUT, e):>4} in={pct(d['in'] * W_IN, e):>4}")
        print(f"{role:12} {m:20} sessions={len(sess_rm[(role, m)]):3} replies={d['n']:6} "
              f"inEq={e / M:8.1f}{parts} perReply={e / max(d['n'], 1) / 1000:6.1f}k")
    print(f"\n== top {a.top} sessions by inEq ==")
    for total, idx, s, role, sub, maxctx in sorted(per, key=lambda x: -x[0])[: a.top]:
        c = s.counted()
        print(f"{label(idx, s)} {role:12} {short_model(s.main_model())[:18]:18} replies={len(c):5} "
              f"inEq={total / M:7.1f} subagentEq={sub / M:5.1f} maxCtx={maxctx / 1000:5.0f}k "
              f"{c[0].ts[5:16]} -> {c[-1].ts[5:16]}")
    b = sorted(x[0] / M for x in per if x[3] == "builder")
    if b:
        print("\n== builders: inEq per session (millions) ==")
        print(f"n={len(b)} min={b[0]:.1f} median={med(b):.1f} p90={b[int(len(b) * 0.9)]:.1f} "
              f"max={b[-1]:.1f} total={sum(b):.1f}")
    print("\n== by day of the session's last reply (UTC), inEq millions ==")
    for d in sorted(by_day):
        print(f"{d} {by_day[d] / M:8.1f}")


def cmd_startup(a) -> None:
    rows = in_window(a.store, a.lo, a.hi, a.roles)
    found: dict = collections.defaultdict(list)
    for idx, s, role in rows:
        c = s.counted()
        start, ended = startup_cut(c)
        found[role].append({
            "idx": idx, "s": s, "first": c[0].ctx, "end": start[-1].ctx + start[-1].out,
            "n": len(start), "eq": sum(r.eq for r in start), "tot": sum(r.eq for r in c),
            "openers": len(s.openers), "ended": ended, "day": c[0].ts[:10],
        })
    print(f"window: sessions whose first reply is {a.lo}..{a.hi}")
    print("start-up turn: first reply up to and including the first reply whose stop reason "
          "ends the turn (not tool_use)")
    print("role         sessions ctxAtFirstReply ctxAfterStartUp startUpReplies startUp(k inEq) "
          "shareOfSession openers/session noEndingReply  (medians)")
    for role in sorted(found):
        x = found[role]
        print(f"{role:12} {len(x):8} {med([y['first'] for y in x]) / 1000:14.0f}k "
              f"{med([y['end'] for y in x]) / 1000:14.0f}k {med([y['n'] for y in x]):14.0f} "
              f"{med([y['eq'] for y in x]) / 1000:15.0f} "
              f"{med([y['eq'] / y['tot'] for y in x if y['tot']]):14.0%} "
              f"{med([y['openers'] for y in x]):15.0f} {sum(not y['ended'] for y in x):13}")
    if a.sessions:
        for role in sorted(found):
            print(f"\n-- {role} sessions --")
            for y in sorted(found[role], key=lambda y: (y["day"], y["idx"])):
                print(f"{y['day']} {label(y['idx'], y['s'])} {short_model(y['s'].main_model())[:12]:12} "
                      f"first={y['first'] / 1000:4.0f}k afterStartUp={y['end'] / 1000:4.0f}k "
                      f"startUpReplies={y['n']:3} startUp={y['eq'] / 1000:5.0f}k "
                      f"session={y['tot'] / 1e6:5.1f}M replies={len(y['s'].counted()):4} "
                      f"ended={'yes' if y['ended'] else 'no'}")


def cmd_tags(a) -> None:
    rows = in_window(a.store, a.lo, a.hi, a.roles)
    names = [START_UP] + [n for n, _ in a.tags] + [MESSAGE_IN, UNTAGGED]
    acc: dict = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for _, s, role in rows:
        if a.only and role not in a.only:
            continue
        c = s.counted()
        x = acc[role]
        x["all"]["sessions"] += 1
        prev_t = None
        for k, (r, tag) in enumerate(zip(c, tag_replies(s, c, a.tags))):
            x[tag]["n"] += 1
            x[tag]["eq"] += r.eq
            x["all"]["n"] += 1
            x["all"]["eq"] += r.eq
            t = seconds(r.ts)
            if t is not None and prev_t is not None and t - prev_t > a.idle_gap:
                x["idle"]["n"] += 1
                x["idle"]["eq"] += r.eq
                x["idle"]["cw"] += r.cw * W_CW
            prev_t = t if t is not None else prev_t
            ncalls = len(r.calls)
            x["calls"][min(ncalls, 2)] += 1
            if k and ncalls == 1 and len(c[k - 1].calls) == 1 and c[k - 1].turn == r.turn:
                x["follow"]["n"] += 1
                x["follow"]["cr"] += r.cr * W_CR
        for sub in s.subagents:
            x["sub"]["files"] += 1
            for r in sub.counted():
                x["sub"]["n"] += 1
                x["sub"]["eq"] += r.eq
    M = 1e6
    print(f"window: sessions whose first reply is {a.lo}..{a.hi}; idle gap {a.idle_gap:.0f}s")
    print("each reply has one tag: start-up, the first rule its own tool calls match, the tag of the "
          "reply before it in the same turn, message in, or untagged")
    for role in sorted(acc):
        x = acc[role]
        e = x["all"]["eq"]
        print(f"\n== {role}: sessions={x['all']['sessions']} replies={x['all']['n']} inEq={e / M:.2f}M ==")
        print("tag            replies  inEq(M)  share")
        for n in names:
            print(f"{n:14} {x[n]['n']:7} {x[n]['eq'] / M:8.2f} {pct(x[n]['eq'], e):>6}")
        print(f"untagged share of inEq: {pct(x[UNTAGGED]['eq'], e)}")
        print(f"idle re-reads (reply after a gap > {a.idle_gap:.0f}s): replies={x['idle']['n']} "
              f"inEq={x['idle']['eq'] / M:.2f}M share={pct(x['idle']['eq'], e)} "
              f"of which cacheWrite={x['idle']['cw'] / M:.2f}M")
        print(f"tool calls per reply: none={x['calls'][0]} one={x['calls'][1]} more={x['calls'][2]}; "
              f"one-call replies right after a one-call reply in the same turn={x['follow']['n']}, "
              f"their cacheRead inEq={x['follow']['cr'] / M:.2f}M (upper bound of what batching saves)")
        print(f"subagents, apart: files={x['sub']['files']} replies={x['sub']['n']} "
              f"inEq={x['sub']['eq'] / M:.2f}M")


def cmd_compacts(a) -> None:
    rows = []
    keys: set[str] = set()
    for s in scan(a.store):
        role = role_of(s, a.roles)
        reps = s.replies
        for cp in s.compacts:
            if not cp.counted or not (a.lo <= cp.ts[:10] <= a.hi):
                continue
            keys |= set(cp.keys)
            before = [r for r in reps[: cp.at]]
            after = reps[cp.at:]
            nxt = [x.at for x in s.compacts if x.at > cp.at]
            if nxt:
                after = reps[cp.at: nxt[0]]
            rows.append({"role": role, "trigger": cp.trigger, "day": cp.ts[:10],
                         "pre": cp.pre or (before[-1].ctx if before else 0),
                         "post": after[0].ctx if after else None, "sum": cp.summary_chars,
                         "after": len(after)})
    print(f"compacts dated {a.lo}..{a.hi}: {len(rows)}")
    if not rows:
        print("compact records: none found")
        return
    print("compactMetadata keys seen:", ", ".join(sorted(keys)) or "none")
    print("triggers:", dict(collections.Counter(str(r["trigger"]) for r in rows)))
    print("role         n  preCtx(median) postCtx(median) summaryTok(median) repliesAfter(median) preRange")
    for role in sorted({r["role"] for r in rows}):
        x = [r for r in rows if r["role"] == role and r["post"] is not None]
        if not x:
            continue
        pre = [r["pre"] for r in x]
        print(f"{role:10} {len(x):3} {med(pre) / 1000:14.0f}k {med([r['post'] for r in x]) / 1000:14.0f}k "
              f"{med([r['sum'] for r in x]) / 4 / 1000:17.1f}k {med([r['after'] for r in x]):20.0f} "
              f"{min(pre) / 1000:.0f}k-{max(pre) / 1000:.0f}k")
    print("by day (count):", dict(sorted(collections.Counter(r["day"] for r in rows).items())))


def cmd_trial(a) -> None:
    paths = sorted(glob.glob(os.path.join(glob.escape(a.store), "*", a.sid + ".jsonl")))
    if not paths:
        print("session not found")
        return
    for p in paths:
        s = read_session(p)
        s.slug = os.path.basename(os.path.dirname(p))
        print(f"role: {role_of(s, a.roles)}")
        if not s.compacts:
            print("last compact: none found")
            continue
        cp = s.compacts[-1]
        before = s.replies[: cp.at]
        after = s.replies[cp.at:]
        print(f"last compact: day={cp.ts[:10]} trigger={cp.trigger} pre={cp.pre} post={cp.post} "
              f"durationMs={cp.ms} lastCtxBefore={before[-1].ctx if before else 0} "
              f"summaryChars={cp.summary_chars}")
        print(f"replies after: {len(after)}  cost after (inEq): {round(sum(r.eq for r in after))}")
        for r in after[:12]:
            print(f"  {r.ts[11:19]} ctx={r.ctx} cacheWrite={r.cw} cacheRead={r.cr} out={r.out} eq={r.eq:.0f}")


def cmd_context(a) -> None:
    s = read_session(a.file)
    print("=== fixed context from attachment records (chars; about 4 chars per token) ===")
    if not s.attach:
        print("attachment records: none found")
    for k, v in sorted(s.attach.items(), key=lambda x: -x[1]):
        print(f"{v:9}  ~{v // 4:7} tok  {k}")
    shape = s.shape
    if isinstance(shape, str):
        try:
            shape = json.loads(shape)
        except ValueError:
            pass
    print("\n=== request shape ===")
    if not isinstance(shape, dict):
        print("api-request-shape record: none found")
        return
    print("top keys:", ", ".join(sorted(str(k) for k in shape)[:20]))
    tools = shape.get("tools")
    if not isinstance(tools, list):
        print("tools: none found")
        return
    grp: collections.Counter = collections.Counter()
    n: collections.Counter = collections.Counter()
    servers = set()
    for t in tools:
        name = t.get("name", "?") if isinstance(t, dict) else str(t)
        sz = len(json.dumps(t))
        if str(name).startswith("mcp__"):
            g = "mcp"
            servers.add(str(name).split("__")[1] if str(name).count("__") >= 2 else "?")
        else:
            g = "built-in"
        grp[g] += sz
        n[g] += 1
    print(f"tools in request: {len(tools)}; mcp servers: {len(servers)}")
    for g, v in grp.most_common():
        print(f"{v:9}  {n[g]:4} tools  {g}")


def cmd_reads(a) -> None:
    s = read_session(a.file)
    start, ended = startup_cut(s.replies)
    if not start:
        print("no replies")
        return
    ids = {r.mid for r in start}
    uses = {}
    for k, r in enumerate(start, 1):
        for c in r.calls:
            uses[c.use_id] = (k, c)
    rows = []
    n = 0
    for ev in s.events:
        if ev[0] == "reply":
            if ev[1].mid not in ids:
                break
            n += 1
        elif ev[0] == "result" and ev[1] in uses:
            k, c = uses[ev[1]]
            # an MCP tool's name carries its server's name, which is the owner's: shown as "mcp"
            rows.append((k, "mcp" if c.name.startswith("mcp__") else c.name, c.ext, ev[2]))
        elif ev[0] == "injected" and n:
            rows.append((n, "(injected text)", "", ev[1]))
    growth = start[-1].ctx - start[0].ctx
    chars = sum(r[3] for r in rows)
    cpt = chars / growth if growth > 0 else 4.0
    print("per-read tokens are ESTIMATES at the turn's mean chars/token (method point 1), not "
          "measurements: together they are an upper bound on the reads (the growth also holds the "
          "replies' own output and injected text); one dense result alone may be shown below its size")
    print(f"start-up turn: replies={len(start)} ended={'yes' if ended else 'no'} ctx {start[0].ctx} -> "
          f"{start[-1].ctx} growth={growth} resultChars={chars} chars/token~{cpt:.2f}")
    print("reply  tool                        ext      ~tokens(est at mean)  ~cost(k inEq: 1.25 write + 0.1 x later replies)")
    for k, name, ext, sz in rows:
        tok = sz / cpt if cpt else 0
        cost = tok * (W_CW + W_CR * max(len(start) - k, 0))
        print(f"{k:5}  {name[:26]:26}  {ext:8} {tok:20.0f}  {cost / 1000:8.1f}k")


def cmd_replies(a) -> None:
    s = read_session(a.file)
    n = 0
    cum = 0.0
    for ev in s.events:
        if ev[0] == "reply":
            r = ev[1]
            n += 1
            if n > a.max:
                break
            cum += r.eq
            print(f"reply {n:3} {r.ts[11:19]} ctxIn={r.ctx:7} out={r.out:5} ctxEnd={r.ctx + r.out:7} "
                  f"inEq={r.eq / 1000:6.1f}k cum={cum / 1000:7.1f}k calls={len(r.calls)} stop={r.stop}")
        elif ev[0] == "user":
            _, kind, meta, length, ts = ev
            print(f"   -- user ({kind}) meta={meta} len={length} {ts[11:19]}")
        elif ev[0] == "record":
            print(f"   -- record {ev[1]} {ev[2][11:19]}")
    start, ended = startup_cut(s.replies)
    print(f"start-up turn: replies 1..{len(start)} ({'ends at a reply that ends the turn' if ended else 'no ending reply'})")


def cmd_turns(a) -> None:
    s = read_session(a.file)
    turns: dict = collections.defaultdict(collections.Counter)
    for r in s.replies:
        T = turns[r.turn]
        T["n"] += 1
        T["eq"] += r.eq
        T["in"] += r.inp
        T["cw"] += r.cw
        T["cr"] += r.cr
        T["out"] += r.out
        if "first" not in T:
            T["first"] = r.ctx
        T["end"] = r.ctx + r.out
    print("model", short_model(s.main_model()))
    print("turn kind             replies ctxFirst   ctxEnd  inEq(k)    input cacheWrite  cacheRead  output")
    cum = 0.0
    for k in range(0, len(s.openers) + 1):
        if k == 0 and not turns.get(0):
            continue
        T = turns.get(k, collections.Counter())
        cum += T["eq"]
        kind = s.openers[k - 1] if k else "(before any)"
        print(f"{k:4} {kind:16} {T['n']:7} {T['first']:8} {T['end']:8} {T['eq'] / 1000:8.1f} {T['in']:8} "
              f"{T['cw']:10} {T['cr']:10} {T['out']:7}  cum={cum / 1000:.1f}k")
    start, ended = startup_cut(s.replies)
    print(f"start-up turn (method point 2): replies={len(start)} inEq={sum(r.eq for r in start) / 1000:.1f}k "
          f"ended={'yes' if ended else 'no'}")


# ---- arguments ----------------------------------------------------------------


def date_arg(text: str) -> str:
    if not DATE_RE.fullmatch(text):
        raise argparse.ArgumentTypeError("expected YYYY-MM-DD")
    return text


def sid_arg(text: str) -> str:
    if not SID_RE.fullmatch(text):
        raise argparse.ArgumentTypeError("expected a session id: letters, digits and -")
    return text


def dir_arg(text: str) -> str:
    if not os.path.isdir(text):
        raise argparse.ArgumentTypeError("not a folder")
    return text


def file_arg(text: str) -> str:
    if not os.path.isfile(text):
        raise argparse.ArgumentTypeError("not a file")
    return text


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="usage.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    def store(sp, window=True):
        sp.add_argument("--store", type=dir_arg, required=True)
        if window:
            sp.add_argument("--from", dest="lo", type=date_arg, required=True)
            sp.add_argument("--to", dest="hi", type=date_arg, required=True)
        sp.add_argument("--role", dest="roles", type=role_rule, action="append", default=None,
                        help="ROLE=KIND:REGEX, KIND title, agent or slug; repeatable; replaces the defaults")

    store(sub.add_parser("baseline"))
    sp = sub.add_parser("ledger")
    store(sp)
    sp.add_argument("--top", type=int, default=25)
    sp = sub.add_parser("startup")
    store(sp)
    sp.add_argument("--sessions", action="store_true")
    sp = sub.add_parser("tags")
    store(sp)
    sp.add_argument("--tag", dest="tags", type=tag_rule, action="append", default=None,
                    help="NAME=REGEX over '<tool name> <command or subagent type>'; replaces the defaults")
    sp.add_argument("--only", action="append", default=None)
    sp.add_argument("--idle-gap", type=float, default=3600.0)
    store(sub.add_parser("compacts"))
    sp = sub.add_parser("trial")
    store(sp, window=False)
    sp.add_argument("sid", type=sid_arg)
    for name in ("context", "reads", "turns"):
        sub.add_parser(name).add_argument("file", type=file_arg)
    sp = sub.add_parser("replies")
    sp.add_argument("file", type=file_arg)
    sp.add_argument("--max", type=int, default=20)
    a = p.parse_args(argv)
    if hasattr(a, "lo") and a.lo > a.hi:
        p.error("--from is after --to")
    if hasattr(a, "roles") and a.roles is None:
        a.roles = [role_rule(x) for x in DEFAULT_ROLES]
    if hasattr(a, "tags") and a.tags is None:
        a.tags = [tag_rule(x) for x in DEFAULT_TAGS]
    return a


COMMANDS = {
    "baseline": cmd_baseline, "ledger": cmd_ledger, "startup": cmd_startup, "tags": cmd_tags,
    "compacts": cmd_compacts, "trial": cmd_trial, "context": cmd_context, "reads": cmd_reads,
    "replies": cmd_replies, "turns": cmd_turns,
}


def main(argv: list[str]) -> int:
    a = parse_args(argv)
    COMMANDS[a.cmd](a)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
