"""StyleSnap AI - Main application."""

import streamlit as st

from src.config import CONFIG


st.set_page_config(
    page_title="StyleSnap AI",
    page_icon="👗",
    layout="wide",
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.markdown(
    """
    <div style="padding: 10px 0 20px 0;">
        <div style="font-size: 28px; font-weight: 800;">
            ✨ StyleSnap
        </div>
        <div style="color: #9ca3af; font-size: 13px;">
            AI Personal Stylist
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Home
# ---------------------------------------------------------

st.title("✨ StyleSnap AI")

st.subheader("Your wardrobe. Your style. Powered by AI.")

st.write(
    "StyleSnap helps you organize your wardrobe, discover outfit ideas, "
    "plan what to wear, and make smarter fashion decisions."
)


# ---------------------------------------------------------
# Feature cards
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 👗 Add to Wardrobe")
    st.write(
        "Upload a fashion item and let StyleSnap identify its category."
    )

with col2:
    st.markdown("### 🤖 AI Stylist")
    st.write(
        "Get outfit suggestions based on your wardrobe and occasion."
    )

with col3:
    st.markdown("### 🛍️ Smart Shopping")
    st.write(
        "Discover useful additions based on what your wardrobe is missing."
    )


col4, col5 = st.columns(2)

with col4:
    st.markdown("### 👚 My Wardrobe")
    st.write(
        "Keep all your clothing and accessories organized in one place."
    )

with col5:
    st.markdown("### 📊 Analytics")
    st.write(
        "Understand your wardrobe through useful statistics."
    )

# ---------------------------------------------------------
# Getting started
# ---------------------------------------------------------

st.divider()

st.header("✨ Get Started")

st.write(
    "Use the pages in the sidebar to explore StyleSnap."
)

st.info(
    "Start by adding a few items to your wardrobe. "
    "Once your wardrobe has items, the AI Stylist, outfit planner, "
    "shopping recommendations, and analytics can use that information."
)


# ---------------------------------------------------------
# Project information
# ---------------------------------------------------------

with st.expander("About StyleSnap"):
    st.write("AI model: MobileNetV2")
    st.write("Image input: 224 × 224 RGB")
    st.write("Fashion categories: 31")
    st.write("Test accuracy: 89.20%")