"""Simple local wardrobe storage for StyleSnap."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WARDROBE_DIR = PROJECT_ROOT / "wardrobe_data"
WARDROBE_FILE = WARDROBE_DIR / "wardrobe.json"


def _ensure_storage() -> None:
    """Create the wardrobe storage location if it does not exist."""
    WARDROBE_DIR.mkdir(parents=True, exist_ok=True)

    if not WARDROBE_FILE.exists():
        WARDROBE_FILE.write_text("[]", encoding="utf-8")


def load_items() -> list[dict[str, Any]]:
    """Load all saved wardrobe items."""
    _ensure_storage()

    try:
        data = json.loads(WARDROBE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return data


def save_items(items: list[dict[str, Any]]) -> None:
    """Save the complete wardrobe list."""
    _ensure_storage()

    WARDROBE_FILE.write_text(
        json.dumps(items, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def add_item(item: dict[str, Any]) -> None:
    """Add one item to the wardrobe."""
    items = load_items()
    items.append(item)
    save_items(items)


def remove_item(item_id: str) -> None:
    """Remove one wardrobe item by ID."""
    items = load_items()
    items = [item for item in items if item.get("id") != item_id]
    save_items(items)


def get_item_count() -> int:
    """Return the number of saved wardrobe items."""
    return len(load_items())