"use client"

interface MLUnavailableBannerProps {
  onRetry?: () => void
}

export function MLUnavailableBanner({ onRetry }: MLUnavailableBannerProps) {
  return (
    <div
      role="alert"
      className="flex items-center justify-between px-4 py-2 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-xs text-yellow-700 dark:text-yellow-400"
    >
      <span>ML analysis unavailable — showing original file order.</span>
      {onRetry && (
        <button
          onClick={onRetry}
          className="ml-3 underline hover:no-underline"
          aria-label="Retry ML analysis"
        >
          Retry
        </button>
      )}
    </div>
  )
}
