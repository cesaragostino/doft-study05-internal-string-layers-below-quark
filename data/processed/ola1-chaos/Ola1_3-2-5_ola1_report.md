# Informe Ola1 – Ola1_3-2-5

## Semáforo de salud
- Runs totales: 68
- Runs aceptados: 67 (98.5%)
- Alertas: ninguna

## Entropía / Caos (nuevo)
- Fuente de datos: partial_runs
- Runs con entropy_chaos: 67
- chaos_mode: dynamic=67, ensemble=0
- PE_tick_norm (mean/med/min/max): 0.705 / 0.692 / 0.508 / 0.885
- T_ticks (mean/med/min/max): 200.0 / 200.0 / 200 / 200
- mean_H_lock_norm (mean/med): 0.005 / 0.004
- mixture_entropy_blocks_norm (mean/med): 0.000 / -0.000
- structure_mix_norm (mean/med): 0.044 / 0.000
- fraction_structured (mean/med): 0.035 / 0.000

## Error de masa vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| delta_1232 | +35.8294% | +14.5913% | +62.3377% | 22 |
| deuteron | +1.4954% | -1.8986% | +4.2085% | 17 |
| eta_prime | +23.8518% | +0.2318% | +45.0113% | 15 |
| quark_s_const | -12.1732% | -12.1732% | -12.1732% | 1 |
| quark_ud_const | +0.9227% | -11.3475% | +13.1928% | 2 |
| tau | -0.4790% | -2.4496% | +2.6846% | 10 |

## Inventario (cosecha)
| Partícula | Cantidad | Mejor d_total | Promedio d_total |
|-----------|----------|---------------|------------------|
| delta_1232 | 22 | 2.560 | 5.264 |
| deuteron | 17 | 1.846 | 4.068 |
| eta_prime | 15 | 0.020 | 2.282 |
| quark_s_const | 1 | 0.434 | 0.434 |
| quark_ud_const | 2 | 0.321 | 0.412 |
| tau | 10 | 0.465 | 3.342 |

## Detalle por partícula (d_total y conteos)
| Partícula | Count | d_min | d_med | d_max | Tiers | S2 states |
|-----------|-------|-------|-------|-------|-------|-----------|
| delta_1232 | 22 | 2.560 | 4.562 | 9.399 | level1:21, none:1 | latent:1, none:21 |
| deuteron | 17 | 1.846 | 3.551 | 7.895 | level1:17 | latent:3, none:14 |
| eta_prime | 15 | 0.020 | 2.773 | 4.309 | level1:15 | latent:1, none:14 |
| quark_s_const | 1 | 0.434 | 0.434 | 0.434 | none:1 | none:1 |
| quark_ud_const | 2 | 0.321 | 0.412 | 0.503 | level2:1, none:1 | latent:1, none:1 |
| tau | 10 | 0.465 | 3.854 | 4.776 | level1:10 | none:10 |

## Radar del Zoo (d_total < 5.0) no aceptados
Sin candidatos cercanos fuera de la selección.

## Pareto de rechazos (causas en selección)
| Razón | Cuenta |
|-------|--------|
| missing_match | 1 |
| unknown_particle | 1 |

## Bloques aceptados con métricas de entropía/caos
### delta_1232_block_0001 (run_id=39)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 9.399
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9722222222222223, 2.0]
- F_m (base): 1.972 GeV
- M_eff (base≈F_m): 1.972
- M_corrected (F_m*(1-H_block)): 1.957 (H_block=0.007)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +60.0830%
- H_block (lock_quality): 0.007
- band_power_capture: 0.7998354429775077
- chaos_mode=dynamic, PE_tick_norm=0.6216181123763271, T_ticks=200
- mean_H_lock_norm=0.00744416242587502, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0018 / 0.0002 / 0.0037

### eta_prime_block_0001 (run_id=17)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.497
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.307692307692308, 1.3846153846153848, 2.0]
- F_m (base): 1.308 GeV
- M_eff (base≈F_m): 1.308
- M_corrected (F_m*(1-H_block)): 1.304 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +36.5337%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6325887641852959, T_ticks=200
- mean_H_lock_norm=0.002460257016730191, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0032 / 0.0005 / 0.0078

### eta_prime_block_0002 (run_id=16)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.463
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.3043478260869565, 1.9130434782608698, 2.0, 2.0869565217391304]
- F_m (base): 1.304 GeV
- M_eff (base≈F_m): 1.304
- M_corrected (F_m*(1-H_block)): 1.300 (H_block=0.004)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +36.1845%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.768719465075447, T_ticks=200
- mean_H_lock_norm=0.0036268985838813976, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0123 / 0.0003 / 0.1065

