#!/usr/bin/env python3
"""
AnkiAmour: Convert medical slides to Anki decks.

Pipeline:
1) Sanitize PDF filenames and optionally compress large files
2) Upload PDFs to AI (Claude or Gemini) and parse JSON responses
3) Convert JSON to CSV format
4) Optionally merge all CSV files into a master deck
"""

import argparse
import sys
from src import pipeline


def main():
    """Parse CLI arguments and execute the pipeline."""
    parser = argparse.ArgumentParser(
        description="Run the AnkiAmour card generation pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --backend claude --prompt QAClozeSourceYield --merge
  python main.py --backend gemini --prompt QACloze --tag "Medical_" --skip-sanitize
  python main.py --backend claude --prompt QAClozeSourceYield --merge custom_deck
        """,
    )

    parser.add_argument(
        "--backend",
        "-b",
        choices=["claude", "gemini"],
        default="gemini",
        help="AI backend to use (default: gemini)",
    )

    parser.add_argument(
        "--prompt",
        "-p",
        default="QAClozeSourceYield",
        help="Prompt file to use (without .txt extension). Default: QAClozeSourceYield",
    )

    parser.add_argument(
        "--tag",
        "-t",
        default="",
        help="Optional tag prefix to prepend before the PDF filename tag.",
    )

    parser.add_argument(
        "--merge",
        "-m",
        nargs="?",
        const="",
        default=None,
        help="Merge CSVs into a master deck. Optionally provide a custom name.",
    )

    parser.add_argument(
        "--skip-sanitize",
        action="store_true",
        help="Skip the file sanitization step.",
    )

    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Keep intermediate JSON files and individual CSVs after processing.",
    )

    args = parser.parse_args()

    # Determine merge output filename
    merge_output = None
    if args.merge is not None:
        merge_output = args.merge if args.merge else "_MASTERDECK"

    try:
        pipeline.run(
            prompt_name=args.prompt,
            backend_type=args.backend,
            tag_prefix=args.tag,
            merge_output=merge_output,
            skip_sanitize=args.skip_sanitize,
            cleanup=not args.no_cleanup,
        )
    except KeyboardInterrupt:
        print("\n[main] Pipeline interrupted by user.")
        sys.exit(1)
    except Exception as exc:
        print(f"[main] Pipeline failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
