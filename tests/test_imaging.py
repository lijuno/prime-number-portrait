import numpy as np
import pytest
from PIL import Image

from prime_portrait import (
    default_output_path,
    fit_palette,
    grid_to_color_image,
    grid_to_number,
    load_image,
    make_digit_grid,
    render_portrait,
)


@pytest.fixture(scope="module")
def image_and_palette():
    rng = np.random.default_rng(0)
    image = rng.random((12, 9, 3))
    return image, fit_palette(image, n_clusters=10, random_state=0)


def test_grid_to_number_matches_digits():
    grid = np.array([[1, 2, 3], [4, 5, 7]])
    number, digits = grid_to_number(grid)
    assert digits == "123457"
    assert number == 123457


def test_digit_grid_constraints(image_and_palette):
    image, kmeans = image_and_palette
    rng = np.random.default_rng(1)
    for _ in range(20):
        grid = make_digit_grid(image, kmeans, rng)
        assert grid.shape == image.shape[:2]
        assert grid.min() >= 0 and grid.max() <= 9
        assert grid[0, 0] != 0, "leading digit must be nonzero"
        assert grid[-1, -1] % 2 == 1, "last digit must be odd"
        number, digits = grid_to_number(grid)
        assert len(digits) == grid.size, "no digits may be lost to leading zeros"
        assert len(str(number)) == len(digits)


def test_digit_grid_last_label_stays_in_range():
    # With few clusters the odd-nudge must not walk off the label range.
    rng = np.random.default_rng(2)
    image = rng.random((6, 6, 3))
    kmeans = fit_palette(image, n_clusters=2, random_state=0)
    for _ in range(20):
        grid = make_digit_grid(image, kmeans, rng)
        assert grid.max() < 2


def test_fit_palette_rejects_bad_cluster_counts():
    image = np.zeros((4, 4, 3))
    with pytest.raises(ValueError):
        fit_palette(image, n_clusters=11)
    with pytest.raises(ValueError):
        fit_palette(image, n_clusters=1)


def test_grid_to_color_image_shape(image_and_palette):
    image, kmeans = image_and_palette
    grid = make_digit_grid(image, kmeans, np.random.default_rng(3))
    colors = grid_to_color_image(grid, kmeans)
    assert colors.shape == image.shape


def test_load_image_handles_odd_modes(tmp_path):
    for mode, name in [("L", "gray.png"), ("RGBA", "alpha.png"), ("RGB", "rgb.jpg")]:
        path = tmp_path / name
        Image.new(mode, (64, 48), 128 if mode == "L" else None).save(path)
        loaded = load_image(str(path), resize_factor=4)
        assert loaded.shape == (12, 16, 3)
        assert loaded.dtype == np.float64
        assert 0.0 <= loaded.min() and loaded.max() <= 1.0


def test_render_portrait_produces_image(image_and_palette, tmp_path):
    image, kmeans = image_and_palette
    grid = make_digit_grid(image, kmeans, np.random.default_rng(4))
    portrait = render_portrait(grid, kmeans, cell_size=16)
    assert portrait.size == (grid.shape[1] * 16, grid.shape[0] * 16)
    portrait.save(tmp_path / "out.png")


def test_default_output_path():
    assert default_output_path("photo.jpg") == "photo-prime.png"
    assert default_output_path("/a/b.dir/photo.v2.jpeg") == "/a/b.dir/photo.v2-prime.png"
    assert default_output_path("noext") == "noext-prime.png"
