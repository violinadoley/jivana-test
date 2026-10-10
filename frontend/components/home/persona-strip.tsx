const personas = [
  {
    role: "Hospital pharmacy",
    outcome: "Ranked discrepancies and cited evidence at discharge—less manual reconciliation time.",
  },
  {
    role: "Care transitions",
    outcome: "One calm workspace for policies, documents, and acknowledgment trails.",
  },
  {
    role: "Clinical operations",
    outcome: "Measure weak evidence and validation issues before orders reach the EHR.",
  },
] as const;

export function PersonaStrip() {
  return (
    <div className="grid gap-8 lg:grid-cols-[0.35fr_1fr] lg:items-end">
      <div>
        <p className="eyebrow">Who it&apos;s for</p>
        <h2 className="text-3xl font-semibold tracking-tight text-foreground">
          Teams on the front line
        </h2>
      </div>
      <ul className="grid gap-6 md:grid-cols-3">
        {personas.map((persona) => (
          <li key={persona.role} className="border-l border-primary/30 pl-5">
            <h3 className="font-display text-lg font-medium text-foreground">{persona.role}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{persona.outcome}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
