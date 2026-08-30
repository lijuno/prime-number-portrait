"""Image loading, color quantization, digit-grid encoding, and rendering."""

import os
import warnings

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from sklearn.cluster import KMeans

# Common TrueType fonts to try, in order, when the user does not supply one.
_FONT_CANDIDATES = (
    "DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
)


def load_image(path: str, resize_factor: int = 16) -> np.ndarray:
    """Load a photo as a small float RGB array in [0, 1].

    Applies EXIF rotation (portrait phone photos come out upright) and
    converts any mode (grayscale, RGBA, CMYK) to RGB. Each side is divided
    by ``resize_factor``; the resulting grid has one digit per pixel.
    """
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        width, height = img.size
        new_size = (max(1, width // resize_factor), max(1, height // resize_factor))
        img = img.resize(new_size, resample=Image.Resampling.LANCZOS)
        return np.asarray(img, dtype=np.float64) / 255.0


def fit_palette(image: np.ndarray, n_clusters: int = 10, random_state: int | None = None) -> KMeans:
    """Cluster the image's colors; each cluster becomes one digit."""
    if not 2 <= n_clusters <= 10:
        raise ValueError("n_clusters must be between 2 and 10: digits are 0-9")
    return KMeans(n_clusters=n_clusters, n_init=10, random_state=random_state).fit(
        image.reshape(-1, 3)
    )


def make_digit_grid(
    image: np.ndarray, kmeans: KMeans, rng: np.random.Generator | None = None
) -> np.ndarray:
    """Quantize ``image`` into a 2-D grid of digit labels.

    Repeated calls must produce different candidate grids for the prime
    search, so randomness enters twice: noise is added before quantization,
    and a few random cells are flipped to their second-nearest color (noise
    alone can be too weak to flip any label, which would make the search
    cycle through the same few numbers forever). Two digits are then
    constrained: the first must be nonzero (a leading zero would silently
    disappear from the integer, making the tested number differ from the
    depicted grid) and the last must be odd (an even number cannot be prime).
    """
    rng = rng if rng is not None else np.random.default_rng()
    noise = rng.random(image.shape) * (image.std() / 3)
    distances = kmeans.transform((image + noise).reshape(-1, 3))
    ranked = np.argsort(distances, axis=1)
    labels = ranked[:, 0].copy()
    flips = rng.integers(0, labels.size, size=int(rng.integers(1, 4)))
    labels[flips] = ranked[flips, 1]
    grid = labels.reshape(image.shape[:2])
    if grid[0, 0] == 0:
        grid[0, 0] = 1
    if grid[-1, -1] % 2 == 0:
        # Nudge to an adjacent odd label, staying inside [0, n_clusters).
        grid[-1, -1] += 1 if grid[-1, -1] + 1 < kmeans.n_clusters else -1
    return grid


def grid_to_number(grid: np.ndarray) -> tuple[int, str]:
    """Read the grid row-major as one large integer; also return its digits."""
    digits = "".join(str(int(d)) for d in grid.ravel())
    return int(digits), digits


def grid_to_color_image(grid: np.ndarray, kmeans: KMeans) -> np.ndarray:
    """Map each digit back to its cluster's color, giving a float RGB image."""
    return kmeans.cluster_centers_[grid]


def load_font(font_path: str | None, size: int) -> ImageFont.ImageFont:
    """Load ``font_path``, or the first available common font, or PIL's default."""
    for candidate in (font_path,) if font_path else _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    if font_path:
        raise OSError(f"could not load font {font_path!r}")
    warnings.warn(
        "No TrueType font found; using PIL's built-in bitmap font. "
        "Pass --font /path/to/font.ttf for nicer output.",
        stacklevel=2,
    )
    return ImageFont.load_default()


def render_portrait(
    grid: np.ndarray,
    kmeans: KMeans,
    font_path: str | None = None,
    cell_size: int = 32,
) -> Image.Image:
    """Render the digit grid as an image: quantized colors with the digits drawn on top."""
    colors = (grid_to_color_image(grid, kmeans) * 255).clip(0, 255).astype(np.uint8)
    height, width = grid.shape
    img = (
        Image.fromarray(colors)
        .resize((width * cell_size, height * cell_size), resample=Image.Resampling.NEAREST)
        .convert("RGBA")
    )
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(font_path, cell_size)
    for y, row in enumerate(grid):
        for x, digit in enumerate(row):
            xpos = x * cell_size + 1
            ypos = y * cell_size - cell_size / 8
            if digit == 1:
                # "1" is narrow; shift it toward the cell center.
                xpos += cell_size / 4
            draw.text(
                (xpos, ypos),
                str(digit),
                fill=(255, 255, 255, 64),
                stroke_width=1,
                stroke_fill=(0, 0, 0, 128),
                font=font,
            )
    return Image.alpha_composite(img, overlay)


def default_output_path(input_path: str) -> str:
    root, _ = os.path.splitext(input_path)
    return root + "-prime.png"
