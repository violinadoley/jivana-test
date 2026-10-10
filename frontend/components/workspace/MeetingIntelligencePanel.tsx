"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ACTIVITY_UPDATED_EVENT } from "@/lib/activity-events";
import { analyzeMeeting } from "@/lib/api";

const SAMPLE = `Facilitator: Weekly care transitions standup.
Pharmacy: Three discharge reconciliations waiting review.
Ops: Document AI latency improved after processor verification.
Action: Nurses to acknowledge dose mismatches before EHR update.`;

export function MeetingIntelligencePanel() {
  const [transcript, setTranscript] = useState(SAMPLE);
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function analyze() {
    setLoading(true);
    try {
      const out = await analyzeMeeting(transcript, "Care transitions standup");
      setResult(out.analysis_markdown);
      window.dispatchEvent(new Event(ACTIVITY_UPDATED_EVENT));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Meeting intelligence</CardTitle>
        <CardDescription>
          Summaries, decisions, and action items from clinical ops meetings (paste transcript).
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea rows={8} value={transcript} onChange={(e) => setTranscript(e.target.value)} />
        <Button onClick={() => void analyze()} disabled={loading}>
          {loading ? "Analyzing…" : "Generate meeting brief"}
        </Button>
        {result && (
          <article className="prose prose-sm max-w-none border border-border p-4 dark:prose-invert">
            <pre className="whitespace-pre-wrap font-sans text-sm">{result}</pre>
          </article>
        )}
      </CardContent>
    </Card>
  );
}
