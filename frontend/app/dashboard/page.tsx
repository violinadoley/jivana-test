import { DashboardAuthGate } from "@/components/dashboard/DashboardAuthGate";
import { WorkspaceShell } from "@/components/dashboard/WorkspaceShell";

export default function DashboardPage() {
  return (
    <DashboardAuthGate>
      <WorkspaceShell />
    </DashboardAuthGate>
  );
}
