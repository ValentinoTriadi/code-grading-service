import type { FewShotPayload } from "./lib/grading-form"
import type { GradingResponse } from "./types"

const BASE = "/api/v1"

export interface InlineGradingParams {
  problems: string
  code: string
  rubric?: string
  few_shot_examples?: FewShotPayload[]
  with_reason: boolean
}

export interface FileGradingParams {
  problems: string
  code: File
  rubric?: string
  few_shot_examples?: FewShotPayload[]
  with_reason: boolean
}

export interface BatchGradingParams {
  problems: string
  files: File
  rubric?: string
  few_shot_examples?: FewShotPayload[]
  with_reason: boolean
}

export async function gradeInline(params: InlineGradingParams): Promise<GradingResponse> {
  const res = await fetch(`${BASE}/grade/inline`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? "Request failed")
  }
  return res.json()
}

export async function gradeFile(params: FileGradingParams): Promise<GradingResponse> {
  const form = new FormData()
  form.append("problems", params.problems)
  form.append("code", params.code)
  if (params.rubric) form.append("rubric", params.rubric)
  if (params.few_shot_examples?.length) {
    form.append("few_shot_examples", JSON.stringify(params.few_shot_examples))
  }
  form.append("with_reason", String(params.with_reason))

  const res = await fetch(`${BASE}/grade/file`, { method: "POST", body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? "Request failed")
  }
  return res.json()
}

export async function gradeBatch(params: BatchGradingParams): Promise<Blob> {
  const form = new FormData()
  form.append("problems", params.problems)
  form.append("files", params.files)
  if (params.rubric) form.append("rubric", params.rubric)
  if (params.few_shot_examples?.length) {
    form.append("few_shot_examples", JSON.stringify(params.few_shot_examples))
  }
  form.append("with_reason", String(params.with_reason))

  const res = await fetch(`${BASE}/grade/batch`, { method: "POST", body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? "Request failed")
  }
  return res.blob()
}

export type GradingProgressEvent =
  | { type: "progress"; step: number; total: number; message: string }
  | { type: "result"; data: GradingResponse }
  | { type: "error"; message: string }

async function* streamPost(url: string, body: string | FormData): AsyncGenerator<unknown> {
  const headers: Record<string, string> = {}
  if (typeof body === "string") headers["Content-Type"] = "application/json"

  const res = await fetch(url, { method: "POST", headers, body })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? "Request failed")
  }

  const reader = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split("\n")
    buffer = lines.pop() ?? ""
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        yield JSON.parse(line.slice(6))
      }
    }
  }
}

export async function* gradeInlineStream(params: InlineGradingParams): AsyncGenerator<GradingProgressEvent> {
  yield* streamPost(`${BASE}/grade/inline/stream`, JSON.stringify(params)) as AsyncGenerator<GradingProgressEvent>
}

export async function* gradeFileStream(params: FileGradingParams): AsyncGenerator<GradingProgressEvent> {
  const form = new FormData()
  form.append("problems", params.problems)
  form.append("code", params.code)
  if (params.rubric) form.append("rubric", params.rubric)
  if (params.few_shot_examples?.length) {
    form.append("few_shot_examples", JSON.stringify(params.few_shot_examples))
  }
  form.append("with_reason", String(params.with_reason))
  yield* streamPost(`${BASE}/grade/file/stream`, form) as AsyncGenerator<GradingProgressEvent>
}

export type BatchProgressEvent =
  | { type: "progress"; done: number; total: number; filename: string; score: number | null; error: string | null }
  | { type: "complete"; excel: string }
  | { type: "error"; message: string }

export async function* gradeBatchStream(params: BatchGradingParams): AsyncGenerator<BatchProgressEvent> {
  const form = new FormData()
  form.append("problems", params.problems)
  form.append("files", params.files)
  if (params.rubric) form.append("rubric", params.rubric)
  if (params.few_shot_examples?.length) {
    form.append("few_shot_examples", JSON.stringify(params.few_shot_examples))
  }
  form.append("with_reason", String(params.with_reason))

  const res = await fetch(`${BASE}/grade/batch/stream`, { method: "POST", body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? "Request failed")
  }

  const reader = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split("\n")
    buffer = lines.pop() ?? ""
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        yield JSON.parse(line.slice(6)) as BatchProgressEvent
      }
    }
  }
}
