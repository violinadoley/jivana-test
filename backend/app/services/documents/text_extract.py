import io


def extract_text_pages(content: bytes, content_type: str) -> list[tuple[int, str]]:
    """Vertex-only fallback: per-page text chunks."""
    if content_type == "text/plain":
        text = content.decode("utf-8", errors="replace")
        return [(1, text)]

    if content_type == "application/pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(content))
            pages: list[tuple[int, str]] = []
            for i, page in enumerate(reader.pages, start=1):
                pages.append((i, page.extract_text() or ""))
            return pages or [(1, "")]
        except Exception:
            return [(1, "")]

    return [(1, "")]
