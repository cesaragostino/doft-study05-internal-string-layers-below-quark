# Informe Ola1 – Ola1_3-2-5

## Semáforo de salud
- Runs totales: 6
- Runs aceptados: 6 (100.0%)
- Alertas: ninguna

## Entropía / Caos (nuevo)
- Fuente de datos: partial_runs
- Runs con entropy_chaos: 6
- chaos_mode: dynamic=6, ensemble=0
- PE_tick_norm (mean/med/min/max): 0.613 / 0.597 / 0.466 / 0.893
- T_ticks (mean/med/min/max): 201.0 / 201.0 / 201 / 201
- mean_H_lock_norm (mean/med): 0.006 / 0.004
- mixture_entropy_blocks_norm (mean/med): 0.000 / -0.000
- structure_mix_norm (mean/med): 0.000 / 0.000
- fraction_structured (mean/med): 0.000 / 0.000

## Energía interna (E_internal)
- Runs con E_internal: 6 / 6
- E_internal runs (mean/med/min/max): 0.00233791 / 0.000127683 / 1.48695e-06 / 0.0110075
- Bloques con internal_energy: 6 / 6
- internal_energy bloques (mean/med/min/max): 0.00233791 / 0.000127683 / 1.48695e-06 / 0.0110075
- mass_sim_gev bloques (mean/med/min/max): 2.88454 / 3.04351 / 1.87561 / 3.75622

## Proxies de masa/lock (unidades internas)
| run | particle | family | omega_ref | M_spec | M1 | M2 | M3 |
|-----|----------|--------|-----------|--------|----|----|----|
| 0 | meson_d_star_zero | charmed_meson | 1.232e+01 | 1.232e+01 | 1.100e+01 | 1.356e+02 | 7.224e+01 |
| 1 | meson_d_star_zero | charmed_meson | 6.904e+00 | 6.904e+00 | 1.101e+01 | 7.603e+01 | 2.990e+01 |
| 3 | meson_d_star_zero | charmed_meson | 1.015e+01 | 1.015e+01 | 1.201e+01 | 1.219e+02 | 4.920e+01 |
| 4 | meson_d_star_zero | charmed_meson | 1.143e+01 | 1.143e+01 | 1.200e+01 | 1.372e+02 | 6.616e+01 |
| 5 | meson_d_star_zero | charmed_meson | 9.820e+00 | 9.820e+00 | 1.100e+01 | 1.081e+02 | 4.192e+01 |
| 2 | meson_ds | charmed_meson | 6.154e+00 | 6.154e+00 | 1.200e+01 | 7.387e+01 | 7.860e+00 |

## Energía calibrada por bloque
- No se pudo construir la tabla (falta internal_energy, mass_gev o sm_mass_gev).

## Error de mass_sim_used vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| meson_d_star_zero | +53.7896% | +4.8497% | +87.1701% | 5 |
| meson_ds | -4.7116% | -4.7116% | -4.7116% | 1 |

## Masa por frecuencia (mass_sim_used_gev)
| run | particle | family | omega_ref_raw | omega_ref_used | mass_sim_used_gev | rel_err_vs_SM | guard |
|-----|----------|--------|--------------|----------------|------------------|---------------|-------|
| 0 | meson_d_star_zero | charmed_meson | 12.324 | 12.324 | 3.75622 | +0.8717 | no |
| 1 | meson_d_star_zero | charmed_meson | 6.90368 | 6.90368 | 2.10418 | +0.0485 | no |
| 3 | meson_d_star_zero | charmed_meson | 10.1511 | 10.1511 | 3.09395 | +0.5417 | no |
| 4 | meson_d_star_zero | charmed_meson | 11.4315 | 11.4315 | 3.4842 | +0.7362 | no |
| 5 | meson_d_star_zero | charmed_meson | 9.8201 | 9.8201 | 2.99307 | +0.4914 | no |
| 2 | meson_ds | charmed_meson | 6.15377 | 6.15377 | 1.87561 | -0.0471 | no |

* = harmonic-guard aplicado

## Harmonic Structure vs SM Quantum Numbers (v1 proxy)
Proceed with v1 using only the stored main FFT peak (plus km1/kp1 if frequency is available) and band_energies anchor. Evidence is score-based (not power-based).
dominant_k, dominant_parity, sector_confidence_v1 computed from k-matching scores (k_tol=0.07, k in 1..5). odd/even evidence fractions are sums of scores.

### By family
| family | count | odd_frac_mean | even_frac_mean | odd_dominant_frac |
|--------|-------|---------------|----------------|-------------------|
| charmed_meson | 6 | 0.479 | 0.521 | 0.500 |

