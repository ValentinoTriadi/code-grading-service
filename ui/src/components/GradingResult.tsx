import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { Separator } from "@/components/ui/separator"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { GradingResponse } from "@/types"

function Markdown({ children }: { children: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <p className="text-sm leading-relaxed mb-2 last:mb-0">{children}</p>,
        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
        em: ({ children }) => <em className="italic">{children}</em>,
        ul: ({ children }) => <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 my-2">{children}</ol>,
        li: ({ children }) => <li className="text-sm">{children}</li>,
        h1: ({ children }) => <h1 className="text-base font-bold mt-3 mb-1">{children}</h1>,
        h2: ({ children }) => <h2 className="text-sm font-bold mt-3 mb-1">{children}</h2>,
        h3: ({ children }) => <h3 className="text-sm font-semibold mt-2 mb-1">{children}</h3>,
        code: ({ children }) => (
          <code className="bg-muted px-1 py-0.5 rounded text-xs font-mono">{children}</code>
        ),
        pre: ({ children }) => (
          <pre className="bg-muted p-3 rounded-md text-xs font-mono overflow-x-auto my-2">{children}</pre>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-muted-foreground/30 pl-3 italic text-muted-foreground my-2">
            {children}
          </blockquote>
        ),
        hr: () => <Separator className="my-2" />,
      }}
    >
      {children}
    </ReactMarkdown>
  )
}

function ScoreDisplay({ score }: { score: number }) {
  const pct = Math.min(100, Math.max(0, score))

  const { bg, ring, label, text } =
    pct >= 85 ? { bg: "bg-emerald-50", ring: "ring-emerald-400", label: "Excellent", text: "text-emerald-700" } :
    pct >= 70 ? { bg: "bg-green-50",   ring: "ring-green-400",   label: "Good",      text: "text-green-700" } :
    pct >= 55 ? { bg: "bg-yellow-50",  ring: "ring-yellow-400",  label: "Fair",      text: "text-yellow-700" } :
    pct >= 40 ? { bg: "bg-orange-50",  ring: "ring-orange-400",  label: "Poor",      text: "text-orange-700" } :
                { bg: "bg-red-50",     ring: "ring-red-400",     label: "Failing",   text: "text-red-700" }

  return (
    <div className={`flex items-center gap-5 rounded-xl p-4 ${bg} ring-1 ${ring}`}>
      {/* Circular progress */}
      <div className="relative size-20 shrink-0">
        <svg viewBox="0 0 36 36" className="size-20 -rotate-90">
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="currentColor"
            className="text-black/10" strokeWidth="3" />
          <circle cx="18" cy="18" r="15.9" fill="none" stroke="currentColor"
            className={text} strokeWidth="3"
            strokeDasharray={`${pct} 100`}
            strokeLinecap="round" />
        </svg>
        <span className={`absolute inset-0 flex items-center justify-center text-xl font-bold ${text}`}>
          {pct}
        </span>
      </div>

      {/* Label + bar */}
      <div className="flex-1 space-y-1.5">
        <p className={`text-sm font-semibold ${text}`}>{label}</p>
        <div className="h-2 rounded-full bg-black/10 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              pct >= 85 ? "bg-emerald-500" :
              pct >= 70 ? "bg-green-500" :
              pct >= 55 ? "bg-yellow-500" :
              pct >= 40 ? "bg-orange-500" : "bg-red-500"
            }`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="text-xs text-muted-foreground">{pct} / 100</p>
      </div>
    </div>
  )
}

export function GradingResult({ result }: { result: GradingResponse }) {
  return (
    <div className="space-y-6">
      {/* Score */}
      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Score</p>
        <ScoreDisplay score={result.score} />
      </div>

      <Separator />

      {/* Feedback */}
      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Feedback</p>
        <Markdown>{result.feedback}</Markdown>
      </div>

      {/* Per-criterion breakdown */}
      {result.feedback_detail && (
        <>
          <Separator />
          <div className="space-y-4">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Breakdown</p>
            <Markdown>{result.feedback_detail.summary}</Markdown>

            {result.feedback_detail.criteria.length > 0 && (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Criterion</TableHead>
                    <TableHead className="text-right w-28">Score</TableHead>
                    <TableHead>Comment</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {result.feedback_detail.criteria.map((c, i) => (
                    <TableRow key={i}>
                      <TableCell className="font-medium whitespace-nowrap">{c.name}</TableCell>
                      <TableCell className="text-right whitespace-nowrap">
                        {c.score} / {c.max_score}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        <Markdown>{c.comment}</Markdown>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            {result.feedback_detail.suggestions.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm font-medium">Suggestions</p>
                {result.feedback_detail.suggestions.map((s, i) => (
                  <div key={i} className="flex gap-3 rounded-lg bg-amber-50 ring-1 ring-amber-200 px-3 py-2.5">
                    <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-amber-400 text-white text-xs font-bold">
                      {i + 1}
                    </span>
                    <div className="text-sm text-amber-900 leading-relaxed">
                      <Markdown>{s}</Markdown>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* Reasoning */}
      {result.reasoning && (
        <>
          <Separator />
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Reasoning</p>
            <div className="text-muted-foreground">
              <Markdown>{result.reasoning}</Markdown>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
