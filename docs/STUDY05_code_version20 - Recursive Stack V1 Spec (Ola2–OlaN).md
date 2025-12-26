# DOFT Recursive Stack V1 Spec (Ola2–OlaN)

## 0. Scope

### 0.1 Goal

Build a generic, configuration-driven system for ola2–olaN that:

- explores candidate structures cheaply (**Explorer**),
- delineates and measures robustness locally (**Sweep**),
- produces a DOFT-only genome (DNA) and DOFT families/taxonomy,
- supports recursion: entities from olaX become blocks for ola(X+1),
- supports pause/resume safely via append-only raw logs and rebuildable catalogs.

### 0.2 Non-goals (V1)

- Do not modify `ola1.run_sweep` or the Ola1 engine behavior.
- Do not provide backward compatibility with old file formats.
- Do not require SM to run (SM integration is optional and external).

---

## 1. Repository Layout

### 1.1 Code directories

**MUST** create/maintain these directories:

```
src/core/
  engine/        # simulation engine shared by Explorer & Sweep
  io/            # append-only JSONL writers, resume index, schema validation
  ids/           # hashing, canonicalization, provenance hashing
  templates/     # template registry + canonical topology signature
  genome/        # genome layers, lineage merge rules
  taxonomy/      # DOFT taxonomy, bins, thresholds, versioning
  catalog/       # catalog builder, rollups

src/ola1/        # frozen legacy producer

src/olar/        # ola-recursive (ola2–olaN)
  explorer.py
  sweep.py
  pipeline.py
  schemas.py

src/sm/          # optional, external SM integration
```

### 1.2 Naming rule

**MUST NOT** use the word `wave` in filenames, modules, config schemas, or docs.  
Use **ola** consistently.

---

## 2. Config Organization

### 2.1 Config directories

```
data/config/run_sequence.json
data/config/ola1/
data/config/ola2/
...
data/config/olaN/
data/config/sm/        # optional
```

### 2.2 Per-ola config naming

For each ola X:

```
olaX_explorer.json
olaX_sweep.json
olaX_taxonomy.json
```

### 2.3 `run_sequence.json` (orchestrator)

- Defines a list of steps
- Each step references **one config file**
- CLI flags allowed **only as overrides**

---

## 3. Data Contracts (Recursion Interfaces)

### 3.1 Block Contract

Required fields:

- `block_id: str`
- `omega_ref: float`
- `dof_grade: {A,B,C,REJECTED}`
- `dof_family_id: str`
- `dof_family_friendly: str`
- `genes_min: object`
- `provenance: object`

### 3.2 Entity Contract

Required fields:

- `entity_id: str`
- `ola: int`
- `build_plan`
- `template_name`
- `canonical_node_order`
- `edges`
- `assignment`
- `parent_ids: list[str]`
- `provenance`

### 3.3 Evaluation Contract (JSONL, append-only)

Required fields:

- `eval_id`
- `entity_id`
- `role: {explorer,sweep}`
- `seed`
- `engine_params`
- `engine_params_bin_id`
- `metrics_raw`
- `tags_raw`
- `timestamp_utc`
- `provenance`

### 3.4 Genome Layer Contract

Required fields:

- `entity_id`
- `ola`
- lineage fields
- `genes_inherited`
- `genes_olaX`
- `robustness_*`
- taxonomy fields
- `taxonomy_version`

---

## 4. ID and Provenance

### 4.1 Required hashes

- `config_hash`
- `code_hash`
- `inputs_hash`
- machine metadata

### 4.2 Hash policy

- **entity_id** → canonical build plan only
- **eval_id** → `(entity_id, seed, param_bin_id, role, schema_version)`

---

## 5. Explorer (`src/olar/explorer.py`)

### 5.1 Purpose

Cheap global search. No scientific validation.

### 5.2 Inputs

- blocks source
- DOFT DNA catalog
- templates
- block selection rules
- engine defaults + variation
- tagging thresholds

### 5.3 Outputs

Append-only:

```
attempts.jsonl
entities_candidates.jsonl (optional)
```

---

## 6. Sweep (`src/olar/sweep.py`)

### 6.1 Purpose

Local robustness delineation.

### 6.2 Inputs

- candidates
- deterministic seed policy
- neighborhood rules
- evaluation budgets

### 6.3 Outputs

Append-only:

```
evaluations.jsonl
```

---

## 7. Catalog Builder

### Purpose

Deterministic rebuild from raw logs.

### Outputs

```
entities.jsonl
genome_layers_olaX.csv
rollups.json
```

Deleting `catalog/` must be safe.

---

## 8. DOFT Taxonomy

- DOFT-only
- versioned bins/thresholds
- provisional vs confirmed families

---

## 9. Recursion Rule

### Entity → Block promotion

```
block_id = entity_id
omega_ref = selected proxy
```

Lineage **must** be preserved.

---

## 10. Resume / Safety

- Append-only JSONL
- Optional resume index

---

## 11. Seed Policy

### Explorer

Deterministic or small N.

### Sweep

```
seed_i = hash(entity_id, i, "sweep")
```

---

## Deliverables Checklist

