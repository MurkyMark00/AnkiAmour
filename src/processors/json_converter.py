"""JSON to CSV conversion processor."""

import csv
import json
import os
from .. import config, utils


def run():
    """Convert JSON files to CSV files."""
    print("[json_converter] Starting JSON to CSV conversion...")

    json_files = utils.get_json_files(config.JSON_DIR)
    print(f"[json_converter] Found {len(json_files)} JSON file(s) to process.")

    for index, filename in enumerate(json_files, start=1):
        print(f"[json_converter] ({index}/{len(json_files)}) Processing {filename}")

        json_path = os.path.join(config.JSON_DIR, filename)
        csv_filename = f"{os.path.splitext(filename)[0]}.csv"
        csv_path = os.path.join(config.CSV_DIR, csv_filename)

        try:
            with open(json_path, "r", encoding="utf-8") as handle:
                cards = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            utils.log_error(
                config.ERROR_DIR,
                "json_converter.py",
                f"Failed to read JSON: {exc}",
                processed_file_name=filename,
            )
            print(f"[json_converter] Failed to read {filename}; skipping.")
            continue

        is_valid, validation_message, filtered_cards = utils.validate_required_fields(cards)
        if not is_valid:
            utils.log_error(
                config.ERROR_DIR,
                "json_converter.py",
                f"Invalid card structure: {validation_message}",
                processed_file_name=filename,
            )
            print(f"[json_converter] Invalid structure in {filename}; skipping file.")
            continue
        
        # Use filtered cards if some were invalid, otherwise use original
        cards_to_write = filtered_cards if filtered_cards is not None else cards
        print(f"[json_converter] Converting {len(cards_to_write)} cards to CSV...")

        try:
            # newline="" avoids CSV writer adding extra blank lines on some platforms.
            with open(csv_path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(
                    handle,
                    delimiter="|",
                    quoting=csv.QUOTE_MINIMAL,
                    lineterminator="\n",
                )

                for card in cards_to_write:
                    writer.writerow(
                        [
                            card["main_content"],
                            card["extra_field"],
                            card["importance_value"],
                        ]
                    )
        except OSError as exc:
            utils.log_error(
                config.ERROR_DIR,
                "json_converter.py",
                f"Failed to write CSV: {exc}",
                processed_file_name=filename,
            )
            print(f"[json_converter] Failed to write CSV for {filename}.")
            continue

        print(f"[json_converter] ✓ Wrote {len(cards_to_write)} cards to {csv_filename}.")

    print("[json_converter] Conversion complete.")


if __name__ == "__main__":
    run()
