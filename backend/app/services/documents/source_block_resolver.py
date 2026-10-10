from app.schemas.meddocs import (
    EvidenceStatus,
    ExtractedField,
    SourceBlock,
    SourceRef,
    ValidationFinding,
    VertexExtractOutput,
    VertexFieldOutput,
)
from app.services.documents.source_block_catalog import SourceBlockCatalog


class ResolveResult:
    def __init__(self) -> None:
        self.fields: list[ExtractedField] = []
        self.findings: list[ValidationFinding] = []
        self.weak_evidence_used: bool = False


def _block_to_ref(block: SourceBlock) -> SourceRef:
    if block.evidence_status == EvidenceStatus.VERIFIED:
        method = "document_ai"
    else:
        method = "vertex_structured"
    if block.evidence_status == EvidenceStatus.LOW:
        method = "document_ai"
    return SourceRef(
        document_id=block.document_id,
        page_number=block.page_number,
        source_text=_snippet(block.text),
        text_anchor=block.source_block_id,
        bounding_box=block.bounding_box,
        extraction_method=method,
        confidence=block.confidence,
        evidence_status=block.evidence_status,
    )


def _snippet(text: str, max_len: int = 120) -> str:
    t = text.strip().replace("\n", " ")
    return t if len(t) <= max_len else t[: max_len - 3] + "..."


def resolve_vertex_output(
    document_id: str,
    catalog: SourceBlockCatalog,
    output: VertexExtractOutput,
) -> ResolveResult:
    result = ResolveResult()
    doc_blocks = catalog.blocks_for_document(document_id)

    for raw_field in output.fields:
        resolved = _resolve_field(document_id, doc_blocks, catalog, raw_field)
        if resolved.field is not None:
            result.fields.append(resolved.field)
            if resolved.weak:
                result.weak_evidence_used = True
        result.findings.extend(resolved.findings)

    for med in output.medications:
        block_ids = med.get("source_block_ids") or []
        if not block_ids:
            result.findings.append(
                ValidationFinding(
                    code="UNSUPPORTED_EVIDENCE_REFERENCE",
                    message="Medication row missing source_block_ids.",
                    requires_review=True,
                )
            )
            continue
        refs = _resolve_block_ids(document_id, doc_blocks, catalog, block_ids)
        result.findings.extend(refs.findings)
        if refs.weak:
            result.weak_evidence_used = True
        if not refs.primary_block:
            continue
        # Medication lines built in pipeline from resolved refs

    return result


class _FieldResolve:
    def __init__(self) -> None:
        self.field: ExtractedField | None = None
        self.findings: list[ValidationFinding] = []
        self.weak: bool = False


class _BlockResolve:
    def __init__(self) -> None:
        self.primary_block: SourceBlock | None = None
        self.findings: list[ValidationFinding] = []
        self.weak: bool = False


def _resolve_field(
    document_id: str,
    doc_blocks: dict[str, SourceBlock],
    catalog: SourceBlockCatalog,
    raw: VertexFieldOutput,
) -> _FieldResolve:
    out = _FieldResolve()
    if not raw.source_block_ids:
        out.findings.append(
            ValidationFinding(
                code="UNSUPPORTED_EVIDENCE_REFERENCE",
                message=f"Field {raw.name} missing source_block_ids.",
                related_fields=[raw.name],
                requires_review=True,
            )
        )
        return out

    block_res = _resolve_block_ids(document_id, doc_blocks, catalog, raw.source_block_ids)
    out.findings.extend(block_res.findings)
    out.weak = block_res.weak
    if block_res.primary_block is None:
        return out

    ref = _block_to_ref(block_res.primary_block)
    out.field = ExtractedField(
        name=raw.name,
        value=raw.value,
        normalized_value=(raw.value or "").strip().lower() or None,
        source_ref=ref,
    )
    return out


def _resolve_block_ids(
    document_id: str,
    doc_blocks: dict[str, SourceBlock],
    catalog: SourceBlockCatalog,
    block_ids: list[str],
) -> _BlockResolve:
    out = _BlockResolve()
    primary: SourceBlock | None = None
    for bid in block_ids:
        block = doc_blocks.get(bid)
        if block is not None:
            primary = primary or block
            if block.evidence_status in (EvidenceStatus.VERTEX_ONLY, EvidenceStatus.LOW):
                out.weak = True
            continue
        # Cross-document check
        cross = _find_on_other_document(catalog, document_id, bid)
        if cross:
            out.findings.append(
                ValidationFinding(
                    code="CROSS_DOCUMENT_EVIDENCE_REFERENCE",
                    message=f"Block id {bid} belongs to another document.",
                    requires_review=True,
                )
            )
        else:
            out.findings.append(
                ValidationFinding(
                    code="UNSUPPORTED_EVIDENCE_REFERENCE",
                    message=f"Unknown source_block_id {bid}.",
                    requires_review=True,
                )
            )
    out.primary_block = primary
    return out


def _find_on_other_document(catalog: SourceBlockCatalog, document_id: str, block_id: str) -> bool:
    for did in catalog.document_ids():
        if did == document_id:
            continue
        if catalog.get_block(did, block_id):
            return True
    return False
