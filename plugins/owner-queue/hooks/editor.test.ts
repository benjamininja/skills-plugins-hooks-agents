import { expect, mock, test } from 'claude-code/testing'

const QUEUE = `# NEEDS-OWNER

## Actions

### [ ] Mine to do
- Ticket: #92
- Session: session-1
`

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

test('a longer comment is written in the text editor and sent from its file', async ($, on) => {
  // The test's hooks stand for the disk: the queue file and the draft files.
  const disk = new Map<string, string>()
  const ran: string[][] = []
  const sent: string[] = []
  const toasts: string[] = []
  const isDraft = (path: string) => /[\\/]drafts[\\/]/.test(path)
  mock.store(on)
  mock.clock(on, { now: Date.UTC(2026, 9, 12, 12, 0, 0) })
  on('fs.read', ($$, e) => {
    if (e.path.endsWith('.git')) throw new Error('a folder')
    if (!isDraft(e.path)) return { value: disk.get('queue') ?? QUEUE }
    const saved = disk.get(e.path)
    if (saved === undefined) throw new Error('missing')

    return { value: saved }
  })
  on('fs.write', ($$, e) => {
    disk.set(isDraft(e.path) ? e.path : 'queue', e.text)

    return { value: undefined }
  })
  on('process.run', ($$, e) => {
    ran.push([...e.argv])

    return {
      value: {
        exitCode: e.argv[0] === 'git' ? 128 : 0,
        stdout: '',
        stderr: '',
      },
    }
  })
  on('session.id', () => ({ value: 'session-1' }))
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
  const id = 'action:Mine to do'

  // The button writes the draft file and hands it to the system's opener.
  await ui.press({ key: `edit:${id}` })
  const [path] = [...disk.keys()].filter(isDraft)
  expect(path).toMatch(/[\\/]drafts[\\/]action-mine-to-do\.txt$/)
  expect(disk.get(path)).toBe('')
  const opened = ran.filter(argv => argv[0] !== 'git')
  expect(opened).toHaveLength(1)
  expect(opened[0].at(-1)?.replaceAll('\\', '/')).toBe(
    path.replaceAll('\\', '/'),
  )
  expect(toasts.at(-1)).toContain('Opened in your text editor')
  expect(await ui.find({ key: `path:${id}` })).toBeDefined()

  // What the owner saves there is drawn at the next read, and sent as one line.
  disk.set(path, 'first line\nsecond line\n')
  await ui.press({ key: 'refresh' })
  expect(await ui.find({ type: 'Text', text: /second line/ })).toBeDefined()
  await ui.press({ key: `send:${id}` })
  expect(disk.get('queue')).toContain('- Note: first line second line | pane, ')
  expect(sent[0]).toContain('Comment: first line second line')
  // The sent draft is emptied, and the box is closed.
  expect(disk.get(path)).toBe('')
  expect(await ui.find({ key: `path:${id}` })).toBe(undefined)

  // Cancel empties the draft and sends nothing.
  await ui.press({ key: `edit:${id}` })
  disk.set(path, 'dropped')
  await ui.press({ key: `cancel:${id}` })
  expect(disk.get(path)).toBe('')
  expect(sent).toHaveLength(1)

  await ui.unmount()
})
