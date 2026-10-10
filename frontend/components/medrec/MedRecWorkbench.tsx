"use client";

import { Loading03Icon, Upload04Icon } from "@hugeicons/core-free-icons";
import { useCallback, useEffect, useMemo, useState } from "react";

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
import { ProductivityInsightsPanel } from "@/components/workspace/ProductivityInsightsPanel";
import { ACTIVITY_UPDATED_EVENT } from "@/lib/activity-events";
import {
  beginMedRecItemReview,
  completeMedRecItemReview,
  createMedRecCase,
  fetchMedRecCase,
  fetchMedRecReviewSummaryHtml,
  finalizeMedRecCaseReview,
  listMedRecCases,
  openHtmlSummaryInNewTab,
  patchMedRecCaseItem,
  reconcileMedRecCase,
} from "@/lib/api";
import { brand } from "@/lib/brand";
import { loadSyntheticDemoMeddocs } from "@/lib/demo-meddocs";
import {
  labelCaseStatus,
  labelDetectionType,
  labelItemStatus,
  labelTransitionType,
} from "@/lib/medrec-labels";
import { cn } from "@/lib/utils";
import type {
  CaseListFilter,
  DiscrepancyItem,
  DiscrepancyItemStatus,
  ItemReviewPatchRequest,
  MedReconciliationJob,
} from "@/types/meddocs";

const ACCEPT = ".pdf,.txt";

const FILTERS: { id: CaseListFilter; label: string }[] = [
  { id: "all", label: "All patients" },
  { id: "draft", label: "Not started" },
  { id: "awaiting_review", label: "Needs review" },
  { id: "legacy_bulk_acknowledged", label: "Imported cases" },
  { id: "review_documented", label: "Completed" },
];

const CLOSURE: DiscrepancyItemStatus[] = [
  "resolved_intentional",
  "resolved_externally_closed",
  "resolved_not_relevant",
];

function itemSummary(item: DiscrepancyItem): string {
  if (item.discrepancy) {
    return item.discrepancy.summary;
  }
  if (item.finding) {
    return item.finding.message;
  }
  return "Review item";
}

function caseTitle(job: MedReconciliationJob): string {
  const label = (job.case_label ?? "").trim();
  if (label) {
    return label;
  }
  if (job.synthetic_mrn) {
    return `Discharge — ${job.synthetic_mrn}`;
  }
  return `Case ${job.job_id.slice(0, 8)}`;
}

function statusBadgeVariant(
  status: string
): "default" | "secondary" | "destructive" | "outline" {
  if (status === "review_documented") {
    return "secondary";
  }
  if (status === "legacy_bulk_acknowledged") {
    return "outline";
  }
  if (status === "awaiting_review") {
    return "destructive";
  }
  return "outline";
}

type ItemEditorProps = {
  item: DiscrepancyItem;
  caseStatus: MedReconciliationJob["case_status"];
  busy: boolean;
  onSubmit: (body: ItemReviewPatchRequest) => Promise<void>;
};

