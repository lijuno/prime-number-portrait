"""Probabilistic primality testing via the Miller-Rabin algorithm."""

import random

# Trial division by small primes rejects most composites before the
# expensive modular exponentiation rounds.
_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_probable_prime(n: int, rounds: int = 40, rng: random.Random | None = None) -> bool:
    """Return True if ``n`` is probably prime, False if it is certainly composite.

    Runs ``rounds`` iterations of Miller-Rabin; the probability that a
    composite number passes is at most 4**-rounds (about 1e-24 for the
    default 40 rounds).
    """
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False

    # Write n - 1 as 2**s * d with d odd.
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    rng = rng if rng is not None else random
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True
