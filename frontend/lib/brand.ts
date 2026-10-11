export const brand = {
  name: "JIVANA",
  tagline:
    "Healthcare knowledge and document work—with discharge med rec you can sign off on.",
  description:
    "One workspace to search policies, brief meetings, and run document workflows with human review. Discharge medication reconciliation is the flagship flow: compare lists, resolve each item, and sign off.",
  medRecLead:
    "Compare home, hospital, and discharge medication lists. Resolve each difference, document your decision, and sign off before export.",
  track: "Healthcare operations · Future of Work",
  problem:
    "Knowledge lives in PDFs, meetings, and policies while high-risk work—like discharge med rec—needs citations and a named reviewer. Teams lose time switching tools and risk when changes are missed.",
} as const;

/** Home + quick-start: flagship med rec first, then platform tools. */
export const solutionPillars = [
  {
    title: "Discharge med rec",
    description:
      "Upload prior home meds, discharge summary, and Rx lists. Review each line with source snippets, then finalize with an audit-ready summary.",
  },
  {
    title: "Policy & knowledge search",
    description:
      "One search bar for internal SOPs and playbooks—Vertex AI Search plus your institutional corpus.",
  },
  {
    title: "Healthcare copilot",
    description:
      "Multi-turn Q&A with session memory, grounded in search and institutional knowledge.",
  },
  {
    title: "Meeting & handoff briefs",
    description:
      "Paste a transcript from stand-up or handoff—get summary, decisions, and action items.",
  },
  {
    title: "Cited research",
    description:
      "Synthesize clinical or operational questions with visible sources.",
  },
  {
    title: "Workflow agent",
    description:
      "Multi-step plans with visible tool use—retrieve, search, then recommend next actions.",
  },
] as const;

export const stackLabels = [
  "Gemini on Vertex AI",
  "Vertex AI Search",
  "Document AI",
  "Cloud Healthcare API",
  "Cloud Run",
  "Firestore",
  "BigQuery",
  "Cloud Storage",
  "Next.js",
] as const;
