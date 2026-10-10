"use client";

import { useCallback, useState } from "react";

import { FileUpload } from "@/components/FileUpload";
import { MedReconciliationPanel } from "@/components/meddocs/MedReconciliationPanel";
import { ReviewQueuePanel } from "@/components/meddocs/ReviewQueuePanel";
import { DashboardWorkflowTracker } from "@/components/analytics/DashboardWorkflowTracker";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { WorkspaceToolFrame } from "@/components/dashboard/WorkspaceToolFrame";
import { CopilotPanel } from "@/components/workspace/CopilotPanel";
import { EnterpriseSearchPanel } from "@/components/workspace/EnterpriseSearchPanel";
import { MeetingIntelligencePanel } from "@/components/workspace/MeetingIntelligencePanel";
import { PlatformCapabilitiesPanel } from "@/components/workspace/PlatformCapabilitiesPanel";
import { ProductivityInsightsPanel } from "@/components/workspace/ProductivityInsightsPanel";
import { WorkspaceQuickStart } from "@/components/workspace/WorkspaceQuickStart";
import { ResearchPanel } from "@/components/workspace/ResearchPanel";
import { WorkflowAgentPanel } from "@/components/workspace/WorkflowAgentPanel";
import { MedRecWorkbench } from "@/components/medrec/MedRecWorkbench";
import { brand } from "@/lib/brand";
import { mvpWorkbenchEnabled } from "@/lib/mvp-workbench";
import {
  hybridWorkspaceTabs,
  parseHybridWorkspaceTab,
  type HybridWorkspaceTabId,
} from "@/lib/workspace-tabs";
import { cn } from "@/lib/utils";
import type { MedReconciliationJob } from "@/types/meddocs";

const legacyTabs = [
  { id: "overview", label: "Overview" },
  { id: "copilot", label: "Copilot" },
  { id: "search", label: "Search" },
  { id: "documents", label: "Documents" },
  { id: "meetings", label: "Meetings" },
  { id: "research", label: "Research" },
  { id: "workflows", label: "Workflows" },
  { id: "insights", label: "Insights" },
] as const;

type LegacyTabId = (typeof legacyTabs)[number]["id"];

function HybridToolPanels({ tab }: { tab: Exclude<HybridWorkspaceTabId, "medrec"> }) {
  switch (tab) {
    case "search":
      return <EnterpriseSearchPanel />;
    case "copilot":
      return <CopilotPanel />;
    case "meetings":
      return <MeetingIntelligencePanel />;
    case "research":
      return <ResearchPanel />;
    case "workflows":
      return <WorkflowAgentPanel />;
    case "insights":
      return (
        <div className="grid gap-8 lg:grid-cols-2">
          <ProductivityInsightsPanel medRecMode />
          <RecentActivity />
        </div>
      );
    default:
      return null;
  }
}

function readTabFromLocation(): HybridWorkspaceTabId {
  if (typeof window === "undefined") {
    return "medrec";
  }
  const hash = window.location.hash.replace(/^#/, "");
  const params = new URLSearchParams(window.location.search);
  const fromQuery = params.get("tab");
  const fromHash = hash || null;
  return parseHybridWorkspaceTab(fromQuery ?? fromHash);
}

function HybridWorkspaceShell() {
  const [tab, setTab] = useState<HybridWorkspaceTabId>(() => readTabFromLocation());

  const selectTab = useCallback((next: HybridWorkspaceTabId) => {
    setTab(next);
    if (typeof window === "undefined") {
      return;
    }
    const path = "/dashboard";
    if (next === "medrec") {
      window.history.replaceState(null, "", path);
    } else {
      window.history.replaceState(null, "", `${path}#${next}`);
    }
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <DashboardWorkflowTracker />
      <DashboardHeader />
      <div className="border-b border-border/80 bg-muted/20">
        <nav
          className="mx-auto flex max-w-6xl flex-wrap gap-2 px-4 py-3 sm:px-6"
          aria-label="Workspace"
        >
          {hybridWorkspaceTabs.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => selectTab(item.id)}
              className={cn(
                "rounded-full px-4 py-2 text-sm font-medium",
                tab === item.id
                  ? "bg-primary text-primary-foreground"
                  : "border border-border bg-background text-muted-foreground hover:text-foreground"
              )}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </div>
      {tab === "medrec" ? (
        <MedRecWorkbench />
      ) : (
        <WorkspaceToolFrame tab={tab}>
          <HybridToolPanels tab={tab} />
        </WorkspaceToolFrame>
      )}
    </div>
  );
}

function LegacyWorkspaceShell() {
  const [tab, setTab] = useState<LegacyTabId>("overview");
  const [queueVersion, setQueueVersion] = useState(0);
  const [focusedJob, setFocusedJob] = useState<MedReconciliationJob | null>(null);

  const onJobUpdated = useCallback(() => {
    setQueueVersion((v) => v + 1);
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <DashboardWorkflowTracker />
      <DashboardHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 space-y-8 px-4 py-8 sm:px-6 sm:py-10">
        <div className="max-w-3xl border-b border-border pb-8">
          <p className="eyebrow">{brand.track}</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
            Healthcare enterprise workspace
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground sm:text-base">
            {brand.description}
          </p>
        </div>

        <nav className="flex flex-wrap gap-2" aria-label="Workspace modules">
          {legacyTabs.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setTab(item.id)}
              className={cn(
                "rounded-full px-4 py-2 text-sm font-medium",
                tab === item.id
                  ? "bg-primary text-primary-foreground"
                  : "border border-border bg-background text-muted-foreground"
              )}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {tab === "overview" && (
          <div className="grid gap-8 lg:grid-cols-3">
            <div className="space-y-6 lg:col-span-2">
              <PlatformCapabilitiesPanel />
              <WorkspaceQuickStart onNavigate={(id) => setTab(id as LegacyTabId)} />
            </div>
            <RecentActivity />
          </div>
        )}

        {tab === "copilot" && <CopilotPanel />}

        {tab === "search" && <EnterpriseSearchPanel />}

        {tab === "documents" && (
          <div className="grid gap-8 lg:grid-cols-3">
            <div className="space-y-8 lg:col-span-2">
              <MedReconciliationPanel
                key={focusedJob?.job_id ?? "new"}
                initialJob={focusedJob}
                onJobChange={onJobUpdated}
              />
              <FileUpload />
            </div>
            <ReviewQueuePanel
              key={queueVersion}
              onSelectJob={(job) => {
                setFocusedJob(job);
              }}
            />
          </div>
        )}

        {tab === "meetings" && <MeetingIntelligencePanel />}

        {tab === "research" && <ResearchPanel />}

        {tab === "workflows" && <WorkflowAgentPanel />}

        {tab === "insights" && (
          <div className="grid gap-8 lg:grid-cols-2">
            <ProductivityInsightsPanel />
            <RecentActivity />
          </div>
        )}
      </main>
    </div>
  );
}

export function WorkspaceShell() {
  if (mvpWorkbenchEnabled) {
    return <HybridWorkspaceShell />;
  }
  return <LegacyWorkspaceShell />;
}
