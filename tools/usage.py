"""Usage figures from a local Claude Code transcript store. Counts only (#263).

Usage:
  python tools/usage.py baseline --store DIR --from YYYY-MM-DD --to YYYY-MM-DD [--role ...]
  python tools/usage.py ledger   --store DIR --from ... --to ... [--role ...] [--top N]
  python tools/usage.py startup  --store DIR --from ... --to ... [--role ...] [--sessions]
  python tools/usage.py tags     --store DIR --from ... --to ... [--role ...] [--tag ...]
                                 [--only ROLE] [--idle-gap SECONDS]
  python tools/usage.py compacts --store DIR --from ... --to ... [--role ...]
  python tools/usage.py shapes   --store DIR --from ... --to ... [--role ...] [--only ROLE]
                                 [--needle NAME] [--top N]
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

Turn openers (step 3 of #263): a user record's own field names its source,
origin.kind, else turnOrigin (human, peer, task-notification, plugin, system);
its text decides only when it has neither. A meta record opens a turn only
when it is a peer message. A peer message queued as a queued_command
attachment arrives inside a running turn: it opens none, and the next reply is
tagged message in. A message queued and then stored as a meta record before
the next reply counts once, matched by its text from the tag on; a different
peer message in between still opens its turn.

Method point 1, per-read sizes (`reads`): only the turn's context growth is
measured. Each tool result is sized in characters and turned into tokens at the
turn's mean ratio, result characters over that growth, so each per-read figure
is an estimate at that mean ratio, not a measurement. For a turn that ended
with positive growth and no compact inside it, the figures add up to the whole
growth, which also holds the replies' own output and text the app injects, so
taken together they are an upper bound on what the reads cost. No bound is
claimed for a turn with no ending reply (results may come after its last
reply, counted but not grown into), with no growth (an assumed 4 characters
per token is used), or with a compact between its first and last reply (the
growth covers only what survived the compact). One
result alone is never bounded: a result denser than the mean (minified JSON,
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
# The one lead line the app writes before a peer message, as it reads in a session's
# context (November 2026). Any other text before a tag makes the opener "ambiguous".
APP_LEADS = ("Another Claude session sent a message:\n",)
ASSUMED_CPT = 4.0  # chars per token when a turn has no growth to divide by
OPENER_KINDS = ("typed", "peer message", "app event", "plugin", "system", "system reminder",
                "ambiguous", "other source")
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
# What may print from the store (#312): words the outputs posted on #258 and #263 show, or
# that this script names itself. A list grows only from a posted output.
KNOWN_MODELS = frozenset({"claude-opus-5-5", "claude-fable-5-2", "claude-sonnet-5-5"})
KNOWN_TRIGGERS = frozenset({"manual", "auto"})
KNOWN_COMPACT_KEYS = frozenset({"trigger", "preTokens", "pre_tokens", "postTokens", "durationMs"})
KNOWN_SHAPE_KEYS = frozenset({"model", "tools"})
KNOWN_TOOLS = frozenset({"Read", "Bash", "Agent", "Task", "SendMessage"})
KNOWN_STOPS = frozenset({"end_turn", "tool_use"})
KNOWN_RECORD_TYPES = frozenset({
    "assistant", "user", "system", "attachment", "progress", "file-history-snapshot",
    "queue-operation", "api-request-blob", "api-request-shape", "custom-title", "agent-name",
})
KNOWN_SUBTYPES = frozenset({"compact_boundary"})
KNOWN_ATTACHMENTS = frozenset({
    "queued_command", "silent_turn_reminder", "deferred_tools_record", "skill_listing",
    "prompt_snapshot", "agent_listing_delta", "deferred_tools_delta", "mcp_instructions_delta",
    "nested_memory", "instructions", "hook_success",
})
KNOWN_BLOCKS = frozenset({"text", "tool_use", "tool_result"})
KNOWN_TAGS = frozenset({
    "system-reminder", "task-notification", "side-sessions-event", "cross-session-message",
    "command-name", "local-command-caveat", "local-command-stdout",
})
KNOWN_RECORD_KEYS = frozenset({
    # on every user record in the shapes output on #263
    "cwd", "entrypoint", "gitBranch", "isSidechain", "message", "parentUuid", "promptId",
    "sessionId", "timestamp", "type", "userType", "uuid", "version",
    # on some of them
    "sourceToolAssistantUUID", "toolUseResult", "permissionDecision", "dataFlowOn",
    "serverClassifierContext", "sandboxed", "slug", "turnPosition", "origin", "turnOrigin",
    "permissionMode", "promptSource", "queueSkipAttachments", "isMeta", "queueSkipSlashCommands",
    "clientPlatform", "turnAttributionKey", "turnPromptId", "turnCompanion", "mcpMeta",
    "mcpCallNotReadOnly", "sourceToolUseID", "toolDenialKind", "queueTranscriptOnly",
    "isCompactSummary", "isVisibleInTranscriptOnly", "interruptedByShutdown", "mergedSendUuids",
    "imagePasteIds", "summarizedTurnPromptUuids",
    # needle paths on #263, and keys this script reads
    "attachment", "content", "rendered", "shape", "subtype", "compactMetadata", "customTitle",
    "title", "agentName", "agentSetting",
})


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
    peers_before: int = 0  # peer messages queued inside the running turn since the reply before it

    @property
    def after_peer(self) -> bool:
        return self.peers_before > 0

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
    queued_peers: int = 0  # peer messages queued since the last reply, waiting for the next
    queued_bodies: list[str] = field(default_factory=list)  # their text from the tag on, to match only

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
    is one whose tag opens the rest, or follows exactly one of APP_LEADS. Text holding
    such a tag anywhere else is "ambiguous" (a typed prompt quoting one, or a lead this
    script does not know), so a miscount shows as a count, never as a silent guess.
    Anything else is typed."""
    t = text.lstrip()
    while t.startswith(REMINDER_MARK):
        end = t.find(REMINDER_END)
        if end < 0:
            return "system reminder"
        t = t[end + len(REMINDER_END):].lstrip()
        if not t:
            return "system reminder"
    rest = next((t[len(lead):] for lead in APP_LEADS if t.startswith(lead)), t)
    tagged = False
    for kind, marks in (("peer message", (PEER_MARK,)), ("app event", APP_MARKS)):
        for m in marks:
            if rest.startswith(m):
                return kind
            tagged = tagged or m in t
    return "ambiguous" if tagged else "typed"


