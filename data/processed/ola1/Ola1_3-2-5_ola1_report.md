# Informe Ola1 – Ola1_3-2-5

## Semáforo de salud
- Runs totales: 2
- Runs aceptados: 2 (100.0%)
- Alertas: ninguna

## Entropía / Caos (nuevo)
- Fuente de datos: partial_runs
- Runs con entropy_chaos: 2
- chaos_mode: dynamic=2, ensemble=0
- PE_tick_norm (mean/med/min/max): 0.635 / 0.635 / 0.585 / 0.685
- T_ticks (mean/med/min/max): 200.0 / 200.0 / 200 / 200
- mean_H_lock_norm (mean/med): 0.009 / 0.009
- mixture_entropy_blocks_norm (mean/med): 0.000 / -0.000
- structure_mix_norm (mean/med): 0.000 / 0.000
- fraction_structured (mean/med): 0.000 / 0.000

## Energía interna (E_internal)
- Runs con E_internal: 2 / 2
- E_internal runs (mean/med/min/max): 7.12979e-05 / 7.12979e-05 / 5.67161e-05 / 8.58796e-05
- Bloques con internal_energy: 2 / 2
- internal_energy bloques (mean/med/min/max): 7.12979e-05 / 7.12979e-05 / 5.67161e-05 / 8.58796e-05
- mass_sim_gev bloques (mean/med/min/max): 1.46132 / 1.46132 / 1.04702 / 1.87561

## Proxies de masa/lock (unidades internas)
| run | particle | family | omega_ref | M_spec | M1 | M2 | M3 |
|-----|----------|--------|-----------|--------|----|----|----|
| 0 | delta_1950 | delta_like | 1.196e+01 | 1.196e+01 | 1.800e+01 | 2.153e+02 | 8.901e+01 |
| 1 | meson_ds | charmed_meson | 6.674e+00 | 6.674e+00 | 1.502e+01 | 1.003e+02 | 3.114e+01 |

## Energía calibrada por bloque
- No se pudo construir la tabla (falta internal_energy, mass_gev o sm_mass_gev).

## Error de mass_sim_used vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| delta_1950 | -3.8149% | -3.8149% | -3.8149% | 1 |
| meson_ds | -46.8072% | -46.8072% | -46.8072% | 1 |

## Masa por frecuencia (mass_sim_used_gev)
| run | particle | family | omega_ref_raw | omega_ref_used | mass_sim_used_gev | rel_err_vs_SM | guard |
|-----|----------|--------|--------------|----------------|------------------|---------------|-------|
| 0 | delta_1950 | delta_like | 11.9556 | 11.9556 | 1.87561 | -0.0381 | no |
| 1 | meson_ds | charmed_meson | 6.67397 | 6.67397 | 1.04702 | -0.4681 | no |

* = harmonic-guard aplicado

## Harmonic Structure vs SM Quantum Numbers (v1 proxy)
Proceed with v1 using only the stored main FFT peak (plus km1/kp1 if frequency is available) and band_energies anchor. Evidence is score-based (not power-based).
dominant_k, dominant_parity, sector_confidence_v1 computed from k-matching scores (k_tol=0.07, k in 1..5). odd/even evidence fractions are sums of scores.

### By family
| family | count | odd_frac_mean | even_frac_mean | odd_dominant_frac |
|--------|-------|---------------|----------------|-------------------|
| charmed_meson | 1 | 1.000 | 0.000 | 1.000 |
| delta_like | 1 | 1.000 | 0.000 | 1.000 |

### By J^PC
| jpc | count | odd_frac_mean | even_frac_mean | odd_dominant_frac |
|-----|-------|---------------|----------------|-------------------|
| 0- | 1 | 1.000 | 0.000 | 1.000 |
| 7/2+ | 1 | 1.000 | 0.000 | 1.000 |

### Top 10 particles by odd evidence
| particle | odd_evidence_frac | even_evidence_frac |
|----------|-------------------|--------------------|
| delta_1950 | 1.000 | 0.000 |
| meson_ds | 1.000 | 0.000 |

### Top 10 particles by even evidence
| particle | odd_evidence_frac | even_evidence_frac |
|----------|-------------------|--------------------|
| meson_ds | 1.000 | 0.000 |
| delta_1950 | 1.000 | 0.000 |