### By J^PC
| jpc | count | odd_frac_mean | even_frac_mean | odd_dominant_frac |
|-----|-------|---------------|----------------|-------------------|
| 0- | 1 | 1.000 | 0.000 | 1.000 |
| 1- | 5 | 0.374 | 0.626 | 0.400 |

### Top 10 particles by odd evidence
| particle | odd_evidence_frac | even_evidence_frac |
|----------|-------------------|--------------------|
| meson_ds | 1.000 | 0.000 |
| meson_d_star_zero | 0.374 | 0.626 |

### Top 10 particles by even evidence
| particle | odd_evidence_frac | even_evidence_frac |
|----------|-------------------|--------------------|
| meson_d_star_zero | 0.374 | 0.626 |
| meson_ds | 1.000 | 0.000 |

## Promedio cósmico (Ola1)
- cosmic_chaos_temp (PE avg): 0.6134
- cosmic_disorder (H_mean avg): 0.0058

## Caos/desorden por run
| Run ID | PE_tick_norm | mean_H_lock_norm |
|--------|--------------|------------------|
| 0 | 0.4655 | 0.0032 |
| 1 | 0.6017 | 0.0126 |
| 2 | 0.8933 | 0.0028 |
| 3 | 0.5931 | 0.0083 |
| 4 | 0.5163 | 0.0032 |
| 5 | 0.6103 | 0.0045 |

## Inventario (cosecha)
| Partícula | Cantidad | Mejor d_total | Promedio d_total |
|-----------|----------|---------------|------------------|
| meson_d_star_zero | 5 | 0.354 | 0.419 |
| meson_ds | 1 | 0.604 | 0.604 |

## Detalle por partícula (d_total y conteos)
| Partícula | Count | d_min | d_med | d_max | Tiers | S2 states |
|-----------|-------|-------|-------|-------|-------|-----------|
| meson_d_star_zero | 5 | 0.354 | 0.399 | 0.548 | level1:5 | latent:1, none:4 |
| meson_ds | 1 | 0.604 | 0.604 | 0.604 | level1:1 | none:1 |

## Radar del Zoo (d_total < 5.0) no aceptados
Sin candidatos cercanos fuera de la selección.

## Harmonic Policy Rejects (tagger)
Sin rechazos por política armónica.

## Pareto de rechazos (causas en selección)
No hay registros de rechazo (o no se encontró el log).

## Bloques aceptados con métricas de entropía/caos
### meson_d_star_zero_block_0001 (run_id=5)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.409
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.994729907773386, 1.997364953886693, 2.0, 2.0026350461133067, 2.005270092226614, 2.007905138339921, 2.010540184453228, 2.013175230566535, 2.015810276679842, 2.018445322793149, 2.021080368906456]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.986 (H_block=0.004)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.99307
- omega_ref_raw: 9.8201
- first_energy: 1.99473
- harmonic_ratio: 1.500
- err_raw_vs_sm: 0.491
- err_fix_vs_sm: 0.006
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +49.1429%
- H_block (lock_quality): 0.004
- band_power_capture: 0.16516101139845044
- chaos_mode=dynamic, PE_tick_norm=0.6103003305028971, T_ticks=201
- mean_H_lock_norm=0.004493286341759505, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0036 / 0.0011 / 0.0070

### meson_d_star_zero_block_0002 (run_id=1)
- Partícula: meson_d_star_zero, tier: level1, s2_state: latent
- match_score.d_total: 0.385
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9954389965792474, 1.9977194982896243, 2.0, 2.002280501710376, 2.0045610034207524, 2.0068415051311295, 2.0091220068415057, 2.0114025085518814, 2.013683010262258, 2.0159635119726342, 2.0182440136830104]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.970 (H_block=0.013)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.10418
- omega_ref_raw: 6.90368
- first_energy: 1.99544
- harmonic_ratio: 1.054
- err_raw_vs_sm: 0.048
- err_fix_vs_sm: 0.006
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +4.8497%
- H_block (lock_quality): 0.013
- band_power_capture: 0.1683220935751636
- chaos_mode=dynamic, PE_tick_norm=0.6017195977935832, T_ticks=201
- mean_H_lock_norm=0.012613196227817923, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0009 / 0.0006 / 0.0011

