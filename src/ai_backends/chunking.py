"""PDF chunking utilities for large files."""

import tempfile
from pypdf import PdfReader, PdfWriter


def extract_pages(input_pdf_path, start_page, end_page):
    """
    Extract pages from start_page to end_page (inclusive, 0-indexed).

    Args:
        input_pdf_path: Path to input PDF
        start_page: Starting page index (0-based)
        end_page: Ending page index (0-based, inclusive)

    Returns:
        BytesIO object containing the extracted pages
    """
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for page_num in range(start_page, min(end_page + 1, len(reader.pages))):
        writer.add_page(reader.pages[page_num])

    # Write to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    with open(temp_file.name, "wb") as output_file:
        writer.write(output_file)

    return temp_file.name


def chunk_pdf(pdf_path, pages_per_chunk=20):
    """
    Split a PDF into chunks of specified pages.

    Args:
        pdf_path: Path to PDF file
        pages_per_chunk: Number of pages per chunk

    Returns:
        List of temporary file paths for each chunk
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    chunks = []

    for start in range(0, total_pages, pages_per_chunk):
        end = min(start + pages_per_chunk - 1, total_pages - 1)
        chunk_path = extract_pages(pdf_path, start, end)
        chunks.append(chunk_path)

    return chunks
