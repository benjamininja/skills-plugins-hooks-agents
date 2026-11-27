import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, RenderSurface } from 'claude-code'

import type {
  OwnerAnswers,
  OwnerComments,
  OwnerHeld,
  OwnerItem,
  OwnerNotes,
  OwnerOption,
  OwnerQueue,
  OwnerQueueFile,
  OwnerRoster,
  OwnerSession,
  OwnerStaged,
} from '../types'
import type { Committed } from './parse'
import type { PrepRequest, SessionRecord } from './sessions'
import {
  HEARTBEAT_MS,
  PROMPTS,
  REQUESTS,
  SESSIONS,
  WHY,
  fileName,
  instruction,
  isContextDue,
  isDown,
  isFresh,
  isIdleDue,
  isUsed,
  recordOf,
  roleOf,
  seenOf,
  wordOf,
} from './sessions'
import {
  answerOf,
  carried,
  carriedDone,
  clean,
  comment,
  commit,
  detail,
  layout,
  here,
  hint,
  idOf,
  isMalformed,
  labelOf,
  notesOf,
  options,
  OTHER,
  parse,
  problemLine,
  recommended,
  reference,
  report,
  said,
  sameFile,
  sessionOf,
  shown as printed,
  slashed,
  spans,
  summary,
  unanswer,
  waiting,
} from './parse'

const VERSION = '0.12.0'
const PANE = 'owner-queue'
const TITLE = 'Needs owner'
const FILE = '.claude/memory/NEEDS-OWNER.md'
const PROBLEMS = '.claude/owner-queue/problems.log'
const PROBLEM_KIND = 'Options line: a key appears twice'
const EVERY_MS = 5000
const GIVE_UP_MS = 60000
const BY_HAND =
  'The queue was not re-keyed after the /clear: change the Session lines by hand (session-rules, parking.md, "The Session line across a clear")'
const HALF =
  'The re-key stopped part way after the /clear: some records or queue files may still name the old id; check the Session lines by hand (session-rules, parking.md, "The Session line across a clear")'
const ANSWERS = 'answers'
const NOTES = 'notes'
const LOGGED = 'logged'

const ref = { plugin: 'owner-queue', key: 'queue' } as const
const EMPTY: OwnerQueue = { isLoaded: false, hasFile: false, items: [] }
const queue = atom(ref, EMPTY)
const open = atom({ plugin: 'owner-queue', key: 'open' } as const, [])
const shownRef = { plugin: 'owner-queue', key: 'shown' } as const
const shown = atom(shownRef, false)
const readAtRef = { plugin: 'owner-queue', key: 'readAt' } as const
const readAt = atom(readAtRef, '')
const stagedRef = { plugin: 'owner-queue', key: 'staged' } as const
const NONE: OwnerStaged = {}
const staged = atom(stagedRef, NONE)
const commentsRef = { plugin: 'owner-queue', key: 'comments' } as const
const NO_COMMENTS: OwnerComments = {}
const comments = atom(commentsRef, NO_COMMENTS)
const writing = atom({ plugin: 'owner-queue', key: 'writing' } as const, [])
const strokes = atom({ plugin: 'owner-queue', key: 'strokes' } as const, 0)
const rosterRef = { plugin: 'owner-queue', key: 'roster' } as const
const NO_ROSTER: OwnerRoster = { sessions: [], held: [] }
const roster = atom(rosterRef, NO_ROSTER)

/**
 * This session's own record, when it was started with a tracked role. Only
 * this session writes its file (#161). Read back from the file after a reload.
 */
let self: SessionRecord | undefined

/** True from a prep instruction until the turn it asked for starts. */
let isQueued = false

let isTending = false

/** A reset prompt the `/clear` re-key moved, waiting for the new id's record. */
let moved: { to: string; at: number } | undefined

/**
 * What is typed in each open comment box, by item id. Kept here and not in
 * the session's state, so a key press redraws nothing and a send button
 * reads the text at once.
 */
const drafts = new Map<string, string>()

type Source = { file: string; isMain: boolean }

let found: Promise<Source> | undefined

/** The other queues the owner listed in the plugin's `queues` setting. */
let listed: string[] = []

/** The session's own project's queue file, once `source` has found it. */
let own: string | undefined

