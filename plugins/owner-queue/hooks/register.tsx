import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, RenderSurface } from 'claude-code'

import type {
  OwnerAnswers,
  OwnerItem,
  OwnerOption,
  OwnerQueue,
  OwnerStaged,
} from '../types'
import {
  answerOf,
  codes,
  commit,
  detail,
  hint,
  idOf,
  options,
  parse,
  recommended,
  reference,
  report,
  shown as printed,
  spans,
  summary,
  unanswer,
  waiting,
} from './parse'

const VERSION = '0.4.1'
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
const stagedRef = { plugin: 'owner-queue', key: 'staged' } as const
const NONE: OwnerStaged = {}
const staged = atom(stagedRef, NONE)

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
  const { file, isMain } = await source($)
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
    isMain,
    foreign: items
      .filter(item => {
        const given = answerOf(item)

        return given !== undefined && own[`${file}|${idOf(item)}`] !== given
      })
      .map(idOf),
  }
  $.ui.status(summary(now.items))
  await $.state.set(readAtRef, (await clock($)).time)
  // What was staged for an entry that has left the list is dropped.
  const { value: held = NONE } = await $.state.get(stagedRef)
  const live = new Set(
    items.filter(item => answerOf(item) === undefined).map(idOf),
  )
  const kept = Object.fromEntries(
    Object.entries(held).filter(([id]) => live.has(id)),
  )
  if (Object.keys(kept).length !== Object.keys(held).length)
    await $.state.set(stagedRef, kept)
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
  if (count > 0) {
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
  $.ui.toast(`Submitted: ${count}${lost}`)
  if (count > 0) void $.prompt.submit({ text: report(made), asUser: true })
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
  const { file } = await source($)
  const text = await $.fs.read(file)
  await $.fs.write(file, unanswer(text, item))
  const own = { ...(await penned($)) }
  delete own[`${file}|${idOf(item)}`]
  await $.store.set(ANSWERS, own)
  $.ui.toast(`Open again: ${item.title}`)
  await refresh($)
}

/**
 * Prints an entry into the transcript as a notice, where the mouse can
 * select it. The model does not receive it.
 */
function print($: EngineInterface, text: string): void {
  $.ui.log(text)
  $.ui.toast('Printed in the chat')
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
    const { Box, Text, Button, Markdown, Link } = $.ui.resolve(e)
    const now = await read($, queue)
    const held = await read($, staged)
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
      // An option's own code spans are copied beside it, the rest up top.
      const beside = new Set(choices.flatMap(choice => spans(choice.text)))
      const above = codes(item).filter(code => !beside.has(code))
      const whole = `${short}\n${detail(item).replaceAll('**', '')}`
      const copyCode = (code: string, key: string) => (
        <Button
          key={key}
          label={`Copy: ${code.length > 60 ? `${code.slice(0, 57)}...` : code}`}
          onPress={press => copy($, code, code, press.surface)}
        />
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
              <Markdown
                text={detail(item, choices.length > 0 ? ['options'] : [])}
              />
              {above.length > 0 && (
                <Box flexDirection="column" marginTop={1}>
                  {above.map((code, n) => copyCode(code, `code:${id}:${n}`))}
                </Box>
              )}
              {choices.length > 0 && (
                <Box flexDirection="column" marginTop={1}>
                  <Text dimColor>Options:</Text>
                  {choices.map(choice => {
                    const isMine =
                      mine !== undefined &&
                      mine !== 'done' &&
                      mine.key === choice.key
                    const words = `(${choice.key}) ${choice.text}`

                    return (
                      <Box flexDirection="column" marginTop={1}>
                        {isMine ? (
                          <Text color="green">{words}</Text>
                        ) : (
                          <Text>{words}</Text>
                        )}
                        <Box flexDirection="row" gap={2}>
                          <Button
                            key={`pick:${id}:${choice.key}`}
                            label={`Choose (${choice.key})${
                              choice.key === best ? '  [recommended]' : ''
                            }${isMine ? '  [selected]' : ''}`}
                            onPress={() => stage($, item, choice)}
                          />
                          {spans(choice.text).map((code, n) =>
                            copyCode(code, `code:${id}:${choice.key}:${n}`),
                          )}
                        </Box>
                      </Box>
                    )
                  })}
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
                    copy($, whole, `all of ${item.title}`, press.surface)
                  }
                />
                <Button
                  key={`print:${id}`}
                  label="Print in chat"
                  onPress={() => print($, whole)}
                />
              </Box>
              {given === undefined && (
                <Box marginTop={1}>
                  <Button
                    key={`done:${id}`}
                    label={mine === 'done' ? 'Not done after all' : 'Mark done'}
                    onPress={() => stage($, item, 'done')}
                  />
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
          To select text with the mouse, press Print in chat on an entry, or
          type /owner show (or /owner show a2).
        </Text>
      </Box>
    )
  })
}
