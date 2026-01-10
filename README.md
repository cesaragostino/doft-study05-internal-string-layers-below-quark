# Study05 – DOFT Internal Layers Simulator

This repo contains the Ola1/Ola2/Ola3 pipeline for recursive DOFT exploration and sweep, plus catalog/taxonomy/promotion for moving to the next Ola.

## Layout
- Code: `src/`
  - `src/olar/` pipeline + explorer + sweep
  - `src/core/` catalog/taxonomy/promotion
  - `src/ola1/` Ola1 export/assembly
- Configs:
  - Ola1 paper: `data/config/ola1_paper/` (engine, layer states, selection, sm_universe)
  - Ola2+ paper runs: `data/config/olaN_paper/`
- Raw inputs: `data/raw/` (legacy + auxiliary inputs)
- Raw outputs: `data/processed/olaN/raw/`
- Sweep workers: `data/processed/olaN/sweep_workers/`
- Merge output: `data/processed/olaN/sweep_merged/`
- Catalog outputs: `data/processed/olaN/catalog/`
- Promoted blocks: `data/processed/olaN/promoted/`
- Reports: `data/processed/olaN/explorer_report.md`, `data/processed/olaN/sweep_report.md`

## Requirements
- Python 3.8+ (tested with 3.13)
- `numpy`

All commands are run from the repo root and use:
```
PYTHONPATH=src
```

## Parallelism (Ola1 + Olar)

Both pipelines are parallel:
- **Ola1 sweep** uses multicore workers (`--workers` flag).
- **Olar sweep** uses multi-worker shards (see `sweep_workers/`).

Monitor sweep progress:
```bash
PYTHONPATH=src python3 scripts/monitor_sweep_progress.py \
  --shards-root data/processed/ola3_paper/sweep_workers \
  --shard-count 12 \
  --sweep-config config/ola3_paper/ola3_sweep.json
```

## Ola1 Sweep + Pipeline (Paper Example)

```bash
PYTHONPATH=src python3 -m ola1.run_sweep \
  --case Ola1_3-2-5 \
  --runs 2000 \
  --seed 42 \
  --max-complexity 35 \
  --engine-config data/config/ola1_paper/engine_core3.json \
  --layer-states data/config/ola1_paper/layer_states.yaml \
  --band-min 0.05 --band-max 5.0 \
  --stop-file /tmp/stop_sweep \
  --output-root data/processed/ola1_paper \
  --no-plots \
  --partial-flush-every 2
```

```bash
PYTHONPATH=src python3 -m ola1.run_ola1_pipeline \
  --case Ola1_3-2-5 \
  --processed-dir data/processed/ola1_paper \
  --results-json data/processed/ola1_paper/partial/runs_partial.jsonl \
  --sm-universe data/config/ola1_paper/sm_universe.json \
  --selection-config data/config/ola1_paper/wave1_selection.json \
  --digest-dir data/processed/digest/ola1_paper \
  --max-blocks-per-particle 10000 \
  --runs-full-jsonl data/processed/ola1_paper/global/runs_full.jsonl
```

Note: Ola2 configs read Ola1 paper outputs from
`data/processed/ola1_paper/simple_blocks_canonical.json` and
`data/processed/ola1_paper/dof_dna_catalog_by_block_id.csv`
(not the `promoted/` folder).

## Paper Data + Figures

Generate consolidated metrics and figures:
```bash
PYTHONPATH=src python3 scripts/paper_build.py
```

Or run them separately:
```bash
PYTHONPATH=src python3 scripts/paper_metrics_pack.py \
  --out-root paper/data \
  --skip-plots \
  --all \
  --ola-dir data/processed/ola2_paper \
  --ola-dir data/processed/ola3_paper \
  --ola-dir data/processed/ola4_paper

PYTHONPATH=src python3 scripts/paper_figures_final.py \
  --metrics-ola2 paper/data/ola2_paper/paper_metrics_ola2_paper.csv \
  --metrics-ola3 paper/data/ola3_paper/paper_metrics_ola3_paper.csv \
  --metrics-ola4 paper/data/ola4_paper/paper_metrics_ola4_paper.csv \
  --genome-ola2 paper/data/genome_layers_ola2_paper.csv \
  --genome-ola3 paper/data/genome_layers_ola3_paper.csv \
  --genome-ola4 paper/data/genome_layers_ola4_paper.csv \
  --out-dir paper/figures
```

