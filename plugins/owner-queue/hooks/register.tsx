import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, RenderSurface } from 'claude-code'

import type { OwnerItem, OwnerQueue } from '../types'
import { detail, hint, idOf, parse, summary, tick } from './parse'

const PANE = 'owner-queue'
const TITLE = 'Needs owner'
const FILE = '.claude/memory/NEEDS-OWNER.md'
const EVERY_MS = 5000

const ref = { plugin: 'owner-queue', key: 'queue' } as const
const EMPTY: OwnerQueue = { isLoaded: false, hasFile: false, items: [] }
const queue = atom(ref, EMPTY)
const open = atom({ plugin: 'owner-queue', key: 'open' } as const, [])
const shownRef = { plugin: 'owner-queue', key: 'shown' } as const
const shown = atom(shownRef, false)

/** Puts the pane on screen and records that it is there. */
async function show($: EngineInterface): Promise<void> {
  await $.state.set(shownRef, true)
  await $.ui.open({ id: PANE, title: TITLE })
}

/** Takes the pane off screen; the `ui.close` hook records it. */
async function hide($: EngineInterface): Promise<void> {
  await $.ui.close({ id: PANE })
}

/** Re-reads the queue file; redraws, toasts and opens the pane on a change. */
async function refresh($: EngineInterface): Promise<OwnerQueue> {
  let text: string | undefined
  try {
    text = await $.fs.read(FILE)
  } catch {
    text = undefined
  }
  const now: OwnerQueue = {
    isLoaded: true,
    hasFile: text !== undefined,
    items: text === undefined ? [] : parse(text),
  }
  $.ui.status(summary(now.items))
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

/** Ticks the item's box in the queue file, which takes it off the list. */
async function markDone($: EngineInterface, item: OwnerItem): Promise<void> {
  const text = await $.fs.read(FILE)
  await $.fs.write(FILE, tick(text, item))
  $.ui.toast(`Done: ${item.title}`)
  await refresh($)
}

/** Puts the item's title and context on the clipboard as plain text. */
async function copy(
  $: EngineInterface,
  item: OwnerItem,
  surface: RenderSurface,
): Promise<void> {
  const text = `${item.title}\n${detail(item).replaceAll('**', '')}`
  const { isCopied } = await $.ui.copy({ text, surface })
  $.ui.toast(isCopied ? `Copied: ${item.title}` : 'Could not copy here')
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
          onPress={() => (isShown ? hide($) : show($))}
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
    const all = now.items.map(idOf)

    const row = (item: OwnerItem, at: number) => {
      const id = idOf(item)
      const isOpen = opened.has(id)
      const about = hint(item)

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
          {!isOpen && about !== '' && (
            <Box paddingLeft={4}>
              <Text dimColor>{about}</Text>
            </Box>
          )}
          {isOpen && (
            <Box flexDirection="column" paddingLeft={4}>
              <Markdown text={detail(item)} />
              <Box flexDirection="row" gap={2}>
                <Button
                  key={`copy:${id}`}
                  label="Copy"
                  onPress={press => copy($, item, press.surface)}
                />
                <Button
                  key={`done:${id}`}
                  label="Mark done"
                  onPress={() => markDone($, item)}
                />
              </Box>
            </Box>
          )}
        </Box>
      )
    }

    const part = (kind: OwnerItem['kind'], heading: string, none: string) => {
      const mine = now.items.filter(item => item.kind === kind)

      return (
        <Box flexDirection="column" marginBottom={1}>
          <Text bold>
            {heading} ({mine.length})
          </Text>
          {mine.length === 0 && <Text dimColor>{none}</Text>}
          {mine.map(row)}
        </Box>
      )
    }

    return (
      <Box flexDirection="column">
        {!now.isLoaded && <Text dimColor>Reading the queue...</Text>}
        {now.isLoaded && !now.hasFile && (
          <Text dimColor>This project has no {FILE}.</Text>
        )}
        {now.isLoaded && now.hasFile && (
          <Box flexDirection="column">
            <Box flexDirection="row" gap={2} marginBottom={1}>
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
            {part('decision', 'Decisions for you', 'Nothing to decide.')}
            {part('action', 'Actions by your hand', 'Nothing to do by hand.')}
          </Box>
        )}
        <Text dimColor>
          Source: {FILE}. Press a row for its context. Mark done takes it off
          the list.
        </Text>
      </Box>
    )
  })
}
