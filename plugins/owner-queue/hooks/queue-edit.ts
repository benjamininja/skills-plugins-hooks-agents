import { parse } from './parse.ts'

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
const PANE_LINE = /^\s*[-*]\s+\**(?:Answer|Note)\**:/i
const NOTE_LINE = /^\s*[-*]\s+\**Note\**:/i

const bare = (line: string) => line.replace(/\r$/, '')
const isPane = (line: string) => PANE_LINE.test(bare(line))

const kindOf = (name: string): Kind | undefined => {
  const lower = name.trim().toLowerCase()

  return lower.startsWith('decision')
    ? 'decision'
    : lower.startsWith('action')
      ? 'action'
      : undefined
}

/**
 * The entries and section headings of a queue, read as parse() reads them:
 * a `###` or `##` line inside a fenced block ends nothing.
 */
function scan(lines: string[]): {
  entries: Entry[]
  sections: { kind: Kind; at: number }[]
} {
  const entries: Entry[] = []
  const sections: { kind: Kind; at: number }[] = []
  let kind: Kind | undefined
  let open: Entry | undefined
  let isFenced = false
  const close = (at: number) => {
    if (open) entries.push({ ...open, to: at })
    open = undefined
  }
  lines.forEach((raw, at) => {
    const line = bare(raw).trimEnd()
    if (open && line.trim().startsWith(FENCE)) {
      isFenced = !isFenced

      return
    }
    if (isFenced) return
    const section = /^##\s+(.+)$/.exec(line)
    if (section) {
      close(at)
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

  return { entries, sections }
}

/**
 * The lines left when each range is cut out. A cut that reaches the end of the
 * file also drops the blank lines before it, and the file keeps a final line
 * break only if it had one.
 */
function cut(lines: string[], ranges: [number, number][]): string[] {
  const isCut = (at: number) => ranges.some(([from, to]) => at >= from && at < to)
  const left = lines.filter((_, at) => !isCut(at))
  if (!ranges.some(([, to]) => to >= lines.length)) return left
  while (left.length > 0 && left[left.length - 1].trim() === '') left.pop()
  if (lines[lines.length - 1] === '') left.push('')

  return left
}

/** Throws unless every Answer and Note line outside the cut ranges is as it was. */
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
  const had = parse(before.join('\n')).length
  if (parse(after.join('\n')).length !== had + openChange)
    throw new Error('stopped: the open entries would not be as expected')
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
  const heading = kind === 'decision' ? '## Decisions' : '## Actions'
  const check = scan([heading, ...own])
  const made = parse([heading, ...own].join('\n'))
  if (check.sections.length !== 1 || check.entries.length !== 1 || made.length !== 1)
    throw new Error('the block must be exactly one entry, with no "##" heading')

  const lines = text.split('\n')
  const now = scan(lines)
  const where = now.sections.filter(section => section.kind === kind)
  if (where.length !== 1)
    throw new Error(`the file needs exactly one ${heading} section, found ${where.length}`)
  if (now.entries.some(one => one.kind === kind && one.title === check.entries[0].title))
    throw new Error(`an entry titled "${check.entries[0].title}" is already in ${heading}`)

  const eol = lines[0]?.endsWith('\r') ? '\r' : ''
  const added = own.map(line => `${line}${eol}`)
  const at = where[0].at
  const next = lines[at + 1]
  let first: number
  if (next === undefined) {
    lines.splice(at + 1, 0, eol, ...added, eol)
    first = at + 2
  } else if (next.trim() === '') {
    lines.splice(at + 2, 0, ...added, eol)
    first = at + 2
  } else {
    lines.splice(at + 1, 0, ...added, eol)
    first = at + 1
  }
  guard(text.split('\n'), lines, [], 1)

  return { text: lines.join('\n'), line: first + 1 }
}

export type Removed = { text: string; line: number; count: number }

/**
 * The file without the one entry of that title. An entry that holds a Note
 * line is refused unless `withNotes`: then its Notes leave with it.
 */
export function remove(text: string, title: string, withNotes = false): Removed {
  const lines = text.split('\n')
  const found = scan(lines).entries.filter(one => one.title === title.trim())
  if (found.length === 0) throw new Error(`no entry is titled "${title}"`)
  if (found.length > 1)
    throw new Error(`the title "${title}" is not unique (${found.length} entries)`)
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
  const ticked = scan(lines).entries.filter(one => one.kind === 'action' && one.isDone)
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
  '  remove --title <title> [--with-notes]     one entry; refuses one that holds a Note line',
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
    if (command === 'add') {
      const flags = flagsOf(args, ['--block-file'])
      const kind = flags.rest[0]
      const blockFile = flags.values['--block-file']?.[0]
      if ((kind !== 'decision' && kind !== 'action') || flags.rest.length !== 1 || !blockFile)
        throw new Error(USAGE)
      const done = add(text, kind, io.read(blockFile))
      io.write(file, done.text)
      io.print(`inserted at line ${done.line}`)
    } else if (command === 'remove') {
      const flags = flagsOf(args, ['--title'])
      const title = flags.values['--title']?.[0]
      if (!title || flags.rest.length > 0) throw new Error(USAGE)
      const done = remove(text, title, flags.isNotes)
      io.write(file, done.text)
      io.print(`removed ${done.count} lines at ${done.line}`)
    } else if (command === 'prune') {
      const flags = flagsOf(args, ['--keep'])
      if (flags.rest.length > 0) throw new Error(USAGE)
      const done = prune(text, flags.values['--keep'] ?? [], flags.isNotes)
      if (done.text !== text) io.write(file, done.text)
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
