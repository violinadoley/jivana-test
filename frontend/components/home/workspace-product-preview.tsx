import { JivanaLogo } from "@/components/brand/jivana-logo";

const tabs = ["Overview", "Copilot", "Search", "Documents", "Meetings"] as const;

const queueItems = [
  { id: "a1", label: "Dose mismatch", detail: "Lisinopril 10 mg → 20 mg", status: "Needs review" },
  { id: "a2", label: "Documented change", detail: "Metformin held at discharge", status: "Ack pending" },
] as const;

const activity = [
  "Copilot answered med-rec policy question",
  "Enterprise search: reconciliation SOP",
  "Reconciliation job submitted (3 files)",
] as const;

/**
 * Real UI chrome preview — not a placeholder gradient block.
 */
export function WorkspaceProductPreview() {
  return (
    <div className="w-full overflow-hidden rounded-2xl border border-border bg-card shadow-xl shadow-foreground/[0.06] ring-1 ring-foreground/[0.04]">
      <div className="flex items-center gap-3 border-b border-border bg-muted/50 px-4 py-2.5">
        <div className="flex gap-1.5" aria-hidden>
          <span className="size-2.5 rounded-full bg-[oklch(0.75_0.12_25)]" />
          <span className="size-2.5 rounded-full bg-[oklch(0.82_0.12_85)]" />
          <span className="size-2.5 rounded-full bg-[oklch(0.72_0.14_145)]" />
        </div>
        <span className="truncate text-xs text-muted-foreground">jivana · healthcare workspace</span>
      </div>

      <div className="border-b border-border px-4 py-3">
        <div className="flex items-center justify-between gap-4">
          <JivanaLogo size="sm" />
          <span className="rounded-full bg-primary px-3 py-1 text-xs font-medium text-primary-foreground">
            Live demo
          </span>
        </div>
        <div className="mt-3 flex flex-wrap gap-1.5">
          {tabs.map((tab) => (
            <span
              key={tab}
              className={
                tab === "Documents"
                  ? "rounded-full bg-primary px-2.5 py-1 text-[11px] font-medium text-primary-foreground"
                  : "rounded-full border border-border px-2.5 py-1 text-[11px] text-muted-foreground"
              }
            >
              {tab}
            </span>
          ))}
        </div>
      </div>

      <div className="grid gap-3 p-4 sm:grid-cols-2">
        <div className="rounded-xl border border-border bg-background p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Review queue
          </p>
          <ul className="mt-2 space-y-2">
            {queueItems.map((item) => (
              <li key={item.id} className="rounded-lg border border-border px-2.5 py-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-medium text-foreground">{item.label}</span>
                  <span className="shrink-0 rounded-full bg-destructive/10 px-2 py-0.5 text-[10px] font-medium text-destructive">
                    {item.status}
                  </span>
                </div>
                <p className="mt-0.5 text-[11px] text-muted-foreground">{item.detail}</p>
              </li>
            ))}
          </ul>
        </div>

        <div className="space-y-3">
          <div className="rounded-xl border border-border bg-background p-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Copilot
            </p>
            <p className="mt-2 text-xs leading-relaxed text-foreground">
              <span className="font-medium">You:</span> What is our weak-evidence policy?
            </p>
            <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
              <span className="font-medium text-foreground">Jivana:</span> Routes to{" "}
              <code className="rounded bg-muted px-1">needs_review</code> until a clinician
              acknowledges…
            </p>
          </div>
          <div className="rounded-xl border border-border bg-background p-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Recent activity
            </p>
            <ul className="mt-2 space-y-1.5 text-[11px] text-muted-foreground">
              {activity.map((line) => (
                <li key={line} className="flex gap-2">
                  <span className="mt-1.5 size-1 shrink-0 rounded-full bg-primary" />
                  {line}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5 border-t border-border bg-muted/30 px-4 py-3">
        {["Cited sources", "Per-item review", "Sign-off record", "Audit history"].map((chip) => (
          <span
            key={chip}
            className="rounded-full border border-border bg-background px-2 py-0.5 text-[10px] font-medium text-foreground"
          >
            {chip}
          </span>
        ))}
      </div>
    </div>
  );
}
