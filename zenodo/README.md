# Study05 – DOFT Internal Layers Simulator

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

This repository contains the computational framework and paper materials for:

> **Coherence Scaling in Hierarchical Oscillator Networks: Power-Law Decay, Memory Overhead, and Topological Constraints with Parallels to Disordered Condensed Matter**
> 
> C. Agostino (2026)

The code implements the Delayed Oscillator Field Theory (DOFT) framework: a four-stage recursive pipeline (Ola1–Ola4) for exploring coherence scaling in networks of coupled oscillators with internal memory.

---

## Repository Layout

```
study05-doft/
├── paper/                        # PAPER (self-contained, compiles directly)
│   ├── main.tex                  # LaTeX source
│   ├── main.bib                  # Bibliography
│   ├── figures/                  # All figures (PDF/PNG)
│   │   ├── Figure_1_Coherence_Scaling.png
│   │   ├── Figure_2_Memory_Overhead.png
│   │   ├── ...
│   │   └── Appendix_G_Critical_Dynamics.png
│   └── data/                     # Paper data (consolidated)
│       ├── paper_metrics_all.csv      # All promoted entities with metrics
│       ├── paper_metrics_manifest.json # Run metadata (configs, dates, versions)
│       └── paper_metrics_summary.json  # Statistical summary by ola
│
├── src/                          # MODEL SOURCE CODE
│   ├── olar/                     # Pipeline, explorer, sweep
│   ├── core/                     # Catalog, taxonomy, promotion
│   └── ola1/                     # Ola1 sweep and assembly
│
├── config/                       # CONFIGURATION FILES
│   ├── ola1_paper/               # Ola1 configs (engine, layers, selection)
│   ├── ola2_paper/               # Ola2 run sequence
│   ├── ola3_paper/               # Ola3 run sequence
│   └── ola4_paper/               # Ola4 run sequence
│
├── data/                         # MODEL DATA
│   └── processed/
│       └── ola1_paper/
│           ├── simple_blocks_canonical.json
│           ├── dof_dna_catalog_by_block_id.csv
│           └── promoted/         # Ola1 blocks (optional)
│               ├── simple_blocks.json
│               └── dof_dna_catalog.csv
│
├── scripts/                      # Utility scripts
│   ├── paper_build.py            # Generate all paper outputs
│   ├── paper_metrics_pack.py     # Consolidate metrics
│   └── paper_figures_final.py    # Generate figures
│
├── README.md                     # This file
└── LICENSE                       # MIT License
```

---

## Quick Start

### 1. Compile the Paper (Fastest)

The `paper/` directory is self-contained. To compile:

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

All figures and data are included—no code execution required.

### 2. Run the Full Model

