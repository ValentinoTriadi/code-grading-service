import { useState } from "react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { BatchMode } from "./components/BatchMode"
import { FileMode } from "./components/FileMode"
import { GradingResult } from "./components/GradingResult"
import { InlineMode } from "./components/InlineMode"
import type { GradingResponse } from "@/types"

export function App() {
  const [result, setResult] = useState<GradingResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  function handleResult(r: GradingResponse) {
    setError(null)
    setResult(r)
  }

  function handleError(e: Error) {
    setResult(null)
    setError(e.message)
  }

  function handleTabChange() {
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-muted/40 py-10 px-4">
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Code Grading Service</h1>
          <p className="text-muted-foreground text-sm mt-1">
            LLM-powered code grading with rubric-based evaluation.
          </p>
        </div>

        <Tabs defaultValue="inline" onValueChange={handleTabChange}>
          <TabsList className="w-full">
            <TabsTrigger value="inline" className="flex-1">Inline</TabsTrigger>
            <TabsTrigger value="file" className="flex-1">File</TabsTrigger>
            <TabsTrigger value="batch" className="flex-1">Batch</TabsTrigger>
          </TabsList>

          <Card className="mt-4">
            <CardHeader className="pb-4">
              <TabsContent value="inline" className="mt-0">
                <CardTitle>Inline Code</CardTitle>
                <CardDescription>Paste student code directly as text.</CardDescription>
              </TabsContent>
              <TabsContent value="file" className="mt-0">
                <CardTitle>File Upload</CardTitle>
                <CardDescription>Upload a single source code file.</CardDescription>
              </TabsContent>
              <TabsContent value="batch" className="mt-0">
                <CardTitle>Batch (Zip)</CardTitle>
                <CardDescription>Upload a zip archive of multiple submissions.</CardDescription>
              </TabsContent>
            </CardHeader>

            <CardContent>
              <TabsContent value="inline" className="mt-0">
                <InlineMode onResult={handleResult} onError={handleError} />
              </TabsContent>
              <TabsContent value="file" className="mt-0">
                <FileMode onResult={handleResult} onError={handleError} />
              </TabsContent>
              <TabsContent value="batch" className="mt-0">
                <BatchMode onError={handleError} />
              </TabsContent>
            </CardContent>
          </Card>
        </Tabs>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {result && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle>Result</CardTitle>
              <CardDescription>Grading result for the submitted code.</CardDescription>
            </CardHeader>
            <CardContent>
              <GradingResult result={result} />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
