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
  await ui.unmount()
})
