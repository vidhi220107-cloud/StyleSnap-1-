"""Opt-in command for acquiring and preparing the confirmed StyleSnap dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python scripts/download_dataset.py` from the repository root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_preparation import prepare_dataset


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download, validate, export, and split the StyleSnap dataset."
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Actually fetch KrushiJethe/fashion_data and create local dataset folders.",
    )
    args = parser.parse_args()

    if not args.download:
        print("No download performed. Run with --download to prepare the confirmed dataset.")
        return

    report = prepare_dataset()
    print("Dataset preparation complete.")
    print(f"Classes: {report['class_count']}")
    print(f"Source images: {report['source_image_count']}")
    print(f"Leakage-safe split images: {report['split_image_count']}")
    print(f"Report: {report['report_path']}")


if __name__ == "__main__":
    main()