# origin.kind, else turnOrigin, as stored in November 2026 (the shapes probe on #263).
SOURCE_KINDS = {"human": "typed", "peer": "peer message", "task-notification": "app event",
                "task_notification": "app event", "plugin": "plugin", "system": "system"}


def source_kind(o: dict) -> str | None:
    """The opener kind a user record's own fields name, or None when it has none."""
    org = o.get("origin")
    k = org.get("kind") if isinstance(org, dict) else None
    if not isinstance(k, str):
        k = o.get("turnOrigin")
    if not isinstance(k, str):
        return None
    return SOURCE_KINDS.get(k, "other source")


def peer_body(text: str) -> str | None:
    """A peer message's text from its tag on, so one stored twice can be matched.
    Compared only, never printed."""
    pos = text.find(PEER_MARK)
    # line endings and runs of whitespace are set aside, so a copy stored with other
    # spacing still matches (F4 of the re-check on PR #308)
    return " ".join(text[pos:].split()) if pos >= 0 else None


def is_queued_peer(att: dict) -> bool:
    """A queued command holding a peer message: the tag opens its prompt."""
    p = att.get("prompt")
    return att.get("type") == "queued_command" and isinstance(p, str) and p.lstrip().startswith(PEER_MARK)


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
                    if is_queued_peer(o["attachment"]):
                        s.queued_peers += 1
                        s.queued_bodies.append(peer_body(o["attachment"]["prompt"]))
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
                  num(u, "cache_read_input_tokens"), num(u, "output_tokens"), len(s.openers),
                  peers_before=s.queued_peers)
        s.queued_peers = 0
        s.queued_bodies = []
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
    # the record's own source field first (step 3 of #263); its text only when it has none
    kind = source_kind(o) or opener_kind(text)
    s.events.append(("user", kind, meta, len(text), ts))
    if meta and kind != "peer message":
        return  # a meta record is injected text, unless it is a peer message
    body = peer_body(text) if kind == "peer message" else None
    if body is not None and body in s.queued_bodies:
        s.queued_bodies.remove(body)  # the same message, queued and stored again before the next reply
        return
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
    """One tag per reply: start-up, a rule's tag, message in (the first reply after a
    peer message queued inside a running turn), the tag carried from the reply before
    it in the same turn, message in (a turn a peer message opened), or untagged."""
    start, _ = startup_cut(replies)
    tags: list[str] = []
    for k, r in enumerate(replies):
        if k < len(start):
            tags.append(START_UP)
            continue
        tag = tag_of(r, rules)
        if tag is None and r.after_peer:
            tag = MESSAGE_IN
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