### eta_prime_block_0003 (run_id=37)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.323
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.2903225806451615, 2.0]
- F_m (base): 1.290 GeV
- M_eff (base≈F_m): 1.290
- M_corrected (F_m*(1-H_block)): 1.285 (H_block=0.004)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +34.7201%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7954959693601852, T_ticks=200
- mean_H_lock_norm=0.004133024826849965, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.2823 / 0.0107 / 0.8637

### delta_1232_block_0002 (run_id=52)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.783
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.6363636363636362, 1.9545454545454541, 2.0]
- F_m (base): 1.636 GeV
- M_eff (base≈F_m): 1.636
- M_corrected (F_m*(1-H_block)): 1.617 (H_block=0.012)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +32.8217%
- H_block (lock_quality): 0.012
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5545623928033834, T_ticks=200
- mean_H_lock_norm=0.011316289743334857, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0072 / 0.0012 / 0.0162

### delta_1232_block_0003 (run_id=19)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.188
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.5064935064935066, 1.5324675324675325, 2.0, 2.025974025974026]
- F_m (base): 1.506 GeV
- M_eff (base≈F_m): 1.506
- M_corrected (F_m*(1-H_block)): 1.499 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +22.2803%
- H_block (lock_quality): 0.005
- band_power_capture: 0.8859450227618128
- chaos_mode=dynamic, PE_tick_norm=0.6227894003452125, T_ticks=200
- mean_H_lock_norm=0.004924927102850987, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0044 / 0.0006 / 0.0099

### tau_block_0001 (run_id=13)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 4.347
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.7333333333333334, 1.8666666666666667, 1.9999999999999998, 2.4, 2.5333333333333337, 2.666666666666667]
- F_m (base): 1.733 GeV
- M_eff (base≈F_m): 1.733
- M_corrected (F_m*(1-H_block)): 1.730 (H_block=0.002)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -2.4496%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7672516211937437, T_ticks=200
- mean_H_lock_norm=0.0019857001514867307, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.1620 / 0.0017 / 0.7697

### quark_s_const_block_0001 (run_id=42)
- Partícula: quark_s_const, tier: none, s2_state: none
- match_score.d_total: 0.434
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [0.4479166666666667, 1.9999999999999998]
- F_m (base): 0.448 GeV
- M_eff (base≈F_m): 0.448
- M_corrected (F_m*(1-H_block)): 0.164 (H_block=0.634)
- sm_mass_gev: 0.510
- Δ_mass vs SM: -12.1732%
- H_block (lock_quality): 0.634
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8846785129776761, T_ticks=200
- mean_H_lock_norm=0.008944396229981588, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=1.0
- fraction_structured=0.5
- lock_S1_series (mean/min/max): 0.9576 / 0.8905 / 0.9828

### quark_ud_const_block_0001 (run_id=59)
- Partícula: quark_ud_const, tier: level2, s2_state: latent
- match_score.d_total: 0.503
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [0.380327868852459, 0.38688524590163925, 2.0]
- F_m (base): 0.380 GeV
- M_eff (base≈F_m): 0.380
- M_corrected (F_m*(1-H_block)): 0.157 (H_block=0.587)
- sm_mass_gev: 0.336
- Δ_mass vs SM: +13.1928%
- H_block (lock_quality): 0.587
- band_power_capture: 0.8681883142976692
- chaos_mode=dynamic, PE_tick_norm=0.6315547508381831, T_ticks=200
- mean_H_lock_norm=0.015091840889993232, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.9182958340544894
- fraction_structured=0.3333333333333333
- lock_S1_series (mean/min/max): 0.6167 / 0.3732 / 0.8702

### eta_prime_block_0004 (run_id=51)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 4.287
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.3866666666666667, 2.0]
- F_m (base): 1.387 GeV
- M_eff (base≈F_m): 1.387
- M_corrected (F_m*(1-H_block)): 1.376 (H_block=0.008)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +44.7792%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7815296267458411, T_ticks=200
- mean_H_lock_norm=0.00743372597466373, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0040 / 0.0009 / 0.0110

### deuteron_block_0001 (run_id=64)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 2.375
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.8518518518518519, 1.9629629629629632, 2.0]
- F_m (base): 1.852 GeV
- M_eff (base≈F_m): 1.852
- M_corrected (F_m*(1-H_block)): 1.842 (H_block=0.005)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -1.2667%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5808507875590374, T_ticks=200
- mean_H_lock_norm=0.005131820579248323, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0002 / 0.0017

