"use client";

import { Loading03Icon, SentIcon } from "@hugeicons/core-free-icons";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { HugeIcon } from "@/components/ui/huge-icon";
import { Textarea } from "@/components/ui/textarea";
import { ACTIVITY_UPDATED_EVENT } from "@/lib/activity-events";
import { copilotChat } from "@/lib/api";
import type { CopilotMessage } from "@/types/enterprise";

export function CopilotPanel() {
  const [message, setMessage] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send() {
    if (!message.trim()) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await copilotChat(message.trim(), sessionId);
      setSessionId(result.session_id);
      setMessages(result.messages);
      setMessage("");
      window.dispatchEvent(new Event(ACTIVITY_UPDATED_EVENT));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Copilot failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Healthcare copilot</CardTitle>
        <CardDescription>
          Ask follow-up questions in this session. Answers combine your internal policy library
          and search results when available.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {messages.length > 0 && (
          <ul className="max-h-64 space-y-2 overflow-y-auto border border-border p-3 text-sm">
            {messages.map((m, i) => (
              <li key={`${m.role}-${i}`}>
                <span className="font-medium capitalize text-primary">{m.role}: </span>
                {m.content}
              </li>
            ))}
          </ul>
        )}
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask about workflows, policies, or collaboration…"
          rows={3}
        />
        {error && <p className="text-sm text-destructive">{error}</p>}
        <Button onClick={() => void send()} disabled={loading}>
          {loading ? (
            <HugeIcon icon={Loading03Icon} size={16} className="animate-spin" />
          ) : (
            <>
              <HugeIcon icon={SentIcon} size={16} className="mr-2" />
              Send
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
