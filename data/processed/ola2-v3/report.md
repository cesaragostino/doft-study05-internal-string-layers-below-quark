# Ola2 Structure Explorer Report

## Run Header
- run_id: 10913f41-23c1-407f-8ac8-47b3f2a42446
- started_utc: 2025-12-22T05:03:24Z
- finished_utc: 2025-12-22T05:27:31Z
- duration_seconds: 1446.46
- attempts_path: data/processed/ola2-v3/attempts.jsonl
- attempts_size_mb: 262.06
- config_path: data/raw/structure_explorer_v3.json
- config_sha256: sha256:c83a7bb31f2fb7ff7c07b2661c3bdffac9511177683eeae9efbec386e64cc4b6
- templates_path: data/raw/compound_templates_v3.json
- templates_sha256: sha256:9446c95d382c585ef29ed1fe4bc80edeb59231f92dc3cf7d2cc90c4c62180cf4
- inputs.blocks_mode: ola1_blocks
- inputs.blocks_json: data/processed/ola1/simple_blocks.json

## Targets Used
| target_name | templates | allowed_block_families | budget_evals |
| --- | --- | --- | --- |
| meson_explore__any | ['meson_dimer'] | [] | 15000 |
| meson_explore__delta_like | ['meson_dimer'] | ['delta_like'] | 8000 |
| meson_explore__charmed_meson | ['meson_dimer'] | ['charmed_meson'] | 8000 |
| baryon_explore__any | ['baryon_triangle'] | [] | 15000 |
| baryon_explore__delta_like | ['baryon_triangle'] | ['delta_like'] | 8000 |
| baryon_explore__mixed | ['baryon_triangle'] | ['delta_like', 'charmed_meson', 'unknown'] | 8000 |

## Templates Used
| template_name | nodes | edges | notes |
| --- | --- | --- | --- |
| meson_dimer | 2 | 1 | meson_complex |
| baryon_triangle | 3 | 3 | baryon |

- edge_weight_policy: sample_discrete
- edge_weight_levels: [0.5, 1.0, 2.0]

## Universe Summary
- total_attempts: 61130
- unique_structures: 32734
- viable_attempts: 23392 (38.27%)
- rejected_attempts: 37738 (61.73% )
- best_attempt: structure_id=86e0da4a8ca27a0156e1c28fe52b2ae548e72d9767a3304a645c1729f8ce1e69 template=meson_dimer target=meson_explore__any
  R_mean_lastW=0.999847173293132 phase_var_lastW=6.858310817972225e-08 memory_score_k10=0.9900449603875671 QualityLock=0.9994366677325148 entropy_quality=0.9955012351664977 omega_eff=0.2056872781789792
- top_reasons: [('high_phase_variance', 36547), ('low_coherence', 32294), ('low_R_final', 29016), ('memory_non_positive', 13639), ('low_quality_lock', 12168)]

## Phase Breakdown
| phase | attempts | viable_rate | unique |
| --- | --- | --- | --- |
| phase1 | 43400 | 27.73% | 32734 |
| phase2 | 17730 | 64.07% | 1773 |

- seed_repeats_per_structure: 10
- param_neighbor_bins: 2
- promising_rule: {'min_R_mean_lastW': 0.8, 'max_phase_var_lastW': 0.03, 'min_memory_score_k10': 0.0}

## Taxonomy & Tags
### Attractor Class
| attractor_class | count | pct |
| --- | --- | --- |
| COHERENT_LOCKED | 23392 | 38.27% |
| DRIFT_BOUNDED | 37738 | 61.73% |

### Grade
| grade | count | pct |
| --- | --- | --- |
| A | 23392 | 38.27% |
| C | 37738 | 61.73% |

### Tags
| tag | count | pct |
| --- | --- | --- |
| ZOMBIE | 13639 | 22.31% |

ZOMBIE rule: memory_score_k10 <= 0

