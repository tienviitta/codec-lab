"""AWGN variance and high-SNR hard decisions."""

import numpy as np

from codec_lab.channels import (
    awgn_llr_bpsk,
    awgn_noise_variance_bpsk,
    awgn_receive_bpsk,
    bpsk_demod_hard,
    bpsk_llr_from_observation,
    bpsk_modulate,
)


def test_noise_variance_matches_eb_n0_definition() -> None:
    eb_n0_db = np.array([0.0, 3.0, 10.0])
    sigma2 = awgn_noise_variance_bpsk(eb_n0_db)
    gamma = 10.0 ** (eb_n0_db / 10.0)
    np.testing.assert_allclose(sigma2, 1.0 / (2.0 * gamma))


def test_bpsk_modulate_is_complex_on_real_axis() -> None:
    bits = np.array([0, 1, 0, 1], dtype=np.int8)
    s = bpsk_modulate(bits)
    assert np.iscomplexobj(s)
    np.testing.assert_allclose(np.imag(s), 0.0)
    np.testing.assert_allclose(np.real(s), [1.0, -1.0, 1.0, -1.0])


def test_awgn_receive_has_circular_noise() -> None:
    rng = np.random.default_rng(0)
    bits = np.zeros(50_000, dtype=np.int8)
    y, llr = awgn_receive_bpsk(bits, eb_n0_db=3.0, rng=rng)
    assert y.dtype == np.complex128
    # Q branch should be active (not identically zero)
    assert float(np.mean(np.abs(np.imag(y)) > 0)) > 0.99


def test_awgn_hard_decisions_perfect_at_high_snr() -> None:
    rng = np.random.default_rng(42)
    bits = rng.integers(0, 2, size=5000, dtype=np.int8)
    llr = awgn_llr_bpsk(bits, eb_n0_db=30.0, rng=rng)
    rx = bpsk_demod_hard(llr)
    assert np.array_equal(rx, bits)


def test_awgn_receive_matches_llr_path() -> None:
    bits = np.random.default_rng(1).integers(0, 2, size=1000, dtype=np.int8)
    rng = np.random.default_rng(7)
    llr_a = awgn_llr_bpsk(bits, eb_n0_db=5.0, rng=rng)
    rng = np.random.default_rng(7)
    _y, llr_b = awgn_receive_bpsk(bits, eb_n0_db=5.0, rng=rng)
    np.testing.assert_allclose(llr_a, llr_b)


def test_llr_arrays_are_real_float64() -> None:
    rng = np.random.default_rng(99)
    bits = rng.integers(0, 2, size=200, dtype=np.int8)
    llr = awgn_llr_bpsk(bits, eb_n0_db=4.0, rng=rng)
    assert llr.dtype == np.float64
    assert not np.iscomplexobj(llr)
    y, llr2 = awgn_receive_bpsk(bits, eb_n0_db=4.0, rng=np.random.default_rng(100))
    assert y.dtype == np.complex128
    assert llr2.dtype == np.float64
    assert not np.iscomplexobj(llr2)


def test_llr_matches_log_likelihood_ratio_for_circular_gaussian() -> None:
    """LLR = log p(y|s=+1) - log p(y|s=-1) with independent I/Q noise N(0, σ²)."""
    rng = np.random.default_rng(123)
    sigma2 = 0.17
    sigma = np.sqrt(sigma2)
    # 2D Gaussian log-density up to same additive constant for both hypotheses
    y = rng.standard_normal(500) + 1j * rng.standard_normal(500)
    y = (y * sigma).astype(np.complex128)  # circular with per-dim variance sigma2

    s0 = 1.0 + 0.0j
    s1 = -1.0 + 0.0j
    logp0 = -((np.real(y - s0) ** 2 + np.imag(y - s0) ** 2) / (2.0 * sigma2))
    logp1 = -((np.real(y - s1) ** 2 + np.imag(y - s1) ** 2) / (2.0 * sigma2))
    expected = logp0 - logp1
    got = bpsk_llr_from_observation(y, sigma2)
    np.testing.assert_allclose(got, expected, rtol=0, atol=1e-14)
