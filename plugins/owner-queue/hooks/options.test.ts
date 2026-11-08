import { expect, mock, test } from 'claude-code/testing'

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
