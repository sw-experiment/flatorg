#!/usr/bin/env python3
"""
File Organizer Script

This script recursively scans a source directory, including hidden files,
and copies all files to a destination directory organized into subfolders:
- pics/ for image files
- vids/ for video files
- docs/ for all other file types

Files are renamed with a sequential numeric prefix (padded to 4 digits).
"""

import argparse
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path


def get_file_category(filename: str) -> str:
    """Determine the category of a file based on its extension."""
    ext = Path(filename).suffix.lower()

    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".webp",
        ".svg",
        ".heic",
        ".heif",
        ".raw",
        ".cr2",
        ".nef",
        ".arw",
    }

    video_extensions = {
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
        ".3gp",
        ".mpg",
        ".mpeg",
        ".ts",
        ".mts",
        ".vob",
    }

    if ext in image_extensions:
        return "pics"
    elif ext in video_extensions:
        return "vids"
    else:
        return "docs"


def collect_files(source_dir: Path) -> list[Path]:
    """Collect all files recursively from source directory."""
    files: list[Path] = []
    for root, _dirs, filenames in os.walk(source_dir):
        for filename in filenames:
            filepath = Path(root) / filename
            files.append(filepath)
    return sorted(files)


def count_files_in_dir(directory: Path) -> int:
    """Count all files recursively in a directory."""
    count = 0
    for _root, _dirs, filenames in os.walk(directory):
        count += len(filenames)
    return count


def copy_files(files: list[Path], dest_dir: Path, plan: bool = False) -> dict[str, int]:
    """Copy files to destination with sequential numbering."""
    counter = 1
    total_files = len(files)
    counts = {"pics": 0, "vids": 0, "docs": 0}

    for i, filepath in enumerate(files, 1):
        category = get_file_category(filepath.name)
        category_dir = dest_dir / category
        if not plan:
            try:
                category_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                logging.error(
                    f"Failed to create category directory {category_dir}: {e}"
                )
                print(f"\nError: Failed to create category directory {category}: {e}")
                raise

        new_filename = f"{counter:04d}_{filepath.name}"
        new_filepath = category_dir / new_filename

        if plan:
            # In plan mode, just log what would happen
            counts[category] += 1
            logging.info(f"PLAN: Would copy {filepath} -> {new_filepath}")
        else:
            try:
                shutil.copy2(filepath, new_filepath)
                counts[category] += 1
                # Log the copy operation
                logging.info(f"COPIED: {filepath} -> {new_filepath}")
            except (OSError, IOError) as e:
                logging.error(f"FAILED to copy {filepath} -> {new_filepath}: {e}")
                print(f"\nError: Failed to copy {filepath.name}: {e}")
                raise  # Re-raise to stop the script

        # Progress indicator with current file
        progress = (i / total_files) * 100
        print(f"{progress:.1f}% - {filepath.name}", end="\r", flush=True)
        counter += 1

    print()  # New line after progress
    operation_type = "planning" if plan else "copy"
    logging.info(
        f"{operation_type.capitalize()} operation completed. Total files: {total_files}"
    )
    return counts


def main():
    parser = argparse.ArgumentParser(
        description="Organize files from source directory into categorized subfolders with sequential numbering."
    )
    parser.add_argument("source", type=Path, help="Source directory to scan for files")
    parser.add_argument(
        "destination",
        type=Path,
        help="Destination directory where organized files will be copied",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Show what would be done without actually copying files (dry run)",
    )

    args = parser.parse_args()

    # Set up logging
    mode = "PLAN" if args.plan else "LIVE"
    log_filename = (
        f"file_organizer_{mode.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info(f"File organizer started ({mode} mode)")
    logging.info(f"Source: {args.source}")
    logging.info(f"Destination: {args.destination}")

    if not args.source.exists():
        print(f"Error: Source directory '{args.source}' does not exist.")
        return 1

    if not args.source.is_dir():
        print(f"Error: Source '{args.source}' is not a directory.")
        return 1

    if args.destination.exists() and not args.destination.is_dir():
        print(f"Error: Destination '{args.destination}' exists but is not a directory.")
        return 1

    # Defensive check: Ensure destination is not inside source directory
    try:
        args.destination.resolve().relative_to(args.source.resolve())
        print(
            f"Error: Destination directory '{args.destination}' cannot be inside source directory '{args.source}'."
        )
        return 1
    except ValueError:
        # Destination is not inside source, which is good
        pass

    # In plan mode, skip destination directory checks and creation
    if not args.plan:
        # Defensive check: Ensure destination directory is empty if it exists
        if args.destination.exists():
            dest_files = list(args.destination.rglob("*"))
            if dest_files:
                print(
                    f"Error: Destination directory '{args.destination}' is not empty. Refusing to overwrite existing files."
                )
                print(f"Found {len(dest_files)} existing items in destination.")
                return 1

        # Create destination if it doesn't exist
        try:
            args.destination.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(
                f"Error: Cannot create destination directory '{args.destination}': {e}"
            )
            logging.error(f"Failed to create destination directory: {e}")
            return 1

    print(f"Scanning files from {args.source}...")
    files = collect_files(args.source)
    source_file_count = len(files)
    print(f"Found {source_file_count} files.")

    print(f"{'Planning' if args.plan else 'Copying'} files to {args.destination}...")
    counts = copy_files(files, args.destination, args.plan)

    if args.plan:
        print("Plan completed - no files were actually copied.")
        dest_file_count = 0  # No files copied in plan mode
    else:
        # Verification
        dest_file_count = count_files_in_dir(args.destination)
        if dest_file_count == source_file_count:
            print("Verification: File counts match!")
        else:
            print(
                f"Warning: Source has {source_file_count} files, destination has {dest_file_count} files."
            )

    # Summary
    print(f"\nSummary ({'PLAN' if args.plan else 'ACTUAL'}):")
    print(f"  Source files: {source_file_count}")
    if not args.plan:
        print(f"  Destination files: {dest_file_count}")
    print(f"  Pics files: {counts['pics']}")
    print(f"  Vids files: {counts['vids']}")
    print(f"  Docs files: {counts['docs']}")

    print("Done!")

    completion_msg = (
        f"File organizer {'plan' if args.plan else 'operation'} completed successfully"
    )
    logging.info(completion_msg)
    return 0


if __name__ == "__main__":
    exit(main())
