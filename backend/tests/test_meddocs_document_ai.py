from app.core.config import Settings
from app.core.exceptions import DocumentAIConfigurationError
from app.services.documents.document_ai_service import DocumentAIService

from meddocs_helpers import FakeDocumentAIClient


def test_docai_unset_uses_vertex_only_path() -> None:
    settings = Settings(DOCUMENT_AI_PROCESSOR_ID="")
    svc = DocumentAIService(settings)
    assert not svc.is_configured
    svc.verify_processor_if_configured()
    blocks = svc.process_to_blocks("d1", b"hello", "text/plain")
    assert blocks == []


def test_docai_invalid_processor_fails_fast() -> None:
    settings = Settings(DOCUMENT_AI_PROCESSOR_ID="bad-processor", GCP_PROJECT_ID="test-proj")
    fake = FakeDocumentAIClient(fail_verify=True)
    svc = DocumentAIService(settings, client=fake)
    try:
        svc.verify_processor_if_configured()
        raise AssertionError("expected error")
    except DocumentAIConfigurationError as exc:
        assert exc.code == "DOCUMENT_AI_MISCONFIGURED"


def test_docai_verify_processor_called_when_configured() -> None:
    settings = Settings(DOCUMENT_AI_PROCESSOR_ID="proc-1", GCP_PROJECT_ID="test-proj")
    fake = FakeDocumentAIClient()
    svc = DocumentAIService(settings, client=fake)
    svc.verify_processor_if_configured()
    assert fake.verify_called is True
