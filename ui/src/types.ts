export interface CriterionResult {
  name: string
  score: number
  max_score: number
  comment: string
}

export interface FeedbackDetail {
  summary: string
  criteria: CriterionResult[]
  suggestions: string[]
}

export interface GradingResponse {
  score: number
  feedback: string
  feedback_detail: FeedbackDetail | null
  reasoning: string | null
}
