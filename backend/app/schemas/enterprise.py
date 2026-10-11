from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    title: str
    snippet: str
    source: str
    uri: str | None = None
    score: float | None = None


class EnterpriseSearchResponse(BaseModel):
    success: bool = True
    query: str
    engine: str
    vertex_search_configured: bool
    results: list[SearchResultItem]


class MeetingIntelligenceRequest(BaseModel):
    transcript: str = Field(..., min_length=20, max_length=120000)
    title: str | None = Field(default=None, max_length=200)


class MeetingIntelligenceResponse(BaseModel):
    success: bool = True
    title: str
    analysis_markdown: str


class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=4000)


class ResearchResponse(BaseModel):
    success: bool = True
    question: str
    answer_markdown: str
    sources: list[SearchResultItem]


class WorkflowRunRequest(BaseModel):
    goal: str = Field(..., min_length=10, max_length=8000)


class WorkflowStep(BaseModel):
    step: int
    tool: str
    status: str
    output_preview: str


class WorkflowRunResponse(BaseModel):
    success: bool = True
    goal: str
    plan_markdown: str
    tools_used: list[str]
    steps: list[WorkflowStep] = Field(default_factory=list)


class ProductivityMetricsResponse(BaseModel):
    success: bool = True
    totals: dict[str, int]
    bigquery_configured: bool
    notes: str | None = None


class MedRecMetricsResponse(BaseModel):
    success: bool = True
    cases_awaiting_review: int = 0
    cases_legacy_bulk_acknowledged: int = 0
    cases_review_documented: int = 0
    open_items_total: int = 0
    items_awaiting_external_action: int = 0
