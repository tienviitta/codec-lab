"""BER utilities and analytic BPSK baseline."""

import numpy as np
import pytest
from scipy.special import erfc

from codec_lab.utils.ber import ber, ber_bpsk_awgn_theory


def test_ber_counts_errors() -> None:
    assert ber(np.array([0, 1, 0]), np.array([0, 0, 0])) == pytest.approx(1.0 / 3.0)


def test_ber_bpsk_at_0_db() -> None:
    # P_b = 0.5 * erfc(1) at Eb/N0 = 1 (0 dB)
    got = ber_bpsk_awgn_theory(0.0)
    want = 0.5 * float(erfc(1.0))
    assert float(got) == pytest.approx(want, rel=0, abs=1e-12)


def test_ber_requires_same_shape() -> None:
    with pytest.raises(ValueError):
        ber(np.zeros(3), np.zeros(4))
