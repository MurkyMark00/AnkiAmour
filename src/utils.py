"""Shared utility functions for AnkiAmour pipeline."""

import json
import os
import re
from datetime import datetime


def log_error(
    error_dir,
    script_name,
    error_message,
    processed_file_name="",
    prompt_file_name="",
    uploaded_file_name="",
    complete_ai_response="",
):
    """
    Append a single error entry to error/errors.log in JSON format.
    """
    timestamp = datetime.now().isoformat(timespec="seconds")

    entry = {
        "Timestamp": timestamp,
        "Script name": script_name,
        "Prompt file name": prompt_file_name,
        "Uploaded file name": uploaded_file_name,
        "Error message": error_message,
        "Complete AI response": complete_ai_response,
        "Processed file name": processed_file_name,
    }

    os.makedirs(error_dir, exist_ok=True)
    error_log = os.path.join(error_dir, "errors.log")

    with open(error_log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps([entry], ensure_ascii=False) + "\n")


def strip_code_fences(text):
    """Remove Markdown code fences (``` or ```json) if present."""
    if "```" not in text:
        return text

    match = re.search(
        r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE
    )
    if match:
        return match.group(1).strip()

    return text


def extract_json_payload(text):
    """
    Extract a JSON payload from a larger response string.

    Handles Markdown fences, leading BOMs, and extra prose around JSON.
    """
    cleaned = strip_code_fences(text).strip().lstrip("\ufeff")
    if not cleaned:
        return ""

    decoder = json.JSONDecoder()

    # Scan for the first valid JSON object/array start and decode from there.
    for index, ch in enumerate(cleaned):
        if ch not in "[{":
            continue
        try:
            _, end = decoder.raw_decode(cleaned[index:])
            return cleaned[index : index + end]
        except json.JSONDecodeError:
            continue

    return cleaned


def is_retryable_error(exc):
    """Identify retryable errors based on common status codes and error types."""
    error_type = type(exc).__name__
    message = str(exc)
    code = getattr(exc, "code", None)
    status = getattr(exc, "status_code", None)

    # Check for rate limit errors (429)
    if "429" in message or "rate_limit" in error_type.lower():
        return True
    if code in (429, 503) or status in (429, 503):
        return True

    # Check for server errors (5xx)
    if "503" in message or "server" in error_type.lower():
        return True

    return False


def read_prompt(prompt_path):
    """Read the prompt file content as UTF-8 text."""
    with open(prompt_path, "r", encoding="utf-8") as handle:
        return handle.read()


def sanitize_tag(value):
    """Replace spaces with underscores in tags."""
    return value.replace(" ", "_")


_BAD_CLOZE_PATTERN = re.compile(r"\{\{c(\d+):(?!:)")


def fix_cloze_format(text):
    """Normalize cloze deletions like {{c1:answer}} to {{c1::answer}}."""
    return _BAD_CLOZE_PATTERN.sub(r"{{c\1::", text)


def normalize_cloze_payload(value):
    """Walk lists/dicts and normalize cloze markers inside any strings."""
    if isinstance(value, str):
        return fix_cloze_format(value)
    if isinstance(value, list):
        return [normalize_cloze_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_cloze_payload(item) for key, item in value.items()}
    return value


def validate_required_fields(items, required_fields=None):
    """
    Ensure every card has required fields.
    Returns (is_valid, error_message).
    """
    if required_fields is None:
        required_fields = {"main_content", "extra_field", "importance_value"}

    if not isinstance(items, list):
        return False, "AI response JSON is not a list."

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            return False, f"Card #{index} is not an object."
        missing = required_fields.difference(item.keys())
        if missing:
            return False, f"Card #{index} is missing fields: {sorted(missing)}"

    return True, ""


def get_pdf_files(directory):
    """Get sorted list of PDF files in directory."""
    pdf_files = [
        name
        for name in os.listdir(directory)
        if name.lower().endswith(".pdf") and os.path.isfile(os.path.join(directory, name))
    ]
    pdf_files.sort(key=str.lower)
    return pdf_files


def get_json_files(directory):
    """Get sorted list of JSON files in directory."""
    json_files = [
        name
        for name in os.listdir(directory)
        if name.lower().endswith(".json")
        and os.path.isfile(os.path.join(directory, name))
    ]
    json_files.sort(key=str.lower)
    return json_files


def get_csv_files(directory, exclude_pattern=None):
    """Get sorted list of CSV files in directory."""
    csv_files = [
        name
        for name in os.listdir(directory)
        if name.lower().endswith(".csv")
        and os.path.isfile(os.path.join(directory, name))
        and (exclude_pattern is None or not exclude_pattern(name))
    ]
    csv_files.sort(key=str.lower)
    return csv_files
