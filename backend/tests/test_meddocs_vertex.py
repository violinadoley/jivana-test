from app.schemas.meddocs import DocumentType
from app.services.documents.source_block_catalog import SourceBlockCatalog
from app.services.documents.source_block_resolver import resolve_vertex_output
from app.services.documents.vertex_gemini_service import _parse_vertex_json

from meddocs_helpers import verified_block


def test_gemini_output_ignored_without_block_ids() -> None:
    raw = """
    {
      "document_type": "prior_medication_record",
      "classification_confidence": 0.8,
      "fields": [{"name": "mrn", "value": "123"}],
      "medications": []
    }
    """
    parsed = _parse_vertex_json(raw)
    catalog = SourceBlockCatalog()
    catalog.add_block(verified_block("d1", "d1:p1:b1", "MRN 123"))
    result = resolve_vertex_output("d1", catalog, parsed)
    assert result.fields == []
    assert any(f.code == "UNSUPPORTED_EVIDENCE_REFERENCE" for f in result.findings)


def test_parse_vertex_json_document_type() -> None:
    parsed = _parse_vertex_json(
        '{"document_type":"discharge_summary","fields":[],"medications":[]}'
    )
    assert parsed.document_type == DocumentType.DISCHARGE_SUMMARY