### deuteron_block_0002 (run_id=6)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.914
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.894736842105263, 1.9999999999999998]
- F_m (base): 1.895 GeV
- M_eff (base≈F_m): 1.895
- M_corrected (F_m*(1-H_block)): 1.892 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.0198%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6250467465883088, T_ticks=200
- mean_H_lock_norm=0.001510667079824818, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0016 / 0.0001 / 0.0035

### delta_1232_block_0004 (run_id=9)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 2.560
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.5, 1.6666666666666667, 2.0, 2.166666666666667, 2.333333333333333]
- F_m (base): 1.500 GeV
- M_eff (base≈F_m): 1.500
- M_corrected (F_m*(1-H_block)): 1.492 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +21.7532%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8644275604905408, T_ticks=200
- mean_H_lock_norm=0.0050727286966164, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.1249 / 0.0006 / 0.8211

### deuteron_block_0003 (run_id=44)
- Partícula: deuteron, tier: level1, s2_state: latent
- match_score.d_total: 2.184
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8974358974358974, 1.9487179487179487, 1.9999999999999998, 2.051282051282051]
- F_m (base): 1.897 GeV
- M_eff (base≈F_m): 1.897
- M_corrected (F_m*(1-H_block)): 1.873 (H_block=0.013)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.1637%
- H_block (lock_quality): 0.013
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8508963709846895, T_ticks=200
- mean_H_lock_norm=0.012814270451701889, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0426 / 0.0003 / 0.4285

### delta_1232_block_0005 (run_id=3)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.680
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [2.0]
- F_m (base): 2.000 GeV
- M_eff (base≈F_m): 2.000
- M_corrected (F_m*(1-H_block)): 1.983 (H_block=0.009)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +62.3377%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6924876100995664, T_ticks=200
- mean_H_lock_norm=0.00867515381022412, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0324 / 0.0002 / 0.2708

### delta_1232_block_0006 (run_id=28)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.106
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.5714285714285716, 1.9285714285714286, 2.0]
- F_m (base): 1.571 GeV
- M_eff (base≈F_m): 1.571
- M_corrected (F_m*(1-H_block)): 1.566 (H_block=0.004)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +27.5510%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6965546508358367, T_ticks=200
- mean_H_lock_norm=0.003568016517387367, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0006 / 0.0000 / 0.0013

### delta_1232_block_0007 (run_id=58)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.926
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.4712643678160922, 1.9770114942528736, 2.0, 2.022988505747126, 2.0459770114942533]
- F_m (base): 1.471 GeV
- M_eff (base≈F_m): 1.471
- M_corrected (F_m*(1-H_block)): 1.461 (H_block=0.007)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +19.4208%
- H_block (lock_quality): 0.007
- band_power_capture: 0.607524220113007
- chaos_mode=dynamic, PE_tick_norm=0.5627146988820596, T_ticks=200
- mean_H_lock_norm=0.006824673962357515, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0039 / 0.0003 / 0.0089

### tau_block_0002 (run_id=48)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 2.070
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.7560975609756095, 1.8048780487804879, 2.0, 2.048780487804878, 2.097560975609756]
- F_m (base): 1.756 GeV
- M_eff (base≈F_m): 1.756
- M_corrected (F_m*(1-H_block)): 1.751 (H_block=0.003)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -1.1685%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7084294111535525, T_ticks=200
- mean_H_lock_norm=0.002806629362472587, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0006 / 0.0001 / 0.0034

### deuteron_block_0004 (run_id=63)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 2.945
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.846153846153846, 1.9230769230769231, 2.0]
- F_m (base): 1.846 GeV
- M_eff (base≈F_m): 1.846
- M_corrected (F_m*(1-H_block)): 1.833 (H_block=0.007)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -1.5705%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6782668332859103, T_ticks=200
- mean_H_lock_norm=0.00734396178405903, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0003 / 0.0014

### tau_block_0003 (run_id=22)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 4.347
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.7333333333333332, 1.9333333333333333, 2.0, 2.0666666666666664, 2.133333333333333]
- F_m (base): 1.733 GeV
- M_eff (base≈F_m): 1.733
- M_corrected (F_m*(1-H_block)): 1.725 (H_block=0.005)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -2.4496%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7818610662760938, T_ticks=200
- mean_H_lock_norm=0.005052063451748727, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.5255 / 0.0913 / 0.9468

