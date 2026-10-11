import { Suspense } from "react";

import { SmartLaunchPanel } from "@/components/smart/SmartLaunchPanel";

export default function SmartLaunchPage() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto max-w-2xl px-4 py-12 text-sm text-muted-foreground">
          Loading SMART launch…
        </main>
      }
    >
      <SmartLaunchPanel />
    </Suspense>
  );
}
