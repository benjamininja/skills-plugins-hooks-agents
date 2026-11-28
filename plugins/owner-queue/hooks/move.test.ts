import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code/testing'

// A folder move (#240): the store's records keyed by a queue path that is
// gone move to the queue file that took its place.

const OWN = '.claude/memory/NEEDS-OWNER.md'
const OLD = 'C:/old/dynasty/.claude/memory/NEEDS-OWNER.md'
const NEW = 'C:/new/dynasty/.claude/memory/NEEDS-OWNER.md'
const TWIN = 'C:/twin/dynasty/.claude/memory/NEEDS-OWNER.md'
const TOOLS = 'C:/work/tools/.claude/memory/NEEDS-OWNER.md'
const LOG = 'C:/home/.claude/owner-queue/problems.log'
const TWICE = 'Options line: a key appears twice'

const GIVEN = '(b) no | pane, 2026-11-20 11:00:00, session session-2'
const NOTE = 'keep it short | pane, 2026-11-20 11:05:00, session session-2'
const TOOLS_GIVEN = '(a) yes | pane, 2026-11-20 11:10:00, session session-2'

const OWN_FILE = `# NEEDS-OWNER

## Actions

### [ ] Own thing
`

const ASKED = `# NEEDS-OWNER

## Decisions

### [ ] Who merges
- Options: (a) yes; (b) no
- Session: session-1
- Answer: ${GIVEN}
- Note: ${NOTE}

### [ ] Malformed
- Options: (a) one; (b) two; (a) three
`

const TOOLS_FILE = `# NEEDS-OWNER

## Decisions

### [ ] Tools thing
- Options: (a) yes; (b) no
- Answer: ${TOOLS_GIVEN}
`

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

const WHO = 'decision:Who merges'
const place = (file: string, id = WHO) => `${file}|${id}`

function world(
  on: On,
  files: Map<string, string>,
  start: Record<string, unknown>,
  ids: { now: string; failOnce?: string; hasKeys?: boolean },
) {
  const sent: string[] = []
  const toasts: string[] = []
  const writes: string[] = []
  const store = new Map(Object.entries(start))
  mock.clock(on, { now: Date.UTC(2026, 10, 28, 12, 0, 0) })
  mock.env(on, { USERPROFILE: 'C:/home' })
  on('store.get', ($$, e) => ({ value: store.get(e.key) }))
  on('store.set', ($$, e) => {
    if (ids.failOnce === e.key) {
      ids.failOnce = undefined
      throw new Error('the store is busy')
    }
    writes.push(e.key)
    store.set(e.key, JSON.parse(JSON.stringify(e.value)))

    return { value: undefined }
  })
  on('store.delete', ($$, e) => {
    store.delete(e.key)

    return { value: undefined }
  })
  on('store.keys', () => {
    if (ids.hasKeys === false) throw new Error('no keys here')

    return { value: [...store.keys()] }
  })
  // The engine may give the session's own relative path as an absolute one;
  // the test's absolute queue paths are never the session's own.
  const named = [OLD, NEW, TWIN, TOOLS].map(one => one.toLowerCase())
  const key = (path: string) => {
    const slashed = path.replaceAll('\\', '/')
    const isNamed = named.includes(slashed.toLowerCase())

    return !files.has(slashed) && !isNamed && slashed.endsWith(`/${OWN}`)
      ? OWN
      : slashed
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

  return { sent, toasts, writes, store }
}

test(
  'after a move each record goes to the new path, and an Answer and a Note are carried once',
  { options: { queues: [NEW] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [NEW, ASKED],
    ])
    const ids = { now: 'reader' }
    const { sent, toasts, writes, store } = world(on, files, {
      answers: { [place(OLD)]: GIVEN },
      notes: { [place(OLD)]: [NOTE] },
      logged: [`${place(OLD, 'decision:Malformed')}|${TWICE}`],
    }, ids)

    // Another session reads first: the records move then.
    await $.command.run({ command: 'owner', args: '' })
    expect(store.get('answers')).toEqual({ [place(NEW)]: GIVEN })
    expect(store.get('notes')).toEqual({ [place(NEW)]: [NOTE] })
    expect(store.get('logged')).toEqual([
      `${place(NEW, 'decision:Malformed')}|${TWICE}`,
    ])
    // The malformed entry was logged before the move: not logged again.
    expect(files.has(LOG)).toBe(false)

    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    expect(
      await ui.findAll({ type: 'Text', text: /Not written by the pane/ }),
    ).toHaveLength(0)

    // The session the entry names is told, once.
    ids.now = 'session-1'
    await ui.press({ key: 'refresh' })
    expect(sent).toHaveLength(1)
    expect(sent[0]).toContain('Decision: Who merges')
    expect(sent[0]).toContain('keep it short')
    await ui.press({ key: 'refresh' })
    expect(sent).toHaveLength(1)

    // A second read finds nothing to move and writes nothing.
    const before = writes.length
    await $.command.run({ command: 'owner', args: '' })
    expect(writes.slice(before)).toEqual([])
    expect(toasts.filter(one => one.includes('not moved'))).toHaveLength(0)

    // No queue file was touched.
    expect(files.get(NEW)).toBe(ASKED)
    expect(files.get(OWN)).toBe(OWN_FILE)
    await ui.unmount()
  },
)

