import { expect, mock, test } from 'claude-code/testing'
import type { Engine, On } from 'claude-code/testing'

const FILE = `# NEEDS-OWNER

## Decisions

### [ ] Refers to a key
- Options: (a) one; (b) the rest as in (a); (c) as (a), but later

### [ ] Same key twice
- Options: (a) one; (b) two; (a) three
`

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

test('an option that names another key stays one option; a twice-used key draws none', async ($, on) => {
  mock.store(on)
  mock.clock(on, { now: Date.UTC(2026, 9, 12, 12, 0, 0) })
  on('fs.read', ($$, e) => {
    if (e.path.endsWith('.git')) throw new Error('a folder')

    return { value: FILE }
  })
  on('process.run', () => ({
    value: { exitCode: 128, stdout: '', stderr: 'not a repository' },
  }))
  on('session.id', () => ({ value: 'session-1' }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))

  await $.command.run({ command: 'owner', args: '' })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  await ui.press({ key: 'expand-all' })
  const named = 'decision:Refers to a key'
  const twice = 'decision:Same key twice'

  // Three options, three buttons; no extra `Choose (a)`.
  expect(await ui.find({ key: `pick:${named}:a` })).toBeDefined()
  expect(await ui.find({ key: `pick:${named}:b` })).toBeDefined()
  expect(await ui.find({ key: `pick:${named}:c` })).toBeDefined()
  expect(
    await ui.findAll({ type: 'Button', text: /^Choose \(a\)/ }),
  ).toHaveLength(1)
  expect(await ui.find({ text: /^\(b\) the rest as in \(a\)$/ })).toBeDefined()
  expect(await ui.find({ text: /^\(c\) as \(a\), but later$/ })).toBeDefined()

  // The twice-used key draws no option and says why; the text is still there.
  expect(await ui.find({ key: `pick:${twice}:a` })).toBe(undefined)
  expect(await ui.find({ key: `pick:${twice}:b` })).toBe(undefined)
  expect(
    await ui.findAll({ type: 'Text', text: /The Options line is malformed/ }),
  ).toHaveLength(1)
  expect(await ui.find({ text: /\(a\) one; \(b\) two; \(a\) three/ })).toBeDefined()

  await ui.unmount()
})

const FEW = `# NEEDS-OWNER

## Decisions

### [ ] Period before the second key
- Options: (1) Change the rule; a held file may hold more; the rest goes first. (2) Keep the rule and go in steps; three changes in all.

### [ ] One keyed option
- Options: (a) only this

### [ ] One plain option
- Options: only this

### [ ] No options at all
- Context: asked in words

### [ ] Two keyed
- Options: (a) one; (b) two

### [ ] Two plain
- Options: One; Two

### [ ] Key twice
- Options: (a) one; (b) two; (a) three
`

const OWN = '.claude/memory/NEEDS-OWNER.md'
const LOG = 'C:/home/.claude/owner-queue/problems.log'

/** The pane mounted on FEW, every row open; `files` holds what was written. */
async function mountFew($: Engine, on: On) {
  const files = new Map([[OWN, FEW]])
  const key = (path: string) => {
    const slashed = path.replaceAll('\\', '/')

    return slashed.endsWith(`/${OWN}`) ? OWN : slashed
  }
  mock.store(on)
  mock.clock(on, { now: Date.UTC(2026, 10, 28, 12, 0, 0) })
  mock.env(on, { USERPROFILE: 'C:/home' })
  on('fs.read', ($$, e) => {
    if (e.path.endsWith('.git')) throw new Error('a folder')
    const text = files.get(key(e.path))
    if (text === undefined) throw new Error('missing')

    return { value: text }
  })
  on('fs.write', ($$, e) => {
    files.set(key(e.path), e.text)

    return { value: undefined }
  })
  on('fs.exists', ($$, e) => ({ value: files.has(key(e.path)) }))
  on('process.run', () => ({
    value: { exitCode: 128, stdout: '', stderr: 'not a repository' },
  }))
  on('session.id', () => ({ value: 'session-1' }))
  on('prompt.submit', ($$, e) => ({ text: e.text }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.log', () => ({ value: undefined }))

  await $.command.run({ command: 'owner', args: '' })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  await ui.press({ key: 'expand-all' })

  return { ui, files }
}

const FEW_NOTE = /fewer than two options were read/

test('a period before the second key reads as malformed: no button, its own note, no answer', async ($, on) => {
  const { ui, files } = await mountFew($, on)
  const id = 'decision:Period before the second key'

  expect(await ui.find({ key: `pick:${id}:1` })).toBe(undefined)
  expect(await ui.find({ key: `pick:${id}:2` })).toBe(undefined)
  expect(await ui.find({ text: /^\(1\) Change the rule/ })).toBe(undefined)
  // The new note names the fault and where a key counts.
  const notes = await ui.findAll({ type: 'Text', text: FEW_NOTE })
  expect(notes.length).toBeGreaterThan(0)
  expect(notes[0].text).toMatch(/The Options line is malformed/)
  expect(notes[0].text).toMatch(/right after a semicolon/)
  expect(notes[0].text).toMatch(/No options are drawn/)
  // Only the two good decisions have option buttons, so nothing can be
  // staged for this one: no Submit is drawn and the file is not written.
  expect(await ui.findAll({ type: 'Button', text: /^Choose \(/ })).toHaveLength(4)
  expect(await ui.find({ key: 'submit' })).toBe(undefined)
  expect(files.get(OWN)).toBe(FEW)

  await ui.unmount()
})

test('one option alone is malformed; no Options, two options and a key twice are as before', async ($, on) => {
  const { ui, files } = await mountFew($, on)

  // One keyed and one plain option: no button each, three new notes in all.
  expect(await ui.find({ key: 'pick:decision:One keyed option:a' })).toBe(undefined)
  expect(await ui.find({ key: 'pick:decision:One plain option:a' })).toBe(undefined)
  expect(await ui.findAll({ type: 'Text', text: FEW_NOTE })).toHaveLength(3)

  // Two keyed and two plain: both drawn.
  for (const title of ['Two keyed', 'Two plain']) {
    expect(await ui.find({ key: `pick:decision:${title}:a` })).toBeDefined()
    expect(await ui.find({ key: `pick:decision:${title}:b` })).toBeDefined()
  }

  // A key twice keeps its own note; no Options field draws no note at all,
  // so the notes are the three new ones and the one for the key twice.
  expect(
    await ui.findAll({ type: 'Text', text: /a key appears twice/ }),
  ).toHaveLength(1)
  expect(
    await ui.findAll({ type: 'Text', text: /The Options line is malformed/ }),
  ).toHaveLength(4)

  // Each fault is logged under its own kind.
  const kinds = (files.get(LOG) ?? '')
    .split('\n')
    .filter(one => one !== '')
    .map(one => one.split(' | ').slice(2).join(' | '))
  expect(kinds).toEqual([
    'Period before the second key | Options line: fewer than two options',
    'One keyed option | Options line: fewer than two options',
    'One plain option | Options line: fewer than two options',
    'Key twice | Options line: a key appears twice',
  ])

  await ui.unmount()
})
