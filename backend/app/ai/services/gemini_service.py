import logging
from typing import Any

from app.ai.base import AIService
from app.ai.models.registry import AIExecutionContext
from app.ai.prompts.loader import render_generate_text_prompt
from app.core.config import Settings
from app.core.exceptions import AIGenerationError
from google import genai
from google.genai import errors as genai_errors

logger = logging.getLogger(__name__)


class GeminiService(AIService):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: genai.Client | None = None

    @property
    def execution_context(self) -> AIExecutionContext:
        return AIExecutionContext.from_settings(self._settings)

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            if not self._settings.gemini_api_key:
                raise AIGenerationError("Gemini API key is not configured. Set GEMINI_API_KEY.")
            self._client = genai.Client(api_key=self._settings.gemini_api_key)
        return self._client

    def generate_text(self, prompt: str) -> str:
        ctx = self.execution_context
        composed = render_generate_text_prompt(prompt, version=self._settings.ai_prompt_version)
        logger.info(
            "AI generate_text",
            extra={
                "model_id": ctx.model_id,
                "prompt_version": ctx.prompt_version,
                "retrieval_version": ctx.retrieval_version,
            },
        )
        try:
            response = self.client.models.generate_content(
                model=self._settings.gemini_model,
                contents=composed,
            )
        except genai_errors.ClientError as exc:
            logger.exception("Gemini client error")
            raise AIGenerationError("Unable to generate a response.") from exc
        except Exception as exc:
            logger.exception("Unexpected Gemini error")
            raise AIGenerationError("Unable to generate a response.") from exc

        text = getattr(response, "text", None)
        if not text:
            raise AIGenerationError("Model returned an empty response.")
        return str(text).strip()

    def generate_structured_output(self, prompt: str, schema: type[Any]) -> Any:
        raise NotImplementedError("Use response_schema in GenerateContentConfig when implementing.")

    def analyze_image(self, prompt: str, image_bytes: bytes, mime_type: str) -> str:
        raise NotImplementedError("Pass image parts to generate_content when implementing.")

    def generate_with_context(self, messages: list[dict[str, Any]]) -> str:
        raise NotImplementedError(
            "Build a contents array from messages when implementing RAG/chat."
        )
