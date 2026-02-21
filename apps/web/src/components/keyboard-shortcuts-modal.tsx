"use client"

import { KEYBOARD_SHORTCUTS } from "@/hooks/use-hotkeys"

interface KeyboardShortcutsModalProps {
  open: boolean
  onClose: () => void
}

export function KeyboardShortcutsModal({ open, onClose }: KeyboardShortcutsModalProps) {
  if (!open) return null

  const categories = [...new Set(KEYBOARD_SHORTCUTS.map(s => s.category))]

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="shortcuts-title"
    >
      <div className="absolute inset-0 bg-background/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-background border border-border rounded-xl shadow-2xl p-6 w-full max-w-md">
        <h2 id="shortcuts-title" className="text-lg font-semibold mb-4">Keyboard Shortcuts</h2>
        {categories.map(cat => (
          <div key={cat} className="mb-4">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">{cat}</h3>
            <div className="space-y-1">
              {KEYBOARD_SHORTCUTS.filter(s => s.category === cat).map(s => (
                <div key={s.keys} className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{s.description}</span>
                  <kbd className="font-mono text-xs bg-muted border border-border rounded px-2 py-0.5">{s.keys}</kbd>
                </div>
              ))}
            </div>
          </div>
        ))}
        <button
          onClick={onClose}
          className="mt-4 w-full text-sm py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
          aria-label="Close keyboard shortcuts"
        >
          Close
        </button>
      </div>
    </div>
  )
}
