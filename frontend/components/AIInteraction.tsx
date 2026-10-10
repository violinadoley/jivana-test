"use client";

import { Loader2, RotateCcw, Send, ThumbsDown, ThumbsUp } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { notifyActivityUpdated } from "@/lib/activity-events";
import { generateAI } from "@/lib/api";
import {
  bucketInputLength,
  trackActionApproved,
  trackAiWorkflowCompleted,
  trackAiWorkflowFailed,
  trackFeedbackSubmitted,
  trackInputSubmitted,
  trackRecommendationReviewed,
} from "@/lib/posthog/events";

export function AIInteraction() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const reviewedRef = useRef(false);

  useEffect(() => {
    if (response && !reviewedRef.current) {
      reviewedRef.current = true;
      trackRecommendationReviewed("ai_chat");
    }
  }, [response]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || loading) {
      return;
    }
    trackInputSubmitted("ai_chat", {
      input_length_bucket: bucketInputLength(trimmed.length),
    });
    setLoading(true);
    setError(null);
    setFeedbackSent(false);
    reviewedRef.current = false;
    const started = performance.now();
    try {
      const text = await generateAI(trimmed);
      setResponse(text);
      notifyActivityUpdated();
      trackAiWorkflowCompleted("ai_chat", Math.round(performance.now() - started));
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      setError(msg);
      setResponse(null);
      trackAiWorkflowFailed(
        "ai_chat",
        Math.round(performance.now() - started),
        msg
      );
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setMessage("");
    setResponse(null);
    setError(null);
    setFeedbackSent(false);
    reviewedRef.current = false;
  }

  function sendFeedback(useful: boolean) {
    trackFeedbackSubmitted("ai_chat", useful);
    setFeedbackSent(true);
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Assistant</CardTitle>
        <CardDescription>
          Send a message to the backend Gemini service. TODO: customize prompts
          and domain logic for your hackathon use case.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          <Textarea
            placeholder="Ask anything…"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={4}
            disabled={loading}
            data-ph-mask
          />
          <div className="flex flex-wrap gap-2">
            <Button type="submit" disabled={loading || !message.trim()}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 size-4 animate-spin" />
                  Generating…
                </>
              ) : (
                <>
                  <Send className="mr-2 size-4" />
                  Submit
                </>
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleReset}
              disabled={loading && !response && !error}
            >
              <RotateCcw className="mr-2 size-4" />
              Reset
            </Button>
          </div>
        </form>

        {error && (
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {!error && !response && !loading && (
          <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
            No response yet. Submit a message to see AI output here.
          </div>
        )}

        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="size-4 animate-spin" />
            Waiting for the model…
          </div>
        )}

        {response && (
          <div className="space-y-3">
            <div
              className="rounded-lg bg-muted/50 p-4 text-sm whitespace-pre-wrap"
              data-ph-mask
            >
              {response}
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Button
                type="button"
                size="sm"
                variant="secondary"
                onClick={() => trackActionApproved("ai_chat")}
              >
                Accept result
              </Button>
              <span className="text-xs text-muted-foreground">Was this useful?</span>
              <Button
                type="button"
                size="icon"
                variant="outline"
                aria-label="Useful"
                disabled={feedbackSent}
                onClick={() => sendFeedback(true)}
              >
                <ThumbsUp className="size-4" />
              </Button>
              <Button
                type="button"
                size="icon"
                variant="outline"
                aria-label="Not useful"
                disabled={feedbackSent}
                onClick={() => sendFeedback(false)}
              >
                <ThumbsDown className="size-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
