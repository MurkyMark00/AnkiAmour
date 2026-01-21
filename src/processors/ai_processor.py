"""AI processor for converting PDFs to JSON."""

import json
import os
import time
from .. import config, utils, prompts
from ..ai_backends.base import AIBackend
from ..ai_backends.claude import ClaudeBackend
from ..ai_backends.gemini import GeminiBackend
from ..ai_backends import chunking


def get_backend(backend_type="claude"):
    """
    Get an AI backend instance.

    Args:
        backend_type: "claude" or "gemini"

    Returns:
        AIBackend instance
    """
    if backend_type.lower() == "claude":
        if not config.CLAUDE_API_KEY:
            raise ValueError(
                "CLAUDE_API_KEY not set. Set it as an environment variable."
            )
        return ClaudeBackend(
            api_key=config.CLAUDE_API_KEY,
            model_name=config.CLAUDE_MODEL,
            max_retries=config.MAX_RETRIES,
            retry_delay=config.RETRY_DELAY_SECONDS,
        )
    elif backend_type.lower() == "gemini":
        if not config.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not set. Set it as an environment variable."
            )
        return GeminiBackend(
            api_key=config.GEMINI_API_KEY,
            model_name=config.GEMINI_MODEL,
            max_retries=config.MAX_RETRIES,
            retry_delay=config.RETRY_DELAY_SECONDS,
        )
    else:
        raise ValueError(f"Unknown backend: {backend_type}")


def run(prompt_name, backend_type="claude", tag_prefix=""):
    """
    Process PDFs to JSON using specified AI backend.

    Args:
        prompt_name: Name of prompt file (with or without .txt)
        backend_type: "claude" or "gemini"
        tag_prefix: Optional prefix for filename tags
    """
    print(f"[ai_processor] Starting {backend_type.upper()} processing of slides...")

    # Load prompt
    try:
        prompt_text = prompts.get_prompt(prompt_name)
    except FileNotFoundError as exc:
        utils.log_error(
            config.ERROR_DIR,
            "ai_processor.py",
            str(exc),
        )
        raise SystemExit(str(exc))

    # Get backend
    try:
        backend = get_backend(backend_type)
    except ValueError as exc:
        utils.log_error(
            config.ERROR_DIR,
            "ai_processor.py",
            str(exc),
        )
        raise SystemExit(str(exc))

    # Get PDF files
    pdf_files = utils.get_pdf_files(config.SLIDES_DIR)
    print(f"[ai_processor] Found {len(pdf_files)} PDF file(s) to process.")

    for index, filename in enumerate(pdf_files, start=1):
        print(f"[ai_processor] ({index}/{len(pdf_files)}) Processing {filename}")

        pdf_path = os.path.join(config.SLIDES_DIR, filename)
        pdf_base = os.path.splitext(filename)[0]
        pdf_tag = utils.sanitize_tag(pdf_base)
        combined_tag = f"{tag_prefix}{pdf_tag}" if tag_prefix else pdf_tag

        # Check if PDF needs chunking
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"[ai_processor] PDF has {total_pages} pages")

        # Chunk if necessary
        if total_pages > config.PDF_CHUNK_MAX_PAGES:
            print(f"[ai_processor] PDF exceeds max pages ({config.PDF_CHUNK_MAX_PAGES}), chunking...")
            chunks = chunking.chunk_pdf(pdf_path)
            all_cards = []
            
            for chunk_idx, chunk_path in enumerate(chunks, start=1):
                print(f"[ai_processor] Processing chunk {chunk_idx}/{len(chunks)}...")
                chunk_start = time.time()
                
                cards = backend.process_pdf(chunk_path, prompt_text)
                
                chunk_time = time.time() - chunk_start
                if cards:
                    print(f"[ai_processor] Chunk {chunk_idx} completed in {chunk_time:.1f}s with {len(cards)} cards")
                    all_cards.extend(cards)
                else:
                    print(f"[ai_processor] Chunk {chunk_idx} failed or returned no cards")
                    
            cards = all_cards if all_cards else None
        else:
            print(f"[ai_processor] Processing as single file...")
            process_start = time.time()
            cards = backend.process_pdf(pdf_path, prompt_text)
            process_time = time.time() - process_start
            print(f"[ai_processor] Processing completed in {process_time:.1f}s")

        if cards is None:
            utils.log_error(
                config.ERROR_DIR,
                "ai_processor.py",
                f"{backend_type.upper()} API error occurred",
                processed_file_name=filename,
                prompt_file_name=prompt_name,
            )
            print(f"[ai_processor] Skipping {filename} due to API error.")
            continue

        # Validate response
        validated_cards, error_msg = backend.validate_response(cards)
        if validated_cards is None:
            utils.log_error(
                config.ERROR_DIR,
                "ai_processor.py",
                f"Invalid card structure: {error_msg}",
                processed_file_name=filename,
                prompt_file_name=prompt_name,
            )
            print(f"[ai_processor] Invalid card structure for {filename}; skipping.")
            continue
        
        # Log any auto-corrections made during validation
        if error_msg:
            try:
                correction_info = json.loads(error_msg)
                if "corrected_cards" in correction_info and correction_info["corrected_cards"]:
                    utils.log_error(
                        config.ERROR_DIR,
                        "ai_processor.py",
                        f"Auto-corrected {len(correction_info['corrected_cards'])} cards with missing fields: {json.dumps(correction_info['corrected_cards'])}",
                        processed_file_name=filename,
                        prompt_file_name=prompt_name,
                    )
            except (json.JSONDecodeError, TypeError):
                pass  # error_msg is not correction info, skip logging

        # Add file tag
        tagged_cards = backend.add_file_tag(validated_cards, combined_tag)
        print(f"[ai_processor] Added tag '{combined_tag}' to {len(tagged_cards)} cards")

        # Write output
        json_output_name = f"{pdf_base}.json"
        json_output_path = os.path.join(config.JSON_DIR, json_output_name)

        try:
            with open(json_output_path, "w", encoding="utf-8") as handle:
                json.dump(tagged_cards, handle, ensure_ascii=False, indent=2)
        except OSError as exc:
            utils.log_error(
                config.ERROR_DIR,
                "ai_processor.py",
                f"Failed to write JSON output: {exc}",
                processed_file_name=filename,
                prompt_file_name=prompt_name,
            )
            print(f"[ai_processor] Failed to write JSON for {filename}; skipping.")
            continue

        print(f"[ai_processor] ✓ Wrote {len(tagged_cards)} cards to {json_output_name}.")

    print(f"[ai_processor] {backend_type.upper()} processing complete.")


if __name__ == "__main__":
    run("QAClozeSourceYield", backend_type="claude")