### eta_prime_block_0005 (run_id=24)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.420
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [0.9999999999999999, 1.9230769230769231, 1.9999999999999998]
- F_m (base): 1.000 GeV
- M_eff (base≈F_m): 1.000
- M_corrected (F_m*(1-H_block)): 0.996 (H_block=0.004)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +4.4081%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7085083722007445, T_ticks=200
- mean_H_lock_norm=0.0035514502976062554, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0023 / 0.0001 / 0.0094

### deuteron_block_0005 (run_id=34)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.748
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9230769230769231, 2.0]
- F_m (base): 1.923 GeV
- M_eff (base≈F_m): 1.923
- M_corrected (F_m*(1-H_block)): 1.919 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.5307%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8745514582730278, T_ticks=200
- mean_H_lock_norm=0.002198107210859273, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0027 / 0.0003 / 0.0449

### tau_block_0004 (run_id=50)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 0.465
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.7721518987341773, 1.9746835443037976, 2.0, 2.0253164556962027, 2.0506329113924053]
- F_m (base): 1.772 GeV
- M_eff (base≈F_m): 1.772
- M_corrected (F_m*(1-H_block)): 1.768 (H_block=0.002)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -0.2650%
- H_block (lock_quality): 0.002
- band_power_capture: 0.5149214601368484
- chaos_mode=dynamic, PE_tick_norm=0.6468693815270395, T_ticks=200
- mean_H_lock_norm=0.0023665948664235432, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0005 / 0.0001 / 0.0016

### delta_1232_block_0008 (run_id=43)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.449
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.5555555555555558, 2.0]
- F_m (base): 1.556 GeV
- M_eff (base≈F_m): 1.556
- M_corrected (F_m*(1-H_block)): 1.549 (H_block=0.004)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +26.2626%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7925773087896897, T_ticks=200
- mean_H_lock_norm=0.004488004539157504, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0007 / 0.0000 / 0.0021

### delta_1232_block_0009 (run_id=20)
- Partícula: delta_1232, tier: none, s2_state: none
- match_score.d_total: 8.031
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9881305637982198, 1.9940652818991098, 2.0, 2.00593471810089, 2.011869436201781, 2.0178041543026706, 2.0237388724035608]
- F_m (base): 1.988 GeV
- M_eff (base≈F_m): 1.988
- M_corrected (F_m*(1-H_block)): 1.962 (H_block=0.013)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +61.3742%
- H_block (lock_quality): 0.013
- band_power_capture: 0.5172990006844066
- chaos_mode=dynamic, PE_tick_norm=0.6177161184469522, T_ticks=200
- mean_H_lock_norm=0.013071727441424727, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=1.0
- lock_S1_series (mean/min/max): 0.9955 / 0.9874 / 0.9988

### deuteron_block_0006 (run_id=60)
- Partícula: deuteron, tier: level1, s2_state: latent
- match_score.d_total: 3.551
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.9111111111111112, 1.9555555555555557, 2.0, 2.2222222222222223, 2.2666666666666666, 2.3111111111111113]
- F_m (base): 1.911 GeV
- M_eff (base≈F_m): 1.911
- M_corrected (F_m*(1-H_block)): 1.893 (H_block=0.009)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.8928%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6616968215046571, T_ticks=200
- mean_H_lock_norm=0.009277966472673359, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0009 / 0.0001 / 0.0020

### tau_block_0005 (run_id=7)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 4.138
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8181818181818183, 1.9090909090909092, 1.9999999999999998, 2.0909090909090913]
- F_m (base): 1.818 GeV
- M_eff (base≈F_m): 1.818
- M_corrected (F_m*(1-H_block)): 1.816 (H_block=0.001)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +2.3256%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7475149486476064, T_ticks=200
- mean_H_lock_norm=0.0009276421783549375, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.9083 / 0.7233 / 0.9728

### tau_block_0006 (run_id=36)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 4.347
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.7333333333333334, 1.8666666666666667, 2.0]
- F_m (base): 1.733 GeV
- M_eff (base≈F_m): 1.733
- M_corrected (F_m*(1-H_block)): 1.728 (H_block=0.003)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -2.4496%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.66870354509808, T_ticks=200
- mean_H_lock_norm=0.003263274027397132, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0141 / 0.0002 / 0.2597

### eta_prime_block_0006 (run_id=4)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.946
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.0526315789473684, 2.0]
- F_m (base): 1.053 GeV
- M_eff (base≈F_m): 1.053
- M_corrected (F_m*(1-H_block)): 1.048 (H_block=0.004)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +9.9033%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7498699821239433, T_ticks=200
- mean_H_lock_norm=0.0040844136112220125, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0029 / 0.0005 / 0.0260