/** The setting's value as a list of absolute paths; anything else is dropped. */
function queuesOf(value: unknown): string[] {
  const list = typeof value === 'string' ? [value] : Array.isArray(value) ? value : []

  return list
    .filter((one): one is string => typeof one === 'string')
    .map(one => slashed(one.trim()))
    .filter(one => /^([A-Za-z]:)?\//.test(one))
}

/**
 * The key of an entry in the pane's state and its button keys. The session's
 * own queue keeps the entry's id; any other queue's key has its path first,
 * so two queues never share a key.
 */
function keyOf(item: OwnerItem): string {
  return item.queue === undefined || item.queue === own
    ? idOf(item)
    : `${item.queue}|${idOf(item)}`
}

/** The key of an entry in the mod's store: its queue file, then its id. */
function at(item: OwnerItem, file = item.queue ?? own ?? FILE): string {
  return `${file}|${idOf(item)}`
}

/**
 * The queue file every session reads: the main checkout's, so a session in a
 * worktree shows the same queue. A worktree's `.git` is a file naming the
 * main checkout; elsewhere git is asked; failing both, the session's own copy.
 */
function source($: EngineInterface): Promise<Source> {
  found ??= (async () => {
    try {
      const link = /^gitdir:\s*(.+?)[\\/]\.git[\\/]worktrees[\\/]/m.exec(
        await $.fs.read('.git'),
      )
      if (link)
        return { file: `${link[1].replaceAll('\\', '/')}/${FILE}`, isMain: true }
    } catch {
      // A main checkout's `.git` is a folder: no file to read.
    }
    try {
      const { exitCode, stdout } = await $.process.run([
        'git',
        'rev-parse',
        '--path-format=absolute',
        '--git-common-dir',
      ])
      const common = stdout.trim().replaceAll('\\', '/')
      if (exitCode === 0 && common.endsWith('/.git'))
        return {
          file: `${common.slice(0, -'/.git'.length)}/${FILE}`,
          isMain: true,
        }
    } catch {
      // Not a repository, or a surface that runs no process.
    }

    return { file: FILE, isMain: false }
  })().then(one => {
    own = one.file

    return one
  })

  return found
}

/** Every queue the pane reads: the session's own first, then each listed one. */
async function every($: EngineInterface): Promise<Source[]> {
  const first = await source($)
  const all = [first]
  for (const file of listed)
    if (!all.some(one => sameFile(one.file, file)))
      all.push({ file, isMain: true })

  return all
}

const two = (n: number) => String(n).padStart(2, '0')

async function clock($: EngineInterface): Promise<{ day: string; time: string }> {
  let at = new Date()
  try {
    at = new Date(await $.clock.now())
  } catch {
    // The engine's clock is the better one; the environment's will do.
  }

  return {
    day: `${at.getFullYear()}-${two(at.getMonth() + 1)}-${two(at.getDate())}`,
    time: `${two(at.getHours())}:${two(at.getMinutes())}:${two(at.getSeconds())}`,
  }
}

/** The Answer lines the pane itself wrote, which no session can write. */
async function penned($: EngineInterface): Promise<OwnerAnswers> {
  try {
    return ((await $.store.get(ANSWERS)) as OwnerAnswers | undefined) ?? {}
  } catch {
    return {}
  }
}

/** This session's id, or undefined where the engine gives none. */
async function me($: EngineInterface): Promise<string | undefined> {
  try {
    return (await $.session.id()) || undefined
  } catch {
    return undefined
  }
}

async function kept<T>($: EngineInterface, key: string, none: T): Promise<T> {
  try {
    return ((await $.store.get(key)) as T | undefined) ?? none
  } catch {
    return none
  }
}

let isDelivering = false

/**
 * Message back: an entry that names this session and has gained an Answer
 * line or a Note line the pane wrote, or was marked done, in any session's
 * pane, is said in this session's chat as the owner's words, once.
 */
async function deliver(
  $: EngineInterface,
  items: OwnerItem[],
  answered: OwnerAnswers,
  wrote: OwnerNotes,
): Promise<void> {
  if (isDelivering) return
  isDelivering = true
  try {
    const mine = await me($)
    if (!mine) return
    const had = await kept<OwnerAnswers>($, `delivered:${mine}`, {})
    const due = items.filter(item => {
      const given = answerOf(item)
      const place = at(item)

      return (
        sessionOf(item) === mine &&
        given !== undefined &&
        answered[place] === given &&
        had[place] !== given
      )
    })
    const marked = await kept<string[]>($, `done:${mine}`, [])
    const told = await kept<OwnerNotes>($, `noted:${mine}`, {})
    const fresh = items.flatMap(item => {
      const place = at(item)
      if (sessionOf(item) !== mine) return []

      return notesOf(item)
        .filter(
          one =>
            (wrote[place] ?? []).includes(one) &&
            !(told[place] ?? []).includes(one),
        )
        .map(one => ({ item, place, line: one }))
    })
    if (due.length === 0 && marked.length === 0 && fresh.length === 0) return
    if (fresh.length > 0) {
      const now = { ...told }
      for (const { place, line } of fresh)
        now[place] = [...(now[place] ?? []), line]
      await $.store.set(`noted:${mine}`, now)
    }
    if (due.length > 0)
      await $.store.set(`delivered:${mine}`, {
        ...had,
        ...Object.fromEntries(
          due.map(item => [at(item), answerOf(item) ?? '']),
        ),
      })
    if (marked.length > 0) await $.store.set(`done:${mine}`, [])
    const text = [
      ...due.map(item => carried(item, answerOf(item) ?? '')),
      ...(marked.length > 0 ? [carriedDone(marked)] : []),
      ...fresh.map(({ item, line }) => {
        const { text: words, when } = said(line)

        return comment(item, words, true, when)
      }),
    ].join('\n\n')
    const answers = due.length + marked.length
    $.ui.toast(
      [
        ...(answers > 0 ? [`The owner answered: ${answers}`] : []),
        ...(fresh.length > 0 ? [`The owner commented: ${fresh.length}`] : []),
      ].join('; '),
    )
    void $.prompt.submit({ text, asUser: true })
  } finally {
    isDelivering = false
  }
}

/** Puts the pane on screen and records whether a surface drew it. */
async function show($: EngineInterface): Promise<void> {
  const { isPlaced } = await $.ui.open({ id: PANE, title: TITLE })
  await $.state.set(shownRef, isPlaced)
}

/**
 * Takes the pane off screen and records it. The `ui.close` hook only hears
 * the person's close and an unload, so this call records its own.
 */
async function hide($: EngineInterface): Promise<void> {
  await $.ui.close({ id: PANE })
  await $.state.set(shownRef, false)
}

/** Flips the pane by the engine's record, so a stale flag cannot stick. */
async function toggle($: EngineInterface): Promise<void> {
  const isUp = (await $.ui.panes()).some(
    pane => pane.id === PANE && pane.isPlaced,
  )
  await (isUp ? hide($) : show($))
}

let isLogging = false

/** The user's home folder, where the problems log is kept; undefined if unknown. */
async function home($: EngineInterface): Promise<string | undefined> {
  try {
    const path = (await $.env.get('USERPROFILE')) || (await $.env.get('HOME'))

    return path ? slashed(path) : undefined
  } catch {
    return undefined
  }
}

/**
 * Adds one line to the problems log for each entry the parser cannot draw.
 * The same entry with the same problem is logged once: the store keeps what
 * is already logged, and drops an entry that is fixed, so a return of the
 * problem is logged again. A failure to log never stops a read.
 */
async function log($: EngineInterface, items: OwnerItem[]): Promise<void> {
  if (isLogging) return
  isLogging = true
  try {
    const bad = items
      .filter(
        item =>
          item.kind === 'decision' &&
          answerOf(item) === undefined &&
          isMalformed(item),
      )
      .map(item => ({ item, mark: `${at(item)}|${PROBLEM_KIND}` }))
    const had = await kept<string[]>($, LOGGED, [])
    const marks = bad.map(({ mark }) => mark)
    if (marks.length === had.length && marks.every(mark => had.includes(mark)))
      return
    await $.store.set(LOGGED, marks)
    const fresh = bad.filter(({ mark }) => !had.includes(mark))
    const base = fresh.length > 0 ? await home($) : undefined
    if (base === undefined) return
    const path = `${base}/${PROBLEMS}`
    const { day, time } = await clock($)
    const before = (await $.fs.exists(path)) ? await $.fs.read(path) : ''
    const lines = fresh.map(({ item }) =>
      problemLine(`${day} ${time}`, item.queue ?? FILE, item, PROBLEM_KIND),
    )
    await $.fs.write(
      path,
      `${before}${before === '' || before.endsWith('\n') ? '' : '\n'}${lines.join('\n')}\n`,
    )
  } catch {
    // The log is a courtesy; the pane still says what it cannot draw.
  } finally {
    isLogging = false
  }
}

/** The queue's file read as text, or undefined when it is missing. */
async function slurp($: EngineInterface, file: string): Promise<string | undefined> {
  try {
    return await $.fs.read(file)
  } catch {
    return undefined
  }
}

/**
 * The id a `/clear` ended in this session, and when. Kept here and not in the
 * store, which every session's copy of the mod shares. A clear neither
 * reloads the mod nor fires `session.start`, so the variable lives on; the
 * next read that finds another id under `$.session.id()` re-keys from it.
 */
let cleared: { from: string; at: number } | undefined

let isRekeying = false

/** The engine's time in milliseconds; the environment's will do. */
async function stamp($: EngineInterface): Promise<number> {
  try {
    return await $.clock.now()
  } catch {
    return Date.now()
  }
}

/**
 * The queue text with the id each `- Session:` field names changed from
 * `from` to `to`, and how many entries changed. An entry is judged as the
 * parser routes it, by its first Session field: if that names `from`, every
 * Session field of the entry that names `from` is changed; an entry whose
 * first Session field names another id is left whole. A field is read as the
 * parser reads it (a space before the colon, or the id on the next line).
 * Only an entry under a Decisions or Actions heading and `###` title is
 * touched, outside a fenced block. Any other line, an Answer or a Note among
 * them, and the words after the id, stay as written.
 */
function rekeyed(
  text: string,
  from: string,
  to: string,
): { text: string; count: number } {
  let count = 0
  let isListed = false
  let hasEntry = false
  let isFenced = false
  let first: boolean | undefined
  let isBare = false
  let isCounted = false
  const change = (id: string): boolean => {
    first ??= id === from
    if (!first || id !== from) return false
    if (!isCounted) count++
    isCounted = true

    return true
  }
  const lines = text.split('\n').map(raw => {
    const line = raw.trimEnd()
    const tail = raw.slice(line.length)
    if (hasEntry && line.trim().startsWith('```')) {
      isFenced = !isFenced

      return raw
    }
    if (isFenced) return raw
    const section = /^##\s+(.+)$/.exec(line)
    if (section) {
      isListed = /^(decision|action)/i.test(section[1].trim())
      hasEntry = false
      isFenced = false

      return raw
    }
    if (/^###\s+(?:\[( |x|X)\]\s*)?(.+)$/.test(line)) {
      hasEntry = isListed
      isFenced = false
      first = undefined
      isBare = false
      isCounted = false

      return raw
    }
    if (!hasEntry || line.trim() === '') return raw
    const field = /^(\s*[-*]\s+\**)([A-Za-z][A-Za-z ]{0,24}?)(\**:\**\s*)(.*)$/.exec(
      line,
    )
    if (field) {
      if (isBare) first ??= false
      isBare = false
      if (field[2].trim().toLowerCase() !== 'session') return raw
      const value = /^(\S+)(.*)$/.exec(field[4])
      if (!value) {
        isBare = true

        return raw
      }

      return change(value[1])
        ? `${field[1]}${field[2]}${field[3]}${to}${value[2]}${tail}`
        : raw
    }
    if (!isBare) return raw
    isBare = false
    const word = /^(\s*)(\S+)(.*)$/.exec(line)

    return word && change(word[2]) ? `${word[1]}${to}${word[3]}${tail}` : raw
  })

  return { text: lines.join('\n'), count }
}

/** Moves the record `<name>:<from>` to `<name>:<to>`, joined with one already there. */
async function shift<T>(
  $: EngineInterface,
  name: string,
  from: string,
  to: string,
  none: T,
  join: (into: T, was: T) => T,
): Promise<void> {
  const was = await kept<T>($, `${name}:${from}`, none)
  if (JSON.stringify(was) === JSON.stringify(none)) return
  await $.store.set(
    `${name}:${to}`,
    join(await kept<T>($, `${name}:${to}`, none), was),
  )
  await $.store.delete(`${name}:${from}`)
}

/**
 * After a `/clear`: at the first read where `$.session.id()` answers an id
 * other than the one the clear ended, the records of the old id move to the
 * new one and each queue's `Session:` lines that name the old id are
 * rewritten to it. With no clear seen it does nothing, since a resume also
 * moves the process to another id. If the old id still answers, or no id
 * does, after `GIVE_UP_MS`, it gives up and says the manual rule applies.
 */
async function rekey($: EngineInterface): Promise<void> {
  if (cleared === undefined || isRekeying) return
  isRekeying = true
  let isStarted = false
  try {
    const { from, at: since } = cleared
    const to = await me($)
    if (to === undefined || to === from) {
      if ((await stamp($)) - since >= GIVE_UP_MS) {
        cleared = undefined
        $.ui.toast(BY_HAND)
      }

      return
    }
    cleared = undefined
    isStarted = true
    await shift<OwnerAnswers>($, 'delivered', from, to, {}, (into, was) => ({
      ...into,
      ...was,
    }))
    await shift<OwnerNotes>($, 'noted', from, to, {}, (into, was) => ({
      ...into,
      ...Object.fromEntries(
        Object.entries(was).map(([place, lines]) => [
          place,
          [...new Set([...(into[place] ?? []), ...lines])],
        ]),
      ),
    }))
    await shift<string[]>($, 'done', from, to, [], (into, was) => [
      ...new Set([...into, ...was]),
    ])
    await movePrompt($, from, to)
    let count = 0
    let left = 0
    for (const one of await every($)) {
      const text = await slurp($, one.file)
      if (text === undefined) continue
      const made = rekeyed(text, from, to)
      if (made.count > 0) await $.fs.write(one.file, made.text)
      count += made.count
      left += parse(made.text).filter(item => sessionOf(item) === from).length
    }
    if (count > 0)
      $.ui.toast(
        `Re-keyed ${count} ${count === 1 ? 'entry' : 'entries'} to this session's new id`,
      )
    if (left > 0)
      $.ui.toast(
        `${left} ${left === 1 ? 'entry still names' : 'entries still name'} the old id: change ${left === 1 ? 'its' : 'their'} Session ${left === 1 ? 'line' : 'lines'} by hand (session-rules, parking.md, "The Session line across a clear")`,
      )
  } catch {
    cleared = undefined
    $.ui.toast(isStarted ? HALF : BY_HAND)
  } finally {
    isRekeying = false
  }
}

/**
 * Re-reads every queue file; redraws and toasts on a change. The owner opens
 * the pane. `canPrep` is false inside a `command.run` hook, where a submitted
 * prompt would wait on the hook itself; the next read takes the triggers.
 */
async function refresh($: EngineInterface, canPrep = true): Promise<OwnerQueue> {
  await rekey($)
  const sources = await every($)
  const { file, isMain } = sources[0]
  const queues: OwnerQueueFile[] = []
  const items: OwnerItem[] = []
  for (const one of sources) {
    const text = await slurp($, one.file)
    queues.push({
      file: one.file,
      label: one.file === file && !isMain ? 'this project' : labelOf(one.file),
      hasFile: text !== undefined,
    })
    if (text !== undefined)
      items.push(...parse(text).map(item => ({ ...item, queue: one.file })))
  }
  await pull($)
  const answered = await penned($)
  const wrote = await kept<OwnerNotes>($, NOTES, {})
  const now: OwnerQueue = {
    isLoaded: true,
    hasFile: queues.some(one => one.hasFile),
    items,
    queues,
    file,
    isMain,
    foreign: items
      .filter(item => {
        const given = answerOf(item)

        return given !== undefined && answered[at(item)] !== given
      })
      .map(keyOf),
    unpenned: Object.fromEntries(
      items
        .map(item => {
          const mine = wrote[at(item)] ?? []

          return [
            keyOf(item),
            notesOf(item).filter(one => !mine.includes(one)),
          ] as const
        })
        .filter(([, lines]) => lines.length > 0),
    ),
  }
  $.ui.status(summary(now.items))
  await log($, items)
  await deliver($, items, answered, wrote)
  await roll($, items, answered, wrote)
  if (canPrep) await tend($)
  await $.state.set(readAtRef, (await clock($)).time)
  // What was staged for an entry that has left the list is dropped.
  const { value: held = NONE } = await $.state.get(stagedRef)
  const live = new Set(
    items.filter(item => answerOf(item) === undefined).map(keyOf),
  )
  const still = Object.fromEntries(
    Object.entries(held).filter(([id]) => live.has(id)),
  )
  if (Object.keys(still).length !== Object.keys(held).length)
    await $.state.set(stagedRef, still)
  // A staged comment stays on an answered entry; it goes with an entry that
  // has left the file.
  const { value: typed = NO_COMMENTS } = await $.state.get(commentsRef)
  const present = new Set(items.map(keyOf))
  const remaining = Object.fromEntries(
    Object.entries(typed).filter(([id]) => present.has(id)),
  )
  if (Object.keys(remaining).length !== Object.keys(typed).length)
    await $.state.set(commentsRef, remaining)
  const { value: was = EMPTY } = await $.state.get(ref)
  if (JSON.stringify(was) === JSON.stringify(now)) return now

  await $.state.set(ref, now)

  const known = new Set(was.items.map(keyOf))
  const fresh = now.items.filter(item => !known.has(keyOf(item)))
  if (fresh.length > 0) {
    if (was.isLoaded) {
      const first = fresh[0]
      const more = fresh.length > 1 ? ` (+${fresh.length - 1} more)` : ''
      $.ui.toast(`Needs you, ${first.kind}: ${first.title}${more}`)
    }
  }

  return now
}

/** The Refresh button: reads now and says what it found. */
async function reread($: EngineInterface): Promise<void> {
  const now = await refresh($)
  $.ui.toast(
    now.hasFile
      ? `Queue read: ${summary(now.items) ?? 'nothing waiting'}`
      : 'No queue file was found',
  )
}

/** Stages a press, or takes it back when the same thing is pressed again. */
function stage(
  $: EngineInterface,
  item: OwnerItem,
  what: OwnerOption | 'done',
): Promise<void> {
  const id = keyOf(item)
  // A typed answer is never taken back by typing it again; it replaces.
  const isSame = (was: OwnerOption | 'done' | undefined) =>
    was !== undefined &&
    (was === 'done' || what === 'done'
      ? was === what
      : was.key !== OTHER && was.key === what.key)

  let isTaken = false

  return update($, staged, held => {
    const { [id]: was, ...rest } = held
    isTaken = isSame(was)

    return isTaken ? rest : { ...rest, [id]: what }
  }).then(() =>
    // A press that stages closes the entry, as a press on its title would.
    isTaken
      ? undefined
      : update($, open, list => list.filter(one => one !== id)),
  )
}

/**
 * What one Submit did in one queue file; `to` names each other session that
 * an answer, Note or done mark went to.
 */
type Wrote = {
  count: number
  away: number
  said: Committed
  lost: number
  to: string[]
}

/**
 * Writes what was staged for one queue file, in one write to that file, and
 * the pane's own record of each Answer and Note line under that file's path.
 */
async function write1(
  $: EngineInterface,
  file: string,
  held: OwnerStaged,
  typed: OwnerComments,
  by: string,
  mine: string | undefined,
  stamp: string,
): Promise<Wrote> {
  const text = await slurp($, file)
  if (text === undefined) {
    const lost = new Set([...Object.keys(held), ...Object.keys(typed)]).size

    return {
      count: 0,
      away: 0,
      said: { text: '', answered: [], noted: [], done: [], missing: [] },
      lost,
      to: [],
    }
  }
  const made = commit(
    text,
    held,
    chosen => `(${chosen.key}) ${chosen.text} | ${by}`,
    typed,
    words => `${words} | ${by}`,
  )
  const count = made.answered.length + made.noted.length + made.done.length
  const said = here(made, mine)
  const away =
    count - said.answered.length - said.noted.length - said.done.length
  if (count > 0) {
    // The pane's own record of each Note goes first, so no reader sees a line
    // it cannot place. This session's own are said by Submit, not carried.
    if (made.noted.length > 0) {
      const wrote = { ...(await kept<OwnerNotes>($, NOTES, {})) }
      const told = {
        ...(mine === undefined
          ? {}
          : await kept<OwnerNotes>($, `noted:${mine}`, {})),
      }
      for (const { item, line } of made.noted) {
        const place = at(item, file)
        wrote[place] = [...(wrote[place] ?? []), line]
        if (mine !== undefined && sessionOf(item) === mine)
          told[place] = [...(told[place] ?? []), line]
      }
      await $.store.set(NOTES, wrote)
      if (mine !== undefined) await $.store.set(`noted:${mine}`, told)
    }
    // This session's own entries are said by Submit below, not carried again.
    const self = made.answered.filter(
      ({ item }) => mine !== undefined && sessionOf(item) === mine,
    )
    if (mine !== undefined && self.length > 0)
      await $.store.set(`delivered:${mine}`, {
        ...(await kept<OwnerAnswers>($, `delivered:${mine}`, {})),
        ...Object.fromEntries(
          self.map(({ item, line }) => [at(item, file), line]),
        ),
      })
    // An item marked done has left the file: its raiser is told by the store.
    for (const item of made.done) {
      const to = sessionOf(item)
      if (to === undefined || to === mine) continue
      await $.store.set(`done:${to}`, [
        ...(await kept<string[]>($, `done:${to}`, [])),
        `${reference(item)}, marked done ${stamp}`,
      ])
    }
    await $.fs.write(file, made.text)
    if (made.answered.length > 0)
      await $.store.set(ANSWERS, {
        ...(await penned($)),
        ...Object.fromEntries(
          made.answered.map(({ item, line }) => [at(item, file), line]),
        ),
      })
  }

  const to = [
    ...made.answered.map(({ item }) => item),
    ...made.noted.map(({ item }) => item),
    ...made.done,
  ]
    .map(sessionOf)
    .filter((id): id is string => id !== undefined && id !== mine)

  return { count, away, said, lost: made.missing.length, to }
}

/**
 * Submit: everything staged (chosen options, typed answers, comments, done
 * marks) goes into the queue file each entry came from, one write to each,
 * the pane's own record of each Answer and Note line into the store, and one
 * message to this session's chat as the owner's words. Nothing is written
 * before it.
 */
async function submit($: EngineInterface): Promise<void> {
  const { value: held = NONE } = await $.state.get(stagedRef)
  const { value: typed = NO_COMMENTS } = await $.state.get(commentsRef)
  if (Object.keys(held).length === 0 && Object.keys(typed).length === 0) return
  const { value: now = EMPTY } = await $.state.get(ref)
  const places = new Map(now.items.map(item => [keyOf(item), item]))
  const { day, time } = await clock($)
  let session = 'unknown'
  try {
    session = await $.session.id()
  } catch {
    // The line still says when and by what it was written.
  }
  const by = `pane, ${day} ${time}, session ${session}`
  const mine = session === 'unknown' ? undefined : session
  const stamp = `${day} ${time}`
  // Each staged thing goes under the id it has in its own queue's file.
  const files = new Map<string, { held: OwnerStaged; typed: OwnerComments }>()
  const unplaced = new Set<string>()
  const into = (key: string) => {
    const item = places.get(key)
    if (item?.queue === undefined) {
      unplaced.add(key)

      return undefined
    }
    const slot = files.get(item.queue) ?? { held: {}, typed: {} }
    files.set(item.queue, slot)

    return { slot, id: idOf(item) }
  }
  for (const [key, what] of Object.entries(held)) {
    const to = into(key)
    if (to) to.slot.held[to.id] = what
  }
  for (const [key, list] of Object.entries(typed)) {
    const to = into(key)
    if (to) to.slot.typed[to.id] = list
  }
  let count = 0
  let away = 0
  let lost = unplaced.size
  const targets = new Set<string>()
  const said: Committed = {
    text: '',
    answered: [],
    noted: [],
    done: [],
    missing: [],
  }
  for (const [file, slot] of files) {
    const one = await write1($, file, slot.held, slot.typed, by, mine, stamp)
    count += one.count
    away += one.away
    lost += one.lost
    said.answered.push(...one.said.answered)
    said.noted.push(...one.said.noted)
    said.done.push(...one.said.done)
    for (const id of one.to) targets.add(id)
  }
  await $.state.set(stagedRef, NONE)
  await $.state.set(commentsRef, NO_COMMENTS)
  await refresh($)
  const notFound = lost > 0 ? `; ${lost} not found` : ''
  const gone = away > 0 ? `; ${away} go to the session that raised them` : ''
  $.ui.toast(`Submitted: ${count}${notFound}${gone}`)
  // A target that is not running is named, and its item is held (#161).
  const { value: known = NO_ROSTER } = await $.state.get(rosterRef)
  for (const id of targets) {
    const one = known.sessions.find(row => row.id === id)
    if (one !== undefined && isDown(one.seen))
      $.ui.toast(
        `Held for ${one.name}: it is ${one.seen}; the item waits until it runs again`,
      )
  }
  if (count - away > 0)
    void $.prompt.submit({
      text: report(said, stamp),
      asUser: true,
    })
}

/**
 * The draft file of each entry being written in the owner's text editor, by
 * item id. The files are in the mod's own folder, outside any repository.
 */
const editing = new Map<string, string>()

/** Reads again what the owner saved in each draft file. */
async function pull($: EngineInterface): Promise<void> {
  let isChanged = false
  for (const [id, path] of editing) {
    let saved: string
    try {
      saved = await $.fs.read(path)
    } catch {
      continue
    }
    if (saved === (drafts.get(id) ?? '')) continue
    drafts.set(id, saved)
    isChanged = true
  }
  if (isChanged) await update($, strokes, n => n + 1)
}

/**
 * "Write in editor": puts what was typed so far in the entry's draft file
 * and opens it in the owner's text editor, where a long text can be moved
 * around in. What is saved there is what the send buttons send.
 */
async function write($: EngineInterface, id: string): Promise<void> {
  const name = id
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .slice(-60)
    .replace(/^-+|-+$/g, '')
  const path = `${$.plugin.root.replaceAll('\\', '/')}/drafts/${name}.txt`
  try {
    await $.fs.write(path, drafts.get(id) ?? '')
  } catch {
    $.ui.toast('The draft file could not be written; type in the field')

    return
  }
  editing.set(id, path)
  await compose($, id, true)
  await update($, strokes, n => n + 1)
  // No shell reads the path: each is the system's own opener, by argv.
  const openers = /^[A-Za-z]:/.test(path)
    ? [['rundll32', 'url.dll,FileProtocolHandler', path.replaceAll('/', '\\')]]
    : [
        ['open', path],
        ['xdg-open', path],
      ]
  for (const argv of openers) {
    try {
      const { exitCode } = await $.process.run(argv, { timeoutMs: 10000 })
      if (exitCode === 0) {
        $.ui.toast('Opened in your text editor. Save there, then send here')

        return
      }
    } catch {
      // The next opener, or the path by hand.
    }
  }
  $.ui.toast('No editor opened. Copy path gives the file to open by hand')
}

/** Opens an entry's comment box, or closes it and drops what was typed. */
function compose($: EngineInterface, id: string, isOpen: boolean): Promise<void> {
  if (!isOpen) {
    drafts.delete(id)
    const path = editing.get(id)
    editing.delete(id)
    // The API removes no file: the draft is emptied.
    if (path) void $.fs.write(path, '').catch(() => undefined)
  }

  return update($, writing, list =>
    isOpen
      ? list.includes(id)
        ? list
        : [...list, id]
      : list.filter(one => one !== id),
  )
}

/**
 * "Send comment" and "Send as answer": what the owner typed is staged, as
 * one comment beside the entry's other staged things, or as the typed
 * (`other`) answer of an open decision, which replaces a chosen option. Like
 * a pressed option it waits for Submit: nothing is written and nothing is
 * said in a chat before it. The box closes and the draft is emptied.
 */
async function stageText(
  $: EngineInterface,
  item: OwnerItem,
  typed: string | undefined,
  as: 'comment' | 'answer',
): Promise<void> {
  const id = keyOf(item)
  if (typed === undefined) await pull($)
  const text = clean(typed ?? drafts.get(id) ?? '')
  if (text === '') {
    $.ui.toast('Nothing typed; nothing staged')

    return
  }
  if (as === 'answer') await stage($, item, { key: OTHER, text })
  else
    await update($, comments, held => ({
      ...held,
      [id]: [...(held[id] ?? []), text],
    }))
  await compose($, id, false)
  $.ui.toast(
    `${as === 'answer' ? 'Answer' : 'Comment'} staged; it is written on Submit`,
  )
}

/** "Change answer": the Answer line and the pane's record of it are removed. */
async function reopen($: EngineInterface, item: OwnerItem): Promise<void> {
  const file = item.queue ?? (await source($)).file
  const text = await $.fs.read(file)
  await $.fs.write(file, unanswer(text, item))
  const written = { ...(await penned($)) }
  delete written[at(item, file)]
  await $.store.set(ANSWERS, written)
  $.ui.toast(`Open again: ${item.title}`)
  await refresh($)
}

/** Puts text on the clipboard and says what was copied. */
async function copy(
  $: EngineInterface,
  text: string,
  what: string,
  surface: RenderSurface,
): Promise<void> {
  const { isCopied } = await $.ui.copy({ text, surface })
  $.ui.toast(isCopied ? `Copied: ${what}` : 'Could not copy here')
}

/**
 * The mod's own data folder, where `drafts` is: the plugin folder, inside the
 * live clone, its data folders gitignored and never committed.
 */
function dataDir($: EngineInterface): string {
  return $.plugin.root.replaceAll('\\', '/')
}

const recordPath = ($: EngineInterface, id: string) =>
  `${dataDir($)}/${SESSIONS}/${fileName(id)}.json`
const requestPath = ($: EngineInterface, id: string) =>
  `${dataDir($)}/${REQUESTS}/${fileName(id)}.json`

/** Where a tracked session writes its reset prompt (the write route, #161). */
const promptPath = ($: EngineInterface, id: string) =>
  `${dataDir($)}/${PROMPTS}/${fileName(id)}.md`

/** A file time as `YYYY-MM-DD HH:MM`. */
function dated(ms: number): string {
  const at = new Date(ms)

  return `${at.getFullYear()}-${two(at.getMonth() + 1)}-${two(at.getDate())} ${two(at.getHours())}:${two(at.getMinutes())}`
}

/** True while this session's record could not be written; said once (F7). */
let isUnsaved = false

/**
 * Writes this session's own record whole. A failed write is said once, since
 * other panes would then draw this running session as stopped; the next
 * heartbeat writes it again.
 */
async function save($: EngineInterface): Promise<void> {
  if (self === undefined) return
  try {
    await $.fs.write(recordPath($, self.id), `${JSON.stringify(self, null, 2)}\n`)
    isUnsaved = false
  } catch {
    if (!isUnsaved)
      $.ui.toast(
        "owner-queue: this session's record could not be written; other panes may show it stopped",
      )
    isUnsaved = true
  }
}

async function readRecord(
  $: EngineInterface,
  id: string,
): Promise<SessionRecord | undefined> {
  try {
    return recordOf(await $.fs.read(recordPath($, id)))
  } catch {
    return undefined
  }
}

/** The reset prompt file's time and size, or undefined when it is missing. */
async function promptStat(
  $: EngineInterface,
  id: string,
): Promise<{ mtimeMs: number; size: number } | undefined> {
  try {
    const stat = await $.fs.stat(promptPath($, id))

    return stat.kind === 'file' ? { mtimeMs: stat.mtimeMs, size: stat.size } : undefined
  } catch {
    return undefined
  }
}

/**
 * Tracks this session when it was started with a tracked role, at
 * `classic.SessionStart`, and after a `/clear` under the new id. A compaction
 * keeps the record as it was. A start or a resume takes no request older
 * than itself, and its idle time counts from its first turn in this process,
 * not from a turn before it was resumed (F5 of PR #197's review).
 */
async function enroll(
  $: EngineInterface,
  id: string | undefined,
  role: string | undefined,
  title: string | undefined,
  source: string,
): Promise<void> {
  if (!id || role === undefined) {
    self = undefined

    return
  }
  const now = await stamp($)
  const was = await readRecord($, id)
  const isCompact = source === 'compact'
  self = {
    id,
    role,
    name: title?.trim() || was?.name || role,
    // A compaction can come mid-turn: it keeps the state it found.
    state: isCompact && was?.state === 'busy' ? 'busy' : 'idle',
    turnStart: was?.turnStart ?? 0,
    turnEnd: isCompact ? (was?.turnEnd ?? 0) : 0,
    workStart: was?.workStart ?? 0,
    tokens: was?.tokens ?? 0,
    beat: now,
    ran: isCompact ? (was?.ran ?? now) : Math.max(was?.ran ?? 0, now),
    sent: was?.sent ?? {},
    ...(moved?.to === id
      ? { movedAt: moved.at }
      : was?.movedAt === undefined
        ? {}
        : { movedAt: was.movedAt }),
  }
  if (moved?.to === id) moved = undefined
  await save($)
}

/**
 * Sends the prep instruction into this session's own chat, once it is idle.
 * `ran` is the request it answers, if any. A submit the host refuses takes
 * nothing: the record is put back, and the next read tries again.
 */
async function prep(
  $: EngineInterface,
  why: string,
  now: number,
  ran?: number,
): Promise<void> {
  if (self === undefined) return
  const one = self
  const was = { sent: one.sent, ran: one.ran }
  // One prep answers every trigger until a new turn starts after it.
  one.sent = { ...one.sent, context: now, idle: now }
  if (ran !== undefined) one.ran = ran
  isQueued = true
  await save($)
  $.prompt.submit({ text: instruction(why, promptPath($, one.id)) }).catch(() => {
    one.sent = was.sent
    one.ran = was.ran
    isQueued = false
    void save($)
  })
}

/**
 * The session's own triggers and the pane's request, checked while it is
 * idle: a request newer than the last one it took, the context limit, then
 * 45 minutes idle. A fresh reset prompt stops all three.
 */
async function tend($: EngineInterface): Promise<void> {
  if (self === undefined || self.state !== 'idle' || isQueued || isTending) return
  isTending = true
  try {
    const now = await stamp($)
    const isPromptFresh = isFresh(await promptStat($, self.id), self)
    let asked: PrepRequest | undefined
    try {
      asked = JSON.parse(await $.fs.read(requestPath($, self.id))) as PrepRequest
    } catch {
      asked = undefined
    }
    if (typeof asked?.at === 'number' && asked.at > self.ran) {
      if (!isPromptFresh) {
        await prep($, WHY.request(), now, asked.at)

        return
      }
      // A fresh prompt answers the request already.
      self.ran = asked.at
      await save($)
    }
    if (isContextDue(self, isPromptFresh))
      await prep($, WHY.context(self.tokens), now)
    else if (isIdleDue(self, now, isPromptFresh)) await prep($, WHY.idle(), now)
  } finally {
    isTending = false
  }
}

/** The heartbeat: the record's time, then the triggers. */
async function beat($: EngineInterface): Promise<void> {
  if (self === undefined) return
  self.beat = await stamp($)
  await save($)
  await tend($)
}

/**
 * After a `/clear`: the reset prompt moves to the new id. The new file takes
 * the text and the old one is emptied, since the API removes no file. The
 * new id's record marks it used.
 */
async function movePrompt($: EngineInterface, from: string, to: string): Promise<void> {
  try {
    const text = await slurp($, promptPath($, from))
    if (text === undefined || text === '') return
    await $.fs.write(promptPath($, to), text)
    await $.fs.write(promptPath($, from), '')
    const at = (await promptStat($, to))?.mtimeMs ?? (await stamp($))
    if (self?.id === to) {
      self.movedAt = at
      await save($)
    } else moved = { to, at }
  } catch {
    $.ui.toast("The reset prompt was not moved to this session's new id")
  }
}

/**
 * Reads every tracked session's record and reset prompt, and what is held
 * for each one that is not running: pane-written answers and Notes it has
 * not been told, and done marks waiting in the store.
 */
async function roll(
  $: EngineInterface,
  items: OwnerItem[],
  answered: OwnerAnswers,
  wrote: OwnerNotes,
): Promise<void> {
  const now = await stamp($)
  const folder = `${dataDir($)}/${SESSIONS}`
  let entries: { name: string; kind: string }[] = []
  try {
    entries = [...(await $.fs.list(folder))]
  } catch {
    entries = []
  }
  const sessions: OwnerSession[] = []
  for (const entry of entries) {
    if (entry.kind !== 'file' || !entry.name.endsWith('.json')) continue
    const text = await slurp($, `${folder}/${entry.name}`)
    const one = text === undefined ? undefined : recordOf(text)
    if (one === undefined) continue
    const seen = seenOf(one, now)
    if (seen === undefined) continue
    const stat = await promptStat($, one.id)
    sessions.push({
      id: one.id,
      role: one.role,
      name: one.name,
      seen,
      ...(stat !== undefined && stat.size > 0
        ? {
            prompt: {
              path: promptPath($, one.id),
              at: dated(stat.mtimeMs),
              isFresh: isFresh(stat, one),
              isUsed: isUsed(stat, one),
            },
          }
        : {}),
    })
  }
  sessions.sort((a, b) => a.name.localeCompare(b.name) || a.id.localeCompare(b.id))
  const held: OwnerHeld[] = []
  for (const one of sessions.filter(row => isDown(row.seen))) {
    const delivered = await kept<OwnerAnswers>($, `delivered:${one.id}`, {})
    const noted = await kept<OwnerNotes>($, `noted:${one.id}`, {})
    const lines: string[] = []
    for (const item of items.filter(row => sessionOf(row) === one.id)) {
      const place = at(item)
      const given = answerOf(item)
      if (given !== undefined && answered[place] === given && delivered[place] !== given)
        lines.push(`Answer: ${reference(item)}`)
      const notes = notesOf(item).filter(
        line =>
          (wrote[place] ?? []).includes(line) && !(noted[place] ?? []).includes(line),
      )
      if (notes.length > 0)
        lines.push(
          `${notes.length} ${notes.length === 1 ? 'Note' : 'Notes'}: ${reference(item)}`,
        )
    }
    lines.push(...(await kept<string[]>($, `done:${one.id}`, [])))
    if (lines.length > 0)
      held.push({ id: one.id, name: one.name, seen: one.seen, lines })
  }
  const drawn: OwnerRoster = { sessions, held }
  const { value: was = NO_ROSTER } = await $.state.get(rosterRef)
  if (JSON.stringify(was) !== JSON.stringify(drawn)) await $.state.set(rosterRef, drawn)
}

/**
 * End of Day: a prep request for every running tracked session with no
 * fresh reset prompt. Each session's own mod takes it at its next read and
 * runs it once its turn has ended. One not running is drawn in red.
 */
async function endOfDay($: EngineInterface): Promise<void> {
  const { value: now = NO_ROSTER } = await $.state.get(rosterRef)
  const at = await stamp($)
  let asked = 0
  let fresh = 0
  let down = 0
  let failed = 0
  for (const one of now.sessions) {
    if (isDown(one.seen)) down++
    else if (one.prompt?.isFresh) fresh++
    else
      try {
        await $.fs.write(requestPath($, one.id), `${JSON.stringify({ at })}\n`)
        asked++
      } catch {
        failed++
      }
  }
  $.ui.toast(
    [
      `End of Day: asked ${asked}`,
      `${fresh} had a fresh prompt`,
      `${down} not running`,
      ...(failed > 0 ? [`${failed} could not be asked`] : []),
    ].join('; '),
  )
  await refresh($)
}

/** "Copy prompt": the reset prompt file's text, whole, with its line breaks. */
async function copyPrompt(
  $: EngineInterface,
  one: OwnerSession,
  surface: RenderSurface,
): Promise<void> {
  const text = await slurp($, promptPath($, one.id))
  if (text === undefined || text === '') {
    $.ui.toast(`No reset prompt for ${one.name}`)

    return
  }
  await copy($, text, `the reset prompt of ${one.name}`, surface)
}

export const register: Register = (on, settings) => {
  found = undefined
  own = undefined
  listed = queuesOf(settings?.queues)
  cleared = undefined
  self = undefined
  isQueued = false
  isTending = false
  isUnsaved = false
  moved = undefined

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'owner',
      description:
        'Show the decisions and hands-on actions waiting on the owner',
    })
    // A reload starts the module's variables over: a tracked session reads
    // its own record back. A new process is tracked at `classic.SessionStart`.
    if (self === undefined) {
      const id = await me($)
      const was = id === undefined ? undefined : await readRecord($, id)
      if (was !== undefined && (was.state === 'busy' || was.state === 'idle'))
        self = was
    }
    await refresh($)
    $.clock.every(EVERY_MS, () => void refresh($))
    $.clock.every(HEARTBEAT_MS, () => void beat($))

    return next(e)
  })

  // Tracked sessions (#161, Q3): the main thread of a session started with a
  // tracked `--agent` role. A subagent's start (`agent_id`) is not one.
  on('classic.SessionStart', async ($, e, next) => {
    if (e.agent_id === undefined)
      await enroll($, e.session_id, roleOf(e.agent_type), e.session_title, e.source)

    return next(e)
  }).catch(($, e, next) => next(e))

  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined && self !== undefined) {
      self.state = 'busy'
      self.turnStart = await stamp($)
      // The turn a prep instruction asked for re-arms nothing (F1).
      if (!isQueued) self.workStart = self.turnStart
      isQueued = false
      await save($)
    }

    return next(e)
  }).catch(($, e, next) => next(e))

  on('turn.complete', async ($, e, next) => {
    const done = await next(e)
    if (e.agentId === undefined && self !== undefined) {
      self.state = 'idle'
      self.turnEnd = await stamp($)
      await save($)
      await tend($)
    }

    return done
  }).catch(($, e, next) => next(e))

  on('session.measure', async ($, e, next) => {
    if (self !== undefined && typeof e.context.tokens === 'number') {
      self.tokens = e.context.tokens
      await save($)
      await tend($)
    }

    return next(e)
  }).catch(($, e, next) => next(e))

  // A `/clear` ends the session's id and fires no `session.start` for the new
  // one. The hook reads no id and writes no store: it keeps the ending id, and
  // the next read re-keys once `$.session.id()` answers another. Any other end
  // (a resume into an older conversation) drops it, so that id is never taken
  // for the cleared session's. A tracked session's record says `cleared` at a
  // `/clear` and `closed` at any other end.
  on('session.end', async ($, e, next) => {
    if (e.reason !== 'clear') cleared = undefined
    else if (e.sessionId)
      cleared = { from: cleared?.from ?? e.sessionId, at: await stamp($) }
    if (self !== undefined && self.id === e.sessionId) {
      self.state = e.reason === 'clear' ? 'cleared' : 'closed'
      await save($)
      if (e.reason !== 'clear') self = undefined
    }

    return next(e)
  }).catch(($, e, next) => next(e))

  on('command.run', { command: 'owner' }, async ($, e) => {
    const now = await refresh($, false)
    // `/owner show`, `/owner show a2`: the entries as text in the transcript,
    // where the mouse can select them.
    const asked = /^show\b(.*)$/i.exec((e.args ?? '').trim())
    if (asked) return { text: printed(now.items, asked[1]) }
    // `/owner id`: the id an entry's Session field names for this session.
    if (/^id$/i.test((e.args ?? '').trim()))
      return {
        text: [
          `Session: ${(await me($)) ?? 'unknown'}`,
          ...(self === undefined ? [] : [`Reset prompt: ${promptPath($, self.id)}`]),
        ].join('\n'),
      }
    await show($)

    return { text: summary(now.items) ?? 'Nothing is waiting on the owner.' }
  })

  // A session in a project with a queue is told its own id, so it can name
  // itself in the Session field of an entry it raises.
  on('prompt.compose', async ($, e, next) => {
    const made = await next(e)
    const mine = await me($)
    const { value: now = EMPTY } = await $.state.get(ref)
    const added = [
      ...(mine && now.hasFile
        ? [
            {
              id: 'owner-queue:session',
              text: `owner-queue: this session's id is ${mine}. When you write an entry in NEEDS-OWNER.md whose answer should come back to this session, add the field "- Session: ${mine}" to it. For an entry you write for another session, use that session's id.`,
              scope: 'session' as const,
            },
          ]
        : []),
      // The write route (#161): the exact file a tracked session's reset
      // prompt goes to.
      ...(self === undefined
        ? []
        : [
            {
              id: 'owner-queue:reset-prompt',
              text: `owner-queue: this session is tracked as ${self.role}. When it prepares for a clear (the session-rules skill, "A role session's clear boundary"), it writes its reset prompt, whole, to ${promptPath($, self.id)} with its file tool: it replaces the file, never appends. The owner-queue pane reads it from there.`,
              scope: 'session' as const,
            },
          ]),
    ]
    if (added.length === 0) return made

    return { sections: [...made.sections, ...added] }
  })

  on('ui.close', async ($, e, next) => {
    if (e.id === PANE) await $.state.set(shownRef, false)

    return next(e)
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const now = await read($, queue)
    if (e.props.hasSurvey || !now.hasFile) return next(e)

    const { Box, Button, Text } = $.ui.resolve(e)
    const isShown = await read($, shown)

    return (
      <Box flexDirection="row" gap={2}>
        <Text dimColor>{summary(now.items) ?? 'Owner: nothing waiting'}</Text>
        <Button
          key="toggle"
          label={isShown ? 'Hide queue' : 'Show queue'}
          onPress={() => toggle($)}
        />
      </Box>
    )
  })

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    void refresh($)

    return ran
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Input, Markdown, Link } = $.ui.resolve(e)
    const now = await read($, queue)
    const held = await read($, staged)
    const typed = await read($, comments)
    const boxes = new Set(await read($, writing))
    await read($, strokes)
    const unpenned = now.unpenned ?? {}
    const pending =
      Object.keys(held).length +
      Object.values(typed).reduce((sum, list) => sum + list.length, 0)
    const opened = new Set(await read($, open))
    const lastRead = await read($, readAt)
    const tracked = await read($, roster)
    const all = now.items.map(keyOf)
    const foreign = new Set(now.foreign ?? [])
    const isAnswered = (item: OwnerItem) => answerOf(item) !== undefined

    const row = (item: OwnerItem, at: number) => {
      const id = keyOf(item)
      const isOpen = opened.has(id)
      const about = hint(item)
      const given = answerOf(item)
      const short = reference(item, given === undefined ? at : undefined)
      const best = recommended(item)
      const mine = held[id]
      const choices =
        item.kind === 'decision' && given === undefined ? options(item) : []
      // Every code span and block is copied from under the field or the
      // step that names it; an option's spans under the options.
      const blocks = item.blocks ?? []
      const parts = layout(item, choices.length > 0 ? ['options'] : [])
      // Where each part's first code button stands among the entry's.
      const firsts = parts.map((_, at) =>
        parts.slice(0, at).reduce((sum, one) => sum + one.codes.length, 0),
      )
      const whole = `${short}\n${detail(item).replaceAll('**', '')}`
      const copyCode = (code: string, key: string) => (
        <Button
          key={key}
          label={`Copy: ${code.length > 60 ? `${code.slice(0, 57)}...` : code}`}
          onPress={press => copy($, code, code, press.surface)}
        />
      )
      const isChosen = (choice: OwnerOption) =>
        mine !== undefined && mine !== 'done' && mine.key === choice.key
      const optionCodes = choices.flatMap(choice =>
        spans(choice.text).map((code, n) =>
          copyCode(code, `code:${id}:${choice.key}:${n}`),
        ),
      )
      // A line between the groups of an open entry.
      const rule = (
        <Box marginY={1}>
          <Text dimColor>{'─'.repeat(24)}</Text>
        </Box>
      )

      return (
        <Box flexDirection="column" marginBottom={isOpen ? 1 : 0}>
          <Button
            key={`row:${id}`}
            plain
            label={`${isOpen ? 'v' : '>'} ${at + 1}. ${item.title}`}
            onPress={() =>
              update($, open, list =>
                list.includes(id)
                  ? list.filter(one => one !== id)
                  : [...list, id],
              )
            }
          />
          {given !== undefined && (
            <Box flexDirection="column" paddingLeft={4}>
              <Text>Answer: {given}</Text>
              {foreign.has(id) && (
                <Text bold>
                  Not written by the pane. Check it before anyone acts on it.
                </Text>
              )}
            </Box>
          )}
          {notesOf(item).map(one => {
            const { text, when } = said(one)
            const isMine = !(unpenned[id] ?? []).includes(one)

            return (
              <Box flexDirection="column" paddingLeft={4}>
                <Text>
                  {isMine && when ? `You said, ${when}: ${text}` : `Note: ${one}`}
                </Text>
                {!isMine && (
                  <Text bold>
                    Not written by the pane. It is not the owner's comment.
                  </Text>
                )}
              </Box>
            )
          })}
          {mine !== undefined && (
            <Box paddingLeft={4}>
              <Text color="green">
                {mine === 'done'
                  ? 'Marked done, not submitted'
                  : `Chosen, not submitted: (${mine.key}) ${mine.text}`}
              </Text>
            </Box>
          )}
          {(typed[id] ?? []).map(words => (
            <Box paddingLeft={4}>
              <Text color="green">{`Comment, not submitted: ${words}`}</Text>
            </Box>
          ))}
          {!isOpen && given === undefined && about !== '' && (
            <Box paddingLeft={4}>
              <Text dimColor>{about}</Text>
            </Box>
          )}
          {isOpen && (
            <Box flexDirection="column" paddingLeft={4}>
              {parts.length === 0 && <Text dimColor>No context was given.</Text>}
              {parts.map((part, at) => {
                const hasCopies = part.codes.length + part.blocks.length > 0

                return (
                  <Box
                    flexDirection="column"
                    paddingLeft={part.step === undefined ? 0 : 2}
                    marginBottom={hasCopies ? 1 : 0}
                  >
                    <Markdown
                      text={
                        part.step === undefined
                          ? `**${part.label}:** ${part.text}`
                          : `**${part.step}.** ${part.text}`
                      }
                    />
                    {part.codes.length > 0 && (
                      <Box flexDirection="row" flexWrap="wrap" columnGap={2}>
                        {part.codes.map((code, n) =>
                          copyCode(code, `code:${id}:${firsts[at] + n}`),
                        )}
                      </Box>
                    )}
                    {part.blocks.map(n => (
                      <Box flexDirection="column">
                        <Markdown
                          text={`Block ${n + 1}:\n\`\`\`\n${blocks[n]}\n\`\`\``}
                        />
                        <Box flexDirection="row">
                          <Button
                            key={`block:${id}:${n}`}
                            label={`Copy block ${n + 1}`}
                            onPress={press =>
                              copy($, blocks[n], `block ${n + 1}`, press.surface)
                            }
                          />
                        </Box>
                      </Box>
                    ))}
                  </Box>
                )
              })}
              {item.kind === 'decision' && given === undefined && isMalformed(item) && (
                <Box marginTop={1}>
                  <Text bold>
                    The Options line is malformed: a key appears twice. No
                    options are drawn. Fix the line in the file.
                  </Text>
                </Box>
              )}
              {choices.length > 0 && (
                <Box flexDirection="column" marginTop={1}>
                  <Text dimColor>Options:</Text>
                  {choices.map(choice => {
                    const words = `(${choice.key}) ${choice.text}`

                    return isChosen(choice) ? (
                      <Text color="green">{words}</Text>
                    ) : (
                      <Text>{words}</Text>
                    )
                  })}
                  <Box flexDirection="row" flexWrap="wrap" columnGap={2} marginTop={1}>
                    {choices.map(choice => (
                      <Button
                        key={`pick:${id}:${choice.key}`}
                        label={`Choose (${choice.key})${
                          choice.key === best ? '  [recommended]' : ''
                        }${isChosen(choice) ? '  [selected]' : ''}`}
                        onPress={() => stage($, item, choice)}
                      />
                    ))}
                  </Box>
                  {optionCodes.length > 0 && (
                    <Box flexDirection="row" flexWrap="wrap" columnGap={2}>
                      {optionCodes}
                    </Box>
                  )}
                </Box>
              )}
              {rule}
              <Box flexDirection="row" gap={2}>
                {given !== undefined && (
                  <Button
                    key={`reopen:${id}`}
                    label="Change answer"
                    onPress={() => reopen($, item)}
                  />
                )}
                <Button
                  key={`ref:${id}`}
                  label="Copy name"
                  onPress={press => copy($, short, short, press.surface)}
                />
                <Button
                  key={`copy:${id}`}
                  label="Copy all"
                  onPress={press =>
                    copy($, whole, `all of ${item.title}`, press.surface)
                  }
                />
              </Box>
              <Box flexDirection="row" gap={2} marginTop={1}>
                <Button
                  key={`post:${id}`}
                  label="Post comment"
                  onPress={() => compose($, id, !boxes.has(id))}
                />
                <Button
                  key={`edit:${id}`}
                  label="Write in editor"
                  onPress={() => write($, id)}
                />
                {given === undefined && (
                  <Button
                    key={`done:${id}`}
                    label={mine === 'done' ? 'Not done after all' : 'Mark done'}
                    onPress={() => stage($, item, 'done')}
                  />
                )}
              </Box>
              {boxes.has(id) && (
                <Box flexDirection="column">
                  {rule}
                  {editing.has(id) && (
                    <Box flexDirection="column">
                      <Text>
                        Writing in your text editor. Save the file there; what
                        is saved shows below within 5 seconds.
                      </Text>
                      <Box flexDirection="row" gap={2} marginTop={1}>
                        <Button
                          key={`path:${id}`}
                          label="Copy path"
                          onPress={press =>
                            copy(
                              $,
                              editing.get(id) ?? '',
                              'the draft file path',
                              press.surface,
                            )
                          }
                        />
                        <Button
                          key={`cancel:${id}`}
                          label="Cancel"
                          onPress={() => compose($, id, false)}
                        />
                      </Box>
                    </Box>
                  )}
                  {!editing.has(id) && (
                    <Box flexDirection="row" gap={2}>
                      <Input
                        key={`text:${id}`}
                        placeholder="Type a comment or an answer"
                        value={drafts.get(id) ?? ''}
                        submitLabel="Enter"
                        autoFocus
                        onInput={value => {
                          drafts.set(id, value)
                          void update($, strokes, n => n + 1)
                        }}
                        onSubmit={value => {
                          void stageText($, item, value, 'comment')
                        }}
                      />
                      <Button
                        key={`cancel:${id}`}
                        label="Cancel"
                        onPress={() => compose($, id, false)}
                      />
                    </Box>
                  )}
                  <Box
                    borderStyle="round"
                    borderDimColor
                    paddingX={1}
                    minHeight={5}
                    marginTop={1}
                  >
                    {drafts.get(id) ? (
                      <Text>{drafts.get(id)}</Text>
                    ) : (
                      <Text dimColor>
                        {editing.has(id)
                          ? 'Nothing saved yet.'
                          : 'What you type shows here in full.'}
                      </Text>
                    )}
                  </Box>
                  <Box flexDirection="row" gap={2} marginTop={1}>
                    <Button
                      key={`send:${id}`}
                      label="Send comment"
                      onPress={() => stageText($, item, undefined, 'comment')}
                    />
                    {item.kind === 'decision' && given === undefined && (
                      <Button
                        key={`send-answer:${id}`}
                        label="Send as answer"
                        onPress={() => stageText($, item, undefined, 'answer')}
                      />
                    )}
                  </Box>
                  <Box marginTop={1}>
                    <Text dimColor>
                      Staged as one line; nothing is written or sent until
                      Submit. A comment leaves the entry open. Enter stages a
                      comment.
                    </Text>
                  </Box>
                </Box>
              )}
            </Box>
          )}
        </Box>
      )
    }

    // An entry is numbered by its place among all queues' waiting entries, so
    // `d2` names the same entry in the pane and in `/owner show d2`.
    const part = (
      mine: OwnerItem[],
      heading: string,
      none: string,
      numbered: OwnerItem[] = mine,
    ) => (
      <Box flexDirection="column" marginBottom={1}>
        <Text bold>
          {heading} ({mine.length})
        </Text>
        {mine.length === 0 && <Text dimColor>{none}</Text>}
        {mine.map(item => row(item, numbered.indexOf(item)))}
      </Box>
    )

    const decisions = waiting(now.items, 'decision')
    const actions = waiting(now.items, 'action')
    const answered = now.items.filter(isAnswered)
    const groups = now.queues ?? []
    const isMany = groups.length > 1
    const shelves = (queue?: string) => {
      const here = (one: OwnerItem) => queue === undefined || one.queue === queue

      return (
        <Box flexDirection="column">
          {part(
            decisions.filter(here),
            'Decisions for you',
            'Nothing to decide.',
            decisions,
          )}
          {part(
            actions.filter(here),
            'Actions by your hand',
            'Nothing to do by hand.',
            actions,
          )}
          {answered.filter(here).length > 0 &&
            part(
              answered.filter(here),
              'Answered, waiting for pickup',
              '',
              answered,
            )}
        </Box>
      )
    }

    // End of Day sits in the top row, beside Refresh: Submit shows only
    // while something is staged.
    const endButton = tracked.sessions.length > 0 && (
      <Button key="end-of-day" label="End of Day" onPress={() => endOfDay($)} />
    )

    // Each tracked session (#161): its state, its reset prompt, and a copy
    // button. Stopped and closed are drawn in red, each with its own word.
    const prompts = tracked.sessions.length > 0 && (
      <Box flexDirection="column" marginBottom={1}>
        <Text bold>Reset prompts ({tracked.sessions.length})</Text>
        {tracked.sessions.map(one => {
          const isOff = isDown(one.seen)
          const prompt = one.prompt
          const word =
            prompt === undefined
              ? undefined
              : prompt.isUsed
                ? 'used'
                : prompt.isFresh
                  ? 'fresh'
                  : 'stale'
          const isMissing = isOff && !prompt?.isFresh

          return (
            <Box flexDirection="column" paddingLeft={2}>
              {isOff ? (
                <Text color="red">{`${one.name} (${one.role}): ${wordOf(one.seen)}`}</Text>
              ) : (
                <Text>{`${one.name} (${one.role}): ${wordOf(one.seen)}`}</Text>
              )}
              <Box paddingLeft={2} flexDirection="column">
                {isMissing && (
                  <Text color="red">{`no reset prompt, ${one.seen}`}</Text>
                )}
                {prompt !== undefined ? (
                  <Text dimColor>{`Reset prompt ${prompt.at}: ${word}`}</Text>
                ) : (
                  !isMissing && <Text dimColor>No reset prompt yet</Text>
                )}
                {prompt !== undefined && (
                  <Box flexDirection="row">
                    <Button
                      key={`prompt:${one.id}`}
                      label="Copy prompt"
                      onPress={press => copyPrompt($, one, press.surface)}
                    />
                  </Box>
                )}
              </Box>
            </Box>
          )
        })}
      </Box>
    )

    // What waits on a session that is not running, so none sits unseen.
    const heldList = tracked.held.length > 0 && (
      <Box flexDirection="column" marginBottom={1}>
        <Text bold color="red">
          Held for sessions not running ({tracked.held.length})
        </Text>
        {tracked.held.map(one => (
          <Box flexDirection="column" paddingLeft={2}>
            <Text color="red">{`${one.name}: ${one.seen}`}</Text>
            {one.lines.map(line => (
              <Box paddingLeft={2}>
                <Text>{line}</Text>
              </Box>
            ))}
          </Box>
        ))}
      </Box>
    )

    return (
      <Box flexDirection="column">
        <Text dimColor>owner-queue {VERSION}</Text>
        {now.isLoaded && now.isMain === false && (
          <Text bold>
            Reading this session's copy, not the main checkout's.
          </Text>
        )}
        {!now.isLoaded && <Text dimColor>Reading the queue...</Text>}
        {now.isLoaded && !now.hasFile && (
          <Box flexDirection="column">
            <Text dimColor>No queue file at {now.file ?? FILE}.</Text>
            <Box flexDirection="row" gap={2}>
              <Button key="refresh" label="Refresh" onPress={() => reread($)} />
              {endButton}
            </Box>
          </Box>
        )}
        {now.isLoaded && now.hasFile && (
          <Box flexDirection="column">
            <Box flexDirection="row" gap={2} marginBottom={1}>
              <Button key="refresh" label="Refresh" onPress={() => reread($)} />
              {endButton}
              <Button
                key="expand-all"
                label="Expand all"
                onPress={() => update($, open, () => all)}
              />
              <Button
                key="collapse-all"
                label="Collapse all"
                onPress={() => update($, open, () => [])}
              />
            </Box>
            {pending > 0 && (
              <Box flexDirection="row" gap={2} marginBottom={1}>
                <Button
                  key="submit"
                  variant="primary"
                  label={`Submit (${pending})`}
                  onPress={() => submit($)}
                />
                <Button
                  key="clear"
                  label="Clear"
                  onPress={() => {
                    void update($, staged, () => NONE)
                    void update($, comments, () => NO_COMMENTS)
                  }}
                />
                <Text color="green">
                  {pending} staged; nothing is written until Submit
                </Text>
              </Box>
            )}
            {!isMany && shelves()}
            {isMany &&
              groups.map(queue => (
                <Box flexDirection="column" marginBottom={1}>
                  <Text bold underline>
                    {queue.label}
                  </Text>
                  {queue.hasFile ? (
                    shelves(queue.file)
                  ) : (
                    <Text dimColor>No queue file at {queue.file}.</Text>
                  )}
                </Box>
              ))}
          </Box>
        )}
        {heldList}
        {prompts}
        <Text dimColor>
          Source:{' '}
          {groups.length > 0
            ? groups.map(one => one.file).join(', ')
            : (now.file ?? FILE)}
          . Last read {lastRead || 'not yet'}; it is read again every 5
          seconds. Press a row for its context.
        </Text>
        {groups
          .filter(one => one.hasFile && (one.file !== now.file || now.isMain))
          .map(one => (
            <Link
              key={`file:${one.file}`}
              href={`file:///${one.file}`}
              label={
                isMany ? `Open the ${one.label} queue file` : 'Open the queue file'
              }
            />
          ))}
        <Text dimColor>
          To select text with the mouse, type /owner show (or /owner show
          a2).
        </Text>
      </Box>
    )
  })
}
