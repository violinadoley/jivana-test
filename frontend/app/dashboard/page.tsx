import { AIInteraction } from "@/components/AIInteraction";
import { FileUpload } from "@/components/FileUpload";
import { MedReconciliationPanel } from "@/components/meddocs/MedReconciliationPanel";
import { ReviewQueuePanel } from "@/components/meddocs/ReviewQueuePanel";
import { DashboardWorkflowTracker } from "@/components/analytics/DashboardWorkflowTracker";
import { DashboardAuthGate } from "@/components/dashboard/DashboardAuthGate";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { RecentActivity } from "@/components/dashboard/RecentActivity";

export default function DashboardPage() {
  return (
    <DashboardAuthGate>
    <div className="min-h-screen flex flex-col bg-background">
      <DashboardWorkflowTracker />
      <DashboardHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 space-y-8 px-4 py-8 sm:px-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            MedDocs Module 1 — synthetic medication reconciliation prototype
            plus generic AI utilities.
          </p>
        </div>
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-8">
            <MedReconciliationPanel />
            <AIInteraction />
            <FileUpload />
          </div>
          <div className="space-y-8">
            <ReviewQueuePanel />
            <RecentActivity />
          </div>
        </div>
      </main>
    </div>
    </DashboardAuthGate>
  );
}
