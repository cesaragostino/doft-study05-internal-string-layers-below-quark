# Informe Ola1 – Ola1_3-2-5

## Semáforo de salud
- Runs totales: 4
- Runs aceptados: 4 (100.0%)
- Alertas: ninguna

## Entropía / Caos (nuevo)
- Fuente de datos: partial_runs
- Runs con entropy_chaos: 4
- chaos_mode: dynamic=4, ensemble=0
- PE_tick_norm (mean/med/min/max): 0.702 / 0.689 / 0.585 / 0.845
- T_ticks (mean/med/min/max): 200.0 / 200.0 / 200 / 200
- mean_H_lock_norm (mean/med): 0.007 / 0.006
- mixture_entropy_blocks_norm (mean/med): 0.000 / -0.000
- structure_mix_norm (mean/med): 0.250 / 0.000
- fraction_structured (mean/med): 0.125 / 0.000

## Energía interna (E_internal)
- Runs con E_internal: 4 / 4
- E_internal runs (mean/med/min/max): 0.000712328 / 7.12979e-05 / 2.4973e-05 / 0.00268174
- Bloques con internal_energy: 4 / 4
- internal_energy bloques (mean/med/min/max): 0.000712328 / 7.12979e-05 / 2.4973e-05 / 0.00268174
- mass_sim_gev bloques (mean/med/min/max): 0.556548 / 0.561005 / 0.430948 / 0.673234

## Proxies de masa/lock (unidades internas)
| run | particle | family | omega_ref | M_spec | M1 | M2 | M3 |
|-----|----------|--------|-----------|--------|----|----|----|
| 3 | delta_1232 | delta_like | 1.017e+01 | 1.017e+01 | 1.001e+00 | 1.018e+01 | 3.102e+00 |
| 1 | deuteron | nucleus | 6.956e+00 | 6.956e+00 | 2.003e+00 | 1.393e+01 | 4.331e+00 |
| 0 | eta_prime | eta_prime_like | 6.577e+00 | 6.577e+00 | 4.001e+00 | 2.632e+01 | 1.088e+01 |
| 2 | quark_ud_const | quark_like | 1.028e+01 | 1.028e+01 | 1.475e+00 | 1.515e+01 | 2.336e+00 |

## Energía calibrada por bloque
- No se pudo construir la tabla (falta internal_energy, mass_gev o sm_mass_gev).

## Error de masa vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| delta_1232 | +62.3377% | +62.3377% | +62.3377% | 1 |
| deuteron | +3.8978% | +3.8978% | +3.8978% | 1 |
| eta_prime | +10.2086% | +10.2086% | +10.2086% | 1 |
| quark_ud_const | -11.3475% | -11.3475% | -11.3475% | 1 |

## Error de mass_sim vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| delta_1232 | -45.9217% | -45.9217% | -45.9217% | 1 |
| deuteron | -75.7004% | -75.7004% | -75.7004% | 1 |
| eta_prime | -55.0055% | -55.0055% | -55.0055% | 1 |
| quark_ud_const | +100.3672% | +100.3672% | +100.3672% | 1 |

## Promedio cósmico (Ola1)
- cosmic_chaos_temp (PE avg): 0.7019
- cosmic_disorder (H_mean avg): 0.0072

## Caos/desorden por run
| Run ID | PE_tick_norm | mean_H_lock_norm |
|--------|--------------|------------------|
| 0 | 0.5853 | 0.0029 |
| 1 | 0.6845 | 0.0145 |
| 2 | 0.8454 | 0.0026 |
| 3 | 0.6925 | 0.0087 |

## Inventario (cosecha)
| Partícula | Cantidad | Mejor d_total | Promedio d_total |
|-----------|----------|---------------|------------------|
| delta_1232 | 1 | 7.680 | 7.680 |
| deuteron | 1 | 7.312 | 7.312 |
| eta_prime | 1 | 0.976 | 0.976 |
| quark_ud_const | 1 | 0.321 | 0.321 |

