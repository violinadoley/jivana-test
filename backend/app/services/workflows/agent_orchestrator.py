from app.ai.adk.knowledge_tools import build_workflow_context
from app.ai.base import AIService
from app.core.config import Settings
from app.schemas.enterprise import WorkflowStep


def run_workflow_agent(
    settings: Settings,
    ai: AIService,
    goal: str,
) -> tuple[list[WorkflowStep], str, list[str]]:
    steps, knowledge_text, search_text, tools_used = build_workflow_context(settings, goal)

    plan = ai.generate_from_template(
        settings.ai_prompt_version,
        "workflow_agent",
        goal=goal,
        knowledge=knowledge_text or "None.",
        search=search_text,
    )
    tools_used.append("vertex_gemini")
    steps.append(
        WorkflowStep(
            step=3,
            tool="vertex_gemini",
            status="completed",
            output_preview=_preview(plan),
        )
    )

    return steps, plan, tools_used


def _preview(text: str, limit: int = 220) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return f"{cleaned[: limit - 1]}…"
