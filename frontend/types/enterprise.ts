export type SearchResultItem = {
  title: string;
  snippet: string;
  source: string;
  uri?: string | null;
  score?: number | null;
};

export type EnterpriseSearchResponse = {
  query: string;
  engine: string;
  vertex_search_configured: boolean;
  results: SearchResultItem[];
};

export type CopilotMessage = {
  role: string;
  content: string;
};

export type CopilotChatResponse = {
  session_id: string;
  response: string;
  messages: CopilotMessage[];
};

export type ProductivityMetrics = {
  totals: Record<string, number>;
  bigquery_configured: boolean;
  notes?: string | null;
};

export type MedRecMetrics = {
  cases_awaiting_review: number;
  cases_legacy_bulk_acknowledged: number;
  cases_review_documented: number;
  open_items_total: number;
  items_awaiting_external_action: number;
};

export type PlatformCapability = {
  id: string;
  label: string;
  configured: boolean;
  description: string;
};

export type PlatformCapabilities = {
  environment: string;
  capabilities: PlatformCapability[];
};

export type WorkflowStep = {
  step: number;
  tool: string;
  status: string;
  output_preview: string;
};
