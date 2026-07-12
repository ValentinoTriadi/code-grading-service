import { Plus, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { emptyBand, type RubricBand, type RubricCriterion } from "@/lib/grading-form"

interface Props {
  index: number
  criterion: RubricCriterion
  onChange: (patch: Partial<RubricCriterion>) => void
  onRemove: () => void
}

export function RubricCriterionCard({
  index,
  criterion,
  onChange,
  onRemove,
}: Props) {
  const denom = criterion.weight.trim() || "?"

  function updateBand(id: string, patch: Partial<RubricBand>) {
    onChange({
      bands: criterion.bands.map((b) => (b.id === id ? { ...b, ...patch } : b)),
    })
  }
  function removeBand(id: string) {
    onChange({ bands: criterion.bands.filter((b) => b.id !== id) })
  }
  function addBand() {
    onChange({ bands: [...criterion.bands, emptyBand()] })
  }

  return (
    <div className="rounded-md border bg-muted/30 p-3 space-y-2">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-muted-foreground">
          Criterion {index + 1}
        </span>
        <Button
          type="button"
          variant="ghost"
          size="icon-xs"
          onClick={onRemove}
          aria-label="Remove criterion"
        >
          <X />
        </Button>
      </div>

      <div className="grid grid-cols-[1fr_5rem] gap-2">
        <Input
          placeholder="Name (e.g. Correctness)"
          value={criterion.name}
          onChange={(e) => onChange({ name: e.target.value })}
        />
        <Input
          placeholder="Weight %"
          inputMode="numeric"
          value={criterion.weight}
          onChange={(e) => onChange({ weight: e.target.value })}
        />
      </div>

      <Textarea
        rows={2}
        placeholder="What this criterion measures (the headline before the scoring bands)..."
        value={criterion.description}
        onChange={(e) => onChange({ description: e.target.value })}
      />

      {criterion.bands.length > 0 && (
        <div className="space-y-2 rounded-md border border-dashed p-2">
          <Label className="text-xs text-muted-foreground">
            Scoring bands — point thresholds the grader picks between
          </Label>
          {criterion.bands.map((b) => (
            <div key={b.id} className="flex items-start gap-2">
              <div className="flex shrink-0 items-center gap-1 pt-1.5">
                <Input
                  className="h-7 w-12 text-center"
                  placeholder="pts"
                  inputMode="numeric"
                  value={b.points}
                  onChange={(e) => updateBand(b.id, { points: e.target.value })}
                />
                <span className="text-xs text-muted-foreground">/{denom}</span>
              </div>
              <Textarea
                rows={2}
                className="text-sm"
                placeholder="When does the submission land in this band?"
                value={b.description}
                onChange={(e) =>
                  updateBand(b.id, { description: e.target.value })
                }
              />
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                className="mt-1"
                onClick={() => removeBand(b.id)}
                aria-label="Remove band"
              >
                <X />
              </Button>
            </div>
          ))}
          <Button type="button" variant="outline" size="xs" onClick={addBand}>
            <Plus /> Add band
          </Button>
        </div>
      )}

      {criterion.bands.length === 0 && (
        <Button
          type="button"
          variant="ghost"
          size="xs"
          onClick={addBand}
          className="text-muted-foreground"
        >
          <Plus /> Add scoring bands (optional — e.g. 60/60, 45/60, 25/60…)
        </Button>
      )}
    </div>
  )
}
