"""Manual processing helpers."""

import pymupdf

from .models import DocumentChunk


def ingest_manual_pdf(manual_instance):
    """Extract non-empty PDF pages and store them as manual chunks."""
    chunks = []
    with pymupdf.open(manual_instance.pdf_file.path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text()
            if text.strip():
                chunks.append(
                    DocumentChunk(
                        manual=manual_instance,
                        page_number=page_number,
                        text_content=text,
                    )
                )

    manual_instance.chunks.all().delete()
    DocumentChunk.objects.bulk_create(chunks)
