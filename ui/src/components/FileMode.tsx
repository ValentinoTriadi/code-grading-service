import { useState } from "react"
import { gradeFileStream } from "@/api"
import { Button } from "@/components/ui/button"
import {
  buildRubricString,
  emptyCriterion,
  normalizeExamples,
  type FewShotExample,
  type RubricCriterion,
  type RubricMode,
} from "@/lib/grading-form"
import { CommonFields } from "./CommonFields"
import { FileDropzone } from "./FileDropzone"
import { GradingProgress } from "./GradingProgress"
import type { GradingResponse } from "@/types"

const ACCEPTED_EXTS = ".py,.java,.cpp,.c,.js,.ts,.go"

interface Props {
  onResult: (r: GradingResponse) => void
  onError: (e: Error) => void
}

interface Progress { step: number; total: number; message: string }

export function FileMode({ onResult, onError }: Props) {
  const [problems, setProblems] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [rubricMode, setRubricMode] = useState<RubricMode>("guided")
  const [rubricText, setRubricText] = useState("")
  const [rubricCriteria, setRubricCriteria] = useState<RubricCriterion[]>(() => [
    emptyCriterion(),
  ])
  const [examples, setExamples] = useState<FewShotExample[]>([])
  const [withReason, setWithReason] = useState(true)
  const [isRunning, setIsRunning] = useState(false)
  const [progress, setProgress] = useState<Progress | null>(null)

  async function handleGrade() {
    if (!file || !problems.trim()) return
    setIsRunning(true)
    setProgress(null)
    try {
      const rubric = buildRubricString(rubricMode, rubricText, rubricCriteria)
      const few_shot_examples = normalizeExamples(examples)
      for await (const event of gradeFileStream({
        problems,
        code: file,
        rubric,
        few_shot_examples,
        with_reason: withReason,
      })) {
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
        rubricMode={rubricMode}
        rubricText={rubricText}
        rubricCriteria={rubricCriteria}
        examples={examples}
        withReason={withReason}
        onProblemsChange={setProblems}
        onRubricModeChange={setRubricMode}
        onRubricTextChange={setRubricText}
        onRubricCriteriaChange={setRubricCriteria}
        onExamplesChange={setExamples}
        onWithReasonChange={setWithReason}
      />

      <FileDropzone
        file={file}
        onChange={setFile}
        accept={ACCEPTED_EXTS}
        label="Source file"
        required
      />

      <Button
        onClick={handleGrade}
        disabled={isRunning || !problems.trim() || !file}
        className="w-full"
      >
        {isRunning ? "Grading…" : "Grade"}
      </Button>

      {isRunning && progress && <GradingProgress {...progress} />}
    </div>
  )
}
