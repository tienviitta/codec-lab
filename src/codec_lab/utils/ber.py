"""Bit error rate helpers (Monte Carlo and analytic baselines)."""

from __future__ import annotations

import numpy as np
from scipy.special import erfc


def ber(transmitted: np.ndarray, received: np.ndarray) -> float:
    """Empirical bit error rate between 0/1 arrays of the same shape."""
    t = np.asarray(transmitted).astype(np.int8, copy=False).ravel()
    r = np.asarray(received).astype(np.int8, copy=False).ravel()
    if t.shape != r.shape:
        raise ValueError("transmitted and received must have the same shape")
    n = t.size
    if n == 0:
        raise ValueError("empty arrays")
    return float(np.mean(t != r))


def ber_bpsk_awgn_theory(eb_n0_db: float | np.ndarray) -> np.ndarray:
    """Analytic average BER for coherent BPSK on AWGN.

    P_b = ½ erfc(√(E_b/N₀)) with E_b/N₀ linear.

    Uses ``scipy.special.erfc`` for numerical stability over a range of SNRs.
    """
    gamma = np.asarray(10.0 ** (np.asarray(eb_n0_db, dtype=np.float64) / 10.0))
    return 0.5 * erfc(np.sqrt(gamma))
