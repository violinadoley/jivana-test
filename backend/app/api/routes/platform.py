import logging
from typing import Annotated, Any

from app.ai.adk.availability import adk_importable, resolve_agent_backend
from app.core.config import Settings, get_settings
from app.schemas.platform import CapabilityStatus, PlatformCapabilitiesResponse
from app.services.knowledge.institutional_knowledge import InstitutionalKnowledgeService
from app.services.search.enterprise_search_service import EnterpriseSearchService
from fastapi import APIRouter, Depends, Query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/platform", tags=["platform"])


def _demo_check_items(settings: Settings) -> list[dict[str, Any]]:
    gemini_ok = bool((settings.gemini_api_key or "").strip()) or bool(
        settings.effective_gcp_project_id
        and settings.environment.lower() in ("cloud", "production")
    )
    adk_ok = adk_importable() and resolve_agent_backend(settings) == "adk"

    return [
        {
            "id": "gemini",
            "label": "Gemini (API key or Vertex on Cloud Run)",
            "required_for_core_demo": True,
            "ok": gemini_ok,
            "configured": gemini_ok,
        },
        {
            "id": "institutional_corpus",
            "label": "Institutional knowledge corpus",
            "required_for_core_demo": True,
            "ok": True,
            "configured": True,
        },
        {
            "id": "google_adk",
            "label": "Google ADK agents",
            "required_for_core_demo": False,
            "ok": adk_ok,
            "configured": adk_ok,
        },
        {
            "id": "vertex_search",
            "label": "Vertex AI Search",
            "required_for_core_demo": False,
            "ok": settings.vertex_search_configured,
            "configured": settings.vertex_search_configured,
        },
        {
            "id": "document_ai",
            "label": "Document AI",
            "required_for_core_demo": False,
            "ok": settings.document_ai_configured,
            "configured": settings.document_ai_configured,
        },
        {
            "id": "firestore",
            "label": "Firestore",
            "required_for_core_demo": False,
            "ok": settings.firebase_configured,
            "configured": settings.firebase_configured,
        },
        {
            "id": "bigquery",
            "label": "BigQuery productivity events",
            "required_for_core_demo": False,
            "ok": settings.bigquery_analytics_configured,
            "configured": settings.bigquery_analytics_configured,
        },
        {
            "id": "healthcare_fhir",
            "label": "Cloud Healthcare API (FHIR export)",
            "required_for_core_demo": False,
            "ok": settings.healthcare_fhir_configured,
            "configured": settings.healthcare_fhir_configured,
        },
        {
            "id": "cloud_storage",
            "label": "Cloud Storage uploads bucket",
            "required_for_core_demo": False,
            "ok": bool(settings.firebase_storage_bucket),
            "configured": bool(settings.firebase_storage_bucket),
        },
    ]


def _merge_live_probe(items: list[dict[str, Any]], item_id: str, live_ok: bool) -> None:
    for item in items:
        if item["id"] == item_id:
            item["live_probe_ok"] = live_ok
            if item.get("configured", True):
                item["ok"] = live_ok


@router.get("/capabilities", response_model=PlatformCapabilitiesResponse)
def platform_capabilities(
    settings: Settings = Depends(get_settings),
) -> PlatformCapabilitiesResponse:
    caps = [
        CapabilityStatus(
            id="vertex_gemini",
            label="Gemini on Vertex AI",
            configured=(
                settings.environment.lower() in ("cloud", "production")
                and bool(settings.effective_gcp_project_id)
            )
            or bool((settings.gemini_api_key or "").strip()),
            description="Text generation for copilot, meetings, research, workflows, med extract.",
        ),
        CapabilityStatus(
            id="vertex_search",
            label="Vertex AI Search",
            configured=settings.vertex_search_configured,
            description="Discovery Engine data store for enterprise retrieval.",
        ),
        CapabilityStatus(
            id="document_ai",
            label="Document AI",
            configured=settings.document_ai_configured,
            description="OCR and layout blocks for document intelligence.",
        ),
        CapabilityStatus(
            id="firestore",
            label="Firestore",
            configured=settings.firebase_configured,
            description="Activity, copilot sessions, reconciliation jobs.",
        ),
        CapabilityStatus(
            id="healthcare_fhir",
            label="Cloud Healthcare API (FHIR)",
            configured=settings.healthcare_fhir_configured,
            description="Export reviewed med rec as FHIR Bundle.",
        ),
        CapabilityStatus(
            id="bigquery",
            label="BigQuery analytics",
            configured=settings.bigquery_analytics_configured,
            description="Productivity event stream for enterprise reporting.",
        ),
        CapabilityStatus(
            id="cloud_storage",
            label="Cloud Storage",
            configured=bool(settings.firebase_storage_bucket),
            description="Uploaded document blobs via API.",
        ),
        CapabilityStatus(
            id="google_adk",
            label="Google ADK agents",
            configured=adk_importable() and resolve_agent_backend(settings) == "adk",
            description="Copilot, research, meetings, and workflow planning when ADK is active.",
        ),
    ]
    return PlatformCapabilitiesResponse(
        environment=settings.environment,
        capabilities=caps,
    )


@router.get("/demo-readiness")
def demo_readiness(
    settings: Annotated[Settings, Depends(get_settings)],
    probe: Annotated[bool, Query(description="Run lightweight live search probes")] = False,
) -> dict[str, Any]:
    items = _demo_check_items(settings)

    if probe:
        try:
            hits = InstitutionalKnowledgeService().retrieve("medication reconciliation", limit=1)
            _merge_live_probe(items, "institutional_corpus", len(hits) >= 1)
        except Exception:
            logger.exception("Institutional corpus probe failed")
            _merge_live_probe(items, "institutional_corpus", False)

        try:
            payload = EnterpriseSearchService(settings).search("medication policy", limit=1)
            _merge_live_probe(items, "vertex_search", "results" in payload)
        except Exception:
            logger.exception("Search probe failed")
            _merge_live_probe(items, "vertex_search", False)

    required = [i for i in items if i["required_for_core_demo"]]
    optional = [i for i in items if not i["required_for_core_demo"]]

    return {
        "environment": settings.environment,
        "agent_backend": resolve_agent_backend(settings),
        "core_demo_ready": all(i["ok"] for i in required),
        "all_integrations_green": all(i["ok"] for i in items),
        "required": required,
        "optional": optional,
        "gcp_console_checklist": "docs/setup/verify-integrations.md",
    }
