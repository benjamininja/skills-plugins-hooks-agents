import { expect, mock, test } from 'claude-code/testing'
import type { Engine, On } from 'claude-code/testing'
import { WHY, instruction, roleOf } from './sessions'

const QUEUE_PATH = '.claude/memory/NEEDS-OWNER.md'
const QUEUE = `# NEEDS-OWNER

## Decisions

### [ ] Who merges
- Options: (a) yes; (b) no
- Session: planner-2
`
const START = Date.UTC(2026, 10, 14, 9, 0, 0)
const MINUTE = 60000

const PANE = {
  plugin: 'owner-queue',
  component: 'Pane',
  requestId: 'owner-queue',
  props: {},
} as const

type File = { text: string; mtime: number }

/** The engine beneath the mod: a file system with file times, a clock, a chat. */
function world(on: On) {
  const files = new Map<string, File>([[QUEUE_PATH, { text: QUEUE, mtime: START }]])
  const sent: string[] = []
  const toasts: string[] = []
  const copied: string[] = []
  const ids = { now: 'planner-1' }
  const faults = { records: false }
  mock.store(on)
  const time = mock.clock(on, { now: START })
  // The queue is asked for by its absolute path; every other file by its own.
  const slash = (path: string) => {
    const one = path.replaceAll('\\', '/')

    return one.endsWith(`/${QUEUE_PATH}`) ? QUEUE_PATH : one
  }
  on('fs.read', ($$, e) => {
    if (e.path.endsWith('.git')) throw new Error('a folder')
    const one = files.get(slash(e.path))
    if (one === undefined) throw new Error('missing')

    return { value: one.text }
  })
  on('fs.write', ($$, e) => {
    if (faults.records && slash(e.path).includes('/sessions/'))
      throw new Error('the disk is full')
    files.set(slash(e.path), { text: e.text, mtime: time.now() })

    return { value: undefined }
  })
  on('fs.exists', ($$, e) => ({ value: files.has(slash(e.path)) }))
  on('fs.stat', ($$, e) => {
    const one = files.get(slash(e.path))
    if (one === undefined) throw new Error('ENOENT')

    return {
      value: { kind: 'file' as const, size: one.text.length, mtimeMs: one.mtime, isLink: false },
    }
  })
  on('fs.list', ($$, e) => {
    const dir = `${slash(e.path ?? '')}/`
    const value = [...files]
      .filter(([path]) => path.startsWith(dir) && !path.slice(dir.length).includes('/'))
      .map(([path, one]) => ({
        name: path.slice(dir.length),
        kind: 'file' as const,
        size: one.text.length,
        mtimeMs: one.mtime,
        isLink: false,
      }))
    if (value.length === 0) throw new Error('ENOENT')

    return { value }
  })
  on('process.run', () => ({
    value: { exitCode: 128, stdout: '', stderr: 'not a repository' },
  }))
  on('session.id', () => ({ value: ids.now }))
  on('session.end', ($$, e) => ({ sessionId: e.sessionId }))
  on('turn.start', ($$, e) => ({ turnId: e.turnId }))
  on('turn.complete', () => ({ text: '' }))
  on('session.measure', ($$, e) => ({ changed: e.changed }))
  on('classic.SessionStart', () => ({}))
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
  on('ui.copy', ($$, e) => {
    copied.push(e.text)

    return { value: { isCopied: true } }
  })

  const find = (suffix: string) => [...files.keys()].find(path => path.endsWith(suffix))
  const record = (id: string) => {
    const path = find(`/sessions/${id}.json`)

    return path === undefined ? undefined : JSON.parse(files.get(path)?.text ?? '')
  }
  /** The mod's data folder, read off this session's own record. */
  const root = (id = 'planner-1') => {
    const path = find(`/sessions/${id}.json`) ?? ''

    return path.slice(0, -`/sessions/${id}.json`.length)
  }
  /** Another session's own record, as that session's mod would write it. */
  const other = (id: string, fields: Record<string, unknown>) =>
    files.set(`${root()}/sessions/${id}.json`, {
      text: JSON.stringify({
        id,
        role: 'central-builder-manager',
        name: id,
        state: 'idle',
        turnStart: 0,
        turnEnd: 0,
        tokens: 0,
        beat: time.now(),
        ran: 0,
        sent: {},
        ...fields,
      }),
      mtime: time.now(),
    })
  const lineOf = (id: string) => `${root()}/start-lines/${id}.md`

  return { files, sent, toasts, copied, time, ids, faults, find, record, root, other, lineOf }
}

