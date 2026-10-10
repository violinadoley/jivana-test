"use client";

import {
  Loading03Icon,
  RefreshIcon,
  SentIcon,
  ThumbsDownIcon,
  ThumbsUpIcon,
} from "@hugeicons/core-free-icons";
import { useEffect, useRef, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { HugeIcon } from "@/components/ui/huge-icon";
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
        <CardTitle>Knowledge assistant</CardTitle>
        <CardDescription>
          Answers use your institutional policy library when relevant, then complete the response
          with secure server-side AI.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          <Textarea
            placeholder="Ask about a workflow, policy, or document…"
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
                  <HugeIcon
                    icon={Loading03Icon}
                    size={16}
                    className="mr-2 animate-spin"
                  />
                  Generating…
                </>
              ) : (
                <>
                  <HugeIcon icon={SentIcon} size={16} className="mr-2" />
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
              <HugeIcon icon={RefreshIcon} size={16} className="mr-2" />
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
          <div className="border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
            No response yet. Submit a question to see the assistant reply here.
          </div>
        )}

        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <HugeIcon icon={Loading03Icon} size={16} className="animate-spin" />
            Waiting for the model…
          </div>
        )}

        {response && (
          <div className="space-y-3">
            <div
              className="border border-border bg-muted/40 p-4 text-sm whitespace-pre-wrap"
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
                <HugeIcon icon={ThumbsUpIcon} size={16} />
              </Button>
              <Button
                type="button"
                size="icon"
                variant="outline"
                aria-label="Not useful"
                disabled={feedbackSent}
                onClick={() => sendFeedback(false)}
              >
                <HugeIcon icon={ThumbsDownIcon} size={16} />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
