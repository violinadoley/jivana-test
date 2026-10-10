"use client";

import { FileUp, Loader2 } from "lucide-react";
import { useCallback, useState } from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { notifyActivityUpdated } from "@/lib/activity-events";
import { uploadFile } from "@/lib/api";
import {
  bucketFileSize,
  fileExtension,
  trackAiWorkflowCompleted,
  trackAiWorkflowFailed,
  trackInputSubmitted,
  trackRecommendationReviewed,
} from "@/lib/posthog/events";
import type { FileUploadResponse } from "@/types/api";

const ACCEPT = ".pdf,.png,.jpg,.jpeg,.txt";

export function FileUpload() {
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<FileUploadResponse | null>(null);

  const processFile = useCallback(async (file: File) => {
    trackInputSubmitted("file_upload", {
      file_extension: fileExtension(file.name),
      size_bytes_bucket: bucketFileSize(file.size),
    });
    setLoading(true);
    setError(null);
    setResult(null);
    const started = performance.now();
    try {
      const data = await uploadFile(file);
      setResult(data);
      notifyActivityUpdated();
      trackAiWorkflowCompleted(
        "file_upload",
        Math.round(performance.now() - started)
      );
      trackRecommendationReviewed("file_upload");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Upload failed.";
      setError(msg);
      trackAiWorkflowFailed(
        "file_upload",
        Math.round(performance.now() - started),
        msg
      );
    } finally {
      setLoading(false);
    }
  }, []);

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) {
      void processFile(file);
    }
    e.target.value = "";
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      void processFile(file);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>File upload</CardTitle>
        <CardDescription>
          PDF, PNG, JPEG, or TXT. Validated on the API; stored in Cloud Storage when
          the backend bucket is configured.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          className={`flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed p-8 text-center transition-colors ${
            dragOver ? "border-primary bg-muted/40" : "border-muted-foreground/30"
          }`}
        >
          <FileUp className="size-8 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            Drag and drop a file, or choose one below.
          </p>
          <label
            className={cn(
              buttonVariants({ variant: "secondary" }),
              loading && "pointer-events-none opacity-50",
              "cursor-pointer"
            )}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 size-4 animate-spin" />
                Uploading…
              </>
            ) : (
              "Choose file"
            )}
            <input
              type="file"
              accept={ACCEPT}
              className="sr-only"
              onChange={onFileChange}
              disabled={loading}
            />
          </label>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertTitle>Upload error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {result && (
          <div className="rounded-lg bg-muted/50 p-4 text-sm space-y-1">
            <p>
              <span className="font-medium">File:</span> {result.filename}
            </p>
            <p>
              <span className="font-medium">Type:</span> {result.content_type}
            </p>
            <p>
              <span className="font-medium">Size:</span> {result.size_bytes}{" "}
              bytes
            </p>
            <p>
              <span className="font-medium">Storage key:</span>{" "}
              {result.storage_key ?? "Not stored (configure GCS bucket)"}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
