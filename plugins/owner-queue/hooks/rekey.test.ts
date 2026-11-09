import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code/testing'

const OWN = '.claude/memory/NEEDS-OWNER.md'
const DYN = 'C:/work/dynasty/.claude/memory/NEEDS-OWNER.md'
const FENCE = '```'

const GIVEN = '(b) no | pane, 2026-11-08 11:00:00, session session-9'
const NOTE = 'keep - Session: session-1 as it is | pane, 2026-11-08 11:05:00'

const OWN_FILE = `# NEEDS-OWNER

## Decisions

### [ ] Who merges
- Options: (a) yes; (b) no
- Session: session-1 (planner)
- Answer: ${GIVEN}
- Note: ${NOTE}

### [ ] Third party
- Options: (a) yes; (b) no
- Session: session-3

## Actions

### [ ] Fire the login
- Session: session-1
`

const DYN_FILE = `# NEEDS-OWNER

## Decisions

### [ ] Their thing
- Options: (a) yes; (b) no
- Session: session-1

## Actions

### [ ] Run it by hand
- Session: session-1
- Steps: 1. run the line
${FENCE}
- Session: session-1
${FENCE}
`

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

const ENDED ={ reason: 'clear', sessionId: 'session-1', resume: { id: 'session-1' } } as const

function world(
  on: On,
  files: Map<string, string>,
  ids: { now: string },
  store: Record<string, unknown> = {},
) {
  const sent: string[] = []
  const toasts: string[] = []
  mock.store(on, store)
  const time = mock.clock(on, { now: Date.UTC(2026, 10, 9, 12, 0, 0) })
  mock.env(on, { USERPROFILE: 'C:/home' })
  const key = (path: string) => {
    const slashed = path.replaceAll('\\', '/')

    return !files.has(slashed) && slashed.endsWith(`/${OWN}`) ? OWN : slashed
  }
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
  on('session.id', () => ({ value: ids.now }))
  on('session.end', ($$, e) => ({ sessionId: e.sessionId }))
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

  return { sent, toasts, time }
}

const place = (file: string, id: string) => `${file}|${id}`

test(
  'a clear re-keys the entries that name the old id, in two queues',
  { options: { queues: [DYN] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [DYN, DYN_FILE],
    ])
    const ids = { now: 'session-1' }
    const { toasts } = world(on, files, ids)

    await $.session.end(ENDED)
    // The old id still answers: nothing yet.
    await $.command.run({ command: 'owner', args: '' })
    expect(files.get(OWN)).toBe(OWN_FILE)
    expect(files.get(DYN)).toBe(DYN_FILE)

    ids.now = 'session-2'
    await $.command.run({ command: 'owner', args: '' })

    expect(files.get(OWN)).toBe(
      OWN_FILE.replace(
        '- Session: session-1 (planner)',
        '- Session: session-2 (planner)',
      ).replace('### [ ] Fire the login\n- Session: session-1', '### [ ] Fire the login\n- Session: session-2'),
    )
    // The Dynasty queue: two entries; the fenced example is left as written.
    expect(files.get(DYN)).toBe(
      DYN_FILE.replace(
        '### [ ] Their thing\n- Options: (a) yes; (b) no\n- Session: session-1',
        '### [ ] Their thing\n- Options: (a) yes; (b) no\n- Session: session-2',
      ).replace(
        '### [ ] Run it by hand\n- Session: session-1',
        '### [ ] Run it by hand\n- Session: session-2',
      ),
    )
    expect(toasts).toContain("Re-keyed 4 entries to this session's new id")

    // Once only: another read changes nothing.
    const after = [files.get(OWN), files.get(DYN)]
    await $.command.run({ command: 'owner', args: '' })
    expect([files.get(OWN), files.get(DYN)]).toEqual(after)
    expect(toasts.filter(one => one.startsWith('Re-keyed'))).toHaveLength(1)
  },
)