### eta_prime_block_0007 (run_id=0)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.976
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.0555555555555556, 1.9444444444444446, 2.0, 2.055555555555556]
- F_m (base): 1.056 GeV
- M_eff (base≈F_m): 1.056
- M_corrected (F_m*(1-H_block)): 1.052 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +10.2086%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.585332879330038, T_ticks=200
- mean_H_lock_norm=0.002860883825820061, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0063 / 0.0005 / 0.0197

### delta_1232_block_0010 (run_id=26)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 9.387
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9714285714285715, 2.0]
- F_m (base): 1.971 GeV
- M_eff (base≈F_m): 1.971
- M_corrected (F_m*(1-H_block)): 1.962 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +60.0186%
- H_block (lock_quality): 0.005
- band_power_capture: 0.9242614712072281
- chaos_mode=dynamic, PE_tick_norm=0.5664200863713517, T_ticks=200
- mean_H_lock_norm=0.0047155910783806265, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0003 / 0.0001 / 0.0005

### eta_prime_block_0008 (run_id=66)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.855
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.0434782608695654, 1.9130434782608696, 2.0, 2.086956521739131, 2.173913043478261]
- F_m (base): 1.043 GeV
- M_eff (base≈F_m): 1.043
- M_corrected (F_m*(1-H_block)): 1.040 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +8.9476%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.779770366440351, T_ticks=200
- mean_H_lock_norm=0.0034389289637239704, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.8744 / 0.6166 / 0.9888

### quark_ud_const_block_0002 (run_id=2)
- Partícula: quark_ud_const, tier: none, s2_state: none
- match_score.d_total: 0.321
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [0.29787234042553196, 2.0]
- F_m (base): 0.298 GeV
- M_eff (base≈F_m): 0.298
- M_corrected (F_m*(1-H_block)): 0.110 (H_block=0.632)
- sm_mass_gev: 0.336
- Δ_mass vs SM: -11.3475%
- H_block (lock_quality): 0.632
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.845416153988296, T_ticks=200
- mean_H_lock_norm=0.0026361000375823467, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=1.0
- fraction_structured=0.5
- lock_S1_series (mean/min/max): 0.9960 / 0.9916 / 0.9987

### deuteron_block_0007 (run_id=21)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 2.440
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.9000000000000001, 1.9500000000000002, 2.0]
- F_m (base): 1.900 GeV
- M_eff (base≈F_m): 1.900
- M_corrected (F_m*(1-H_block)): 1.888 (H_block=0.006)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.3004%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5728150117314439, T_ticks=200
- mean_H_lock_norm=0.006281109254726402, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0093 / 0.0006 / 0.0268

### deuteron_block_0008 (run_id=47)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 3.744
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.9130434782608694, 1.9565217391304346, 2.0, 2.1739130434782608, 2.217391304347826]
- F_m (base): 1.913 GeV
- M_eff (base≈F_m): 1.913
- M_corrected (F_m*(1-H_block)): 1.907 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.9958%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8481154905823755, T_ticks=200
- mean_H_lock_norm=0.0030759872313693578, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0674 / 0.0014 / 0.1808

### tau_block_0007 (run_id=25)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 2.680
- Bandas: count=8.0, s2_band_fraction=0.0
- band_energies_gev: [1.75, 1.875, 2.0, 2.125, 3.0000000000000004, 3.125, 3.2500000000000004, 3.375]
- F_m (base): 1.750 GeV
- M_eff (base≈F_m): 1.750
- M_corrected (F_m*(1-H_block)): 1.747 (H_block=0.001)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -1.5117%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7378375111108099, T_ticks=200
- mean_H_lock_norm=0.0014893496558557695, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0011 / 0.0001 / 0.0034

### deuteron_block_0009 (run_id=54)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 5.773
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9333333333333331, 2.0]
- F_m (base): 1.933 GeV
- M_eff (base≈F_m): 1.933
- M_corrected (F_m*(1-H_block)): 1.927 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.0776%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6653153231692026, T_ticks=200
- mean_H_lock_norm=0.003107203848081203, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0020 / 0.0002 / 0.0054

### delta_1232_block_0011 (run_id=57)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 5.573
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.7183098591549295, 1.9718309859154928, 1.9999999999999998, 2.028169014084507, 2.0563380281690136]
- F_m (base): 1.718 GeV
- M_eff (base≈F_m): 1.718
- M_corrected (F_m*(1-H_block)): 1.714 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +39.4732%
- H_block (lock_quality): 0.002
- band_power_capture: 0.6460809459225717
- chaos_mode=dynamic, PE_tick_norm=0.5366887082488279, T_ticks=200
- mean_H_lock_norm=0.002253855009316046, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0026 / 0.0002 / 0.0055

