"""StyleSnap - Smart Shopping."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Smart Shopping | StyleSnap",
    page_icon="🛍️",
    layout="wide",
)

st.title("🛍️ Smart Shopping")
st.caption(
    "Discover useful additions based on what is missing from your wardrobe."
)


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

WARDROBE_DIR = PROJECT_ROOT / "data" / "wardrobe"
WARDROBE_FILE = WARDROBE_DIR / "wardrobe.json"


# ---------------------------------------------------------
# Load wardrobe
# ---------------------------------------------------------

def load_wardrobe() -> list[dict]:
    """Load wardrobe items from JSON."""

    if not WARDROBE_FILE.exists():
        return []

    try:
        with WARDROBE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (json.JSONDecodeError, OSError):
        pass

    return []


# ---------------------------------------------------------
# Shopping recommendations
# ---------------------------------------------------------

def generate_recommendations(
    wardrobe_items: list[dict],
) -> list[dict]:
    """Generate simple shopping recommendations from wardrobe gaps."""

    categories = {
        str(item.get("category", "")).strip().lower()
        for item in wardrobe_items
    }

    recommendations = []

    # Common wardrobe categories.
    suggestions = [
        (
            "Tops",
            "Add a versatile top to create more everyday outfit combinations.",
            "Useful for casual, work, and travel outfits.",
        ),
        (
            "Bottoms",
            "Consider adding a pair of versatile bottoms.",
            "Bottoms can be combined with many different tops.",
        ),
        (
            "Shoes",
            "A versatile pair of shoes could expand your outfit options.",
            "Shoes help complete casual, formal, and travel looks.",
        ),
        (
            "Accessories",
            "Add an accessory to give your outfits more variety.",
            "Accessories can change the appearance of an existing outfit.",
        ),
        (
            "Outerwear",
            "Consider adding a lightweight jacket or other outerwear.",
            "Useful for layering and changing weather conditions.",
        ),
    ]

    category_keywords = {
        "tops": ["top", "shirt", "t-shirt", "tshirt", "blouse"],
        "bottoms": ["bottom", "pants", "trousers", "jeans", "shorts", "skirt"],
        "shoes": ["shoe", "shoes", "footwear", "sneaker", "sandals", "boots"],
        "accessories": [
            "accessor",
            "watch",
            "bag",
            "belt",
            "scarf",
            "hat",
            "jewelry",
        ],
        "outerwear": [
            "outerwear",
            "jacket",
            "coat",
            "blazer",
            "hoodie",
        ],
    }

    for category, description, reason in suggestions:

        category_key = category.lower()

        exists = any(
            any(
                keyword in existing_category
                for keyword in category_keywords[category_key]
            )
            for existing_category in categories
        )

        if not exists:
            recommendations.append(
                {
                    "category": category,
                    "description": description,
                    "reason": reason,
                }
            )

    return recommendations


# ---------------------------------------------------------
# Load wardrobe data
# ---------------------------------------------------------

wardrobe_items = load_wardrobe()


# ---------------------------------------------------------
# Empty wardrobe
# ---------------------------------------------------------

if not wardrobe_items:

    st.info(
        "Your wardrobe is currently empty. "
        "Add some items first from the **Add to Wardrobe** page."
    )

    st.stop()


# ---------------------------------------------------------
# Wardrobe overview
# ---------------------------------------------------------

st.subheader("🧾 Your Wardrobe Overview")

total_items = len(wardrobe_items)

unique_categories = sorted(
    {
        str(item.get("category", "Unknown"))
        for item in wardrobe_items
    }
)

unique_colors = sorted(
    {
        str(item.get("color", "Unknown"))
        for item in wardrobe_items
    }
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Items in Wardrobe", total_items)

with col2:
    st.metric("Categories", len(unique_categories))

with col3:
    st.metric("Colors", len(unique_colors))


st.divider()


# ---------------------------------------------------------
# Generate recommendations
# ---------------------------------------------------------

st.subheader("✨ Recommended Additions")

st.write(
    "StyleSnap looks at the categories already present in your wardrobe "
    "and suggests useful areas to expand."
)

recommendations = generate_recommendations(wardrobe_items)


# ---------------------------------------------------------
# Display recommendations
# ---------------------------------------------------------

if not recommendations:

    st.success(
        "🎉 Your wardrobe already contains a good mix of the main "
        "categories. Keep adding items as your style evolves!"
    )

else:

    columns_per_row = 2

    for start in range(
        0,
        len(recommendations),
        columns_per_row,
    ):

        row = recommendations[
            start:start + columns_per_row
        ]

        columns = st.columns(columns_per_row)

        for column, recommendation in zip(columns, row):

            with column:

                st.markdown(
                    f"### 🛒 {recommendation['category']}"
                )

                st.write(
                    recommendation["description"]
                )

                st.info(
                    f"💡 **Why:** {recommendation['reason']}"
                )


# ---------------------------------------------------------
# Existing wardrobe categories
# ---------------------------------------------------------

st.divider()

st.subheader("📦 Categories You Already Own")

if unique_categories:

    category_text = " • ".join(unique_categories)

    st.success(category_text)

st.caption(
    "Tip: Add items from different categories to create more "
    "outfit combinations with the AI Stylist and Weekly Planner."
)