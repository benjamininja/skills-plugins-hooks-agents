import type { OwnerItem } from '../types'

/**
 * The queue file's format:
 *
 *   ## Decisions            (any heading starting "Decision")
 *   ### [ ] Title           ("[x]" marks it done; a done item is not listed)
 *   - Ticket: #130
 *   - Context: why it is asked, with the evidence
 *   - Options: A; B
 *   - Recommended: A, because ...
 *   - Blocks: what waits behind it
 *   - Raised: 2026-10-11, session name
 *
 *   ## Actions              (any heading starting "Action")
 *   ### [ ] Title
 *   - Steps: what to do by hand
 *   ...
 *
 * A line under a field that is not a new "- Label:" continues that field.
 * Text under a title before any field is its Context.
 */
export function parse(text: string): OwnerItem[] {
  const items: OwnerItem[] = []
  let kind: OwnerItem['kind'] | undefined
  let item: OwnerItem | undefined
  let isDone = false

  const close = () => {
    if (item && !isDone) items.push(item)
    item = undefined
    isDone = false
  }

  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trimEnd()
    const section = /^##\s+(.+)$/.exec(line)
    if (section) {
      close()
      const name = section[1].trim().toLowerCase()
      kind = name.startsWith('decision')
        ? 'decision'
        : name.startsWith('action')
          ? 'action'
          : undefined
      continue
    }
    const title = /^###\s+(?:\[( |x|X)\]\s*)?(.+)$/.exec(line)
    if (title) {
      close()
      if (kind) {
        item = { kind, title: title[2].trim(), fields: [] }
        isDone = (title[1] ?? ' ').toLowerCase() === 'x'
      }
      continue
    }
    if (!item) continue
    const body = line.trim()
    if (body === '') continue
    const field = /^[-*]\s+\**([A-Za-z][A-Za-z ]{0,24}?)\**:\**\s*(.*)$/.exec(body)
    if (field) {
      item.fields.push({ label: field[1].trim(), value: field[2].trim() })
      continue
    }
    const last = item.fields[item.fields.length - 1]
    if (last) last.value = `${last.value} ${body}`.trim()
    else item.fields.push({ label: 'Context', value: body })
  }
  close()

  return items
}

export function count(items: OwnerItem[], kind: OwnerItem['kind']): number {
  return items.filter(item => item.kind === kind).length
}

export function summary(items: OwnerItem[]): string | undefined {
  const decisions = count(items, 'decision')
  const actions = count(items, 'action')
  if (decisions + actions === 0) return undefined
  const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? '' : 's'}`

  return `Owner: ${plural(decisions, 'decision')}, ${plural(actions, 'action')}`
}

export function idOf(item: OwnerItem): string {
  return `${item.kind}:${item.title}`
}

/** One line for a collapsed row: its ticket and what it blocks. */
export function hint(item: OwnerItem): string {
  const pick = (label: string) =>
    item.fields.find(field => field.label.toLowerCase() === label)?.value
  const ticket = pick('ticket')
  const blocks = pick('blocks')

  return [ticket, blocks && `blocks: ${blocks}`].filter(Boolean).join(' | ')
}

/** An expanded row's context, as markdown. */
export function detail(item: OwnerItem): string {
  if (item.fields.length === 0) return '_No context was given._'

  return item.fields
    .map(field => `- **${field.label}:** ${field.value}`)
    .join('\n')
}

/** The file with the item's box ticked, so it is no longer listed. */
export function tick(text: string, item: OwnerItem): string {
  let kind: OwnerItem['kind'] | undefined
  let isTicked = false

  return text
    .split('\n')
    .map(raw => {
      const line = raw.replace(/\r$/, '')
      const section = /^##\s+(.+)$/.exec(line)
      if (section) {
        const name = section[1].trim().toLowerCase()
        kind = name.startsWith('decision')
          ? 'decision'
          : name.startsWith('action')
            ? 'action'
            : undefined

        return raw
      }
      const title = /^###\s+(?:\[ \]\s*)?(.+)$/.exec(line)
      if (
        isTicked ||
        !title ||
        kind !== item.kind ||
        title[1].trim() !== item.title
      )
        return raw
      isTicked = true

      return `### [x] ${item.title}${raw.endsWith('\r') ? '\r' : ''}`
    })
    .join('\n')
}

/** The whole queue as markdown, for a text answer. */
export function toMarkdown(items: OwnerItem[]): string {
  const part = (kind: OwnerItem['kind'], heading: string, empty: string) => {
    const mine = items.filter(item => item.kind === kind)
    const lines = [`## ${heading} (${mine.length})`, '']
    if (mine.length === 0) lines.push(`_${empty}_`, '')
    mine.forEach((item, at) => {
      lines.push(`**${at + 1}. ${item.title}**`, '')
      for (const field of item.fields) {
        lines.push(`- **${field.label}:** ${field.value}`)
      }
      lines.push('')
    })

    return lines.join('\n')
  }

  return [
    part('decision', 'Decisions for you', 'Nothing to decide.'),
    part('action', 'Actions by your hand', 'Nothing to do by hand.'),
  ].join('\n')
}