## ⚙️ Explorer-Sweep Tuning Guide

## Overview

The DOFT framework uses a two-stage discovery pipeline:

1. **Explorer** (Kuramoto-based): Fast screening to find candidate structures
2. **Sweep** (Differential equations): Detailed physics validation of candidates

This guide explains how to tune these stages for optimal performance and physical accuracy.

---

## The Core Problem: Misaligned Scales

### What Goes Wrong

A common misconfiguration looks like this:

```json
// Explorer config (ola3_explorer.json)
{
  "engine_defaults": {
    "T_ticks": 1200,
    "W": 200,
    "dt": 1.0
  }
}

// Sweep config (ola3_sweep.json)
{
  "engine_defaults": {
    "T_ticks": 40000,
    "W": 2000,
    "dt": 0.0025
  }
}
```

**Problems:**

1. **Temporal scale mismatch**: Explorer uses `dt=1.0` while Sweep uses `dt=0.0025` (400x difference)
   - They're measuring physics at fundamentally different resolutions
   - Poor correlation between Explorer predictions and Sweep results

2. **Window size mismatch**: Explorer `W=200` vs Sweep `W=2000` (10x difference)
   - Explorer's small window misses convergence patterns
   - Passes transient oscillations as "stable"

3. **Overkill in Sweep**: `T=40000` with `dt=0.0025` is often excessive
   - 13x more expensive than necessary
   - Diminishing returns on physical accuracy

**Observed consequences:**
```
Explorer: 30 candidates from 20k evaluations (0.15% rate)
Sweep:    4 viables from 17 measured (23% viable rate)

-> 70% of candidates are false positives
-> Sweep does the heavy lifting (inefficient)
```

---

## The Solution: Align Temporal Scales

### Key Principle

> **Explorer and Sweep must measure physics at the same temporal resolution (`dt`).**
> 
> - Explorer gates with large window (`W`) and selective thresholds
> - Sweep confirms with more statistics (seeds) and longer integration (T)

### Two Recommended Approaches

#### **Option A: Coarse Resolution (dt=1.0)** [RECOMMENDED]

Best for systems with **slow dynamics** (weak coupling, moderate coherence).

```json
// Explorer: Fast gating
{
  "engine_defaults": {
    "T_ticks": 1200,      // Keep moderate
    "W": 400,             // ↑ Increased (was 200)
    "dt": 1.0             // Keep coarse
  },
  "tagging_thresholds": {
    "R_mean_lastW_min": 0.75,      // ↓ More selective (was 0.80)
    "quality_lock_min": 0.70,      // ↓ More selective (was 0.75)
    "phase_var_lastW_max": 0.08    // ↑ More permissive (was 0.05)
  }
}

// Sweep: Efficient confirmation
{
  "engine_defaults": {
    "T_ticks": 3000,      // ↓ Reduced 13x (was 40000)
    "W": 600,             // ↓ Reduced (was 2000)
    "dt": 1.0             // ↑ ALIGNED with Explorer (was 0.0025)
  },
  "budgets": {
    "early_stop": {
      "after_seeds": 3,              // ↑ More patient (was 2)
      "fail_if_R_mean_below": 0.35   // ↓ Lower threshold (was 0.40)
    }
  }
}
```

**Performance:**
- Explorer: ~20 hrs for 20k evaluations
- Sweep: ~4 hrs for 12 candidates x 6 seeds
- **Total: ~24 hrs** (3x faster than misaligned config)
- Expected: ~8 viables at 60% rate (vs 4 at 23%)

