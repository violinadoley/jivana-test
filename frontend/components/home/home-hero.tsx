import Link from "next/link";
import { ArrowRight01Icon, PlayIcon } from "@hugeicons/core-free-icons";

import { HeroVisual } from "@/components/home/hero-visual";
import { HugeIcon } from "@/components/ui/huge-icon";
import { brand } from "@/lib/brand";

export function HomeHero() {
  return (
    <section className="relative overflow-hidden bg-background pt-8 pb-16 sm:pt-12 sm:pb-24">
      <div className="pointer-events-none absolute -right-32 top-0 size-[480px] rounded-full bg-primary/[0.06] blur-3xl" />
      <div className="mx-auto grid max-w-6xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-2 lg:gap-16">
        <div className="space-y-8">
          <p className="eyebrow-accent">Healthcare operations · Future of Work</p>
          <h1 className="text-4xl font-semibold leading-[1.08] tracking-tight text-foreground sm:text-5xl lg:text-[3.25rem]">
            {brand.tagline}
          </h1>
          <p className="max-w-lg text-base leading-relaxed text-muted-foreground sm:text-lg">
            {brand.description}
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/dashboard"
              className="inline-flex h-11 items-center gap-2 rounded-full bg-foreground px-6 text-sm font-medium text-background shadow-md"
            >
              Open workspace
              <HugeIcon icon={ArrowRight01Icon} size={18} />
            </Link>
            <Link
              href="/#product"
              className="inline-flex h-11 items-center gap-2 rounded-full px-4 text-sm font-medium text-foreground"
            >
              <span className="flex size-8 items-center justify-center rounded-full border border-border bg-card shadow-sm">
                <HugeIcon icon={PlayIcon} size={14} />
              </span>
              Watch how it works
            </Link>
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-lg lg:max-w-none">
          <HeroVisual />

          <div className="absolute -bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:w-64">
            <div className="rounded-2xl border border-border/60 bg-card/95 p-4 shadow-lg backdrop-blur-sm">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-xs font-semibold text-foreground">Review item flagged</p>
                  <p className="mt-0.5 text-[11px] text-muted-foreground">Dose change · needs ack</p>
                </div>
                <span className="rounded-full bg-primary/15 px-2 py-0.5 text-[10px] font-medium text-primary">
                  Live
                </span>
              </div>
              <svg viewBox="0 0 200 40" className="mt-3 h-10 w-full text-primary" aria-hidden>
                <path
                  d="M0 28 L25 22 L50 26 L75 14 L100 18 L125 10 L150 16 L175 8 L200 12"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