## Histograms
### R_mean_lastW
- 0-0.5: 6280
- 0.5-0.7: 23113
- 0.7-0.85: 2901
- 0.85-0.9: 1501
- 0.9-0.95: 3070
- 0.95-0.98: 4577
- 0.98-1.0: 19688
- 1.0+: 0

### phase_var_lastW
- 0-1e-6: 3405
- 1e-6-1e-4: 5806
- 1e-4-1e-3: 5204
- 1e-3-1e-2: 7695
- 1e-2-1e-1: 7404
- 1e-1+: 31616

### memory_score_k10
- [-inf,-10): 971
- [-10,-1): 4027
- [-1,0): 8641
- [0,0.5): 11932
- [0.5,0.8): 12192
- [0.8,1.0): 23367
- [1.0,inf): 0

### omega_eff
- 0-0.5: 38247
- 0.5-1: 7329
- 1-2: 12667
- 2-5: 2887
- 5-10: 0
- 10-20: 0
- 20+: 0

### entropy_quality
- 0-0.2: 0
- 0.2-0.4: 0
- 0.4-0.6: 0
- 0.6-0.8: 0
- 0.8-0.9: 0
- 0.9-1.0: 61130
- 1.0+: 0

## LS View Settings
- max_den: 31
- epsilon_rel: 0.001
- attempts_with_LS: 41393
### Top LS Hashes
- 84f2b00b2c1814bfec00d0b739b3a872cb28ff1f7ca12bdf85b23709e3f5f36e: 4347
- 120359163c88ede1aefbf0892480efd2876be834e881543f132c732b2e103619: 1653
- 599b6f943458436c41b9056ae26955f5858f08f5a054de4ef42a8926854b1130: 530
- 391e90fcea76f4f1d639c7f65ffeb636b938e2903c2c16059b106f7d5279c7d1: 473
- 43d994d3f36b47367e5bdc2d4d2dcd4545ff12c27f98cc4153c45bbe0f830ff9: 95
- 99db5023aaade45329ed3f75e25c90444ebea04105d9f5c7a51cfc0ec538fde2: 92
- 567fb6080dd1f532c3f54a7f151f100818c47b4c220ad8a41132f9c38b90d1c9: 85
- 96ff9434cf1b8c7e642e7786cc8b9f626f2a850661cf1d5c4be9dce1adcf267c: 84
- 6dab9044a9a2bdb6b9d0b08e4dc62a9dd61d372672e2968d450392fb557eefc9: 83
- 55949b45ead810febbf93d008a22c35e4173cabb668ba4d41490e5b5d7b907b5: 77

## Template Stats
| template_name | nodes | attempts | unique | viable_rate | best_R | best_memory |
| --- | --- | --- | --- | --- | --- | --- |
| meson_dimer | 2 | 30130 | 11044 | 44.75% | 0.999847173293132 | 0.9900449603875671 |
| baryon_triangle | 3 | 31000 | 21690 | 31.96% | 0.999964350388843 | 0.9891304287559314 |

## Target Stats
| target_name | templates | attempts | unique | viable_rate | notes |
| --- | --- | --- | --- | --- | --- |
| meson_explore__any | ['meson_dimer'] | 15000 | 10500 | 33.01% |  |
| meson_explore__delta_like | ['meson_dimer'] | 8000 | 328 | 76.20% | includes delta_like |
| meson_explore__charmed_meson | ['meson_dimer'] | 7130 | 216 | 34.17% | includes charmed_meson |
| baryon_explore__any | ['baryon_triangle'] | 15000 | 10500 | 16.31% |  |
| baryon_explore__delta_like | ['baryon_triangle'] | 8000 | 5595 | 73.11% | includes delta_like |
| baryon_explore__mixed | ['baryon_triangle'] | 8000 | 5595 | 20.16% | includes delta_like,charmed_meson,unknown |

