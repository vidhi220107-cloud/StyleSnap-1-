"""StyleSnap - AI Stylist."""

from __future__ import annotations

import json
import random
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Stylist | StyleSnap",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI Stylist")
st.caption("Get outfit suggestions based on the items in your wardrobe.")


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

WARDROBE_FILE = (
    PROJECT_ROOT
    / "data"
    / "wardrobe"
    / "wardrobe.json"
)


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
# Outfit recommendation logic
# ---------------------------------------------------------

def recommend_outfit(
    wardrobe: list[dict],
    occasion: str,
    season: str,
) -> list[dict]:
    """Create a simple outfit recommendation."""

    suitable_items = []

    for item in wardrobe:

        item_occasion = item.get("occasion", "Other")
        item_season = item.get("season", "All Season")

        occasion_match = (
            item_occasion == occasion
            or item_occasion == "Other"
        )

        season_match = (
            item_season == season
            or item_season == "All Season"
        )

        if occasion_match and season_match:
            suitable_items.append(item)

    # If not enough items match both filters,
    # relax the season requirement.
    if len(suitable_items) < 2:

        suitable_items = []

        for item in wardrobe:

            item_occasion = item.get("occasion", "Other")

            if (
                item_occasion == occasion
                or item_occasion == "Other"
            ):
                suitable_items.append(item)

    return suitable_items


# ---------------------------------------------------------
# Load wardrobe
# ---------------------------------------------------------

wardrobe_items = load_wardrobe()


# ---------------------------------------------------------
# Empty wardrobe
# ---------------------------------------------------------

if not wardrobe_items:

    st.info(
        "Your wardrobe is empty. "
        "Go to **Add to Wardrobe** and add some items first."
    )

    st.stop()


# ---------------------------------------------------------
# Introduction
# ---------------------------------------------------------

st.subheader("✨ Create Your Outfit")

st.write(
    "Tell StyleSnap where you are going and the season. "
    "The AI Stylist will use your wardrobe items to suggest an outfit."
)


# ---------------------------------------------------------
# User preferences
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    occasion = st.selectbox(
        "🎯 Occasion",
        [
            "Casual",
            "Formal",
            "Party",
            "Work",
            "Sports",
            "Traditional",
            "Travel",
            "Other",
        ],
    )


with col2:

    season = st.selectbox(
        "🌤️ Season",
        [
            "All Season",
            "Spring",
            "Summer",
            "Autumn",
            "Winter",
        ],
    )


# ---------------------------------------------------------
# Generate outfit
# ---------------------------------------------------------

if st.button(
    "✨ Generate My Outfit",
    type="primary",
    use_container_width=True,
):

    recommendations = recommend_outfit(
        wardrobe_items,
        occasion,
        season,
    )

    if not recommendations:

        st.warning(
            "I couldn't find suitable items for this occasion. "
            "Try adding more items to your wardrobe."
        )

        st.stop()


    # Shuffle so repeated generations can vary.
    recommendations = recommendations.copy()
    random.shuffle(recommendations)

    # Use up to 4 items for the outfit.
    outfit = recommendations[:4]


    # -----------------------------------------------------
    # Display recommendation
    # -----------------------------------------------------

    st.divider()

    st.subheader("👗 Your Recommended Outfit")

    st.success(
        f"StyleSnap created an outfit for **{occasion}** "
        f"during **{season}**."
    )


    columns = st.columns(min(len(outfit), 4))


    for column, item in zip(columns, outfit):

        with column:

            image_relative_path = item.get("image", "")
            image_path = PROJECT_ROOT / image_relative_path

            if image_path.exists():

                st.image(
                    str(image_path),
                    use_container_width=True,
                )

            st.markdown(
                f"### {item.get('name', 'Unnamed item')}"
            )

            st.write(
                f"**Category:** "
                f"{item.get('category', 'Unknown')}"
            )

            st.write(
                f"**Color:** "
                f"{item.get('color', 'Unknown')}"
            )


    # -----------------------------------------------------
    # Styling explanation
    # -----------------------------------------------------

    st.divider()

    st.subheader("💡 Why this outfit?")

    st.write(
        f"These items were selected from your wardrobe "
        f"because they are suitable for a **{occasion.lower()}** "
        f"occasion and **{season.lower()}** season."
    )

    st.info(
        "💡 Tip: Add more clothing items with different "
        "categories, colors, seasons, and occasions to get "
        "better outfit combinations."
    )