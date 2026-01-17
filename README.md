# AnkiAmour - Medical Slide to Anki Deck Converter

Convert medical presentation slides into Anki study decks using AI-powered card generation.

## Project Structure

```
AnkiAmour/
├── src/                          # Core application code
│   ├── config.py                # Configuration management
│   ├── prompts.py               # Prompt loading
│   ├── utils.py                 # Shared utilities
│   ├── pipeline.py              # Main orchestration
│   ├── processors/              # Data processing modules
│   │   ├── sanitizer.py         # PDF file sanitization
│   │   ├── ai_processor.py      # PDF to JSON conversion
│   │   ├── json_converter.py    # JSON to CSV conversion
│   │   └── csv_merger.py        # CSV file merging
│   └── ai_backends/             # AI provider implementations
│       ├── base.py              # Abstract base class
│       ├── claude.py            # Claude API backend
│       ├── gemini.py            # Gemini API backend
│       └── chunking.py          # PDF chunking utilities
├── data/                         # Data directories
│   ├── raw_slides/              # Unsanitized PDF files
│   │   └── DONE/                # Processed raw slides (when --skip-sanitize not used)
│   ├── slides/                  # Sanitized PDFs (input directory)
│   │   └── DONE/                # Processed sanitized slides (when --skip-sanitize not used)
│   ├── json/                    # AI-generated JSON cards
│   │   └── DONE/                # Archived JSON files (when --skip-sanitize used)
│   ├── csv/                     # Generated CSV files
│   │   └── DONE/                # Merged master deck and archived CSVs
│   └── error/                   # Error logs
├── prompts/                      # Prompt templates
├── main.py                       # Entry point
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (create from .env.example)
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
CLAUDE_API_KEY=your_claude_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### 3. Add Prompts

Place prompt files in the `prompts/` directory. Prompt files should be `.txt` files containing instructions for the AI model.

## Usage

### Basic Usage (Claude with default prompt)

```bash
python main.py --merge
```

### Full Options

```bash
python main.py --help

Options:
  -b, --backend {claude,gemini}    AI backend to use (default: claude)
  -p, --prompt PROMPT              Prompt file name (default: QAClozeSourceYield)
  -t, --tag TAG                    Tag prefix for cards
  -m, --merge [NAME]               Merge CSVs into a master deck
  --skip-sanitize                  Preserve JSON files (move to DONE) instead of deleting them. Does NOT skip sanitization.
```

### Examples

```bash
# Process with Claude and merge into master deck
# Result: Master deck in csv/DONE/, individual CSVs deleted
python main.py --backend claude --prompt QAClozeSourceYield --merge

# Process with Gemini with custom tag prefix, no merge
# Result: All CSVs moved to csv/DONE/
python main.py --backend gemini --prompt QACloze --tag "Medical_"

# Preserve JSON files for inspection (don't delete them)
# Result: JSON files moved to json/DONE/, raw slides moved to raw_slides/DONE/
python main.py --backend claude --skip-sanitize --merge

# Process without merging
# Result: Individual CSV files moved to csv/DONE/
python main.py --backend claude --prompt QAClozeSourceYield
```

## Pipeline Steps

The pipeline always runs through these steps:

1. **Sanitize** - Clean PDF filenames, convert Turkish characters to ASCII, optionally compress large files. Moves PDFs from `data/slides/` → `data/raw_slides/`
2. **AI Processing** - Upload PDFs to AI model, generate JSON cards
3. **Convert to CSV** - Transform JSON cards to CSV format (Front|Back|Tags)
4. **JSON Handling** - Based on `--skip-sanitize` flag:
   - **Without `--skip-sanitize`**: JSON files are deleted, raw slides moved to `raw_slides/DONE/`
   - **With `--skip-sanitize`**: JSON files moved to `json/DONE/` for preservation
5. **CSV Handling** - Based on `--merge` flag:
   - **Without `--merge`**: All CSV files moved to `csv/DONE/`
   - **With `--merge`**: Master deck moved to `csv/DONE/`, individual CSV files deleted

## Configuration

### Environment Variables (`.env`)

- `CLAUDE_API_KEY` - Claude API key
- `GEMINI_API_KEY` - Gemini API key
- `CLAUDE_MODEL` - Claude model name (default: claude-sonnet-4-5-20250929)
- `GEMINI_MODEL` - Gemini model name (default: gemini-2.5-pro)

### Code Configuration (`src/config.py`)

- `MAX_RETRIES` - API retry attempts (default: 3)
- `RETRY_DELAY_SECONDS` - Delay between retries (default: 5)
- `PDF_COMPRESSION_SIZE_MB` - Threshold for compression (default: 50)
- `PDF_CHUNK_MIN_PAGES` - Minimum pages per PDF chunk (default: 25, configurable via `PDF_CHUNK_MIN_PAGES` env var)
- `PDF_CHUNK_MAX_PAGES` - Maximum pages per PDF chunk (default: 40, hard limit for token constraints, configurable via `PDF_CHUNK_MAX_PAGES` env var)

## Error Handling

All errors are logged to `data/error/errors.log` in JSON format with:
- Timestamp
- Script name
- Error message
- Complete AI response (if applicable)
- Processed file name
- Prompt file name

## Card Format

### JSON Format (Generated by AI)
```json
[
  {
    "main_content": "Question text with {{c1::answer}}",
    "extra_field": "Additional context, mnemonics, etc.",
    "importance_value": "HighYield"
  }
]
```

### CSV Format (Final output)
```
Main content|Extra field|Tags
Question {{c1::answer}}|Context and mnemonics|HighYield PDF_Name
```

## Extending the System

### Adding a New AI Backend

1. Create a new file in `src/ai_backends/` (e.g., `openai.py`)
2. Inherit from `AIBackend` in `base.py`
3. Implement `process_pdf()` method
4. Update `src/processors/ai_processor.py` to support the new backend

### Custom Data Processing

Add new processors in `src/processors/` following the existing patterns. Update `src/pipeline.py` to include the new step.

## Troubleshooting

### API Key Issues
- Verify `.env` file exists and contains correct keys
- Check that environment variables are properly loaded
- Ensure keys have appropriate permissions/API access

### PDF Compression Issues
- Requires Ghostscript (`gs` command): `brew install ghostscript`
- Ensure Ghostscript is in PATH

### Large PDF Handling
- Files over 50 MB are automatically compressed
- Adjust `PDF_COMPRESSION_SIZE_MB` in `src/config.py` if needed
- Use `--skip-sanitize` if PDFs are already processed

## License

Internal use only.
