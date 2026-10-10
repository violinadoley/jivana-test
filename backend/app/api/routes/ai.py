import asyncio
import logging
from typing import Annotated

from app.core.deps import get_activity_service, get_gemini_service, require_user
from app.core.exceptions import AIGenerationError
from app.schemas.ai import GenerateRequest, GenerateResponse
from app.services.ai.base import AIService
from app.services.firebase.activity_service import ActivityService
from fastapi import APIRouter, Depends

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])

AI_GENERATE_TIMEOUT_SECONDS = 60.0


@router.post("/generate", response_model=GenerateResponse)
async def generate_text(
    body: GenerateRequest,
    ai: Annotated[AIService, Depends(get_gemini_service)],
    user: Annotated[dict | None, Depends(require_user)],
    activity: Annotated[ActivityService, Depends(get_activity_service)],
) -> GenerateResponse:
    try:
        text = await asyncio.wait_for(
            asyncio.to_thread(ai.generate_text, body.message),
            timeout=AI_GENERATE_TIMEOUT_SECONDS,
        )
    except TimeoutError as exc:
        raise AIGenerationError("Request timed out.") from exc
    except AIGenerationError:
        raise
    except Exception as exc:
        logger.exception("AI generation failed")
        raise AIGenerationError() from exc
    uid = str(user["uid"]) if user and user.get("uid") else None
    activity.log_ai_generate(
        user_id=uid,
        message=body.message,
        response_preview=text,
    )
    return GenerateResponse(success=True, response=text)
