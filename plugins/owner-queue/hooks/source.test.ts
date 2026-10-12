import { expect, mock, test } from 'claude-code/testing'

const FILE = `## Decisions

## Actions

### [ ] Fire the first login
`

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

test('a session in a worktree reads the queue of the main checkout', async ($, on) => {
  const read: string[] = []
  mock.store(on)
  mock.clock(on)
  on('fs.read', ($$, e) => {
    read.push(e.path)

    return {
      value: e.path.endsWith('.git')
        ? 'gitdir: C:/repo/.git/worktrees/builder-1\n'
        : FILE,
    }
  })
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))

  await $.command.run({ command: 'owner', args: '' })

  expect(read.map(path => path.replaceAll('\\', '/'))).toContain(
    'C:/repo/.claude/memory/NEEDS-OWNER.md',
  )
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect(
    await ui.find({ text: /Source: C:\/repo\/\.claude\/memory\/NEEDS-OWNER\.md/ }),
  ).toBeDefined()
  expect(await ui.find({ text: /Reading this session's copy/ })).toBe(undefined)
  await ui.unmount()
})

test('a session that cannot find the main checkout says so', async ($, on) => {
  mock.store(on)
  mock.clock(on)
  on('fs.read', ($$, e) => {
    if (e.path.endsWith('.git')) throw new Error('a folder')

    return { value: FILE }
  })
  on('process.run', () => ({
    value: { exitCode: 128, stdout: '', stderr: 'not a repository' },
  }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.open', () => ({ value: { isPlaced: true } }))

  await $.command.run({ command: 'owner', args: '' })
  // `/owner show a1` answers with the entry as text for the transcript.
  const printed = await $.command.run({ command: 'owner', args: 'show a1' })
  expect(JSON.stringify(printed)).toContain('Action 1: Fire the first login')
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect(
    await ui.find({ text: /Reading this session's copy, not the main checkout's/ }),
  ).toBeDefined()
  await ui.unmount()
})
