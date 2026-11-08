import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code/testing'

const OWN = '.claude/memory/NEEDS-OWNER.md'
const DYN = 'C:/work/dynasty/.claude/memory/NEEDS-OWNER.md'
const LOG = 'C:/home/.claude/owner-queue/problems.log'

const OWN_FILE = `# NEEDS-OWNER

## Decisions

### [ ] Own thing
- Options: (a) one; (b) two
`

const DYN_FILE = `# NEEDS-OWNER

## Decisions

### [ ] Their thing
- Options: (a) yes; (b) no
`

const PROMPT = {
  model: 'model',
  promptModel: 'model',
  surfaces: [],
  tools: [],
  outputStyle: null,
  traits: [],
} as const

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

function world(
  on: On,
  files: Map<string, string>,
  store: Record<string, unknown> = {},
) {
  const sent: string[] = []
  const toasts: string[] = []
  mock.store(on, store)
  mock.clock(on, { now: Date.UTC(2026, 10, 8, 12, 0, 0) })
  mock.env(on, { USERPROFILE: 'C:/home' })
  // The engine may give the session's own relative path as an absolute one.
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
  on('session.id', () => ({ value: 'session-1' }))
  on('prompt.submit', ($$, e) => {
    sent.push(e.text)

    return { text: e.text }
  })
  on('prompt.compose', () => ({ sections: [] }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', ($$, e) => {
    toasts.push(e.text)

    return { value: undefined }
  })
  on('ui.open', () => ({ value: { isPlaced: true } }))

  return { sent, toasts }
}

test(
  'two queue files are read and grouped by repo folder',
  { options: { queues: [DYN] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [DYN, DYN_FILE],
    ])
    world(on, files)

    await $.command.run({ command: 'owner', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })

    expect(await ui.find({ text: /^this project$/ })).toBeDefined()
    expect(await ui.find({ text: /^dynasty$/ })).toBeDefined()
    expect(await ui.find({ key: 'row:decision:Own thing' })).toBeDefined()
    expect(await ui.find({ key: `row:${DYN}|decision:Their thing` })).toBeDefined()
    // Numbered across both, as `/owner show d2` numbers them.
    expect(await ui.find({ text: /1\. Own thing/ })).toBeDefined()
    expect(await ui.find({ text: /2\. Their thing/ })).toBeDefined()
    expect(await ui.find({ text: /Source: .*NEEDS-OWNER\.md, C:\/work\/dynasty/ })).toBeDefined()
    const shown = await $.command.run({ command: 'owner', args: 'show d2' })
    expect(JSON.stringify(shown)).toContain('Their thing')
    await ui.unmount()
  },
)

