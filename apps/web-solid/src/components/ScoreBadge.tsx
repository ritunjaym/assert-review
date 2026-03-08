interface Props { label: 'Critical' | 'Important' | 'Low' }

export function ScoreBadge(props: Props) {
  const styles = {
    Critical: 'bg-red-900/60 text-red-300 border-red-800',
    Important: 'bg-yellow-900/60 text-yellow-300 border-yellow-800',
    Low: 'bg-slate-700/60 text-slate-400 border-slate-600',
  }
  return (
    <span class={`text-xs px-1.5 py-0.5 rounded border font-medium ${styles[props.label]}`}>
      {props.label}
    </span>
  )
}
