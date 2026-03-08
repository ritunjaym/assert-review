import { For, Show } from 'solid-js'
import type { Cluster } from '@/lib/ml'

interface Props {
  clusters: Cluster[]
  selectedCluster: string | null
  onSelectCluster: (id: string | null) => void
  isLoading: boolean
}

export function ClusterPanel(props: Props) {
  return (
    <div class="p-3 space-y-2">
      <div class="text-xs font-medium text-slate-400 uppercase tracking-wider px-1">
        Semantic Groups
      </div>
      <Show when={props.isLoading}>
        {[...Array(3)].map(() => (
          <div class="h-16 bg-slate-800 rounded-lg animate-pulse" />
        ))}
      </Show>
      <Show when={!props.isLoading && props.clusters.length === 0}>
        <p class="text-xs text-slate-600 px-1">
          All changes appear related — no distinct groups found.
        </p>
      </Show>
      <For each={props.clusters}>
        {cluster => {
          const isSelected = () => props.selectedCluster === cluster.id
          return (
            <button
              class={`w-full text-left rounded-lg p-3 border transition-colors
                ${isSelected()
                  ? 'border-opacity-100 bg-opacity-20'
                  : 'border-slate-700 hover:border-slate-600 bg-slate-800/30'}
              `}
              style={isSelected() ? {
                'border-color': cluster.color,
                'background-color': `${cluster.color}15`,
              } : {}}
              onClick={() => props.onSelectCluster(isSelected() ? null : cluster.id)}
            >
              <div class="flex items-center gap-2 mb-1">
                <div class="w-2 h-2 rounded-full" style={{ background: cluster.color }} />
                <span class="text-xs font-medium text-slate-200">{cluster.label}</span>
                <span class="ml-auto text-xs text-slate-500">{cluster.files.length} files</span>
              </div>
              <div class="text-xs text-slate-500">
                Coherence: {Math.round(cluster.coherence * 100)}%
              </div>
            </button>
          )
        }}
      </For>
    </div>
  )
}
