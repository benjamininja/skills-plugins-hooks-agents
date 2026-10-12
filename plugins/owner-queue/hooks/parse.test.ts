import { expect, test } from 'claude-code/testing'

import {
  answer,
  answerOf,
  codes,
  commit,
  detail,
  hint,
  message,
  options,
  parse,
  recommended,
  reference,
  report,
  shown,
  spans,
  summary,
  tick,
  toMarkdown,
  unanswer,
} from './parse'

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

const KEYED = `## Decisions

### [ ] Who merges
- Ticket: #166
- Options: (a) The builder; it is green. (b) Two-key merge;
  (c) The owner
- Recommended: (b), because two sets of eyes

### [ ] Second one
- Options: Yes; No
`

test('reads options in both written forms', () => {
  const [keyed, plain] = parse(KEYED)

  expect(options(keyed)).toEqual([
    { key: 'a', text: 'The builder; it is green' },
    { key: 'b', text: 'Two-key merge' },
    { key: 'c', text: 'The owner' },
  ])
  expect(options(plain)).toEqual([
    { key: 'a', text: 'Yes' },
    { key: 'b', text: 'No' },
  ])
  expect(options(parse(FILE)[1])).toEqual([])
})

test('finds the recommended option by key or by its text', () => {
  expect(recommended(parse(KEYED)[0])).toBe('b')
  expect(recommended(parse(KEYED)[1])).toBe(undefined)
  expect(recommended(parse(FILE)[0])).toBe('a')
})

test('an answer is written into its own entry, replaced, and removed', () => {
  const [first, second] = parse(KEYED)
  const once = answer(KEYED, first, '(a) The builder | pane')
  const twice = answer(once, first, '(b) Two-key merge | pane')

  expect(answerOf(parse(twice)[0])).toBe('(b) Two-key merge | pane')
  expect(twice.match(/- Answer:/g)?.length).toBe(1)
  expect(answerOf(parse(twice)[1])).toBe(undefined)
  expect(twice.indexOf('- Answer:')).toBeLessThan(twice.indexOf('### [ ] Second'))
  expect(unanswer(twice, first)).toBe(KEYED)

  const last = answer(KEYED, second, '(b) No | pane')
  expect(answerOf(parse(last)[1])).toBe('(b) No | pane')
  expect(unanswer(last, second)).toBe(KEYED)
})

test('an answer keeps the CRLF line ends of a file', () => {
  const crlf = KEYED.replaceAll('\n', '\r\n')
  const [first, second] = parse(crlf)
  const written = answer(answer(crlf, first, '(c) x'), second, '(a) Yes')

  expect(written.replaceAll('\r\n', '')).not.toContain('\n')
  expect(written.replaceAll('\r\n', '')).not.toContain('\r')
  expect(answerOf(parse(written)[0])).toBe('(c) x')
  expect(answerOf(parse(written)[1])).toBe('(a) Yes')
})

test('an answered decision leaves the count, and its detail', () => {
  const [first] = parse(KEYED)
  const items = parse(answer(KEYED, first, '(a) The builder | pane'))

  expect(summary(items)).toBe('Owner: 1 decision, 0 actions, 1 answered')
  expect(detail(items[0])).not.toContain('Answer')
})

test('names an item shortly, and words the chat message', () => {
  const [first] = parse(KEYED)

  expect(reference(first, 0)).toBe('Decision 1: Who merges (#166)')
  expect(reference(parse(FILE)[1])).toBe('Action: Create the Supabase project')
  const sent = message(first, { key: 'b', text: 'Two-key merge' })
  expect(sent).toContain('Decision: Who merges')
  expect(sent).toContain('Ticket: #166')
  expect(sent).toContain('Answer: (b) Two-key merge')
})

test('draws both lists, an empty one included', () => {
  const drawn = toMarkdown(parse('## Decisions\n### One\n- Context: c\n'))

  expect(drawn).toContain('## Decisions for you (1)')
  expect(drawn).toContain('- **Context:** c')
  expect(drawn).toContain('## Actions by your hand (0)')
})

test('everything staged is applied in one pass, and the lost are named', () => {
  const made = commit(
    KEYED + '\n## Actions\n\n### [ ] Run it\n- Ticket: #9\n',
    {
      'decision:Who merges': { key: 'b', text: 'Two-key merge' },
      'action:Run it': 'done',
      'action:Gone': 'done',
    },
    chosen => `(${chosen.key}) ${chosen.text} | pane`,
  )

  expect(made.text).toContain('- Answer: (b) Two-key merge | pane')
  expect(made.text).toContain('### [x] Run it')
  expect(made.missing).toEqual(['action:Gone'])
  expect(made.answered.map(one => one.line)).toEqual(['(b) Two-key merge | pane'])
  const sent = report(made)
  expect(sent).toContain('Answer: (b) Two-key merge')
  expect(sent).toContain('- Action: Run it (#9)')
  expect(commit(KEYED, {}, () => '').text).toBe(KEYED)
})

test('finds each code span of an entry once', () => {
  const [item] = parse(
    '## Actions\n### Run\n- Steps: run `a b`, then `c`\n- Context: `a b` again\n- Answer: `no`\n',
  )

  expect(codes(item)).toEqual(['a b', 'c'])
  expect(codes(parse(KEYED)[0])).toEqual([])
  expect(spans('use `x y` or `z`, `x y`')).toEqual(['x y', 'z'])
  expect(detail(parse(FILE)[0], ['options'])).not.toContain('Options')
})

test('a fenced block is kept whole, and a heading inside it is not read', () => {
  const [item, next] = parse(
    [
      '## Actions',
      '### Paste',
      '- Steps: add:',
      '  ```json',
      '    "a",',
      '    "b"',
      '  ## not a section',
      '  ```',
      '  then save.',
      '### Next',
    ].join('\n'),
  )

  expect(item.blocks).toEqual(['  "a",\n  "b"\n## not a section'])
  expect(item.fields[0].value).toBe('add: (block 1) then save.')
  expect(detail(item)).toContain('Block 1:\n```\n  "a",')
  expect(next.title).toBe('Next')
  expect(parse(FILE)[0].blocks).toBe(undefined)
})

test('prints all entries, or one by its number', () => {
  const items = parse(FILE)

  expect(shown(items)).toContain('## Decisions for you (1)')
  expect(shown(items, ' a1')).toContain('**Action 1: Create the Supabase project**')
  expect(shown(items, 'a1')).toContain('- **Blocks:** stage C')
  expect(shown(items, '1')).toContain('Decision 1: Claim default contract (#130)')
  expect(shown(items, 'd4')).toBe('No entry d4 is waiting.')
  expect(shown(items, 'x')).toContain('Use d1, a2 or a number')
})
