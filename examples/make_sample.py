"""Generate the synthetic sample image used in the README.

A heart on a diagonal gradient: recognizable even on a small digit grid,
and free of any licensing or privacy concerns.

Usage: python examples/make_sample.py
"""

from pathlib import Path

import numpy as np
from PIL import Image

WIDTH, HEIGHT = 360, 360


def heart_mask(width: int, height: int) -> np.ndarray:
    # Implicit heart curve: (x^2 + y^2 - 1)^3 - x^2 y^3 <= 0
    x = np.linspace(-1.4, 1.4, width)
    y = np.linspace(1.5, -1.3, height)
    xx, yy = np.meshgrid(x, y)
    return (xx**2 + yy**2 - 1) ** 3 - xx**2 * yy**3 <= 0


def main() -> None:
    xx, yy = np.meshgrid(np.linspace(0, 1, WIDTH), np.linspace(0, 1, HEIGHT))
    # Teal-to-navy diagonal gradient background.
    image = np.stack(
        [0.15 + 0.2 * xx, 0.45 - 0.25 * yy, 0.55 + 0.3 * yy * (1 - xx)], axis=-1
    )
    mask = heart_mask(WIDTH, HEIGHT)
    # Crimson heart with a vertical shading gradient.
    shade = 0.75 + 0.25 * yy
    for channel, value in enumerate([0.85, 0.15, 0.25]):
        image[..., channel] = np.where(mask, value * shade, image[..., channel])

    out = Path(__file__).parent / "sample.png"
    Image.fromarray((image.clip(0, 1) * 255).astype(np.uint8)).save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