function ItemReviewEditor({ item, caseStatus, busy, onSubmit }: ItemEditorProps) {
  const [action, setAction] = useState<string>("");
  const [note, setNote] = useState("");
  const [extra, setExtra] = useState("");

  const canReopen =
    caseStatus === "review_documented" &&
    CLOSURE.includes(item.status);

  const actions = useMemo(() => {
    const opts: { value: string; label: string }[] = [];
    if (canReopen) {
      opts.push({ value: "reopen", label: "Reopen item" });
    }
    if (item.status === "open" || item.status === "legacy_unreviewed") {
      opts.push(
        { value: "resolved_not_relevant", label: "Not relevant" },
        { value: "resolved_intentional", label: "Intentional / verified" },
        { value: "pending_clarification", label: "Pending clarification" },
        { value: "awaiting_external_action", label: "Awaiting external action" }
      );
    }
    if (item.status === "pending_clarification") {
      opts.push(
        { value: "resolved_intentional", label: "Resolved intentional" },
        { value: "resolved_not_relevant", label: "Not relevant" },
        { value: "awaiting_external_action", label: "Awaiting external action" }
      );
    }
    if (item.status === "awaiting_external_action") {
      opts.push(
        { value: "resolved_externally_closed", label: "Closed externally" },
        { value: "resolved_not_relevant", label: "Not relevant" }
      );
    }
    return opts;
  }, [canReopen, item.status]);

  const extraLabel = useMemo(() => {
    if (action === "reopen") {
      return "Reopen reason";
    }
    if (action === "resolved_not_relevant") {
      return "Dismissal rationale";
    }
    if (action === "resolved_intentional") {
      return "Verification basis";
    }
    if (action === "pending_clarification") {
      return "Clarification note";
    }
    if (action === "awaiting_external_action") {
      return "External action required";
    }
    if (action === "resolved_externally_closed") {
      return "External evidence";
    }
    return "Detail";
  }, [action]);

  const apply = async () => {
    if (!action) {
      return;
    }
    let body: ItemReviewPatchRequest;
    if (action === "reopen") {
      body = {
        to_status: "open",
        note,
        reopen_reason: extra,
      };
    } else {
      body = {
        to_status: action as DiscrepancyItemStatus,
        note,
      };
      if (action === "resolved_not_relevant") {
        body.dismissal_rationale = extra;
      } else if (action === "resolved_intentional") {
        body.verification_basis = extra;
      } else if (action === "pending_clarification") {
        body.clarification_note = extra;
      } else if (action === "awaiting_external_action") {
        body.external_action_required = extra;
      } else if (action === "resolved_externally_closed") {
        body.external_evidence = extra;
      }
    }
    await onSubmit(body);
    setAction("");
    setNote("");
    setExtra("");
  };

  if (actions.length === 0) {
    return (
      <p className="text-xs text-muted-foreground">
        Item in closure state. Reopen from a documented case if needed.
      </p>
    );
  }

  return (
    <div className="mt-3 space-y-2 border-t border-border pt-3">
      <select
        className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
        value={action}
        onChange={(e) => setAction(e.target.value)}
        aria-label="Review action"
      >
        <option value="">Choose action…</option>
        {actions.map((a) => (
          <option key={a.value} value={a.value}>
            {a.label}
          </option>
        ))}
      </select>
      <textarea
        className="min-h-[60px] w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
        placeholder="Review note (required)"
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />
      {action && action !== "open" && (
        <textarea
          className="min-h-[48px] w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
          placeholder={extraLabel}
          value={extra}
          onChange={(e) => setExtra(e.target.value)}
        />
      )}
      <Button type="button" size="sm" disabled={busy || !action || !note.trim()} onClick={() => void apply()}>
        Apply review
      </Button>
    </div>
  );
}