### delta_1232_block_0012 (run_id=27)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.217
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.5714285714285714, 1.7142857142857142, 2.0]
- F_m (base): 1.571 GeV
- M_eff (base≈F_m): 1.571
- M_corrected (F_m*(1-H_block)): 1.567 (H_block=0.003)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +27.5510%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5915168862478265, T_ticks=200
- mean_H_lock_norm=0.002928145384411874, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.4026 / 0.0736 / 0.7760

### eta_prime_block_0009 (run_id=32)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 1.420
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.1, 2.0]
- F_m (base): 1.100 GeV
- M_eff (base≈F_m): 1.100
- M_corrected (F_m*(1-H_block)): 1.098 (H_block=0.002)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +14.8489%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8787999144571319, T_ticks=200
- mean_H_lock_norm=0.00212881453018908, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.1564 / 0.0072 / 0.6405

### deuteron_block_0010 (run_id=41)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 7.895
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9545454545454548, 2.0]
- F_m (base): 1.955 GeV
- M_eff (base≈F_m): 1.955
- M_corrected (F_m*(1-H_block)): 1.948 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +4.2085%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8385151529443591, T_ticks=200
- mean_H_lock_norm=0.0034038794386542027, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.1143 / 0.0006 / 0.6077

### eta_prime_block_0010 (run_id=5)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.773
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.2352941176470587, 1.941176470588235, 2.0, 2.0588235294117645]
- F_m (base): 1.235 GeV
- M_eff (base≈F_m): 1.235
- M_corrected (F_m*(1-H_block)): 1.230 (H_block=0.005)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +28.9747%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8257164719111137, T_ticks=200
- mean_H_lock_norm=0.004447177737256901, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0104 / 0.0005 / 0.1226

### delta_1232_block_0013 (run_id=30)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.356
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.5714285714285714, 2.0]
- F_m (base): 1.571 GeV
- M_eff (base≈F_m): 1.571
- M_corrected (F_m*(1-H_block)): 1.563 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +27.5510%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8087411991787985, T_ticks=200
- mean_H_lock_norm=0.005324565964487472, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0168 / 0.0003 / 0.2601

### tau_block_0008 (run_id=31)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 2.680
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.75, 1.8749999999999998, 2.0, 2.125, 3.5]
- F_m (base): 1.750 GeV
- M_eff (base≈F_m): 1.750
- M_corrected (F_m*(1-H_block)): 1.746 (H_block=0.002)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -1.5117%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8347438302129151, T_ticks=200
- mean_H_lock_norm=0.0020997558474737067, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0363 / 0.0005 / 0.3110

### delta_1232_block_0014 (run_id=12)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.676
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.7234042553191489, 1.74468085106383, 2.0, 2.0212765957446805]
- F_m (base): 1.723 GeV
- M_eff (base≈F_m): 1.723
- M_corrected (F_m*(1-H_block)): 1.712 (H_block=0.007)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +39.8867%
- H_block (lock_quality): 0.007
- band_power_capture: 0.8922299068312326
- chaos_mode=dynamic, PE_tick_norm=0.5075835339297446, T_ticks=200
- mean_H_lock_norm=0.006881691991043257, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0013 / 0.0002 / 0.0027

### deuteron_block_0011 (run_id=23)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 3.560
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.84, 1.9200000000000002, 2.0]
- F_m (base): 1.840 GeV
- M_eff (base≈F_m): 1.840
- M_corrected (F_m*(1-H_block)): 1.831 (H_block=0.005)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -1.8986%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5926452845011627, T_ticks=200
- mean_H_lock_norm=0.005153024026191329, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0027 / 0.0010 / 0.0063

### delta_1232_block_0015 (run_id=56)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 5.062
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.7142857142857144, 1.8571428571428574, 2.0, 2.428571428571429]
- F_m (base): 1.714 GeV
- M_eff (base≈F_m): 1.714
- M_corrected (F_m*(1-H_block)): 1.712 (H_block=0.001)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +39.1466%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5877438629546939, T_ticks=200
- mean_H_lock_norm=0.0012116955407307727, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0024 / 0.0001 / 0.0071

