import streamlit as st
import cv2
import numpy as np
from PIL import Image

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StyleSnap AI Camera Stylist",
    page_icon="✨",
    layout="wide"
)

# ============================================================
# CUSTOM UI
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background: #0b0f17;
    }

    /* Main content width */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1400px;
    }

    /* Hero */
    .hero {
        padding: 28px 32px;
        border-radius: 24px;
        background: linear-gradient(
            135deg,
            #111827 0%,
            #172554 50%,
            #111827 100%
        );
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: #aeb7c7;
        font-size: 17px;
    }

    /* Section titles */
    .section-title {
        font-size: 27px;
        font-weight: 750;
        margin-top: 28px;
        margin-bottom: 16px;
    }

    .section-subtitle {
        color: #9ca3af;
        margin-bottom: 20px;
    }

    /* Analysis cards */
    .analysis-card {
        padding: 20px;
        min-height: 125px;
        border-radius: 18px;
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .card-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }

    .card-label {
        color: #9ca3af;
        font-size: 14px;
    }

    .card-value {
        font-size: 20px;
        font-weight: 700;
        margin-top: 5px;
    }

    /* Recommendation cards */
    .recommendation {
        padding: 22px;
        border-radius: 18px;
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
        min-height: 180px;
    }

    .recommendation h3 {
        margin-top: 0;
    }

    .recommendation p {
        color: #cbd5e1;
        line-height: 1.6;
    }

    /* AI result */
    .ai-result {
        padding: 24px;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #10251d,
            #123524
        );
        border: 1px solid rgba(74,222,128,0.18);
    }

    .ai-result-title {
        font-size: 22px;
        font-weight: 750;
        margin-bottom: 10px;
    }

    .ai-result-text {
        color: #d1fae5;
        line-height: 1.7;
    }

    /* Info banner */
    .info-banner {
        padding: 16px 20px;
        border-radius: 14px;
        background: #172b43;
        color: #cbd5e1;
        border: 1px solid rgba(96,165,250,0.15);
    }

    /* Divider */
    .soft-divider {
        height: 1px;
        background: rgba(255,255,255,0.10);
        margin: 32px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">📷 StyleSnap AI Camera Stylist</div>
        <div class="hero-subtitle">
            Capture your look and get computer-vision based styling insights
            for your outfit.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HOW IT WORKS
# ============================================================

st.markdown(
    """
    <div class="section-title">🪄 How StyleSnap Works</div>

    <div class="section-subtitle">
        StyleSnap analyzes your camera image and uses the detected visual
        characteristics to generate styling guidance.
    </div>
    """,
    unsafe_allow_html=True
)

step1, step2, step3 = st.columns(3)

with step1:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="card-icon">📸</div>
            <div class="card-label">STEP 01</div>
            <div class="card-value">Capture</div>
            <p>Take a photo using your camera.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with step2:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="card-icon">🔍</div>
            <div class="card-label">STEP 02</div>
            <div class="card-value">Analyze</div>
            <p>OpenCV analyzes the captured image.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with step3:
    st.markdown(
        """
        <div class="analysis-card">
            <div class="card-icon">✨</div>
            <div class="card-label">STEP 03</div>
            <div class="card-value">Style</div>
            <p>Receive personalized styling suggestions.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# CAMERA
# ============================================================

st.markdown(
    """
    <div class="section-title">📸 Capture Your Look</div>

    <div class="section-subtitle">
        Stand in front of the camera so your face and outfit are clearly visible.
    </div>
    """,
    unsafe_allow_html=True
)

camera_image = st.camera_input(
    "Take a photo of your outfit"
)

# ============================================================
# NO IMAGE
# ============================================================

if camera_image is None:

    st.markdown(
        """
        <div class="info-banner">
            📷 <b>Ready when you are.</b><br>
            Take a photo above to start your StyleSnap analysis.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()

# ============================================================
# READ IMAGE
# ============================================================

image = Image.open(camera_image).convert("RGB")
image_np = np.array(image)

cv_image = cv2.cvtColor(
    image_np,
    cv2.COLOR_RGB2BGR
)

# ============================================================
# FACE DETECTION
# ============================================================

gray = cv2.cvtColor(
    cv_image,
    cv2.COLOR_BGR2GRAY
)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(50, 50)
)

# ============================================================
# DRAW DETECTION
# ============================================================

result_image = cv_image.copy()

for (x, y, w, h) in faces:

    cv2.rectangle(
        result_image,
        (x, y),
        (x + w, y + h),
        (0, 255, 0),
        3
    )

    cv2.putText(
        result_image,
        "Face",
        (x, max(y - 10, 25)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

result_rgb = cv2.cvtColor(
    result_image,
    cv2.COLOR_BGR2RGB
)

# ============================================================
# OUTFIT COLOR ANALYSIS
# ============================================================

height, width, _ = image_np.shape

clothing = image_np[
    int(height * 0.35):int(height * 0.85),
    int(width * 0.20):int(width * 0.80)
]

average_color = clothing.mean(axis=(0, 1))

r, g, b = average_color

if r > 180 and g > 180 and b > 180:

    detected_color = "White / Light"

elif r < 70 and g < 70 and b < 70:

    detected_color = "Black / Dark"

elif r > g * 1.3 and r > b * 1.3:

    detected_color = "Red / Warm"

elif g > r * 1.2 and g > b * 1.1:

    detected_color = "Green"

elif b > r * 1.2 and b > g * 1.1:

    detected_color = "Blue"

elif r > 130 and g > 80 and b < 100:

    detected_color = "Yellow / Mustard"

elif r > 100 and g > 60 and b < 70:

    detected_color = "Brown / Warm"

else:

    detected_color = "Mixed / Neutral"

# ============================================================
# AI CAMERA ANALYSIS
# ============================================================

st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-title">🔍 AI Camera Analysis</div>
    """,
    unsafe_allow_html=True
)

image_col, status_col = st.columns([1.35, 1])

# ------------------------------------------------------------
# IMAGE
# ------------------------------------------------------------

with image_col:

    st.image(
        result_rgb,
        caption="StyleSnap Computer Vision Analysis",
        use_container_width=True
    )

# ------------------------------------------------------------
# DETECTION STATUS
# ------------------------------------------------------------

with status_col:

    st.markdown("### 📊 Detection Summary")

    if len(faces) > 0:

        st.markdown(
            """
            <div class="analysis-card">
                <div class="card-icon">👤</div>
                <div class="card-label">PERSON</div>
                <div class="card-value">Detected</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        st.markdown(
            f"""
            <div class="analysis-card">
                <div class="card-icon">🙂</div>
                <div class="card-label">FACE</div>
                <div class="card-value">{len(faces)} detected</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.warning(
            "No clear face detected. Try standing closer to the camera."
        )

    st.write("")

    st.markdown(
        f"""
        <div class="analysis-card">
            <div class="card-icon">🎨</div>
            <div class="card-label">OUTFIT COLOR</div>
            <div class="card-value">{detected_color}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# STYLE INSIGHTS
# ============================================================

suggestions = {

    "White / Light": (
        "Clean and versatile",
        "Try neutral bottoms, denim, brown accessories or minimal sneakers.",
        "Avoid combining too many very light shades without contrast."
    ),

    "Black / Dark": (
        "Sleek and modern",
        "Try white, beige or denim accessories for contrast.",
        "Avoid using too many dark shades if you want a lighter daytime look."
    ),

    "Red / Warm": (
        "Energetic and noticeable",
        "Pair with black, white, beige or denim.",
        "Avoid combining several strong bright colors together."
    ),

    "Green": (
        "Fresh and earthy",
        "Try beige, white, black or brown accessories.",
        "Avoid too many competing bright colors."
    ),

    "Blue": (
        "Versatile and easy to style",
        "Try white, black, beige or denim combinations.",
        "Avoid pairing it with too many saturated colors."
    ),

    "Yellow / Mustard": (
        "Warm statement look",
        "Try black, white, navy, denim or brown.",
        "Avoid combining several bright warm colors."
    ),

    "Brown / Warm": (
        "Earthy and sophisticated",
        "Try cream, white, black, denim or olive.",
        "Avoid using too many similar brown shades."
    ),

    "Mixed / Neutral": (
        "Balanced mixed tones",
        "Use one main color and keep accessories simple.",
        "Avoid adding too many additional colors."
    )
}

style_summary, wear_suggestion, avoid_suggestion = suggestions[
    detected_color
]

# ============================================================
# STYLE INSIGHTS SECTION
# ============================================================

st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-title">✨ StyleSnap Style Insights</div>

    <div class="section-subtitle">
        Styling guidance generated from the detected outfit color profile.
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        f"""
        <div class="recommendation">
            <h3>👗 Current Style</h3>
            <p>{style_summary}</p>
            <p>
                <b>Detected palette:</b><br>
                {detected_color}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="recommendation">
            <h3>✅ What to Wear</h3>
            <p>{wear_suggestion}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        f"""
        <div class="recommendation">
            <h3>🚫 What to Avoid</h3>
            <p>{avoid_suggestion}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# AI RESULT
# ============================================================
st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">🤖 AI Styling Result</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
<div class="ai-result">
<div class="ai-result-title">✨ StyleSnap has analyzed your look</div>
<div class="ai-result-text">
Your detected outfit palette is <b>{detected_color}</b>.<br><br>
Based on this visual analysis, StyleSnap recommends:
<b>{wear_suggestion}</b>.<br><br>
<b>Style direction:</b> {style_summary}.
</div>
</div>
""",
    unsafe_allow_html=True
)
# ============================================================
# PROJECT CONNECTION
# ============================================================

st.markdown(
    '<div class="soft-divider"></div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="section-title">🔗 StyleSnap Project Connection</div>

    <div class="info-banner">

    <b>How this feature connects to StyleSnap</b><br><br>

    The AI Camera Stylist acts as the computer vision component
    of StyleSnap. It captures the user's image, detects the face,
    analyzes the visual outfit colors, and generates styling
    recommendations based on the detected outfit profile.

    <br><br>

    The camera analysis complements the StyleSnap wardrobe and
    styling features by providing outfit insights directly from
    the user's captured look.

    </div>
    """,
    unsafe_allow_html=True
)