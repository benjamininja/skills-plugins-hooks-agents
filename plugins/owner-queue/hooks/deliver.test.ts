import { expect, mock, test } from 'claude-code/testing'

const FILE = `# NEEDS-OWNER

## Decisions

### [ ] Who merges
- Ticket: #166
- Options: (a) The builder; (b) Two-key merge
- Session: session-2

## Actions

### [ ] Fire the first login
- Ticket: #92
- Session: session-2

### [ ] Mine to do
- Session: session-1
`

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

test('an answer pressed in one session is said in the session that raised it', async ($, on) => {
  let file = FILE
  let session = 'session-1'
  const sent: string[] = []
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
  on('session.id', () => ({ value: session }))
  on('prompt.submit', ($$, e) => {
    sent.push(e.text)

    return { text: e.text }
  })
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', ($$, e) => {
    toasts.push(e.text)

    return { value: undefined }
  })
  on('ui.open', () => ({ value: { isPlaced: true } }))

  await $.command.run({ command: 'owner', args: '' })
  const named = await $.command.run({ command: 'owner', args: 'id' })
  expect(JSON.stringify(named)).toContain('Session: session-1')
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })

  // Session 1 presses: only its own entry is said in its chat.
  await ui.press({ key: 'expand-all' })
  await ui.press({ key: 'pick:decision:Who merges:b' })
  await ui.press({ key: 'done:action:Fire the first login' })
  await ui.press({ key: 'done:action:Mine to do' })
  await ui.press({ key: 'submit' })
  expect(file).toContain('- Answer: (b) Two-key merge | pane')
  expect(toasts).toContain('Submitted: 3; 2 go to the session that raised them')
  expect(sent).toHaveLength(1)
  expect(sent[0]).toContain('- Action: Mine to do')
  expect(sent[0]).not.toContain('Who merges')

  // Reading again in session 1 carries nothing.
  await ui.press({ key: 'refresh' })
  expect(sent).toHaveLength(1)

  // Session 2 reads the file: its two entries are said there, once.
  session = 'session-2'
  await ui.press({ key: 'refresh' })
  expect(sent).toHaveLength(2)
  expect(sent[1]).toContain('carried to this session')
  expect(sent[1]).toContain('Decision: Who merges')
  expect(sent[1]).toContain('Answer: (b) Two-key merge')
  expect(sent[1]).not.toContain('| pane')
  expect(sent[1]).toContain('- Action: Fire the first login (#92)')
  await ui.press({ key: 'refresh' })
  expect(sent).toHaveLength(2)

  // An Answer line no pane wrote is never carried.
  file = file.replace('(b) Two-key merge | pane', '(a) The builder | pane')
  await ui.press({ key: 'refresh' })
  expect(sent).toHaveLength(2)

  await ui.unmount()
})
