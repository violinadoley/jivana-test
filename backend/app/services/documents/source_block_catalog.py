from app.schemas.meddocs import SourceBlock


class SourceBlockCatalog:
    """Per-document source block maps (document_id -> block_id -> SourceBlock)."""

    def __init__(self) -> None:
        self._by_document: dict[str, dict[str, SourceBlock]] = {}

    def add_block(self, block: SourceBlock) -> None:
        doc_map = self._by_document.setdefault(block.document_id, {})
        doc_map[block.source_block_id] = block

    def blocks_for_document(self, document_id: str) -> dict[str, SourceBlock]:
        return dict(self._by_document.get(document_id, {}))

    def get_block(self, document_id: str, block_id: str) -> SourceBlock | None:
        return self._by_document.get(document_id, {}).get(block_id)

    def document_ids(self) -> list[str]:
        return list(self._by_document.keys())
