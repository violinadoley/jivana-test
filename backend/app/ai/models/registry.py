from dataclasses import dataclass

from app.core.config import Settings

# Bump when prompt files change materially.
DEFAULT_PROMPT_VERSION = "v1"
DEFAULT_RETRIEVAL_VERSION = "none"


@dataclass(frozen=True)
class AIExecutionContext:
    model_id: str
    model_version: str
    prompt_version: str
    retrieval_version: str

    @classmethod
    def from_settings(cls, settings: Settings) -> "AIExecutionContext":
        return cls(
            model_id=settings.gemini_model,
            model_version=settings.gemini_model,
            prompt_version=settings.ai_prompt_version,
            retrieval_version=DEFAULT_RETRIEVAL_VERSION,
        )
