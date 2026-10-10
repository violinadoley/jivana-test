const steps = [
  {
    title: "Ingest",
    detail: "Upload discharge, prior, and Rx lists. Document AI extracts cited blocks.",
  },
  {
    title: "Reconcile",
    detail: "Vertex compares medications and surfaces dose gaps and documented changes.",
  },
  {
    title: "Review",
    detail: "Clinicians acknowledge every discrepancy—no silent auto-approval.",
  },
  {
    title: "Export",
    detail: "Signed-off bundles write to Cloud Healthcare API FHIR for audit.",
  },
] as const;

export function WorkflowJourney() {
  return (
    <ol className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {steps.map((step, index) => (
        <li
          key={step.title}
          className="rounded-2xl border border-border/80 bg-background p-6"
        >
          <span className="font-display text-sm text-muted-foreground">
            {String(index + 1).padStart(2, "0")}
          </span>
          <h3 className="mt-2 font-display text-lg font-medium text-foreground">{step.title}</h3>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{step.detail}</p>
        </li>
      ))}
    </ol>
  );
}