test('an Answer line and a Note line stay as they were', async ($, on) => {
  const files = new Map([[OWN, OWN_FILE]])
  const ids = { now: 'session-1' }
  world(on, files, ids)

  await $.session.end(ENDED)
  ids.now = 'session-2'
  await $.command.run({ command: 'owner', args: '' })

  const text = files.get(OWN) ?? ''
  expect(text).toContain(`- Answer: ${GIVEN}\n`)
  expect(text).toContain(`- Note: ${NOTE}\n`)
  expect(text.split('\n').filter(one => one.startsWith('- Session: session-1'))).toHaveLength(0)
})

test('the delivered, noted and done records move to the new id', async ($, on) => {
  const files = new Map([[OWN, OWN_FILE]])
  const ids = { now: 'session-1' }
  const who = place(OWN, 'decision:Who merges')
  const { sent } = world(on, files, ids, {
    answers: { [who]: GIVEN },
    notes: { [who]: [NOTE] },
    'delivered:session-1': { [who]: GIVEN },
    'noted:session-1': { [who]: [NOTE] },
    'done:session-1': ['Action: Fire the login, marked done'],
  })

  // `/owner` may not submit a prompt itself; a refresh in the pane does. A
  // reader that names none of the entries loads the queue first.
  ids.now = 'reader'
  await $.command.run({ command: 'owner', args: '' })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  await $.session.end(ENDED)
  ids.now = 'session-2'
  await ui.press({ key: 'refresh' })

  expect(files.get(OWN)).toContain('- Session: session-2 (planner)')
  expect(sent).toHaveLength(1)
  expect(sent[0]).toContain('Marked done by the owner')
  expect(sent[0]).toContain('Action: Fire the login, marked done')
  expect(sent[0]).not.toContain('Owner')
  await ui.press({ key: 'refresh' })
  expect(sent).toHaveLength(1)
  await ui.unmount()
})

test('an entry naming a third id is left alone', async ($, on) => {
  const files = new Map([[OWN, OWN_FILE]])
  const ids = { now: 'session-1' }
  world(on, files, ids)

  await $.session.end(ENDED)
  ids.now = 'session-2'
  await $.command.run({ command: 'owner', args: '' })

  expect(files.get(OWN)).toContain('### [ ] Third party\n- Options: (a) yes; (b) no\n- Session: session-3\n')
})

test('an id change with no clear seen re-keys nothing', async ($, on) => {
  const files = new Map([[OWN, OWN_FILE]])
  const ids = { now: 'session-1' }
  const who = place(OWN, 'decision:Who merges')
  const { sent, toasts } = world(on, files, ids, {
    answers: { [who]: GIVEN },
    'delivered:session-1': { [who]: GIVEN },
  })

  await $.command.run({ command: 'owner', args: '' })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  await $.session.end({ ...ENDED, reason: 'resume' })
  ids.now = 'session-2'
  await ui.press({ key: 'refresh' })
  await ui.press({ key: 'refresh' })

  expect(files.get(OWN)).toBe(OWN_FILE)
  expect(toasts.filter(one => one.startsWith('Re-keyed'))).toHaveLength(0)
  // The record stayed under the old id: back there, the answer is not said again.
  ids.now = 'session-1'
  await ui.press({ key: 'refresh' })
  expect(sent).toHaveLength(0)
  await ui.unmount()
})

test('after 60 s with the old id still answering, it says the manual rule and re-keys nothing', async ($, on) => {
  const files = new Map([[OWN, OWN_FILE]])
  const ids = { now: 'session-1' }
  const { toasts, time } = world(on, files, ids)

  await $.session.end(ENDED)
  await time.advance(59000)
  await $.command.run({ command: 'owner', args: '' })
  expect(toasts.filter(one => one.includes('not re-keyed'))).toHaveLength(0)

  await time.advance(2000)
  await $.command.run({ command: 'owner', args: '' })
  const said = toasts.filter(one => one.includes('not re-keyed'))
  expect(said).toHaveLength(1)
  expect(said[0]).toContain('parking.md')

  // Given up: a later id change re-keys nothing, and the toast is not repeated.
  ids.now = 'session-2'
  await $.command.run({ command: 'owner', args: '' })
  expect(files.get(OWN)).toBe(OWN_FILE)
  expect(toasts.filter(one => one.includes('not re-keyed'))).toHaveLength(1)
  expect(toasts.filter(one => one.startsWith('Re-keyed'))).toHaveLength(0)
})
