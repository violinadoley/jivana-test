import Link from "next/link";
import { ArrowRight01Icon } from "@hugeicons/core-free-icons";

import { HugeIcon } from "@/components/ui/huge-icon";

const steps = [
  {
    name: "Start a case",
    desc: "Enter a patient label and record number (use training IDs in demo mode).",
  },
  {
    name: "Add three documents",
    desc: "Home med list, discharge summary, and current prescriptions—PDF or text.",
  },
  {
    name: "Review each difference",
    desc: "Work the list one medication at a time with notes your team can audit later.",
  },
  {
    name: "Sign off",
    desc: "When every item is resolved, finalize and save or print the review summary.",
  },
] as const;

export function HomeClinicianBand() {
  return (
    <section className="section-ink">
      <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:py-20">
        <div className="grid gap-12 lg:grid-cols-[1fr_1.2fr] lg:items-start">
          <div className="space-y-6">
            <p className="text-[0.65rem] font-medium uppercase tracking-[0.28em] text-cream/60">
              How pharmacists use JIVANA
            </p>
            <h2 className="text-3xl font-semibold leading-tight tracking-tight sm:text-4xl">
              Four steps from upload to signed review
            </h2>
            <p className="text-sm leading-relaxed text-cream/75 sm:text-base">
              Built for transition-of-care workflows—not for IT configuration. Your team stays in
              control of every medication decision.
            </p>
            <Link
              href="/dashboard"
              className="inline-flex h-11 items-center gap-2 rounded-full bg-cream px-6 text-sm font-medium text-ink"
            >
              Go to my cases
              <HugeIcon icon={ArrowRight01Icon} size={18} />
            </Link>
          </div>

          <ol className="grid gap-3 sm:grid-cols-2">
            {steps.map((step, index) => (
              <li
                key={step.name}
                className="rounded-xl border border-cream/15 bg-cream/[0.06] p-4"
              >
                <p className="text-xs font-medium text-cream/60">Step {index + 1}</p>
                <p className="mt-1 font-medium text-cream">{step.name}</p>
                <p className="mt-1 text-xs leading-relaxed text-cream/70">{step.desc}</p>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
