import {
  AiBrain01Icon,
  SecurityCheckIcon,
  SparklesIcon,
  UserGroupIcon,
} from "@hugeicons/core-free-icons";

import { HugeIcon } from "@/components/ui/huge-icon";

const features = [
  {
    icon: AiBrain01Icon,
    title: "Smarter knowledge",
    body: "Pulls medication lines from uploaded documents and lines them up for side-by-side comparison.",
  },
  {
    icon: UserGroupIcon,
    title: "Clinician-first review",
    body: "Med reconciliation and discrepancies stay in a queue until a named reviewer acknowledges each item.",
  },
  {
    icon: SecurityCheckIcon,
    title: "Secure by design",
    body: "Sign-in, role-based access, and a full history of who reviewed each medication line.",
  },
  {
    icon: SparklesIcon,
    title: "Built for operations",
    body: "Discharge med rec on one tab; search, meetings, and copilot on the next—without leaving the workspace.",
  },
] as const;

export function HomeFeatureRow() {
  return (
    <section id="features" className="border-t border-border/60 bg-background py-16 sm:py-20">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 sm:grid-cols-2 sm:px-6 lg:grid-cols-4 lg:gap-8">
        {features.map((item) => (
          <div key={item.title} className="space-y-3">
            <div className="flex size-11 items-center justify-center rounded-2xl bg-primary/10">
              <HugeIcon icon={item.icon} size={22} className="text-primary" />
            </div>
            <h3 className="text-base font-semibold text-foreground">{item.title}</h3>
            <p className="text-sm leading-relaxed text-muted-foreground">{item.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
