import { expect, test } from 'claude-code/testing'

const FILE = `# NEEDS-OWNER

## Decisions

## Actions

### [ ] Fire the first login
- Ticket: #92
`

const PANE = 'owner-queue'
const BAND = {
  plugin: 'owner-queue',
  component: 'AbovePrompt',
  props: { hasSurvey: false },
} as const

test('the band button hides the pane and shows it again', async ($, on) => {
  // The test's hooks stand for the engine: one pane record, as a surface keeps.
  let isUp = false
  let canPlace = true
  on('fs.read', () => ({ value: FILE }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.open', () => {
    isUp = true

    return {
      value: canPlace
        ? { isPlaced: true }
        : { isPlaced: false, reason: 'too narrow' },
    }
  })
  on('ui.close', () => {
    isUp = false

    return { value: undefined }
  })
  on('ui.panes', () => ({
    value: isUp
      ? [
          {
            id: PANE,
            title: 'Needs owner',
            isShown: canPlace,
            isFocused: false,
            isPlaced: canPlace,
          },
        ]
      : [],
  }))

  for (const surface of ['terminal', 'desktop'] as const) {
    isUp = false
    canPlace = true
    await $.command.run({ command: 'owner', args: '' })

    const ui = await $.ui.mount({ ...BAND, surface })
    const label = async () => (await ui.find({ key: 'toggle' }))?.text

    expect(await label()).toBe('Hide queue')

    await ui.press({ key: 'toggle' })
    expect(isUp).toBe(false)
    expect(await label()).toBe('Show queue')

    await ui.press({ key: 'toggle' })
    expect(isUp).toBe(true)
    expect(await label()).toBe('Hide queue')

    // A pane the surface could not seat does not read as shown.
    await ui.press({ key: 'toggle' })
    canPlace = false
    await ui.press({ key: 'toggle' })
    expect(await label()).toBe('Show queue')

    await ui.unmount()
  }
})

test('a read of the queue never opens the pane by itself', async ($, on) => {
  let opened = 0
  on('fs.read', () => ({ value: FILE }))
  on('ui.status', () => ({ value: undefined }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.open', () => {
    opened += 1

    return { value: { isPlaced: true } }
  })

  // `/owner show` reads the queue and finds its entries new, and opens nothing.
  await $.command.run({ command: 'owner', args: 'show' })
  expect(opened).toBe(0)

  await $.command.run({ command: 'owner', args: '' })
  expect(opened).toBe(1)
})