const enroll = (
  $: Engine,
  id = 'planner-1',
  agentType: string | null = 'central-planner',
  source: 'startup' | 'clear' = 'startup',
) =>
  $.classic.SessionStart({
    source,
    session_id: id,
    ...(agentType === null ? {} : { agent_type: agentType }),
  })

const start = ($: Engine, turnId: string) => $.turn.start({ text: '', turnId })
const end = ($: Engine, turnId: string) =>
  $.turn.complete({ answer: '', durationMs: 1, isAborted: false, turnId, reason: 'answer' })
const measure = ($: Engine, tokens: number) =>
  $.session.measure({
    context: { tokens, window: 1000000 },
    rateLimits: [],
    changed: ['context'],
  })
/** A read from the pane's Refresh, where a prep may be submitted. */
const read = async ($: Engine) => {
  // `/owner` loads the queue, so the pane draws its Refresh button.
  await $.command.run({ command: 'owner', args: '' })
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  await ui.press({ key: 'refresh' })
  await ui.unmount()
}

test('the instruction names the rule, the path and the reason, and no kind of boundary', () => {
  const text = instruction(WHY.idle(), '/data/start-lines/planner-1.md')

  expect(text).toBe(
    "owner-queue: prepare now (idle 45 minutes). Follow the session-rules skill, \"A role session's clear boundary\", in order. In its last step, write the start line, whole, to /data/start-lines/planner-1.md, with your file tool: replace the file, never append.",
  )
  for (const why of [WHY.context(260000), WHY.idle(), WHY.request()]) {
    const one = instruction(why, '/data/start-lines/planner-1.md').toLowerCase()
    expect(one).not.toContain('reset prompt')
    expect(one).not.toContain('for a clear')
    expect(one).not.toContain('/clear')
    expect(one).not.toContain('compact')
    // The one "clear" is the quoted heading, character for character.
    expect(one.split('clear')).toHaveLength(2)
  }
})

test('roleOf tracks the Tools manager and no longer the retired dispatch role', () => {
  expect(roleOf('tools-central-builder-manager')).toBe('tools-central-builder-manager')
  expect(roleOf('tools:tools-central-builder-manager')).toBe('tools-central-builder-manager')
  expect(roleOf('supabase-consultant-dispatch')).toBe(undefined)
  expect(roleOf('tools:supabase-consultant-dispatch')).toBe(undefined)
  expect(roleOf('central-planner')).toBe('central-planner')
  expect(roleOf('central-builder-manager')).toBe('central-builder-manager')
  expect(roleOf('supabase-consultant')).toBe('supabase-consultant')
})

test('a tracked role registers, and its id prints its start line path', async ($, on) => {
  const w = world(on)

  await enroll($)
  const one = w.record('planner-1')
  expect(one?.role).toBe('central-planner')
  expect(one?.state).toBe('idle')
  const named = await $.command.run({ command: 'owner', args: 'id' })
  expect(JSON.stringify(named)).toContain('Start line: ')
  expect(JSON.stringify(named)).toContain('/start-lines/planner-1.md')

  // A role a plugin provides is named with its prefix.
  await enroll($, 'consult-1', 'tools:supabase-consultant')
  expect(w.record('consult-1')?.role).toBe('supabase-consultant')
})

