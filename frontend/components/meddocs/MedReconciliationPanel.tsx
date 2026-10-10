"use client";

import { Loading03Icon, Upload04Icon } from "@hugeicons/core-free-icons";
import { useCallback, useState } from "react";

import { ACTIVITY_UPDATED_EVENT } from "@/lib/activity-events";

import { PrototypeBanner } from "@/components/meddocs/PrototypeBanner";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HugeIcon } from "@/components/ui/huge-icon";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { createMedReconciliation } from "@/lib/api";
import {
  bucketFileSize,
  fileExtension,
  trackAiWorkflowCompleted,
  trackAiWorkflowFailed,
  trackInputSubmitted,
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

type Props = {
  initialJob?: MedReconciliationJob | null;
  onJobChange?: () => void;
};

export function MedReconciliationPanel({ initialJob = null, onJobChange }: Props) {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [job, setJob] = useState<MedReconciliationJob | null>(initialJob);

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
      onJobChange?.();
      window.dispatchEvent(new Event(ACTIVITY_UPDATED_EVENT));
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
  }, [files, onJobChange]);

  return (
    <div className="space-y-4">
      <PrototypeBanner />
      <Card>
        <CardHeader>
          <CardTitle>Document intelligence · Medication reconciliation</CardTitle>
          <CardDescription>
            Upload up to three synthetic clinical-administrative files. JIVANA
            extracts structured fields and routes discrepancies for human review.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <label className="flex cursor-pointer flex-col items-center justify-center gap-2 border border-dashed border-border p-8 text-sm text-muted-foreground">
            <HugeIcon icon={Upload04Icon} size={32} />
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
                <HugeIcon
                  icon={Loading03Icon}
                  size={16}
                  className="mr-2 animate-spin"
                />
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
            {job.fhir_export_resource && (
              <p className="text-xs text-muted-foreground">
                FHIR export:{" "}
                {job.fhir_export_resource === "failed"
                  ? "Export to the health record was not completed. Contact your administrator."
                  : job.fhir_export_resource}
              </p>
            )}
            {job.status === "needs_review" && (
              <Alert>
                <AlertTitle>Per-item review required</AlertTitle>
                <AlertDescription>
                  Each medication difference must be reviewed individually. Open{" "}
                  <strong>Medication reconciliation</strong> from the menu to continue this case.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
