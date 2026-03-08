import { createSignal, For, Show, createMemo, onCleanup } from 'solid-js'
import type { PRFile } from '@/lib/github'
import type { RankedFile, Cluster } from '@/lib/ml'
import { ScoreBadge } from './ScoreBadge'

interface Props {
  open: boolean
  onClose: () => void
  files: PRFile[]
  rankedFiles: RankedFile[]
  clusters: Cluster[]
  onSelectFile: (filename: string) => void
  onSelectCluster: (id: string | null) => void
}

export function CommandPalette(props: Props) {
  const [query, setQuery] = createSignal('')

  const rankMap = createMemo(() =>
    new Map(props.rankedFiles.map(r => [r.filename, r]))
  )

  const filteredFiles = createMemo(() => {
    const q = query().toLowerCase()
    return props.files
      .filter(f => f.filename.toLowerCase().includes(q))
      .slice(0, 10)
  })

  const filteredClusters = createMemo(() => {
    const q = query().toLowerCase()
    return props.clusters.filter(c => c.label.toLowerCase().includes(q)).slice(0, 5)
  })

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Escape') props.onClose()
  }

  return (
    <Show when={props.open}>
      <div
        class="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-slate-950/80 backdrop-blur"
        onClick={props.onClose}
        onKeyDown={handleKeyDown}
      >
        <div
          class="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden"
          onClick={e => e.stopPropagation()}
        >
          <div class="flex items-center gap-3 px-4 py-3 border-b border-slate-800">
            <span class="text-slate-500 text-sm">⌘</span>
            <input
              class="flex-1 bg-transparent text-white text-sm outline-none placeholder:text-slate-600"
              placeholder="Search files or clusters..."
              value={query()}
              onInput={e => setQuery(e.currentTarget.value)}
              autofocus
              onKeyDown={handleKeyDown}
            />
            <button class="text-slate-600 hover:text-slate-400 text-xs" onClick={props.onClose}>
              ESC
            </button>
          </div>

          <div class="max-h-80 overflow-y-auto">
            <Show when={filteredClusters().length > 0 && query().length > 0}>
              <div class="px-3 py-1.5 text-xs text-slate-600 uppercase tracking-wider">Clusters</div>
              <For each={filteredClusters()}>
                {cluster => (
                  <button
                    class="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-slate-800 text-left transition-colors"
                    onClick={() => { props.onSelectCluster(cluster.id); props.onClose() }}
                  >
                    <div class="w-2 h-2 rounded-full shrink-0" style={{ background: cluster.color }} />
                    <span class="text-sm text-slate-200">{cluster.label}</span>
                    <span class="ml-auto text-xs text-slate-500">{cluster.files.length} files</span>
                  </button>
                )}
              </For>
            </Show>

            <Show when={filteredFiles().length > 0}>
              <div class="px-3 py-1.5 text-xs text-slate-600 uppercase tracking-wider">Files</div>
              <For each={filteredFiles()}>
                {file => {
                  const rank = () => rankMap().get(file.filename)
                  return (
                    <button
                      class="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-slate-800 text-left transition-colors"
                      onClick={() => { props.onSelectFile(file.filename); props.onClose() }}
                    >
                      <span class="text-sm text-slate-200 font-mono truncate flex-1">{file.filename}</span>
                      <Show when={rank()}>
                        <ScoreBadge label={rank()!.label} />
                      </Show>
                    </button>
                  )
                }}
              </For>
            </Show>

            <Show when={filteredFiles().length === 0 && filteredClusters().length === 0}>
              <div class="px-4 py-8 text-center text-slate-600 text-sm">
                No results for "{query()}"
              </div>
            </Show>
          </div>
        </div>
      </div>
    </Show>
  )
}
