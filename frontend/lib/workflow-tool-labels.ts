/** Human labels for workflow agent step tools (API ids stay technical). */

const LABELS: Record<string, string> = {
  institutional_knowledge: "Internal knowledge library",
  enterprise_search: "Policy & document search",
  vertex_ai_search: "Managed search index",
  vertex_gemini: "AI plan synthesis",
  google_adk: "Google ADK agent runtime",
};

export function labelWorkflowTool(tool: string): string {
  return LABELS[tool] ?? tool.replaceAll("_", " ");
}