- core + olar structure
- schemas
- explorer
- sweep
- catalog builder
- taxonomy
- recursion support
- run_sequence orchestrator

---

## Appendix A — Minimal `run_sequence.json`

```json
{
  "schema_version": "doft_run_sequence_v1",
  "run_name": "doft_v1_ola2_minimal",
  "output_root": "data/processed",
  "steps": [
    {"id": "ola1_export_dna", "type": "ola1_export_dna", "config": "data/config/ola1/ola1_export_dna.json", "enabled": true},
    {"id": "ola2_explorer", "type": "olar_explorer", "config": "data/config/ola2/ola2_explorer.json", "enabled": true},
    {"id": "ola2_sweep", "type": "olar_sweep", "config": "data/config/ola2/ola2_sweep.json", "enabled": true},
    {"id": "ola2_catalog_build", "type": "core_catalog_build", "config": "data/config/ola2/ola2_catalog_build.json", "enabled": true},
    {"id": "ola2_taxonomy", "type": "core_taxonomy", "config": "data/config/ola2/ola2_taxonomy.json", "enabled": true}
  ]
}
```
# Appendices — Minimal Ola 2 Configs (V1)

> **Note:** JSON blocks are copied verbatim (no content changes).  
> Spanish prose has been translated to English where applicable.

---

## Appendix B — Minimal `ola2_explorer.json`

```json
{
  "schema_version": "olar_explorer_config_v1",
  "ola": 2,

  "inputs": {
    "blocks_json": "data/processed/ola1/simple_blocks.json",
    "dof_dna_catalog_csv": "data/processed/ola1/dof_dna_catalog.csv",
    "templates_json": "data/config/ola2/ola2_templates.json"
  }, 

  "targets": [
    {
      "name": "global_blind_search_full_topology",
      "templates": ["bipartite_3_6", "decagon_ring", "ladder_5"],
      "budget_evals": 200000,
      "notes": "Minimal mixed-topology search."
    }
  ],

  "block_selection": {
    "block_id_key": "block_id",
    "require_dna": true,
    "allowed_dof_grades": ["A", "B"],
    "allowed_family_ids": [],
    "denied_family_ids": []
  },

  "engine_defaults": {
    "dt": 1.0,
    "T_ticks": 200,
    "W": 20,
    "K_local": 0.45,
    "kappa_global": 0.30,
    "tau_field": 120.0,
    "sigma0": 0.30,
    "sigma_tc": 60.0,
    "sigma_theta_init": 0.5
  },

  "engine_variation": {
    "enabled": true,
    "mode": "bin_sample",
    "bins": {
      "K_local_edges": [0.2, 0.4, 0.6, 0.8],
      "kappa_edges": [0.1, 0.2, 0.4, 0.6],
      "tau_field_edges": [40, 80, 120, 160, 240],
      "sigma0_edges": [0.1, 0.3, 0.5],
      "sigma_tc_edges": [40, 60, 90, 120]
    }
  },

  "seed_policy": {
    "mode": "deterministic",
    "salt": "explorer_v1",
    "seeds_per_attempt": 1
  },

  "tagging_thresholds": {
    "R_mean_lastW_min": 0.80,
    "phase_var_lastW_max": 0.05,
    "quality_lock_min": 0.75,
    "memory_score_k10_min": 0.0,
    "viability_mode": "hard_viable_soft_memory"
  },

  "outputs": {
    "raw_dir": "data/processed/ola2/raw",
    "attempts_jsonl": "data/processed/ola2/raw/attempts.jsonl",
    "entities_candidates_jsonl": "data/processed/ola2/raw/entities_candidates.jsonl",
    "report_md": "data/processed/ola2/report.md"
  },

  "progress": {
    "flush_every_evals": 500,
    "log_every_terms": 10
  }
}
```

---

## Appendix C — Minimal `ola2_sweep.json`

```json
{
  "schema_version": "olar_sweep_config_v1",
  "ola": 2,

  "inputs": {
    "attempts_jsonl": "data/processed/ola2/raw/attempts.jsonl",
    "entities_candidates_jsonl": "data/processed/ola2/raw/entities_candidates.jsonl"
  },

  "candidate_source": {
    "mode": "attempts",
    "filter": {
      "require_quality_lock_ok": true,
      "require_memory_non_negative": false,
      "min_quality_lock": 0.80,
      "min_R_mean_lastW": 0.70,
      "max_phase_var_lastW": 0.20,
      "top_k_by": "priority_score",
      "top_k": 2000
    }
  },

  "seed_policy": {
    "mode": "deterministic",
    "salt": "sweep_v1",
    "seeds": 12,
    "min_seeds_required": 8
  },

  "neighborhood": {
    "mode": "param_bin_neighbors",
    "max_neighbor_bins": 3
  },

  "budgets": {
    "max_evals_per_entity": 120,
    "early_stop": {
      "enabled": true,
      "after_seeds": 4,
      "fail_if_R_mean_below": 0.40
    }
  },

  "outputs": {
    "raw_dir": "data/processed/ola2/raw",
    "evaluations_jsonl": "data/processed/ola2/raw/evaluations.jsonl",
    "report_md": "data/processed/ola2/sweep_report.md"
  }
}
```

