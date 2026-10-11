const pillars = [
  {
    num: "01",
    title: "Find",
    body: "Vertex AI Search plus your institutional corpus—one search bar for SOPs, policies, and playbooks.",
  },
  {
    num: "02",
    title: "Understand",
    body: "Copilot sessions, research synthesis with sources, and meeting briefs with owned action items.",
  },
  {
    num: "03",
    title: "Act with proof",
    body: "Discharge med rec with per-item review and sign-off—plus workflow agents when you need a guided plan.",
  },
] as const;

export function HomeApproach() {
  return (
    <section id="approach" className="border-t border-border/60 bg-background py-20 sm:py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="eyebrow-accent">Our approach</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            Modern stack, clinical judgment first
          </h2>
          <p className="mt-4 text-muted-foreground">
            Every generative step is visible in the product—search hits, extraction citations, and
            review gates—not hidden behind empty dashboards.
          </p>
        </div>

        <ul className="mt-14 grid gap-6 md:grid-cols-3">
          {pillars.map((item) => (
            <li
              key={item.num}
              className="rounded-3xl border border-border/60 bg-card p-6 shadow-[0_8px_32px_-16px_rgba(15,23,42,0.08)] sm:p-8"
            >
              <span className="text-3xl font-semibold tabular-nums text-primary/40">
                {item.num}
              </span>
              <h3 className="mt-4 text-lg font-semibold text-foreground">{item.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{item.body}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
