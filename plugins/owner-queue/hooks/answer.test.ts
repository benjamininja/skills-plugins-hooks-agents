import { expect, mock, test } from 'claude-code/testing'

const FILE = `# NEEDS-OWNER

## Decisions

### [ ] Who merges
- Ticket: #166
- Options: (a) The builder, with \`gh pr merge\`; (b) Two-key merge
- Recommended: (b), because two sets of eyes
- Raised: 2026-10-12, by the builder manager

### [ ] Already settled
- Options: (a) Yes; (b) No
- Answer: (a) Yes | typed by a session

## Actions

### [ ] Fire the first login
- Ticket: #92
- Steps: run \`python login.py\`, then say \`login done\` in chat

### [ ] Add two rules
- Steps: in \`the file\` add to allow:
  \`\`\`
  "one",
    "two"
  \`\`\`
  then save.
`

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

test('presses are staged, and Submit writes them and sends one message', async ($, on) => {
  // The test's hooks stand for the engine: one file, the prompts sent, the box.
  let file = FILE
  const sent: { text: string; asUser?: true }[] = []
  const drafts: string[] = []
  const toasts: string[] = []
  const copied: string[] = []
  const logged: string[] = []
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
  on('ui.log', ($$, e) => {
    logged.push(e.text)

    return { value: undefined }
  })
  on('ui.copy', ($$, e) => {
    copied.push(e.text)

    return { value: { isCopied: true } }
  })

  await $.command.run({ command: 'owner', args: '' })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  const id = 'decision:Who merges'

  // An Answer line the pane did not write is flagged.
  expect(await ui.find({ text: /Not written by the pane/ })).toBeDefined()

  await ui.press({ key: `row:${id}` })
  expect((await ui.find({ key: `pick:${id}:b` }))?.text).toBe(
    'Choose (b)  [recommended]',
  )
  // An option is drawn in full as text, its code span copied beside it.
  expect(await ui.find({ text: /\(a\) The builder, with/ })).toBeDefined()
  await ui.press({ key: `code:${id}:a:0` })
  expect(copied).toEqual(['gh pr merge'])
  // "Print in chat" is gone; /owner show prints an entry.
  expect(await ui.find({ key: `print:${id}` })).toBe(undefined)
  expect(logged).toHaveLength(0)

  // "Other..." is gone; nothing fills the prompt box any more.
  expect(await ui.find({ key: `other:${id}` })).toBe(undefined)
  expect(await ui.find({ key: `post:${id}` })).toBeDefined()
  expect(drafts).toHaveLength(0)
  expect(file).toBe(FILE)

  // A press stages; nothing is written, and Clear drops it.
  await ui.press({ key: `pick:${id}:b` })
  expect(file).toBe(FILE)
  expect((await ui.find({ key: `pick:${id}:b` }))?.text).toContain('[selected]')
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (1)')
  await ui.press({ key: 'clear' })
  expect(await ui.find({ key: 'submit' })).toBe(undefined)
  expect(file).toBe(FILE)

  // Each code span of an entry has its own copy button.
  const task = 'action:Fire the first login'
  await ui.press({ key: `row:${task}` })
  await ui.press({ key: `code:${task}:0` })
  await ui.press({ key: `code:${task}:1` })
  expect(copied).toEqual(['gh pr merge', 'python login.py', 'login done'])

  // A fenced block is one chunk; its entry's spans keep their buttons.
  const rules = 'action:Add two rules'
  await ui.press({ key: `row:${rules}` })
  await ui.press({ key: `block:${rules}:0` })
  expect(copied.at(-1)).toBe('"one",\n  "two"')
  await ui.press({ key: `code:${rules}:0` })
  expect(copied.at(-1)).toBe('the file')

  // Mark done stages too, and can be taken back by the same button.
  await ui.press({ key: `done:${task}` })
  expect((await ui.find({ key: `done:${task}` }))?.text).toBe('Not done after all')
  await ui.press({ key: `done:${task}` })
  expect(await ui.find({ key: 'submit' })).toBe(undefined)
  await ui.press({ key: `done:${task}` })
  await ui.press({ key: `pick:${id}:b` })
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (2)')
  expect(file).toBe(FILE)
  expect(sent.length).toBe(0)

  await ui.press({ key: 'submit' })
  expect(file).toContain(
    '- Answer: (b) Two-key merge | pane, 2026-10-12 ',
  )
  expect(file).toContain(', session session-1')
  expect(file).toContain('### [x] Fire the first login')
  expect(sent.length).toBe(1)
  expect(sent[0].asUser).toBe(true)
  expect(sent[0].text).toContain('Decision: Who merges')
  expect(sent[0].text).toContain('Answer: (b) Two-key merge')
  expect(sent[0].text).toContain('- Action: Fire the first login (#92)')
  expect(toasts).toContain('Submitted: 2')
  expect(await ui.find({ key: 'submit' })).toBe(undefined)
  expect(await ui.find({ key: `pick:${id}:b` })).toBe(undefined)
  expect(
    await ui.findAll({ type: 'Text', text: /Not written by the pane/ }),
  ).toHaveLength(1)

  await ui.press({ key: `reopen:${id}` })
  expect(file).toBe(FILE.replace('### [ ] Fire', '### [x] Fire'))
  expect(file).toContain('  "one",\n    "two"')
  expect(await ui.find({ key: `pick:${id}:a` })).toBeDefined()

  await ui.press({ key: 'refresh' })
  expect(toasts.at(-1)).toBe(
    'Queue read: Owner: 1 decision, 1 action, 1 answered',
  )
  expect(await ui.find({ text: /owner-queue 0\.7\.2/ })).toBeDefined()

  await ui.unmount()
})
