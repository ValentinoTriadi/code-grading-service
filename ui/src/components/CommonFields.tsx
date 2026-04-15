import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"

interface Props {
  problems: string
  rubric: string
  withReason: boolean
  onProblemsChange: (v: string) => void
  onRubricChange: (v: string) => void
  onWithReasonChange: (v: boolean) => void
}

export function CommonFields({
  problems,
  rubric,
  withReason,
  onProblemsChange,
  onRubricChange,
  onWithReasonChange,
}: Props) {
  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <Label htmlFor="problems">Problems <span className="text-destructive">*</span></Label>
        <Textarea
          id="problems"
          placeholder="Describe the programming problem given to students..."
          rows={3}
          value={problems}
          onChange={(e) => onProblemsChange(e.target.value)}
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="rubric">
          Rubric <span className="text-muted-foreground text-xs">(optional — uses default if empty)</span>
        </Label>
        <Textarea
          id="rubric"
          placeholder="1. Correctness (60%) — ... 
2. Readability (40%) — ..."
          rows={3}
          value={rubric}
          onChange={(e) => onRubricChange(e.target.value)}
        />
      </div>

      <div className="flex items-center gap-3">
        <Switch
          id="with-reason"
          checked={withReason}
          onCheckedChange={onWithReasonChange}
        />
        <Label htmlFor="with-reason">Include reasoning</Label>
      </div>
    </div>
  )
}