**Use when:** Your viable structures show weak locks (R_network ~ 0.4-0.6), sparse topologies, moderate coupling.

---

#### **Option B: Fine Resolution (dt=0.1)**

Best for systems with **fast dynamics** (strong coupling, tight locks).

```json
// Explorer
{
  "engine_defaults": {
    "T_ticks": 4000,      // ↑ Increased for finer sampling
    "W": 600,             // ↑ Larger window
    "dt": 0.1             // Fine resolution
  },
  "tagging_thresholds": {
    // Same as Option A
  }
}

// Sweep
{
  "engine_defaults": {
    "T_ticks": 10000,     // ↑ More steps needed
    "W": 800,             // Larger window
    "dt": 0.1             // ALIGNED with Explorer
  }
}
```

**Performance:**
- Explorer: ~200 hrs for 20k evaluations
- Sweep: ~500 hrs for 10 candidates x 6 seeds
- **Total: ~700 hrs** (10x slower, but captures fast physics)

**Use when:** Convergence test shows dt=1.0 loses physical accuracy (see below).

---

## Convergence Test: Which Resolution?

Before committing to a full run, test whether coarse resolution captures your physics.

### Procedure

1. **Select a test case**: Take one known viable structure from a previous run (e.g., from Ola2)

2. **Run three simulations** with different temporal resolutions:

```python
# Pseudocode example

viable_structure = load_viable("ola2_decagon_ring_viable1")

# Test A: Coarse (dt=1.0)
result_A = simulate(
    structure=viable_structure,
    T_ticks=1000,
    W=200,
    dt=1.0
)
R_final_A = result_A.R_network_final

# Test B: Medium (dt=0.1)
result_B = simulate(
    structure=viable_structure,
    T_ticks=10000,
    W=200,
    dt=0.1
)
R_final_B = result_B.R_network_final

# Test C: Fine (dt=0.01)
result_C = simulate(
    structure=viable_structure,
    T_ticks=100000,
    W=200,
    dt=0.01
)
R_final_C = result_C.R_network_final
```

3. **Compare convergence**:

```python
diff_AB = abs(R_final_A - R_final_B)
diff_BC = abs(R_final_B - R_final_C)

if diff_AB < 0.05 and diff_BC < 0.05:
    print("Converged: dt=1.0 captures physics")
    print("-> Use Option A (24 hrs)")
elif diff_AB > 0.1:
    print("Not converged: dt=1.0 loses physics")
    print("-> Use Option B (240 hrs)")
else:
    print("Marginal: Consider dt=0.1 for safety")
```

### Expected Result

For systems with **weak coupling** (like Ola2 viables with R~0.4):

```
R_final_A = 0.405  (dt=1.0)
R_final_B = 0.407  (dt=0.1)
R_final_C = 0.408  (dt=0.01)

diff_AB = 0.002  Converged
-> Use Option A
```

For systems with **strong coupling** (R>0.9):

```
R_final_A = 0.650  (dt=1.0)  <- Loses fast dynamics
R_final_B = 0.923  (dt=0.1)
R_final_C = 0.925  (dt=0.01)

diff_AB = 0.273  Not converged
-> Use Option B
```

---

## Parameter Relationships

### Formal Policy

To avoid improvisation, use these relationships:

```python
# Basic alignment
dt_explorer = dt_sweep  # MUST be equal

# Time integration
T_explorer = ceil(T_sweep * 0.35)  # Explorer runs 30-40% of Sweep time

# Window size
W_explorer = ceil(W_sweep * 0.7)   # Explorer needs large W to see convergence

# Seeds
seeds_explorer = 1              # Fast screening
seeds_sweep = 6                 # Statistical robustness
```

**Example calculation** (Option A):

```
Given Sweep: T=3000, W=600, dt=1.0

Derived Explorer:
  T = ceil(3000 x 0.35) = 1050  ~= 1200
  W = ceil(600 x 0.7)   = 420   ~= 400
  dt = 1.0                      (aligned)
```

