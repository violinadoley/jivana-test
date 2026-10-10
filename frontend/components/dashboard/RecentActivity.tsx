"use client";

import { Loading03Icon } from "@hugeicons/core-free-icons";
import { useCallback, useEffect, useState } from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { HugeIcon } from "@/components/ui/huge-icon";
import { ACTIVITY_UPDATED_EVENT } from "@/lib/activity-events";
import { listActivity } from "@/lib/api";
import type { ActivityItem } from "@/types/api";

function formatWhen(iso: string | null | undefined): string {
  if (!iso) {
    return "Just now";
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return "Recently";
  }
  return date.toLocaleString();
}

function typeLabel(type: ActivityItem["type"]): string {
  switch (type) {
    case "ai_generate":
      return "AI";
    case "file_upload":
      return "Upload";
    case "meddocs_reconciliation":
      return "Med rec";
    case "meddocs_review":
      return "Review";
    case "copilot_chat":
      return "Copilot";
    case "meeting_intelligence":
      return "Meeting";
    case "research":
      return "Research";
    case "workflow_agent":
      return "Agent";
    case "enterprise_search":
      return "Search";
    default:
      return "Activity";
  }
}

export function RecentActivity() {
  const [items, setItems] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (showSpinner: boolean) => {
    if (showSpinner) {
      setLoading(true);
    }
    setError(null);
    try {
      const next = await listActivity(20);
      setItems(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load activity.");
      setItems([]);
    } finally {
      if (showSpinner) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    let active = true;

    void (async () => {
      setLoading(true);
      setError(null);
      try {
        const next = await listActivity(20);
        if (active) {
          setItems(next);
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error ? err.message : "Could not load activity."
          );
          setItems([]);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    })();

    const onUpdate = () => {
      void load(false);
    };
    window.addEventListener(ACTIVITY_UPDATED_EVENT, onUpdate);
    return () => {
      active = false;
      window.removeEventListener(ACTIVITY_UPDATED_EVENT, onUpdate);
    };
  }, [load]);

  return (
    <Card id="recent-activity">
      <CardHeader>
        <CardTitle>Recent activity</CardTitle>
        <CardDescription>
          AI messages and file uploads saved via the API (Firestore when configured).
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <HugeIcon icon={Loading03Icon} size={16} className="animate-spin" />
            Loading…
          </div>
        )}

        {!loading && error && (
          <p className="text-sm text-muted-foreground">{error}</p>
        )}

        {!loading && !error && items.length === 0 && (
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="rounded-lg border border-dashed border-border px-3 py-2">
              <span className="font-medium text-foreground">Copilot</span> — ask a policy or
              workflow question in the Copilot tab.
            </li>
            <li className="rounded-lg border border-dashed border-border px-3 py-2">
              <span className="font-medium text-foreground">Documents</span> — run med rec or upload
              files; events appear here when Firestore is configured.
            </li>
            <li className="rounded-lg border border-dashed border-border px-3 py-2">
              <span className="font-medium text-foreground">Search &amp; research</span> — enterprise
              search and synthesis log activity after each run.
            </li>
          </ul>
        )}

        {!loading && items.length > 0 && (
          <ul className="space-y-3 text-sm">
            {items.map((item) => (
              <li
                key={item.id}
                className="flex flex-col gap-1 rounded-md border px-3 py-2 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <span className="mr-2 rounded bg-muted px-1.5 py-0.5 text-xs font-medium">
                    {typeLabel(item.type)}
                  </span>
                  <span>{item.title}</span>
                  {item.summary ? (
                    <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
                      {item.summary}
                    </p>
                  ) : null}
                </div>
                <span className="shrink-0 text-muted-foreground">
                  {formatWhen(item.created_at ?? null)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