test('a role that is not tracked, no role, or a subagent writes no record', async ($, on) => {
  const w = world(on)

  await enroll($, 'builder-1', 'stage-builder')
  await enroll($, 'plain-1', null)
  await $.classic.SessionStart({
    source: 'startup',
    session_id: 'sub-1',
    agent_type: 'central-planner',
    agent_id: 'a1',
  })
  await start($, 't1')
  await end($, 't1')
  await measure($, 300000)

  expect(
    [...w.files].filter(([path]) => path.includes('/sessions/')).map(([, one]) => one.text),
  ).toEqual([])
  expect(w.sent).toHaveLength(0)
  const named = await $.command.run({ command: 'owner', args: 'id' })
  expect(JSON.stringify(named)).not.toContain('start-lines')
})

test('the context trigger fires once, after the turn, and again only after a new turn', async ($, on) => {
  const w = world(on)
  await enroll($)

  await start($, 't1')
  await w.time.advance(1000)
  await measure($, 260000)
  // Busy: nothing is sent mid-turn.
  expect(w.sent).toHaveLength(0)
  await end($, 't1')
  expect(w.sent).toHaveLength(1)
  expect(w.sent[0]).toContain('prepare now (context at 260000 tokens')
  expect(w.sent[0]).toContain("A role session's clear boundary")
  expect(w.sent[0]).toContain('/start-lines/planner-1.md')
  expect(w.sent[0]).toContain('replace the file, never append')

  // Once: another measurement with no new turn sends nothing.
  await measure($, 261000)
  await read($)
  expect(w.sent).toHaveLength(1)

  // The prep turn ends with no start line (Esc on it, a denied write, a question
  // back): it re-arms nothing, so the instruction is not sent again (F1).
  await w.time.advance(1000)
  await start($, 't2')
  await w.time.advance(1000)
  await $.turn.complete({
    answer: '',
    durationMs: 1,
    isAborted: true,
    turnId: 't2',
    reason: 'aborted',
  })
  await measure($, 262000)
  await read($)
  expect(w.sent).toHaveLength(1)

  // A turn of work after it, still with no start line: armed again, sent once.
  await w.time.advance(1000)
  await start($, 't3')
  await w.time.advance(1000)
  await end($, 't3')
  await measure($, 263000)
  expect(w.sent).toHaveLength(2)

  // The prep turn writes the start line and leaves it fresh; a turn of work
  // after it makes it stale and arms the trigger once more.
  await w.time.advance(1000)
  await start($, 't4')
  await w.time.advance(1000)
  w.files.set(w.lineOf('planner-1'), { text: 'the start line', mtime: w.time.now() })
  await end($, 't4')
  await measure($, 264000)
  expect(w.sent).toHaveLength(2)
})

test('a prep turn with no start line does not bring the idle trigger back (F1)', async ($, on) => {
  const w = world(on)
  await enroll($)
  await start($, 't1')
  await w.time.advance(1000)
  await end($, 't1')
  await w.time.advance(46 * MINUTE)
  await read($)
  expect(w.sent).toHaveLength(1)

  // The prep turn writes nothing; 45 minutes later, nothing is sent again.
  // A second passes first, so the prep turn starts after the send: without
  // the fix, that start alone would re-arm the trigger.
  await w.time.advance(1000)
  await start($, 't2')
  await w.time.advance(1000)
  await end($, 't2')
  await w.time.advance(46 * MINUTE)
  await read($)
  await w.time.advance(46 * MINUTE)
  await read($)
  expect(w.sent).toHaveLength(1)

  // A turn of work brings it back, once, 45 minutes after that turn.
  await start($, 't3')
  await w.time.advance(1000)
  await end($, 't3')
  await w.time.advance(46 * MINUTE)
  await read($)
  expect(w.sent).toHaveLength(2)
})