## Detalle por partícula (d_total y conteos)
| Partícula | Count | d_min | d_med | d_max | Tiers | S2 states |
|-----------|-------|-------|-------|-------|-------|-----------|
| delta_1232 | 1 | 7.680 | 7.680 | 7.680 | level1:1 | none:1 |
| deuteron | 1 | 7.312 | 7.312 | 7.312 | level1:1 | latent:1 |
| eta_prime | 1 | 0.976 | 0.976 | 0.976 | level1:1 | none:1 |
| quark_ud_const | 1 | 0.321 | 0.321 | 0.321 | none:1 | none:1 |

## Radar del Zoo (d_total < 5.0) no aceptados
Sin candidatos cercanos fuera de la selección.

## Pareto de rechazos (causas en selección)
No hay registros de rechazo (o no se encontró el log).

## Bloques aceptados con métricas de entropía/caos
### delta_1232_block_0001 (run_id=3)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.680
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [2.0]
- F_m (base): 2.000 GeV
- M_eff (base≈F_m): 2.000
- M_corrected (F_m*(1-H_block)): 1.983 (H_block=0.009)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +62.3377%
- mass_sim_gev: 0.666245
- Δ_mass_sim vs SM: -45.9217%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6924876100995664, T_ticks=200
- mean_H_lock_norm=0.00867515381022412, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0324 / 0.0002 / 0.2708

### quark_ud_const_block_0001 (run_id=2)
- Partícula: quark_ud_const, tier: none, s2_state: none
- match_score.d_total: 0.321
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [0.29787234042553196, 2.0]
- F_m (base): 0.298 GeV
- M_eff (base≈F_m): 0.298
- M_corrected (F_m*(1-H_block)): 0.110 (H_block=0.632)
- sm_mass_gev: 0.336
- Δ_mass vs SM: -11.3475%
- mass_sim_gev: 0.673234
- Δ_mass_sim vs SM: +100.3672%
- H_block (lock_quality): 0.632
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.845416153988296, T_ticks=200
- mean_H_lock_norm=0.0026361000375823467, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=1.0
- fraction_structured=0.5
- lock_S1_series (mean/min/max): 0.9960 / 0.9916 / 0.9987

### deuteron_block_0001 (run_id=1)
- Partícula: deuteron, tier: level1, s2_state: latent
- match_score.d_total: 7.312
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9487179487179487, 1.9999999999999998]
- F_m (base): 1.949 GeV
- M_eff (base≈F_m): 1.949
- M_corrected (F_m*(1-H_block)): 1.920 (H_block=0.015)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.8978%
- mass_sim_gev: 0.455765
- Δ_mass_sim vs SM: -75.7004%
- H_block (lock_quality): 0.015
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6845438224083286, T_ticks=200
- mean_H_lock_norm=0.014525308311905797, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0001 / 0.0013

### eta_prime_block_0001 (run_id=0)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.976
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.0555555555555556, 1.9444444444444446, 2.0, 2.055555555555556]
- F_m (base): 1.056 GeV
- M_eff (base≈F_m): 1.056
- M_corrected (F_m*(1-H_block)): 1.052 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +10.2086%
- mass_sim_gev: 0.430948
- Δ_mass_sim vs SM: -55.0055%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.585332879330038, T_ticks=200
- mean_H_lock_norm=0.002860883825820061, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0063 / 0.0005 / 0.0197

- M2 (omega_ref*V_lock*D_stat): 10.1768
- M3 (omega_ref*V_lock*rho_lock): 3.10234
- M2 (omega_ref*V_lock*D_stat): 15.153
- M3 (omega_ref*V_lock*rho_lock): 2.33623
- M2 (omega_ref*V_lock*D_stat): 13.9307
- M3 (omega_ref*V_lock*rho_lock): 4.33068
- M2 (omega_ref*V_lock*D_stat): 26.3166
- M3 (omega_ref*V_lock*rho_lock): 10.8814