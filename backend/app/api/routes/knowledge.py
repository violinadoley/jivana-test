from typing import Annotated

from app.services.knowledge.institutional_knowledge import InstitutionalKnowledgeService
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class KnowledgeArticle(BaseModel):
    id: str
    title: str
    body: str


class KnowledgeSearchResponse(BaseModel):
    success: bool = True
    items: list[KnowledgeArticle] = Field(default_factory=list)


@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    q: Annotated[str, Query(min_length=1, max_length=500)],
    limit: Annotated[int, Query(ge=1, le=10)] = 5,
) -> KnowledgeSearchResponse:
    service = InstitutionalKnowledgeService()
    rows = service.retrieve(q, limit=limit)
    return KnowledgeSearchResponse(
        items=[KnowledgeArticle(id=row["id"], title=row["title"], body=row["body"]) for row in rows]
    )