def known(v, words: frozenset, label: str = "other") -> str:
    """A value read from the store prints only when it is a word the store was seen to
    hold (#312), else as one fixed label. Counts keyed by what this returns still count it."""
    return v if isinstance(v, str) and v in words else label


def trigger_word(t) -> str:
    return "None" if t is None else known(t, KNOWN_TRIGGERS)


def count_of(v) -> str:
    """A number prints as it is; anything else stored in its place is not printed."""
    return str(v) if isinstance(v, int) else ("None" if v is None else "?")


def short_model(m: str) -> str:
    m = known(m, KNOWN_MODELS)
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
        # counted once: a turn counts by its counted replies, so a copied history adds none
        x["openers"].update(s.openers[t - 1] for t in {r.turn for r in c if r.turn > 0})
        x["all"]["peer_mid"] += sum(r.peers_before for r in c)
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
        print("turns opened by: " + " ".join(
            f"{k.replace(' ', '-')}={x['openers'][k]}" for k in OPENER_KINDS)
            + f"; peer messages inside a running turn={x['all']['peer_mid']}")
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
    print("compactMetadata keys seen:", ", ".join(sorted({known(k, KNOWN_COMPACT_KEYS) for k in keys})) or "none")
    print("triggers:", dict(collections.Counter(trigger_word(r["trigger"]) for r in rows)))
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
        print(f"last compact: day={cp.ts[:10]} trigger={trigger_word(cp.trigger)} pre={count_of(cp.pre)} "
              f"post={count_of(cp.post)} durationMs={count_of(cp.ms)} lastCtxBefore={before[-1].ctx if before else 0} "
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
    top = collections.Counter(known(k, KNOWN_SHAPE_KEYS) for k in shape)
    print("top keys:", ", ".join(k if k in KNOWN_SHAPE_KEYS else f"{k}={n}" for k, n in sorted(top.items())))
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
            rows.append((k, "mcp" if c.name.startswith("mcp__") else known(c.name, KNOWN_TOOLS), c.ext, ev[2]))
        elif ev[0] == "injected" and n:
            rows.append((n, "(injected text)", "", ev[1]))
    growth = start[-1].ctx - start[0].ctx
    chars = sum(r[3] for r in rows)
    # a compact between the turn's first and last reply drops context, so the growth
    # covers only what survived it
    compacted = any(1 <= cp.at < len(start) for cp in s.compacts)
    bounded = ended and growth > 0 and not compacted
    cpt = chars / growth if growth > 0 else ASSUMED_CPT
    print("per-read tokens are ESTIMATES at the turn's mean chars/token (method point 1), not "
          "measurements; one dense result alone may be shown below its size")
    if bounded:
        print("the turn ended with positive growth: together the figures are an upper bound on the "
              "reads (the growth also holds the replies' own output and injected text)")
    else:
        # every reason that holds is named, the compact first (F9 of #297): after a compact
        # the growth is usually negative, which would otherwise hide it
        why = []
        if compacted:
            why.append("a compact falls inside the turn, so its growth covers only what survived it")
        if not ended:
            why.append("the turn has no ending reply")
        if growth <= 0:
            why.append(f"growth is {growth}, so {ASSUMED_CPT} is assumed")
        print(f"no bound is claimed: {'; '.join(why)}")
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
                  f"inEq={r.eq / 1000:6.1f}k cum={cum / 1000:7.1f}k calls={len(r.calls)} "
                  f"stop={'None' if r.stop is None else known(r.stop, KNOWN_STOPS)}")
        elif ev[0] == "user":
            _, kind, meta, length, ts = ev
            print(f"   -- user ({kind}) meta={meta} len={length} {ts[11:19]}")
        elif ev[0] == "record":
            print(f"   -- record {known(ev[1], KNOWN_RECORD_TYPES | KNOWN_SUBTYPES)} {ev[2][11:19]}")
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


