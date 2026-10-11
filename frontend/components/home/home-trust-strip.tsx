const partners = [
  "Regional health network",
  "Academic medical center",
  "Community hospital group",
  "Pharmacy collaborative",
  "Digital health lab",
] as const;

export function HomeTrustStrip() {
  return (
    <section className="border-y border-border/60 bg-background py-12">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <p className="text-center text-sm text-muted-foreground">
          Built for teams like leading healthcare organisations
        </p>
        <ul className="mt-8 flex flex-wrap items-center justify-center gap-x-10 gap-y-4">
          {partners.map((name) => (
            <li
              key={name}
              className="text-sm font-semibold tracking-tight text-muted-foreground/45"
            >
              {name}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