test(
  'an answer is written into the file its entry came from',
  { options: { queues: [DYN] } },
  async ($, on) => {
    const files = new Map([
      [OWN, OWN_FILE],
      [DYN, DYN_FILE],
    ])
    const { sent, toasts } = world(on, files)

    await $.command.run({ command: 'owner', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    await ui.press({ key: 'expand-all' })
    await ui.press({ key: `pick:${DYN}|decision:Their thing:b` })
    expect(files.get(DYN)).toBe(DYN_FILE)
    await ui.press({ key: 'submit' })

    expect(files.get(DYN)).toContain('- Answer: (b) no | pane, 2026-11-08 ')
    expect(files.get(OWN)).toBe(OWN_FILE)
    expect(toasts).toContain('Submitted: 1')
    expect(sent).toHaveLength(1)
    expect(sent[0]).toContain('Decision: Their thing')
    await ui.unmount()
  },
)

test(
  'the pane keeps its record of what it wrote per file, so two queues stay apart',
  { options: { queues: [DYN] } },
  async ($, on) => {
    const same = '## Decisions\n\n### [ ] Same title\n- Options: (a) one; (b) two\n'
    const files = new Map([
      [OWN, same],
      [DYN, same],
    ])
    world(on, files)

    await $.command.run({ command: 'owner', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    await ui.press({ key: 'expand-all' })
    await ui.press({ key: `pick:${DYN}|decision:Same title:a` })
    await ui.press({ key: 'submit' })
    const line = /- Answer: .*/.exec(files.get(DYN) ?? '')?.[0]
    expect(line).toContain('| pane, ')
    expect(
      await ui.findAll({ type: 'Text', text: /Not written by the pane/ }),
    ).toHaveLength(0)

    // The same line typed into the other queue by hand is not the pane's.
    files.set(OWN, `${same}${line}\n`)
    await ui.press({ key: 'refresh' })
    expect(
      await ui.findAll({ type: 'Text', text: /Not written by the pane/ }),
    ).toHaveLength(1)
    await ui.unmount()
  },
)

test(
  'a session whose own project has no queue is told its id from a listed one',
  { options: { queues: [DYN] } },
  async ($, on) => {
    const files = new Map([[DYN, DYN_FILE]])
    world(on, files)

    await $.command.run({ command: 'owner', args: '' })
    const made = await $.prompt.compose(PROMPT)

    expect(JSON.stringify(made)).toContain("this session's id is session-1")
  },
)

test('without a listed queue a project with no queue is told nothing', async ($, on) => {
  world(on, new Map())

  await $.command.run({ command: 'owner', args: '' })
  const made = await $.prompt.compose(PROMPT)

  expect(JSON.stringify(made)).not.toContain("this session's id")
})

test(
  'an answer to an entry in a listed queue reaches the session that raised it',
  { options: { queues: [DYN] } },
  async ($, on) => {
    const line = '(b) no | pane, 2026-11-08 11:00:00, session session-2'
    const asked = `## Decisions\n\n### [ ] Who merges\n- Options: (a) yes; (b) no\n- Session: session-1\n`
    const files = new Map([[DYN, asked]])
    // The pane's record of the line another session's pane will write.
    const { sent } = world(on, files, {
      answers: { [`${DYN}|decision:Who merges`]: line },
    })

    // `/owner` may not submit a prompt itself; a refresh in the pane does.
    await $.command.run({ command: 'owner', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    expect(sent).toHaveLength(0)

    // Another session's pane answers it.
    files.set(DYN, `${asked}- Answer: ${line}\n`)
    await ui.press({ key: 'refresh' })
    expect(sent).toHaveLength(1)
    expect(sent[0]).toContain('carried to this session')
    expect(sent[0]).toContain('Decision: Who merges')

    await ui.press({ key: 'refresh' })
    expect(sent).toHaveLength(1)
    await ui.unmount()
  },
)

test(
  'an entry the parser cannot draw is logged once, without field values',
  { options: { queues: [DYN] } },
  async ($, on) => {
    const broken = `## Decisions\n\n### [ ] Same key twice\n- Options: (a) one; (b) two; (a) three\n- Context: private words\n`
    const files = new Map([[DYN, broken]])
    world(on, files)

    await $.command.run({ command: 'owner', args: '' })
    await $.command.run({ command: 'owner', args: '' })
    await $.command.run({ command: 'owner', args: '' })

    const lines = (files.get(LOG) ?? '').split('\n').filter(one => one !== '')
    expect(lines).toHaveLength(1)
    expect(lines[0]).toBe(
      `2026-11-08 ${lines[0].slice(11, 19)} | ${DYN} | Same key twice | Options line: a key appears twice`,
    )
    expect(lines[0]).not.toContain('private')
    expect(lines[0]).not.toContain('three')

    // Fixed, then broken again: the return of the problem is logged.
    files.set(DYN, broken.replace('(a) three', '(c) three'))
    await $.command.run({ command: 'owner', args: '' })
    files.set(DYN, broken)
    await $.command.run({ command: 'owner', args: '' })
    expect((files.get(LOG) ?? '').split('\n').filter(one => one !== '')).toHaveLength(2)
  },
)
