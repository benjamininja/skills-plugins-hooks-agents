import { expect, test } from 'claude-code/testing'

import { parse } from './parse.ts'
import { add, prune, remove, run } from './queue-edit.ts'
import type { Io } from './queue-edit.ts'

const F = '```'

const FILE = `# NEEDS-OWNER

Intro.

## Decisions

### [ ] Open decision
- Ticket: #1
- Options: (a) one; (b) two
- Note: first words | pane, 2026-11-12 08:00, session s1

### [x] Ticked decision
- Context: done
- Answer: (a) one | pane, 2026-11-12 08:01, session s1

### [ ] Answered decision
- Options: (a) one; (b) two
- Answer: (b) two | pane, 2026-11-12 08:02, session s1

## Actions

### [ ] Open action
- Steps: do it

### [x] Done action
- Steps: done

### [x] Done action with a note
- Steps: done
- Note: still wanted | pane, 2026-11-12 08:03, session s1

### [x] Keep me action
- Steps: run
${F}
### [ ] inside a fence
${F}

### [x] Last action
- Steps: end

## Notes

Footer.
`

const SMALL = `## Decisions

### [ ] Old
- Context: x

## Actions

### [ ] A
- Steps: s
`

const BLOCK = `### [ ] New
- Context: y
`

const paneLines = (text: string) =>
  text.split('\n').filter(line => /^- (?:Answer|Note):/.test(line))

const titles = (text: string) => parse(text).map(item => item.title)

const failure = (fn: () => unknown): string => {
  try {
    fn()
  } catch (error) {
    return error instanceof Error ? error.message : String(error)
  }

  return ''
}

test('add puts one open entry at the top of its section, as the old script did', () => {
  const done = add(SMALL, 'decision', BLOCK)

  expect(done.text).toBe(
    '## Decisions\n\n### [ ] New\n- Context: y\n\n### [ ] Old\n- Context: x\n\n' +
      '## Actions\n\n### [ ] A\n- Steps: s\n',
  )
  expect(done.line).toBe(3)
  expect(titles(done.text)).toEqual(['New', 'Old', 'A'])
  expect(parse(done.text)[0].kind).toBe('decision')
  expect(titles(add(SMALL, 'action', '### [ ] B\n- Steps: b').text)).toEqual([
    'Old',
    'B',
    'A',
  ])
})

test('add then remove gives the file back, byte for byte', () => {
  const added = add(FILE, 'action', BLOCK).text
  expect(added).not.toBe(FILE)
  expect(remove(added, 'New').text).toBe(FILE)
  const crlf = FILE.replaceAll('\n', '\r\n')
  expect(remove(add(crlf, 'decision', BLOCK).text, 'New').text).toBe(crlf)
})

test('add never changes an Answer or Note line, and keeps CRLF', () => {
  expect(paneLines(add(FILE, 'decision', BLOCK).text)).toEqual(paneLines(FILE))
  const crlf = add(SMALL.replaceAll('\n', '\r\n'), 'action', BLOCK).text
  expect(crlf.replaceAll('\r\n', '')).not.toContain('\n')
  expect(titles(crlf)).toEqual(['Old', 'New', 'A'])
})

test('add reaches a heading with no blank line after it, or none at all', () => {
  const tight = add('## Actions\n### [ ] A\n- Steps: s\n', 'action', BLOCK)
  expect(tight.text).toBe(
    '## Actions\n### [ ] New\n- Context: y\n\n### [ ] A\n- Steps: s\n',
  )
  expect(tight.line).toBe(2)
  expect(add('## Actions', 'action', BLOCK).text).toBe(
    '## Actions\n\n### [ ] New\n- Context: y\n',
  )
  expect(add('## Actions\n', 'action', BLOCK).text).toBe(
    '## Actions\n\n### [ ] New\n- Context: y\n',
  )
})

