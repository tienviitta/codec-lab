"""Binary symmetric channel (memoryless bit flips)."""

from __future__ import annotations

import numpy as np


def bsc_flip(
    bits: np.ndarray,
    p: float,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Return received bits after independent flips with probability ``p``.

    Parameters
    ----------
    bits
        Array of 0/1, any shape.
    p
        Crossover probability in (0, 1). ``p == 0`` is allowed (identity).
    rng
        Optional ``numpy.random.Generator``.
    """
    if rng is None:
        rng = np.random.default_rng()
    if not 0.0 <= p <= 1.0:
        raise ValueError("p must be in [0, 1]")
    b = np.asarray(bits).astype(np.int8, copy=False)
    flip = rng.random(b.shape) < p
    out = np.bitwise_xor(b, flip.astype(np.int8))
    return out
