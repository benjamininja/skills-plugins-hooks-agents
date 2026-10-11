import { expect, test } from 'claude-code/testing'

import { detail, hint, parse, summary, tick, toMarkdown } from './parse'

const FILE = `# NEEDS-OWNER

Intro text that is not an item.

## Decisions

### [ ] Claim default contract
- Ticket: #130
- Context: Fantrax shows FA on 41 of 46 claims
  of minors-eligible players.
- Options: FA; Minor
- Recommended: FA

### [x] Already answered
- Context: done

## Actions

### Create the Supabase project
Free tier is enough.
- Steps: create it, put the URL in .env
- Blocks: stage C

## Notes

### Not an item
- Context: ignored
`

test('reads open decisions and actions with their fields', () => {
  const items = parse(FILE)

  expect(items.map(item => `${item.kind}:${item.title}`)).toEqual([
    'decision:Claim default contract',
    'action:Create the Supabase project',
  ])
  expect(items[0].fields[1]).toEqual({
    label: 'Context',
    value: 'Fantrax shows FA on 41 of 46 claims of minors-eligible players.',
  })
  expect(items[1].fields[0]).toEqual({
    label: 'Context',
    value: 'Free tier is enough.',
  })
})

test('summarises the counts, and nothing for an empty queue', () => {
  expect(summary(parse(FILE))).toBe('Owner: 1 decision, 1 action')
  expect(summary(parse('## Decisions\n\n## Actions\n'))).toBe(undefined)
})

test('ticking an item takes it, and only it, off the list', () => {
  const items = parse(FILE)
  const ticked = tick(FILE, items[1])

  expect(parse(ticked).map(item => item.title)).toEqual([
    'Claim default contract',
  ])
  expect(ticked).toContain('### [x] Create the Supabase project')
})

test('a collapsed row shows its ticket and what it blocks', () => {
  const items = parse(FILE)

  expect(hint(items[0])).toBe('#130')
  expect(hint(items[1])).toBe('blocks: stage C')
  expect(detail(items[0])).toContain('- **Options:** FA; Minor')
})

test('draws both lists, an empty one included', () => {
  const drawn = toMarkdown(parse('## Decisions\n### One\n- Context: c\n'))

  expect(drawn).toContain('## Decisions for you (1)')
  expect(drawn).toContain('- **Context:** c')
  expect(drawn).toContain('## Actions by your hand (0)')
})
