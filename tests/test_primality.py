from prime_portrait import is_probable_prime

KNOWN_PRIMES = [2, 3, 5, 7, 97, 7919, 104729, 2**31 - 1, 2**61 - 1]
KNOWN_COMPOSITES = [0, 1, 4, 100, 7917, 2**31 + 1]
# Carmichael numbers fool Fermat tests but not Miller-Rabin.
CARMICHAEL = [561, 1105, 1729, 41041, 825265]


def test_known_primes():
    for n in KNOWN_PRIMES:
        assert is_probable_prime(n), n


def test_known_composites():
    for n in KNOWN_COMPOSITES:
        assert not is_probable_prime(n), n


def test_carmichael_numbers_rejected():
    for n in CARMICHAEL:
        assert not is_probable_prime(n), n


def test_negative_and_small():
    assert not is_probable_prime(-7)
    assert not is_probable_prime(1)
    assert is_probable_prime(2)


def test_large_known_prime():
    # 2^127 - 1 is a Mersenne prime.
    assert is_probable_prime(2**127 - 1)
    assert not is_probable_prime((2**127 - 1) * (2**61 - 1))