## Promedio cósmico (Ola1)
- cosmic_chaos_temp (PE avg): 0.6349
- cosmic_disorder (H_mean avg): 0.0091

## Caos/desorden por run
| Run ID | PE_tick_norm | mean_H_lock_norm |
|--------|--------------|------------------|
| 0 | 0.5853 | 0.0028 |
| 1 | 0.6845 | 0.0155 |

## Inventario (cosecha)
| Partícula | Cantidad | Mejor d_total | Promedio d_total |
|-----------|----------|---------------|------------------|
| delta_1950 | 1 | 0.081 | 0.081 |
| meson_ds | 1 | 0.172 | 0.172 |

## Detalle por partícula (d_total y conteos)
| Partícula | Count | d_min | d_med | d_max | Tiers | S2 states |
|-----------|-------|-------|-------|-------|-------|-----------|
| delta_1950 | 1 | 0.081 | 0.081 | 0.081 | level1:1 | none:1 |
| meson_ds | 1 | 0.172 | 0.172 | 0.172 | level1:1 | latent:1 |

## Radar del Zoo (d_total < 5.0) no aceptados
Sin candidatos cercanos fuera de la selección.

## Pareto de rechazos (causas en selección)
No hay registros de rechazo (o no se encontró el log).

## Bloques aceptados con métricas de entropía/caos
### delta_1950_block_0001 (run_id=0)
- Partícula: delta_1950, tier: level1, s2_state: none
- match_score.d_total: 0.081
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.945945945945946, 1.9729729729729732, 2.0, 2.027027027027027, 2.0540540540540544, 2.081081081081081, 3.702702702702703, 3.7297297297297303, 3.7567567567567575, 3.7837837837837847, 3.810810810810811, 3.837837837837838, 3.8648648648648654, 3.891891891891892, 3.918918918918919, 3.9459459459459465, 3.9729729729729737, 4.0]
- F_m (base): 1.946 GeV
- M_eff (base≈F_m): 1.946
- M_corrected (F_m*(1-H_block)): 1.940 (H_block=0.003)
- sm_mass_gev: 1.950
- mass_sim_raw_gev: 1.87561
- omega_ref_raw: 11.9556
- first_energy: 1.94595
- harmonic_ratio: 0.964
- err_raw_vs_sm: 0.038
- err_fix_vs_sm: 0.002
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: -3.8149%
- H_block (lock_quality): 0.003
- band_power_capture: 0.1605959891761886
- chaos_mode=dynamic, PE_tick_norm=0.585332879330038, T_ticks=200
- mean_H_lock_norm=0.0027586947795524433, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0063 / 0.0005 / 0.0197

### meson_ds_block_0001 (run_id=1)
- Partícula: meson_ds, tier: level1, s2_state: latent
- match_score.d_total: 0.172
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.973154362416107, 1.9865771812080533, 1.9999999999999998, 2.013422818791946, 2.026845637583892, 2.040268456375838, 2.053691275167785, 2.0671140939597312, 2.0805369127516773, 2.0939597315436234, 2.1073825503355703, 2.1208053691275164, 2.1342281879194624, 2.147651006711409, 2.1610738255033555]
- F_m (base): 1.973 GeV
- M_eff (base≈F_m): 1.973
- M_corrected (F_m*(1-H_block)): 1.943 (H_block=0.016)
- sm_mass_gev: 1.968
- mass_sim_raw_gev: 1.04702
- omega_ref_raw: 6.67397
- first_energy: 1.97315
- harmonic_ratio: 0.531
- err_raw_vs_sm: 0.468
- err_fix_vs_sm: 0.002
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: -46.8072%
- H_block (lock_quality): 0.016
- band_power_capture: 0.13918874113004487
- chaos_mode=dynamic, PE_tick_norm=0.6845438224083286, T_ticks=200
- mean_H_lock_norm=0.015484560203796972, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0001 / 0.0013

- M2 (omega_ref*V_lock*D_stat): 215.26
- M3 (omega_ref*V_lock*rho_lock): 89.0149
- M2 (omega_ref*V_lock*D_stat): 100.251
- M3 (omega_ref*V_lock*rho_lock): 31.135