test('a resumed session takes no old request and no old idle time (F5)', async ($, on) => {
  const w = world(on)
  await enroll($)
  await start($, 't1')
  await w.time.advance(1000)
  await end($, 't1')
  // The session stops; End of Day writes a request it never takes.
  w.files.set(`${w.root()}/requests/planner-1.json`, {
    text: JSON.stringify({ at: w.time.now() }),
    mtime: w.time.now(),
  })
  await $.session.end({
    reason: 'prompt_input_exit',
    sessionId: 'planner-1',
    resume: { id: 'planner-1' },
  })
  await w.time.advance(3 * 60 * MINUTE)

  await $.classic.SessionStart({
    source: 'resume',
    session_id: 'planner-1',
    agent_type: 'central-planner',
  })
  await read($)
  expect(w.sent).toHaveLength(0)
  expect(w.record('planner-1')?.state).toBe('idle')
})

test('a record that cannot be written is said once (F7)', async ($, on) => {
  const w = world(on)
  w.faults.records = true
  await enroll($)
  await start($, 't1')
  await end($, 't1')

  const said = w.toasts.filter(one => one.includes('record could not be written'))
  expect(said).toHaveLength(1)
})

test('the idle trigger fires after 45 minutes, once, and a fresh start line stops it', async ($, on) => {
  const w = world(on)
  await enroll($)
  await start($, 't1')
  await w.time.advance(1000)
  await end($, 't1')

  await w.time.advance(44 * MINUTE)
  await read($)
  expect(w.sent).toHaveLength(0)
  await w.time.advance(2 * MINUTE)
  await read($)
  expect(w.sent).toHaveLength(1)
  expect(w.sent[0]).toContain('idle 45 minutes')
  await w.time.advance(50 * MINUTE)
  await read($)
  expect(w.sent).toHaveLength(1)

  // The prep turn writes the start line: idle again, nothing is sent a second time.
  await start($, 't2')
  await w.time.advance(1000)
  w.files.set(w.lineOf('planner-1'), { text: 'the start line', mtime: w.time.now() })
  await end($, 't2')
  await w.time.advance(50 * MINUTE)
  await read($)
  expect(w.sent).toHaveLength(1)
})

test('a prep request for a busy session runs only after its turn ends', async ($, on) => {
  const w = world(on)
  await enroll($)
  await start($, 't1')
  await w.time.advance(1000)
  w.files.set(`${w.root()}/requests/planner-1.json`, {
    text: JSON.stringify({ at: w.time.now() }),
    mtime: w.time.now(),
  })

  await read($)
  expect(w.sent).toHaveLength(0)
  await end($, 't1')
  expect(w.sent).toHaveLength(1)
  expect(w.sent[0]).toContain('End of Day, asked by the owner')
  await read($)
  expect(w.sent).toHaveLength(1)
})

test('End of Day skips a fresh start line, asks a busy one, and flags a closed one', async ($, on) => {
  const w = world(on)
  await enroll($)
  w.other('manager-1', { state: 'busy', turnStart: w.time.now() })
  w.other('consult-1', { role: 'supabase-consultant', turnStart: w.time.now() - MINUTE })
  w.files.set(w.lineOf('consult-1'), { text: 'consult start line', mtime: w.time.now() })
  w.other('dispatch-1', { role: 'tools-central-builder-manager', state: 'closed' })
  await read($)
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })

  await w.time.advance(1000)
  await ui.press({ key: 'end-of-day' })

  expect(w.toasts).toContain('End of Day: asked 2; 1 had a fresh start line; 1 not running')
  expect(w.find('/requests/planner-1.json')).toBeDefined()
  expect(w.find('/requests/manager-1.json')).toBeDefined()
  expect(w.find('/requests/consult-1.json')).toBe(undefined)
  expect(w.find('/requests/dispatch-1.json')).toBe(undefined)
  // This session is idle: it takes its own request at once.
  expect(w.sent).toHaveLength(1)
  expect(w.sent[0]).toContain('End of Day')
  expect(await ui.find({ text: /no start line, closed/ })).toBeDefined()
  expect(await ui.find({ text: /consult-1 \(supabase-consultant\): running, idle/ })).toBeDefined()
  await ui.unmount()
})

