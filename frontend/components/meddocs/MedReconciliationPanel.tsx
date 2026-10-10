"use client";

import { FileUp, Loader2 } from "lucide-react";
import { useCallback, useState } from "react";

import { PrototypeBanner } from "@/components/meddocs/PrototypeBanner";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  createMedReconciliation,
  submitMedReconciliationReview,
} from "@/lib/api";
import {
  bucketFileSize,
  fileExtension,
  trackAiWorkflowCompleted,
  trackAiWorkflowFailed,
  trackInputSubmitted,
  trackRecommendationReviewed,
} from "@/lib/posthog/events";
import type { MedReconciliationJob } from "@/types/meddocs";

const ACCEPT = ".pdf,.txt";

function statusVariant(
  status: string
): "default" | "secondary" | "destructive" | "outline" {
  if (status === "completed") {
    return "secondary";
  }
  if (status === "needs_review") {
    return "destructive";
  }
  if (status === "failed") {
    return "destructive";
  }
  return "outline";
}

export function MedReconciliationPanel() {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [job, setJob] = useState<MedReconciliationJob | null>(null);
  const [reviewNote, setReviewNote] = useState("");

  const onFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files ? Array.from(e.target.files) : [];
    setFiles(list.slice(0, 3));
    e.target.value = "";
  }, []);

  const runReconciliation = useCallback(async () => {
    if (files.length < 1) {
      setError("Upload 1–3 synthetic documents (prior, discharge, prescription).");
      return;
    }
    for (const f of files) {
      trackInputSubmitted("meddocs_reconciliation", {
        file_extension: fileExtension(f.name),
        size_bytes_bucket: bucketFileSize(f.size),
      });
    }
    setLoading(true);
    setError(null);
    setJob(null);
    const started = performance.now();
    try {
      const result = await createMedReconciliation(files);
      setJob(result);
      trackAiWorkflowCompleted(
        "meddocs_reconciliation",
        Math.round(performance.now() - started)
      );
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Reconciliation failed.";
      setError(msg);
      trackAiWorkflowFailed(
        "meddocs_reconciliation",
        Math.round(performance.now() - started),
        msg
      );
    } finally {
      setLoading(false);
    }
  }, [files]);

  async function acknowledgeReview() {
    if (!job || job.status !== "needs_review") {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const updated = await submitMedReconciliationReview(job.job_id, {
        note: reviewNote || "Acknowledged for demo.",
        corrections_count: 0,
      });
      setJob({
        ...job,
        status: updated.status as MedReconciliationJob["status"],
        human_review: updated.human_review,
      });
      trackRecommendationReviewed("meddocs_reconciliation");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Review submit failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <PrototypeBanner />
      <Card>
        <CardHeader>
          <CardTitle>Medication reconciliation</CardTitle>
          <CardDescription>
            Upload up to three synthetic PDFs or text files. Evidence is shown
            from server-resolved source blocks only.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border border-dashed p-8 text-sm text-muted-foreground hover:bg-muted/40">
            <FileUp className="h-8 w-8" />
            <span>Select 1–3 files ({ACCEPT})</span>
            <input
              type="file"
              accept={ACCEPT}
              multiple
              className="hidden"
              onChange={onFileChange}
            />
          </label>
          {files.length > 0 && (
            <ul className="text-sm text-muted-foreground">
              {files.map((f) => (
                <li key={f.name}>{f.name}</li>
              ))}
            </ul>
          )}
          <Button onClick={() => void runReconciliation()} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing…
              </>
            ) : (
              "Run reconciliation"
            )}
          </Button>
          {error && (
            <Alert variant="destructive">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {job && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-2">
            <div>
              <CardTitle className="text-lg">Job {job.job_id.slice(0, 8)}…</CardTitle>
              <CardDescription>
                {job.reconciliation_used_weak_evidence
                  ? "Weak evidence (vertex_only/low) — cannot auto-complete."
                  : "Evidence from verified blocks where configured."}
              </CardDescription>
            </div>
            <Badge variant={statusVariant(job.status)}>{job.status}</Badge>
          </CardHeader>
          <CardContent className="space-y-6">
            {job.discrepancies.length > 0 && (
              <section>
                <h3 className="mb-2 font-medium">Discrepancies</h3>
                <ul className="space-y-2 text-sm">
                  {job.discrepancies.map((d, i) => (
                    <li key={i} className="rounded-md border p-3">
                      <span className="font-mono text-xs">{d.discrepancy_type}</span>
                      <p>{d.summary}</p>
                      {d.left_source?.source_text && (
                        <p className="mt-1 text-muted-foreground">
                          Left: {d.left_source.source_text}
                        </p>
                      )}
                      {d.right_source?.source_text && (
                        <p className="text-muted-foreground">
                          Right: {d.right_source.source_text}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              </section>
            )}
            {Object.entries(job.medications_by_document).length > 0 && (
              <section>
                <h3 className="mb-2 font-medium">Medications by document</h3>
                {Object.entries(job.medications_by_document).map(([docId, meds]) => (
                  <div key={docId} className="mb-3">
                    <p className="text-xs text-muted-foreground">{docId}</p>
                    <ul className="text-sm">
                      {meds.map((m, idx) => (
                        <li key={idx}>
                          {m.medication_name} — {m.dose ?? m.strength}{" "}
                          <Badge variant="outline" className="ml-1 text-[10px]">
                            {m.evidence_status}
                          </Badge>
                          {m.source_ref.source_text && (
                            <span className="block text-muted-foreground">
                              {m.source_ref.source_text}
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </section>
            )}
            {job.status === "needs_review" && (
              <div className="space-y-2">
                <textarea
                  className="w-full rounded-md border bg-background p-2 text-sm"
                  placeholder="Reviewer note (acknowledge only)"
                  value={reviewNote}
                  onChange={(e) => setReviewNote(e.target.value)}
                  rows={2}
                />
                <Button variant="secondary" onClick={() => void acknowledgeReview()} disabled={loading}>
                  Acknowledge review
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
