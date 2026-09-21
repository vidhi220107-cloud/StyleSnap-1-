"""StyleSnap - Wardrobe Analytics."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Analytics | StyleSnap",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Wardrobe Analytics")
st.caption("Understand your wardrobe through useful statistics.")


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
    """Load saved wardrobe items."""

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
# Load data
# ---------------------------------------------------------

wardrobe_items = load_wardrobe()


# ---------------------------------------------------------
# Empty wardrobe
# ---------------------------------------------------------

if not wardrobe_items:
    st.info(
        "Your wardrobe is empty. Go to **Add to Wardrobe** "
        "and add some fashion items first."
    )
    st.stop()


# ---------------------------------------------------------
# Basic statistics
# ---------------------------------------------------------

total_items = len(wardrobe_items)

categories = [
    item.get("category", "Unknown")
    for item in wardrobe_items
]

colors = [
    item.get("color", "Unknown")
    for item in wardrobe_items
]

seasons = [
    item.get("season", "Unknown")
    for item in wardrobe_items
]

occasions = [
    item.get("occasion", "Unknown")
    for item in wardrobe_items
]


unique_categories = len(set(categories))

unique_colors = len(set(colors))


# ---------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------

st.subheader("📈 Wardrobe Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Items",
        total_items,
    )

with col2:
    st.metric(
        "Categories",
        unique_categories,
    )

with col3:
    st.metric(
        "Colors",
        unique_colors,
    )

with col4:

    if colors:
        most_common_color = max(
            set(colors),
            key=colors.count,
        )
    else:
        most_common_color = "None"

    st.metric(
        "Most Common Color",
        most_common_color,
    )


st.divider()


# ---------------------------------------------------------
# Count helper
# ---------------------------------------------------------

def count_values(values: list[str]) -> dict[str, int]:
    """Count occurrences of each value."""

    counts: dict[str, int] = {}

    for value in values:
        counts[value] = counts.get(value, 0) + 1

    return dict(
        sorted(
            counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )


category_counts = count_values(categories)
color_counts = count_values(colors)
season_counts = count_values(seasons)
occasion_counts = count_values(occasions)


# ---------------------------------------------------------
# Category statistics
# ---------------------------------------------------------

st.subheader("👗 Items by Category")

category_columns = st.columns(2)

with category_columns[0]:

    for category, count in category_counts.items():

        st.write(
            f"**{category}** — {count} item(s)"
        )

        st.progress(
            count / total_items
        )

with category_columns[1]:

    st.write("### Category Summary")

    for category, count in category_counts.items():

        st.metric(
            category,
            count,
        )


st.divider()


# ---------------------------------------------------------
# Color statistics
# ---------------------------------------------------------

st.subheader("🎨 Items by Color")

color_columns = st.columns(2)

with color_columns[0]:

    for color, count in color_counts.items():

        st.write(
            f"**{color}** — {count} item(s)"
        )

        st.progress(
            count / total_items
        )

with color_columns[1]:

    st.write("### Color Summary")

    for color, count in color_counts.items():

        st.metric(
            color,
            count,
        )


st.divider()


# ---------------------------------------------------------
# Season and occasion statistics
# ---------------------------------------------------------

season_col, occasion_col = st.columns(2)


with season_col:

    st.subheader("🌤️ Items by Season")

    for season, count in season_counts.items():

        st.write(
            f"**{season}** — {count} item(s)"
        )

        st.progress(
            count / total_items
        )


with occasion_col:

    st.subheader("🎯 Items by Occasion")

    for occasion, count in occasion_counts.items():

        st.write(
            f"**{occasion}** — {count} item(s)"
        )

        st.progress(
            count / total_items
        )


st.divider()


# ---------------------------------------------------------
# AI confidence
# ---------------------------------------------------------

confidence_values = [
    item.get("ai_confidence")
    for item in wardrobe_items
    if item.get("ai_confidence") is not None
]


if confidence_values:

    average_confidence = (
        sum(confidence_values)
        / len(confidence_values)
    )

    st.subheader("🤖 AI Classification")

    st.metric(
        "Average AI Confidence",
        f"{average_confidence * 100:.2f}%",
    )

    st.progress(
        float(average_confidence)
    )


# ---------------------------------------------------------
# Final tip
# ---------------------------------------------------------

st.info(
    "💡 Tip: Add more items from different categories, "
    "colors, seasons, and occasions to make your wardrobe "
    "analytics more useful."
)