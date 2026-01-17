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

### Simplest (Claude + Default Prompt + Merge)
```bash
python main.py --merge
```

### With Gemini
```bash
python main.py --backend gemini --merge
```

### Custom Prompt
```bash
python main.py --backend claude --prompt QACloze --merge
```

### With Tag Prefix
```bash
python main.py --backend claude --tag "MED_" --merge custom_deck
```

### No Merge (Just Generate Cards)
```bash
python main.py --backend claude --prompt QAClozeSourceYield
```

## 📁 Output Location

- **JSON cards**: `data/json/`
- **CSV files**: `data/csv/`
- **Merged deck**: `data/csv/_MASTERDECK.csv` or `data/csv/{custom_name}.csv`
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

- Use `--skip-sanitize` if PDFs are already cleaned
- Large PDFs (>50MB) are automatically compressed
- All errors logged to `data/error/errors.log`
- Use different output names to keep multiple decks: `--merge deck_v1`, `--merge deck_v2`
- Preview cards in `data/json/` before importing to Anki

## 🆘 More Help

See `README.md` for complete documentation