# ---- shapes: where a kind of record lives in the store (#263 step 2) -------------

NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_-]{0,40}")
TAG_RE = re.compile(r"<([a-z][a-z0-9-]{0,40})[\s>/]")
# Keys below a record's top level that are the transcript format's own, never data.
STRUCT_KEYS = frozenset({
    "message", "content", "text", "attachment", "type", "input", "toolUseResult", "data",
    "stdout", "stderr", "output", "result", "prompt", "summary", "command", "value",
    "addedBlocks", "addedLines", "systemPrompt", "files",
})


def safe(v, words: frozenset = frozenset()) -> str:
    """A type or key name from the store: itself when it is one of words, "-" when
    missing, else "?"."""
    if v is None:
        return "-"
    return known(v, words, "?")


def lead_of(text: str) -> str:
    """How a text starts: its leading tag's name, or only that it is text. Never the text."""
    t = text.lstrip()
    if not t:
        return "empty"
    if t.startswith("<"):
        m = TAG_RE.match(t)
        return f"<{known(m.group(1), KNOWN_TAGS, '?')}>" if m else "<?>"
    return "text"


def content_kind(c) -> str:
    if isinstance(c, str):
        return "str:" + lead_of(c)
    if isinstance(c, list):
        kinds = set()
        for x in c:
            k = safe(x.get("type"), KNOWN_BLOCKS) if isinstance(x, dict) else "?"
            if k == "text" and isinstance(x, dict):
                k += ":" + lead_of(str(x.get("text") or ""))
            kinds.add(k)
        return "list[" + ",".join(sorted(kinds)) + "]"
    return "none" if c is None else "?"


def shape_of(o: dict) -> str:
    msg = o.get("message") if isinstance(o.get("message"), dict) else {}
    att = o.get("attachment") if isinstance(o.get("attachment"), dict) else {}
    parts = [f"type={safe(o.get('type'), KNOWN_RECORD_TYPES)}"]
    if "subtype" in o:
        parts.append(f"subtype={safe(o.get('subtype'), KNOWN_SUBTYPES)}")
    if att:
        parts.append(f"attachment={safe(att.get('type'), KNOWN_ATTACHMENTS)}")
    parts.append(f"meta={bool(o.get('isMeta'))}")
    if "content" in msg:
        parts.append("content=" + content_kind(msg.get("content")))
    elif "content" in att:
        parts.append("attachment.content=" + content_kind(att.get("content")))
    return " ".join(parts)


def needle_places(o, needle: str, path: str = "", depth: int = 0):
    """(key path, position) of each string under o that holds the needle. A key prints
    only at a record's top level or when it is one of STRUCT_KEYS: anywhere below, a
    map may be data keyed by names (session ids, branches, servers), so it prints "?"."""
    if isinstance(o, dict):
        for k, v in o.items():
            name = k if k in STRUCT_KEYS else (safe(k, KNOWN_RECORD_KEYS) if depth == 0 else "?")
            yield from needle_places(v, needle, f"{path}.{name}", depth + 1)
    elif isinstance(o, list):
        for v in o:
            yield from needle_places(v, needle, path + "[]", depth)
    elif isinstance(o, str) and needle in o:
        pos = o.find(needle)
        before = o[:pos]
        if before.strip() in ("", "<"):
            where = "at start"
        else:
            n = before.count("\n")
            where = "line 1, after text" if n == 0 else ("line 2" if n == 1 else "line 3 or later")
        yield path or ".", where


