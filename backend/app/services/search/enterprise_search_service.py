import logging
from typing import Any, Protocol

from app.core.config import Settings
from app.services.knowledge.institutional_knowledge import InstitutionalKnowledgeService

logger = logging.getLogger(__name__)


class SearchHit:
    def __init__(
        self,
        *,
        title: str,
        snippet: str,
        source: str,
        uri: str | None = None,
        score: float | None = None,
    ) -> None:
        self.title = title
        self.snippet = snippet
        self.source = source
        self.uri = uri
        self.score = score

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "snippet": self.snippet,
            "source": self.source,
            "uri": self.uri,
            "score": self.score,
        }


class VertexSearchClient(Protocol):
    def search(self, query: str, *, page_size: int) -> list[SearchHit]: ...


class EnterpriseSearchService:
    """Vertex AI Search when configured; institutional corpus always available."""

    def __init__(
        self,
        settings: Settings,
        vertex_client: VertexSearchClient | None = None,
        knowledge: InstitutionalKnowledgeService | None = None,
    ) -> None:
        self._settings = settings
        self._vertex = vertex_client
        self._knowledge = knowledge or InstitutionalKnowledgeService()

    def _vertex_client(self) -> VertexSearchClient | None:
        if self._vertex is not None:
            return self._vertex
        if not self._settings.vertex_search_configured:
            return None
        return _LiveVertexSearchClient(self._settings)

    def search(self, query: str, *, limit: int = 8) -> dict[str, Any]:
        hits: list[SearchHit] = []
        engine = "institutional_corpus"

        client = self._vertex_client()
        if client is not None:
            try:
                vertex_hits = client.search(query, page_size=limit)
                hits.extend(vertex_hits)
                engine = "vertex_ai_search"
            except Exception:
                logger.exception("Vertex AI Search failed; continuing with institutional corpus")

        for article in self._knowledge.retrieve(query, limit=min(limit, 5)):
            hits.append(
                SearchHit(
                    title=article["title"],
                    snippet=article["body"][:280],
                    source="institutional_corpus",
                    uri=f"knowledge://{article['id']}",
                )
            )

        deduped: list[dict[str, Any]] = []
        seen: set[str] = set()
        for hit in hits:
            key = f"{hit.title}:{hit.snippet[:40]}"
            if key in seen:
                continue
            seen.add(key)
            deduped.append(hit.as_dict())
            if len(deduped) >= limit:
                break

        return {
            "query": query,
            "engine": engine,
            "vertex_search_configured": self._settings.vertex_search_configured,
            "results": deduped,
        }


class _LiveVertexSearchClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def search(self, query: str, *, page_size: int) -> list[SearchHit]:
        from google.api_core.client_options import ClientOptions
        from google.cloud import discoveryengine_v1 as discoveryengine

        project = self._settings.effective_gcp_project_id
        location = self._settings.vertex_search_location
        store = (self._settings.vertex_search_data_store_id or "").strip()
        serving = self._settings.vertex_search_serving_config
        if not project or not store:
            return []

        api_endpoint = f"{location}-discoveryengine.googleapis.com"
        client = discoveryengine.SearchServiceClient(
            client_options=ClientOptions(api_endpoint=api_endpoint)
        )
        serving_config = (
            f"projects/{project}/locations/{location}/collections/default_collection/"
            f"dataStores/{store}/servingConfigs/{serving}"
        )
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=page_size,
        )
        response = client.search(request)
        hits: list[SearchHit] = []
        for result in response.results:
            doc = result.document
            struct = dict(doc.derived_struct_data) if doc.derived_struct_data else {}
            title = struct.get("title") or doc.id or "Result"
            snippets = struct.get("snippets")
            if isinstance(snippets, list) and snippets:
                first = snippets[0]
                snippet_text = str(getattr(first, "snippet", first) if first else "")
            else:
                snippet_text = str(struct.get("extractive_answers") or doc.content or "")[:280]
            score = None
            if result.rank_signals and hasattr(result.rank_signals, "score"):
                score = float(result.rank_signals.score)
            hits.append(
                SearchHit(
                    title=str(title),
                    snippet=str(snippet_text)[:280],
                    source="vertex_ai_search",
                    uri=str(doc.uri) if doc.uri else None,
                    score=score,
                )
            )
        return hits
