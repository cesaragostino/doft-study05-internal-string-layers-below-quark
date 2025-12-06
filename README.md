# Study05 – DOFT Internal Layers Simulator

Lightweight simulator of coupled oscillators with internal layers (S1, S2, optional S3) and an effective layer Q, following `docs/STUDY05_code_header_and_structures.md`.

## Layout
- Code: `src/study05/`
- Input draws/parameters: `data/raw/<case>/`
- Processed results and plots: `data/processed/<case>/`

## Requirements
- Python 3.8+ with `numpy`; `matplotlib` is optional (only needed for plots).

## Full workflow (generate data)
From the repo root:
```bash
PYTHONPATH=src python3 -m study05.run_sweep \
  --case CaseA_2layers \
  --runs 50 \
  --seed 123 \
  --band-min 0.0 \
  --band-max 5.0
```
This:
- Stores parameters in `data/raw/<case>/study05_sweep_params.json`.
- Stores results in `data/processed/<case>/study05_sweep_results.json`.
- If you omit `--no-plots`, also writes plots to `data/processed/<case>/`.

Useful variations:
- `--case CaseB_3layers` to include S3.
- `--case CaseB_debug` to force a small setup biased toward S2 dominance for debugging locks/mixing.
- Family-conditioned sweeps: add `--family-config data/raw/config/<file>.json` (or `--family-name Nucleon_like/Rho_like/Pion_like` if placed in that folder) to focus parameter ranges and match spacings for that family; summary will report family match counts and S2 involvement.
- Tune `--n-*` for modes per layer (defaults: Q=3, S1=3, S2=2, S3=0) and `--max-complexity` (defaults to 10 per spec).
- Narrow the band back to `--band-max 3.0` after exploring mode density or widen for exploratory runs.
- Runs that blow up numerically/physically are flagged as unstable (not counted in spacing stats) to reflect non-confining configurations.

Family reports:
```bash
PYTHONPATH=src python3 -m study05.report_families \
  --case CaseB_debug \
  --families Nucleon_like Rho_like Pion_like \
  --output reports/CaseB_debug_families
```
Reads per-family processed JSONs (under `data/processed/<case>/<family>/`) and writes comparative CSV/JSON + basic plots in `reports/CaseB_debug_families/`.