---

## Appendix D — Minimal `ola2_catalog_build.json`

```json
{
  "schema_version": "core_catalog_build_v1",
  "ola": 2,

  "inputs": {
    "attempts_jsonl": "data/processed/ola2/raw/attempts.jsonl",
    "evaluations_jsonl": "data/processed/ola2/raw/evaluations.jsonl",
    "templates_json": "data/config/ola2/ola2_templates.json"
  },

  "outputs": {
    "catalog_dir": "data/processed/ola2/catalog",
    "entities_jsonl": "data/processed/ola2/catalog/entities.jsonl",
    "genome_layer_csv": "data/processed/ola2/catalog/genome_layers_ola2.csv",
    "rollups_json": "data/processed/ola2/catalog/rollups.json"
  }
}
```

---

## Appendix E — Minimal `ola2_taxonomy.json`

```json
{
  "schema_version": "core_taxonomy_config_v1",
  "ola": 2,
  "taxonomy_version": "ola2_taxonomy_v1",

  "inputs": {
    "genome_layer_csv": "data/processed/ola2/catalog/genome_layers_ola2.csv",
    "entities_jsonl": "data/processed/ola2/catalog/entities.jsonl"
  },

  "thresholds": {
    "kingdom_order": ["ZOMBIE", "LOCKED", "SOFT_LOCK", "DRIFT", "CHAOTIC"],
    "locked_requires_min_seeds": 2,
    "locked_min_quality_lock": 0.95,
    "locked_min_R_mean_lastW": 0.90,
    "locked_max_phase_var_lastW": 0.02
  },

  "family_bins": {
    "use_bins_for_id": true,
    "notes": "Bins affect only stable grouping/hash; raw metrics are always stored.",
    "bins": {
      "R_mean_lastW_edges": [0.70, 0.85, 0.95, 0.985],
      "entropy_quality_edges": [0.97, 0.985, 0.995],
      "memory_score_k10_edges": [0.0, 0.2, 0.5, 0.8],
      "phase_var_lastW_edges": [0.0005, 0.005, 0.02, 0.1]
    }
  },

  "outputs": {
    "genome_layer_out_csv": "data/processed/ola2/catalog/genome_layers_ola2_taxonomy.csv",
    "taxonomy_rollups_json": "data/processed/ola2/catalog/taxonomy_rollups.json"
  }
}
```

---

## Appendix F — Minimal `ola2_templates.json` (starter set)

```json
{
  "schema_version": "olar_templates_v1",
  "templates": [
    {
      "name": "bipartite_3_6",
      "nodes": 9,
      "edges": [
        [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8],
        [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8],
        [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8]
      ],
      "edge_weights_mode": "fixed_template"
    },
    {
      "name": "decagon_ring",
      "nodes": 10,
      "edges": [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,0]],
      "edge_weights_mode": "fixed_template"
    },
    {
      "name": "ladder_5",
      "nodes": 10,
      "edges": [
        [0,1],[1,2],[2,3],[3,4],
        [5,6],[6,7],[7,8],[8,9],
        [0,5],[1,6],[2,7],[3,8],[4,9]
      ],
      "edge_weights_mode": "fixed_template"
    }
  ]
}
```

---

## `data/config/doft_run_inputs_v1.json`

```json
{
  "schema_version": "doft_run_inputs_v1",

  "inputs": {
    "ola1": {
      "simple_blocks_json": "data/processed/ola1/simple_blocks.json",
      "dof_dna_catalog_csv": "data/processed/ola1/dof_dna_catalog.csv",
      "provenance_json": "data/processed/ola1/provenance_ola1_export.json"
    },

    "sm_audit_optional": {
      "enabled": true,
      "sm_universe_json": "data/raw/sm_universe.json",
      "hbar_sim_calibration_json": "data/raw/hbar_sim_calibration.json"
    }
  },

  "outputs": {
    "root": "data/processed",
    "by_ola": {
      "ola2": "data/processed/ola2",
      "ola3": "data/processed/ola3"
    }
  },

  "identity": {
    "block_id_key": "block_id",
    "require_dna_for_blocks": true
  }
}
```

---

## Notes (minimal but important)

These examples assume you already produce:

- `data/processed/ola1/simple_blocks.json`
- `data/processed/ola1/dof_dna_catalog.csv`

Additional clarifications:

- `allowed_family_ids` empty means **“no restriction.”**
- `require_dna: true` means the Explorer **errors** if a block lacks DOF DNA.

---

## Output convention (so it “works for everything”)

For each ola **N**, fix these standard paths:

### Explorer

- `data/processed/olaN/raw/attempts.jsonl`
- `data/processed/olaN/raw/entities_candidates.jsonl`
- `data/processed/olaN/report.md`

### Sweep

- `data/processed/olaN/raw/evaluations.jsonl`
- `data/processed/olaN/sweep_report.md`

### Optional SM audit

- `data/processed/olaN/sm/sm_trace.jsonl`
- `data/processed/olaN/sm/sm_report.md`
