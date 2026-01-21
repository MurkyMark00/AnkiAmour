"""Abstract base class for AI backends."""

from abc import ABC, abstractmethod
import json
from .. import utils


class AIBackend(ABC):
    """Base class for AI provider implementations."""

    def __init__(self, api_key, model_name, max_retries=3, retry_delay=5):
        """
        Initialize AI backend.

        Args:
            api_key: API key for the service
            model_name: Model identifier
            max_retries: Number of retries for transient errors
            retry_delay: Delay in seconds between retries
        """
        self.api_key = api_key
        self.model_name = model_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    @abstractmethod
    def process_pdf(self, pdf_path, prompt_text):
        """
        Process a PDF and return card data.

        Args:
            pdf_path: Path to PDF file
            prompt_text: Prompt to send to AI

        Returns:
            List of card dictionaries or None on error
        """
        pass

    def validate_response(self, cards):
        """
        Validate and normalize card response.

        Args:
            cards: Raw response from AI

        Returns:
            Tuple of (normalized_cards, error_message)
        """
        is_valid, error_msg, filtered_cards = utils.validate_required_fields(cards)
        if not is_valid:
            return None, error_msg

        # Use filtered cards if available, otherwise use original
        cards_to_normalize = filtered_cards if filtered_cards is not None else cards

        # Normalize cloze deletions
        cards = utils.normalize_cloze_payload(cards_to_normalize)

        return cards, ""

    def add_file_tag(self, cards, tag):
        """Add filename tag to card importance_value."""
        for card in cards:
            existing_value = card.get("importance_value")
            if existing_value:
                card["importance_value"] = f"{existing_value} {tag}"
            else:
                card["importance_value"] = tag

        return cards

    def validate_and_tag_response(self, cards, tag):
        """
        Validate response and add file tag in one step with debug info.

        Args:
            cards: Raw response from AI
            tag: Filename tag to add

        Returns:
            Tuple of (validated_cards, error_message)
        """
        is_valid, error_msg, filtered_cards = utils.validate_required_fields(cards)
        if not is_valid:
            return None, error_msg

        # Use filtered cards if available, otherwise use original
        cards_to_normalize = filtered_cards if filtered_cards is not None else cards

        # Normalize cloze deletions
        cards = utils.normalize_cloze_payload(cards_to_normalize)

        # Add tag
        cards = self.add_file_tag(cards, tag)

        return cards, ""
