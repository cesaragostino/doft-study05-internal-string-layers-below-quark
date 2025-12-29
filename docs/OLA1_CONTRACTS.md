# OLA1 Contracts (I/O Only)

Rule of thumb: physics stays untouched; only pipeline/export/serialization/validation/reporting.

## Artifacts and Minimum Schemas

1) `study05_sweep_results.json` (from `ola1.run_sweep`)
   - Required top-level: `summary`, `runs`
   - Each run (in `runs`):
     - `run_id`
     - `theta_internal` (canonical parameters blob; no state)
     - `metrics` / summary fields as written by sweep (no contract changes here)

2) `study05_sweep_params.json` (from `ola1.run_sweep`)
   - Required top-level: `inputs`, `seed`, `engine_config_path`, `engine_config_hash`, `run_session_id`, `session_tag`

3) `*_all_runs_proxies.csv` (from `ola1.analyze_proxies`)
   - Required columns:
     - `run_id`
     - `omega_ref`
     - `R_S1_Q`, `R_S2_S1`, `R_S3_S2`
     - `g_couplings`, `memory_taus`, `memory_amps`, `memory_terms_by_layer`
     - Any columns consumed by `ola1.ola1_dof_dna_catalog` / `ola1.promote_simple_blocks`

4) `dof_dna_catalog.csv` (from `ola1.ola1_dof_dna_catalog`)
   - Required columns:
     - `run_id`
     - `dof_grade`, `dof_family_id`, `dof_family_friendly`
     - `genes_min` (stringified JSON if applicable)
     - `omega_ref_proxy`
     - `dna_cluster_id` (always present as a column)

5) `simple_blocks.json` (from `ola1.promote_simple_blocks`)
   - Required per-block fields:
     - `block_id`
     - `origin_run_id`
     - `omega_ref`
     - `theta_internal` (parameters blob; no state)

6) `hbar_sim_calibration.json` (from `ola1.hbar_sim_calibration`)
   - Required top-level: calibration payload as written by the script (no contract changes)

7) `*_ola1_report.md` (from `ola1.ola1_status_report`)
   - Informational only (no strict schema).

## Hard-Fail Policy

- Any exporter should fail if a required input file is missing or empty.
- Any exporter/adapter should fail if required fields are missing from input rows.
- Any adapter producing cross-OLA artifacts should fail if it cannot resolve required keys (e.g., `run_id` -> `origin_run_id` joins).

