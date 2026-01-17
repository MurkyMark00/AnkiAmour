"""Prompt management for AnkiAmour pipeline."""

import os
from . import config


def get_prompt(prompt_name):
    """
    Load a prompt file by name.

    Args:
        prompt_name: Filename (with or without .txt extension)

    Returns:
        Prompt text content
    """
    if not prompt_name.endswith(".txt"):
        prompt_name = f"{prompt_name}.txt"

    prompt_path = os.path.join(config.PROMPTS_DIR, prompt_name)

    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as handle:
        return handle.read()


def list_prompts():
    """List all available prompt files."""
    if not os.path.isdir(config.PROMPTS_DIR):
        return []

    prompts = [
        name for name in os.listdir(config.PROMPTS_DIR) if name.endswith(".txt")
    ]
    return sorted(prompts)
