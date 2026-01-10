# Study05 – DOFT Internal Layers Simulator

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18200973.svg)](https://doi.org/10.5281/zenodo.18200973)

This repository contains the computational framework and paper materials for:

> **Coherence Scaling in Hierarchical Oscillator Networks: Power-Law Decay, Memory Overhead, and Topological Constraints with Parallels to Disordered Condensed Matter**  
> C. Agostino (2026)

The code implements the **Delayed Oscillator Field Theory (DOFT)** framework: a four-stage recursive pipeline (**Ola1–Ola4**) for exploring coherence scaling in networks of coupled oscillators with internal memory.

---

## TL;DR

- **Want to read the paper?** Compile `paper/main.tex` (no code execution required).
- **Want to reproduce the paper outputs using the included Ola1 blocks?** Run **Ola2–Ola4** (~**14 hours** on an 8‑core workstation).
- **Want full reproduction from scratch including Ola1?** Expect **~3+ days** for Ola1 alone on reference hardware.
- **Want to check the pipeline works without committing days?** Run the **Minimal Validation** (~30 minutes).

> **Important (expectations):** DOFT is a **stochastic rare‑event search**. Short runs may produce **zero viable candidates**. Publication‑scale statistics require sustained sampling; runtime depends on hardware, seed, and candidate yield.

---

## Repository Layout

```
study05-doft/
├── paper/                        # PAPER (self-contained, compiles directly)
│   ├── main.tex                  # LaTeX source
│   ├── main.bib                  # Bibliography
│   ├── figures/                  # All figures (PDF/PNG)
│   └── data/                     # Paper data (consolidated)
│       ├── paper_metrics_all.csv
│       ├── paper_metrics_manifest.json
│       └── paper_metrics_summary.json
│
├── src/                          # MODEL SOURCE CODE
│   ├── olar/                     # Pipeline, explorer, sweep
│   ├── core/                     # Catalog, taxonomy, promotion
│   └── ola1/                     # Ola1 sweep and assembly
│
├── config/                       # CONFIGURATION FILES
│   ├── ola1_paper/
│   ├── ola2_paper/
│   ├── ola3_paper/
│   └── ola4_paper/
│
├── data/                         # MODEL DATA (precomputed blocks included)
│   └── processed/
│       └── ola1_paper/
│           └── promoted/         # Ola1 blocks (needed for Ola2+)
│               ├── simple_blocks.json
│               └── dof_dna_catalog.csv
│
├── scripts/                      # Utilities
│   ├── paper_build.py            # Generate all paper outputs
│   ├── paper_metrics_pack.py     # Consolidate metrics
│   ├── paper_figures_final.py    # Generate figures
│   └── monitor_sweep_progress.py # (Optional) Monitor multi-shard sweeps
│
├── README.md                     # This file
└── LICENSE                       # MIT License
```

---

## Quick Start

### 1) Compile the Paper (fastest)

The `paper/` directory is self-contained — all figures and data are included.

```bash
cd paper
pdflatex main
pdflatex main
```

No model execution required.

### 2) Reproduce figures/metrics (compute required)

If you want to reproduce results from scratch, follow:
- [Computational Requirements](#computational-requirements)
- [Running the Model](#running-the-model)
- [Regenerate Paper Outputs](#regenerate-paper-outputs)

---

## Computational Requirements

### Reference Hardware (used for the timings below)

| Component | Specification |
|-----------|---------------|
| Machine | MacBook Pro 16-inch (2019) |
| CPU | Intel Core i9 (8 cores), 2.3 GHz |
| Memory | 32 GB RAM |
| OS | macOS (version at time of runs) |

### Execution Times (reference hardware)

| Stage | Configuration | Wall Time | Notes |
|-------|---------------|-----------|-------|
| **Ola1 sweep** | ~350 runs (paper sweep subset) | ~3 days | Single-node oscillators, broad parameter space |
| **Ola2 pipeline** | ~323 candidates | ~4 hours | N=2–5 (high promotion expected in this regime) |
| **Ola3 pipeline** | ~3000 → 402 swept | ~6 hours | N=6–9 |
| **Ola4 pipeline** | ~1000 → 462 swept | ~4 hours | N=9–12 |
| **Total (Ola2–4)** | Full paper reproduction | ~14 hours | **Excludes** Ola1 |

### Very rough scaling (order-of-magnitude)

Runtime depends on CPU architecture (IPC), memory bandwidth, and parallel efficiency. As a **rough** heuristic:

```
Time_your_machine ≈ Time_reference × (8 / your_physical_cores) × (2.3 / your_GHz) × C_arch
```

where `C_arch` can vary significantly across CPUs (treat this as an order‑of‑magnitude guide, not a promise).

---

## Running the Model

### Requirements

- Python 3.8+ (tested with 3.13)
- NumPy (required)
- pandas, matplotlib, scipy (for figures)

If a `requirements.txt` is present, prefer:

```bash
pip install -r requirements.txt
```

Otherwise:

```bash
pip install numpy pandas matplotlib scipy
```

> **Tip:** If you use `venv`/conda, create an isolated environment first.

### Make the package visible

Most commands assume `src/` is on `PYTHONPATH`.

```bash
export PYTHONPATH=src
```

(or prefix commands with `PYTHONPATH=src` as shown below).

### Parallelism

- **Ola1 sweep** supports multicore workers (`--workers` flag).
- **Olar sweep** can run in multi-worker shards (see your `sweep_workers/` output directory).

(Optional) monitor shard progress:

```bash
PYTHONPATH=src python3 scripts/monitor_sweep_progress.py \
  --shards-root data/processed/ola3_paper/sweep_workers \
  --shard-count 12 \
  --sweep-config config/ola3_paper/ola3_sweep.json
```

### Option A: Start from included Ola1 blocks (**recommended**, ~14 hours)

This repository includes precomputed Ola1 blocks under `data/processed/ola1_paper/promoted/`, so you can skip the 3‑day Ola1 sweep.

```bash
# Ola2 (~4 hours)
PYTHONPATH=src python3 -m olar.pipeline   --sequence config/ola2_paper/run_sequence_ola2_paper.json

# Ola3 (~6 hours)
PYTHONPATH=src python3 -m olar.pipeline   --sequence config/ola3_paper/run_sequence_ola3_paper.json

# Ola4 (~4 hours)
PYTHONPATH=src python3 -m olar.pipeline   --sequence config/ola4_paper/run_sequence_ola4_paper.json
```

#### Expected outputs (after Option A)

You should see new/updated outputs under:

- `data/processed/ola2_paper/`, `data/processed/ola3_paper/`, `data/processed/ola4_paper/`
- consolidated metrics written to `paper/data/` after running `scripts/paper_build.py` (see below)
- regenerated figures written to `paper/figures/` after running the figure script

### Option B: Full reproduction from scratch (**~3+ days**)

#### Step 1: Ola1 Sweep (~3 days)

```bash
PYTHONPATH=src python3 -m ola1.run_sweep   --case Ola1_3-2-5   --runs 2000   --seed 42   --max-complexity 35   --engine-config config/ola1_paper/engine_core3.json   --layer-states config/ola1_paper/layer_states.yaml   --band-min 0.05 --band-max 5.0   --stop-file /tmp/stop_sweep   --output-root data/processed/ola1_paper   --no-plots   --partial-flush-every 2
```

#### Step 2: Ola1 Assembly

```bash
PYTHONPATH=src python3 -m ola1.run_ola1_pipeline   --case Ola1_3-2-5   --processed-dir data/processed/ola1_paper   --results-json data/processed/ola1_paper/Ola1_3-2-5_study05_sweep_results.json   --sm-universe config/ola1_paper/sm_universe.json   --selection-config config/ola1_paper/wave1_selection.json   --digest-dir data/processed/digest/ola1_paper   --max-blocks-per-particle 10000   --runs-full-jsonl data/processed/ola1_paper/Ola1_3-2-5/runs_full.jsonl
```

#### Steps 3–5: Ola2–Ola4

Run as shown in Option A.

### Option C: Minimal validation (**~30 minutes**)

This verifies that the engine runs and produces outputs (it may produce few/zero candidates — that can be normal for short runs).

```bash
PYTHONPATH=src python3 -m ola1.run_sweep   --case Ola1_test   --runs 50   --seed 42   --max-complexity 35   --engine-config config/ola1_paper/engine_core3.json   --layer-states config/ola1_paper/layer_states.yaml   --band-min 0.05 --band-max 5.0   --output-root data/processed/ola1_test   --no-plots
```

**Success criteria:** a non-empty directory is created under `data/processed/ola1_test/` and the run writes partial results/logs (file names may vary by version).

---

## Regenerate Paper Outputs

After running the model (Ola2–Ola4), regenerate metrics and figures used by the manuscript.

### All at once (recommended)

```bash
PYTHONPATH=src python3 scripts/paper_build.py
```

This updates consolidated CSV/JSON outputs in `paper/data/` and regenerates figures in `paper/figures/`.

### Step by step

**1) Consolidate metrics**

```bash
PYTHONPATH=src python3 scripts/paper_metrics_pack.py   --out-root paper/data   --skip-plots   --all   --ola-dir data/processed/ola2_paper   --ola-dir data/processed/ola3_paper   --ola-dir data/processed/ola4_paper
```

**2) Generate figures**

```bash
PYTHONPATH=src python3 scripts/paper_figures_final.py   --metrics-ola2 paper/data/ola2_paper/paper_metrics_ola2_paper.csv   --metrics-ola3 paper/data/ola3_paper/paper_metrics_ola3_paper.csv   --metrics-ola4 paper/data/ola4_paper/paper_metrics_ola4_paper.csv   --genome-ola2 paper/data/genome_layers_ola2_paper.csv   --genome-ola3 paper/data/genome_layers_ola3_paper.csv   --genome-ola4 paper/data/genome_layers_ola4_paper.csv   --out-dir paper/figures
```

---

## Custom Experiments

### Reproducibility knobs (faster runs)

| Knob | Where | Effect / risk |
|------|------|----------------|
| Reduce seeds per entity | configs / CLI (if available) | Faster; lower statistical robustness |
| Reduce `T_ticks` | `engine_defaults` | Faster; may miss locking |
| Increase `dt` | `engine_defaults` | Faster; can degrade accuracy; affects dynamics |
| Reduce candidate count | run sequences | Faster; less coverage |
| Increase workers/shards | CLI / sweep workers | Faster; requires more cores |

### Modifying parameters

```bash
# Copy and edit a config
cp config/ola3_paper/ola3_explorer.json config/my_experiment/explorer.json

# Run with custom config
PYTHONPATH=src python3 -m olar.explorer   --config config/my_experiment/explorer.json
```

### Key parameters (definitions)

| Parameter | Location | Meaning |
|-----------|----------|---------|
| `T_ticks` | `engine_defaults` | Integration length |
| `dt` | `engine_defaults` | Time step (affects cost roughly linearly) |
| `R_network_S1_mean` | metrics output | **Global coherence** R (paper observable) |
| `R_mean_lastW_*` | tagging/metrics | **Lock score** L (operational; see paper) |
| `quality_lock_min` | tagging_thresholds | Lock quality threshold |
| `phase_var_lastW_max` | tagging_thresholds | Phase variance threshold |

> Note: naming is historical; see the manuscript for the precise definitions of R and L.

---

## Paper Data Description

### `paper/data/`

| File | Description |
|------|-------------|
| `paper_metrics_all.csv` | All 1,187 promoted entities with full metrics |
| `paper_metrics_manifest.json` | Run metadata (configs, dates, software versions) |
| `paper_metrics_summary.json` | Statistical summary (counts, means, rates by ola) |

### `paper_metrics_all.csv` (selected columns)

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

### `ModuleNotFoundError: No module named 'olar'`

```bash
export PYTHONPATH=src
```

(or prefix each command with `PYTHONPATH=src`).

### `FileNotFoundError: blocks not found`

Ola2+ requires Ola1 blocks. Use the included `data/processed/ola1_paper/promoted/` or run Ola1 first.

### Slow execution / low yield

- Ensure **Explorer and Sweep use the same `dt`** (see tuning guide below).
- Short runs can have **zero candidates** (rare-event sampling).
- If yield is extremely low, reduce strictness of operational thresholds for exploratory runs, then restore paper thresholds for reproduction.

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
  doi = {10.5281/zenodo.18200973}
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

## Appendix: Explorer–Sweep Tuning Guide (short)

### Core principle

> **Explorer and Sweep must use the same temporal resolution (`dt`).**

Misaligned `dt` can produce many false positives and waste computation.

### Recommended configuration (paper: `dt=0.0025`)

**Explorer (example):**
```json
{
  "engine_defaults": {
    "T_ticks": 20000,
    "W": 4000,
    "dt": 0.0025
  },
  "tagging_thresholds": {
    "R_mean_lastW_min": 0.75,
    "quality_lock_min": 0.70,
    "phase_var_lastW_max": 0.05
  }
}
```

**Sweep (example):**
```json
{
  "engine_defaults": {
    "T_ticks": 20000,
    "W": 4000,
    "dt": 0.0025
  }
}
```

### Performance notes (illustrative)

- In the reference configs, runtime is often dominated by **seeds per entity** and sweep breadth.
- **Decreasing `dt` increases cost roughly linearly** (more integration steps).
- Reducing seeds speeds runs but lowers statistical robustness.

Example outcomes observed during tuning:

| Configuration | Time | Viable Rate |
|---------------|------|------------|
| Misaligned `dt` | ~80 hrs | 23% |
| Aligned `dt=0.0025` | ~14 hrs | 67% |

For the complete tuning guide with examples, see `docs/tuning_guide.md` if present in this release.