### delta_1232_block_0016 (run_id=29)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.419
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.4146341463414633, 1.4634146341463414, 2.0, 2.048780487804878, 2.0975609756097557]
- F_m (base): 1.415 GeV
- M_eff (base≈F_m): 1.415
- M_corrected (F_m*(1-H_block)): 1.403 (H_block=0.008)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +14.8242%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7365916512815969, T_ticks=200
- mean_H_lock_norm=0.007978127196886078, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0058 / 0.0003 / 0.0171

### deuteron_block_0012 (run_id=18)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 2.440
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.9, 1.9499999999999997, 1.9999999999999998, 2.05, 2.0999999999999996, 2.15]
- F_m (base): 1.900 GeV
- M_eff (base≈F_m): 1.900
- M_corrected (F_m*(1-H_block)): 1.896 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.3004%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.720113335855327, T_ticks=200
- mean_H_lock_norm=0.0020948325203340888, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0002 / 0.0000 / 0.0008

### delta_1232_block_0017 (run_id=46)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.537
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.4545454545454548, 1.5454545454545456, 2.0, 2.090909090909091, 2.181818181818182, 2.272727272727273]
- F_m (base): 1.455 GeV
- M_eff (base≈F_m): 1.455
- M_corrected (F_m*(1-H_block)): 1.451 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +18.0638%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8399905030577153, T_ticks=200
- mean_H_lock_norm=0.0024441836929667174, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0910 / 0.0002 / 0.8203

### eta_prime_block_0011 (run_id=55)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 4.309
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.3888888888888886, 1.9444444444444442, 2.0, 2.0555555555555554, 2.1111111111111107]
- F_m (base): 1.389 GeV
- M_eff (base≈F_m): 1.389
- M_corrected (F_m*(1-H_block)): 1.375 (H_block=0.010)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +45.0113%
- H_block (lock_quality): 0.010
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6518019316085534, T_ticks=200
- mean_H_lock_norm=0.009425543200642036, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0081 / 0.0007 / 0.0511

### deuteron_block_0013 (run_id=11)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 3.349
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.909090909090909, 2.0]
- F_m (base): 1.909 GeV
- M_eff (base≈F_m): 1.909
- M_corrected (F_m*(1-H_block)): 1.907 (H_block=0.001)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.7851%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7049745080656846, T_ticks=200
- mean_H_lock_norm=0.0008915856555246151, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0129 / 0.0002 / 0.1189

### eta_prime_block_0012 (run_id=33)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.814
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.2394366197183098, 2.0]
- F_m (base): 1.239 GeV
- M_eff (base≈F_m): 1.239
- M_corrected (F_m*(1-H_block)): 1.234 (H_block=0.005)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +29.4072%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7671821736844391, T_ticks=200
- mean_H_lock_norm=0.004386890489340845, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0028 / 0.0003 / 0.0077

### eta_prime_block_0013 (run_id=65)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 1.753
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.1333333333333335, 2.0]
- F_m (base): 1.133 GeV
- M_eff (base≈F_m): 1.133
- M_corrected (F_m*(1-H_block)): 1.129 (H_block=0.004)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +18.3292%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6891661266920197, T_ticks=200
- mean_H_lock_norm=0.0038984244465024723, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0030 / 0.0002 / 0.0091

### delta_1232_block_0018 (run_id=62)
- Partícula: delta_1232, tier: level1, s2_state: latent
- match_score.d_total: 7.680
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [2.0]
- F_m (base): 2.000 GeV
- M_eff (base≈F_m): 2.000
- M_corrected (F_m*(1-H_block)): 1.971 (H_block=0.014)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +62.3377%
- H_block (lock_quality): 0.014
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.664189329009661, T_ticks=200
- mean_H_lock_norm=0.01431819120850429, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0007 / 0.0000 / 0.0027

### eta_prime_block_0014 (run_id=10)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.020
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [0.9600000000000001, 1.04, 2.0, 2.08]
- F_m (base): 0.960 GeV
- M_eff (base≈F_m): 0.960
- M_corrected (F_m*(1-H_block)): 0.958 (H_block=0.002)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +0.2318%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6853623294396579, T_ticks=200
- mean_H_lock_norm=0.0019715005256091224, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0042 / 0.0001 / 0.0108

### eta_prime_block_0015 (run_id=14)
- Partícula: eta_prime, tier: level1, s2_state: latent
- match_score.d_total: 3.378
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.2957746478873242, 2.0]
- F_m (base): 1.296 GeV
- M_eff (base≈F_m): 1.296
- M_corrected (F_m*(1-H_block)): 1.276 (H_block=0.015)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +35.2894%
- H_block (lock_quality): 0.015
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7803259662410384, T_ticks=200
- mean_H_lock_norm=0.015209458087242542, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0034 / 0.0001 / 0.0090