## Species Catalog (Top 20 by seed_stability)
| species_id | template | trials | seed_stability | omega_eff | memory | entropy_quality | QualityLock | zombie_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4d1fee68e9e3cf5c4bd6805aa8a3a5997196473a56b065cb3d0e20619f5606bf | meson_dimer | 26 | 1.000 | 0.02139675726988788 | 0.9859845837322541 | 0.9867468032138121 | 0.9980752982745029 | 0.11538461538461539 |
| 973269878a03e1a85bfd87d7f4b0a700921a5a1e14d435445aa27c0e9679af5f | meson_dimer | 23 | 1.000 | 0.09961401088322225 | 0.9767733919729158 | 0.9899737571647029 | 0.9986541469542466 | 0.08695652173913043 |
| 4e6de464bea03be63ec186f4b3532e55456caf30ac54aa4747dcc344baaa0f2c | meson_dimer | 19 | 1.000 | 0.22817167656771004 | 0.9853439996134101 | 0.9957953738340841 | 0.9994934409662739 | 0.05263157894736842 |
| 5d98d0ed7040bb5b41b87e0e4545a3c78093ce7c5c28868b6787d5ac660c3867 | meson_dimer | 16 | 1.000 | 0.2590775324665177 | 0.9581298754180544 | 0.9942735498674111 | 0.999276586130746 | 0.0 |
| 647a0a4015bfbe8fa6366a30dfdb260995bb21aded3cea3eb3468656c7264151 | meson_dimer | 15 | 1.000 | 0.23107883980691174 | 0.9706676521210681 | 0.9964059677588679 | 0.9995419477125598 | 0.0 |
| 03a8b7b60725c4801db2ae82862e880706785ee2082b8799c8d6bed86ff33b21 | meson_dimer | 11 | 1.000 | 0.0875043752127942 | 0.9220181965954823 | 0.9979035398400122 | 0.9997661938765823 | 0.09090909090909091 |
| 6bbe538177c2c38bbd5d247637bdbfe7179efafca49c9bc43bfce5e0639dfee0 | meson_dimer | 11 | 1.000 | 0.11431610518837103 | 0.8473183031215233 | 0.995770022859129 | 0.999492922482971 | 0.09090909090909091 |
| c0cea301cc6ccd87c463d231739dc41af3d39dc3b2a140b443d405a71aed70bb | meson_dimer | 11 | 1.000 | 0.02082385689394979 | 0.863978190648507 | 0.9958958502891719 | 0.9994926828704751 | 0.09090909090909091 |
| 2051f223c1b391feceb5a635122de0024a24dcd671e64dacab4c3c32aa918412 | meson_dimer | 11 | 1.000 | 0.10456608228559551 | 0.9628773796544124 | 0.996369194382744 | 0.9995581573487737 | 0.0 |
| 8dba2c75feca1bfaa2e72f299fce7abe1a7c4c77326b296e1fce648192761321 | meson_dimer | 11 | 1.000 | 0.00369818445796815 | 0.9755129882481626 | 0.9962697944689477 | 0.9995364865680445 | 0.09090909090909091 |
| ff836af928b4b2ca7fcd12de76f170e99b572b4d2ff9a271f697217a66e65733 | meson_dimer | 11 | 1.000 | 0.0751377085461486 | 0.9516937207232897 | 0.9943478314589586 | 0.9992316591993478 | 0.09090909090909091 |
| 005f15a52706f09bcc0817fb7589b6b1a6bc4342c5510dbe58611de28e34e581 | meson_dimer | 11 | 1.000 | 0.24845038787742227 | 0.9645790582907617 | 0.9966897686733804 | 0.9996022787994645 | 0.09090909090909091 |
| 44080932a65d9194d4f3e6a6b4cbf7873d23e0e92d53ec0ad25608d81d8b746c | meson_dimer | 11 | 1.000 | 0.09316827141420636 | 0.9724615975304263 | 0.9970428195708245 | 0.9996647615797528 | 0.09090909090909091 |
| f2d45aa24eb635cf3fffb0620daf407119de96e634d0e9e7127ff9ea221b41df | meson_dimer | 11 | 1.000 | 0.013275606444500295 | 0.93413001088111 | 0.9922837133086411 | 0.9989144217586515 | 0.09090909090909091 |
| 205893213656c35efe77919428cf6f60209e86e7c9f0650581e1b97fc7eb5f9f | meson_dimer | 11 | 1.000 | 0.17722703013379537 | 0.9383535809096818 | 0.995502895517288 | 0.9994527379877273 | 0.0 |
| 0d7305716cefc9c7030c13d8aa371f6d66eb7ad06dd82dfd5ee2843f2ae50041 | meson_dimer | 11 | 1.000 | 0.21451535457227058 | 0.9547337792481352 | 0.9932767686258286 | 0.9990959456345448 | 0.0 |
| 1bb9c248d310e2fe8e88f7e29aa7cd0a62a55b39fc07f1038090316aaef365cd | meson_dimer | 11 | 1.000 | 0.34156948626918854 | 0.9121858114831837 | 0.9953871947779751 | 0.999431230353413 | 0.0 |
| bb14497dbe3b897895fb12cd18d0abcfdef0ebfd23f5dfe1afa528b73eba39c5 | meson_dimer | 11 | 1.000 | 0.251458686919979 | 0.9698739669913595 | 0.9992740833650307 | 0.49992293318343173 | 0.09090909090909091 |
| f87e78ee75f56f4865310d4578ca9bf75a4e886b709bd03158c1ae99f782a7c1 | meson_dimer | 11 | 1.000 | 0.007699826477190193 | 0.9752263531831784 | 0.9968187639834805 | 0.9996213173673916 | 0.0 |
| 7df8d786d873055ee3615d2f1970a9ebc07cf979a547d866cd2a8ca34771034d | meson_dimer | 11 | 1.000 | 0.031488337843367846 | 0.9264426099623931 | 0.9973065412866146 | 0.999681599723028 | 0.09090909090909091 |