---

## Threshold Philosophy

### Explorer Thresholds: Gating, Not Certification

Explorer should be **permissive enough** to avoid false negatives (missing "diamonds") but **selective enough** to filter obvious garbage.

**Recommended margins:**

```json
{
  "explorer": {
    "min_coherence": 0.35,      // Lower than final
    "min_complexity": 0.03,     // Lower than final
    "R_mean_lastW_min": 0.75,   // Relaxed
    "quality_lock_min": 0.70    // Relaxed
  },
  "sweep_final": {
    "min_coherence": 0.40,      // True target
    "min_complexity": 0.05,     // True target
    "R_mean_lastW_min": 0.85,   // Stricter
    "quality_lock_min": 0.90    // Stricter
  }
}
```

**Philosophy**: Explorer rejects the "obviously bad", Sweep certifies the "truly good".

---

## Cost Optimization

### Where to Cut Costs

The right lever is **NOT** making Explorer extremely coarse (it breaks correlation). Instead:

#### 1. Early Stopping in Explorer

Reject immediately on clear failures:

```json
{
  "early_stop": {
    "enabled": true,
    "conditions": [
      {"type": "nan_overflow", "action": "reject_immediate"},
      {"type": "R_network_below", "threshold": 0.3, "after_ticks": 400}
    ]
  }
}
```

#### 2. Reduce Explorer Seeds

```json
{
  "explorer": {"seeds": 1},    // Or 2 for minimal robustness
  "sweep": {"seeds": 6}         // Keep high for statistics
}
```

#### 3. Reduce Sweep Neighborhood

```json
{
  "neighborhood": {
    "mode": "param_bin_neighbors",
    "max_neighbor_bins": 1      // Reduce from 3
  }
}
```

---

## Complete Example Configs

### Option A: Balanced (dt=1.0)

**ola3_explorer.json:**
```json
{
  "engine_defaults": {
    "T_ticks": 1200,
    "W": 400,
    "dt": 1.0,
    "K_local": 0.45,
    "kappa_global": 0.3,
    "sigma0": 0.3,
    "sigma_tc": 60.0,
    "sigma_theta_init": 0.5,
    "tau_field": 120.0
  },
  "tagging_thresholds": {
    "R_mean_lastW_min": 0.75,
    "memory_score_k10_min": 0.0,
    "phase_var_lastW_max": 0.08,
    "quality_lock_min": 0.70,
    "viability_mode": "hard_viable_soft_memory"
  },
  "seed_policy": {
    "mode": "deterministic",
    "seeds_per_attempt": 1
  }
}
```

**ola3_sweep.json:**
```json
{
  "engine_defaults": {
    "T_ticks": 3000,
    "W": 600,
    "dt": 1.0,
    "K_local": 0.45,
    "kappa_global": 0.3,
    "sigma0": 0.3,
    "sigma_tc": 60.0,
    "sigma_theta_init": 0.5,
    "tau_field": 120.0
  },
  "budgets": {
    "max_evals_per_entity": 24,
    "early_stop": {
      "enabled": true,
      "after_seeds": 3,
      "fail_if_R_mean_below": 0.35
    }
  },
  "seed_policy": {
    "mode": "deterministic",
    "seeds": 6,
    "min_seeds_required": 4
  },
  "candidate_source": {
    "filter": {
      "require_candidate": true,
      "top_k": 50,
      "top_k_by": "priority_score"
    }
  }
}
```

---

### Option B: Fine Physics (dt=0.1)

**ola3_explorer.json:**
```json
{
  "engine_defaults": {
    "T_ticks": 4000,      // ↑
    "W": 600,             // ↑
    "dt": 0.1,            // <- Fine
    // ... rest same as A
  },
  // thresholds same as A
}
```

**ola3_sweep.json:**
```json
{
  "engine_defaults": {
    "T_ticks": 10000,     // ↑
    "W": 800,             // ↑
    "dt": 0.1,            // <- Fine, ALIGNED
    // ... rest same as A
  },
  // budgets same as A
}
```

