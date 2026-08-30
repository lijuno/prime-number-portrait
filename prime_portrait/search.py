"""Randomized multiprocess search for a digit grid that encodes a prime."""

import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from multiprocessing import Pool

import numpy as np
from sklearn.cluster import KMeans

from .imaging import grid_to_number, make_digit_grid
from .primality import is_probable_prime


@dataclass
class PrimePortrait:
    number: int
    digits: str
    grid: np.ndarray
    attempts: int
    seconds: float

    def digit_rows(self) -> list[str]:
        return ["".join(str(int(d)) for d in row) for row in self.grid]


def check_grid(grid: np.ndarray, trials: int = 40):
    """Worker task: return (number, grid) if the grid encodes a probable prime."""
    number, _ = grid_to_number(grid)
    if is_probable_prime(number, rounds=trials):
        return number, grid
    return None


def search_prime_portrait(
    image: np.ndarray,
    kmeans: KMeans,
    *,
    threads: int | None = None,
    trials: int = 40,
    max_attempts: int = 1_000_000,
    seed: int | None = None,
    log_every: int = 50,
    progress: Callable[[str], None] | None = print,
) -> PrimePortrait | None:
    """Try noisy quantizations of ``image`` until one reads as a prime.

    Returns a :class:`PrimePortrait`, or None if ``max_attempts`` candidates
    were all composite (astronomically unlikely for reasonable grid sizes).
    """
    rng = np.random.default_rng(seed)
    candidates = (make_digit_grid(image, kmeans, rng) for _ in range(max_attempts))
    start = time.perf_counter()
    checked = 0
    with Pool(threads) as pool:
        for result in pool.imap_unordered(partial(check_grid, trials=trials), candidates):
            checked += 1
            if result is not None:
                number, grid = result
                elapsed = time.perf_counter() - start
                _, digits = grid_to_number(grid)
                return PrimePortrait(number, digits, grid, checked, elapsed)
            if progress is not None and checked % log_every == 0:
                elapsed = time.perf_counter() - start
                progress(
                    f"Checked {checked} candidates in {elapsed:.1f}s "
                    f"({1000 * elapsed / checked:.0f} ms per candidate)"
                )
    return None
