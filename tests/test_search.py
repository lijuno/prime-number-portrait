import numpy as np

from prime_portrait import fit_palette, is_probable_prime, search_prime_portrait
from prime_portrait.search import check_grid


def test_check_grid_detects_prime():
    grid = np.array([[1, 0], [0, 9]])  # 1009 is prime
    result = check_grid(grid)
    assert result is not None
    assert result[0] == 1009
    assert check_grid(np.array([[1, 0], [0, 8]])) is None  # 1008 is composite


def test_end_to_end_search_finds_verified_prime():
    # A tiny 6x6 grid (36 digits) keeps this test fast.
    rng = np.random.default_rng(5)
    image = rng.random((6, 6, 3))
    kmeans = fit_palette(image, n_clusters=10, random_state=5)
    result = search_prime_portrait(
        image, kmeans, threads=2, max_attempts=20000, seed=5, progress=None
    )
    assert result is not None
    assert len(result.digits) == 36
    assert int(result.digits) == result.number
    # Independent high-confidence confirmation of the reported prime.
    assert is_probable_prime(result.number, rounds=100)
