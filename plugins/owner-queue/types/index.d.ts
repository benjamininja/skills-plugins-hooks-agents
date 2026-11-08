export type OwnerField = { label: string; value: string }

export type OwnerItem = {
  kind: 'decision' | 'action'
  title: string
  fields: OwnerField[]
  /** Each fenced block of the entry, whole: one chunk to copy and paste. */
  blocks?: string[]
  /** The queue file the entry was read from; set by the pane, not the parser. */
  queue?: string
}

/**
 * One stretch of an entry's text as the pane draws it: a field's own words,
 * or one numbered step of it (`step`), with what is copied from it.
 */
export type OwnerPart = {
  /** The field's label, on the part that opens the field. */
  label?: string
  /** The step's number, on a numbered step. */
  step?: number
  text: string
  /** Each `code` span of the text, once. */
  codes: string[]
  /** The places, in the entry's blocks, of the blocks the text names. */
  blocks: number[]
}

/** One choice of a decision: its key (`a`) and its text as written. */
export type OwnerOption = { key: string; text: string }

/** One queue the pane reads: the session's own project's, or a listed one. */
export type OwnerQueueFile = {
  /** The path read: absolute for a main checkout and for every listed queue. */
  file: string
  /** The repo folder name the group is headed with. */
  label: string
  /** False when the file is missing or could not be read. */
  hasFile: boolean
}

export type OwnerQueue = {
  /** False until the queue file has been read once in this session. */
  isLoaded: boolean
  /** False when no queue file, the session's own or a listed one, exists. */
  hasFile: boolean
  /** The entries of every queue read, each carrying its `queue`. */
  items: OwnerItem[]
  /** Every queue the pane reads, the session's own first. */
  queues?: OwnerQueueFile[]
  /** The file read: the main checkout's by absolute path when it was found. */
  file?: string
  /** The ids of answered decisions whose Answer line the pane did not write. */
  foreign?: string[]
  /** By item id, the Note lines of the entry that the pane did not write. */
  unpenned?: Record<string, string[]>
  /** False when the main checkout was not found and the session's copy is read. */
  isMain?: boolean
}

/**
 * What the owner has pressed and not yet submitted, by item id: the option
 * chosen for a decision, or `done` for an item marked done.
 */
export type OwnerStaged = Record<string, OwnerOption | 'done'>

/**
 * The comments the owner has typed and not yet submitted, by item id, in the
 * order typed. An entry may hold several, beside a chosen option or a done
 * mark. Each becomes a Note line on Submit, and not before.
 */
export type OwnerComments = Record<string, string[]>

/**
 * The mod's own store (`$.store`), key `answers`: the Answer line the pane
 * wrote for each decision, under `<file>|<kind:title>`. No session writes it.
 */
export type OwnerAnswers = Record<string, string>

/**
 * The mod's own store, key `notes`: the Note lines the pane wrote for each
 * entry, under `<file>|<kind:title>`. Key `noted:<session>` holds, in the
 * same shape, the ones already said in that session's chat.
 */
export type OwnerNotes = Record<string, string[]>

declare module 'claude-code' {
  interface PluginState {
    'owner-queue': {
      queue: OwnerQueue
      /** The ids (`kind:title`) of the items drawn expanded. */
      open: string[]
      /** True while the pane is on screen; the band's button flips it. */
      shown: boolean
      /** When the queue file was last read, as `HH:MM:SS`. */
      readAt: string
      /** Pressed, not yet submitted; nothing is written before Submit. */
      staged: OwnerStaged
      /** Typed comments, not yet submitted; nothing is written before Submit. */
      comments: OwnerComments
      /** The ids of the items whose comment box is open. */
      writing: string[]
      /** Counts the key presses in a comment box, to redraw what was typed. */
      strokes: number
    }
  }
}
