"""Gemini AI backend implementation."""

import json
import time
from google import genai
from .. import utils
from .base import AIBackend


class GeminiBackend(AIBackend):
    """Gemini API backend for processing PDFs."""

    def __init__(self, api_key, model_name="gemini-2.5-pro", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        self.client = genai.Client(api_key=api_key)

    def _extract_text(self, response):
        """Extract text from Gemini response."""
        if response is None:
            return ""

        # Try direct .text property (newest SDK)
        text_value = getattr(response, "text", None)
        if isinstance(text_value, str):
            return text_value

        # Fallback: try candidates list
        candidates = getattr(response, "candidates", None)
        if candidates:
            first_candidate = candidates[0]
            content = getattr(first_candidate, "content", None)
            if content and hasattr(content, "parts") and content.parts:
                part_text = getattr(content.parts[0], "text", None)
                if isinstance(part_text, str):
                    return part_text

        return str(response)

    def _upload_file(self, path):
        """Upload file to Gemini."""
        try:
            return self.client.files.upload(file=path)
        except TypeError:
            # Some SDK versions use "path" instead of "file"
            return self.client.files.upload(path=path)

    def process_pdf(self, pdf_path, prompt_text):
        """
        Process a PDF using Gemini API.

        Args:
            pdf_path: Path to PDF file
            prompt_text: Prompt to send to Gemini

        Returns:
            List of card dictionaries or None on error
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                # Upload PDF
                print(f"[gemini] Uploading PDF...")
                upload_start = time.time()
                uploaded_file = self._upload_file(pdf_path)
                upload_time = time.time() - upload_start
                print(f"[gemini] PDF uploaded in {upload_time:.1f}s")

                # Generate response
                print(f"[gemini] Generating content...")
                gen_start = time.time()
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[uploaded_file, prompt_text],
                )
                gen_time = time.time() - gen_start
                print(f"[gemini] Content generated in {gen_time:.1f}s")

                raw_text = self._extract_text(response)

                # Parse JSON from response
                try:
                    cleaned_text = utils.extract_json_payload(raw_text)
                    cards = json.loads(cleaned_text)
                    print(f"[gemini] Generated {len(cards)} cards")
                    return cards
                except json.JSONDecodeError:
                    print(f"[gemini] JSON parsing failed")
                    return None

            except Exception as exc:
                print(f"[gemini] Error (attempt {attempt}/{self.max_retries}): {exc}")
                if utils.is_retryable_error(exc) and attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                return None

        return None
