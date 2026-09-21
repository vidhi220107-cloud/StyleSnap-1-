"""StyleSnap - My Wardrobe."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="My Wardrobe | StyleSnap",
    page_icon="👚",
    layout="wide",
)

st.title("👚 My Wardrobe")
st.caption("View and manage everything you have added to your wardrobe.")


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

WARDROBE_DIR = PROJECT_ROOT / "data" / "wardrobe"
IMAGE_DIR = WARDROBE_DIR / "images"
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
# Save wardrobe
# ---------------------------------------------------------

def save_wardrobe(items: list[dict]) -> None:
    """Save wardrobe items to JSON."""

    WARDROBE_DIR.mkdir(parents=True, exist_ok=True)

    with WARDROBE_FILE.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=2, ensure_ascii=False)


# ---------------------------------------------------------
# Delete image
# ---------------------------------------------------------

def delete_image(item: dict) -> None:
    """Delete the image associated with a wardrobe item."""

    image_relative_path = item.get("image", "")

    if not image_relative_path:
        return

    image_path = PROJECT_ROOT / image_relative_path

    try:
        if image_path.exists():
            image_path.unlink()
    except OSError:
        pass


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
        "and add your first fashion item."
    )

    st.stop()


# ---------------------------------------------------------
# Wardrobe summary
# ---------------------------------------------------------

st.subheader("Your Wardrobe")

total_items = len(wardrobe_items)

categories = len(
    set(
        item.get("category", "Unknown")
        for item in wardrobe_items
    )
)

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Items", total_items)

with col2:
    st.metric("Categories", categories)


st.divider()


# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

st.subheader("🔎 Filter Wardrobe")

all_categories = sorted(
    set(
        item.get("category", "Unknown")
        for item in wardrobe_items
    )
)

all_colors = sorted(
    set(
        item.get("color", "Unknown")
        for item in wardrobe_items
    )
)

filter_col1, filter_col2 = st.columns(2)

with filter_col1:

    selected_category = st.selectbox(
        "Category",
        ["All"] + all_categories,
    )

with filter_col2:

    selected_color = st.selectbox(
        "Color",
        ["All"] + all_colors,
    )


# ---------------------------------------------------------
# Apply filters
# ---------------------------------------------------------

filtered_items = wardrobe_items

if selected_category != "All":

    filtered_items = [
        item
        for item in filtered_items
        if item.get("category") == selected_category
    ]

if selected_color != "All":

    filtered_items = [
        item
        for item in filtered_items
        if item.get("color") == selected_color
    ]


st.write(
    f"Showing **{len(filtered_items)}** item(s)"
)


# ---------------------------------------------------------
# Display wardrobe
# ---------------------------------------------------------

if not filtered_items:

    st.warning(
        "No wardrobe items match the selected filters."
    )

    st.stop()


columns_per_row = 4


for start in range(
    0,
    len(filtered_items),
    columns_per_row,
):

    row_items = filtered_items[
        start:start + columns_per_row
    ]

    columns = st.columns(columns_per_row)

    for column, item in zip(columns, row_items):

        with column:

            # ---------------------------------------------
            # Image
            # ---------------------------------------------

            image_relative_path = item.get(
                "image",
                "",
            )

            image_path = (
                PROJECT_ROOT
                / image_relative_path
            )

            if image_path.exists():

                st.image(
                    str(image_path),
                    use_container_width=True,
                )

            else:

                st.warning(
                    "Image not found."
                )


            # ---------------------------------------------
            # Item information
            # ---------------------------------------------

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

            st.write(
                f"**Season:** "
                f"{item.get('season', 'Unknown')}"
            )

            st.write(
                f"**Occasion:** "
                f"{item.get('occasion', 'Unknown')}"
            )

            confidence = item.get(
                "ai_confidence"
            )

            if confidence is not None:

                st.caption(
                    f"AI confidence: "
                    f"{confidence * 100:.2f}%"
                )


            # ---------------------------------------------
            # Edit item
            # ---------------------------------------------

            with st.expander("✏️ Edit Item"):

                edited_name = st.text_input(
                    "Item name",
                    value=item.get(
                        "name",
                        "",
                    ),
                    key=f"name_{item['id']}",
                )

                edited_category = st.text_input(
                    "Category",
                    value=item.get(
                        "category",
                        "",
                    ),
                    key=f"category_{item['id']}",
                )

                edited_color = st.selectbox(
                    "Color",
                    [
                        "Black",
                        "White",
                        "Grey",
                        "Brown",
                        "Blue",
                        "Red",
                        "Green",
                        "Yellow",
                        "Pink",
                        "Purple",
                        "Orange",
                        "Beige",
                        "Multi-color",
                        "Other",
                    ],
                    index=(
                        [
                            "Black",
                            "White",
                            "Grey",
                            "Brown",
                            "Blue",
                            "Red",
                            "Green",
                            "Yellow",
                            "Pink",
                            "Purple",
                            "Orange",
                            "Beige",
                            "Multi-color",
                            "Other",
                        ].index(
                            item.get(
                                "color",
                                "Other",
                            )
                        )
                        if item.get(
                            "color",
                            "Other",
                        )
                        in [
                            "Black",
                            "White",
                            "Grey",
                            "Brown",
                            "Blue",
                            "Red",
                            "Green",
                            "Yellow",
                            "Pink",
                            "Purple",
                            "Orange",
                            "Beige",
                            "Multi-color",
                            "Other",
                        ]
                        else 13
                    ),
                    key=f"color_{item['id']}",
                )

                edited_season = st.selectbox(
                    "Season",
                    [
                        "All Season",
                        "Spring",
                        "Summer",
                        "Autumn",
                        "Winter",
                    ],
                    index=(
                        [
                            "All Season",
                            "Spring",
                            "Summer",
                            "Autumn",
                            "Winter",
                        ].index(
                            item.get(
                                "season",
                                "All Season",
                            )
                        )
                        if item.get(
                            "season",
                            "All Season",
                        )
                        in [
                            "All Season",
                            "Spring",
                            "Summer",
                            "Autumn",
                            "Winter",
                        ]
                        else 0
                    ),
                    key=f"season_{item['id']}",
                )

                edited_occasion = st.selectbox(
                    "Occasion",
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
                    index=(
                        [
                            "Casual",
                            "Formal",
                            "Party",
                            "Work",
                            "Sports",
                            "Traditional",
                            "Travel",
                            "Other",
                        ].index(
                            item.get(
                                "occasion",
                                "Other",
                            )
                        )
                        if item.get(
                            "occasion",
                            "Other",
                        )
                        in [
                            "Casual",
                            "Formal",
                            "Party",
                            "Work",
                            "Sports",
                            "Traditional",
                            "Travel",
                            "Other",
                        ]
                        else 7
                    ),
                    key=f"occasion_{item['id']}",
                )


                if st.button(
                    "💾 Save Changes",
                    key=f"save_{item['id']}",
                    use_container_width=True,
                ):

                    for saved_item in wardrobe_items:

                        if saved_item.get(
                            "id"
                        ) == item.get("id"):

                            saved_item[
                                "name"
                            ] = edited_name.strip()

                            saved_item[
                                "category"
                            ] = edited_category.strip()

                            saved_item[
                                "color"
                            ] = edited_color

                            saved_item[
                                "season"
                            ] = edited_season

                            saved_item[
                                "occasion"
                            ] = edited_occasion

                            break

                    save_wardrobe(
                        wardrobe_items
                    )

                    st.success(
                        "✅ Item updated successfully!"
                    )

                    st.rerun()


            # ---------------------------------------------
            # Delete item
            # ---------------------------------------------

            with st.expander("🗑️ Delete Item"):

                st.warning(
                    "Deleting this item will also remove "
                    "its saved image."
                )

                confirm_delete = st.checkbox(
                    "I understand and want to delete this item.",
                    key=f"confirm_{item['id']}",
                )

                if st.button(
                    "🗑️ Delete Permanently",
                    key=f"delete_{item['id']}",
                    use_container_width=True,
                ):

                    if not confirm_delete:

                        st.error(
                            "Please confirm the deletion first."
                        )

                    else:

                        wardrobe_items = [
                            saved_item
                            for saved_item in wardrobe_items
                            if saved_item.get("id")
                            != item.get("id")
                        ]

                        save_wardrobe(
                            wardrobe_items
                        )

                        delete_image(item)

                        st.success(
                            "✅ Item deleted successfully!"
                        )

                        st.rerun()


            st.divider()