## Config Snapshot
```json
{
  "schema_version": "ola2_structure_explorer_v3",
  "inputs": {
    "blocks_json": "data/processed/ola1/simple_blocks.json",
    "templates_json": "data/raw/compound_templates_v3.json",
    "dof_dna_catalog_csv": "data/processed/ola1/dof_dna_catalog.csv",
    "species_catalog_jsonl": "data/processed/ola2-v3/species_catalog.jsonl",
    "blocks_mode": "ola1_blocks"
  },
  "targets": [
    {
      "name": "meson_explore__any",
      "templates": [
        "meson_dimer"
      ],
      "allowed_block_families": [],
      "budget_evals": 15000
    },
    {
      "name": "meson_explore__delta_like",
      "templates": [
        "meson_dimer"
      ],
      "allowed_block_families": [
        "delta_like"
      ],
      "budget_evals": 8000
    },
    {
      "name": "meson_explore__charmed_meson",
      "templates": [
        "meson_dimer"
      ],
      "allowed_block_families": [
        "charmed_meson"
      ],
      "budget_evals": 8000
    },
    {
      "name": "baryon_explore__any",
      "templates": [
        "baryon_triangle"
      ],
      "allowed_block_families": [],
      "budget_evals": 15000
    },
    {
      "name": "baryon_explore__delta_like",
      "templates": [
        "baryon_triangle"
      ],
      "allowed_block_families": [
        "delta_like"
      ],
      "budget_evals": 8000
    },
    {
      "name": "baryon_explore__mixed",
      "templates": [
        "baryon_triangle"
      ],
      "allowed_block_families": [
        "delta_like",
        "charmed_meson",
        "unknown"
      ],
      "budget_evals": 8000
    }
  ],
  "engine_defaults": {
    "dt": 1,
    "T_ticks": 120,
    "W": 20,
    "K_local": 0.15,
    "kappa_global": 0.25,
    "tau_field": 20,
    "sigma0": 0.3,
    "sigma_tc": 60,
    "sigma_theta_init": 0.5
  },
  "engine_variation": {
    "enabled": true,
    "mode": "bin_sample",
    "bins": {
      "K_local_edges": [
        0.0,
        0.1,
        0.2,
        0.4
      ],
      "kappa_edges": [
        0.0,
        0.1,
        0.2,
        0.4
      ],
      "tau_field_edges": [
        5,
        10,
        20,
        40,
        80
      ],
      "sigma0_edges": [
        0.0,
        0.1,
        0.2,
        0.3,
        0.5
      ],
      "sigma_tc_edges": [
        10,
        30,
        60,
        120,
        240
      ]
    }
  },
  "coupling_mode": {
    "mode": "absolute",
    "alpha_range": [
      0.2,
      20.0
    ],
    "beta_range": [
      0.05,
      5.0
    ],
    "omega_floor": 1e-12,
    "sample": "log_uniform"
  },
  "templates": {
    "weighted_edges": true,
    "edge_weight_levels": [
      0.5,
      1.0,
      2.0
    ],
    "edge_weight_policy": "sample_discrete"
  },
  "tagging": {
    "R_mean_lastW_min": 0.85,
    "phase_var_lastW_max": 0.02,
    "memory_score_k10_min": 0.0,
    "R_final_min": 0.9,
    "quality_lock_min": 0.8,
    "viability_mode": "hard_viable_soft_memory"
  },
  "search_policy": {
    "phase1_fraction": 0.7,
    "phase2_fraction": 0.3,
    "phase1": {
      "prefer_novel_structures": true,
      "template_balance": "round_robin",
      "max_repeats_per_structure": 1
    },
    "phase2": {
      "promising_rule": {
        "min_R_mean_lastW": 0.8,
        "max_phase_var_lastW": 0.03,
        "min_memory_score_k10": 0.0
      },
      "seed_repeats_per_structure": 10,
      "param_neighbor_bins": 2
    },
    "priority_scoring": {
      "score": "R_mean_lastW - 3.0*phase_var_lastW + 0.2*memory_score_k10"
    }
  },
  "canonicalization": {
    "enabled": true,
    "method": "template_automorphisms_lexmin",
    "block_key": "block_id"
  },
  "progress": {
    "term_attempts": 500,
    "term_seconds": 10
  },
  "outputs": {
    "attempts_jsonl": "attempts.jsonl",
    "species_catalog_jsonl": "species_catalog.jsonl",
    "report_md": "report.md",
    "views_enabled": true
  }
}
```

