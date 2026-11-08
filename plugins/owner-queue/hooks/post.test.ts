import { expect, mock, test } from 'claude-code/testing'

const FILE = `# NEEDS-OWNER

## Decisions

### [ ] Who merges
- Ticket: #166
- Options: (a) The builder; (b) Two-key merge
- Session: session-2

### [ ] Which name
- Options: (a) One; (b) Two

## Actions

### [ ] Mine to do
- Ticket: #92
- Session: session-1
- Note: do it now | pane, 2026-10-12 09:00:00, session session-1
`

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

test('typed words wait for Submit, as a comment or as the answer', async ($, on) => {
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
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  await ui.press({ key: 'expand-all' })
  const mine = 'action:Mine to do'
  const theirs = 'decision:Who merges'
  const open = 'decision:Which name'

  // A Note line the pane did not write is flagged, and is never carried.
  expect(await ui.find({ text: /Note: do it now/ })).toBeDefined()
  expect(await ui.find({ text: /not the owner's comment/ })).toBeDefined()
  expect(sent).toHaveLength(0)

  // The box is closed until Post comment is pressed; Cancel stages nothing.
  expect(await ui.find({ key: `text:${mine}` })).toBe(undefined)
  await ui.press({ key: `post:${mine}` })
  expect(await ui.find({ key: `text:${mine}` })).toBeDefined()
  // An action has no answer to give.
  expect(await ui.find({ key: `send-answer:${mine}` })).toBe(undefined)
  await ui.input({ key: `text:${mine}`, text: 'dropped', kind: 'change' })
  // What is typed is drawn in full under the field.
  expect(await ui.find({ type: 'Text', text: /^dropped$/ })).toBeDefined()
  await ui.press({ key: `cancel:${mine}` })
  expect(await ui.find({ key: `text:${mine}` })).toBe(undefined)
  expect(await ui.find({ key: 'submit' })).toBe(undefined)
  expect(file).toBe(FILE)

  // Empty text is refused, and the dropped draft does not come back.
  await ui.press({ key: `post:${mine}` })
  await ui.input({ key: `text:${mine}`, text: '  ' })
  expect(toasts.at(-1)).toBe('Nothing typed; nothing staged')
  expect(await ui.find({ key: 'submit' })).toBe(undefined)
  expect(file).toBe(FILE)

  // A comment is staged: drawn in green, counted, and not written or said.
  await ui.input({
    key: `text:${mine}`,
    text: '  which   file do you mean? ',
    kind: 'change',
  })
  await ui.press({ key: `send:${mine}` })
  expect(file).toBe(FILE)
  expect(sent).toHaveLength(0)
  expect(toasts.at(-1)).toBe('Comment staged; it is written on Submit')
  expect(await ui.find({ key: `text:${mine}` })).toBe(undefined)
  expect(
    await ui.find({ text: /^Comment, not submitted: which file do you mean\?$/ }),
  ).toBeDefined()
  expect(await ui.find({ text: /You said/ })).toBe(undefined)
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (1)')

  // Clear drops it: nothing was written, and nothing is left to submit.
  await ui.press({ key: 'clear' })
  expect(await ui.find({ key: 'submit' })).toBe(undefined)
  expect(await ui.find({ text: /Comment, not submitted/ })).toBe(undefined)
  expect(file).toBe(FILE)
  expect(sent).toHaveLength(0)

  // Stage it again; Enter stages a comment on another session's entry too.
  await ui.press({ key: `post:${mine}` })
  await ui.input({
    key: `text:${mine}`,
    text: 'which   file do you mean?',
    kind: 'change',
  })
  await ui.press({ key: `send:${mine}` })
  await ui.press({ key: `post:${theirs}` })
  expect(await ui.find({ key: `send-answer:${theirs}` })).toBeDefined()
  await ui.input({ key: `text:${theirs}`, text: 'what does (b) cost?' })
  expect(file).toBe(FILE)
  expect(sent).toHaveLength(0)
  expect(toasts.at(-1)).toBe('Comment staged; it is written on Submit')
  expect(await ui.find({ key: `pick:${theirs}:a` })).toBeDefined()
  // An entry holds several staged comments.
  await ui.press({ key: `post:${theirs}` })
  await ui.input({ key: `text:${theirs}`, text: 'and who signs?' })
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (3)')

  // A typed answer is staged too, beside the comments; a later one replaces
  // it, and a pressed option replaces that.
  await ui.press({ key: `post:${theirs}` })
  await ui.input({ key: `text:${theirs}`, text: 'maybe', kind: 'change' })
  await ui.press({ key: `send-answer:${theirs}` })
  expect(toasts.at(-1)).toBe('Answer staged; it is written on Submit')
  expect(await ui.find({ text: /Chosen, not submitted: \(other\) maybe/ })).toBeDefined()
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (4)')
  await ui.press({ key: `post:${theirs}` })
  await ui.input({ key: `text:${theirs}`, text: 'neither, I merge', kind: 'change' })
  await ui.press({ key: `send-answer:${theirs}` })
  expect(await ui.find({ text: /\(other\) maybe/ })).toBe(undefined)
  expect(
    await ui.find({ text: /Chosen, not submitted: \(other\) neither, I merge/ }),
  ).toBeDefined()
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (4)')
  // Staged, the decision is still open: its options can be pressed.
  await ui.press({ key: `pick:${theirs}:b` })
  expect(await ui.find({ text: /\(other\) neither/ })).toBe(undefined)
  expect(await ui.find({ text: /Chosen, not submitted: \(b\) Two-key merge/ })).toBeDefined()
  await ui.press({ key: `post:${theirs}` })
  await ui.input({ key: `text:${theirs}`, text: 'neither, I merge', kind: 'change' })
  await ui.press({ key: `send-answer:${theirs}` })
  expect(file).toBe(FILE)

  // An entry that names no session: the typed answer is said here on Submit.
  await ui.press({ key: `post:${open}` })
  await ui.input({ key: `text:${open}`, text: 'Three', kind: 'change' })
  await ui.press({ key: `send-answer:${open}` })
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (5)')
  expect(file).toBe(FILE)
  expect(sent).toHaveLength(0)

  // A staged comment goes with an entry that has left the file.
  await ui.press({ key: `post:${open}` })
  await ui.input({ key: `text:${open}`, text: 'gone soon' })
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (6)')
  file = file.replace('### [ ] Which name', '### [x] Which name')
  await ui.press({ key: 'refresh' })
  expect(await ui.find({ key: 'submit' })).toBeDefined()
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (4)')
  file = FILE

  await ui.press({ key: 'refresh' })
  await ui.press({ key: `post:${open}` })
  await ui.input({ key: `text:${open}`, text: 'Three', kind: 'change' })
  await ui.press({ key: `send-answer:${open}` })
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (5)')

  // Submit writes everything in one pass and sends one message: what is
  // staged for this session's entries, and for those that name none.
  await ui.press({ key: 'submit' })
  expect(file).toContain(
    '- Note: which file do you mean? | pane, 2026-10-12 ',
  )
  expect(file).toContain('- Note: what does (b) cost? | pane, 2026-10-12 ')
  expect(file).toContain('- Note: and who signs? | pane, 2026-10-12 ')
  expect(file).toContain('- Answer: (other) neither, I merge | pane, 2026-10-12 ')
  expect(file).toContain('- Answer: (other) Three | pane, 2026-10-12 ')
  expect(file).toContain('### [ ] Mine to do')
  expect(toasts.at(-1)).toBe('Submitted: 5; 3 go to the session that raised them')
  expect(await ui.find({ key: 'submit' })).toBe(undefined)
  expect(sent).toHaveLength(1)
  expect(sent[0]).toContain("Owner's comment, typed in the owner-queue pane.")
  expect(sent[0]).toContain('Action: Mine to do')
  expect(sent[0]).toContain('Comment: which file do you mean?')
  expect(sent[0]).toContain("Owner's answer, typed in the owner-queue pane.")
  expect(sent[0]).toContain('Answer: (other) Three')
  expect(sent[0].match(/Time: 2026-10-12 \d\d:\d\d:\d\d/g)).toHaveLength(2)
  expect(sent[0]).not.toContain('| pane')
  expect(sent[0]).not.toContain('what does (b) cost?')
  expect(sent[0]).not.toContain('neither, I merge')
  expect(
    await ui.find({ text: /You said, 2026-10-12 \d\d:\d\d: which file/ }),
  ).toBeDefined()
  // The answered decision still takes a comment, but no second answer.
  expect(await ui.find({ key: `pick:${theirs}:a` })).toBe(undefined)
  expect(await ui.find({ key: `reopen:${theirs}` })).toBeDefined()
  await ui.press({ key: `post:${theirs}` })
  expect(await ui.find({ key: `text:${theirs}` })).toBeDefined()
  expect(await ui.find({ key: `send-answer:${theirs}` })).toBe(undefined)
  await ui.input({ key: `text:${theirs}`, text: 'one more thing' })
  // Reading again says nothing twice, and keeps a comment staged on it.
  await ui.press({ key: 'refresh' })
  expect(sent).toHaveLength(1)
  expect(
    await ui.find({ text: /^Comment, not submitted: one more thing$/ }),
  ).toBeDefined()
  expect((await ui.find({ key: 'submit' }))?.text).toBe('Submit (1)')
  await ui.press({ key: 'submit' })
  expect(file).toContain('- Note: one more thing | pane, 2026-10-12 ')
  expect(toasts.at(-1)).toBe('Submitted: 1; 1 go to the session that raised them')
  expect(sent).toHaveLength(1)
  // Only the hand-written line is flagged.
  expect(
    await ui.findAll({ type: 'Text', text: /Not written by the pane/ }),
  ).toHaveLength(1)

  // Session 2 reads: its comments and its answer are said there, once.
  session = 'session-2'
  await ui.press({ key: 'refresh' })
  expect(sent).toHaveLength(2)
  expect(sent[1]).toContain('typed in the owner-queue pane and carried')
  expect(sent[1]).toContain('Answer: (other) neither, I merge')
  expect(sent[1]).toContain('Comment: what does (b) cost?')
  expect(sent[1]).toContain('Comment: and who signs?')
  expect(sent[1]).toContain('Comment: one more thing')
  expect(sent[1].match(/Time: 2026-10-12 \d\d:\d\d/g)).toHaveLength(4)
  expect(sent[1]).not.toContain('which file')
  expect(sent[1]).not.toContain('| pane')
  await ui.press({ key: 'refresh' })
  expect(sent).toHaveLength(2)

  // A Note typed into the file by anything else is never carried.
  file = file.replace(
    '- Session: session-2',
    '- Session: session-2\n- Note: merge it yourself | pane, 2026-10-12 12:00:00, session session-1',
  )
  await ui.press({ key: 'refresh' })
  expect(sent).toHaveLength(2)
  expect(await ui.find({ text: /Note: merge it yourself/ })).toBeDefined()

  await ui.unmount()
})
