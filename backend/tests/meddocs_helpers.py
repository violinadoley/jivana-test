from app.schemas.meddocs import (
    DocumentType,
    EvidenceStatus,
    SourceBlock,
    VertexExtractOutput,
    VertexFieldOutput,
)


def verified_block(document_id: str, block_id: str, text: str, page: int = 1) -> SourceBlock:
    return SourceBlock(
        source_block_id=block_id,
        document_id=document_id,
        page_number=page,
        text=text,
        confidence=0.95,
        evidence_status=EvidenceStatus.VERIFIED,
    )


def vertex_only_block(document_id: str, block_id: str, text: str, page: int = 1) -> SourceBlock:
    return SourceBlock(
        source_block_id=block_id,
        document_id=document_id,
        page_number=page,
        text=text,
        evidence_status=EvidenceStatus.VERTEX_ONLY,
    )


class FakeVertexMeddocsClient:
    """Deterministic Vertex mock keyed by filename hints."""

    def __init__(
        self,
        *,
        med_name: str = "lisinopril",
        discharge_dose: str | None = None,
        mrn: str = "12345",
        cross_doc_block_id: str | None = None,
    ) -> None:
        self.med_name = med_name
        self.discharge_dose = discharge_dose
        self.mrn = mrn
        self.cross_doc_block_id = cross_doc_block_id
        self.calls: list[tuple[str, str]] = []

    def extract(
        self,
        document_id: str,
        blocks: list[SourceBlock],
        filename: str,
    ) -> VertexExtractOutput:
        self.calls.append((document_id, filename))
        lower = filename.lower()
        if "prior" in lower:
            doc_type = DocumentType.PRIOR_MEDICATION_RECORD
        elif "discharge" in lower:
            doc_type = DocumentType.DISCHARGE_SUMMARY
        elif "rx" in lower or "prescription" in lower:
            doc_type = DocumentType.CURRENT_PRESCRIPTION
        else:
            doc_type = DocumentType.UNKNOWN

        block_id = blocks[0].source_block_id if blocks else f"{document_id}:p1:b1"
        med_block = block_id
        if self.cross_doc_block_id and "discharge" in lower:
            med_block = self.cross_doc_block_id

        fields = [
            VertexFieldOutput(name="mrn", value=self.mrn, source_block_ids=[block_id]),
            VertexFieldOutput(name="patient_name", value="Jane Doe", source_block_ids=[block_id]),
        ]
        med_dose = "10 mg"
        if "discharge" in lower and self.discharge_dose:
            med_dose = self.discharge_dose
        medications = [
            {
                "medication_name": self.med_name,
                "strength": med_dose,
                "dose": med_dose,
                "route": "oral",
                "frequency": "daily",
                "source_block_ids": [med_block],
            }
        ]

        return VertexExtractOutput(
            document_type=doc_type,
            classification_confidence=0.9,
            fields=fields,
            medications=medications,
        )


class FakeDocumentAIClient:
    def __init__(self, *, fail_verify: bool = False, return_empty: bool = False) -> None:
        self.fail_verify = fail_verify
        self.return_empty = return_empty
        self.verify_called = False
        self.process_called = False

    def verify_processor(self) -> None:
        self.verify_called = True
        if self.fail_verify:
            from app.core.exceptions import DocumentAIConfigurationError

            raise DocumentAIConfigurationError("bad processor")

    def process_to_blocks(
        self, document_id: str, content: bytes, mime_type: str
    ) -> list[SourceBlock]:
        self.process_called = True
        if self.return_empty:
            return []
        text = content.decode("utf-8", errors="replace")
        return [
            verified_block(document_id, f"{document_id}:p1:b1", text),
        ]
