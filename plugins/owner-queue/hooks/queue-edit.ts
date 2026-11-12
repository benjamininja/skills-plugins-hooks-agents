import { answerOf, notesOf, parse } from './parse.ts'

export type Kind = 'decision' | 'action'

type Entry = {
  kind: Kind
  title: string
  isDone: boolean
  /** The title line, and one past the entry's last line (the next heading). */
  from: number
  to: number
}

const FENCE = '```'
const PANE_LINE = /^\s*[-*]\s+\**\s*(?:Answer|Note)\s*\**\s*:/i
const NOTE_LINE = /^\s*[-*]\s+\**\s*Note\s*\**\s*:/i

const bare = (line: string) => line.replace(/\r$/, '')
const isPane = (line: string) => PANE_LINE.test(bare(line))
const count = (text: string, pattern: RegExp) => (text.match(pattern) ?? []).length

const kindOf = (name: string): Kind | undefined => {
  const lower = name.trim().toLowerCase()

  return lower.startsWith('decision')
    ? 'decision'
    : lower.startsWith('action')
      ? 'action'
      : undefined
}

/**
 * The entries and headings of a queue, read as parse() reads them: a `###` or
 * `##` line inside a fenced block ends nothing. `unclosed` is the line of a
 * fence that is never closed (parse() reads everything after it as inside it).
 */
function scan(lines: string[]): {
  entries: Entry[]
  sections: { kind: Kind; at: number }[]
  headings: number[]
  unclosed: number | undefined
} {
  const entries: Entry[] = []
  const sections: { kind: Kind; at: number }[] = []
  const headings: number[] = []
  let kind: Kind | undefined
  let open: Entry | undefined
  let isFenced = false
  let fenceAt = -1
  const close = (at: number) => {
    if (open) entries.push({ ...open, to: at })
    open = undefined
  }
  lines.forEach((raw, at) => {
    const line = bare(raw).trimEnd()
    if (open && line.trim().startsWith(FENCE)) {
      isFenced = !isFenced
      fenceAt = isFenced ? at : -1

      return
    }
    if (isFenced) return
    const section = /^##\s+(.+)$/.exec(line)
    if (section) {
      close(at)
      headings.push(at)
      kind = kindOf(section[1])
      if (kind) sections.push({ kind, at })

      return
    }
    const title = /^###\s+(?:\[( |x|X)\]\s*)?(.+)$/.exec(line)
    if (title) {
      close(at)
      if (kind)
        open = {
          kind,
          title: title[2].trim(),
          isDone: (title[1] ?? ' ').toLowerCase() === 'x',
          from: at,
          to: at,
        }
    }
  })
  close(lines.length)

  return { entries, sections, headings, unclosed: isFenced ? fenceAt : undefined }
}

/** scan() of a queue file; a queue with a fence that is never closed is refused. */
function scanFile(lines: string[]): ReturnType<typeof scan> {
  const found = scan(lines)
  if (found.unclosed !== undefined)
    throw new Error(
      `the code fence opened at line ${found.unclosed + 1} is never closed: close it by hand first`,
    )

  return found
}

/**
 * The lines left when each range is cut out. A cut that reaches the end of the
 * file also drops the blank lines before it. The file keeps a final line break
 * only if it had one: without one, the last line left has no line end at all.
 */
function cut(lines: string[], ranges: [number, number][]): string[] {
  const isCut = (at: number) => ranges.some(([from, to]) => at >= from && at < to)
  const left = lines.filter((_, at) => !isCut(at))
  if (!ranges.some(([, to]) => to >= lines.length)) return left
  while (left.length > 0 && left[left.length - 1].trim() === '') left.pop()
  if (lines[lines.length - 1] === '') left.push('')
  else if (left.length > 0) left[left.length - 1] = bare(left[left.length - 1])

  return left
}

/**
 * Throws unless every Answer and Note line outside the cut ranges is as it was,
 * the open entries are as expected, and no line end of a CRLF file was broken.
 */
function guard(
  before: string[],
  after: string[],
  cuts: [number, number][],
  openChange: number,
) {
  const expected = before.filter(
    (line, at) =>
      isPane(line) && !cuts.some(([from, to]) => at >= from && at < to),
  )
  const found = after.filter(isPane)
  if (expected.length !== found.length || expected.some((l, i) => l !== found[i]))
    throw new Error('stopped: an Answer or Note line would change')
  const was = before.join('\n')
  const now = after.join('\n')
  if (parse(now).length !== parse(was).length + openChange)
    throw new Error('stopped: the open entries would not be as expected')
  if (
    count(now, /\r(?!\n)/g) > count(was, /\r(?!\n)/g) ||
    (was.includes('\r\n') && count(now, /(?<!\r)\n/g) > count(was, /(?<!\r)\n/g))
  )
    throw new Error('stopped: a line end of the file would be broken')
}

