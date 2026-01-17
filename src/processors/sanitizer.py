"""File sanitization processor."""

import json
import os
import shutil
import subprocess
import tempfile
import unicodedata
from .. import config, utils


TURKISH_CHAR_MAP = {
    "ç": "c",
    "Ç": "C",
    "ğ": "g",
    "Ğ": "G",
    "ı": "i",
    "İ": "I",
    "ö": "o",
    "Ö": "O",
    "ş": "s",
    "Ş": "S",
    "ü": "u",
    "Ü": "U",
}


def strip_diacritics(text):
    """Remove combining diacritics while preserving base characters."""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def sanitize_name(name):
    """Apply Unicode normalization, Turkish character mapping, and space cleanup."""
    without_marks = strip_diacritics(name)
    mapped = "".join(TURKISH_CHAR_MAP.get(ch, ch) for ch in without_marks)
    return mapped.replace(" ", "_")


def unique_path(directory, filename):
    """Generate a unique path by appending _2, _3, etc. before the extension."""
    base, ext = os.path.splitext(filename)
    candidate = filename
    counter = 2

    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{base}_{counter}{ext}"
        counter += 1

    return os.path.join(directory, candidate)


def compress_pdf(input_path, output_path):
    """
    Compress a PDF using Ghostscript.

    Returns:
        Tuple of (success, stderr_text)
    """
    command = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path,
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    success = (
        result.returncode == 0
        and os.path.exists(output_path)
        and os.path.getsize(output_path) > 0
    )

    return success, result.stderr.strip()


def run():
    """Sanitize and move PDFs from raw_slides to slides."""
    print("[sanitizer] Starting sanitization of raw slides...")

    if not os.path.isdir(config.RAW_SLIDES_DIR):
        utils.log_error(
            config.ERROR_DIR,
            "sanitizer.py",
            f"raw_slides folder not found: {config.RAW_SLIDES_DIR}",
        )
        print("[sanitizer] raw_slides folder not found. Aborting.")
        return

    pdf_files = utils.get_pdf_files(config.RAW_SLIDES_DIR)
    print(f"[sanitizer] Found {len(pdf_files)} PDF file(s) to process.")

    for index, filename in enumerate(pdf_files, start=1):
        print(f"[sanitizer] ({index}/{len(pdf_files)}) Processing {filename}")

        original_path = os.path.join(config.RAW_SLIDES_DIR, filename)
        base_name, extension = os.path.splitext(filename)

        sanitized_base = sanitize_name(base_name)
        sanitized_filename = f"{sanitized_base}{extension}"
        target_path = unique_path(config.SLIDES_DIR, sanitized_filename)

        try:
            file_size = os.path.getsize(original_path)
        except OSError as exc:
            utils.log_error(
                config.ERROR_DIR,
                "sanitizer.py",
                f"Unable to read file size: {exc}",
                processed_file_name=filename,
            )
            continue

        if file_size > config.PDF_COMPRESSION_SIZE_BYTES:
            print("[sanitizer] File exceeds 50 MB, attempting compression...")

            with tempfile.NamedTemporaryFile(
                dir=config.RAW_SLIDES_DIR, delete=False, suffix=extension
            ) as tmp_handle:
                temp_output_path = tmp_handle.name

            success, stderr_text = compress_pdf(original_path, temp_output_path)

            if not success:
                error_target = unique_path(config.ERROR_DIR, sanitized_filename)
                try:
                    shutil.move(original_path, error_target)
                except OSError as exc:
                    utils.log_error(
                        config.ERROR_DIR,
                        "sanitizer.py",
                        f"Compression failed and move to error failed: {exc}",
                        processed_file_name=filename,
                        complete_ai_response=stderr_text,
                    )
                    if os.path.exists(temp_output_path):
                        os.remove(temp_output_path)
                    continue

                utils.log_error(
                    config.ERROR_DIR,
                    "sanitizer.py",
                    "Compression failed; file moved to error folder.",
                    processed_file_name=filename,
                    complete_ai_response=stderr_text,
                )

                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
                continue

            try:
                shutil.move(temp_output_path, target_path)
            except OSError as exc:
                utils.log_error(
                    config.ERROR_DIR,
                    "sanitizer.py",
                    f"Compression succeeded but move to slides failed: {exc}",
                    processed_file_name=filename,
                )
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
                continue

            try:
                os.remove(original_path)
            except OSError as exc:
                utils.log_error(
                    config.ERROR_DIR,
                    "sanitizer.py",
                    f"Compressed file moved, but could not remove original: {exc}",
                    processed_file_name=filename,
                )

            print("[sanitizer] Compression complete and file moved to slides.")
            continue

        try:
            shutil.move(original_path, target_path)
            print("[sanitizer] File moved to slides without compression.")
        except OSError as exc:
            utils.log_error(
                config.ERROR_DIR,
                "sanitizer.py",
                f"Move to slides failed: {exc}",
                processed_file_name=filename,
            )

    print("[sanitizer] Sanitization step complete.")


if __name__ == "__main__":
    run()
