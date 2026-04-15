import { useState } from "react"
import { gradeInlineStream } from "@/api"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { CommonFields } from "./CommonFields"
import { GradingProgress } from "./GradingProgress"
import type { GradingResponse } from "@/types"

interface Props {
  onResult: (r: GradingResponse) => void
  onError: (e: Error) => void
}

interface Progress { step: number; total: number; message: string }

export function InlineMode({ onResult, onError }: Props) {
  const [problems, setProblems] = useState("")
  const [code, setCode] = useState("")
  const [rubric, setRubric] = useState("")
  const [withReason, setWithReason] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [progress, setProgress] = useState<Progress | null>(null)

  async function handleGrade() {
    if (!problems.trim() || !code.trim()) return
    setIsRunning(true)
    setProgress(null)
    try {
      for await (const event of gradeInlineStream({ problems, code, rubric: rubric || undefined, with_reason: withReason })) {
        if (event.type === "error") throw new Error(event.message)
        if (event.type === "progress") setProgress({ step: event.step, total: event.total, message: event.message })
        if (event.type === "result") onResult(event.data)
      }
    } catch (err) {
      onError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsRunning(false)
      setProgress(null)
    }
  }

  return (
    <div className="space-y-6">
      <CommonFields
        problems={problems}
        rubric={rubric}
        withReason={withReason}
        onProblemsChange={setProblems}
        onRubricChange={setRubric}
        onWithReasonChange={setWithReason}
      />

      <div className="space-y-1.5">
        <Label htmlFor="code">Code <span className="text-destructive">*</span></Label>
        <Textarea
          id="code"
          placeholder="Paste student code here..."
          rows={10}
          className="font-mono text-sm"
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
      </div>

      <Button
        onClick={handleGrade}
        disabled={isRunning || !problems.trim() || !code.trim()}
        className="w-full"
      >
        {isRunning ? "Grading…" : "Grade"}
      </Button>

      {isRunning && progress && <GradingProgress {...progress} />}
    </div>
  )
}
