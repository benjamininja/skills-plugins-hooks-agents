export type OwnerField = { label: string; value: string }

export type OwnerItem = {
  kind: 'decision' | 'action'
  title: string
  fields: OwnerField[]
}

/** One choice of a decision: its key (`a`) and its text as written. */
export type OwnerOption = { key: string; text: string }

export type OwnerQueue = {
  /** False until the queue file has been read once in this session. */
  isLoaded: boolean
  /** False when the project has no queue file. */
  hasFile: boolean
  items: OwnerItem[]
  /** The file read: the main checkout's by absolute path when it was found. */
  file?: string
  /** The ids of answered decisions whose Answer line the pane did not write. */
  foreign?: string[]
}

/**
 * The mod's own store (`$.store`), key `answers`: the Answer line the pane
 * wrote for each decision, under `<file>|<kind:title>`. No session writes it.
 */
export type OwnerAnswers = Record<string, string>

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
    }
  }
}
