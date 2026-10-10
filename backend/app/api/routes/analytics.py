from typing import Annotated

from app.core.config import Settings, get_settings
from app.core.deps import get_activity_service, get_document_store, require_user
from app.schemas.enterprise import MedRecMetricsResponse, ProductivityMetricsResponse
from app.services.documents.document_store import DocumentStore
from app.services.documents.medrec_metrics import compute_medrec_metrics
from app.services.firebase.activity_service import ActivityService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/productivity", response_model=ProductivityMetricsResponse)
async def productivity_metrics(
    activity: Annotated[ActivityService, Depends(get_activity_service)],
    user: Annotated[dict | None, Depends(require_user)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ProductivityMetricsResponse:
    uid = str(user["uid"]) if user and user.get("uid") else None
    rows = activity.list_recent(user_id=uid, limit=100)
    totals: dict[str, int] = {}
    for row in rows:
        kind = str(row.get("type") or "other")
        totals[kind] = totals.get(kind, 0) + 1

    notes = None
    if settings.bigquery_analytics_configured:
        notes = "Events also stream to BigQuery for enterprise analytics."
    elif settings.vertex_search_configured:
        notes = "Connect BigQuery dataset for cross-team productivity dashboards."

    return ProductivityMetricsResponse(
        totals=totals,
        bigquery_configured=settings.bigquery_analytics_configured,
        notes=notes,
    )


@router.get("/medrec", response_model=MedRecMetricsResponse)
async def medrec_metrics(
    store: Annotated[DocumentStore, Depends(get_document_store)],
    user: Annotated[dict | None, Depends(require_user)],
) -> MedRecMetricsResponse:
    uid = str(user["uid"]) if user and user.get("uid") else None
    data = compute_medrec_metrics(store, uid)
    return MedRecMetricsResponse(
        cases_awaiting_review=data["cases_awaiting_review"],
        cases_legacy_bulk_acknowledged=data["cases_legacy_bulk_acknowledged"],
        cases_review_documented=data["cases_review_documented"],
        open_items_total=data["open_items_total"],
        items_awaiting_external_action=data["items_awaiting_external_action"],
    )