test('add refuses a block that is not one plain open entry', () => {
  const bad = (block: string, kind: 'decision' | 'action' = 'decision') =>
    failure(() => add(SMALL, kind, block))

  expect(bad('### New\n- Context: y')).toContain('### [ ] Title')
  expect(bad('### [x] New\n- Context: y')).toContain('### [ ] Title')
  expect(bad('')).toContain('### [ ] Title')
  expect(bad('### [ ] New\n- Answer: (a) x | pane')).toContain('Answer or Note')
  expect(bad('### [ ] New\n- Note: said | pane')).toContain('Answer or Note')
  expect(bad('### [ ] New\n- Context: y\n## Actions')).toContain('exactly one entry')
  expect(bad('### [ ] New\n- Context: y\n\n### [ ] Two\n- Context: z')).toContain(
    'exactly one entry',
  )
  expect(bad(`### [ ] New\n- Steps: x\n${F}\ncode`)).toContain('does not close')
  expect(bad('### [ ] Old\n- Context: y')).toContain('already in')
  expect(failure(() => add('# nothing here\n', 'action', BLOCK))).toContain(
    'exactly one ## Actions',
  )
})

test('add allows a fenced block that holds heading-like lines', () => {
  const block = `### [ ] New\n- Steps: run\n${F}\n## Actions\n### [ ] x\n${F}`
  const done = add(SMALL, 'action', block)

  expect(titles(done.text)).toEqual(['Old', 'New', 'A'])
  expect(remove(done.text, 'New').text).toBe(SMALL)
})

test('remove takes one entry and nothing around it', () => {
  const done = remove(FILE, 'Open action')

  expect(titles(done.text)).toEqual(['Open decision', 'Answered decision'])
  expect(done.text).not.toContain('Open action')
  expect(done.text).toContain('### [x] Done action\n')
  expect(done.line).toBe(22)
  expect(done.count).toBe(3)
  expect(paneLines(done.text)).toEqual(paneLines(FILE))
})

test('remove takes an answered entry, whole, without the flag', () => {
  const done = remove(FILE, 'Answered decision')

  expect(done.text).not.toContain('Answered decision')
  expect(paneLines(done.text)).toEqual(
    paneLines(FILE).filter(line => !line.startsWith('- Answer: (b) two')),
  )
})

test('remove refuses an entry that holds a Note, and keeps it unless flagged', () => {
  expect(failure(() => remove(FILE, 'Open decision'))).toContain('holds a Note')
  const flagged = remove(FILE, 'Open decision', true)

  expect(flagged.text).not.toContain('Open decision')
  expect(flagged.text).not.toContain('first words')
  expect(paneLines(flagged.text)).toHaveLength(paneLines(FILE).length - 1)
})

test('remove refuses a missing or repeated title', () => {
  expect(failure(() => remove(FILE, 'Nothing'))).toContain('no entry')
  expect(failure(() => remove(FILE, 'inside a fence'))).toContain('no entry')
  const twice = `${SMALL}\n### [ ] Old\n- Steps: again\n`
  expect(failure(() => remove(twice, 'Old'))).toContain('not unique')
})

test('remove of the last entry leaves a clean end, with or without a final break', () => {
  const two = '## Actions\n\n### [ ] A\n- Steps: a\n\n### [ ] B\n- Steps: b\n'

  expect(remove(two, 'B').text).toBe('## Actions\n\n### [ ] A\n- Steps: a\n')
  expect(remove(two.trimEnd(), 'B').text).toBe('## Actions\n\n### [ ] A\n- Steps: a')
  expect(remove(two, 'A').text).toBe('## Actions\n\n### [ ] B\n- Steps: b\n')
  expect(remove(two.replaceAll('\n', '\r\n'), 'B').text).toBe(
    '## Actions\r\n\r\n### [ ] A\r\n- Steps: a\r\n',
  )
})

test('remove reads a fence as the parser does', () => {
  const done = remove(FILE, 'Keep me action')

  expect(done.text).not.toContain('inside a fence')
  expect(done.text).toContain('### [x] Last action')
  expect(done.count).toBe(6)
})

