"""CSV merge processor."""

import os
from .. import config, utils


def is_excluded_master(name, base_name):
    """Exclude existing master deck files that match the output base name."""
    if not name.lower().endswith(".csv"):
        return False

    stem = os.path.splitext(name)[0]
    if stem == base_name:
        return True

    # Exclude suffix variants like Base_2, Base_3, etc.
    if stem.startswith(f"{base_name}_"):
        suffix = stem[len(base_name) + 1 :]
        return suffix.isdigit()

    return False


def unique_output_path(directory, filename):
    """Generate a unique output file path by appending _2, _3, etc. to the name."""
    base, ext = os.path.splitext(filename)
    candidate = filename
    counter = 2

    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{base}_{counter}{ext}"
        counter += 1

    return os.path.join(directory, candidate)


def run(output_name=None):
    """Merge CSV files into a master deck."""
    print("[csv_merger] Starting CSV merge...")

    # Default output name if none was provided.
    if output_name:
        output_filename = output_name
    else:
        output_filename = "_MASTERDECK"

    # Ensure the output name ends with .csv.
    if not output_filename.lower().endswith(".csv"):
        output_filename = f"{output_filename}.csv"

    output_base = os.path.splitext(output_filename)[0]

    def exclude_filter(name):
        return is_excluded_master(name, output_base)

    csv_files = utils.get_csv_files(config.CSV_DIR, exclude_pattern=exclude_filter)

    if not csv_files:
        print("[csv_merger] No CSV files found. Nothing to merge.")
        return

    # Order by modified time
    csv_files.sort(key=lambda name: os.path.getmtime(os.path.join(config.CSV_DIR, name)))

    output_path = unique_output_path(config.CSV_DIR, output_filename)

    print(f"[csv_merger] Merging {len(csv_files)} file(s) into {output_path}.")

    try:
        with open(output_path, "w", encoding="utf-8") as out_handle:
            last_char = None

            for name in csv_files:
                input_path = os.path.join(config.CSV_DIR, name)

                with open(input_path, "r", encoding="utf-8") as in_handle:
                    content = in_handle.read()

                # Insert a newline if the previous file did not end with one.
                if last_char not in (None, "\n") and content:
                    out_handle.write("\n")

                out_handle.write(content)

                if content:
                    last_char = content[-1]

    except OSError as exc:
        utils.log_error(
            config.ERROR_DIR,
            "csv_merger.py",
            f"Failed to merge CSV files: {exc}",
            processed_file_name=output_filename,
        )
        print("[csv_merger] Merge failed; see error log for details.")
        return

    print("[csv_merger] Merge complete.")


if __name__ == "__main__":
    run()
