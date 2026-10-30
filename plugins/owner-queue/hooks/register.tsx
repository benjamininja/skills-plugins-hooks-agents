import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, RenderSurface } from 'claude-code'

import type {
  OwnerAnswers,
  OwnerItem,
  OwnerNotes,
  OwnerOption,
  OwnerQueue,
  OwnerStaged,
} from '../types'
import {
  answer,
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
  message,
  note,
  notesOf,
  options,
  parse,
  recommended,
  reference,
  report,
  said,
  sessionOf,
  shown as printed,
  spans,
  summary,
  unanswer,
  waiting,
} from './parse'

const VERSION = '0.7.2'
const PANE = 'owner-queue'
const TITLE = 'Needs owner'
const FILE = '.claude/memory/NEEDS-OWNER.md'
const EVERY_MS = 5000
const ANSWERS = 'answers'
const NOTES = 'notes'

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
const writing = atom({ plugin: 'owner-queue', key: 'writing' } as const, [])
const strokes = atom({ plugin: 'owner-queue', key: 'strokes' } as const, 0)

/**
 * What is typed in each open comment box, by item id. Kept here and not in
 * the session's state, so a key press redraws nothing and a send button
 * reads the text at once.
 */
const drafts = new Map<string, string>()

type Source = { file: string; isMain: boolean }

