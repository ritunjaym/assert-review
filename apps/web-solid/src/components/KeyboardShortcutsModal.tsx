import { Show } from 'solid-js'

interface Props {
  open: boolean
  onClose: () => void
}

const shortcuts = [
  { key: 'j / k', description: 'Navigate files down / up' },
  { key: 'c', description: 'Add inline comment on selected line' },
  { key: 'o', description: 'Toggle AI priority ordering' },
  { key: '⌘K', description: 'Open command palette' },
  { key: '?', description: 'Show keyboard shortcuts' },
  { key: 'g d', description: 'Go to dashboard' },
  { key: 'Esc', description: 'Close modal / cancel comment' },
]

export function KeyboardShortcutsModal(props: Props) {
  return (
    <Show when={props.open}>
      <div
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur"
        onClick={props.onClose}
      >
        <div
          class="w-full max-w-sm bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden"
          onClick={e => e.stopPropagation()}
        >
          <div class="flex items-center justify-between px-4 py-3 border-b border-slate-800">
            <h2 class="text-sm font-semibold text-white">Keyboard Shortcuts</h2>
            <button class="text-slate-600 hover:text-slate-400 text-xs" onClick={props.onClose}>
              ESC
            </button>
          </div>
          <div class="p-4 space-y-1">
            {shortcuts.map(({ key, description }) => (
              <div class="flex items-center justify-between py-2 border-b border-slate-800/50 last:border-0">
                <span class="text-slate-400 text-sm">{description}</span>
                <kbd class="bg-slate-800 border border-slate-700 text-slate-300 text-xs px-2 py-0.5 rounded font-mono">
                  {key}
                </kbd>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Show>
  )
}
