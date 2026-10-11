import asyncio
import logging
from typing import Annotated

from app.ai.adk.dispatch import run_workflow_agent_dispatch
from app.ai.base import AIService
from app.core.config import get_settings
from app.core.deps import get_activity_service, get_gemini_service, require_user
from app.core.exceptions import AIGenerationError
from app.schemas.enterprise import WorkflowRunRequest, WorkflowRunResponse
from app.services.analytics.bigquery_productivity import BigQueryProductivityService
from app.services.firebase.activity_service import ActivityService
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])

TIMEOUT = 90.0


@router.post("/agent-run", response_model=WorkflowRunResponse)
async def run_agent_workflow(
    body: WorkflowRunRequest,
    ai: Annotated[AIService, Depends(get_gemini_service)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
) -> WorkflowRunResponse:
    """Multi-step workflow: institutional knowledge, enterprise search, then AI plan."""
    settings = get_settings()
    try:
        steps, plan, tools_used = await asyncio.wait_for(
            run_workflow_agent_dispatch(settings, ai, body.goal),
            timeout=TIMEOUT,
        )
    except TimeoutError as exc:
        raise AIGenerationError("Workflow agent timed out.") from exc

    uid = str(user["uid"]) if user and user.get("uid") else None
    activity.log_workflow_agent(user_id=uid, goal=body.goal)
    BigQueryProductivityService(settings).record_event(
        event_type="workflow_agent_run",
        user_id=uid,
        metadata={"goal_length": len(body.goal), "steps": len(steps)},
    )
    return WorkflowRunResponse(
        goal=body.goal,
        plan_markdown=plan,
        tools_used=tools_used,
        steps=steps,
    )
