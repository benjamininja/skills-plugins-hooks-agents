import type { OwnerSeen } from '../types'

/** The main-agent roles whose sessions are tracked (#161, Q3). Stage builders never are. */
export const ROLES = [
  'central-planner',
  'central-builder-manager',
  'supabase-consultant',
  'supabase-consultant-dispatch',
] as const

/** How often a tracked session writes its heartbeat: no more often than this. */
export const HEARTBEAT_MS = 30000

/** A record is stale, and its session stopped, after this many missed heartbeats. */
export const MISSED_BEATS = 3

/** The context size, in tokens, at which a session must prepare for a clear. */
export const CONTEXT_LIMIT = 255000

/** How long a session may sit idle after a turn before it prepares for a clear. */
export const IDLE_MS = 45 * 60 * 1000

/** The folders in the mod's own data folder, beside `drafts`. */
export const SESSIONS = 'sessions'
export const REQUESTS = 'requests'
export const PROMPTS = 'reset-prompts'

export type Trigger = 'context' | 'idle'

/**
 * One tracked session's own record, `sessions/<id>.json`. Only that session
 * writes it.
 */
export type SessionRecord = {
  id: string
  role: string
  name: string
  /** `cleared` when a `/clear` ended this id; the pane leaves it out. */
  state: 'busy' | 'idle' | 'closed' | 'cleared'
  /** When the last main-loop turn started and ended; 0 before the first. */
  turnStart: number
  turnEnd: number
  /** The context tokens the last measurement gave. */
  tokens: number
  /** The last heartbeat. */
  beat: number
  /** The time of the newest prep request this session has taken. */
  ran: number
  /** When each trigger last sent the prep instruction. */
  sent: Partial<Record<Trigger, number>>
  /** The file time of a reset prompt the `/clear` re-key moved here. */
  movedAt?: number
}

/** A prep request the pane writes, `requests/<id>.json`. Only the pane writes it. */
export type PrepRequest = { at: number }

/** The role a session was started with, `--agent <role>`, with any `plugin:` prefix cut. */
export function roleOf(agentType: string | undefined): string | undefined {
  if (!agentType) return undefined
  const bare = agentType.slice(agentType.lastIndexOf(':') + 1)

  return (ROLES as readonly string[]).includes(bare) ? bare : undefined
}

/** A session id as a file name: anything but letters, digits, `_` and `-` becomes `-`. */
export function fileName(id: string): string {
  return id.replace(/[^A-Za-z0-9_-]/g, '-')
}

/** The record read back from its file's text, or undefined when it is not one. */
export function recordOf(text: string): SessionRecord | undefined {
  try {
    const one = JSON.parse(text) as Partial<SessionRecord>
    if (
      typeof one?.id !== 'string' ||
      typeof one.role !== 'string' ||
      typeof one.beat !== 'number'
    )
      return undefined

    return {
      name: one.role,
      state: 'idle',
      turnStart: 0,
      turnEnd: 0,
      tokens: 0,
      ran: 0,
      sent: {},
      ...one,
    } as SessionRecord
  } catch {
    return undefined
  }
}

/**
 * The three-way answer: a fresh heartbeat is running (busy or idle as
 * written), `closed` is closed, a stale heartbeat with no `closed` is stopped.
 * Undefined for an id a `/clear` ended.
 */
export function seenOf(one: SessionRecord, now: number): OwnerSeen | undefined {
  if (one.state === 'cleared') return undefined
  if (one.state === 'closed') return 'closed'
  if (now - one.beat > MISSED_BEATS * HEARTBEAT_MS) return 'stopped'

  return one.state
}

/** Whether the session is not running: stopped or closed. */
export function isDown(seen: OwnerSeen | undefined): boolean {
  return seen === 'stopped' || seen === 'closed'
}

/**
 * A reset prompt is fresh when its file time is at or after the session's
 * last `turn.start`. An empty or missing file is no prompt.
 */
export function isFresh(
  prompt: { mtimeMs: number; size: number } | undefined,
  one: Pick<SessionRecord, 'turnStart'>,
): boolean {
  return prompt !== undefined && prompt.size > 0 && prompt.mtimeMs >= one.turnStart
}

/** A moved prompt the session has not written over since the `/clear`. */
export function isUsed(
  prompt: { mtimeMs: number; size: number } | undefined,
  one: Pick<SessionRecord, 'movedAt'>,
): boolean {
  return (
    prompt !== undefined &&
    prompt.size > 0 &&
    one.movedAt !== undefined &&
    prompt.mtimeMs <= one.movedAt
  )
}

/** Each trigger sends once, until a new turn starts after it. */
export function isArmed(one: SessionRecord, trigger: Trigger): boolean {
  const at = one.sent[trigger]

  return at === undefined || one.turnStart > at
}

/** Whether the context trigger is due: at or past the limit, armed. */
export function isContextDue(one: SessionRecord, isPromptFresh: boolean): boolean {
  return one.tokens >= CONTEXT_LIMIT && !isPromptFresh && isArmed(one, 'context')
}

/** Whether the idle trigger is due: idle 45 minutes after a turn, armed. */
export function isIdleDue(
  one: SessionRecord,
  now: number,
  isPromptFresh: boolean,
): boolean {
  return (
    one.state === 'idle' &&
    one.turnEnd > 0 &&
    now - one.turnEnd >= IDLE_MS &&
    !isPromptFresh &&
    isArmed(one, 'idle')
  )
}

/** The prep instruction, naming the session-rules text and the exact file. */
export function instruction(why: string, path: string): string {
  return [
    `owner-queue: prepare for a clear now (${why}).`,
    `Follow the session-rules skill, "A role session's clear boundary", in order.`,
    `Write the reset prompt last, whole, to ${path}, with your file tool: replace the file, never append.`,
  ].join(' ')
}

/** Why each trigger fired, as the instruction says it. */
export const WHY = {
  context: (tokens: number) =>
    `context at ${tokens} tokens, at or past ${CONTEXT_LIMIT}: finish the current step, then prepare before any new work`,
  idle: () => `idle ${IDLE_MS / 60000} minutes`,
  request: () => 'End of Day, asked by the owner',
} as const

/** The word the pane draws for a session's state. */
export function wordOf(seen: OwnerSeen): string {
  return seen === 'busy' ? 'running, busy' : seen === 'idle' ? 'running, idle' : seen
}