test('a stale heartbeat with no closed shows as stopped; closed shows as closed', async ($, on) => {
  const w = world(on)
  await enroll($)
  w.other('manager-1', { beat: w.time.now() - 91000 })
  w.other('consult-1', { role: 'supabase-consultant', beat: w.time.now() - 60000 })
  w.other('tools-1', { role: 'tools-central-builder-manager', state: 'closed' })
  await read($)
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })

  expect(await ui.find({ text: /manager-1 \(central-builder-manager\): stopped/ })).toBeDefined()
  expect(await ui.find({ text: /tools-1 \(tools-central-builder-manager\): closed/ })).toBeDefined()
  expect(await ui.find({ text: /consult-1 \(supabase-consultant\): running, idle/ })).toBeDefined()
  await ui.unmount()

  // This session's own end: closed, not stopped.
  await $.session.end({
    reason: 'prompt_input_exit',
    sessionId: 'planner-1',
    resume: { id: 'planner-1' },
  })
  expect(w.record('planner-1')?.state).toBe('closed')
})

test('a start line is read whole, and Copy start line copies the newest text', async ($, on) => {
  const w = world(on)
  await enroll($)
  w.files.set(w.lineOf('planner-1'), { text: 'first start line', mtime: w.time.now() })
  await w.time.advance(1000)
  w.files.set(w.lineOf('planner-1'), {
    text: 'Act as the central-planner. State branch: state/central-planner.',
    mtime: w.time.now(),
  })
  await read($)
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })

  expect(await ui.find({ text: /Start lines \(1\)/ })).toBeDefined()
  expect(await ui.find({ text: /Start line .*: fresh/ })).toBeDefined()
  expect(await ui.find({ type: 'Button', label: 'Copy start line' })).toBeDefined()
  await ui.press({ key: 'start-line:planner-1' })
  expect(w.copied).toEqual(['Act as the central-planner. State branch: state/central-planner.'])

  // A turn after it makes it stale.
  await w.time.advance(1000)
  await start($, 't1')
  await ui.press({ key: 'refresh' })
  expect(await ui.find({ text: /Start line .*: stale/ })).toBeDefined()
  await ui.unmount()
})

test('a /clear moves the start line to the new id and marks it used', async ($, on) => {
  const w = world(on)
  await enroll($)
  w.files.set(w.lineOf('planner-1'), { text: 'the start line', mtime: w.time.now() })
  await read($)

  await $.session.end({ reason: 'clear', sessionId: 'planner-1', resume: { id: 'planner-1' } })
  expect(w.record('planner-1')?.state).toBe('cleared')
  await w.time.advance(1000)
  await enroll($, 'planner-2', 'central-planner', 'clear')
  w.ids.now = 'planner-2'
  await read($)

  expect(w.files.get(w.lineOf('planner-2'))?.text).toBe('the start line')
  expect(w.files.get(w.lineOf('planner-1'))?.text).toBe('')
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect(await ui.find({ text: /Start line .*: used/ })).toBeDefined()
  expect(await ui.find({ key: 'start-line:planner-2' })).toBeDefined()
  expect(await ui.find({ key: 'start-line:planner-1' })).toBe(undefined)
  expect(await ui.findAll({ type: 'Text', text: /\(central-planner\)/ })).toHaveLength(1)
  await ui.unmount()
})

test('Submit to a closed tracked session says the item is held, and the pane lists it', async ($, on) => {
  const w = world(on)
  await enroll($)
  w.other('planner-2', { role: 'central-planner', name: 'Tools planner', state: 'closed' })
  await read($)
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })

  await ui.press({ key: 'expand-all' })
  await ui.press({ key: 'pick:decision:Who merges:b' })
  await ui.press({ key: 'submit' })

  expect(w.toasts).toContain(
    'Held for Tools planner: it is closed; the item waits until it runs again',
  )
  expect(await ui.find({ text: /Held for sessions not running \(1\)/ })).toBeDefined()
  expect(await ui.find({ text: /Answer: .*Who merges/ })).toBeDefined()
  await ui.unmount()
})
