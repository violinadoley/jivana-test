from __future__ import annotations

from app.core.config import Settings
from app.schemas.enterprise import WorkflowStep
from app.services.knowledge.institutional_knowledge import InstitutionalKnowledgeService
from app.services.search.enterprise_search_service import EnterpriseSearchService


def _preview(text: str, limit: int = 220) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 1]}…"


def retrieve_institutional_knowledge(query: str) -> str:
    """ADK tool: fetch institutional policy excerpts for a query."""
    svc = InstitutionalKnowledgeService()
    return svc.format_context(query, limit=4) or "No institutional matches."


def enterprise_search(query: str) -> str:
    """ADK tool: search policies and corpus for a query."""
    from app.ai.adk.session_context import current_settings

    settings = current_settings()
    payload = EnterpriseSearchService(settings).search(query, limit=6)
    engine = str(payload.get("engine", "search"))
    lines = [f"- {r['title']}: {r['snippet']}" for r in payload.get("results", [])[:6]]
    body = "\n".join(lines) if lines else "No search hits."
    return f"engine={engine}\n{body}"


def build_workflow_context(
    settings: Settings,
    goal: str,
) -> tuple[list[WorkflowStep], str, str, list[str]]:
    """Deterministic knowledge + search steps (shared by legacy and ADK paths)."""
    tools_used: list[str] = []
    steps: list[WorkflowStep] = []

    knowledge_svc = InstitutionalKnowledgeService()
    articles = knowledge_svc.retrieve(goal, limit=4)
    knowledge_text = knowledge_svc.format_context(goal, limit=4)
    tools_used.append("institutional_knowledge")
    steps.append(
        WorkflowStep(
            step=1,
            tool="institutional_knowledge",
            status="completed",
            output_preview=_preview(knowledge_text or f"{len(articles)} articles matched"),
        )
    )

    search_svc = EnterpriseSearchService(settings)
    search_payload = search_svc.search(goal, limit=6)
    engine = str(search_payload.get("engine", "search"))
    if settings.vertex_search_configured:
        tools_used.insert(0, "vertex_ai_search")
    tools_used.append("enterprise_search")
    search_text = (
        "\n".join(f"- {r['title']}: {r['snippet']}" for r in search_payload.get("results", []))
        or "No search hits."
    )
    steps.append(
        WorkflowStep(
            step=2,
            tool="enterprise_search",
            status="completed",
            output_preview=_preview(f"engine={engine}; {search_text}"),
        )
    )

    return steps, knowledge_text or "", search_text, tools_used
