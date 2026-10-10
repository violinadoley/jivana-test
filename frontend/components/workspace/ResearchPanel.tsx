"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ACTIVITY_UPDATED_EVENT } from "@/lib/activity-events";
import { researchSynthesize } from "@/lib/api";
import type { SearchResultItem } from "@/types/enterprise";

export function ResearchPanel() {
  const [question, setQuestion] = useState(
    "How should we handle weak evidence in medication reconciliation?"
  );
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<SearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    try {
      const out = await researchSynthesize(question);
      setAnswer(out.answer_markdown);
      setSources(out.sources);
      window.dispatchEvent(new Event(ACTIVITY_UPDATED_EVENT));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Research assistant</CardTitle>
        <CardDescription>
          Retrieves enterprise sources, then synthesizes cited answers for ops and quality teams.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea rows={3} value={question} onChange={(e) => setQuestion(e.target.value)} />
        <Button onClick={() => void run()} disabled={loading}>
          {loading ? "Researching…" : "Synthesize answer"}
        </Button>
        {sources.length > 0 && (
          <section>
            <h3 className="mb-2 text-sm font-medium">Sources</h3>
            <ul className="space-y-2 text-sm">
              {sources.map((s, i) => (
                <li key={i} className="border border-border p-2">
                  <span className="font-medium">{s.title}</span>
                  <span className="ml-2 text-xs text-primary">{s.source}</span>
                  <p className="text-muted-foreground">{s.snippet}</p>
                </li>
              ))}
            </ul>
          </section>
        )}
        {answer && (
          <pre className="whitespace-pre-wrap rounded-md border p-4 text-sm">{answer}</pre>
        )}
      </CardContent>
    </Card>
  );
}