---

## Performance Comparison

### Before Optimization (Misaligned)

```
Configuration:
  Explorer: T=1200,  W=200,   dt=1.0
  Sweep:    T=40000, W=2000,  dt=0.0025

Results:
  Explorer: 30 candidates from 20k evals (0.15%)
  Sweep:    4 viables from 17 measured (23%)
  
  Time: ~80 hrs total
  Efficiency: Poor (70% candidates rejected)
```

### After Optimization (Option A)

```
Configuration:
  Explorer: T=1200, W=400,  dt=1.0
  Sweep:    T=3000, W=600,  dt=1.0  <- Aligned

Results:
  Explorer: 12 candidates from 20k evals (0.06%)
  Sweep:    8 viables from 12 measured (67%)
  
  Time: ~24 hrs total (3x faster)
  Efficiency: Excellent (only 33% candidates rejected)
```

---

## Diagnostic Outputs

### Expected Console Output (Well-Tuned)

```
[Explorer]
attempts_written:          20000
entities_candidates:       12      <- Low rate (selective)
candidate_rate:            0.06%

[Sweep]
entities_measured:         12
viables_found:             8
viable_rate:               67%     <- High rate (good filtering)
early_stop_rate:           25%     <- Some early stops OK
```

### Warning Signs

```
[Explorer]
candidate_rate: 0.15%     <- Too high (passing garbage)

[Sweep]
viable_rate: 23%          <- Too low (Explorer failed to gate)
early_stop_rate: 80%      <- Explorer-Sweep mismatch
```

**Diagnosis**: Explorer thresholds too permissive OR `dt` misaligned.

---

## Physical Interpretation

### Why dt Matters

The coupling timescale in your system is approximately:

```
tau_coupling ~ 1 / K_local
```

For `K_local = 0.45`:
```
tau_coupling ~ 2.2 time units
```

**Nyquist criterion** for stable integration:
```
dt < tau_coupling / 2
dt < 1.1
```

Therefore `dt=1.0` is **safe** for this system.

Using `dt=0.0025` provides:
```
dt / tau_coupling = 0.0025 / 2.2 = 0.001
```

This is 1000x oversampling - physically accurate but computationally wasteful.

### System Classification

**Weak coupling** (R_network ~ 0.3-0.6):
- Kuramoto-like dynamics
- Slow phase evolution
- tau ~ 2-5 units
- **Use dt=1.0** (Option A)

**Strong coupling** (R_network ~ 0.9-1.0):
- BCS-like condensation
- Fast collective modes
- tau ~ 0.1-0.5 units
- **Use dt=0.1** (Option B)

---

## Quick Start Checklist

- [ ] Run convergence test on one viable structure
- [ ] Choose resolution based on test results
  - [ ] dt=1.0 if converged (Option A)
  - [ ] dt=0.1 if not converged (Option B)
- [ ] Apply parameter relationships (T, W)
- [ ] Set Explorer thresholds (selective but not strict)
- [ ] Configure early stopping in Sweep
- [ ] Verify `dt` is **equal** in both configs
- [ ] Test on small budget first (5k evals)
- [ ] Monitor candidate rate (should be <0.1%)
- [ ] Monitor viable rate (should be >50%)

---

## Troubleshooting

### "Explorer finds too few candidates (<5)"

**Symptoms:**
```
attempts: 20000
candidates: 3
```

**Causes:**
- Thresholds too strict
- W too small (missing convergence)

**Fixes:**
- Lower `R_mean_lastW_min` by 0.05
- Increase `phase_var_lastW_max` by 0.02
- Increase `W` by 50-100

---

### "Explorer finds too many candidates (>50)"

**Symptoms:**
```
attempts: 20000
candidates: 80
viable_rate: 15%
```

**Causes:**
- Thresholds too permissive
- W too small (passing oscillations)

