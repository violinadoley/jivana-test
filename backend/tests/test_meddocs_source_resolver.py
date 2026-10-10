from app.schemas.meddocs import EvidenceStatus, VertexExtractOutput, VertexFieldOutput
from app.services.documents.source_block_catalog import SourceBlockCatalog
from app.services.documents.source_block_resolver import resolve_vertex_output

from meddocs_helpers import verified_block


def test_resolver_maps_valid_block_ids_to_catalog() -> None:
    doc_a = "docA"
    catalog = SourceBlockCatalog()
    block = verified_block(doc_a, f"{doc_a}:p1:b1", "MRN: 999")
    catalog.add_block(block)
    output = VertexExtractOutput(
        fields=[
            VertexFieldOutput(name="mrn", value="999", source_block_ids=[block.source_block_id])
        ]
    )
    result = resolve_vertex_output(doc_a, catalog, output)
    assert len(result.fields) == 1
    ref = result.fields[0].source_ref
    assert ref.source_text == "MRN: 999"
    assert ref.page_number == 1
    assert ref.evidence_status == EvidenceStatus.VERIFIED


def test_unknown_block_id_rejects_field_and_needs_review() -> None:
    doc_a = "docA"
    catalog = SourceBlockCatalog()
    output = VertexExtractOutput(
        fields=[VertexFieldOutput(name="mrn", value="1", source_block_ids=["missing-id"])]
    )
    result = resolve_vertex_output(doc_a, catalog, output)
    assert result.fields == []
    assert any(f.code == "UNSUPPORTED_EVIDENCE_REFERENCE" for f in result.findings)


def test_reject_cross_document_source_block_id() -> None:
    doc_a, doc_b = "docA", "docB"
    catalog = SourceBlockCatalog()
    b_block = verified_block(doc_b, f"{doc_b}:p1:b1", "other doc text")
    catalog.add_block(b_block)
    output = VertexExtractOutput(
        fields=[
            VertexFieldOutput(name="mrn", value="x", source_block_ids=[b_block.source_block_id])
        ]
    )
    result = resolve_vertex_output(doc_a, catalog, output)
    assert result.fields == []
    assert any(f.code == "CROSS_DOCUMENT_EVIDENCE_REFERENCE" for f in result.findings)


def test_resolver_scopes_catalog_to_document() -> None:
    doc_a, doc_b = "docA", "docB"
    shared_id = "same-id-string"
    catalog = SourceBlockCatalog()
    catalog.add_block(verified_block(doc_a, shared_id, "text A"))
    catalog.add_block(verified_block(doc_b, shared_id, "text B"))
    assert catalog.get_block(doc_a, shared_id).text == "text A"
    assert catalog.get_block(doc_b, shared_id).text == "text B"
    result = resolve_vertex_output(
        doc_a,
        catalog,
        VertexExtractOutput(
            fields=[VertexFieldOutput(name="mrn", value="1", source_block_ids=[shared_id])]
        ),
    )
    assert result.fields[0].source_ref.source_text == "text A"
