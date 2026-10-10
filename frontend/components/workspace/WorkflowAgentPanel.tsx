"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ACTIVITY_UPDATED_EVENT } from "@/lib/activity-events";
import { runWorkflowAgent } from "@/lib/api";
import { labelWorkflowTool } from "@/lib/workflow-tool-labels";
import type { WorkflowStep } from "@/types/enterprise";

export function WorkflowAgentPanel() {
  const [goal, setGoal] = useState(
    "Automate discharge medication reconciliation checklist for nursing and pharmacy with human sign-off gates."
  );
  const [plan, setPlan] = useState<string | null>(null);
  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  const [tools, setTools] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    try {
      const out = await runWorkflowAgent(goal);
      setPlan(out.plan_markdown);
      setTools(out.tools_used);
      setSteps(out.steps ?? []);
      window.dispatchEvent(new Event(ACTIVITY_UPDATED_EVENT));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Workflow agent</CardTitle>
        <CardDescription>
          Describe an operational goal. JIVANA pulls relevant policies and search results, then
          drafts a step-by-step plan. Each step is shown below before you use the plan clinically.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Textarea rows={4} value={goal} onChange={(e) => setGoal(e.target.value)} />
        <Button onClick={() => void run()} disabled={loading}>
          {loading ? "Building plan…" : "Generate workflow plan"}
        </Button>
        {steps.length > 0 && (
          <ol className="space-y-2 text-sm">
            {steps.map((s) => (
              <li key={s.step} className="border border-border p-3">
                <p className="font-medium">
                  Step {s.step}: {labelWorkflowTool(s.tool)}{" "}
                  <span className="text-xs text-muted-foreground">({s.status})</span>
                </p>
                <p className="mt-1 text-muted-foreground">{s.output_preview}</p>
              </li>
            ))}
          </ol>
        )}
        {tools.length > 0 && (
          <p className="text-xs text-muted-foreground">
            Sources used: {tools.map(labelWorkflowTool).join(" · ")}
          </p>
        )}
        {plan && (
          <pre className="whitespace-pre-wrap rounded-md border p-4 text-sm">{plan}</pre>
        )}
      </CardContent>
    </Card>
  );
}
