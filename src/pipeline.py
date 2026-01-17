"""Pipeline orchestration for the full AnkiAmour process."""

import os
import shutil
from .processors import sanitizer
from .processors.ai_processor import run as run_ai_processor
from .processors.json_converter import run as run_json_converter
from .processors.csv_merger import run as run_csv_merger
from . import config


def _cleanup_json_files():
    """Delete all files in the json directory."""
    if os.path.isdir(config.JSON_DIR):
        for filename in os.listdir(config.JSON_DIR):
            if filename == "DONE":
                continue
            file_path = os.path.join(config.JSON_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"[pipeline] Warning: Could not delete {file_path}: {e}")


def _move_json_to_done():
    """Move all JSON files from json/ to json/DONE/."""
    if os.path.isdir(config.JSON_DIR):
        for filename in os.listdir(config.JSON_DIR):
            if filename == "DONE":
                continue
            file_path = os.path.join(config.JSON_DIR, filename)
            if os.path.isfile(file_path):
                done_path = os.path.join(config.JSON_DONE_DIR, filename)
                try:
                    shutil.move(file_path, done_path)
                    print(f"[pipeline] Moved {filename} to json/DONE/")
                except Exception as e:
                    print(f"[pipeline] Warning: Could not move {filename}: {e}")


def _move_raw_slides_to_done():
    """Move all processed PDF files from raw_slides/ to raw_slides/DONE/."""
    if os.path.isdir(config.RAW_SLIDES_DIR):
        for filename in os.listdir(config.RAW_SLIDES_DIR):
            if filename == "DONE":
                continue
            file_path = os.path.join(config.RAW_SLIDES_DIR, filename)
            if os.path.isfile(file_path):
                done_path = os.path.join(config.RAW_SLIDES_DONE_DIR, filename)
                try:
                    shutil.move(file_path, done_path)
                    print(f"[pipeline] Moved {filename} to raw_slides/DONE/")
                except Exception as e:
                    print(f"[pipeline] Warning: Could not move {filename}: {e}")


def _cleanup_csv_files():
    """Delete all CSV files in the csv directory (except in DONE subfolder)."""
    if os.path.isdir(config.CSV_DIR):
        for filename in os.listdir(config.CSV_DIR):
            if filename == "DONE":
                continue
            if filename.lower().endswith(".csv"):
                file_path = os.path.join(config.CSV_DIR, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"[pipeline] Warning: Could not delete {file_path}: {e}")


def _move_all_csv_to_done():
    """Move all CSV files from csv/ to csv/DONE/."""
    if os.path.isdir(config.CSV_DIR):
        for filename in os.listdir(config.CSV_DIR):
            if filename == "DONE":
                continue
            if filename.lower().endswith(".csv"):
                file_path = os.path.join(config.CSV_DIR, filename)
                if os.path.isfile(file_path):
                    done_path = os.path.join(config.CSV_DONE_DIR, filename)
                    try:
                        shutil.move(file_path, done_path)
                        print(f"[pipeline] Moved {filename} to csv/DONE/")
                    except Exception as e:
                        print(f"[pipeline] Warning: Could not move {filename}: {e}")


def _move_merged_deck(merged_filename):
    """Move merged CSV file from csv/ to csv/DONE/."""
    file_path = os.path.join(config.CSV_DIR, merged_filename)
    if os.path.isfile(file_path):
        done_path = os.path.join(config.CSV_DONE_DIR, merged_filename)
        try:
            shutil.move(file_path, done_path)
            print(f"[pipeline] Moved {merged_filename} to csv/DONE/")
        except Exception as e:
            print(f"[pipeline] Warning: Could not move {merged_filename}: {e}")


def run(
    prompt_name,
    backend_type="gemini",
    tag_prefix="",
    merge_output=None,
    skip_sanitize=False,
    cleanup=True,
):
    """
    Run the full AnkiAmour pipeline.

    Args:
        prompt_name: Name of prompt file (with or without .txt)
        backend_type: "claude" or "gemini" (default: gemini)
        tag_prefix: Optional prefix for filename tags
        merge_output: Output filename for merged CSV (None to skip merge)
        skip_sanitize: Skip file sanitization step if True
        cleanup: Delete intermediate files (JSON and individual CSVs) if True (default)
    """
    print("=" * 60)
    print("AnkiAmour Pipeline Starting")
    print("=" * 60)

    # Step 1: Always Sanitize (regardless of skip_sanitize flag)
    print("\nStep 1/4: Sanitizing raw slides...")
    try:
        sanitizer.run()
    except Exception as exc:
        print(f"[pipeline] Sanitization failed: {exc}")
        return

    # Step 2: PDF to JSON
    print("\nStep 2/4: Converting PDFs to JSON...")
    try:
        run_ai_processor(prompt_name, backend_type=backend_type, tag_prefix=tag_prefix)
    except Exception as exc:
        print(f"[pipeline] PDF to JSON failed: {exc}")
        return

    # Step 3: JSON to CSV
    print("\nStep 3/4: Converting JSON to CSV...")
    try:
        run_json_converter()
    except Exception as exc:
        print(f"[pipeline] JSON to CSV failed: {exc}")
        return

    # Step 4: Merge (optional)
    merged_filename = None
    if merge_output is not None:
        print("\nStep 4/4: Merging CSV files...")
        try:
            run_csv_merger(merge_output)
            # Determine the merged filename for cleanup later
            if merge_output:
                merged_filename = (
                    merge_output
                    if merge_output.lower().endswith(".csv")
                    else f"{merge_output}.csv"
                )
            else:
                merged_filename = "_MASTERDECK.csv"
        except Exception as exc:
            print(f"[pipeline] CSV merge failed: {exc}")
            return
    else:
        print("\nStep 4/4: Skipping CSV merge (not requested)...")

    # Step 5: Handle JSON files based on skip_sanitize flag
    if skip_sanitize:
        print("\nPreserving JSON files (moving to json/DONE/)...")
        _move_json_to_done()
    else:
        print("\nCleaning up JSON files...")
        _cleanup_json_files()
        print("Moving processed slides from raw_slides/ to raw_slides/DONE/...")
        _move_raw_slides_to_done()

    # Step 6: Handle CSV files
    if merge_output is not None:
        print("\nMoving merged deck to csv/DONE/...")
        _move_merged_deck(merged_filename)
        print("Deleting individual CSV files...")
        _cleanup_csv_files()
    else:
        print("\nMoving all CSV files to csv/DONE/...")
        _move_all_csv_to_done()

    print("\n" + "=" * 60)
    print("AnkiAmour Pipeline Complete!")
    print("=" * 60)
