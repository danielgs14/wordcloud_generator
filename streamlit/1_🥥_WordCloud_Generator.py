# imports
import io
import os
import unicodedata
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from wordcloud import WordCloud

# page config
st.set_page_config(
    page_title="Word Cloud Generator",
    page_icon="🥥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🥥 Word Cloud Generator")
st.markdown("Upload a CSV, tweak the settings, and generate your word cloud.")

# helper functions
def normalize_text(text: str) -> str:
    """Lowercase and strip accents so variants like lógico/logico merge."""
    text = text.lower()
    nfd = unicodedata.normalize("NFD", text)
    return "".join(i for i in nfd if unicodedata.category(i) != "Mn")


def build_wordcloud(text, width, height, background, colormap, max_words, font_path):
    transparent = background.lower() == "none"
    bg_color = None if transparent else background

    word_counts = Counter(text.split())

    wc = WordCloud(
        width=width,
        height=height,
        background_color=bg_color,
        mode="RGBA" if transparent else "RGB",
        colormap=colormap,
        max_words=max_words,
        collocations=False,
        prefer_horizontal=0.85,
        margin=10,
        font_path=font_path if font_path and os.path.exists(font_path) else None,
    ).generate_from_frequencies(word_counts)

    fig_height = height / 100
    fig, ax = plt.subplots(figsize=(width / 100, fig_height), dpi=100)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout(pad=0)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150, transparent=transparent)
    plt.close(fig)
    buf.seek(0)
    return buf

# sidebar configs

with st.sidebar:
    st.header("🍈 Settings")

    colormap = st.selectbox(
        "Color palette",
        ["inferno", "viridis", "plasma", "magma", "cividis",
         "inferno_r", "viridis_r", "plasma_r", "magma_r"],
        index=0
    )
    background = st.selectbox(
        "Background",
        ["none (transparent)", "white", "black"],
        index=0
    )
    background = "none" if background.startswith("none") else background
    max_words = st.slider("Max words", min_value=20, max_value=500, value=200, step=10)

    st.divider()

    st.subheader("🥭 Font")
    fonts_dir = os.path.join("files", "fonts")
    available_fonts = sorted([
        f for f in os.listdir(fonts_dir)
        if f.lower().endswith((".ttf", ".otf"))
    ]) if os.path.exists(fonts_dir) else []
    if available_fonts:
        def clean_font_name(filename):
            name = os.path.splitext(filename)[0]
            name = name.replace("-", " ").replace("_", " ")
            for suffix in ["Regular", "Bold", "Italic", "Light", "Medium", "Thin", "Black", "SemiBold", "ExtraBold"]:
                name = name.replace(f" {suffix}", "")
            return name.strip()
        font_display_names = [clean_font_name(f) for f in available_fonts]
        default_font_name = "YanoneKaffeesatz-Regular.ttf"
        default_index = available_fonts.index(default_font_name) if default_font_name in available_fonts else 0
        selected_font_display = st.selectbox("Font", font_display_names, index=default_index)
        selected_font = available_fonts[font_display_names.index(selected_font_display)]
        font_path = os.path.join(fonts_dir, selected_font)
    else:
        st.warning("No fonts found in `files/fonts/` — default font will be used.")
        font_path = None

    st.divider()

    st.subheader("🍍 Dimensions")
    width  = st.number_input("Width (px)",  min_value=400, max_value=4000, value=1200, step=100)
    height = st.number_input("Height (px)", min_value=200, max_value=4000, value=700,  step=100)

# main app

st.header("1. Upload your CSV")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded **{len(df)} rows** and **{len(df.columns)} columns**.")
    st.dataframe(df.head(), hide_index=True)
    column = st.selectbox("Select the text column to use", df.columns.tolist())
    st.divider()
    st.header("2. Generate Word Cloud")
    if st.button("Generate 🥥", type="primary"):
        text_raw = " ".join(df[column].dropna().astype(str).tolist())
        text = normalize_text(text_raw)
        if not text.strip():
            st.error("No text found in the selected column.")
        else:
            with st.spinner("Generating word cloud..."):
                img_buf = build_wordcloud(
                    text=text,
                    width=int(width),
                    height=int(height),
                    background=background,
                    colormap=colormap,
                    max_words=max_words,
                    font_path=font_path,
                )
            st.image(img_buf, use_container_width=True)
            st.download_button(
                label="🍊 Download Word Cloud as PNG",
                data=img_buf,
                file_name="wordcloud.png",
                mime="image/png"
            )
else:
    st.info("Upload a CSV file to get started.")