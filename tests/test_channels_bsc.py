"""BSC flip channel."""

import numpy as np

from codec_lab.channels import bsc_flip


def test_bsc_zero_probability_is_identity() -> None:
    rng = np.random.default_rng(0)
    bits = rng.integers(0, 2, size=1000, dtype=np.int8)
    out = bsc_flip(bits, 0.0, rng=rng)
    assert np.array_equal(out, bits)


def test_bsc_crossover_roughly_p() -> None:
    rng = np.random.default_rng(1)
    p = 0.11
    n = 200_000
    bits = rng.integers(0, 2, size=n, dtype=np.int8)
    out = bsc_flip(bits, p, rng=rng)
    empirical = float(np.mean(bits != out))
    assert abs(empirical - p) < 0.005
