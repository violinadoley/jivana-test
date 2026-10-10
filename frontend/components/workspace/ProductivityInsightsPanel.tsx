"use client";

import { useEffect, useState } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchMedRecMetrics, fetchProductivityMetrics } from "@/lib/api";
import type { MedRecMetrics, ProductivityMetrics } from "@/types/enterprise";

type Props = {
  medRecMode?: boolean;
};

export function ProductivityInsightsPanel({ medRecMode = false }: Props) {
  const [metrics, setMetrics] = useState<ProductivityMetrics | null>(null);
  const [medRec, setMedRec] = useState<MedRecMetrics | null>(null);

  useEffect(() => {
    if (medRecMode) {
      void fetchMedRecMetrics().then(setMedRec).catch(() => setMedRec(null));
      return;
    }
    void fetchProductivityMetrics().then(setMetrics).catch(() => setMetrics(null));
  }, [medRecMode]);

  if (medRecMode) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Your team&apos;s workload</CardTitle>
          <CardDescription>Cases and medication lines that still need attention.</CardDescription>
        </CardHeader>
        <CardContent>
          {!medRec && (
            <p className="text-sm text-muted-foreground">
              Counts will appear when you are signed in and cases exist.
            </p>
          )}
          {medRec && (
            <dl className="grid grid-cols-2 gap-3">
              {(
                [
                  ["awaiting review", medRec.cases_awaiting_review],
                  ["legacy bulk", medRec.cases_legacy_bulk_acknowledged],
                  ["documented", medRec.cases_review_documented],
                  ["open items", medRec.open_items_total],
                  ["external wait", medRec.items_awaiting_external_action],
                ] as const
              ).map(([label, count]) => (
                <div key={label} className="border border-border p-3 text-center">
                  <dt className="text-xs text-muted-foreground">{label}</dt>
                  <dd className="font-heading text-2xl font-semibold">{count}</dd>
                </div>
              ))}
            </dl>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Productivity insights</CardTitle>
        <CardDescription>
          Firestore activity aggregates; stream events to BigQuery for enterprise analytics when
          configured.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!metrics && (
          <p className="text-sm text-muted-foreground">Metrics unavailable (API or Firestore).</p>
        )}
        {metrics && (
          <>
            {metrics.notes && (
              <p className="mb-4 text-sm text-muted-foreground">{metrics.notes}</p>
            )}
            <dl className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {Object.entries(metrics.totals).map(([key, count]) => (
                <div key={key} className="border border-border p-3 text-center">
                  <dt className="text-xs text-muted-foreground">{key.replace(/_/g, " ")}</dt>
                  <dd className="font-heading text-2xl font-semibold">{count}</dd>
                </div>
              ))}
            </dl>
            {Object.keys(metrics.totals).length === 0 && (
              <p className="text-sm text-muted-foreground">
                No events yet. Use copilot, search, documents, or meetings to populate insights.
              </p>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