SOURCE_KEYS = ("origin", "turnOrigin", "promptSource")


# Inside an object, only these keys' word values print; any other key's value is an id or
# text (from=, runId=, name=, msg_id= held ids on the real store, #263), so it prints "?".
WORD_VALUE_KEYS = frozenset({"kind", "producer", "fromMode"})
# Every value and key that prints is one the store was seen to hold (November 2026, #263):
# an enum, never an id or a name. Anything else prints "?".
KNOWN_VALUES = frozenset(SOURCE_KINDS) | frozenset({"sdk", "prompting", "session-task"})
KNOWN_KEYS = frozenset({
    "kind", "producer", "fromMode", "from", "fromSession", "msg_id", "name", "runId", "body",
    "hopChain", "fullHopChain", "handback", "handbackReportText", "handbackToolUseId",
    "hostInjected", "asUser",
})


def word(v, show: bool = True) -> str:
    """A value as a known word (KNOWN_VALUES), else "?". An object shows at most ten
    keys, each from KNOWN_KEYS else "?"; a value inside prints only under
    WORD_VALUE_KEYS, or as true/false; a nested object or list is "?"."""
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return v if show and v in KNOWN_VALUES else "?"
    if isinstance(v, dict):
        items = sorted(v.items(), key=lambda kv: str(kv[0]))
        parts = [f"{k if k in KNOWN_KEYS else '?'}="
                 f"{'?' if isinstance(x, (dict, list)) else word(x, show=k in WORD_VALUE_KEYS)}"
                 for k, x in items[:10]]
        return "{" + ",".join(parts) + (",..." if len(items) > 10 else "") + "}"
    return "?"


def record_kind(o: dict, needle: str) -> str:
    """What a user record is, for the source-key count. Never its text."""
    c = (o.get("message") or {}).get("content") if isinstance(o.get("message"), dict) else None
    if o.get("isCompactSummary"):
        return "compact summary"
    if isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
        return "tool result"
    text = text_of(o) if isinstance(o.get("message"), dict) else None
    if o.get("isMeta"):
        t = text or ""
        pos = t.find("<" + needle)
        return "meta, tag on line 1-2" if pos >= 0 and t[:pos].count("\n") <= 1 else "meta, other"
    return "other" if text is None else "non-meta " + opener_kind(text)


class Arrivals:
    """Per file: tagged queued commands and tagged meta user records, their overlap
    and where in a turn they land. Counts only."""

    def __init__(self, needle: str):
        self.needle = needle
        self.overlap: collections.Counter = collections.Counter()
        self.where: collections.Counter = collections.Counter()

    def start_file(self) -> None:
        self.last_stop: str | None = None  # None: no reply yet
        self.reply_id = None
        self.pending = 0  # tagged queued commands since the last reply, not yet met by a meta record

    def position(self) -> str:
        if self.last_stop is None:
            return "before any reply"
        if self.last_stop in (TOOL_USE, "pending"):
            return "inside a running turn"
        return "after a reply that ended its turn"

    def flush(self, why: str) -> None:
        if self.pending:
            self.overlap[f"queued command, no meta record before {why}"] += self.pending
        self.pending = 0

    def feed(self, o: dict) -> None:
        t = o.get("type")
        if t == "assistant":
            msg = o.get("message") if isinstance(o.get("message"), dict) else {}
            if msg.get("model") == SYNTHETIC:
                return
            if msg.get("id") != self.reply_id:
                self.reply_id = msg.get("id")
                self.flush("the next reply")
                self.last_stop = "pending"
            if msg.get("stop_reason"):
                self.last_stop = msg["stop_reason"]
        elif t == "attachment":
            att = o.get("attachment") if isinstance(o.get("attachment"), dict) else {}
            if att.get("type") == "queued_command" and self.needle in json.dumps(att.get("prompt")):
                self.where[("tagged queued command", self.position())] += 1
                self.pending += 1
        elif t == "user" and o.get("isMeta") and self.needle in (text_of(o) or ""):
            self.where[("tagged meta record", self.position())] += 1
            if self.pending:
                self.pending -= 1
                self.overlap["queued command, then a meta record before the next reply"] += 1
            else:
                self.overlap["meta record, no queued command since the last reply"] += 1


