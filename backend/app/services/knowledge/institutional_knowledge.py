import json
import logging
import re
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "institutional_knowledge.json"


@lru_cache
def _load_articles() -> list[dict[str, str]]:
    try:
        raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    except OSError:
        logger.warning("Institutional knowledge file missing at %s", _DATA_PATH)
        return []
    if not isinstance(raw, list):
        return []
    articles: list[dict[str, str]] = []
    for row in raw:
        if not isinstance(row, dict):
            continue
        articles.append(
            {
                "id": str(row.get("id", "")),
                "title": str(row.get("title", "")),
                "tags": " ".join(row.get("tags") or []),
                "body": str(row.get("body", "")),
            }
        )
    return articles


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


class InstitutionalKnowledgeService:
    def retrieve(self, query: str, *, limit: int = 3) -> list[dict[str, str]]:
        tokens = _tokenize(query)
        if not tokens:
            return []
        scored: list[tuple[int, dict[str, str]]] = []
        for article in _load_articles():
            hay = f"{article['title']} {article['tags']} {article['body']}".lower()
            score = sum(1 for t in tokens if t in hay)
            if score > 0:
                scored.append((score, article))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [article for _, article in scored[:limit]]

    def format_context(self, query: str, *, limit: int = 3) -> str:
        chunks = self.retrieve(query, limit=limit)
        if not chunks:
            return ""
        parts = []
        for item in chunks:
            parts.append(f"### {item['title']}\n{item['body']}")
        return "\n\n".join(parts)
