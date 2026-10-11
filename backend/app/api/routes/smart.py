"""SMART on FHIR launch helpers (EHR embed Phase 2 — configure OAuth client in production)."""

from typing import Annotated, Any

from app.core.config import Settings, get_settings
from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/smart", tags=["smart"])


@router.get("/configuration")
def smart_configuration(
    settings: Annotated[Settings, Depends(get_settings)],
    iss: Annotated[str | None, Query(description="FHIR base URL from EHR launch")] = None,
) -> dict[str, Any]:
    """Minimal SMART configuration for sandbox / demo EHR integration."""
    api_base = (settings.smart_app_launch_url or "").strip().rstrip("/")
    if not api_base:
        api_base = "https://YOUR_HOSTING_URL/smart/launch"

    fhir_iss = iss or settings.smart_fhir_iss or "https://healthcare.googleapis.com/v1/PLACEHOLDER"

    return {
        "issuer": fhir_iss,
        "jwks_uri": None,
        "authorization_endpoint": f"{api_base}?step=authorize",
        "token_endpoint": f"{api_base}?step=token",
        "grant_types_supported": ["authorization_code"],
        "response_types_supported": ["code"],
        "scopes_supported": ["launch", "openid", "fhirUser", "patient/*.read"],
        "capabilities": ["launch-ehr", "client-public"],
        "smart_app_status": "demo_stub",
        "documentation": "docs/setup/smart-on-fhir.md",
        "project_configured": bool(settings.smart_client_id),
    }


@router.get("/launch")
def smart_launch_redirect(
    settings: Annotated[Settings, Depends(get_settings)],
    iss: Annotated[str | None, Query()] = None,
    launch: Annotated[str | None, Query()] = None,
) -> RedirectResponse:
    """Redirect EHR SMART launch to the hosted workspace (Firebase Hosting)."""
    from urllib.parse import urlencode

    base = (settings.smart_app_launch_url or "").strip().rstrip("/")
    if not base:
        base = "https://YOUR_PROJECT.web.app/smart/launch"
    params = {k: v for k, v in {"iss": iss, "launch": launch}.items() if v}
    target = base if not params else f"{base}?{urlencode(params)}"
    return RedirectResponse(url=target, status_code=302)
