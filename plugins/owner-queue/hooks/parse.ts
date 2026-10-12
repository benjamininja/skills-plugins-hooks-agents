import type { OwnerItem, OwnerOption, OwnerStaged } from '../types'

/**
 * The queue file's format:
 *
 *   ## Decisions            (any heading starting "Decision")
 *   ### [ ] Title           ("[x]" marks it done; a done item is not listed)
 *   - Ticket: #130
 *   - Context: why it is asked, with the evidence
 *   - Options: A; B
 *   - Options: (a) one; (b) two      (the keyed form, also read)
 *   - Recommended: A, because ...
 *   - Blocks: what waits behind it
 *   - Raised: 2026-10-11, session name
 *   - Answer: (a) one | pane, ...    (written by the pane alone)
 *
 *   ## Actions              (any heading starting "Action")
 *   ### [ ] Title
 *   - Steps: what to do by hand
 *   ...
 *
 * A line under a field that is not a new "- Label:" continues that field.
 * Text under a title before any field is its Context.
 */
const FENCE = '```'

export function parse(text: string): OwnerItem[] {
  const items: OwnerItem[] = []
  let kind: OwnerItem['kind'] | undefined
  let item: OwnerItem | undefined
  let isDone = false
  // The lines of a fenced block being read, or undefined outside one.
  let fence: string[] | undefined

  const close = () => {
    if (item && !isDone) items.push(item)
    item = undefined
    isDone = false
    fence = undefined
  }

  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trimEnd()
    if (item && line.trim().startsWith(FENCE)) {
      if (fence === undefined) {
        fence = []
        continue
      }
      const indent = Math.min(
        ...fence
          .filter(one => one.trim() !== '')
          .map(one => one.length - one.trimStart().length),
      )
      const block = fence
        .map(one => one.slice(Number.isFinite(indent) ? indent : 0))
        .join('\n')
      fence = undefined
      if (block.trim() === '') continue
      item.blocks = [...(item.blocks ?? []), block]
      const mark = `(block ${item.blocks.length})`
      const held = item.fields[item.fields.length - 1]
      if (held) held.value = `${held.value} ${mark}`.trim()
      else item.fields.push({ label: 'Context', value: mark })
      continue
    }
    if (fence !== undefined) {
      fence.push(line)
      continue
    }
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

/** What still waits on the owner; an answered decision waits on a session. */
export function summary(items: OwnerItem[]): string | undefined {
  const answered = items.filter(item => answerOf(item) !== undefined).length
  const decisions = count(items, 'decision') - answered
  const actions = count(items, 'action')
  if (decisions + actions + answered === 0) return undefined
  const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? '' : 's'}`
  const tail = answered > 0 ? `, ${answered} answered` : ''

  return `Owner: ${plural(decisions, 'decision')}, ${plural(actions, 'action')}${tail}`
}

export function idOf(item: OwnerItem): string {
  return `${item.kind}:${item.title}`
}

/** One line for a collapsed row: its ticket and what it blocks. */
export function hint(item: OwnerItem): string {
  const ticket = pick(item, 'ticket')
  const blocks = pick(item, 'blocks')

  return [ticket, blocks && `blocks: ${blocks}`].filter(Boolean).join(' | ')
}

const pick = (item: OwnerItem, label: string): string | undefined =>
  item.fields.find(field => field.label.toLowerCase() === label)?.value

/** An expanded row's context, as markdown; its answer is drawn apart. */
export function detail(item: OwnerItem, without: string[] = []): string {
  const left = ['answer', ...without]
  const fields = item.fields.filter(
    field => !left.includes(field.label.toLowerCase()),
  )
  if (fields.length === 0) return '_No context was given._'
  const blocks = (item.blocks ?? []).map(
    (block, at) => `\nBlock ${at + 1}:\n${FENCE}\n${block}\n${FENCE}`,
  )

  return [
    fields.map(field => `- **${field.label}:** ${field.value}`).join('\n'),
    ...blocks,
  ].join('\n')
}

/** A short way to name the item in chat: its place, title and ticket. */
export function reference(item: OwnerItem, at?: number): string {
  const kind = item.kind === 'decision' ? 'Decision' : 'Action'
  const place = at === undefined ? '' : ` ${at + 1}`
  const ticket = pick(item, 'ticket')

  return `${kind}${place}: ${item.title}${ticket ? ` (${ticket})` : ''}`
}

/** The chat message a pressed option sends: the entry and the choice. */
export function message(item: OwnerItem, chosen: OwnerOption): string {
  const line = (label: string) => {
    const value = pick(item, label.toLowerCase())

    return value ? [`${label}: ${value}`] : []
  }

  return [
    `Owner's answer, given by a button in the owner-queue pane.`,
    `Decision: ${item.title}`,
    ...line('Ticket'),
    ...line('Raised'),
    ...line('Options'),
    `Answer: (${chosen.key}) ${chosen.text}`,
    `It is recorded as the Answer line of this entry in NEEDS-OWNER.md.`,
  ].join('\n')
}