test(
  'with two queues only the one that moved changes; a live path in other case is left as written',
  { options: { queues: [NEW, TOOLS] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [NEW, ASKED],
      [TOOLS, TOOLS_FILE],
    ])
    const upper = 'C:/WORK/tools/.claude/memory/NEEDS-OWNER.md'
    const { store } = world(on, files, {
      answers: {
        [place(OLD)]: GIVEN,
        [place(TOOLS, 'decision:Tools thing')]: TOOLS_GIVEN,
        [place(upper, 'decision:Other')]: 'kept',
      },
    }, { now: 'reader' })

    await $.command.run({ command: 'owner', args: '' })

    expect(store.get('answers')).toEqual({
      [place(TOOLS, 'decision:Tools thing')]: TOOLS_GIVEN,
      [place(upper, 'decision:Other')]: 'kept',
      [place(NEW)]: GIVEN,
    })
  },
)

test(
  "every session's delivered and noted records move, joined with what is already at the new path",
  { options: { queues: [NEW] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [NEW, ASKED],
    ])
    const { store } = world(on, files, {
      answers: { [place(OLD)]: 'the old line', [place(NEW)]: GIVEN },
      notes: { [place(OLD)]: ['one', 'two'], [place(NEW)]: ['two', 'three'] },
      'delivered:session-7': { [place(OLD)]: 'the old line', [place(NEW)]: GIVEN },
      'noted:session-7': { [place(OLD)]: ['one'], [place(NEW)]: ['three'] },
      'delivered:session-8': { [place(OLD)]: GIVEN },
      'done:session-7': ['Action: Fire it (#1), marked done 2026-11-20 11:00:00'],
    }, { now: 'reader' })

    await $.command.run({ command: 'owner', args: '' })

    expect(store.get('answers')).toEqual({ [place(NEW)]: GIVEN })
    expect(store.get('notes')).toEqual({ [place(NEW)]: ['two', 'three', 'one'] })
    expect(store.get('delivered:session-7')).toEqual({ [place(NEW)]: GIVEN })
    expect(store.get('noted:session-7')).toEqual({ [place(NEW)]: ['three', 'one'] })
    expect(store.get('delivered:session-8')).toEqual({ [place(NEW)]: GIVEN })
    expect(store.get('done:session-7')).toEqual([
      'Action: Fire it (#1), marked done 2026-11-20 11:00:00',
    ])
  },
)

