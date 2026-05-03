"""
Week 1 visualizations: uncoded BPSK BER vs E_b/N_0 and BSC bit-flip heatmap.

Uses NumPy, SciPy (analytic BER), and Matplotlib only.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from codec_lab.channels import awgn_llr_bpsk, bpsk_demod_hard, bsc_flip
from codec_lab.utils.ber import ber, ber_bpsk_awgn_theory


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _outputs_dir() -> Path:
    d = _repo_root() / "outputs" / "figures"
    d.mkdir(parents=True, exist_ok=True)
    return d


def plot_uncoded_bpsk_ber(
    eb_n0_db: np.ndarray,
    sim_ber: np.ndarray,
    theory_ber: np.ndarray,
    out_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.semilogy(eb_n0_db, theory_ber, "k-", label="Analytic (coherent BPSK)")
    ax.semilogy(eb_n0_db, sim_ber, "s-", label="Monte Carlo")
    ax.set_xlabel(r"$E_b/N_0$ (dB)")
    ax.set_ylabel("BER")
    ax.set_title("Uncoded BPSK over AWGN")
    ax.grid(True, which="both", ls=":", alpha=0.6)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_bsc_heatmap(
    bits: np.ndarray,
    received: np.ndarray,
    out_path: Path,
) -> None:
    err = (bits != received).astype(np.float64)
    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(err, aspect="auto", cmap="magma", vmin=0.0, vmax=1.0, interpolation="nearest")
    ax.set_xlabel("bit index")
    ax.set_ylabel("trial")
    ax.set_title("BSC: bit errors (1 = flip) vs index and trial")
    fig.colorbar(im, ax=ax, label="error")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def run_monte_carlo_bpsk(
    eb_n0_db: np.ndarray,
    n_bits: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    rates = np.empty_like(eb_n0_db, dtype=np.float64)
    tx = rng.integers(0, 2, size=n_bits, dtype=np.int8)
    for i, snr in enumerate(eb_n0_db):
        llr = awgn_llr_bpsk(tx, float(snr), rng=rng)
        rx = bpsk_demod_hard(llr)
        rates[i] = ber(tx, rx)
    return rates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=0, help="RNG seed")
    parser.add_argument(
        "--n-bits",
        type=int,
        default=200_000,
        help="Bits per SNR point for BPSK simulation",
    )
    parser.add_argument(
        "--bsc-trials",
        type=int,
        default=80,
        help="Rows in BSC heatmap",
    )
    parser.add_argument(
        "--bsc-width",
        type=int,
        default=200,
        help="Columns (bit index) in BSC heatmap",
    )
    parser.add_argument(
        "--bsc-p",
        type=float,
        default=0.08,
        help="BSC crossover probability",
    )
    args = parser.parse_args()
    out_dir = _outputs_dir()

    eb_n0_db = np.arange(0.0, 11.0, 1.0)
    theory = ber_bpsk_awgn_theory(eb_n0_db)
    sim = run_monte_carlo_bpsk(eb_n0_db, n_bits=args.n_bits, seed=args.seed)

    p_ber = out_dir / "week01_uncoded_bpsk_ber.png"
    plot_uncoded_bpsk_ber(eb_n0_db, sim, theory, p_ber)
    print(f"Wrote {p_ber}")

    rng = np.random.default_rng(args.seed + 1)
    bits = rng.integers(0, 2, size=(args.bsc_trials, args.bsc_width), dtype=np.int8)
    rec = np.empty_like(bits)
    for row in range(bits.shape[0]):
        rec[row] = bsc_flip(bits[row], args.bsc_p, rng=rng)

    p_bsc = out_dir / "week01_bsc_flip_heatmap.png"
    plot_bsc_heatmap(bits, rec, p_bsc)
    print(f"Wrote {p_bsc}")


if __name__ == "__main__":
    main()
