import type { ReactNode } from "react";

import { hybridToolMeta, type HybridWorkspaceTabId } from "@/lib/workspace-tabs";

type Props = {
  tab: Exclude<HybridWorkspaceTabId, "medrec">;
  children: ReactNode;
};

export function WorkspaceToolFrame({ tab, children }: Props) {
  const meta = hybridToolMeta[tab];

  return (
    <main className="mx-auto w-full max-w-6xl flex-1 space-y-8 px-4 py-8 sm:px-6 sm:py-10">
      <div className="max-w-3xl border-b border-border pb-8">
        <p className="eyebrow">Workspace tools</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          {meta.title}
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground sm:text-base">
          {meta.description}
        </p>
      </div>
      {children}
    </main>
  );
}
