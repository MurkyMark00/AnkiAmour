"""Configuration management for AnkiAmour pipeline."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory is the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directories
RAW_SLIDES_DIR = os.path.join(BASE_DIR, "data", "raw_slides")
RAW_SLIDES_DONE_DIR = os.path.join(RAW_SLIDES_DIR, "DONE")
SLIDES_DIR = os.path.join(BASE_DIR, "data", "slides")
SLIDES_DONE_DIR = os.path.join(SLIDES_DIR, "DONE")
JSON_DIR = os.path.join(BASE_DIR, "data", "json")
JSON_DONE_DIR = os.path.join(JSON_DIR, "DONE")
CSV_DIR = os.path.join(BASE_DIR, "data", "csv")
CSV_DONE_DIR = os.path.join(CSV_DIR, "DONE")
ERROR_DIR = os.path.join(BASE_DIR, "data", "error")

# Prompts directory
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

# API Configuration (override with environment variables)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

# Pipeline Configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5
PDF_COMPRESSION_SIZE_MB = 50
PDF_COMPRESSION_SIZE_BYTES = PDF_COMPRESSION_SIZE_MB * 1024 * 1024
PDF_CHUNK_MIN_PAGES = int(os.getenv("PDF_CHUNK_MIN_PAGES", "25"))
PDF_CHUNK_MAX_PAGES = int(os.getenv("PDF_CHUNK_MAX_PAGES", "40"))  # Hard limit for token constraints

# Ensure all directories exist
for directory in [RAW_SLIDES_DIR, RAW_SLIDES_DONE_DIR, SLIDES_DIR, SLIDES_DONE_DIR, JSON_DIR, JSON_DONE_DIR, CSV_DIR, CSV_DONE_DIR, ERROR_DIR, PROMPTS_DIR]:
    os.makedirs(directory, exist_ok=True)
