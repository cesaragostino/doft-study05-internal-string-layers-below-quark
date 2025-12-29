# OLA1 Freeze Manifest

Publicable / reproducible manifest for Ola1 artifacts.

## Commit + Date

- git_commit: 3e02cdb32a4f0e87004bd74431feb7d6bbfe9635
- timestamp_utc: (fill at freeze time)

## Sweep Params (reference)

- study05_sweep_params.json:
  - path: `data/processed/ola1/<case>/global/study05_sweep_params.json`
  - sha256: (fill at freeze time)

## Hashes (config / code / inputs)

- config_hash: (engine_config_hash from run_sweep)
- code_hash: (sha256 of `src/ola1/run_sweep.py`)
- inputs_hash: (sha256 of inputs payload used by run_sweep)

## Outputs + Hashes (sha256)

- `data/processed/ola1/<case>/global/runs_full.jsonl` → sha256:
- `data/processed/ola1/<case>/global/all_attempts.jsonl` → sha256:
- `data/processed/ola1/<case>/global/study05_sweep_results.json` → sha256:
- `data/processed/ola1/<case>/global/study05_sweep_params.json` → sha256:
- `data/processed/ola1/Ola1_3-2-5_all_runs_proxies.csv` → sha256:
- `data/processed/ola1/dof_dna_catalog.csv` → sha256:
- `data/processed/ola1/dof_dna_catalog_by_block_id.csv` → sha256:
- `data/processed/ola1/simple_blocks_canonical.json` → sha256:
- `data/processed/ola1/hbar_sim_calibration.json` → sha256:
- `data/processed/ola1/*_ola1_report.md` → sha256:

## Validation

- `scripts/validate_outputs.py` (hard-fail)

## Notes

- `runs_full.jsonl` and `all_attempts.jsonl` are append-only.
- Canonical blocks and DNA are keyed by `block_id = "ola1_" + sha256(origin_run_id)[:16]`.