## Templates Snapshot
```json
[
  {
    "name": "singlet",
    "type": "elementary",
    "nodes": 1,
    "edges": [],
    "allowed_block_families": [
      "lepton",
      "gauge_boson",
      "nucleus",
      "match_any",
      "quark_like"
    ]
  },
  {
    "name": "meson_dimer",
    "type": "meson_complex",
    "nodes": 2,
    "edges": [
      [
        0,
        1
      ]
    ],
    "allowed_block_families": [
      "pion_like",
      "rho_like",
      "kaon_like",
      "quark_like"
    ]
  },
  {
    "name": "baryon_triangle",
    "type": "baryon",
    "nodes": 3,
    "edges": [
      [
        0,
        1
      ],
      [
        1,
        2
      ],
      [
        2,
        0
      ]
    ],
    "allowed_block_families": [
      "quark_like",
      "pion_like",
      "rho_like"
    ]
  },
  {
    "name": "nucleus_cluster",
    "type": "nucleus",
    "nodes": 4,
    "edges": [
      [
        0,
        1
      ],
      [
        1,
        2
      ],
      [
        2,
        0
      ],
      [
        0,
        3
      ],
      [
        1,
        3
      ],
      [
        2,
        3
      ]
    ],
    "allowed_block_families": [
      "nucleus",
      "baryon",
      "pion_like"
    ]
  }
]
```
