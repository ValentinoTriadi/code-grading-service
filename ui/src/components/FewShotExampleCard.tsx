import { Plus, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import {
  buildGradingBlock,
  emptyGradingCriterion,
  parseGradingBlock,
  type FewShotExample,
  type GradingCriterion,
} from "@/lib/grading-form"
import { StringListEditor } from "./StringListEditor"

interface Props {
  index: number
  example: FewShotExample
  onChange: (patch: Partial<FewShotExample>) => void
  onRemove: () => void
}

export function FewShotExampleCard({
  index,
  example,
  onChange,
  onRemove,
}: Props) {
  const isGuided = example.gradingMode === "guided"
  const preview = buildGradingBlock(example)

  function handleGradingModeChange(raw: boolean) {
    if (raw) {
      // Translate the structured fields into the raw box.
      const composed = buildGradingBlock({ ...example, gradingMode: "guided" })
      onChange({ gradingMode: "raw", rawGrading: composed || example.rawGrading })
    } else {
      // Parse the raw block back into structured fields.
      const parsed = parseGradingBlock(example.rawGrading)
      onChange({ gradingMode: "guided", ...(parsed ?? {}) })
    }
  }

  function updateCriterion(id: string, patch: Partial<GradingCriterion>) {
    onChange({
      criteria: example.criteria.map((c) =>
        c.id === id ? { ...c, ...patch } : c,
      ),
    })
  }
  function removeCriterion(id: string) {
    onChange({ criteria: example.criteria.filter((c) => c.id !== id) })
  }
  function addCriterion() {
    onChange({ criteria: [...example.criteria, emptyGradingCriterion()] })
  }

  return (
    <div className="rounded-md border bg-muted/30 p-3 space-y-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-muted-foreground">
          Example {index + 1}
        </span>
        <Button
          type="button"
          variant="ghost"
          size="icon-xs"
          onClick={onRemove}
          aria-label="Remove example"
        >
          <X />
        </Button>
      </div>

      <div className="space-y-1.5">
        <Label className="text-xs">Problem</Label>
        <Textarea
          rows={2}
          placeholder="Problem statement for this example..."
          value={example.problem}
          onChange={(e) => onChange({ problem: e.target.value })}
        />
      </div>

      <div className="space-y-1.5">
        <Label className="text-xs">Student code</Label>
        <Textarea
          rows={4}
          placeholder="Example student code..."
          className="font-mono text-xs"
          value={example.code}
          onChange={(e) => onChange({ code: e.target.value })}
        />
      </div>

      <div className="space-y-2 rounded-md border border-dashed p-2">
        <div className="flex items-center justify-between gap-3">
          <Label className="text-xs">Expected grading</Label>
          <div className="flex items-center gap-2">
            <span
              className={
                isGuided ? "text-xs font-medium" : "text-xs text-muted-foreground"
              }
            >
              Guided
            </span>
            <Switch
              size="sm"
              checked={!isGuided}
              onCheckedChange={handleGradingModeChange}
              aria-label="Toggle raw grading mode"
            />
            <span
              className={
                isGuided ? "text-xs text-muted-foreground" : "text-xs font-medium"
              }
            >
              Raw
            </span>
          </div>
        </div>

        {isGuided ? (
          <div className="space-y-3">
            <div className="grid grid-cols-[1fr_6rem] gap-2">
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">
                  Overall score
                </Label>
                <Input
                  placeholder="0–100"
                  inputMode="decimal"
                  value={example.score}
                  onChange={(e) => onChange({ score: e.target.value })}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">
                  Confidence
                </Label>
                <Input
                  placeholder="0–1"
                  inputMode="decimal"
                  value={example.confidence}
                  onChange={(e) => onChange({ confidence: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">Summary</Label>
              <Textarea
                rows={2}
                placeholder="2–4 sentence headline of the grading..."
                value={example.summary}
                onChange={(e) => onChange({ summary: e.target.value })}
              />
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs text-muted-foreground">
                Per-criterion scores
              </Label>
              {example.criteria.map((c) => (
                <div
                  key={c.id}
                  className="space-y-1.5 rounded-md border bg-background/60 p-2"
                >
                  <div className="grid grid-cols-[1fr_4rem_4rem_auto] items-center gap-2">
                    <Input
                      className="h-7"
                      placeholder="Criterion name"
                      value={c.name}
                      onChange={(e) =>
                        updateCriterion(c.id, { name: e.target.value })
                      }
                    />
                    <Input
                      className="h-7 text-center"
                      placeholder="score"
                      inputMode="numeric"
                      value={c.score}
                      onChange={(e) =>
                        updateCriterion(c.id, { score: e.target.value })
                      }
                    />
                    <Input
                      className="h-7 text-center"
                      placeholder="max"
                      inputMode="numeric"
                      value={c.maxScore}
                      onChange={(e) =>
                        updateCriterion(c.id, { maxScore: e.target.value })
                      }
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-sm"
                      onClick={() => removeCriterion(c.id)}
                      aria-label="Remove criterion"
                    >
                      <X />
                    </Button>
                  </div>
                  <Textarea
                    rows={2}
                    className="text-sm"
                    placeholder="Comment explaining this criterion's score..."
                    value={c.comment}
                    onChange={(e) =>
                      updateCriterion(c.id, { comment: e.target.value })
                    }
                  />
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="xs"
                onClick={addCriterion}
              >
                <Plus /> Add criterion
              </Button>
            </div>

            <StringListEditor
              label="Suggestions"
              items={example.suggestions}
              placeholder="A specific, actionable improvement..."
              addLabel="Add suggestion"
              onChange={(suggestions) => onChange({ suggestions })}
            />

            <StringListEditor
              label="Exemplary points"
              items={example.exemplaryPoints}
              placeholder="Something the submission did well..."
              addLabel="Add exemplary point"
              onChange={(exemplaryPoints) => onChange({ exemplaryPoints })}
            />

            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">
                  Time complexity
                </Label>
                <Input
                  placeholder="e.g. O(n)"
                  value={example.timeComplexity}
                  onChange={(e) =>
                    onChange({ timeComplexity: e.target.value })
                  }
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs text-muted-foreground">
                  Space complexity
                </Label>
                <Input
                  placeholder="e.g. O(1)"
                  value={example.spaceComplexity}
                  onChange={(e) =>
                    onChange({ spaceComplexity: e.target.value })
                  }
                />
              </div>
            </div>

            {preview && (
              <details className="rounded-md border bg-background/60 text-xs">
                <summary className="cursor-pointer select-none px-2 py-1.5 text-muted-foreground">
                  Preview composed &lt;RESULT&gt; block
                </summary>
                <pre className="overflow-x-auto px-2 pb-2 font-mono text-[11px] leading-snug">
                  {preview}
                </pre>
              </details>
            )}
          </div>
        ) : (
          <div className="space-y-1.5">
            <Textarea
              rows={6}
              className="font-mono text-xs"
              placeholder={"<RESULT>\n{ ... }\n</RESULT>"}
              value={example.rawGrading}
              onChange={(e) => onChange({ rawGrading: e.target.value })}
            />
            <p className="text-xs text-muted-foreground">
              Paste a complete grading block verbatim (e.g. a{" "}
              <code>&lt;RESULT&gt;…&lt;/RESULT&gt;</code> JSON block).
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
