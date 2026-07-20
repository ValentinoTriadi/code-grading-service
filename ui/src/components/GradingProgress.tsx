interface Props {
  step: number
  total: number
  message: string
  unit?: string
}

export function GradingProgress({ step, total, message, unit }: Props) {
  const pct = Math.round((step / total) * 100)
  const counter = unit ? `${step} / ${total} ${unit}` : `${step} / ${total}`

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs text-muted-foreground">
        <span className="truncate max-w-[70%]">{message}</span>
        <span className="shrink-0">{counter}</span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
