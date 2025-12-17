# Informe Ola1 – Ola1_3-2-5

## Semáforo de salud
- Runs totales: 6
- Runs aceptados: 6 (100.0%)
- Alertas: ninguna

## Entropía / Caos (nuevo)
- Fuente de datos: partial_runs
- Runs con entropy_chaos: 6
- chaos_mode: dynamic=6, ensemble=0
- PE_tick_norm (mean/med/min/max): 0.731 / 0.721 / 0.585 / 0.845
- T_ticks (mean/med/min/max): 200.0 / 200.0 / 200 / 200
- mean_H_lock_norm (mean/med): 0.006 / 0.004
- mixture_entropy_blocks_norm (mean/med): 0.000 / -0.000
- structure_mix_norm (mean/med): 0.167 / 0.000
- fraction_structured (mean/med): 0.083 / 0.000

## Energía interna (E_internal)
- Runs con E_internal: 6 / 6
- E_internal runs (mean/med/min/max): 0.000529866 / 0.00011895 / 2.4973e-05 / 0.00268174
- Bloques con internal_energy: 6 / 6
- internal_energy bloques (mean/med/min/max): 0.000529866 / 0.00011895 / 2.4973e-05 / 0.00268174
- mass_sim_gev bloques (mean/med/min/max): 0.90487 / 0.983409 / 0.642678 / 1.13604

## Proxies de masa/lock (unidades internas)
| run | particle | family | omega_ref | M_spec | M1 | M2 | M3 |
|-----|----------|--------|-----------|--------|----|----|----|
| 3 | delta_1232 | delta_like | 1.017e+01 | 1.017e+01 | 1.001e+00 | 1.018e+01 | 3.102e+00 |
| 1 | deuteron | nucleus | 6.956e+00 | 6.956e+00 | 2.003e+00 | 1.393e+01 | 4.331e+00 |
| 0 | eta_prime | eta_prime_like | 6.577e+00 | 6.577e+00 | 4.001e+00 | 2.632e+01 | 1.088e+01 |
| 4 | eta_prime | eta_prime_like | 1.163e+01 | 1.163e+01 | 2.001e+00 | 2.326e+01 | 5.795e+00 |
| 5 | eta_prime | eta_prime_like | 9.960e+00 | 9.960e+00 | 4.002e+00 | 3.986e+01 | 6.916e+00 |
| 2 | quark_ud_const | quark_like | 1.028e+01 | 1.028e+01 | 1.475e+00 | 1.515e+01 | 2.336e+00 |

## Energía calibrada por bloque
- No se pudo construir la tabla (falta internal_energy, mass_gev o sm_mass_gev).

## Error de masa vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| delta_1232 | +62.3377% | +62.3377% | +62.3377% | 1 |
| deuteron | +3.8978% | +3.8978% | +3.8978% | 1 |
| eta_prime | +16.3622% | +9.9033% | +28.9747% | 3 |
| quark_ud_const | -11.3475% | -11.3475% | -11.3475% | 1 |

## Error de mass_sim vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| delta_1232 | -19.3524% | -19.3524% | -19.3524% | 1 |
| deuteron | -63.7618% | -63.7618% | -63.7618% | 1 |
| eta_prime | -4.2245% | -32.8992% | +18.6117% | 3 |
| quark_ud_const | +198.8097% | +198.8097% | +198.8097% | 1 |

## Promedio cósmico (Ola1)
- cosmic_chaos_temp (PE avg): 0.7306
- cosmic_disorder (H_mean avg): 0.0062

## Caos/desorden por run
| Run ID | PE_tick_norm | mean_H_lock_norm |
|--------|--------------|------------------|
| 0 | 0.5853 | 0.0029 |
| 1 | 0.6845 | 0.0145 |
| 2 | 0.8454 | 0.0026 |
| 3 | 0.6925 | 0.0087 |
| 4 | 0.7499 | 0.0041 |
| 5 | 0.8257 | 0.0044 |

## Inventario (cosecha)
| Partícula | Cantidad | Mejor d_total | Promedio d_total |
|-----------|----------|---------------|------------------|
| delta_1232 | 1 | 7.680 | 7.680 |
| deuteron | 1 | 7.312 | 7.312 |
| eta_prime | 3 | 0.946 | 1.565 |
| quark_ud_const | 1 | 0.321 | 0.321 |

