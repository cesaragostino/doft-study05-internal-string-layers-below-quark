# Study05 – DOFT Internal Layers Simulator

Lightweight simulator of coupled oscillators with internal layers (S1, S2, optional S3) and an effective layer Q, following `docs/STUDY05_code_header_and_structures.md`.

## Layout
- Code: `src/study05/`
- Input draws/parameters and catalogs: `data/raw/` (e.g., `data/raw/sm_universe.json`, `data/raw/layer_states.yaml`)
- Engine/configs: `data/raw/engine_core3.json`, `data/raw/compound_templates.json`, `data/raw/wave1_blocks.json`, `data/raw/wave2_compounds.json`
- Processed results and plots: `data/processed/`
- Important digests/summaries: `data/processed/digest/`

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
- Stores parameters in `data/raw/<case>/global/study05_sweep_params.json`.
- Stores results in `data/processed/<case>/global/study05_sweep_results.json`.
- If you omit `--no-plots`, also writes plots to `data/processed/<case>/global/`.

Useful variations:
- `--case CaseB_3layers` to include S3.
- `--case CaseB_debug` to force a small setup biased toward S2 dominance for debugging locks/mixing.
- Tune `--n-*` for modes per layer (defaults: Q=3, S1=3, S2=2, S3=0) and `--max-complexity` (defaults to 10 per spec).
- Narrow the band back to `--band-max 3.0` after exploring mode density or widen for exploratory runs.
- Runs that blow up numerically/physically are flagged as unstable (not counted in spacing stats) to reflect non-confining configurations.

Family reports (write to processed by default):
```bash
PYTHONPATH=src python3 -m study05.report_families \
  --case CaseB_debug \
  --families Nucleon_like Rho_like Pion_like \
  --output data/processed/ola1/CaseB_debug/families
```
Reads per-family processed JSONs (under `data/processed/<case>/<family>/`) and writes comparative CSV/JSON + basic plots.

S2-friendly region analysis (post-processing only):
```bash
PYTHONPATH=src python3 -m study05.analyze_s2_region \
  --case CaseB_debug \
  --proxies-csv reports/CaseB_debug_pipeline/CaseB_debug_all_runs_proxies.csv \
  --first-energy-max 0.8 \
  --spacing-mean-min 0.45 \
  --nucleon-d-spacing-min 6.0 \
  --output reports/CaseB_debug_pipeline/s2_region
```
Generates a summary JSON, splits in/out CSVs, and basic plots showing where S2 is more likely in proxy space.

S2 threshold scan (post-processing only):
```bash
PYTHONPATH=src python3 -m study05.analyze_s2_scan \
  --proxies-csv reports/CaseB_debug_combined/CaseB_debug_all_runs_proxies.csv \
  --output reports/CaseB_debug_combined/s2_scan \
  --first-grid 0.6 0.7 0.8 0.9 \
  --spacing-grid 0.40 0.45 0.50 \
  --dspacing-grid 5.5 6.0 6.5
```
Produces `s2_scan_results.csv` with p(S2) and z-scores for each box.

Optional: logistic boundary fit
```bash
PYTHONPATH=src python3 -m study05.fit_s2_logit \
  --proxies-csv reports/CaseB_debug_combined/CaseB_debug_all_runs_proxies.csv \
  --output reports/CaseB_debug_combined/s2_logit
```

Ola1 (SM matching and block promotion):
1) Sweep with extended metrics (optional output root):
```bash
PYTHONPATH=src python3 -m study05.run_sweep \
  --case Core3L_Hadron \
  --runs 2000 \
  --seed 123 \
  --band-min 0.1 \
  --band-max 3.0 \
  --layer-states data/raw/layer_states.yaml \
  --engine-config data/raw/engine_core3.json \
  --no-plots
```
Notes: `layer_states.yaml` now uses relative thresholds (`T_Q_rel_min`, `T_S1_rel_min`, `T_S2_rel_min`) applied to the structural mass share of each layer; adjust there if you need to relax or tighten tiering.

2) Build proxies CSV (includes lock_quality, structure_tier, s2_state, s3_state):
```bash
PYTHONPATH=src python3 -m study05.analyze_proxies \
  --case Core3L_Hadron \
  --sm-universe data/raw/sm_universe.json \
  --output data/processed/ola1
```
Outputs land in `data/processed/Core3L_Hadron/combined/`.

3) Match against SM catalog (pion/rho/proton):
```bash
PYTHONPATH=src python3 -m study06.match_sm_ola1 \
  --proxies-csv data/processed/ola1/Core3L_Hadron_all_runs_proxies.csv \
  --sm-universe data/raw/sm_universe.json \
  --output data/processed/ola1 \
  --digest data/processed/digest/ola1
```
Writes full match table to processed and a digest copy of `best_match_per_run.csv` under `data/processed/digest/ola1/`.

4) Promote simple blocks:
```bash
PYTHONPATH=src python3 -m study06.promote_simple_blocks \
  --proxies-csv data/processed/ola1/Core3L_Hadron_all_runs_proxies.csv \
  --zoo-matches-csv data/processed/ola1/zoo_matches.csv \
  --sm-universe data/raw/sm_universe.json \
  --output data/processed/ola1/simple_blocks.json \
  --digest data/processed/digest/blocks
```
Promoted blocks are stored in processed and copied to `data/processed/digest/blocks/simple_blocks.json` for quick inspection.

5) Catalog complex cores (strong S2, level3):
```bash
PYTHONPATH=src python3 -m study06.catalog_complex_cores \
  --proxies-csv data/processed/ola1/Core3L_Hadron_all_runs_proxies.csv \
  --sm-universe data/raw/sm_universe.json \
  --output data/processed/ola1/complex_cores.json
```

Ola2 (compounds + viability):
```bash
# build compounds with physical stitching of blocks
PYTHONPATH=src python3 -m study06.run_ola2_compounds \
  --blocks-json data/processed/ola1/simple_blocks.json \
  --wave2-config data/raw/wave2_compounds.json \
  --sm-universe data/raw/sm_universe.json \
  --templates-json data/raw/compound_templates.json \
  --output-root data/processed/ola2

# label viability (example for proton)
PYTHONPATH=src python3 -m study06.label_ola2_viability \
  --compounds-csv data/processed/ola2/compounds_proton.csv \
  --output data/processed/ola1/ola2/viability_proton.csv \
  --d-yes 0.25 \
  --d-possible 0.45 \
  --min-structure-tier level2 \
  --allowed-s2-states latent structural
```

Pipeline runner (uses `data/raw/sequence.json`):
```bash
PYTHONPATH=src python3 -m study06.run_pipeline --sequence data/raw/sequence.json
```
