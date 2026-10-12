import { expect, mock, test } from 'claude-code/testing'

const FILE = `# NEEDS-OWNER

## Decisions

### [ ] Who merges
- Ticket: #166
- Options: (a) The builder; (b) Two-key merge
- Recommended: (b), because two sets of eyes
- Raised: 2026-10-12, by the builder manager

### [ ] Already settled
- Options: (a) Yes; (b) No
- Answer: (a) Yes | typed by a session

## Actions

### [ ] Fire the first login
- Ticket: #92
`

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

test('a pressed option writes the file, sends the answer, and can be undone', async ($, on) => {
  // The test's hooks stand for the engine: one file, the prompts sent, the box.
  let file = FILE
  const sent: { text: string; asUser?: true }[] = []
  const drafts: string[] = []
  const toasts: string[] = []
  mock.store(on)
  mock.clock(on, { now: Date.UTC(2026, 9, 12, 12, 0, 0) })
  on('fs.read', ($$, e) => {
    if (e.path.endsWith('.git')) throw new Error('a folder')

    return { value: file }
  })
  on('fs.write', ($$, e) => {
    file = e.text

    return { value: undefined }
  })
  on('process.run', () => ({
    value: { exitCode: 128, stdout: '', stderr: 'not a repository' },
  }))
  on('session.id', () => ({ value: 'session-1' }))
  on('prompt.submit', ($$, e) => {
    const from = e.origin
    sent.push({
      text: e.text,
      asUser: from?.kind === 'plugin' ? from.asUser : undefined,
    })

    return { text: e.text }
  })
  on('prompt.fill', ($$, e) => {
    drafts.push(e.text)

    return { isFilled: true }
  })
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', ($$, e) => {
    toasts.push(e.text)

    return { value: undefined }
  })
  on('ui.open', () => ({ value: { isPlaced: true } }))

  await $.command.run({ command: 'owner', args: '' })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const id = 'decision:Who merges'

  // An Answer line the pane did not write is flagged.
  expect(await ui.find({ text: /Not written by the pane/ })).toBeDefined()

  await ui.press({ key: `row:${id}` })
  expect((await ui.find({ key: `pick:${id}:b` }))?.text).toContain(
    '[recommended]',
  )

  await ui.press({ key: `other:${id}` })
  expect(drafts[0]).toContain('Decision: Who merges (#166)')
  expect(file).toBe(FILE)

  await ui.press({ key: `pick:${id}:b` })
  expect(file).toContain(
    '- Answer: (b) Two-key merge | pane, 2026-10-12 ',
  )
  expect(file).toContain(', session session-1')
  expect(sent.length).toBe(1)
  expect(sent[0].asUser).toBe(true)
  expect(sent[0].text).toContain('Decision: Who merges')
  expect(sent[0].text).toContain('Answer: (b) Two-key merge')
  expect(toasts).toContain('Answered: Who merges')
  expect(await ui.find({ key: `pick:${id}:b` })).toBe(undefined)
  expect(
    await ui.findAll({ type: 'Text', text: /Not written by the pane/ }),
  ).toHaveLength(1)

  await ui.press({ key: `reopen:${id}` })
  expect(file).toBe(FILE)
  expect(await ui.find({ key: `pick:${id}:a` })).toBeDefined()

  await ui.press({ key: 'refresh' })
  expect(toasts.at(-1)).toBe(
    'Queue read: Owner: 1 decision, 1 action, 1 answered',
  )

  await ui.unmount()
})
