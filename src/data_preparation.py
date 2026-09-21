"""Acquire, validate, export, and split the confirmed StyleSnap dataset.

This module deliberately contains no model or training logic. It turns the
Hugging Face Parquet dataset into a portable ImageFolder-style dataset that
TensorFlow can consume in a later phase.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError
from sklearn.model_selection import train_test_split

from src.config import CONFIG, PROJECT_ROOT


VALID_IMAGE_SUFFIX = ".jpg"
MANIFEST_FIELDS = ("source_id", "class_name", "relative_path", "sha256")


def _require_empty_directory(path: Path) -> None:
    """Create a destination or fail safely when it already contains files."""
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(
            f"Refusing to overwrite existing data at {path}. Remove it manually only if intended."
        )
    path.mkdir(parents=True, exist_ok=True)


def _safe_class_directory(class_name: str) -> str:
    """Accept source class names while preventing an unsafe path from being created."""
    if not class_name or Path(class_name).name != class_name:
        raise ValueError(f"Unsafe dataset class name: {class_name!r}")
    return class_name


def _save_rgb_jpeg(image: Image.Image, destination: Path) -> str:
    """Validate, convert to RGB, save, and return the output file hash."""
    try:
        image.load()
        rgb_image = image.convert("RGB")
    except (OSError, UnidentifiedImageError) as error:
        raise ValueError(f"Unreadable source image for {destination.name}") from error

    rgb_image.save(destination, format="JPEG", quality=95)
    with destination.open("rb") as image_file:
        return hashlib.sha256(image_file.read()).hexdigest()


def _load_source_dataset() -> Any:
    """Load the confirmed source lazily so normal imports do not need datasets installed."""
    try:
        from datasets import load_dataset
    except ImportError as error:
        raise RuntimeError(
            "Missing dependency 'datasets'. Install requirements.txt before downloading the dataset."
        ) from error

    return load_dataset(CONFIG.dataset_id, split=CONFIG.dataset_source_split)


def export_raw_dataset() -> list[dict[str, str]]:
    """Download source rows and export verified RGB images grouped by true class name."""
    _require_empty_directory(CONFIG.raw_data_dir)
    dataset = _load_source_dataset()
    required_columns = {"image", "Unnamed: 0", "articleType"}
    missing_columns = required_columns.difference(dataset.column_names)
    if missing_columns:
        raise ValueError(f"Unexpected source schema; missing columns: {sorted(missing_columns)}")

    records: list[dict[str, str]] = []
    seen_source_ids: set[str] = set()
    for row in dataset:
        source_id = str(row["Unnamed: 0"])
        class_name = _safe_class_directory(str(row["articleType"]))
        if source_id in seen_source_ids:
            raise ValueError(f"Duplicate source ID found: {source_id}")
        seen_source_ids.add(source_id)

        class_dir = CONFIG.raw_data_dir / class_name
        class_dir.mkdir(exist_ok=True)
        destination = class_dir / f"{source_id}{VALID_IMAGE_SUFFIX}"
        file_hash = _save_rgb_jpeg(row["image"], destination)
        records.append(
            {
                "source_id": source_id,
                "class_name": class_name,
                "relative_path": str(destination.relative_to(PROJECT_ROOT)),
                "sha256": file_hash,
            }
        )

    _write_manifest(CONFIG.raw_data_dir / "manifest.csv", records)
    return records


def _write_manifest(path: Path, records: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as manifest_file:
        writer = csv.DictWriter(manifest_file, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(records)


def _read_manifest(path: Path) -> list[dict[str, str]]:
    """Load a prior raw export manifest to safely resume interrupted preparation."""
    with path.open(newline="", encoding="utf-8") as manifest_file:
        reader = csv.DictReader(manifest_file)
        if tuple(reader.fieldnames or ()) != MANIFEST_FIELDS:
            raise ValueError(f"Unexpected manifest schema in {path}")
        return [dict(row) for row in reader]


def remove_exact_duplicates(records: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    """Keep one deterministic copy of each exact image for leakage-free evaluation.

    The raw export remains complete for provenance. Only duplicate copies are
    excluded from the derived split folders. A duplicate hash with different
    labels would be a label conflict and stops preparation for manual review.
    """
    records_by_hash: dict[str, list[dict[str, str]]] = {}
    for record in records:
        records_by_hash.setdefault(record["sha256"], []).append(record)

    selected_source_ids: set[str] = set()
    duplicate_count = 0
    for image_records in records_by_hash.values():
        labels = {record["class_name"] for record in image_records}
        if len(labels) > 1:
            raise ValueError(
                "The same image appears with conflicting labels: "
                f"{sorted(labels)}. Resolve this before splitting."
            )
        selected_record = min(image_records, key=lambda record: int(record["source_id"]))
        selected_source_ids.add(selected_record["source_id"])
        duplicate_count += len(image_records) - 1

    unique_records = [record for record in records if record["source_id"] in selected_source_ids]
    return unique_records, duplicate_count


def create_splits(records: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Create deterministic, stratified, mutually exclusive train/validation/test records."""
    CONFIG.validate_split_ratios()
    train_records, holdout_records = train_test_split(
        records,
        test_size=CONFIG.validation_split + CONFIG.test_split,
        random_state=CONFIG.random_seed,
        stratify=[record["class_name"] for record in records],
    )
    validation_fraction_of_holdout = CONFIG.validation_split / (
        CONFIG.validation_split + CONFIG.test_split
    )
    validation_records, test_records = train_test_split(
        holdout_records,
        test_size=1 - validation_fraction_of_holdout,
        random_state=CONFIG.random_seed,
        stratify=[record["class_name"] for record in holdout_records],
    )
    return {"train": train_records, "validation": validation_records, "test": test_records}