### meson_d_star_zero_block_0003 (run_id=0)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.399
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9950248756218902, 1.9975124378109448, 2.0, 2.0024875621890548, 2.004975124378109, 2.007462686567164, 2.0099502487562186, 2.0124378109452734, 2.014925373134328, 2.017412935323383, 2.0199004975124377]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.989 (H_block=0.003)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 3.75622
- omega_ref_raw: 12.324
- first_energy: 1.99502
- harmonic_ratio: 1.883
- err_raw_vs_sm: 0.872
- err_fix_vs_sm: 0.006
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +87.1701%
- H_block (lock_quality): 0.003
- band_power_capture: 0.16760328959879653
- chaos_mode=dynamic, PE_tick_norm=0.4655412777286469, T_ticks=201
- mean_H_lock_norm=0.0031920479875085493, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0079 / 0.0005 / 0.0213

### meson_ds_block_0001 (run_id=2)
- Partícula: meson_ds, tier: level1, s2_state: none
- match_score.d_total: 0.604
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9861111111111112, 1.9930555555555556, 1.9999999999999998, 2.006944444444444, 2.013888888888889, 2.020833333333333, 2.0277777777777777, 3.333333333333333, 3.3402777777777777, 3.347222222222222, 3.3541666666666665, 3.3611111111111107]
- F_m (base): 1.986 GeV
- M_eff (base≈F_m): 1.986
- M_corrected (F_m*(1-H_block)): 1.981 (H_block=0.003)
- sm_mass_gev: 1.968
- mass_sim_raw_gev: 1.87561
- omega_ref_raw: 6.15377
- first_energy: 1.98611
- harmonic_ratio: 0.944
- err_raw_vs_sm: 0.047
- err_fix_vs_sm: 0.009
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: -4.7116%
- H_block (lock_quality): 0.003
- band_power_capture: 0.20428979189290092
- chaos_mode=dynamic, PE_tick_norm=0.8933003893794171, T_ticks=201
- mean_H_lock_norm=0.002766425889241407, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.9907 / 0.9660 / 0.9977

### meson_d_star_zero_block_0004 (run_id=3)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.354
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9963898916967506, 1.9981949458483754, 2.0, 2.0018050541516246, 2.003610108303249, 2.0054151624548737, 2.007220216606498, 2.0090252707581224, 2.0108303249097474, 2.0126353790613716, 2.0144404332129966, 2.0162454873646207]
- F_m (base): 1.996 GeV
- M_eff (base≈F_m): 1.996
- M_corrected (F_m*(1-H_block)): 1.980 (H_block=0.008)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 3.09395
- omega_ref_raw: 10.1511
- first_energy: 1.99639
- harmonic_ratio: 1.550
- err_raw_vs_sm: 0.542
- err_fix_vs_sm: 0.005
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +54.1697%
- H_block (lock_quality): 0.008
- band_power_capture: 0.16303090732763015
- chaos_mode=dynamic, PE_tick_norm=0.5930597289965321, T_ticks=201
- mean_H_lock_norm=0.008347151006301881, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0079 / 0.0007 / 0.0211

### meson_d_star_zero_block_0005 (run_id=4)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.548
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9905660377358492, 1.9952830188679247, 2.0, 2.0047169811320757, 2.0094339622641515, 2.014150943396227, 2.0188679245283025, 2.023584905660378, 2.028301886792453, 2.0330188679245285, 2.037735849056604, 2.0424528301886795]
- F_m (base): 1.991 GeV
- M_eff (base≈F_m): 1.991
- M_corrected (F_m*(1-H_block)): 1.984 (H_block=0.003)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 3.4842
- omega_ref_raw: 11.4315
- first_energy: 1.99057
- harmonic_ratio: 1.750
- err_raw_vs_sm: 0.736
- err_fix_vs_sm: 0.008
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +73.6155%
- H_block (lock_quality): 0.003
- band_power_capture: 0.16302040693834596
- chaos_mode=dynamic, PE_tick_norm=0.516348136180885, T_ticks=201
- mean_H_lock_norm=0.0031717388704359784, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0020 / 0.0007 / 0.0048

- M2 (omega_ref*V_lock*D_stat): 108.068
- M3 (omega_ref*V_lock*rho_lock): 41.9248
- M2 (omega_ref*V_lock*D_stat): 76.0289
- M3 (omega_ref*V_lock*rho_lock): 29.8989
- M2 (omega_ref*V_lock*D_stat): 135.605
- M3 (omega_ref*V_lock*rho_lock): 72.2442
- M2 (omega_ref*V_lock*D_stat): 73.8653
- M3 (omega_ref*V_lock*rho_lock): 7.8596
- M2 (omega_ref*V_lock*D_stat): 121.909
- M3 (omega_ref*V_lock*rho_lock): 49.1956
- M2 (omega_ref*V_lock*D_stat): 137.22
- M3 (omega_ref*V_lock*rho_lock): 66.1561