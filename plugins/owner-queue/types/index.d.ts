export type OwnerField = { label: string; value: string }

export type OwnerItem = {
  kind: 'decision' | 'action'
  title: string
  fields: OwnerField[]
}

export type OwnerQueue = {
  /** False until the queue file has been read once in this session. */
  isLoaded: boolean
  /** False when the project has no queue file. */
  hasFile: boolean
  items: OwnerItem[]
}

declare module 'claude-code' {
  interface PluginState {
    'owner-queue': {
      queue: OwnerQueue
      /** The ids (`kind:title`) of the items drawn expanded. */
      open: string[]
      /** True while the pane is on screen; the band's button flips it. */
      shown: boolean
    }
  }
}
