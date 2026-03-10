"""
Generates a word cloud visualization from a CSV file.
"""
# imports
import argparse
import os
import unicodedata
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# function to remove accents and try to standardize words
def normalize_text(text: str) -> str:
    text = text.lower()
    nfd = unicodedata.normalize("NFD", text)
    return "".join(i for i in nfd if unicodedata.category(i) != "Mn")

#function to load csv and extract text from column
def load_csv(filepath: str, column: str = None) -> str:
    df = pd.read_csv(filepath)
    target_col = df.columns[0]
    text = " ".join(df[target_col].dropna().astype(str).tolist())
    text = normalize_text(text)
    return text


def generate_wordcloud(
    text: str,
    output: str = "wordcloud.png",
    width: int = 1200,
    height: int = 700,
    background: str = "none",
    colormap: str = "inferno",
    max_words: int = 200,
    use_stopwords: bool = True,
    title: str = None,
    font_path: str = os.path.join("files", "fonts", "YanoneKaffeesatz-Regular.ttf"),
):

    transparent = background.lower() == "none"
    bg_color = None if transparent else background
    stopwords = STOPWORDS if use_stopwords else set()

    wc = WordCloud(
        width=width,
        height=height,
        background_color=bg_color,
        mode="RGBA" if transparent else "RGB",
        colormap=colormap,
        max_words=max_words,
        stopwords=stopwords,
        collocations=True,
        prefer_horizontal=0.85,
        margin=10,
        font_path=font_path if font_path and os.path.exists(font_path) else None,
    ).generate(text)

    fig_height = height / 100
    if title:
        fig_height += 1
    fig, ax = plt.subplots(figsize=(width / 100, fig_height), dpi=100)
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    if title:
        fig.suptitle(title, fontsize=22, fontweight="bold", y=0.98)
    plt.tight_layout(pad=0)
    plt.savefig(output, bbox_inches="tight", dpi=150, transparent=transparent)
    plt.close()
    print(f"Word cloud saved to: {output}")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a word cloud from a CSV file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", default=os.path.join("files", "raw", "wordcloud_1.csv"), metavar="FILE", help="Path to the CSV input file (default: .\\files\\raw\\wordcloud_1.csv)")
    parser.add_argument("--column", default=None, metavar="NAME", help="Column name to use (default: first column)")
    parser.add_argument("--output", default=os.path.join("files", "output", "wordcloud.png"), metavar="FILE", help="Output image filename (default: .\\files\\output\\wordcloud.png)")
    parser.add_argument("--width", type=int, default=1200, help="Image width in pixels (default: 1200)")
    parser.add_argument("--height", type=int, default=700, help="Image height in pixels (default: 700)")
    parser.add_argument("--background", default="none", metavar="COLOR", help="Background color, use 'none' for transparent (default: none)")
    parser.add_argument("--colormap", default="inferno", metavar="NAME", help="Matplotlib colormap (default: inferno)")
    parser.add_argument("--max-words", type=int, default=200, help="Max words to display (default: 200)")
    parser.add_argument("--no-stopwords", action="store_true", help="Disable stopword removal")
    parser.add_argument("--title", default=None, metavar="TEXT", help="Optional title for the image")
    parser.add_argument("--font", default=os.path.join("files", "fonts", "YanoneKaffeesatz-Regular.ttf"), metavar="FILE", help="Path to a .ttf or .otf font file (default: .\\files\\fonts\\YanoneKaffeesatz-Regular.ttf)")
    return parser.parse_args()


def main():
    args = parse_args()

    text = load_csv(args.input, args.column)

    generate_wordcloud(
        text=text,
        output=args.output,
        width=args.width,
        height=args.height,
        background=args.background,
        colormap=args.colormap,
        max_words=args.max_words,
        use_stopwords=not args.no_stopwords,
        title=args.title,
        font_path=args.font,
    )


if __name__ == "__main__":
    main()