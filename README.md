# codec-lab

Hands-on **forward error correction (FEC)** and **error-correcting codes (ECC)** for learning—oriented toward **wireless PHY** (5G/NR and beyond). This repo is the **Python workbench**: small, testable building blocks in `src/codec_lab`, **Jupyter** notebooks for exploration and visuals, and room for animations and publishable assets.

Primary references: **Todd K. Moon** (*Error Correction Coding*, lab-oriented spine), **David MacKay** (*ITILA*, intuition and message passing), **Lin & Costello** / **Lin & Li** (deeper lookup). A concrete week-by-week checklist lives in [`CHECKLIST.md`](CHECKLIST.md); a longer bibliography and visualization notes live in your separate study document (O’Reilly, IEEE Xplore, arXiv, Sionna tutorials, etc.).

---

## Design choices (how this repo is meant to be used)

| Topic | Decision |
|--------|-----------|
| **First coded FEC** | **Polar codes at small block length** (e.g. \(N=8\) or \(16\)), successive cancellation (SC) first—strong visuals (frozen bits, tree) before LDPC belief-propagation plumbing. Hamming, RS, convolutional, toy LDPC, NR-style LDPC/rate matching, larger polar (SCL, CRC-aided), and HARQ follow the broader study plan. |
| **Workflow** | **Both**: **Jupyter** for curves, experiments, and animations; **pytest** for primitives (channels, encoders, decoders) with golden vectors and regressions. |
| **Dependencies** | **Default stack**: NumPy, SciPy, Matplotlib (see `pyproject.toml`). **Optional later**: e.g. `networkx` (Tanner graphs), **CommPy** / **pyldpc** (LDPC cross-checks), **Sionna** (NR-style tutorials and baselines), high-performance **ldpc** (PyPI) for benchmarking—add as optional extras only when a notebook or experiment needs them. |
| **Time budget** | Roughly **6–8 hours/week** study + implementation; adjust as needed. |

---

## Quickstart ([uv](https://docs.astral.sh/uv/))

Requires **Python ≥3.12**.

Implementation stack for this repo: **NumPy** (arrays, RNG), **SciPy** (e.g. `erfc` for analytic BER), **Matplotlib** (figures and animations).

```bash
uv sync --all-extras    # core + dev (pytest, ruff) + Jupyter
uv run pytest
uv run ruff check src tests
uv run jupyter lab      # optional: explore notebooks once added
```

### Run tests (step by step)

1. From the repo root, create/update the environment: `uv sync --extra dev` (or `uv sync --all-extras` if you also want Jupyter).
2. Run the full suite: `uv run pytest` (quiet by default; use `uv run pytest -v` for per-test names).
3. Run a subset, e.g. only channels: `uv run pytest tests/test_channels_awgn.py tests/test_channels_bsc.py`.
4. Optional static checks: `uv run ruff check src tests`.

Tests live under `tests/` and mirror packages under `src/codec_lab/` (e.g. `channels/` → `test_channels_*.py`, `utils/ber.py` → `test_ber.py`).

### Run Week 1 visuals (uncoded BPSK + BSC heatmap)

1. Ensure deps are installed: `uv sync` (Matplotlib is already a core dependency).
2. Generate PNGs into `outputs/figures/`:

   ```bash
   uv run python experiments/week01_visuals.py
   ```

   **VS Code / Cursor:** open **Run and Debug**, choose **“Python: week01_visuals”** (or **“… (fast preview)”** for smaller `--n-bits` / heatmap). Ensure the workspace interpreter is `.venv` (e.g. **Python: Select Interpreter** → `./.venv/Scripts/python.exe` on Windows) and the **Python** / **debugpy** extension is enabled.

3. Optional CLI knobs: `--n-bits 500000` (more stable Monte Carlo BER), `--seed 1`, `--bsc-p 0.1`, `--bsc-trials 100`, `--bsc-width 300`.

You should see `week01_uncoded_bpsk_ber.png` and `week01_bsc_flip_heatmap.png` under `outputs/figures/`.

### Adding new implementations and visuals

1. **Library code** under `src/codec_lab/<area>/` (small modules, clear docstrings). Re-export public APIs from `codec_lab.<area>.__init__` when it helps imports.
2. **Tests** in `tests/test_<area>_<topic>.py`: use `numpy.random.Generator` with fixed seeds for reproducibility; compare to **SciPy** closed forms or golden vectors when possible.
3. **Figures or sweeps** as scripts under `experiments/` (e.g. `experiments/week02_….py`): only **NumPy / SciPy / Matplotlib** and imports from `codec_lab`; write artifacts to `outputs/` so git stays clean.
4. **Notebooks** (optional): thin wrappers that call the same functions as tests/scripts for interactive exploration.

