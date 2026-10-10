from abc import ABC, abstractmethod
from typing import Any, TypeVar

T = TypeVar("T")


class AIService(ABC):
    """Abstraction for Gemini and future model providers."""

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate plain text from a user prompt."""

    def generate_structured_output(self, prompt: str, schema: type[T]) -> T:
        raise NotImplementedError("Structured output not implemented yet.")

    def analyze_image(self, prompt: str, image_bytes: bytes, mime_type: str) -> str:
        raise NotImplementedError("Multimodal analysis not implemented yet.")

    def generate_with_context(self, messages: list[dict[str, Any]]) -> str:
        raise NotImplementedError("RAG/context chat not implemented yet.")

    def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError("Embeddings not implemented yet.")
