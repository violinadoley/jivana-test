/** Hybrid workspace: discharge med rec + secondary tools (Option C). */

export const hybridWorkspaceTabs = [
  { id: "medrec", label: "Discharge med rec" },
  { id: "search", label: "Search" },
  { id: "copilot", label: "Copilot" },
  { id: "meetings", label: "Meetings" },
  { id: "research", label: "Research" },
  { id: "workflows", label: "Workflows" },
  { id: "insights", label: "Insights" },
] as const;

export type HybridWorkspaceTabId = (typeof hybridWorkspaceTabs)[number]["id"];

const hybridTabIdSet = new Set<string>(hybridWorkspaceTabs.map((t) => t.id));

export function parseHybridWorkspaceTab(
  value: string | null | undefined
): HybridWorkspaceTabId {
  if (value && hybridTabIdSet.has(value)) {
    return value as HybridWorkspaceTabId;
  }
  return "medrec";
}

export const hybridToolMeta: Record<
  Exclude<HybridWorkspaceTabId, "medrec">,
  { title: string; description: string }
> = {
  search: {
    title: "Policy & knowledge search",
    description:
      "Find SOPs, protocols, and playbooks from your institutional corpus—and Vertex AI Search when configured.",
  },
  copilot: {
    title: "Healthcare copilot",
    description:
      "Ask follow-up questions with session memory. Answers combine search hits and institutional knowledge.",
  },
  meetings: {
    title: "Meeting & handoff briefs",
    description:
      "Paste a stand-up, huddle, or handoff transcript. Get a summary, decisions, and owned action items.",
  },
  research: {
    title: "Research assistant",
    description:
      "Synthesize a question with cited sources from search and the knowledge corpus—useful for protocol updates.",
  },
  workflows: {
    title: "Workflow agent",
    description:
      "Describe an operational goal and get a step-by-step plan grounded in policies and search—with each step visible.",
  },
  insights: {
    title: "Productivity & activity",
    description:
      "See workspace activity and discharge med-rec counts for your team.",
  },
};
