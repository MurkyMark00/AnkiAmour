"""PDF chunking utilities for large files."""

import tempfile
import logging
from pypdf import PdfReader, PdfWriter
from .. import config

logger = logging.getLogger(__name__)


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


def chunk_pdf(pdf_path, min_pages=None, max_pages=None):
    """
    Split a PDF into evenly-sized chunks within a specified page range.
    Dynamically adjusts range based on total pages while respecting the hard max.

    Args:
        pdf_path: Path to PDF file
        min_pages: Minimum pages per chunk (defaults to config.PDF_CHUNK_MIN_PAGES)
        max_pages: Maximum pages per chunk (defaults to config.PDF_CHUNK_MAX_PAGES, hard max)

    Returns:
        List of temporary file paths for each chunk
    """
    if min_pages is None:
        min_pages = config.PDF_CHUNK_MIN_PAGES
    if max_pages is None:
        max_pages = config.PDF_CHUNK_MAX_PAGES
    
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    if total_pages == 0:
        logger.warning(f"PDF {pdf_path} has 0 pages")
        return []
    
    # Calculate minimum number of chunks needed to respect max_pages constraint
    min_chunks_needed = (total_pages + max_pages - 1) // max_pages  # Ceiling division
    
    # Adjust min_pages if it's impossible to achieve (too many pages for reasonable chunks)
    if total_pages < min_pages:
        # Single chunk, below min (unavoidable)
        num_chunks = 1
        logger.info(f"PDF {total_pages} pages < min_pages {min_pages}. Using 1 chunk.")
    else:
        # Use min_chunks_needed to ensure we don't exceed max_pages
        num_chunks = min_chunks_needed
    
    # Distribute pages evenly across chunks
    base_pages = total_pages // num_chunks
    remainder = total_pages % num_chunks
    
    chunks = []
    start = 0
    
    for i in range(num_chunks):
        # First 'remainder' chunks get one extra page
        chunk_size = base_pages + (1 if i < remainder else 0)
        
        # Log if chunk falls outside ideal range
        if chunk_size < min_pages or chunk_size > max_pages:
            logger.warning(
                f"Chunk {i+1}/{num_chunks}: {chunk_size} pages (ideal range: {min_pages}-{max_pages})"
            )
        
        end = min(start + chunk_size - 1, total_pages - 1)
        chunk_path = extract_pages(pdf_path, start, end)
        chunks.append(chunk_path)
        start = end + 1
    
    logger.info(f"Split PDF ({total_pages} pages) into {num_chunks} chunks")
    return chunks