export type Added = { text: string; line: number }

/** The file with one new open entry at the top of the kind's section. */
export function add(text: string, kind: Kind, block: string): Added {
  const own = block.replaceAll('\r\n', '\n').replace(/^\n+|\s+$/g, '').split('\n')
  if (!/^###\s+\[ \]\s*\S/.test(own[0]))
    throw new Error('the block must start with "### [ ] Title"')
  if (own.some(line => isPane(line)))
    throw new Error('the block holds an Answer or Note line: only the pane writes those')
  if (own.filter(line => line.trim().startsWith(FENCE)).length % 2 !== 0)
    throw new Error('the block opens a code fence it does not close')
  let isFenced = false
  for (const line of own) {
    if (line.trim().startsWith(FENCE)) isFenced = !isFenced
    else if (!isFenced && /^##\s/.test(line))
      throw new Error('the block must be exactly one entry, with no "##" heading')
  }
  const heading = kind === 'decision' ? '## Decisions' : '## Actions'
  const check = scan([heading, ...own])
  const made = parse([heading, ...own].join('\n'))
  if (check.entries.length !== 1 || made.length !== 1)
    throw new Error('the block must be exactly one entry, with no "##" heading')
  if (answerOf(made[0]) !== undefined || notesOf(made[0]).length > 0)
    throw new Error('the block holds an Answer or Note line: only the pane writes those')

  const lines = text.split('\n')
  const now = scanFile(lines)
  const where = now.sections.filter(section => section.kind === kind)
  if (where.length !== 1)
    throw new Error(`the file needs exactly one ${heading} section, found ${where.length}`)
  if (now.entries.some(one => one.kind === kind && one.title === check.entries[0].title))
    throw new Error(`an entry titled "${check.entries[0].title}" is already in ${heading}`)

  const hasEnd = lines.length > 1 && lines[lines.length - 1] === ''
  if (hasEnd) lines.pop()
  const at = where[0].at
  const stop = now.headings.find(one => one > at) ?? lines.length
  const firstEntry = now.entries.find(one => one.from > at && one.from < stop)?.from ?? stop
  if (lines.slice(at + 1, firstEntry).some(line => line.trim() !== ''))
    throw new Error(
      `${heading} holds text between its heading and its first entry: move it by hand first`,
    )

  const eol = lines[0]?.endsWith('\r') ? '\r' : ''
  const added = own.map(line => `${line}${eol}`)
  const next = lines[at + 1]
  let first: number
  let isLast = false
  if (next === undefined) {
    if (!hasEnd) lines[at] = `${lines[at]}${eol}`
    lines.splice(at + 1, 0, eol, ...added)
    first = at + 2
    isLast = true
  } else if (next.trim() === '') {
    isLast = at + 2 >= lines.length
    lines.splice(at + 2, 0, ...added, ...(isLast ? [] : [eol]))
    first = at + 2
  } else {
    lines.splice(at + 1, 0, ...added, eol)
    first = at + 1
  }
  if (isLast && !hasEnd) lines[lines.length - 1] = bare(lines[lines.length - 1])
  if (hasEnd) lines.push('')
  guard(text.split('\n'), lines, [], 1)

  return { text: lines.join('\n'), line: first + 1 }
}

export type Removed = { text: string; line: number; count: number }

/**
 * The file without the one entry of that title (of that kind, when `kind` is
 * given, for a title used in both sections). An entry that holds a Note line
 * is refused unless `withNotes`: then its Notes leave with it.
 */
export function remove(
  text: string,
  title: string,
  withNotes = false,
  kind?: Kind,
): Removed {
  const lines = text.split('\n')
  const found = scanFile(lines).entries.filter(
    one => one.title === title.trim() && (kind === undefined || one.kind === kind),
  )
  if (found.length === 0) throw new Error(`no entry is titled "${title}"`)
  if (found.length > 1)
    throw new Error(
      `the title "${title}" is not unique (${found.length} entries): name one with --kind decision or --kind action`,
    )
  const one = found[0]
  const range: [number, number] = [one.from, one.to]
  if (!withNotes && lines.slice(one.from, one.to).some(line => NOTE_LINE.test(bare(line))))
    throw new Error(
      'the entry holds a Note line: raise it in the chat, or remove it with --with-notes',
    )
  const left = cut(lines, [range])
  guard(lines, left, [range], one.isDone ? 0 : -1)

  return { text: left.join('\n'), line: one.from + 1, count: one.to - one.from }
}

export type Pruned = {
  text: string
  removed: string[]
  kept: string[]
  /** Ticked entries left in place because they hold a Note line. */
  held: string[]
}

/**
 * The file without its ticked Actions, except those whose title holds one of
 * `keep`. A ticked Action that holds a Note line stays unless `withNotes`.
 */
export function prune(text: string, keep: string[] = [], withNotes = false): Pruned {
  const lines = text.split('\n')
  const ticked = scanFile(lines).entries.filter(
    one => one.kind === 'action' && one.isDone,
  )
  const out: Pruned = { text, removed: [], kept: [], held: [] }
  const ranges: [number, number][] = []
  for (const one of ticked) {
    if (keep.some(word => word !== '' && one.title.includes(word))) {
      out.kept.push(one.title)
    } else if (
      !withNotes &&
      lines.slice(one.from, one.to).some(line => NOTE_LINE.test(bare(line)))
    ) {
      out.held.push(one.title)
    } else {
      ranges.push([one.from, one.to])
      out.removed.push(one.title)
    }
  }
  const left = cut(lines, ranges)
  guard(lines, left, ranges, 0)
  out.text = left.join('\n')

  return out
}

export type Io = {
  read: (path: string) => string
  write: (path: string, text: string) => void
  print: (line: string) => void
}

export const USAGE = [
  'usage: queue-cli.ts <queue file> <command>',
  '  add decision|action --block-file <file>   one new open entry, at the top of its section',
  '  remove --title <title> [--kind decision|action] [--with-notes]',
  '                                            one entry; refuses one that holds a Note line',
  '  prune [--keep <text>]... [--with-notes]   ticked Actions, keeping titles that hold <text>',
].join('\n')

type Flags = { values: Record<string, string[]>; isNotes: boolean; rest: string[] }

function flagsOf(args: string[], names: string[]): Flags {
  const out: Flags = { values: {}, isNotes: false, rest: [] }
  for (let at = 0; at < args.length; at++) {
    const arg = args[at]
    if (arg === '--with-notes') out.isNotes = true
    else if (names.includes(arg)) {
      const value = args[++at]
      if (value === undefined) throw new Error(`${arg} needs a value`)
      out.values[arg] = [...(out.values[arg] ?? []), value]
    } else if (arg.startsWith('--')) throw new Error(`unknown flag ${arg}`)
    else out.rest.push(arg)
  }

  return out
}

/** Runs one command on a queue file. Returns the exit code; writes only on success. */
export function run(argv: string[], io: Io): number {
  const [file, command, ...args] = argv
  try {
    if (!file || !command) throw new Error(USAGE)
    const text = io.read(file)
    const save = (next: string) => {
      if (io.read(file) !== text)
        throw new Error(
          'the file changed while it was being edited: nothing was written, run the command again',
        )
      io.write(file, next)
    }
    if (command === 'add') {
      const flags = flagsOf(args, ['--block-file'])
      const kind = flags.rest[0]
      const blockFile = flags.values['--block-file']?.[0]
      if ((kind !== 'decision' && kind !== 'action') || flags.rest.length !== 1 || !blockFile)
        throw new Error(USAGE)
      const done = add(text, kind, io.read(blockFile))
      save(done.text)
      io.print(`inserted at line ${done.line}`)
    } else if (command === 'remove') {
      const flags = flagsOf(args, ['--title', '--kind'])
      const title = flags.values['--title']?.[0]
      const kind = flags.values['--kind']?.[0]
      if (!title || flags.rest.length > 0) throw new Error(USAGE)
      if (kind !== undefined && kind !== 'decision' && kind !== 'action') throw new Error(USAGE)
      const done = remove(text, title, flags.isNotes, kind as Kind | undefined)
      save(done.text)
      io.print(`removed ${done.count} lines at ${done.line}`)
    } else if (command === 'prune') {
      const flags = flagsOf(args, ['--keep'])
      if (flags.rest.length > 0) throw new Error(USAGE)
      const done = prune(text, flags.values['--keep'] ?? [], flags.isNotes)
      if (done.text !== text) save(done.text)
      io.print(
        `removed ${done.removed.length} kept ${JSON.stringify(done.kept)} held for a Note ${JSON.stringify(done.held)}`,
      )
    } else throw new Error(USAGE)

    return 0
  } catch (error) {
    io.print(`refused: ${error instanceof Error ? error.message : String(error)}`)

    return 1
  }
}
