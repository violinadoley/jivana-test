import Link from "next/link";

export function HomeBottomCta() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      <div
        className="absolute inset-0 bg-gradient-to-br from-primary/15 via-[oklch(0.88_0.06_280)] to-primary/10"
        aria-hidden
      />
      <div
        className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-background/80 to-transparent"
        aria-hidden
      />
      <svg
        className="absolute bottom-0 left-0 right-0 h-40 w-full text-primary/10"
        viewBox="0 0 1440 120"
        preserveAspectRatio="none"
        aria-hidden
      >
        <path
          fill="currentColor"
          d="M0,80 C360,120 720,40 1080,70 C1260,85 1380,95 1440,90 L1440,120 L0,120 Z"
        />
      </svg>

      <div className="relative mx-auto max-w-3xl px-4 text-center sm:px-6">
        <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Start with discharge med rec—or explore the full workspace
        </h2>
        <p className="mt-4 text-muted-foreground">
          Load sample charts in minutes, then try search, meeting briefs, and copilot from the same
          dashboard. Use de-identified files only.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex h-11 items-center rounded-full bg-foreground px-6 text-sm font-medium text-background shadow-md"
          >
            Open workspace
          </Link>
          <Link
            href="/#product"
            className="inline-flex h-11 items-center rounded-full px-6 text-sm font-medium text-foreground"
          >
            See the product
          </Link>
        </div>
      </div>
    </section>
  );
}
