interface ScoreLabelBadgeProps {
  label: string
}

export function ScoreLabelBadge({ label }: ScoreLabelBadgeProps) {
  const styles =
    label === "Critical"
      ? "bg-red-500/20 text-red-400 border-red-500/40"
      : label === "Important"
      ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/40"
      : "bg-muted text-muted-foreground border-border"

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-semibold ${styles}`}
      aria-label={`Priority: ${label}`}
    >
      {label}
    </span>
  )
}
