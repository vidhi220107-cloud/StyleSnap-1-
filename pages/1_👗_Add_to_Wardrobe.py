"""StyleSnap - Add an item to the user's wardrobe."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image

from src.config import CONFIG


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Add to Wardrobe | StyleSnap",
    page_icon="👗",
    layout="wide",
)

st.title("👗 Add to Wardrobe")
st.caption("Upload a fashion item and let StyleSnap identify it.")


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = CONFIG.model_path

WARDROBE_DIR = PROJECT_ROOT / "data" / "wardrobe"
IMAGE_DIR = WARDROBE_DIR / "images"
WARDROBE_FILE = WARDROBE_DIR / "wardrobe.json"

WARDROBE_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Load class names
# ---------------------------------------------------------

def get_class_names() -> tuple[str, ...]:
    """Discover the same alphabetical class order used by TensorFlow."""

    train_dir = Path(CONFIG.train_data_dir)

    if not train_dir.is_dir():
        raise FileNotFoundError(
            f"Training directory does not exist: {train_dir}"
        )

    class_names = sorted(
        folder.name
        for folder in train_dir.iterdir()
        if folder.is_dir()
    )

    if len(class_names) < 2:
        raise ValueError("At least two fashion categories are required.")

    return tuple(class_names)


# ---------------------------------------------------------
# Load trained model
# ---------------------------------------------------------

@st.cache_resource
def load_model():
    """Load the trained StyleSnap MobileNetV2 model once."""

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Trained model was not found at: {MODEL_PATH}"
        )

    return tf.keras.models.load_model(MODEL_PATH)


# ---------------------------------------------------------
# Prediction
# ---------------------------------------------------------

def predict_image(
    image: Image.Image,
    model,
    class_names: tuple[str, ...],
) -> tuple[str, float, list[tuple[str, float]]]:
    """Predict the fashion category and return top-5 predictions."""

    image = image.convert("RGB")
    image = image.resize(CONFIG.image_size)

    image_array = np.asarray(image, dtype=np.float32)
    image_array = np.expand_dims(image_array, axis=0)

    # Same preprocessing used during model training.
    image_array = tf.keras.applications.mobilenet_v2.preprocess_input(
        image_array
    )

    predictions = model.predict(image_array, verbose=0)[0]

    top_indices = np.argsort(predictions)[::-1][:5]

    top_predictions = [
        (class_names[index], float(predictions[index]))
        for index in top_indices
    ]

    predicted_class = top_predictions[0][0]
    confidence = top_predictions[0][1]

    return predicted_class, confidence, top_predictions


# ---------------------------------------------------------
# Wardrobe storage
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


def save_wardrobe(items: list[dict]) -> None:
    """Save wardrobe items as JSON."""

    with WARDROBE_FILE.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=2, ensure_ascii=False)


# ---------------------------------------------------------
# Upload section
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a fashion item image",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file is None:
    st.info(
        "Upload an image of a clothing item, footwear, accessory, "
        "or beauty product to begin."
    )
    st.stop()


# ---------------------------------------------------------
# Display image
# ---------------------------------------------------------

image = Image.open(uploaded_file).convert("RGB")

left, right = st.columns([1, 1])

with left:
    st.subheader("Uploaded Image")
    st.image(image, use_container_width=True)


# ---------------------------------------------------------
# Model prediction
# ---------------------------------------------------------

with st.spinner("Analyzing your item..."):

    try:
        model = load_model()
        class_names = get_class_names()

        predicted_class, confidence, top_predictions = predict_image(
            image,
            model,
            class_names,
        )

    except Exception as error:
        st.error(f"Unable to analyze the image: {error}")
        st.stop()


with right:
    st.subheader("AI Prediction")

    st.success(
        f"**{predicted_class}** — {confidence * 100:.2f}% confidence"
    )

    st.write("### Top 5 predictions")

    for category, probability in top_predictions:
        st.write(
            f"**{category}** — {probability * 100:.2f}%"
        )
        st.progress(float(probability))


# ---------------------------------------------------------
# Wardrobe details
# ---------------------------------------------------------

st.divider()

st.subheader("📝 Item Details")
st.caption("You can correct the AI category before saving the item.")

categories = list(class_names)

default_index = categories.index(predicted_class)

category = st.selectbox(
    "Category",
    categories,
    index=default_index,
)

item_name = st.text_input(
    "Item name",
    placeholder="Example: Brown leather watch",
)

col1, col2, col3 = st.columns(3)

with col1:
    color = st.selectbox(
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
    )

with col2:
    season = st.selectbox(
        "Season",
        [
            "All Season",
            "Spring",
            "Summer",
            "Autumn",
            "Winter",
        ],
    )

with col3:
    occasion = st.selectbox(
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
    )


# ---------------------------------------------------------
# Save item
# ---------------------------------------------------------

if st.button(
    "💾 Add to My Wardrobe",
    type="primary",
    use_container_width=True,
):

    if not item_name.strip():
        item_name = category

    wardrobe_items = load_wardrobe()

    item_id = (
        datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    )

    image_extension = Path(uploaded_file.name).suffix.lower()

    if image_extension not in {".jpg", ".jpeg", ".png", ".webp"}:
        image_extension = ".jpg"

    image_filename = f"{item_id}{image_extension}"
    image_path = IMAGE_DIR / image_filename

    image.save(image_path)

    wardrobe_item = {
        "id": item_id,
        "name": item_name.strip(),
        "category": category,
        "color": color,
        "season": season,
        "occasion": occasion,
        "image": str(
            Path("data") / "wardrobe" / "images" / image_filename
        ),
        "ai_prediction": predicted_class,
        "ai_confidence": round(confidence, 4),
        "added_at": datetime.now().isoformat(timespec="seconds"),
    }

    wardrobe_items.append(wardrobe_item)
    save_wardrobe(wardrobe_items)

    st.success(
        f"✅ **{item_name.strip()}** has been added to your wardrobe!"
    )

    st.info(
        "You can now view this item from the **My Wardrobe** page."
    )