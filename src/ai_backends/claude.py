"""Claude AI backend implementation."""

import base64
import json
import time
from anthropic import Anthropic
from .. import utils
from .base import AIBackend


class ClaudeBackend(AIBackend):
    """Claude API backend for processing PDFs."""

    def __init__(self, api_key, model_name="claude-sonnet-4-5-20250929", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        self.client = Anthropic(api_key=api_key)

    def _extract_text(self, response):
        """Extract text from Claude response."""
        if response is None:
            return ""

        content = getattr(response, "content", None)
        if isinstance(content, list) and len(content) > 0:
            first_block = content[0]
            text_value = getattr(first_block, "text", None)
            if isinstance(text_value, str):
                return text_value

        return str(response)

    def process_pdf(self, pdf_path, prompt_text):
        """
        Process a PDF using Claude API.

        Args:
            pdf_path: Path to PDF file
            prompt_text: Prompt to send to Claude

        Returns:
            List of card dictionaries or None on error
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                # Read and encode PDF
                with open(pdf_path, "rb") as pdf_file:
                    pdf_data = pdf_file.read()

                # Create stream with PDF attachment
                start_time = time.time()
                stream = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=64000,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "document",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "application/pdf",
                                        "data": base64.b64encode(pdf_data).decode("utf-8"),
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": prompt_text,
                                },
                            ],
                        }
                    ],
                    stream=True,
                )

                # Collect streamed response
                raw_text = ""
                chunk_count = 0
                for event in stream:
                    if event.type == "content_block_delta":
                        if hasattr(event.delta, "text"):
                            raw_text += event.delta.text
                            chunk_count += 1

                elapsed_time = time.time() - start_time
                print(f"[claude] Received {chunk_count} stream chunks in {elapsed_time:.1f}s")

                # Parse JSON from response
                try:
                    cleaned_text = utils.extract_json_payload(raw_text)
                    cards = json.loads(cleaned_text)
                    print(f"[claude] Generated {len(cards)} cards")
                    return cards
                except json.JSONDecodeError as e:
                    print(f"[claude] JSON parsing failed: {e}")
                    return None

            except Exception as exc:
                print(f"[claude] Error (attempt {attempt}/{self.max_retries}): {exc}")
                if utils.is_retryable_error(exc) and attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
                return None

        return None
