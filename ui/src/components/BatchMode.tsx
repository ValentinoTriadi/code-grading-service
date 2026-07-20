import { useState } from "react"
import { gradeBatchStream } from "@/api"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
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

interface Props {
  onError: (e: Error) => void
}

interface Progress {
  step: number
  total: number
  message: string
}

function b64ToBlob(b64: string): Blob {
  const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0))
  return new Blob([bytes], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  })
}

function triggerDownload(blob: Blob): string {
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = "grading_results.xlsx"
  a.click()
  return url
}

export function BatchMode({ onError }: Props) {
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
  const [statusMessage, setStatusMessage] = useState<string | null>(null)
  const [progress, setProgress] = useState<Progress | null>(null)
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)

  async function handleGrade() {
    if (!file || !problems.trim()) return
    if (downloadUrl) {
      URL.revokeObjectURL(downloadUrl)
      setDownloadUrl(null)
    }
    setIsRunning(true)
    setProgress(null)
    setStatusMessage("Uploading zip file…")

    try {
      const rubric = buildRubricString(rubricMode, rubricText, rubricCriteria)
      const few_shot_examples = normalizeExamples(examples)
      for await (const event of gradeBatchStream({
        problems,
        files: file,
        rubric,
        few_shot_examples,
        with_reason: withReason,
      })) {
        if (event.type === "error") {
          throw new Error(event.message)
        }
        if (event.type === "progress") {
          setStatusMessage(null)
          setProgress({
            step: event.done,
            total: event.total,
            message: `${event.filename}${event.error ? " — error" : ""}`,
          })
        }
        if (event.type === "complete") {
          setStatusMessage("Building Excel…")
          setProgress(null)
          const blob = b64ToBlob(event.excel)
          const url = triggerDownload(blob)
          setDownloadUrl(url)
        }
      }
    } catch (err) {
      onError(err instanceof Error ? err : new Error(String(err)))
    } finally {
      setIsRunning(false)
      setStatusMessage(null)
      setProgress(null)
    }
  }

  return (
    <div className="space-y-6">
      <Alert>
        <AlertDescription>
          Upload a <strong>.zip</strong> archive containing one source file per student.
          Results will be downloaded as an Excel file.
        </AlertDescription>
      </Alert>

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
        accept=".zip"
        label="Zip archive"
        required
      />

      <Button
        onClick={handleGrade}
        disabled={isRunning || !problems.trim() || !file}
        className="w-full"
      >
        {isRunning ? "Grading batch…" : "Grade & Download Excel"}
      </Button>

      {isRunning && statusMessage && (
        <div className="space-y-1.5">
          <p className="text-xs text-muted-foreground">{statusMessage}</p>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div className="h-full w-1/3 bg-primary rounded-full animate-[slide_1.2s_ease-in-out_infinite]" />
          </div>
        </div>
      )}

      {isRunning && progress && <GradingProgress {...progress} unit="files" />}

      {!isRunning && downloadUrl && (
        <Alert>
          <AlertDescription className="flex items-center justify-between gap-4">
            <span>Done! Your Excel file has been downloaded.</span>
            <a
              href={downloadUrl}
              download="grading_results.xlsx"
              className="shrink-0 text-sm font-medium underline underline-offset-2 hover:opacity-70 transition-opacity"
            >
              Download again
            </a>
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}