/**
 * The choices of a decision, from its Options field. Written
 * `(a) one; (b) two`, the keys are the letters; written `One; Two`, the
 * keys are a, b, c by place.
 */
export function options(item: OwnerItem): OwnerOption[] {
  const value = pick(item, 'options')
  if (!value) return []
  const clean = (text: string) => text.trim().replace(/[;,.]+$/, '').trim()

  const keyed = [...value.matchAll(/\(([A-Za-z0-9])\)\s*/g)]
  if (keyed.length > 0 && keyed[0].index === 0) {
    return keyed
      .map((match, at) => ({
        key: match[1].toLowerCase(),
        text: clean(
          value.slice(
            (match.index ?? 0) + match[0].length,
            keyed[at + 1]?.index ?? value.length,
          ),
        ),
      }))
      .filter(option => option.text !== '')
  }

  return value
    .split(';')
    .map(clean)
    .filter(text => text !== '')
    .map((text, at) => ({ key: String.fromCharCode(97 + at), text }))
}

/** The key of the option the Recommended field names, if it names one. */
export function recommended(item: OwnerItem): string | undefined {
  const value = pick(item, 'recommended')?.trim()
  if (!value) return undefined
  const all = options(item)
  const keyed = /^\(?([A-Za-z0-9])\)/.exec(value)?.[1].toLowerCase()
  if (keyed && all.some(option => option.key === keyed)) return keyed
  const lower = value.toLowerCase()

  return [...all]
    .sort((one, other) => other.text.length - one.text.length)
    .find(option => lower.startsWith(option.text.toLowerCase()))?.key
}

/** The decision's recorded answer, if it has one. */
export function answerOf(item: OwnerItem): string | undefined {
  return pick(item, 'answer')
}

const ANSWER = /^\s*[-*]\s+\**Answer\**:/i