def cmd_shapes(a) -> None:
    shapes: collections.Counter = collections.Counter()
    needles: collections.Counter = collections.Counter()
    keys: collections.Counter = collections.Counter()
    sources: collections.Counter = collections.Counter()
    arrivals = Arrivals(a.needle)
    n_sessions = n_records = n_needle = 0
    for _, s, role in in_window(a.store, a.lo, a.hi, a.roles):
        if a.only and role not in a.only:
            continue
        n_sessions += 1
        arrivals.start_file()
        with open(s.path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(o, dict) or o.get("isSidechain"):
                    continue
                n_records += 1
                shape = shape_of(o)
                shapes[shape] += 1
                arrivals.feed(o)
                if o.get("type") == "user":
                    keys.update(safe(k, KNOWN_RECORD_KEYS) for k in o)
                    sources[(record_kind(o, a.needle),) + tuple(word(o.get(k)) for k in SOURCE_KEYS)] += 1
                if a.needle in line:
                    n_needle += 1
                    places = sorted(set(needle_places(o, a.needle))) or [("(not in a string value)", "-")]
                    for path, where in places:
                        needles[(shape, path, where)] += 1
        arrivals.flush("the end of the file")
    print(f"window: sessions whose first reply is {a.lo}..{a.hi}; sessions={n_sessions} records={n_records}; "
          "counts and structure only")
    print(f"\n== records by shape (top {a.top}) ==")
    for shape, n in shapes.most_common(a.top):
        print(f"{n:8}  {shape}")
    print(f"\n== records holding {a.needle!r}: {n_needle} ==")
    for (shape, path, where), n in needles.most_common(a.top):
        print(f"{n:8}  {shape} | at {path} | {where}")
    print("\n== top-level keys of user records ==")
    print(" ".join(f"{k}={n}" for k, n in sorted(keys.items())))
    print(f"\n== user records by what they are, against {', '.join(SOURCE_KEYS)} (one short word, else ?; "
          "- when missing) ==")
    for (kind, *vals), n in sorted(sources.items(), key=lambda x: (-x[1], x[0])):
        print(f"{n:8}  {kind} | " + " ".join(f"{k}={v}" for k, v in zip(SOURCE_KEYS, vals)))
    print(f"\n== tagged queued commands and tagged meta records: overlap ==")
    for what, n in sorted(arrivals.overlap.items()):
        print(f"{n:8}  {what}")
    print("\n== where they land in a turn ==")
    for (what, where), n in sorted(arrivals.where.items()):
        print(f"{n:8}  {what} | {where}")


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


def needle_arg(text: str) -> str:
    if not NAME_RE.fullmatch(text) or len(text) < 3:
        raise argparse.ArgumentTypeError("expected a tag-like name: letters, digits, _ and -")
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
    sp = sub.add_parser("shapes")
    store(sp)
    sp.add_argument("--only", action="append", default=None)
    sp.add_argument("--needle", type=needle_arg, default="cross-session-message")
    sp.add_argument("--top", type=int, default=40)
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
    "replies": cmd_replies, "turns": cmd_turns, "shapes": cmd_shapes,
}


def main(argv: list[str]) -> int:
    a = parse_args(argv)
    COMMANDS[a.cmd](a)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