See [Running the Model](#running-the-model) below.

---

## Computational Requirements

### Reference Hardware

| Component | Specification |
|-----------|---------------|
| Machine | MacBook Pro 16-inch, 2019 |
| Processor | 2.3 GHz 8-Core Intel Core i9 |
| Memory | 32 GB 2667 MHz DDR4 |
| OS | macOS Tahoe 26.2 |

### Execution Times (Reference Hardware)

| Stage | Configuration | Wall Time | Notes |
|-------|---------------|-----------|-------|
| **Ola1 sweep** | 350 runs | ~3 days | Single-node oscillators, full parameter space |
| **Ola2 pipeline** | 323 candidates | ~4 hours | N=2–5, 100% promotion rate |
| **Ola3 pipeline** | 3000 → 402 swept | ~6 hours | N=6–9, 3.9% promotion rate |
| **Ola4 pipeline** | 1000 → 462 swept | ~4 hours | N=9–12, 0.7% promotion rate |
| **Total (Ola2–4)** | Full paper run | ~14 hours | Excluding Ola1 |

### Scaling Estimates

```
Time_your_machine ≈ Time_reference × (8 / your_cores) × (2.3 / your_GHz)
```

---

## Running the Model

### Requirements

- Python 3.8+ (tested with 3.13)
- NumPy (required)
- pandas, matplotlib, scipy (for figures)

```bash
pip install numpy pandas matplotlib scipy
```

### Option A: Start from Ola1 Blocks (Recommended, ~14 hours)

The repository includes pre-computed Ola1 blocks (canonical + DNA by block_id), so you can skip the 3-day Ola1 sweep:

```bash
# Ola2 (~4 hours)
PYTHONPATH=src python3 -m olar.pipeline \
  --sequence config/ola2_paper/run_sequence_ola2_paper.json

# Ola3 (~6 hours)
PYTHONPATH=src python3 -m olar.pipeline \
  --sequence config/ola3_paper/run_sequence_ola3_paper.json

# Ola4 (~4 hours)
PYTHONPATH=src python3 -m olar.pipeline \
  --sequence config/ola4_paper/run_sequence_ola4_paper.json

# Generate paper outputs (paper/data + paper/figures)
PYTHONPATH=src python3 scripts/paper_build.py
```

### Option B: Full Reproduction from Scratch (~3+ days)

To reproduce everything including Ola1:

#### Step 1: Ola1 Sweep (~3 days)

```bash
PYTHONPATH=src python3 -m ola1.run_sweep \
  --case Ola1_3-2-5 \
  --runs 2000 \
  --seed 42 \
  --max-complexity 35 \
  --engine-config config/ola1_paper/engine_core3.json \
  --layer-states config/ola1_paper/layer_states.yaml \
  --band-min 0.05 --band-max 5.0 \
  --stop-file /tmp/stop_sweep \
  --output-root data/processed/ola1_paper \
  --no-plots \
  --partial-flush-every 2
```

#### Step 2: Ola1 Assembly

```bash
PYTHONPATH=src python3 -m ola1.run_ola1_pipeline \
  --case Ola1_3-2-5 \
  --processed-dir data/processed/ola1_paper \
  --results-json data/processed/ola1_paper/partial/runs_partial.jsonl \
  --sm-universe config/ola1_paper/sm_universe.json \
  --selection-config config/ola1_paper/wave1_selection.json \
  --digest-dir data/processed/digest/ola1_paper \
  --max-blocks-per-particle 10000 \
  --runs-full-jsonl data/processed/ola1_paper/global/runs_full.jsonl
```

#### Steps 3–5: Ola2–4

Run as shown in Option A above.

### Option C: Minimal Validation (~30 minutes)

To verify the pipeline works:

```bash
PYTHONPATH=src python3 -m ola1.run_sweep \
  --case Ola1_test \
  --runs 50 \
  --seed 42 \
  --max-complexity 35 \
  --engine-config config/ola1_paper/engine_core3.json \
  --layer-states config/ola1_paper/layer_states.yaml \
  --band-min 0.05 --band-max 5.0 \
  --output-root data/processed/ola1_test \
  --no-plots
```

---

## Custom Experiments

### Modifying Parameters

```bash
# Copy and edit a config
cp config/ola3_paper/ola3_explorer.json config/my_experiment/explorer.json
# Edit thresholds, dt, T_ticks, etc.

# Run with custom config
PYTHONPATH=src python3 -m olar.explorer \
  --config config/my_experiment/explorer.json
```

### Key Parameters

| Parameter | Location | Effect |
|-----------|----------|--------|
| `T_ticks` | engine_defaults | Integration length |
| `dt` | engine_defaults | Time step (critical—see Tuning Guide) |
| `R_mean_lastW_min` | tagging_thresholds | Coherence threshold |
| `quality_lock_min` | tagging_thresholds | Lock quality threshold |

---

## Paper Data Description

### paper/data/

| File | Description |
|------|-------------|
| `paper_metrics_all.csv` | All 1,187 promoted entities with full metrics |
| `paper_metrics_manifest.json` | Run metadata (configs, dates, software versions) |
| `paper_metrics_summary.json` | Statistical summary (counts, means, rates by ola) |

### paper_metrics_all.csv columns

| Column | Description |
|--------|-------------|
| `entity_id` | Unique identifier |
| `ola` | Pipeline stage (2, 3, or 4) |
| `node_count` | Network size N |
| `template_name` | Topology type |
| `R_network_S1_mean` | Global coherence R |
| `PE_lockS1_norm_mean` | Participation entropy |
| `H_part_norm_mean` | Normalized entropy |
| `R_mean_lastW_mean` | Lock score L |
| `phase_var_lastW_mean` | Phase variance |
| `QualityLock_mean` | Lock quality |
| `dof_grade` | Grade (A, B, or C) |
| `promoted` | Promotion status |

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'olar'"

```bash
export PYTHONPATH=src
# Or prefix commands with PYTHONPATH=src
```

### "FileNotFoundError: blocks not found"

Ola2+ requires Ola1 blocks. Use the included `data/processed/ola1_paper/promoted/` or run Ola1 first.

### Slow execution

Check `dt` alignment between Explorer and Sweep configs. See the Tuning Guide appendix.

---

## Citation

```bibtex
@article{Agostino2026coherence,
  author = {Agostino, C.},
  title = {Coherence Scaling in Hierarchical Oscillator Networks: 
           Power-Law Decay, Memory Overhead, and Topological Constraints 
           with Parallels to Disordered Condensed Matter},
  year = {2026},
  note = {Submitted to Physical Review B}
}

@dataset{Agostino2026doft,
  author = {Agostino, C.},
  title = {DOFT Framework: Code and Data for Coherence Scaling},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

---

## License

MIT License. See [LICENSE](LICENSE).

---

## Contact

- **Author:** C. Agostino
- **Email:** cesar.agostino@gmail.com

---

## Appendix: Explorer-Sweep Tuning Guide

### The Core Principle

> **Explorer and Sweep must use the same temporal resolution (`dt`).**

Misaligned `dt` causes 70%+ false positives and wasted computation.

### Recommended Configuration (dt=1.0)

**Explorer:**
```json
{
  "engine_defaults": {
    "T_ticks": 1200,
    "W": 400,
    "dt": 1.0
  },
  "tagging_thresholds": {
    "R_mean_lastW_min": 0.75,
    "quality_lock_min": 0.70,
    "phase_var_lastW_max": 0.08
  }
}
```

**Sweep:**
```json
{
  "engine_defaults": {
    "T_ticks": 3000,
    "W": 600,
    "dt": 1.0
  }
}
```

### Parameter Relationships

```python
dt_explorer = dt_sweep              # MUST be equal
T_explorer  = ceil(T_sweep * 0.35)  # Explorer ~35% of Sweep
W_explorer  = ceil(W_sweep * 0.7)   # Large window for convergence
```

### Performance Comparison

| Configuration | Time | Viable Rate |
|---------------|------|-------------|
| Misaligned dt | ~80 hrs | 23% |
| Aligned dt=1.0 | ~24 hrs | 67% |

### Convergence Test

Before a full run, test whether dt=1.0 captures your physics:

```python
# Run same structure with dt=1.0 and dt=0.1
# If R_final differs by >5%, use dt=0.1 (slower but accurate)
```

### When to Use dt=0.1

- Strong coupling (R > 0.9)
- Fast collective modes
- Convergence test fails

For the complete tuning guide with examples and troubleshooting, see the extended documentation in `docs/tuning_guide.md`.