**Fixes:**
- Raise `R_mean_lastW_min` by 0.05
- Decrease `phase_var_lastW_max` by 0.02
- Increase `W` (counterintuitive but correct)

---

### "Sweep early-stops everything"

**Symptoms:**
```
early_stop_rate: 90%
viables: 1
```

**Causes:**
- Explorer-Sweep `dt` mismatch
- Sweep thresholds too strict
- Different parameter bins

**Fixes:**
- **Verify `dt` alignment** (most common)
- Lower Sweep `fail_if_R_mean_below`
- Increase `after_seeds` (give more chances)
- Check bin neighborhood settings

## Pipeline (full)
These run the entire sequence defined in the run_sequence file, honoring the `enabled` flags inside.

Ola2:
```
PYTHONPATH=src python3 -m olar.pipeline --sequence data/processed/ola2/config/run_sequence_ola2.json
```

Ola3:
```
PYTHONPATH=src python3 -m olar.pipeline --sequence data/processed/ola3/config/run_sequence_ola3.json
```

### Reset (start from zero outputs)
Use `--RESET` to delete all outputs generated by the pipeline for the Ola in the sequence (explorer, sweep/workers, merge, catalog, taxonomy, promote, reports).

```
PYTHONPATH=src python3 -m olar.pipeline \
  --sequence data/processed/ola3/config/run_sequence_ola3.json \
  --RESET
```

## Pipeline (partial steps)
You can run steps individually when needed.

Explorer only:
```
PYTHONPATH=src python3 -m olar.explorer --config data/processed/ola3/config/ola3_explorer.json
```

Dynamic sweep (central scheduler):
```
PYTHONPATH=src python3 -m olar.sweep_dynamic \
  --config data/processed/ola3/config/ola3_sweep_dynamic.json
```

Merge workers:
```
PYTHONPATH=src python3 scripts/merge_evaluations.py \
  --inputs data/processed/ola3/sweep_workers/worker_*/raw/evaluations.jsonl \
  --output data/processed/ola3/sweep_merged/evaluations.jsonl \
  --stats-output data/processed/ola3/sweep_merged/merge_stats.json
```

Catalog + taxonomy + promote (after merge):
```
PYTHONPATH=src python3 -m core.catalog.builder \
  --config data/processed/ola3/config/ola3_catalog_build.json

PYTHONPATH=src python3 -m core.taxonomy.builder \
  --config data/processed/ola3/config/ola3_taxonomy.json

PYTHONPATH=src python3 -m core.promotion.blocks_from_ola \
  --ola-from 3 --ola-to 4 \
  --run-inputs data/processed/ola3/config/ola3_promote_blocks.json
```

## Reports
Explorer report and sweep report are generated by the catalog build step:
- `data/processed/olaN/explorer_report.md`
- `data/processed/olaN/sweep_report.md`

Regenerate reports for Ola2:
```
PYTHONPATH=src python3 -m core.catalog.builder \
  --config data/processed/ola2/config/ola2_catalog_build.json
```

## Tools
Monitor sweep progress:
```
PYTHONPATH=src python3 scripts/monitor_sweep_progress.py \
  --shards-root data/processed/ola3/sweep_workers \
  --shard-count 12 \
  --sweep-config data/processed/ola3/config/ola3_sweep.json
```

Merge evaluations (manual):
```
PYTHONPATH=src python3 scripts/merge_evaluations.py \
  --inputs data/processed/ola3/sweep_workers/worker_*/raw/evaluations.jsonl \
  --output data/processed/ola3/sweep_merged/evaluations.jsonl \
  --stats-output data/processed/ola3/sweep_merged/merge_stats.json
```

## Notes
- The pipeline prints a step summary at start showing ENABLED/DISABLED steps.
- Explorer stops early if there are not enough blocks for the selected templates.
- For Ola3, inputs are the promoted outputs from Ola2:
  - `data/processed/ola2/promoted/simple_blocks.json`
  - `data/processed/ola2/promoted/dof_dna_catalog.csv`