Generated figures and videos should go under **`outputs/`** (gitignored). Curate finals for posts or a separate site into **`publish/`** when you introduce that layout.

---

## Layout (current and planned)

This workbench is **this** repository (`codec-lab`). An optional **second repo** (e.g. Next.js portfolio) can later consume curated assets from `publish/` or GitHub Releases; you do not need that on day one.

```
codec-lab/
├── README.md
├── CHECKLIST.md          # week-by-week reading / coding / visuals
├── pyproject.toml
├── uv.lock               # after uv lock/sync
├── src/
│   └── codec_lab/        # importable package (channels, utils, polar, …)
├── tests/                # pytest
├── notebooks/            # Jupyter (to be added)
├── experiments/          # e.g. week01_visuals.py → outputs/figures/
├── .vscode/
│   └── launch.json       # shared debug configs (local settings.json ignored)
├── animations/           # matplotlib / export scripts (optional)
├── outputs/              # generated; not committed
├── publish/              # optional curated assets + post drafts
└── docs/                 # optional notes, references, index
```

Suggested **notebook** order (aligned with checklist + “polar first” for first codec implementation):

| Notebook | Focus |
|----------|--------|
| `01_uncoded_ber.ipynb` | AWGN/BSC, BER vs Eb/N0 |
| `02_syndromes_linear_block.ipynb` | \(G\), \(H\), syndrome decoding (optional if you want algebra before polar) |
| `03_polar_small_n.ipynb` | First **coded** FEC: encode + SC decode, frozen bits, visuals |
| Later | Hamming, CRC, RS, Viterbi, LDPC BP, rate matching, polar SCL/CRC, HARQ (see `CHECKLIST.md`) |

**Naming**: notebooks `NN_topic.ipynb`, experiments `exp_<topic>_<variant>.py`, animations `anim_<topic>_<what>.py`, post drafts `YYYY-MM-DD_<slug>.md`.

---

## Implementation trajectory (PHY-minded)

1. **Channels and metrics** — AWGN, BSC, BER/BLER helpers (`codec_lab.channels`, `codec_lab.utils`).
2. **Polar (small \(N\))** — encoder, bit-reversal / Kronecker structure, SC decoder, tests; then notebook + tree or LLR-flow animation.
3. **Continue** the linear → Hamming → CRC → RS → convolutional → **LDPC** → rate matching → **advanced polar** → HARQ arc from your plan, reusing the same patterns: library code + tests + one flagship visual per milestone.

For **NR realism**, use tutorials and APIs from **Sionna** and 3GPP-oriented papers when you reach LDPC/rate matching/polar at larger \(N\); keep your own toy implementations for understanding.

---

## Optional reference software (add when needed)

| Tool | Use |
|------|-----|
| [CommPy](https://github.com/veeresht/CommPy) | Readable NumPy implementations; Viterbi, LDPC BP docs |
| [pyldpc](https://github.com/hichamjananih/pyldpc) | LDPC matrices and BP cross-checks |
| [Sionna](https://nvlabs.github.io/sionna/) | 5G-style polar/LDPC/rate matching notebooks |
| [ldpc](https://pypi.org/project/ldpc/) (C++ core) | Benchmarking after educational decoders |
| **libcorrect** (C) | Later RS/Viterbi baseline outside Python |

Golden tests: save small `.npz` fixtures from a reference once, assert your decoder matches within tolerance.

---

## Visuals and animations

- Prefer **Matplotlib** (`FuncAnimation`) for MP4/GIF; use **ffmpeg** on PATH for H.264 export where needed.
- Put shared **rcParams**, output paths, and RNG seeds in something like `codec_lab.utils.render` when animation scripts multiply.
- Aim for **one strong animation per topic** (e.g. polar SC tree, LDPC message passing, trellis survivors) for Substack or portfolio reuse.
- Large binaries: prefer **Git LFS** or keep only curated clips under `publish/` / post media.

---

## Publishing (optional, later)

- **Scratch**: `outputs/` (ignored).
- **Curated**: `publish/assets/` and `publish/posts/` plus optional `publish/index.json` (slug, title, tags, asset paths) for a static site or hand-off to a separate repo.
- **GitHub Releases** can ship a zip of `publish/` for a portfolio site build to download—avoids bloating main history.

---

## License

See [`LICENSE`](LICENSE).