let found: Promise<Source> | undefined

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
  })()

  return found
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
  file: string,
  items: OwnerItem[],
  own: OwnerAnswers,
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
      const at = `${file}|${idOf(item)}`

      return (
        sessionOf(item) === mine &&
        given !== undefined &&
        own[at] === given &&
        had[at] !== given
      )
    })
    const marked = await kept<string[]>($, `done:${mine}`, [])
    const told = await kept<OwnerNotes>($, `noted:${mine}`, {})
    const fresh = items.flatMap(item => {
      const at = `${file}|${idOf(item)}`
      if (sessionOf(item) !== mine) return []

      return notesOf(item)
        .filter(
          one => (wrote[at] ?? []).includes(one) && !(told[at] ?? []).includes(one),
        )
        .map(one => ({ item, at, line: one }))
    })
    if (due.length === 0 && marked.length === 0 && fresh.length === 0) return
    if (fresh.length > 0) {
      const now = { ...told }
      for (const { at, line } of fresh) now[at] = [...(now[at] ?? []), line]
      await $.store.set(`noted:${mine}`, now)
    }
    if (due.length > 0)
      await $.store.set(`delivered:${mine}`, {
        ...had,
        ...Object.fromEntries(
          due.map(item => [`${file}|${idOf(item)}`, answerOf(item) ?? '']),
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

/** Re-reads the queue file; redraws and toasts on a change. The owner opens the pane. */
async function refresh($: EngineInterface): Promise<OwnerQueue> {
  const { file, isMain } = await source($)
  let text: string | undefined
  try {
    text = await $.fs.read(file)
  } catch {
    text = undefined
  }
  const items = text === undefined ? [] : parse(text)
  await pull($)
  const own = await penned($)
  const wrote = await kept<OwnerNotes>($, NOTES, {})
  const now: OwnerQueue = {
    isLoaded: true,
    hasFile: text !== undefined,
    items,
    file,
    isMain,
    foreign: items
      .filter(item => {
        const given = answerOf(item)

        return given !== undefined && own[`${file}|${idOf(item)}`] !== given
      })
      .map(idOf),
    unpenned: Object.fromEntries(
      items
        .map(item => {
          const mine = wrote[`${file}|${idOf(item)}`] ?? []

          return [
            idOf(item),
            notesOf(item).filter(one => !mine.includes(one)),
          ] as const
        })
        .filter(([, lines]) => lines.length > 0),
    ),
  }
  $.ui.status(summary(now.items))
  await deliver($, file, items, own, wrote)
  await $.state.set(readAtRef, (await clock($)).time)
  // What was staged for an entry that has left the list is dropped.
  const { value: held = NONE } = await $.state.get(stagedRef)
  const live = new Set(
    items.filter(item => answerOf(item) === undefined).map(idOf),
  )
  const still = Object.fromEntries(
    Object.entries(held).filter(([id]) => live.has(id)),
  )
  if (Object.keys(still).length !== Object.keys(held).length)
    await $.state.set(stagedRef, still)
  const { value: was = EMPTY } = await $.state.get(ref)
  if (JSON.stringify(was) === JSON.stringify(now)) return now

  await $.state.set(ref, now)

  const known = new Set(was.items.map(idOf))
  const fresh = now.items.filter(item => !known.has(idOf(item)))
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
  const id = idOf(item)
  const isSame = (was: OwnerOption | 'done' | undefined) =>
    was !== undefined &&
    (was === 'done' || what === 'done' ? was === what : was.key === what.key)

  return update($, staged, held => {
    const { [id]: was, ...rest } = held

    return isSame(was) ? rest : { ...rest, [id]: what }
  })
}

/**
 * Submit: everything staged goes into the queue file in one write, the
 * pane's own record of each Answer line into the store, and one message to
 * this session's chat as the owner's words. Nothing is written before it.
 */
async function submit($: EngineInterface): Promise<void> {
  const { value: held = NONE } = await $.state.get(stagedRef)
  if (Object.keys(held).length === 0) return
  const { file } = await source($)
  const { day, time } = await clock($)
  let session = 'unknown'
  try {
    session = await $.session.id()
  } catch {
    // The line still says when and by what it was written.
  }
  const text = await $.fs.read(file)
  const made = commit(
    text,
    held,
    chosen =>
      `(${chosen.key}) ${chosen.text} | pane, ${day} ${time}, session ${session}`,
  )
  const count = made.answered.length + made.done.length
  const mine = session === 'unknown' ? undefined : session
  const said = here(made, mine)
  const away = count - said.answered.length - said.done.length
  if (count > 0) {
    // This session's own entries are said by Submit below, not carried again.
    const self = made.answered.filter(
      ({ item }) => mine !== undefined && sessionOf(item) === mine,
    )
    if (mine !== undefined && self.length > 0)
      await $.store.set(`delivered:${mine}`, {
        ...(await kept<OwnerAnswers>($, `delivered:${mine}`, {})),
        ...Object.fromEntries(
          self.map(({ item, line }) => [`${file}|${idOf(item)}`, line]),
        ),
      })
    // An item marked done has left the file: its raiser is told by the store.
    for (const item of made.done) {
      const to = sessionOf(item)
      if (to === undefined || to === mine) continue
      await $.store.set(`done:${to}`, [
        ...(await kept<string[]>($, `done:${to}`, [])),
        `${reference(item)}, marked done ${day} ${time}`,
      ])
    }
    await $.fs.write(file, made.text)
    if (made.answered.length > 0)
      await $.store.set(ANSWERS, {
        ...(await penned($)),
        ...Object.fromEntries(
          made.answered.map(({ item, line }) => [`${file}|${idOf(item)}`, line]),
        ),
      })
  }
  await $.state.set(stagedRef, NONE)
  await refresh($)
  const lost =
    made.missing.length > 0 ? `; ${made.missing.length} not found` : ''
  const gone = away > 0 ? `; ${away} go to the session that raised them` : ''
  $.ui.toast(`Submitted: ${count}${lost}${gone}`)
  if (count - away > 0)
    void $.prompt.submit({
      text: report(said, `${day} ${time}`),
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
    .replace(/^-+|-+$/g, '')
    .slice(0, 60)
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
 * "Post comment": what the owner typed goes out at once, without Submit.
 * As a comment it is a Note line of the entry, which stays open; as an
 * answer it is the Answer line of an open decision. The pane records the
 * line in its store, and the text is said in this session's chat when the
 * entry names it or names no session; else the raising session carries it.
 */
async function post(
  $: EngineInterface,
  item: OwnerItem,
  typed: string | undefined,
  as: 'comment' | 'answer',
): Promise<void> {
  const id = idOf(item)
  if (typed === undefined) await pull($)
  const text = clean(typed ?? drafts.get(id) ?? '')
  if (text === '') {
    $.ui.toast('Nothing typed; nothing sent')

    return
  }
  const { file } = await source($)
  const { day, time } = await clock($)
  const mine = await me($)
  const before = await $.fs.read(file)
  const now = parse(before).find(one => idOf(one) === id)
  const isAnswer = as === 'answer'
  if (now && isAnswer && (now.kind !== 'decision' || answerOf(now) !== undefined)) {
    $.ui.toast('Already answered; nothing sent. Change answer opens it again')
    await refresh($)

    return
  }
  const line = `${isAnswer ? '(other) ' : ''}${text} | pane, ${day} ${time}, session ${mine ?? 'unknown'}`
  const after = !now
    ? before
    : isAnswer
      ? answer(before, now, line)
      : note(before, now, line)
  if (!now || after === before) {
    $.ui.toast('That entry is no longer open in the file; nothing sent')
    await refresh($)

    return
  }
  const at = `${file}|${id}`
  const to = sessionOf(now)
  const isHere = to === undefined || to === mine
  // The pane's own record goes first, so no reader sees a line it cannot place.
  if (isAnswer) {
    await $.store.set(ANSWERS, { ...(await penned($)), [at]: line })
    if (mine !== undefined && to === mine)
      await $.store.set(`delivered:${mine}`, {
        ...(await kept<OwnerAnswers>($, `delivered:${mine}`, {})),
        [at]: line,
      })
  } else {
    const wrote = await kept<OwnerNotes>($, NOTES, {})
    await $.store.set(NOTES, { ...wrote, [at]: [...(wrote[at] ?? []), line] })
    if (mine !== undefined && to === mine) {
      const told = await kept<OwnerNotes>($, `noted:${mine}`, {})
      await $.store.set(`noted:${mine}`, {
        ...told,
        [at]: [...(told[at] ?? []), line],
      })
    }
  }
  await $.fs.write(file, after)
  await compose($, id, false)
  await refresh($)
  $.ui.toast(
    `${isAnswer ? 'Answer' : 'Comment'} sent${
      isHere ? '' : '; it goes to the session that raised the entry'
    }`,
  )
  if (isHere)
    void $.prompt.submit({
      text: isAnswer
        ? message(now, { key: 'other', text }, `${day} ${time}`)
        : comment(now, text, false, `${day} ${time}`),
      asUser: true,
    })
}

/** "Change answer": the Answer line and the pane's record of it are removed. */
async function reopen($: EngineInterface, item: OwnerItem): Promise<void> {
  const { file } = await source($)
  const text = await $.fs.read(file)
  await $.fs.write(file, unanswer(text, item))
  const own = { ...(await penned($)) }
  delete own[`${file}|${idOf(item)}`]
  await $.store.set(ANSWERS, own)
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

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'owner',
      description:
        'Show the decisions and hands-on actions waiting on the owner',
    })
    await refresh($)
    $.clock.every(EVERY_MS, () => void refresh($))

    return next(e)
  })

  on('command.run', { command: 'owner' }, async ($, e) => {
    const now = await refresh($)
    // `/owner show`, `/owner show a2`: the entries as text in the transcript,
    // where the mouse can select them.
    const asked = /^show\b(.*)$/i.exec((e.args ?? '').trim())
    if (asked) return { text: printed(now.items, asked[1]) }
    // `/owner id`: the id an entry's Session field names for this session.
    if (/^id$/i.test((e.args ?? '').trim()))
      return { text: `Session: ${(await me($)) ?? 'unknown'}` }
    await show($)

    return { text: summary(now.items) ?? 'Nothing is waiting on the owner.' }
  })

  // A session in a project with a queue is told its own id, so it can name
  // itself in the Session field of an entry it raises.
  on('prompt.compose', async ($, e, next) => {
    const made = await next(e)
    const mine = await me($)
    const { value: now = EMPTY } = await $.state.get(ref)
    if (!mine || !now.hasFile) return made

    return {
      sections: [
        ...made.sections,
        {
          id: 'owner-queue:session',
          text: `owner-queue: this session's id is ${mine}. When you write an entry in NEEDS-OWNER.md whose answer should come back to this session, add the field "- Session: ${mine}" to it. For an entry you write for another session, use that session's id.`,
          scope: 'session' as const,
        },
      ],
    }
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
    const boxes = new Set(await read($, writing))
    await read($, strokes)
    const unpenned = now.unpenned ?? {}
    const pending = Object.keys(held).length
    const opened = new Set(await read($, open))
    const lastRead = await read($, readAt)
    const all = now.items.map(idOf)
    const foreign = new Set(now.foreign ?? [])
    const isAnswered = (item: OwnerItem) => answerOf(item) !== undefined

    const row = (item: OwnerItem, at: number) => {
      const id = idOf(item)
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
                          void post($, item, value, 'comment')
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
                      onPress={() => post($, item, undefined, 'comment')}
                    />
                    {item.kind === 'decision' && given === undefined && (
                      <Button
                        key={`send-answer:${id}`}
                        label="Send as answer"
                        onPress={() => post($, item, undefined, 'answer')}
                      />
                    )}
                  </Box>
                  <Box marginTop={1}>
                    <Text dimColor>
                      Sent at once, as one line. A comment leaves the entry
                      open. Enter sends a comment.
                    </Text>
                  </Box>
                </Box>
              )}
            </Box>
          )}
        </Box>
      )
    }

    const part = (mine: OwnerItem[], heading: string, none: string) => (
      <Box flexDirection="column" marginBottom={1}>
        <Text bold>
          {heading} ({mine.length})
        </Text>
        {mine.length === 0 && <Text dimColor>{none}</Text>}
        {mine.map(row)}
      </Box>
    )

    const answered = now.items.filter(isAnswered)

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
            <Button key="refresh" label="Refresh" onPress={() => reread($)} />
          </Box>
        )}
        {now.isLoaded && now.hasFile && (
          <Box flexDirection="column">
            <Box flexDirection="row" gap={2} marginBottom={1}>
              <Button key="refresh" label="Refresh" onPress={() => reread($)} />
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
                  onPress={() => update($, staged, () => NONE)}
                />
                <Text color="green">
                  {pending} staged; nothing is written until Submit
                </Text>
              </Box>
            )}
            {part(
              waiting(now.items, 'decision'),
              'Decisions for you',
              'Nothing to decide.',
            )}
            {part(
              waiting(now.items, 'action'),
              'Actions by your hand',
              'Nothing to do by hand.',
            )}
            {answered.length > 0 &&
              part(answered, 'Answered, waiting for pickup', '')}
          </Box>
        )}
        <Text dimColor>
          Source: {now.file ?? FILE}. Last read {lastRead || 'not yet'}; it is
          read again every 5 seconds. Press a row for its context.
        </Text>
        {now.isMain && now.file && (
          <Link href={`file:///${now.file}`} label="Open the queue file" />
        )}
        <Text dimColor>
          To select text with the mouse, type /owner show (or /owner show
          a2).
        </Text>
      </Box>
    )
  })
}
