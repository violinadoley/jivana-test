"use client";

import { SlidingNumber } from "@/components/animate-ui/primitives/texts/sliding-number";

const metrics = [
  { label: "Knowledge surfaces", value: 4 },
  { label: "Review gates", value: 1 },
  { label: "Cloud regions", value: 2 },
] as const;

export function HeroMetrics() {
  return (
    <dl className="grid grid-cols-3 gap-4 border border-border bg-card/60 px-4 py-6 sm:gap-8 sm:px-8">
      {metrics.map((item) => (
        <div key={item.label} className="space-y-1 text-center sm:text-left">
          <dt className="text-xs uppercase tracking-wide text-muted-foreground">
            {item.label}
          </dt>
          <dd className="text-2xl font-semibold tabular-nums text-foreground sm:text-3xl">
            <SlidingNumber number={item.value} inViewOnce initiallyStable />
          </dd>
        </div>
      ))}
    </dl>
  );
}
