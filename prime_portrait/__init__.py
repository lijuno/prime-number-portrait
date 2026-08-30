"""Turn photos into prime number portraits.

A prime portrait is an image quantized to at most ten colors, where each
color is a digit 0-9; read row by row, the digits form one huge integer
that is (very probably) prime.
"""

from .imaging import (
    default_output_path,
    fit_palette,
    grid_to_color_image,
    grid_to_number,
    load_image,
    make_digit_grid,
    render_portrait,
)
from .primality import is_probable_prime
from .search import PrimePortrait, search_prime_portrait

__version__ = "1.0.0"

__all__ = [
    "PrimePortrait",
    "default_output_path",
    "fit_palette",
    "grid_to_color_image",
    "grid_to_number",
    "is_probable_prime",
    "load_image",
    "make_digit_grid",
    "render_portrait",
    "search_prime_portrait",
    "__version__",
]