## Detalle por partícula (d_total y conteos)
| Partícula | Count | d_min | d_med | d_max | Tiers | S2 states |
|-----------|-------|-------|-------|-------|-------|-----------|
| delta_1232 | 1 | 7.680 | 7.680 | 7.680 | level1:1 | none:1 |
| deuteron | 1 | 7.312 | 7.312 | 7.312 | level1:1 | latent:1 |
| eta_prime | 3 | 0.946 | 0.976 | 2.773 | level1:3 | none:3 |
| quark_ud_const | 1 | 0.321 | 0.321 | 0.321 | none:1 | none:1 |

## Radar del Zoo (d_total < 5.0) no aceptados
Sin candidatos cercanos fuera de la selección.

## Pareto de rechazos (causas en selección)
No hay registros de rechazo (o no se encontró el log).

## Bloques aceptados con métricas de entropía/caos
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
- mass_sim_gev: 0.679687
- Δ_mass_sim vs SM: -63.7618%
- H_block (lock_quality): 0.015
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6845438224083286, T_ticks=200
- mean_H_lock_norm=0.014525308311905797, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0001 / 0.0013

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
- mass_sim_gev: 1.004
- Δ_mass_sim vs SM: +198.8097%
- H_block (lock_quality): 0.632
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.845416153988296, T_ticks=200
- mean_H_lock_norm=0.0026361000375823467, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=1.0
- fraction_structured=0.5
- lock_S1_series (mean/min/max): 0.9960 / 0.9916 / 0.9987

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
- mass_sim_gev: 0.993578
- Δ_mass_sim vs SM: -19.3524%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6924876100995664, T_ticks=200
- mean_H_lock_norm=0.00867515381022412, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0324 / 0.0002 / 0.2708

### eta_prime_block_0001 (run_id=4)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.946
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.0526315789473684, 2.0]
- F_m (base): 1.053 GeV
- M_eff (base≈F_m): 1.053
- M_corrected (F_m*(1-H_block)): 1.048 (H_block=0.004)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +9.9033%
- mass_sim_gev: 1.13604
- Δ_mass_sim vs SM: +18.6117%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7498699821239433, T_ticks=200
- mean_H_lock_norm=0.0040844136112220125, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0029 / 0.0005 / 0.0260

### eta_prime_block_0002 (run_id=5)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.773
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.2352941176470587, 1.941176470588235, 2.0, 2.0588235294117645]
- F_m (base): 1.235 GeV
- M_eff (base≈F_m): 1.235
- M_corrected (F_m*(1-H_block)): 1.230 (H_block=0.005)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +28.9747%
- mass_sim_gev: 0.97324
- Δ_mass_sim vs SM: +1.6142%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8257164719111137, T_ticks=200
- mean_H_lock_norm=0.004447177737256901, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0104 / 0.0005 / 0.1226

### eta_prime_block_0003 (run_id=0)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.976
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.0555555555555556, 1.9444444444444446, 2.0, 2.055555555555556]
- F_m (base): 1.056 GeV
- M_eff (base≈F_m): 1.056
- M_corrected (F_m*(1-H_block)): 1.052 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +10.2086%
- mass_sim_gev: 0.642678
- Δ_mass_sim vs SM: -32.8992%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.585332879330038, T_ticks=200
- mean_H_lock_norm=0.002860883825820061, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0063 / 0.0005 / 0.0197

- M2 (omega_ref*V_lock*D_stat): 13.9307
- M3 (omega_ref*V_lock*rho_lock): 4.33068
- M2 (omega_ref*V_lock*D_stat): 15.153
- M3 (omega_ref*V_lock*rho_lock): 2.33623
- M2 (omega_ref*V_lock*D_stat): 10.1768
- M3 (omega_ref*V_lock*rho_lock): 3.10234
- M2 (omega_ref*V_lock*D_stat): 23.2621
- M3 (omega_ref*V_lock*rho_lock): 5.79478
- M2 (omega_ref*V_lock*D_stat): 39.8588
- M3 (omega_ref*V_lock*rho_lock): 6.91583
- M2 (omega_ref*V_lock*D_stat): 26.3166
- M3 (omega_ref*V_lock*rho_lock): 10.8814