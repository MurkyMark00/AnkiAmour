# Quick Start Guide

## 1️⃣ Installation (First Time Only)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# CLAUDE_API_KEY=sk-ant-...
# GEMINI_API_KEY=AIza...
```

## 2️⃣ Add Prompts

Place prompt files in the `prompts/` directory:
- `QAClozeSourceYield.txt` (already present)
- `QACloze.txt`
- Custom prompts...

## 3️⃣ Add PDFs

Place PDF files in `data/raw_slides/`

## 4️⃣ Run Pipeline

### Simplest (Gemini + Default Prompt + Merge)
```bash
python main.py --merge
```
Result: `slides/DONE/`, `csv/DONE/_MASTERDECK.csv`, JSON deleted

### With Claude
```bash
python main.py --backend claude --merge
```

### Custom Prompt + No Merge
```bash
python main.py --backend gemini --prompt QACloze
```
Result: `slides/DONE/`, individual CSVs in `csv/DONE/`

### Preserve JSON for Inspection
```bash
python main.py --no-cleanup --merge
```
Result: `slides/DONE/`, `json/DONE/`, `csv/DONE/_MASTERDECK.csv`

### With Tag Prefix
```bash
python main.py --tag "MED_" --merge custom_deck
```

### Process Raw Slides (Skip Sanitization)
```bash
python main.py --skip-sanitize --no-cleanup --merge
```
Result: `raw_slides/DONE/`, `json/DONE/`, `csv/DONE/`

### Compare Prompts (Keep Files in Place)
```bash
python main.py --prompt QACloze --compare
python main.py --prompt QAClozeSourceYield --compare
```
Result: All files remain in original folders (no DONE moves), can re-run multiple times

## 📁 Output Location

- **Input PDFs**: `data/raw_slides/` (or `data/slides/` after sanitization)
- **Processed PDFs**: Moved to `DONE/` subfolder (unless `--compare`)
- **JSON cards**: `data/json/` (deleted by default, preserved with `--no-cleanup`)
- **CSV files**: `data/csv/` → `data/csv/DONE/`
- **Merged deck**: `data/csv/DONE/_MASTERDECK.csv` or custom name
- **Errors**: `data/error/errors.log`

## 🔧 Configuration

Edit `src/config.py` to change:
- Max retries for API calls
- Retry delay
- PDF compression threshold
- Data directory paths

## 📖 Full Help

```bash
python main.py --help
```

## ❌ Troubleshooting

### API Key Error
```
ValueError: CLAUDE_API_KEY not set
```
→ Check `.env` file exists and has `CLAUDE_API_KEY=...`

### Prompt Not Found
```
FileNotFoundError: Prompt file not found
```
→ Verify prompt file is in `prompts/` directory

### No PDFs Found
→ Place PDF files in `data/raw_slides/`

### Permission Error
→ Check `data/` directory is writable

## 📝 Available Prompts

List available prompts in `prompts/`:
- `QAClozeSourceYield.txt` - Questions with yield levels and sources
- `QACloze.txt` - Simple question format
- Add custom `.txt` files as needed

## 🎯 Typical Workflow

```bash
# 1. Copy PDFs to raw_slides
cp ~/Medical_Slides/*.pdf data/raw_slides/

# 2. Run full pipeline with Claude
python main.py --backend claude --prompt QAClozeSourceYield --merge

# 3. Open Anki and import
# File → Import → data/csv/_MASTERDECK.csv

# 4. Check for errors if needed
cat data/error/errors.log
```

## 💡 Pro Tips

- Use `--skip-sanitize` if PDFs are already cleaned (keeps them in `raw_slides/DONE/`)
- Use `--no-cleanup` to preserve JSON for debugging (moves to `json/DONE/`)
- Use `--compare` to test multiple prompts on the same PDFs without moving files
- Large PDFs (>50MB) are automatically compressed
- All errors logged to `data/error/errors.log`
- Use different output names to keep multiple decks: `--merge deck_v1`, `--merge deck_v2`
- Default behavior: `--merge` moves to `slides/DONE/` after processing

## 🆘 More Help

See `README.md` for complete documentation
