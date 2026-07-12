import { Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import {
  buildRubricString,
  emptyCriterion,
  emptyExample,
  parseRubricString,
  type FewShotExample,
  type RubricCriterion,
  type RubricMode,
} from "@/lib/grading-form"
import { FewShotExampleCard } from "./FewShotExampleCard"
import { RubricCriterionCard } from "./RubricCriterionCard"

interface Props {
  problems: string
  rubricMode: RubricMode
  rubricText: string
  rubricCriteria: RubricCriterion[]
  examples: FewShotExample[]
  withReason: boolean
  onProblemsChange: (v: string) => void
  onRubricModeChange: (v: RubricMode) => void
  onRubricTextChange: (v: string) => void
  onRubricCriteriaChange: (v: RubricCriterion[]) => void
  onExamplesChange: (v: FewShotExample[]) => void
  onWithReasonChange: (v: boolean) => void
}

export function CommonFields({
  problems,
  rubricMode,
  rubricText,
  rubricCriteria,
  examples,
  withReason,
  onProblemsChange,
  onRubricModeChange,
  onRubricTextChange,
  onRubricCriteriaChange,
  onExamplesChange,
  onWithReasonChange,
}: Props) {
  const isGuided = rubricMode === "guided"

  function handleRubricModeChange(next: RubricMode) {
    if (next === "free") {
      // Translate the structured criteria into the free-text box.
      const composed = buildRubricString("guided", rubricText, rubricCriteria)
      if (composed) onRubricTextChange(composed)
    } else {
      // Parse the free text back into structured criteria.
      const parsed = parseRubricString(rubricText)
      if (parsed.length > 0) onRubricCriteriaChange(parsed)
      else if (rubricCriteria.length === 0)
        onRubricCriteriaChange([emptyCriterion()])
    }
    onRubricModeChange(next)
  }

  function updateCriterion(id: string, patch: Partial<RubricCriterion>) {
    onRubricCriteriaChange(
      rubricCriteria.map((c) => (c.id === id ? { ...c, ...patch } : c)),
    )
  }
  function removeCriterion(id: string) {
    onRubricCriteriaChange(rubricCriteria.filter((c) => c.id !== id))
  }
  function addCriterion() {
    onRubricCriteriaChange([...rubricCriteria, emptyCriterion()])
  }

  function updateExample(id: string, patch: Partial<FewShotExample>) {
    onExamplesChange(
      examples.map((ex) => (ex.id === id ? { ...ex, ...patch } : ex)),
    )
  }
  function removeExample(id: string) {
    onExamplesChange(examples.filter((ex) => ex.id !== id))
  }
  function addExample() {
    onExamplesChange([...examples, emptyExample()])
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1.5">
        <Label htmlFor="problems">
          Problems <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="problems"
          placeholder="Describe the programming problem given to students..."
          rows={3}
          value={problems}
          onChange={(e) => onProblemsChange(e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between gap-3">
          <Label>
            Rubric{" "}
            <span className="text-muted-foreground text-xs">
              (optional — uses default if empty)
            </span>
          </Label>
          <div className="flex items-center gap-2">
            <span
              className={
                isGuided ? "text-xs text-muted-foreground" : "text-xs font-medium"
              }
            >
              Free text
            </span>
            <Switch
              checked={isGuided}
              onCheckedChange={(v) => handleRubricModeChange(v ? "guided" : "free")}
              aria-label="Toggle guided rubric mode"
            />
            <span
              className={
                isGuided ? "text-xs font-medium" : "text-xs text-muted-foreground"
              }
            >
              Guided
            </span>
          </div>
        </div>

        {isGuided ? (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground">
              Add a criterion per dimension. Fill the description for a simple
              rubric, or add scoring bands (e.g. 60/60, 45/60…) to fully guide
              the grader's point thresholds.
            </p>
            {rubricCriteria.map((c, idx) => (
              <RubricCriterionCard
                key={c.id}
                index={idx}
                criterion={c}
                onChange={(patch) => updateCriterion(c.id, patch)}
                onRemove={() => removeCriterion(c.id)}
              />
            ))}
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={addCriterion}
              className="w-full"
            >
              <Plus /> Add criterion
            </Button>
          </div>
        ) : (
          <Textarea
            id="rubric"
            placeholder={`1. Correctness (60%) — ...
2. Readability (40%) — ...`}
            rows={3}
            value={rubricText}
            onChange={(e) => onRubricTextChange(e.target.value)}
          />
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between gap-3">
          <Label>
            Few-shot examples{" "}
            <span className="text-muted-foreground text-xs">(optional)</span>
          </Label>
          {examples.length > 0 && (
            <span className="text-xs text-muted-foreground">
              {examples.length} example{examples.length === 1 ? "" : "s"}
            </span>
          )}
        </div>

        {examples.map((ex, idx) => (
          <FewShotExampleCard
            key={ex.id}
            index={idx}
            example={ex}
            onChange={(patch) => updateExample(ex.id, patch)}
            onRemove={() => removeExample(ex.id)}
          />
        ))}

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={addExample}
          className="w-full"
        >
          <Plus /> Add example
        </Button>
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