export function MedRecWorkbench() {
  const [filter, setFilter] = useState<CaseListFilter>("all");
  const [cases, setCases] = useState<MedReconciliationJob[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selected, setSelected] = useState<MedReconciliationJob | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingCase, setLoadingCase] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [newLabel, setNewLabel] = useState("Discharge review — Sample patient");
  const [newMrn, setNewMrn] = useState("TRAIN-1001");
  const [newTransition, setNewTransition] = useState<"discharge" | "admission" | "transfer">(
    "discharge"
  );
  const [uploadFiles, setUploadFiles] = useState<File[]>([]);
  const [finalizeNote, setFinalizeNote] = useState("");
  const [weakAck, setWeakAck] = useState(false);
  const [noDiscAck, setNoDiscAck] = useState(false);

  const refreshList = useCallback(async () => {
    setLoadingList(true);
    try {
      const list = await listMedRecCases(filter);
      setCases(list);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load cases.");
    } finally {
      setLoadingList(false);
    }
  }, [filter]);

  useEffect(() => {
    let active = true;
    void listMedRecCases(filter)
      .then((list) => {
        if (active) {
          setCases(list);
        }
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Could not load cases.");
        }
      })
      .finally(() => {
        if (active) {
          setLoadingList(false);
        }
      });
    return () => {
      active = false;
    };
  }, [filter]);

  const loadCase = useCallback(async (id: string) => {
    setLoadingCase(true);
    setError(null);
    try {
      const job = await fetchMedRecCase(id);
      setSelected(job);
      setSelectedId(id);
      setWeakAck(job.reconciliation_used_weak_evidence);
      setNoDiscAck(job.discrepancy_items.length === 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load case.");
    } finally {
      setLoadingCase(false);
    }
  }, []);

  const createCase = async () => {
    setBusy(true);
    setError(null);
    try {
      const job = await createMedRecCase({
        case_label: newLabel,
        synthetic_mrn: newMrn || null,
        transition_type: newTransition,
      });
      await refreshList();
      await loadCase(job.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create case.");
    } finally {
      setBusy(false);
    }
  };

  const runReconcile = async () => {
    if (!selected || uploadFiles.length < 1) {
      setError("Please add three documents: home med list, discharge summary, and prescriptions.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const job = await reconcileMedRecCase(selected.job_id, uploadFiles);
      setSelected(job);
      setUploadFiles([]);
      await refreshList();
      window.dispatchEvent(new Event(ACTIVITY_UPDATED_EVENT));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reconciliation failed.");
    } finally {
      setBusy(false);
    }
  };

  const patchItem = async (itemId: string, body: ItemReviewPatchRequest) => {
    if (!selected) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const job = await patchMedRecCaseItem(selected.job_id, itemId, body);
      setSelected(job);
      await refreshList();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update item.");
    } finally {
      setBusy(false);
    }
  };

  const beginLegacy = async () => {
    if (!selected) {
      return;
    }
    setBusy(true);
    try {
      const job = await beginMedRecItemReview(selected.job_id);
      setSelected(job);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not begin item review.");
    } finally {
      setBusy(false);
    }
  };

  const completeItems = async () => {
    if (!selected) {
      return;
    }
    setBusy(true);
    try {
      const job = await completeMedRecItemReview(selected.job_id);
      setSelected(job);
      await refreshList();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Complete item review failed.");
    } finally {
      setBusy(false);
    }
  };

  const openSummary = async () => {
    if (!selected) {
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const html = await fetchMedRecReviewSummaryHtml(selected.job_id);
      openHtmlSummaryInNewTab(html);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load review summary.");
    } finally {
      setBusy(false);
    }
  };

  const loadDemoFiles = async () => {
    setError(null);
    try {
      setUploadFiles(await loadSyntheticDemoMeddocs());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load demo documents.");
    }
  };

  const finalize = async () => {
    if (!selected) {
      return;
    }
    setBusy(true);
    try {
      const job = await finalizeMedRecCaseReview(selected.job_id, {
        attestation_note: finalizeNote || null,
        weak_evidence_acknowledged: weakAck,
        no_discrepancies_attestation: noDiscAck,
      });
      setSelected(job);
      await refreshList();
      window.dispatchEvent(new Event(ACTIVITY_UPDATED_EVENT));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Finalize failed.");
    } finally {
      setBusy(false);
    }
  };

  const allItemsClosed =
    selected &&
    selected.discrepancy_items.length > 0 &&
    selected.discrepancy_items.every((i) => CLOSURE.includes(i.status));

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 space-y-8 px-4 py-8 sm:px-6 sm:py-10">
      <div className="max-w-3xl border-b border-border pb-8">
        <p className="eyebrow">{brand.track}</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Discharge medication reconciliation
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground sm:text-base">
          {brand.medRecLead}
        </p>
      </div>

      <PrototypeBanner />

      {error && (
        <Alert variant="destructive">
          <AlertTitle>Something went wrong</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Patient cases</CardTitle>
              <CardDescription>Show cases by status</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {FILTERS.map((f) => (
                  <button
                    key={f.id}
                    type="button"
                    onClick={() => {
                      setLoadingList(true);
                      setFilter(f.id);
                    }}
                    className={cn(
                      "rounded-full px-3 py-1 text-xs font-medium",
                      filter === f.id
                        ? "bg-primary text-primary-foreground"
                        : "border border-border text-muted-foreground"
                    )}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
              {loadingList && (
                <p className="text-sm text-muted-foreground">Loading…</p>
              )}
              <ul className="max-h-64 space-y-2 overflow-y-auto">
                {cases.map((c) => (
                  <li key={c.job_id}>
                    <button
                      type="button"
                      onClick={() => void loadCase(c.job_id)}
                      className={cn(
                        "w-full rounded-md border px-3 py-2 text-left text-sm",
                        selectedId === c.job_id
                          ? "border-primary bg-primary/5"
                          : "border-border hover:bg-muted/50"
                      )}
                    >
                      <span className="font-medium">{caseTitle(c)}</span>
                      <Badge
                        variant={statusBadgeVariant(c.case_status)}
                        className="ml-2 align-middle text-[10px]"
                      >
                        {labelCaseStatus(c.case_status)}
                      </Badge>
                    </button>
                  </li>
                ))}
                {!loadingList && cases.length === 0 && (
                  <p className="text-sm text-muted-foreground">No cases match this filter.</p>
                )}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">New medication review</CardTitle>
              <CardDescription>
                Discharge, admission, or transfer — same compare-and-sign-off workflow.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <label className="block text-xs font-medium text-muted-foreground">
                Care transition
                <select
                  className="mt-1 w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
                  value={newTransition}
                  onChange={(e) =>
                    setNewTransition(e.target.value as "discharge" | "admission" | "transfer")
                  }
                >
                  <option value="discharge">Discharge</option>
                  <option value="admission">Admission</option>
                  <option value="transfer">Transfer</option>
                </select>
              </label>
              <input
                className="w-full rounded-md border border-border px-2 py-1.5 text-sm"
                value={newLabel}
                onChange={(e) => setNewLabel(e.target.value)}
                aria-label="Patient or case name"
                placeholder="e.g. Discharge review — J. Smith"
              />
              <input
                className="w-full rounded-md border border-border px-2 py-1.5 text-sm"
                value={newMrn}
                onChange={(e) => setNewMrn(e.target.value)}
                aria-label="Medical record number"
                placeholder="Medical record number (use training ID in demo)"
              />
              <Button type="button" disabled={busy} onClick={() => void createCase()}>
                Start new {labelTransitionType(newTransition).toLowerCase()} review
              </Button>
            </CardContent>
          </Card>

          <ProductivityInsightsPanel medRecMode />
        </div>

        <div className="space-y-6 lg:col-span-2">
          {!selected && (
            <Card>
              <CardContent className="py-12 text-center text-sm text-muted-foreground">
                Select a patient case on the left, or start a new discharge review.
              </CardContent>
            </Card>
          )}

          {selected && (
            <>
              <Card>
                <CardHeader>
                  <div className="flex flex-wrap items-center gap-2">
                    <CardTitle>{caseTitle(selected)}</CardTitle>
                    <Badge variant={statusBadgeVariant(selected.case_status)}>
                      {labelCaseStatus(selected.case_status)}
                    </Badge>
                    {selected.reconciliation_used_weak_evidence && (
                      <Badge variant="outline">Verify source documents</Badge>
                    )}
                  </div>
                  <CardDescription>
                    {labelTransitionType(selected.transition_type)} · {selected.documents.length}{" "}
                    document
                    {selected.documents.length === 1 ? "" : "s"} uploaded ·{" "}
                    {selected.discrepancy_items.length} medication line
                    {selected.discrepancy_items.length === 1 ? "" : "s"} to review
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {selected.case_status === "draft" && (
                    <div className="space-y-3 rounded-md border border-dashed border-border p-4">
                      <p className="text-sm font-medium text-foreground">Step 1 — Add documents</p>
                      <p className="text-sm text-muted-foreground">
                        Home medication list, hospital discharge summary, and current prescriptions
                        (PDF or text).
                      </p>
                      <input
                        type="file"
                        accept={ACCEPT}
                        multiple
                        onChange={(e) => {
                          const list = e.target.files ? Array.from(e.target.files) : [];
                          setUploadFiles(list.slice(0, 3));
                          e.target.value = "";
                        }}
                      />
                      <div className="flex flex-wrap gap-2">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          disabled={busy}
                          onClick={() => void loadDemoFiles()}
                        >
                          Use sample patient documents
                        </Button>
                        {uploadFiles.length > 0 && (
                          <span className="self-center text-xs text-muted-foreground">
                            {uploadFiles.map((f) => f.name).join(", ")}
                          </span>
                        )}
                      </div>
                      <Button
                        type="button"
                        disabled={busy || uploadFiles.length < 1}
                        onClick={() => void runReconcile()}
                      >
                        {busy ? (
                          <HugeIcon icon={Loading03Icon} className="mr-2 size-4 animate-spin" />
                        ) : (
                          <HugeIcon icon={Upload04Icon} className="mr-2 size-4" />
                        )}
                        Compare medication lists
                      </Button>
                    </div>
                  )}

                  {selected.case_status === "legacy_bulk_acknowledged" &&
                    !selected.legacy_item_review_started && (
                      <Alert>
                        <AlertTitle>This case was imported from an older list</AlertTitle>
                        <AlertDescription>
                          Each medication must be reviewed individually before you can sign off.
                        </AlertDescription>
                        <Button
                          type="button"
                          className="mt-3"
                          size="sm"
                          disabled={busy}
                          onClick={() => void beginLegacy()}
                        >
                          Start reviewing medications
                        </Button>
                      </Alert>
                    )}

                  {selected.discrepancy_items.length === 0 &&
                    selected.case_status !== "draft" && (
                      <p className="text-sm text-muted-foreground">
                        No differences were found between documents. You can still sign off after
                        confirming the lists match.
                      </p>
                    )}

                  {selected.discrepancy_items.map((item) => (
                    <div
                      key={item.item_id}
                      className="rounded-md border border-border p-4"
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm font-medium">{itemSummary(item)}</span>
                        <Badge variant="outline">{labelItemStatus(item.status)}</Badge>
                      </div>
                      {item.discrepancy && (
                        <p className="mt-1 text-xs text-muted-foreground">
                          {labelDetectionType(item.discrepancy.discrepancy_type)}
                        </p>
                      )}
                      <ItemReviewEditor
                        item={item}
                        caseStatus={selected.case_status}
                        busy={busy}
                        onSubmit={(body) => patchItem(item.item_id, body)}
                      />
                      {item.review_history.length > 0 && (
                        <details className="mt-3 text-xs text-muted-foreground">
                          <summary>Previous decisions ({item.review_history.length})</summary>
                          <ol className="mt-2 list-decimal space-y-1 pl-4">
                            {item.review_history.map((ev) => (
                              <li key={ev.event_id}>
                                {ev.reviewed_at.slice(0, 16).replace("T", " ")} ·{" "}
                                {labelItemStatus(ev.from_status)} →{" "}
                                {labelItemStatus(ev.to_status)}: {ev.note}
                              </li>
                            ))}
                          </ol>
                        </details>
                      )}
                    </div>
                  ))}

                  {allItemsClosed && selected.case_status !== "review_documented" && (
                    <Button
                      type="button"
                      variant="secondary"
                      disabled={busy}
                      onClick={() => void completeItems()}
                    >
                      Mark all items reviewed
                    </Button>
                  )}

                  {selected.case_status === "awaiting_review" && (
                    <div className="space-y-3 border-t border-border pt-4">
                      <h3 className="text-sm font-semibold">Sign off on this review</h3>
                      <p className="text-xs text-muted-foreground">
                        This documents that you completed reconciliation—it is not a clinical order.
                      </p>
                      {selected.reconciliation_used_weak_evidence && (
                        <label className="flex items-center gap-2 text-sm">
                          <input
                            type="checkbox"
                            checked={weakAck}
                            onChange={(e) => setWeakAck(e.target.checked)}
                          />
                          I verified medications against the source documents (some text was
                          unclear in the upload).
                        </label>
                      )}
                      {selected.discrepancy_items.length === 0 && (
                        <label className="flex items-center gap-2 text-sm">
                          <input
                            type="checkbox"
                            checked={noDiscAck}
                            onChange={(e) => setNoDiscAck(e.target.checked)}
                          />
                          I confirm there are no medication differences requiring action.
                        </label>
                      )}
                      <textarea
                        className="min-h-[56px] w-full rounded-md border border-border px-2 py-1.5 text-sm"
                        placeholder="Optional note for the chart (e.g. spoke with covering MD)"
                        value={finalizeNote}
                        onChange={(e) => setFinalizeNote(e.target.value)}
                      />
                      <div className="flex flex-wrap gap-2">
                        <Button type="button" disabled={busy} onClick={() => void finalize()}>
                          Complete sign-off
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          disabled={busy}
                          onClick={() => void openSummary()}
                        >
                          View review summary
                        </Button>
                      </div>
                    </div>
                  )}

                  {selected.case_status === "review_documented" && (
                    <div className="flex flex-wrap gap-2 border-t border-border pt-4">
                      <p className="w-full text-sm text-muted-foreground">
                        Signed off
                        {selected.finalized_by_display
                          ? ` by ${selected.finalized_by_display}`
                          : ""}
                        {selected.finalized_at
                          ? ` on ${selected.finalized_at.slice(0, 10)}`
                          : ""}
                        . To change a decision, reopen a medication line below and sign off again.
                      </p>
                      <Button
                        type="button"
                        variant="outline"
                        disabled={busy}
                        onClick={() => void openSummary()}
                      >
                        View review summary
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          )}

          {loadingCase && (
            <p className="text-sm text-muted-foreground">Loading case…</p>
          )}
        </div>
      </div>
    </main>
  );
}
