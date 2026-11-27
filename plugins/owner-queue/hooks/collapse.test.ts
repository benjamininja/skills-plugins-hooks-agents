import { expect, mock, test } from 'claude-code/testing'

const FILE = `# NEEDS-OWNER

## Decisions

### [ ] Who merges
- Options: (a) The builder; (b) Two-key merge

### [ ] Which name
- Options: (a) One; (b) Two

## Actions

### [ ] Fire the first login
- Ticket: #92

### [ ] Second task
- Ticket: #93
`

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

const A = 'decision:Who merges'
const B = 'decision:Which name'
const T1 = 'action:Fire the first login'
const T2 = 'action:Second task'

async function setup($: any, on: any) {
  const writes: string[] = []
  mock.store(on)
  mock.clock(on, { now: Date.UTC(2026, 9, 12, 12, 0, 0) })
  on('fs.read', ($$: any, e: any) => {
    if (e.path.endsWith('.git')) throw new Error('a folder')

    return { value: FILE }
  })
  on('fs.write', ($$: any, e: any) => {
    writes.push(e.text)

    return { value: undefined }
  })
  on('process.run', () => ({
    value: { exitCode: 128, stdout: '', stderr: 'not a repository' },
  }))
  on('session.id', () => ({ value: 'session-1' }))
  on('prompt.submit', ($$: any, e: any) => ({ text: e.text }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))

  await $.command.run({ command: 'owner', args: '' })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  await ui.press({ key: 'expand-all' })

  return { ui, writes }
}

test('a press on an option closes the entry; pressing it again leaves it as it was', async ($, on) => {
  const { ui, writes } = await setup($, on)

  expect(await ui.find({ key: `pick:${A}:b` })).toBeDefined()
  await ui.press({ key: `pick:${A}:b` })
  // Closed: its buttons are gone, the other entries are still open.
  expect(await ui.find({ key: `pick:${A}:b` })).toBe(undefined)
  expect(await ui.find({ key: `pick:${B}:a` })).toBeDefined()
  expect(await ui.find({ key: `done:${T1}` })).toBeDefined()
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (1)')

  // The owner opens it again by hand; the same option taken back leaves it open.
  await ui.press({ key: `row:${A}` })
  expect(await ui.find({ key: `pick:${A}:b` })).toBeDefined()
  await ui.press({ key: `pick:${A}:b` })
  expect(await ui.find({ key: 'submit' })).toBe(undefined)
  expect(await ui.find({ key: `pick:${A}:b` })).toBeDefined()

  expect(writes).toHaveLength(0)
  await ui.unmount()
})

test('a press on Mark done closes the entry; Not done after all leaves it as it was', async ($, on) => {
  const { ui, writes } = await setup($, on)

  await ui.press({ key: `done:${T1}` })
  expect(await ui.find({ key: `done:${T1}` })).toBe(undefined)
  expect(await ui.find({ key: `done:${T2}` })).toBeDefined()
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (1)')

  await ui.press({ key: `row:${T1}` })
  expect((await ui.find({ key: `done:${T1}` }))?.text).toBe('Not done after all')
  await ui.press({ key: `done:${T1}` })
  expect(await ui.find({ key: 'submit' })).toBe(undefined)
  expect(await ui.find({ key: `done:${T1}` })).toBeDefined()

  expect(writes).toHaveLength(0)
  await ui.unmount()
})

test('a typed answer closes the entry, a comment does not', async ($, on) => {
  const { ui, writes } = await setup($, on)

  await ui.press({ key: `post:${B}` })
  await ui.input({ key: `text:${B}`, text: 'a third name', kind: 'change' })
  await ui.press({ key: `send-answer:${B}` })
  expect(await ui.find({ key: `pick:${B}:a` })).toBe(undefined)
  expect(await ui.find({ key: `pick:${A}:a` })).toBeDefined()
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (1)')

  await ui.press({ key: `post:${T2}` })
  await ui.input({ key: `text:${T2}`, text: 'which file?', kind: 'change' })
  await ui.press({ key: `send:${T2}` })
  expect(await ui.find({ key: `done:${T2}` })).toBeDefined()
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (2)')

  expect(writes).toHaveLength(0)
  await ui.unmount()
})
