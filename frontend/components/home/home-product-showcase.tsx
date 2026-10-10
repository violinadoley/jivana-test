import Link from "next/link";
import {
  Activity01Icon,
  AiBrain01Icon,
  File02Icon,
  Home01Icon,
  Search01Icon,
  Settings01Icon,
} from "@hugeicons/core-free-icons";

import { HugeIcon } from "@/components/ui/huge-icon";

const navItems = [
  { icon: Home01Icon, label: "Overview" },
  { icon: File02Icon, label: "Documents" },
  { icon: Search01Icon, label: "Search" },
  { icon: AiBrain01Icon, label: "Copilot" },
  { icon: Activity01Icon, label: "Insights" },
  { icon: Settings01Icon, label: "Settings" },
] as const;

function MiniSparkline() {
  return (
    <svg viewBox="0 0 120 32" className="h-8 w-full text-primary" aria-hidden>
      <path
        d="M0 24 L15 18 L30 22 L45 12 L60 16 L75 8 L90 14 L105 6 L120 10"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

function DocPreview() {
  return (
    <div className="space-y-2 rounded-xl border border-border/80 bg-muted/30 p-3">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">
        Source · discharge summary
      </p>
      <div className="space-y-1.5">
        <div className="h-2 w-full rounded-full bg-border" />
        <div className="h-2 w-[92%] rounded-full bg-border" />
        <div className="h-2 w-[78%] rounded-full bg-primary/25" />
        <div className="h-2 w-[85%] rounded-full bg-border" />
      </div>
      <p className="text-[10px] text-muted-foreground">Lisinopril 10 mg → 20 mg · cited p.2</p>
    </div>
  );
}

export function HomeProductShowcase() {
  return (
    <section id="product" className="section-soft py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow-accent">Product</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            From documents to direction
          </h2>
          <p className="mt-4 text-base leading-relaxed text-muted-foreground">
            See reconciliation status, AI insight, and review gates in one calm surface—what your
            team sees in the live workspace.
          </p>
        </div>

        <div className="mt-14 overflow-hidden rounded-3xl border border-border/60 bg-card shadow-[0_24px_80px_-24px_rgba(15,23,42,0.18)]">
          <div className="flex min-h-[420px] flex-col lg:flex-row">
            <aside className="flex flex-row gap-1 border-b border-border/60 bg-primary/[0.06] p-3 lg:w-52 lg:flex-col lg:border-b-0 lg:border-r lg:py-6">
              {navItems.map((item, index) => (
                <div
                  key={item.label}
                  className={
                    index === 0
                      ? "flex items-center gap-2 rounded-xl bg-background px-3 py-2 text-xs font-medium text-foreground shadow-sm"
                      : "flex items-center gap-2 rounded-xl px-3 py-2 text-xs text-muted-foreground"
                  }
                >
                  <HugeIcon icon={item.icon} size={16} />
                  <span className="hidden sm:inline">{item.label}</span>
                </div>
              ))}
            </aside>

            <div className="flex flex-1 flex-col lg:flex-row">
              <div className="flex-1 space-y-5 p-6 sm:p-8">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">Case overview</p>
                    <h3 className="text-xl font-semibold text-foreground">Discharge med rec · M.R.</h3>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Age 54 · Home, discharge, and Rx on file
                    </p>
                  </div>
                  <div className="flex size-12 items-center justify-center rounded-full bg-primary/15 text-sm font-semibold text-primary">
                    MR
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {["Summary", "Medications", "Review queue", "Export"].map((tab, i) => (
                    <span
                      key={tab}
                      className={
                        i === 0
                          ? "rounded-full bg-foreground px-3 py-1 text-xs font-medium text-background"
                          : "rounded-full px-3 py-1 text-xs text-muted-foreground"
                      }
                    >
                      {tab}
                    </span>
                  ))}
                </div>

                <div className="rounded-2xl border border-primary/20 bg-primary/[0.07] p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-primary">
                    AI insight
                  </p>
                  <p className="mt-2 text-sm leading-relaxed text-foreground">
                    Dose increase for lisinopril is documented on discharge but not on the prior
                    home list. Route to{" "}
                    <span className="font-medium">needs review</span> until pharmacy acknowledges.
                  </p>
                </div>

                <div className="grid gap-3 sm:grid-cols-3">
                  {[
                    { label: "Open discrepancies", value: "2" },
                    { label: "Acknowledged today", value: "5" },
                    { label: "FHIR export", value: "Ready" },
                  ].map((m) => (
                    <div
                      key={m.label}
                      className="rounded-2xl border border-border/80 bg-background p-4 shadow-sm"
                    >
                      <p className="text-[11px] text-muted-foreground">{m.label}</p>
                      <p className="mt-1 text-lg font-semibold tabular-nums text-foreground">
                        {m.value}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border-t border-border/60 bg-muted/20 p-6 lg:w-72 lg:border-t-0 lg:border-l">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Evidence
                </p>
                <DocPreview />
                <div className="mt-4 rounded-xl border border-border/80 bg-background p-3">
                  <p className="text-[10px] font-medium text-muted-foreground">Activity trend</p>
                  <MiniSparkline />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-10 text-center">
          <Link
            href="/dashboard"
            className="inline-flex h-11 items-center rounded-full bg-foreground px-6 text-sm font-medium text-background shadow-md"
          >
            Open live workspace
          </Link>
        </div>
      </div>
    </section>
  );
}
