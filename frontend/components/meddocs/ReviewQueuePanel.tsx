"use client";

import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { fetchMedReviewQueue } from "@/lib/api";
import type { MedReconciliationJob } from "@/types/meddocs";

type Props = {
  onSelectJob?: (job: MedReconciliationJob) => void;
};

export function ReviewQueuePanel({ onSelectJob }: Props) {
  const [items, setItems] = useState<MedReconciliationJob[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async (showSpinner: boolean) => {
    if (showSpinner) {
      setLoading(true);
    }
    setError(null);
    try {
      setItems(await fetchMedReviewQueue());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load queue.");
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
        const next = await fetchMedReviewQueue();
        if (active) {
          setItems(next);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to load queue.");
          setItems([]);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    })();

    return () => {
      active = false;
    };
  }, []);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Review queue</CardTitle>
          <CardDescription>Jobs awaiting human acknowledgment</CardDescription>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => void load(true)}
          disabled={loading}
        >
          Refresh
        </Button>
      </CardHeader>
      <CardContent>
        {error && <p className="text-sm text-destructive">{error}</p>}
        {items.length === 0 && !loading && (
          <p className="text-sm text-muted-foreground">No jobs need review.</p>
        )}
        <ul className="space-y-2">
          {items.map((job) => (
            <li key={job.job_id}>
              <button
                type="button"
                className="flex w-full items-center justify-between rounded-md border p-3 text-left text-sm hover:bg-muted/50"
                onClick={() => onSelectJob?.(job)}
              >
                <span className="font-mono text-xs">{job.job_id.slice(0, 10)}…</span>
                <Badge variant="destructive">{job.discrepancies.length} issues</Badge>
              </button>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
