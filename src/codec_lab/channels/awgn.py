"""AWGN channel for BPSK on complex baseband (I/Q), extensible to higher-order modulations.

Observations ``y`` are complex (I/Q). **LLRs are always real-valued**: for each
binary hypothesis pair, log(p(y|b=0)/p(y|b=1)) is a real scalar (ratio of
positive densities). For BPSK on the I axis with circular Gaussian noise,
that statistic reduces to ``2·Re(y)/σ²``; the imaginary part of ``y`` affects
|y−s|² but drops out of the difference between the two hypotheses in the
same way as the constant normalization.

**Higher-order constellations (QPSK, QAM, …):** each complex receive sample
still yields **only real LLRs**, but typically **one real scalar per coded bit**
that labels that symbol (e.g. 16-QAM → four LLRs per ``y``, often written as
a real vector ``[L₀, L₁, L₂, L₃]``). Those values differ across bit indices
because each bit’s 0/1 hypothesis partitions the constellation differently.
They are not complex LLRs; soft demappers may use max-log approximations over
neighbors, but each output channel remains real.
"""

from __future__ import annotations

import numpy as np

_TWO = 2.0


def awgn_noise_variance_bpsk(eb_n0_db: float | np.ndarray) -> np.ndarray:
    """Variance σ² of each real noise component (I and Q) for unit-energy BPSK.

    Symbols are s ∈ {+1+0j, −1+0j} so E_b = E[|s|²] = 1.
    Complex circular AWGN n = n_I + j n_Q with n_I, n_Q ∼ N(0, σ²) i.i.d.
    For ML detection on the real axis, Re(y) = s + n_I and E_b/N₀ = 1/(2σ²),
    hence σ² = 1 / (2 · (E_b/N₀)_linear).
    """
    eb_n0 = np.asarray(10.0 ** (np.asarray(eb_n0_db, dtype=np.float64) / 10.0))
    return 1.0 / (_TWO * eb_n0)


def bpsk_modulate(bits: np.ndarray) -> np.ndarray:
    """Map bits to complex antipodal symbols on the real (I) axis.

    bit 0 → +1+0j, bit 1 → −1+0j. Output dtype ``numpy.complex128``.
    """
    b = np.asarray(bits).astype(np.int8, copy=False)
    s_real = (1 - 2 * b).astype(np.float64)
    return s_real.astype(np.complex128)


def bpsk_llr_from_observation(y: np.ndarray, sigma2_per_dimension: float) -> np.ndarray:
    """Real-valued LLR log(p(y|b=0)/p(y|b=1)) for BPSK on the I axis under circular Gaussian noise.

    ``y`` may be complex; the returned array has dtype ``numpy.float64`` (never complex).

    With independent I/Q noise of variance σ² per dimension,
    LLR = (|y+1|² − |y−1|²) / (2σ²) = 2·Re(y)/σ².
    """
    sigma2 = float(sigma2_per_dimension)
    llr = (2.0 / sigma2) * np.real(np.asarray(y, dtype=np.complex128))
    return np.asarray(llr, dtype=np.float64)


def awgn_receive_bpsk(
    bits: np.ndarray,
    eb_n0_db: float,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Complex baseband receive samples and real LLRs (same channel as :func:`awgn_llr_bpsk`).

    Returns
    -------
    y
        Complex received array ``s + n``.
    llr
        Real LLRs suitable for :func:`bpsk_demod_hard`.
    """
    if rng is None:
        rng = np.random.default_rng()
    s = bpsk_modulate(bits)
    sigma2 = float(awgn_noise_variance_bpsk(eb_n0_db))
    sigma = np.sqrt(sigma2)
    shape = s.shape
    n_i = rng.normal(0.0, sigma, size=shape)
    n_q = rng.normal(0.0, sigma, size=shape)
    y = s + n_i.astype(np.float64) + 1j * n_q.astype(np.float64)
    return y, bpsk_llr_from_observation(y, sigma2)


def awgn_llr_bpsk(
    bits: np.ndarray,
    eb_n0_db: float,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Transmit bits over complex AWGN; return real LLRs log(p(y|b=0)/p(y|b=1)).

    Mapping: bit 0 → s = +1+0j, bit 1 → s = −1+0j.

    Noise is circular: y = s + n_I + j·n_Q with n_I, n_Q ∼ N(0, σ²), same σ²
    as :func:`awgn_noise_variance_bpsk`.

    Parameters
    ----------
    bits
        Array of 0/1 (integer or bool), any shape.
    eb_n0_db
        E_b/N₀ in dB.
    rng
        Optional ``numpy.random.Generator``; default ``numpy.random.default_rng()``.
    """
    _, llr = awgn_receive_bpsk(bits, eb_n0_db, rng=rng)
    return llr


def bpsk_demod_hard(llr: np.ndarray) -> np.ndarray:
    """Hard decisions from LLR; real part is used if ``llr`` is complex."""
    x = np.asarray(llr)
    if np.iscomplexobj(x):
        x = np.real(x)
    return (x < 0).astype(np.int8)