test(
  'a stop between two records is finished by the next read, and nothing is said again',
  { options: { queues: [NEW] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [NEW, ASKED],
    ])
    const ids: { now: string; failOnce?: string } = {
      now: 'session-1',
      failOnce: 'answers',
    }
    // Before the move this session was already told both.
    const { sent, store } = world(on, files, {
      answers: { [place(OLD)]: GIVEN },
      notes: { [place(OLD)]: [NOTE] },
      'delivered:session-1': { [place(OLD)]: GIVEN },
      'noted:session-1': { [place(OLD)]: [NOTE] },
    }, ids)

    await $.command.run({ command: 'owner', args: '' })
    // The session's records moved; the shared ones stopped at the failed write.
    expect(store.get('delivered:session-1')).toEqual({ [place(NEW)]: GIVEN })
    expect(store.get('noted:session-1')).toEqual({ [place(NEW)]: [NOTE] })
    expect(store.get('answers')).toEqual({ [place(OLD)]: GIVEN })

    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    await ui.press({ key: 'refresh' })
    expect(store.get('answers')).toEqual({ [place(NEW)]: GIVEN })
    expect(store.get('notes')).toEqual({ [place(NEW)]: [NOTE] })
    await ui.press({ key: 'refresh' })
    expect(sent).toHaveLength(0)
    await ui.unmount()
  },
)

test(
  'two queues with the same folder name: nothing moves, and the path is said once',
  { options: { queues: [NEW, TWIN] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [NEW, ASKED],
      [TWIN, ASKED],
    ])
    const start = { answers: { [place(OLD)]: GIVEN } }
    const { store, toasts } = world(on, files, start, { now: 'reader' })

    await $.command.run({ command: 'owner', args: '' })
    await $.command.run({ command: 'owner', args: '' })

    expect(store.get('answers')).toEqual({ [place(OLD)]: GIVEN })
    const said = toasts.filter(one => one.includes('not moved'))
    expect(said).toHaveLength(1)
    expect(said[0]).toContain(OLD)
  },
)

test(
  'no queue read now holds an entry found under the old path: nothing moves',
  { options: { queues: [NEW] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [NEW, TOOLS_FILE],
    ])
    const { store, toasts } = world(on, files, {
      answers: { [place(OLD)]: GIVEN },
    }, { now: 'reader' })

    await $.command.run({ command: 'owner', args: '' })

    expect(store.get('answers')).toEqual({ [place(OLD)]: GIVEN })
    expect(toasts.filter(one => one.includes('not moved'))).toHaveLength(1)
  },
)

test(
  "a queue that is still there, though this session does not read it, is not moved",
  { options: { queues: [NEW] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [NEW, ASKED],
      [OLD, ASKED],
    ])
    const { store, toasts } = world(on, files, {
      answers: { [place(OLD)]: GIVEN },
      notes: { [`${OWN}|${WHO}`]: [NOTE] },
    }, { now: 'reader' })

    await $.command.run({ command: 'owner', args: '' })

    expect(store.get('answers')).toEqual({ [place(OLD)]: GIVEN })
    expect(store.get('notes')).toEqual({ [`${OWN}|${WHO}`]: [NOTE] })
    expect(toasts.filter(one => one.includes('not moved'))).toHaveLength(0)
  },
)

test(
  "where the store lists no keys, a session moves only its own records and the shared ones",
  { options: { queues: [NEW] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [NEW, ASKED],
    ])
    const { store } = world(on, files, {
      answers: { [place(OLD)]: GIVEN },
      'delivered:session-1': { [place(OLD)]: GIVEN },
      'delivered:session-7': { [place(OLD)]: GIVEN },
    }, { now: 'session-1', hasKeys: false })

    await $.command.run({ command: 'owner', args: '' })

    expect(store.get('answers')).toEqual({ [place(NEW)]: GIVEN })
    expect(store.get('delivered:session-1')).toEqual({ [place(NEW)]: GIVEN })
    expect(store.get('delivered:session-7')).toEqual({ [place(OLD)]: GIVEN })
  },
)

test(
  "a session whose own queue file is missing is told so once, with its path",
  { options: { queues: [NEW] } },
  async ($, on) => {
    const files = new Map([[NEW, ASKED]])
    const { toasts } = world(on, files, {}, { now: 'reader' })

    await $.command.run({ command: 'owner', args: '' })
    await $.command.run({ command: 'owner', args: '' })

    const said = toasts.filter(one => one.includes('own queue file was not found'))
    expect(said).toHaveLength(1)
    expect(said[0]).toContain(OWN)
  },
)
