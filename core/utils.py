import fitz  # PyMuPDF
from .models import DocumentChunk


def ingest_manual_pdf(manual_instance):
  """Opens an uploaded Manual PDF using PyMuPDF, extracts text page-by-page,

  and saves each page as a DocumentChunk while preserving exact page numbers.
  """
  pdf_path = manual_instance.pdf_file.path
  doc = fitz.open(pdf_path)

  # Clear any existing chunks for this manual if re-indexing
  manual_instance.chunks.all().delete()

  for page_index in range(len(doc)):
    page = doc[page_index]
    text = page.get_text()

    if text.strip():  # Avoid storing blank pages
      # Page 1 of the PDF counts as PDF page 1 matching printed convention
      DocumentChunk.objects.create(
          manual=manual_instance,
          page_number=page_index + 1,
          text_content=text,
      )

  doc.close()
  