test('prune takes ticked Actions, keeps the named, and holds the ones with a Note', () => {
  const done = prune(FILE, ['Keep me'])

  expect(done.removed).toEqual(['Done action', 'Last action'])
  expect(done.kept).toEqual(['Keep me action'])
  expect(done.held).toEqual(['Done action with a note'])
  expect(done.text).toContain('### [x] Done action with a note')
  expect(done.text).toContain('### [x] Keep me action')
  expect(done.text).toContain('### [x] Ticked decision')
  expect(done.text).not.toContain('### [x] Last action')
  expect(done.text).toContain('## Notes\n\nFooter.\n')
  expect(paneLines(done.text)).toEqual(paneLines(FILE))
  expect(titles(done.text)).toEqual(titles(FILE))
})

test('prune with the flag takes the Notes of a ticked Action with it', () => {
  const done = prune(FILE, ['Keep me'], true)

  expect(done.removed).toEqual([
    'Done action',
    'Done action with a note',
    'Last action',
  ])
  expect(done.held).toEqual([])
  expect(done.text).not.toContain('still wanted')
  expect(done.text).toContain('first words')
})

test('prune lays the file out as it was, and a file with nothing ticked is unchanged', () => {
  const small =
    '## Actions\n\n### [x] A\n- Steps: a\n\n### [ ] B\n- Steps: b\n\n### [x] C\n- Steps: c\n'

  expect(prune(small).text).toBe('## Actions\n\n### [ ] B\n- Steps: b\n')
  expect(prune(SMALL).text).toBe(SMALL)
  expect(prune(small.replaceAll('\n', '\r\n')).text).toBe(
    '## Actions\r\n\r\n### [ ] B\r\n- Steps: b\r\n',
  )
})

const memory = (files: Record<string, string>) => {
  const out: string[] = []
  const writes: string[] = []
  const io: Io = {
    read: path => {
      if (!(path in files)) throw new Error(`no file ${path}`)

      return files[path]
    },
    write: (path, text) => {
      files[path] = text
      writes.push(path)
    },
    print: line => out.push(line),
  }

  return { io, out, writes, files }
}

test('the command line adds, removes and prunes, and prints what it did', () => {
  const m = memory({ 'q.md': SMALL, 'b.md': BLOCK })

  expect(run(['q.md', 'add', 'decision', '--block-file', 'b.md'], m.io)).toBe(0)
  expect(m.out).toEqual(['inserted at line 3'])
  expect(titles(m.files['q.md'])).toEqual(['New', 'Old', 'A'])
  expect(run(['q.md', 'remove', '--title', 'New'], m.io)).toBe(0)
  expect(m.files['q.md']).toBe(SMALL)
  expect(m.out[1]).toBe('removed 3 lines at 3')

  const n = memory({ 'q.md': FILE })
  expect(run(['q.md', 'prune', '--keep', 'Keep me', '--keep', 'x'], n.io)).toBe(0)
  expect(n.out[0]).toBe(
    'removed 2 kept ["Keep me action"] held for a Note ["Done action with a note"]',
  )
  expect(n.writes).toEqual(['q.md'])
})

test('the command line refuses without writing, and says why', () => {
  const m = memory({ 'q.md': FILE, 'b.md': '### [ ] X\n- Note: hi', 'ok.md': BLOCK })

  expect(run(['q.md', 'remove', '--title', 'Open decision'], m.io)).toBe(1)
  expect(m.out[0]).toContain('refused: the entry holds a Note')
  expect(run(['q.md', 'add', 'action', '--block-file', 'b.md'], m.io)).toBe(1)
  expect(run(['q.md', 'add', 'action', '--block-file', 'ok.md', '--force'], m.io)).toBe(1)
  expect(run(['q.md', 'add', 'notes', '--block-file', 'ok.md'], m.io)).toBe(1)
  expect(run(['q.md', 'remove'], m.io)).toBe(1)
  expect(run(['q.md', 'sweep'], m.io)).toBe(1)
  expect(run(['q.md'], m.io)).toBe(1)
  expect(run(['missing.md', 'prune'], m.io)).toBe(1)
  expect(m.out[m.out.length - 1]).toContain('no file missing.md')
  expect(m.writes).toEqual([])
  expect(m.files['q.md']).toBe(FILE)
})
