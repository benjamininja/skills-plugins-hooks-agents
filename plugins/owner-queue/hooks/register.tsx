import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, RenderSurface } from 'claude-code'

import type {
  OwnerAnswers,
  OwnerItem,
  OwnerOption,
  OwnerQueue,
} from '../types'
import {
  answer,
  answerOf,
  detail,
  hint,
  idOf,
  message,
  options,
  parse,
  recommended,
  reference,
  summary,
  tick,
  unanswer,
} from './parse'

const PANE = 'owner-queue'
const TITLE = 'Needs owner'
const FILE = '.claude/memory/NEEDS-OWNER.md'
const EVERY_MS = 5000
const ANSWERS = 'answers'

const ref = { plugin: 'owner-queue', key: 'queue' } as const
const EMPTY: OwnerQueue = { isLoaded: false, hasFile: false, items: [] }
const queue = atom(ref, EMPTY)
const open = atom({ plugin: 'owner-queue', key: 'open' } as const, [])
const shownRef = { plugin: 'owner-queue', key: 'shown' } as const
const shown = atom(shownRef, false)
const readAtRef = { plugin: 'owner-queue', key: 'readAt' } as const
const readAt = atom(readAtRef, '')

let found: Promise<string> | undefined

/**
 * The queue file every session reads: the main checkout's, so a session in a
 * worktree shows the same queue. A worktree's `.git` is a file naming the
 * main checkout; elsewhere git is asked; failing both, the session's own copy.
 */
function source($: EngineInterface): Promise<string> {
  found ??= (async () => {
    try {
      const link = /^gitdir:\s*(.+?)[\\/]\.git[\\/]worktrees[\\/]/m.exec(
        await $.fs.read('.git'),
      )
      if (link) return `${link[1].replaceAll('\\', '/')}/${FILE}`
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
        return `${common.slice(0, -'/.git'.length)}/${FILE}`
    } catch {
      // Not a repository, or a surface that runs no process.
    }

    return FILE
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

/** Re-reads the queue file; redraws, toasts and opens the pane on a change. */
async function refresh($: EngineInterface): Promise<OwnerQueue> {
  const file = await source($)
  let text: string | undefined
  try {
    text = await $.fs.read(file)
  } catch {
    text = undefined
  }
  const items = text === undefined ? [] : parse(text)
  const own = await penned($)
  const now: OwnerQueue = {
    isLoaded: true,
    hasFile: text !== undefined,
    items,
    file,
    foreign: items
      .filter(item => {
        const given = answerOf(item)

        return given !== undefined && own[`${file}|${idOf(item)}`] !== given
      })
      .map(idOf),
  }
  $.ui.status(summary(now.items))
  await $.state.set(readAtRef, (await clock($)).time)
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
    void show($)
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

/** Ticks the item's box in the queue file, which takes it off the list. */
async function markDone($: EngineInterface, item: OwnerItem): Promise<void> {
  const file = await source($)
  const text = await $.fs.read(file)
  await $.fs.write(file, tick(text, item))
  $.ui.toast(`Done: ${item.title}`)
  await refresh($)
}

/**
 * A pressed option: the Answer line goes into the entry, the pane's own
 * record of it into the store, and the answer to this session's chat as the
 * owner's words.
 */
async function choose(
  $: EngineInterface,
  item: OwnerItem,
  chosen: OwnerOption,
): Promise<void> {
  const file = await source($)
  const { day, time } = await clock($)
  let session = 'unknown'
  try {
    session = await $.session.id()
  } catch {
    // The line still says when and by what it was written.
  }
  const line = `(${chosen.key}) ${chosen.text} | pane, ${day} ${time}, session ${session}`
  const text = await $.fs.read(file)
  const next = answer(text, item, line)
  if (next === text) {
    $.ui.toast(`Could not find the entry: ${item.title}`)

    return
  }
  await $.fs.write(file, next)
  await $.store.set(ANSWERS, {
    ...(await penned($)),
    [`${file}|${idOf(item)}`]: line,
  })
  await refresh($)
  $.ui.toast(`Answered: ${item.title}`)
  void $.prompt.submit({ text: message(item, chosen), asUser: true })
}

/** "Other...": a draft in the prompt box for an answer no option covers. */
async function other($: EngineInterface, item: OwnerItem): Promise<void> {
  const { isFilled } = await $.prompt.fill({
    text: `My answer to "${reference(item)}": `,
    mode: 'append',
  })
  $.ui.toast(
    isFilled
      ? 'Type your answer in the prompt box and send it'
      : 'No prompt box here; answer in chat',
  )
}

/** "Change answer": the Answer line and the pane's record of it are removed. */
async function reopen($: EngineInterface, item: OwnerItem): Promise<void> {
  const file = await source($)
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

  on('command.run', { command: 'owner' }, async $ => {
    const now = await refresh($)
    await show($)

    return { text: summary(now.items) ?? 'Nothing is waiting on the owner.' }
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
    const { Box, Text, Button, Markdown } = $.ui.resolve(e)
    const now = await read($, queue)
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
      const choices =
        item.kind === 'decision' && given === undefined ? options(item) : []

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
          {!isOpen && given === undefined && about !== '' && (
            <Box paddingLeft={4}>
              <Text dimColor>{about}</Text>
            </Box>
          )}
          {isOpen && (
            <Box flexDirection="column" paddingLeft={4}>
              <Markdown text={detail(item)} />
              {choices.length > 0 && (
                <Box flexDirection="column" marginTop={1}>
                  <Text dimColor>Answer with a button:</Text>
                  {choices.map(choice => (
                    <Button
                      key={`pick:${id}:${choice.key}`}
                      label={`(${choice.key}) ${choice.text}${
                        choice.key === best ? '  [recommended]' : ''
                      }`}
                      onPress={() => choose($, item, choice)}
                    />
                  ))}
                </Box>
              )}
              <Box flexDirection="row" gap={2} marginTop={1}>
                {item.kind === 'decision' && given === undefined && (
                  <Button
                    key={`other:${id}`}
                    label="Other..."
                    onPress={() => other($, item)}
                  />
                )}
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
                    copy(
                      $,
                      `${short}\n${detail(item).replaceAll('**', '')}`,
                      `all of ${item.title}`,
                      press.surface,
                    )
                  }
                />
                {given === undefined && (
                  <Button
                    key={`done:${id}`}
                    label="Mark done"
                    onPress={() => markDone($, item)}
                  />
                )}
              </Box>
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

    const waiting = (kind: OwnerItem['kind']) =>
      now.items.filter(item => item.kind === kind && !isAnswered(item))
    const answered = now.items.filter(isAnswered)

    return (
      <Box flexDirection="column">
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
            {part(waiting('decision'), 'Decisions for you', 'Nothing to decide.')}
            {part(
              waiting('action'),
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
      </Box>
    )
  })
}
