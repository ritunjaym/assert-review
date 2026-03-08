import { ErrorBoundary as SolidErrorBoundary } from 'solid-js'
import type { ParentProps } from 'solid-js'

interface Props extends ParentProps {
  fallback?: (err: Error, reset: () => void) => any
}

export function ErrorBoundary(props: Props) {
  return (
    <SolidErrorBoundary fallback={(err, reset) => (
      props.fallback?.(err, reset) ?? (
        <div class="flex items-center justify-center h-full min-h-48">
          <div class="text-center space-y-3">
            <p class="text-slate-400 text-sm">Something went wrong</p>
            <p class="text-slate-600 text-xs font-mono">{err.message}</p>
            <button
              class="text-xs bg-blue-600 text-white px-3 py-1.5 rounded hover:bg-blue-700 transition-colors"
              onClick={reset}
            >Try again</button>
          </div>
        </div>
      )
    )}>
      {props.children}
    </SolidErrorBoundary>
  )
}