/** The first and one-past-last line of the open item's entry, title included. */
function span(lines: string[], item: OwnerItem): [number, number] | undefined {
  let kind: OwnerItem['kind'] | undefined
  let from = -1
  for (let at = 0; at < lines.length; at++) {
    const line = lines[at].replace(/\r$/, '')
    const section = /^##\s+(.+)$/.exec(line)
    const title = /^###\s+(?:\[ \]\s*)?(.+)$/.exec(line)
    if (from >= 0 && (section || /^###\s/.test(line))) return [from, at]
    if (section) {
      const name = section[1].trim().toLowerCase()
      kind = name.startsWith('decision')
        ? 'decision'
        : name.startsWith('action')
          ? 'action'
          : undefined
    } else if (title && kind === item.kind && title[1].trim() === item.title) {
      from = at
    }
  }

  return from >= 0 ? [from, lines.length] : undefined
}

/** The file without the item's Answer line. */
export function unanswer(text: string, item: OwnerItem): string {
  const lines = text.split('\n')
  const found = span(lines, item)
  if (!found) return text
  const [from, to] = found

  return lines
    .filter((line, at) => at <= from || at >= to || !ANSWER.test(line))
    .join('\n')
}

/** The file with `- Answer: <line>` as the last field of the item's entry. */
export function answer(text: string, item: OwnerItem, line: string): string {
  const lines = unanswer(text, item).split('\n')
  const found = span(lines, item)
  if (!found) return text
  let last = found[1] - 1
  while (last > found[0] && lines[last].trim() === '') last--
  const isCrlf = lines[found[0]].endsWith('\r')
  // The file's last line has no line break after it; give it its own first.
  if (last === lines.length - 1 && isCrlf && !lines[last].endsWith('\r'))
    lines[last] = `${lines[last]}\r`
  const closed = last < lines.length - 1
  lines.splice(last + 1, 0, `- Answer: ${line}${isCrlf && closed ? '\r' : ''}`)

  return lines.join('\n')
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

/** Each `code` span of the item's fields, once, in the order written. */
export function codes(item: OwnerItem): string[] {
  return spans(
    item.fields
      .filter(field => field.label.toLowerCase() !== 'answer')
      .map(field => field.value)
      .join('\n'),
  )
}

/** Each `code` span of a text, once, in the order written. */
export function spans(text: string): string[] {
  const found = [...text.matchAll(/`([^`]+)`/g)]
    .map(match => match[1].trim())
    .filter(code => code !== '')

  return [...new Set(found)]
}

/** The items still waiting on the owner, as the pane numbers them. */
export function waiting(items: OwnerItem[], kind: OwnerItem['kind']): OwnerItem[] {
  return items.filter(
    item => item.kind === kind && answerOf(item) === undefined,
  )
}

/**
 * Entries as markdown for the transcript, where the mouse can select them.
 * `which` is empty for all, `d2` or `a1` for one, `2` for the second of each.
 */
export function shown(items: OwnerItem[], which = ''): string {
  const asked = /^([da])?\s*(\d+)$/.exec(which.trim().toLowerCase())
  if (!asked) return which.trim() === '' ? toMarkdown(items) : `No entry "${which.trim()}". Use d1, a2 or a number.`
  const at = Number(asked[2]) - 1
  const kinds: OwnerItem['kind'][] =
    asked[1] === 'd' ? ['decision'] : asked[1] === 'a' ? ['action'] : ['decision', 'action']
  const found = kinds.flatMap(kind => {
    const item = waiting(items, kind)[at]

    return item ? [`**${reference(item, at)}**\n\n${detail(item)}`] : []
  })

  return found.length > 0 ? found.join('\n\n') : `No entry ${which.trim()} is waiting.`
}

export type Committed = {
  text: string
  answered: { item: OwnerItem; chosen: OwnerOption; line: string }[]
  done: OwnerItem[]
  /** The ids staged whose entry is no longer open in the file. */
  missing: string[]
}

/**
 * The file with everything staged applied in one pass: an Answer line per
 * chosen option (`line` words it) and a ticked box per item marked done.
 */
export function commit(
  text: string,
  staged: OwnerStaged,
  line: (chosen: OwnerOption) => string,
): Committed {
  const out: Committed = { text, answered: [], done: [], missing: [] }
  for (const [id, what] of Object.entries(staged)) {
    const item = parse(out.text).find(one => idOf(one) === id)
    const next = !item
      ? out.text
      : what === 'done'
        ? tick(out.text, item)
        : answer(out.text, item, line(what))
    if (!item || next === out.text) {
      out.missing.push(id)
      continue
    }
    out.text = next
    if (what === 'done') out.done.push(item)
    else out.answered.push({ item, chosen: what, line: line(what) })
  }

  return out
}

/** The one chat message a Submit sends: every answer, every item marked done. */
export function report(done: Committed): string {
  return [
    ...done.answered.map(({ item, chosen }) => message(item, chosen)),
    ...(done.done.length > 0
      ? [
          [
            'Marked done by the owner in the owner-queue pane:',
            ...done.done.map(item => `- ${reference(item)}`),
          ].join('\n'),
        ]
      : []),
  ].join('\n\n')
}