### delta_1232_block_0019 (run_id=45)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 2.560
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.5000000000000002, 1.6666666666666667, 2.0]
- F_m (base): 1.500 GeV
- M_eff (base≈F_m): 1.500
- M_corrected (F_m*(1-H_block)): 1.496 (H_block=0.003)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +21.7532%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6881467851277403, T_ticks=200
- mean_H_lock_norm=0.0028755977911295062, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0013 / 0.0001 / 0.0039

### delta_1232_block_0020 (run_id=38)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.141
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.5625, 1.9374999999999998, 2.0, 2.0625, 2.125]
- F_m (base): 1.562 GeV
- M_eff (base≈F_m): 1.562
- M_corrected (F_m*(1-H_block)): 1.551 (H_block=0.007)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +26.8263%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7441981017810467, T_ticks=200
- mean_H_lock_norm=0.007404296537844612, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0051 / 0.0004 / 0.0311

### tau_block_0009 (run_id=15)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 3.570
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8124999999999998, 1.9375000000000002, 2.0, 2.0625]
- F_m (base): 1.812 GeV
- M_eff (base≈F_m): 1.812
- M_corrected (F_m*(1-H_block)): 1.801 (H_block=0.007)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +2.0058%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6881040049861288, T_ticks=200
- mean_H_lock_norm=0.00661465207548643, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0190 / 0.0001 / 0.1486

### deuteron_block_0014 (run_id=53)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.846
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.8571428571428574, 1.9285714285714288, 2.0]
- F_m (base): 1.857 GeV
- M_eff (base≈F_m): 1.857
- M_corrected (F_m*(1-H_block)): 1.845 (H_block=0.007)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.9846%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6707618237340764, T_ticks=200
- mean_H_lock_norm=0.006510974575977641, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0017 / 0.0003 / 0.0035

### deuteron_block_0015 (run_id=8)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 6.884
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9444444444444444, 2.0]
- F_m (base): 1.944 GeV
- M_eff (base≈F_m): 1.944
- M_corrected (F_m*(1-H_block)): 1.942 (H_block=0.001)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.6700%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6915397013314226, T_ticks=200
- mean_H_lock_norm=0.0014268028550437624, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0015 / 0.0001 / 0.0033

### deuteron_block_0016 (run_id=40)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 6.190
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9374999999999998, 1.9999999999999998]
- F_m (base): 1.937 GeV
- M_eff (base≈F_m): 1.937
- M_corrected (F_m*(1-H_block)): 1.934 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.2997%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6726051394857695, T_ticks=200
- mean_H_lock_norm=0.0020457145613201463, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0001 / 0.0018

### tau_block_0010 (run_id=67)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 4.776
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.824561403508772, 1.9649122807017543, 2.0, 2.0350877192982457]
- F_m (base): 1.825 GeV
- M_eff (base≈F_m): 1.825
- M_corrected (F_m*(1-H_block)): 1.818 (H_block=0.003)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +2.6846%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7811610844442312, T_ticks=200
- mean_H_lock_norm=0.003375680340054567, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0001 / 0.0028

### deuteron_block_0017 (run_id=1)
- Partícula: deuteron, tier: level1, s2_state: latent
- match_score.d_total: 7.312
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9487179487179487, 1.9999999999999998]
- F_m (base): 1.949 GeV
- M_eff (base≈F_m): 1.949
- M_corrected (F_m*(1-H_block)): 1.920 (H_block=0.015)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.8978%
- H_block (lock_quality): 0.015
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6845438224083286, T_ticks=200
- mean_H_lock_norm=0.014525308311905797, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0001 / 0.0013

### delta_1232_block_0021 (run_id=35)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.403
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.411764705882353, 1.5294117647058825, 2.0]
- F_m (base): 1.412 GeV
- M_eff (base≈F_m): 1.412
- M_corrected (F_m*(1-H_block)): 1.410 (H_block=0.001)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +14.5913%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5746904996562293, T_ticks=200
- mean_H_lock_norm=0.001424379733579558, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0011 / 0.0001 / 0.0022

### delta_1232_block_0022 (run_id=61)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.680
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [2.0]
- F_m (base): 2.000 GeV
- M_eff (base≈F_m): 2.000
- M_corrected (F_m*(1-H_block)): 1.991 (H_block=0.004)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +62.3377%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6314836496820696, T_ticks=200
- mean_H_lock_norm=0.004308883237324045, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0020 / 0.0007 / 0.0045