def materialize_splits(split_records: dict[str, list[dict[str, str]]]) -> None:
    """Copy exported files into independent ImageFolder-style split directories."""
    destination_dirs = {
        "train": CONFIG.train_data_dir,
        "validation": CONFIG.validation_data_dir,
        "test": CONFIG.test_data_dir,
    }
    for split_name, destination_root in destination_dirs.items():
        _require_empty_directory(destination_root)
        split_manifest: list[dict[str, str]] = []
        for record in split_records[split_name]:
            source = PROJECT_ROOT / record["relative_path"]
            destination = destination_root / record["class_name"] / source.name
            destination.parent.mkdir(exist_ok=True)
            shutil.copy2(source, destination)
            split_manifest.append({**record, "relative_path": str(destination.relative_to(PROJECT_ROOT))})
        _write_manifest(destination_root / "manifest.csv", split_manifest)


def _verify_export(records: list[dict[str, str]]) -> dict[str, int]:
    """Open every exported image to verify RGB readability and count each class."""
    counts: Counter[str] = Counter()
    for record in records:
        image_path = PROJECT_ROOT / record["relative_path"]
        try:
            with Image.open(image_path) as image:
                if image.mode != "RGB":
                    raise ValueError(f"Exported image is not RGB: {image_path}")
                image.verify()
        except (OSError, UnidentifiedImageError) as error:
            raise ValueError(f"Exported image validation failed: {image_path}") from error
        counts[record["class_name"]] += 1
    return dict(sorted(counts.items()))


def prepare_dataset() -> dict[str, Any]:
    """Run the complete Phase 2 acquisition and leakage-safe preparation workflow."""
    raw_manifest_path = CONFIG.raw_data_dir / "manifest.csv"
    raw_records = _read_manifest(raw_manifest_path) if raw_manifest_path.exists() else export_raw_dataset()
    raw_class_counts = _verify_export(raw_records)
    records, duplicate_count = remove_exact_duplicates(raw_records)
    split_records = create_splits(records)
    materialize_splits(split_records)

    split_counts = {
        split_name: dict(sorted(Counter(r["class_name"] for r in split).items()))
        for split_name, split in split_records.items()
    }
    report = {
        "dataset_id": CONFIG.dataset_id,
        "source_split": CONFIG.dataset_source_split,
        "source_image_count": len(raw_records),
        "split_image_count": len(records),
        "class_count": len(raw_class_counts),
        "raw_class_counts": raw_class_counts,
        "split_class_counts": dict(sorted(Counter(r["class_name"] for r in records).items())),
        "split_counts": split_counts,
        "random_seed": CONFIG.random_seed,
        "image_validation": "Every exported image reopened successfully as RGB.",
        "duplicate_image_check": {
            "exact_duplicate_copies_excluded_from_splits": duplicate_count,
            "policy": "One deterministic copy per SHA-256 hash; cross-label duplicates fail preparation.",
        },
        "license_note": "The source dataset card does not declare a derivative license; document the upstream Kaggle MIT source and attribution.",
    }
    report_path = CONFIG.raw_data_dir / "verification_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["report_path"] = str(report_path.relative_to(PROJECT_ROOT))
    return report
