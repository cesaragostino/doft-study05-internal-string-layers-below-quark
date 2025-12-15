# Informe Ola1 – Ola1_3-2-5

## Semáforo de salud
- Runs totales: 256
- Runs aceptados: 253 (98.8%)
- Alertas: ninguna

## Entropía / Caos (nuevo)
- Fuente de datos: partial_runs
- Runs con entropy_chaos: 253
- chaos_mode: dynamic=253, ensemble=0
- PE_tick_norm (mean/med/min/max): 0.701 / 0.697 / 0.301 / 0.914
- T_ticks (mean/med/min/max): 200.0 / 200.0 / 200 / 200
- mean_H_lock_norm (mean/med): 0.005 / 0.005
- mixture_entropy_blocks_norm (mean/med): 0.000 / -0.000
- structure_mix_norm (mean/med): 0.029 / 0.000
- fraction_structured (mean/med): 0.034 / 0.000

## Error de masa vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| delta_1232 | +36.7221% | +8.2251% | +62.3377% | 80 |
| deuteron | +1.1341% | -2.4431% | +4.5412% | 73 |
| eta_prime | +21.7566% | -8.1209% | +47.3997% | 59 |
| quark_s_const | +1.7726% | -12.1732% | +15.7184% | 2 |
| quark_ud_const | -23.2012% | -52.8524% | +13.1928% | 6 |
| tau | +0.0486% | -3.0750% | +2.7704% | 33 |

## Inventario (cosecha)
| Partícula | Cantidad | Mejor d_total | Promedio d_total |
|-----------|----------|---------------|------------------|
| delta_1232 | 80 | 2.560 | 5.337 |
| deuteron | 73 | 0.060 | 3.673 |
| eta_prime | 59 | 0.020 | 2.156 |
| quark_s_const | 2 | 0.434 | 0.593 |
| quark_ud_const | 6 | 0.321 | 1.048 |
| tau | 33 | 0.098 | 2.699 |

## Detalle por partícula (d_total y conteos)
| Partícula | Count | d_min | d_med | d_max | Tiers | S2 states |
|-----------|-------|-------|-------|-------|-------|-----------|
| delta_1232 | 80 | 2.560 | 4.534 | 9.594 | level1:75, none:5 | latent:8, none:69, structural:3 |
| deuteron | 73 | 0.060 | 3.551 | 8.518 | level1:73 | latent:5, none:68 |
| eta_prime | 59 | 0.020 | 2.420 | 4.538 | level1:59 | latent:3, none:56 |
| quark_s_const | 2 | 0.434 | 0.593 | 0.751 | none:2 | none:2 |
| quark_ud_const | 6 | 0.321 | 1.032 | 1.716 | level2:4, none:2 | latent:1, none:5 |
| tau | 33 | 0.098 | 2.680 | 5.458 | level1:33 | latent:4, none:29 |

## Radar del Zoo (d_total < 5.0) no aceptados
Sin candidatos cercanos fuera de la selección.

## Pareto de rechazos (causas en selección)
| Razón | Cuenta |
|-------|--------|
| missing_match | 3 |
| unknown_particle | 3 |

## Bloques aceptados con métricas de entropía/caos
### tau_block_0001 (run_id=102)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 5.458
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.7222222222222225, 1.9444444444444449, 2.0]
- F_m (base): 1.722 GeV
- M_eff (base≈F_m): 1.722
- M_corrected (F_m*(1-H_block)): 1.719 (H_block=0.002)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -3.0750%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8523909245089007, T_ticks=200
- mean_H_lock_norm=0.001703190121374095, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0605 / 0.0008 / 0.3195

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
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.585332879330038, T_ticks=200
- mean_H_lock_norm=0.002860883825820061, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0063 / 0.0005 / 0.0197

### deuteron_block_0001 (run_id=157)
- Partícula: deuteron, tier: level1, s2_state: latent
- match_score.d_total: 1.846
- Bandas: count=7.0, s2_band_fraction=0.0
- band_energies_gev: [1.8571428571428568, 1.9285714285714282, 2.0, 2.071428571428571, 2.2857142857142856, 2.3571428571428568, 2.4285714285714284]
- F_m (base): 1.857 GeV
- M_eff (base≈F_m): 1.857
- M_corrected (F_m*(1-H_block)): 1.830 (H_block=0.015)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.9846%
- H_block (lock_quality): 0.015
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8311144125762118, T_ticks=200
- mean_H_lock_norm=0.014603256723402435, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0011 / 0.0000 / 0.0027

### delta_1232_block_0001 (run_id=28)
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

### tau_block_0002 (run_id=25)
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

### deuteron_block_0002 (run_id=201)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 5.167
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.9272727272727272, 1.9636363636363634, 2.0, 2.036363636363636]
- F_m (base): 1.927 GeV
- M_eff (base≈F_m): 1.927
- M_corrected (F_m*(1-H_block)): 1.908 (H_block=0.010)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.7544%
- H_block (lock_quality): 0.010
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6050497378843505, T_ticks=200
- mean_H_lock_norm=0.010188846790603178, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0188 / 0.0024 / 0.0592

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

### delta_1232_block_0002 (run_id=214)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.850
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9714285714285715, 1.9857142857142858, 2.0]
- F_m (base): 1.971 GeV
- M_eff (base≈F_m): 1.971
- M_corrected (F_m*(1-H_block)): 1.944 (H_block=0.014)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +60.0186%
- H_block (lock_quality): 0.014
- band_power_capture: 0.6540188282539666
- chaos_mode=dynamic, PE_tick_norm=0.5428674769060005, T_ticks=200
- mean_H_lock_norm=0.014164828926637908, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0044 / 0.0017 / 0.0073

### delta_1232_block_0003 (run_id=200)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 5.513
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.710526315789474, 1.9736842105263162, 2.0, 2.0263157894736845]
- F_m (base): 1.711 GeV
- M_eff (base≈F_m): 1.711
- M_corrected (F_m*(1-H_block)): 1.698 (H_block=0.007)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +38.8414%
- H_block (lock_quality): 0.007
- band_power_capture: 0.835409153272543
- chaos_mode=dynamic, PE_tick_norm=0.8525744775239495, T_ticks=200
- mean_H_lock_norm=0.007064431828812949, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0156 / 0.0008 / 0.0878

### deuteron_block_0003 (run_id=250)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 7.996
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9555555555555555, 2.0]
- F_m (base): 1.956 GeV
- M_eff (base≈F_m): 1.956
- M_corrected (F_m*(1-H_block)): 1.952 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +4.2624%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6711899424574348, T_ticks=200
- mean_H_lock_norm=0.001755946198167014, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0004 / 0.0000 / 0.0012

### tau_block_0003 (run_id=183)
- Partícula: tau, tier: level1, s2_state: latent
- match_score.d_total: 4.138
- Bandas: count=7.0, s2_band_fraction=0.0
- band_energies_gev: [1.8181818181818181, 1.9545454545454546, 2.0, 2.0454545454545454, 2.090909090909091, 2.1363636363636362, 2.1818181818181817]
- F_m (base): 1.818 GeV
- M_eff (base≈F_m): 1.818
- M_corrected (F_m*(1-H_block)): 1.784 (H_block=0.019)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +2.3256%
- H_block (lock_quality): 0.019
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5953630326855349, T_ticks=200
- mean_H_lock_norm=0.01877051446130942, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0011 / 0.0004 / 0.0024

### delta_1232_block_0004 (run_id=45)
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

### eta_prime_block_0002 (run_id=217)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.420
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.2, 1.96, 2.0, 2.04]
- F_m (base): 1.200 GeV
- M_eff (base≈F_m): 1.200
- M_corrected (F_m*(1-H_block)): 1.189 (H_block=0.009)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +25.2897%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6413554678099567, T_ticks=200
- mean_H_lock_norm=0.008939238661386757, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0132 / 0.0068 / 0.0213

### quark_ud_const_block_0001 (run_id=98)
- Partícula: quark_ud_const, tier: level2, s2_state: none
- match_score.d_total: 1.561
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [0.17391304347826086, 0.1847826086956522, 2.0]
- F_m (base): 0.174 GeV
- M_eff (base≈F_m): 0.174
- M_corrected (F_m*(1-H_block)): 0.072 (H_block=0.585)
- sm_mass_gev: 0.336
- Δ_mass vs SM: -48.2402%
- H_block (lock_quality): 0.585
- band_power_capture: 0.9335153823162091
- chaos_mode=dynamic, PE_tick_norm=0.6422757075453418, T_ticks=200
- mean_H_lock_norm=0.007216635569713549, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.9182958340544894
- fraction_structured=0.3333333333333333
- lock_S1_series (mean/min/max): 0.9071 / 0.6196 / 0.9938

### deuteron_block_0004 (run_id=224)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 6.558
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9411764705882353, 1.9705882352941178, 2.0, 2.323529411764706, 2.3529411764705883]
- F_m (base): 1.941 GeV
- M_eff (base≈F_m): 1.941
- M_corrected (F_m*(1-H_block)): 1.927 (H_block=0.007)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.4957%
- H_block (lock_quality): 0.007
- band_power_capture: 0.7609871342119986
- chaos_mode=dynamic, PE_tick_norm=0.7524776402411635, T_ticks=200
- mean_H_lock_norm=0.007195704143445713, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0011 / 0.0002 / 0.0031

### tau_block_0004 (run_id=122)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 1.267
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.7894736842105263, 1.894736842105263, 1.9999999999999998, 2.1052631578947367]
- F_m (base): 1.789 GeV
- M_eff (base≈F_m): 1.789
- M_corrected (F_m*(1-H_block)): 1.780 (H_block=0.006)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +0.7099%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6105990856340408, T_ticks=200
- mean_H_lock_norm=0.0055659666622025344, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0017 / 0.0005 / 0.0051

### deuteron_block_0005 (run_id=141)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 6.190
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.9375, 1.9687499999999996, 2.0]
- F_m (base): 1.938 GeV
- M_eff (base≈F_m): 1.938
- M_corrected (F_m*(1-H_block)): 1.924 (H_block=0.007)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.2997%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5795120275039612, T_ticks=200
- mean_H_lock_norm=0.007139980191297956, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0084 / 0.0006 / 0.0247

### tau_block_0005 (run_id=124)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 0.407
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.7727272727272723, 1.9848484848484849, 2.0, 2.0151515151515147]
- F_m (base): 1.773 GeV
- M_eff (base≈F_m): 1.773
- M_corrected (F_m*(1-H_block)): 1.758 (H_block=0.009)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -0.2326%
- H_block (lock_quality): 0.009
- band_power_capture: 0.8897566386906878
- chaos_mode=dynamic, PE_tick_norm=0.6956791564037146, T_ticks=200
- mean_H_lock_norm=0.008323124526812133, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0015 / 0.0000 / 0.0033

### deuteron_block_0006 (run_id=70)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 2.375
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.8518518518518519, 1.925925925925926, 2.0, 2.5185185185185186, 2.592592592592593]
- F_m (base): 1.852 GeV
- M_eff (base≈F_m): 1.852
- M_corrected (F_m*(1-H_block)): 1.844 (H_block=0.004)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -1.2667%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7899914020788679, T_ticks=200
- mean_H_lock_norm=0.00444552152724287, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0022 / 0.0000 / 0.0057

### delta_1232_block_0005 (run_id=12)
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

### eta_prime_block_0003 (run_id=100)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.790
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.037037037037037, 1.9999999999999998]
- F_m (base): 1.037 GeV
- M_eff (base≈F_m): 1.037
- M_corrected (F_m*(1-H_block)): 1.027 (H_block=0.009)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +8.2751%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8170648892619126, T_ticks=200
- mean_H_lock_norm=0.009350044770921469, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0032 / 0.0002 / 0.0149

### eta_prime_block_0004 (run_id=37)
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

### delta_1232_block_0006 (run_id=52)
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

### eta_prime_block_0005 (run_id=94)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.976
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.0555555555555556, 2.0]
- F_m (base): 1.056 GeV
- M_eff (base≈F_m): 1.056
- M_corrected (F_m*(1-H_block)): 1.046 (H_block=0.009)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +10.2086%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.582925622808882, T_ticks=200
- mean_H_lock_norm=0.008300258215854202, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0158 / 0.0014 / 0.0553

### delta_1232_block_0007 (run_id=69)
- Partícula: delta_1232, tier: level1, s2_state: latent
- match_score.d_total: 3.448
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.4782608695652175, 1.565217391304348, 2.0, 2.0869565217391304, 2.1739130434782608, 2.2608695652173916]
- F_m (base): 1.478 GeV
- M_eff (base≈F_m): 1.478
- M_corrected (F_m*(1-H_block)): 1.462 (H_block=0.011)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +19.9887%
- H_block (lock_quality): 0.011
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7237731336951472, T_ticks=200
- mean_H_lock_norm=0.011151532697395217, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0015 / 0.0001 / 0.0057

### tau_block_0006 (run_id=207)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 2.680
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.7499999999999996, 1.8749999999999996, 1.9999999999999998, 2.1249999999999996]
- F_m (base): 1.750 GeV
- M_eff (base≈F_m): 1.750
- M_corrected (F_m*(1-H_block)): 1.748 (H_block=0.001)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -1.5117%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6022992571824116, T_ticks=200
- mean_H_lock_norm=0.0013675165661561073, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0006 / 0.0001 / 0.0016

### deuteron_block_0007 (run_id=211)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.846
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.8571428571428577, 1.9285714285714286, 2.0]
- F_m (base): 1.857 GeV
- M_eff (base≈F_m): 1.857
- M_corrected (F_m*(1-H_block)): 1.846 (H_block=0.006)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.9846%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5913382350489411, T_ticks=200
- mean_H_lock_norm=0.005620639164945856, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0026 / 0.0002 / 0.0086

### eta_prime_block_0006 (run_id=173)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.532
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.0112359550561796, 1.0337078651685394, 2.0, 2.022471910112359]
- F_m (base): 1.011 GeV
- M_eff (base≈F_m): 1.011
- M_corrected (F_m*(1-H_block)): 1.004 (H_block=0.008)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +5.5812%
- H_block (lock_quality): 0.008
- band_power_capture: 0.7053890381187
- chaos_mode=dynamic, PE_tick_norm=0.5138086847623119, T_ticks=200
- mean_H_lock_norm=0.007122818442077628, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0229 / 0.0014 / 0.0789

### tau_block_0007 (run_id=208)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 0.961
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.7864077669902911, 1.9029126213592233, 1.9999999999999998]
- F_m (base): 1.786 GeV
- M_eff (base≈F_m): 1.786
- M_corrected (F_m*(1-H_block)): 1.772 (H_block=0.008)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +0.5373%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.30112570389237225, T_ticks=200
- mean_H_lock_norm=0.007789137822503744, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0011 / 0.0004 / 0.0021

### deuteron_block_0008 (run_id=246)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 5.660
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.9322033898305089, 1.9661016949152545, 2.0, 2.033898305084746]
- F_m (base): 1.932 GeV
- M_eff (base≈F_m): 1.932
- M_corrected (F_m*(1-H_block)): 1.922 (H_block=0.005)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.0173%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.59879519311302, T_ticks=200
- mean_H_lock_norm=0.005379812428175217, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0013 / 0.0004 / 0.0028

### delta_1232_block_0008 (run_id=72)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.385
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.5714285714285714, 1.6428571428571426, 1.9999999999999998, 2.071428571428571]
- F_m (base): 1.571 GeV
- M_eff (base≈F_m): 1.571
- M_corrected (F_m*(1-H_block)): 1.569 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +27.5510%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7479598854451925, T_ticks=200
- mean_H_lock_norm=0.0017042213411272529, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0004 / 0.0000 / 0.0012

### tau_block_0008 (run_id=140)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 2.680
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.7499999999999998, 1.875, 2.0, 2.125, 3.75, 3.874999999999999]
- F_m (base): 1.750 GeV
- M_eff (base≈F_m): 1.750
- M_corrected (F_m*(1-H_block)): 1.747 (H_block=0.002)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -1.5117%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.817165879581347, T_ticks=200
- mean_H_lock_norm=0.001709937323622291, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.3867 / 0.0685 / 0.8117

### delta_1232_block_0009 (run_id=191)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.678
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9555555555555555, 1.9777777777777776, 2.0]
- F_m (base): 1.956 GeV
- M_eff (base≈F_m): 1.956
- M_corrected (F_m*(1-H_block)): 1.937 (H_block=0.010)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +58.7302%
- H_block (lock_quality): 0.010
- band_power_capture: 0.8244843328808255
- chaos_mode=dynamic, PE_tick_norm=0.5204689149431988, T_ticks=200
- mean_H_lock_norm=0.009567403857415668, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0127 / 0.0014 / 0.0309

### deuteron_block_0009 (run_id=178)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.227
- Bandas: count=7.0, s2_band_fraction=0.0
- band_energies_gev: [1.8333333333333335, 1.916666666666667, 2.0, 2.0833333333333335, 3.2500000000000004, 3.333333333333334, 3.416666666666667]
- F_m (base): 1.833 GeV
- M_eff (base≈F_m): 1.833
- M_corrected (F_m*(1-H_block)): 1.828 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -2.2540%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7365953401066109, T_ticks=200
- mean_H_lock_norm=0.002944322062174106, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0043 / 0.0002 / 0.0119

### eta_prime_block_0007 (run_id=195)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.753
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.3333333333333333, 1.9259259259259258, 1.9999999999999998]
- F_m (base): 1.333 GeV
- M_eff (base≈F_m): 1.333
- M_corrected (F_m*(1-H_block)): 1.327 (H_block=0.005)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +39.2108%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8078683517014328, T_ticks=200
- mean_H_lock_norm=0.0050338967256154275, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0192 / 0.0002 / 0.2072

### eta_prime_block_0008 (run_id=65)
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

### deuteron_block_0010 (run_id=216)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.629
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.891891891891892, 1.945945945945946, 2.0, 2.0540540540540544]
- F_m (base): 1.892 GeV
- M_eff (base≈F_m): 1.892
- M_corrected (F_m*(1-H_block)): 1.887 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +0.8681%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.595684539892349, T_ticks=200
- mean_H_lock_norm=0.002714462643224491, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0050 / 0.0003 / 0.0169

### eta_prime_block_0009 (run_id=87)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.420
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.0, 1.1, 2.0, 2.1, 2.2]
- F_m (base): 1.000 GeV
- M_eff (base≈F_m): 1.000
- M_corrected (F_m*(1-H_block)): 0.999 (H_block=0.001)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +4.4081%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8247349022628839, T_ticks=200
- mean_H_lock_norm=0.0011062485007517532, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.5408 / 0.1258 / 0.8779

### deuteron_block_0011 (run_id=119)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 8.092
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9565217391304348, 2.0]
- F_m (base): 1.957 GeV
- M_eff (base≈F_m): 1.957
- M_corrected (F_m*(1-H_block)): 1.942 (H_block=0.007)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +4.3139%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5555947838224686, T_ticks=200
- mean_H_lock_norm=0.007306554927265979, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0110 / 0.0006 / 0.0345

### tau_block_0009 (run_id=172)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 0.537
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.7714285714285716, 1.885714285714286, 2.0]
- F_m (base): 1.771 GeV
- M_eff (base≈F_m): 1.771
- M_corrected (F_m*(1-H_block)): 1.761 (H_block=0.006)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -0.3057%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8153630043825292, T_ticks=200
- mean_H_lock_norm=0.006160106885006532, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.8915 / 0.7776 / 0.9447

### deuteron_block_0012 (run_id=54)
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

### delta_1232_block_0010 (run_id=154)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.559
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.3333333333333333, 1.8666666666666665, 2.0, 2.1333333333333333]
- F_m (base): 1.333 GeV
- M_eff (base≈F_m): 1.333
- M_corrected (F_m*(1-H_block)): 1.323 (H_block=0.008)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +8.2251%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6477478998448183, T_ticks=200
- mean_H_lock_norm=0.007565171255107021, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0014 / 0.0001 / 0.0030

### tau_block_0010 (run_id=221)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 4.138
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8181818181818183, 1.9090909090909092, 2.0, 2.1818181818181817]
- F_m (base): 1.818 GeV
- M_eff (base≈F_m): 1.818
- M_corrected (F_m*(1-H_block)): 1.816 (H_block=0.001)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +2.3256%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6143919094898719, T_ticks=200
- mean_H_lock_norm=0.0012215910026867182, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0009 / 0.0000 / 0.0023

### eta_prime_block_0010 (run_id=10)
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

### deuteron_block_0013 (run_id=147)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 6.091
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.9365079365079363, 1.9682539682539681, 2.0]
- F_m (base): 1.937 GeV
- M_eff (base≈F_m): 1.937
- M_corrected (F_m*(1-H_block)): 1.925 (H_block=0.006)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.2468%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.562291844839627, T_ticks=200
- mean_H_lock_norm=0.005964863476389967, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0137 / 0.0015 / 0.0349

### delta_1232_block_0011 (run_id=156)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.403
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.411764705882353, 1.5294117647058825, 2.0, 2.1176470588235294, 2.235294117647059, 2.3529411764705883]
- F_m (base): 1.412 GeV
- M_eff (base≈F_m): 1.412
- M_corrected (F_m*(1-H_block)): 1.404 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +14.5913%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8262102523762401, T_ticks=200
- mean_H_lock_norm=0.005227187581417021, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0990 / 0.0004 / 0.7874

### eta_prime_block_0011 (run_id=228)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 1.753
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.1333333333333333, 1.966666666666667, 2.0]
- F_m (base): 1.133 GeV
- M_eff (base≈F_m): 1.133
- M_corrected (F_m*(1-H_block)): 1.123 (H_block=0.009)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +18.3292%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7277726931258552, T_ticks=200
- mean_H_lock_norm=0.008714916554844548, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0158 / 0.0007 / 0.1120

### deuteron_block_0014 (run_id=93)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 3.349
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.842105263157895, 1.9736842105263157, 2.0, 2.026315789473684, 2.052631578947368]
- F_m (base): 1.842 GeV
- M_eff (base≈F_m): 1.842
- M_corrected (F_m*(1-H_block)): 1.840 (H_block=0.001)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -1.7863%
- H_block (lock_quality): 0.001
- band_power_capture: 0.6330256067824623
- chaos_mode=dynamic, PE_tick_norm=0.6839907615254615, T_ticks=200
- mean_H_lock_norm=0.001261656581728264, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0002 / 0.0000 / 0.0004

### eta_prime_block_0012 (run_id=66)
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

### eta_prime_block_0013 (run_id=97)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.106
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [0.9473684210526314, 1.9473684210526312, 2.0]
- F_m (base): 0.947 GeV
- M_eff (base≈F_m): 0.947
- M_corrected (F_m*(1-H_block)): 0.939 (H_block=0.009)
- sm_mass_gev: 0.958
- Δ_mass vs SM: -1.0871%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8845449510991722, T_ticks=200
- mean_H_lock_norm=0.008508706458419925, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.2070 / 0.0175 / 0.5617

### eta_prime_block_0014 (run_id=194)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.420
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.0, 1.1250000000000002, 2.0, 2.1250000000000004]
- F_m (base): 1.000 GeV
- M_eff (base≈F_m): 1.000
- M_corrected (F_m*(1-H_block)): 0.994 (H_block=0.006)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +4.4081%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7010959181523012, T_ticks=200
- mean_H_lock_norm=0.005599433533853299, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0050 / 0.0000 / 0.1289

### delta_1232_block_0012 (run_id=174)
- Partícula: delta_1232, tier: level1, s2_state: latent
- match_score.d_total: 9.399
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9722222222222219, 1.9999999999999998]
- F_m (base): 1.972 GeV
- M_eff (base≈F_m): 1.972
- M_corrected (F_m*(1-H_block)): 1.939 (H_block=0.017)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +60.0830%
- H_block (lock_quality): 0.017
- band_power_capture: 0.9219335713934098
- chaos_mode=dynamic, PE_tick_norm=0.5786842857100528, T_ticks=200
- mean_H_lock_norm=0.017007412376150034, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0052 / 0.0007 / 0.0117

### eta_prime_block_0015 (run_id=5)
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

### deuteron_block_0015 (run_id=86)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 0.893
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.866666666666667, 1.9333333333333336, 2.0, 2.066666666666667, 2.8666666666666667, 2.9333333333333336]
- F_m (base): 1.867 GeV
- M_eff (base≈F_m): 1.867
- M_corrected (F_m*(1-H_block)): 1.855 (H_block=0.006)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.4768%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.816548095402663, T_ticks=200
- mean_H_lock_norm=0.00605706977168518, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0019 / 0.0001 / 0.0078

### deuteron_block_0016 (run_id=130)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.846
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8571428571428574, 1.9285714285714286, 2.0, 2.0714285714285716]
- F_m (base): 1.857 GeV
- M_eff (base≈F_m): 1.857
- M_corrected (F_m*(1-H_block)): 1.842 (H_block=0.008)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.9846%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6814520432304244, T_ticks=200
- mean_H_lock_norm=0.008235077604161303, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0023 / 0.0010 / 0.0045

### eta_prime_block_0016 (run_id=110)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.801
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.2380952380952381, 1.9523809523809523, 2.0]
- F_m (base): 1.238 GeV
- M_eff (base≈F_m): 1.238
- M_corrected (F_m*(1-H_block)): 1.229 (H_block=0.007)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +29.2672%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8828962567586313, T_ticks=200
- mean_H_lock_norm=0.0069140409892957085, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0021 / 0.0002 / 0.0082

### delta_1232_block_0013 (run_id=179)
- Partícula: delta_1232, tier: none, s2_state: structural
- match_score.d_total: 8.107
- Bandas: count=1.0, s2_band_fraction=1.0
- band_energies_gev: [1.995115995115995, 1.9975579975579973, 1.9999999999999998, 2.0024420024420024, 2.004884004884005, 2.0073260073260073, 2.0097680097680097]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.995 (H_block=0.000)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +61.9412%
- H_block (lock_quality): 0.000
- band_power_capture: 0.4513394455880564
- chaos_mode=dynamic, PE_tick_norm=0.8787504527852505, T_ticks=200
- mean_H_lock_norm=1.4171741844121111e-05, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=1.0
- lock_S1_series (mean/min/max): 0.0003 / 0.0000 / 0.0036

### deuteron_block_0017 (run_id=203)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 0.060
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.8750000000000002, 2.0]
- F_m (base): 1.875 GeV
- M_eff (base≈F_m): 1.875
- M_corrected (F_m*(1-H_block)): 1.871 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.0325%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7320348899239801, T_ticks=200
- mean_H_lock_norm=0.002011550229625689, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0004 / 0.0002 / 0.0006

### deuteron_block_0018 (run_id=233)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 0.893
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.866666666666667, 1.9111111111111114, 2.0, 2.0444444444444447, 2.0888888888888895]
- F_m (base): 1.867 GeV
- M_eff (base≈F_m): 1.867
- M_corrected (F_m*(1-H_block)): 1.861 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.4768%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7079852197367523, T_ticks=200
- mean_H_lock_norm=0.003007447187837771, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0001 / 0.0043

### delta_1232_block_0014 (run_id=26)
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

### deuteron_block_0019 (run_id=18)
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

### eta_prime_block_0017 (run_id=16)
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

### eta_prime_block_0018 (run_id=188)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.780
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [0.88, 0.9599999999999999, 1.9999999999999998]
- F_m (base): 0.880 GeV
- M_eff (base≈F_m): 0.880
- M_corrected (F_m*(1-H_block)): 0.879 (H_block=0.002)
- sm_mass_gev: 0.958
- Δ_mass vs SM: -8.1209%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7420861407948647, T_ticks=200
- mean_H_lock_norm=0.001527810977823901, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.2513 / 0.0006 / 0.9215

### deuteron_block_0020 (run_id=212)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.597
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.9215686274509804, 1.96078431372549, 2.0, 2.0392156862745097]
- F_m (base): 1.922 GeV
- M_eff (base≈F_m): 1.922
- M_corrected (F_m*(1-H_block)): 1.896 (H_block=0.013)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.4503%
- H_block (lock_quality): 0.013
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.4981761332977848, T_ticks=200
- mean_H_lock_norm=0.01327429271969649, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0319 / 0.0021 / 0.0859

### deuteron_block_0021 (run_id=242)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.107
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.9166666666666665, 1.9583333333333333, 1.9999999999999998, 2.4999999999999996, 2.5416666666666665]
- F_m (base): 1.917 GeV
- M_eff (base≈F_m): 1.917
- M_corrected (F_m*(1-H_block)): 1.912 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.1890%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8926730160840392, T_ticks=200
- mean_H_lock_norm=0.0024939589838978574, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0007 / 0.0001 / 0.0059

### deuteron_block_0022 (run_id=47)
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

### delta_1232_block_0015 (run_id=143)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.466
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.5849056603773586, 1.9622641509433962, 2.0, 2.037735849056604, 2.0754716981132075]
- F_m (base): 1.585 GeV
- M_eff (base≈F_m): 1.585
- M_corrected (F_m*(1-H_block)): 1.577 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +28.6449%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.561220178087164, T_ticks=200
- mean_H_lock_norm=0.004771270340796138, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0029 / 0.0002 / 0.0078

### eta_prime_block_0019 (run_id=223)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 1.189
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.076923076923077, 1.9230769230769231, 2.0]
- F_m (base): 1.077 GeV
- M_eff (base≈F_m): 1.077
- M_corrected (F_m*(1-H_block)): 1.075 (H_block=0.002)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +12.4395%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7799241397760552, T_ticks=200
- mean_H_lock_norm=0.0020051121876810464, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0018 / 0.0004 / 0.0056

### delta_1232_block_0016 (run_id=204)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.368
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.6551724137931034, 2.0]
- F_m (base): 1.655 GeV
- M_eff (base≈F_m): 1.655
- M_corrected (F_m*(1-H_block)): 1.653 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +34.3484%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8458402188442041, T_ticks=200
- mean_H_lock_norm=0.0015944382280754913, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.4296 / 0.0948 / 0.8145

### delta_1232_block_0017 (run_id=177)
- Partícula: delta_1232, tier: level1, s2_state: latent
- match_score.d_total: 4.161
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.5833333333333335, 1.916666666666667, 1.9999999999999998, 2.0833333333333335]
- F_m (base): 1.583 GeV
- M_eff (base≈F_m): 1.583
- M_corrected (F_m*(1-H_block)): 1.568 (H_block=0.010)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +28.5173%
- H_block (lock_quality): 0.010
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7344726692355712, T_ticks=200
- mean_H_lock_norm=0.009659289814770565, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0011 / 0.0001 / 0.0023

### deuteron_block_0023 (run_id=6)
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

### eta_prime_block_0020 (run_id=51)
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

### eta_prime_block_0021 (run_id=104)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 4.010
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.358974358974359, 1.9743589743589745, 2.0]
- F_m (base): 1.359 GeV
- M_eff (base≈F_m): 1.359
- M_corrected (F_m*(1-H_block)): 1.349 (H_block=0.007)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +41.8879%
- H_block (lock_quality): 0.007
- band_power_capture: 0.848520765948718
- chaos_mode=dynamic, PE_tick_norm=0.6723235114695489, T_ticks=200
- mean_H_lock_norm=0.007099160896660667, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0071 / 0.0008 / 0.0164

### eta_prime_block_0022 (run_id=123)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 4.538
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.4117647058823528, 2.0]
- F_m (base): 1.412 GeV
- M_eff (base≈F_m): 1.412
- M_corrected (F_m*(1-H_block)): 1.406 (H_block=0.004)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +47.3997%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6952291478307732, T_ticks=200
- mean_H_lock_norm=0.004425350689800987, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.3515 / 0.0249 / 0.9004

### eta_prime_block_0023 (run_id=251)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.420
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.0, 1.962962962962963, 2.0]
- F_m (base): 1.000 GeV
- M_eff (base≈F_m): 1.000
- M_corrected (F_m*(1-H_block)): 0.994 (H_block=0.006)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +4.4081%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6177027402532282, T_ticks=200
- mean_H_lock_norm=0.00566632532882647, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0113 / 0.0007 / 0.0359

### tau_block_0011 (run_id=133)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 4.929
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.8260869565217388, 1.9130434782608696, 2.0]
- F_m (base): 1.826 GeV
- M_eff (base≈F_m): 1.826
- M_corrected (F_m*(1-H_block)): 1.811 (H_block=0.008)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +2.7704%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6379188785649585, T_ticks=200
- mean_H_lock_norm=0.008438773836554109, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0036 / 0.0006 / 0.0149

### deuteron_block_0024 (run_id=186)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.277
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.9183673469387754, 1.959183673469388, 2.0, 2.4489795918367347, 2.489795918367347]
- F_m (base): 1.918 GeV
- M_eff (base≈F_m): 1.918
- M_corrected (F_m*(1-H_block)): 1.915 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.2797%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7879261491140716, T_ticks=200
- mean_H_lock_norm=0.0017031147969575051, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0007 / 0.0001 / 0.0016

### delta_1232_block_0018 (run_id=219)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.797
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.5454545454545456, 1.909090909090909, 2.0, 2.0909090909090913, 2.181818181818182]
- F_m (base): 1.545 GeV
- M_eff (base≈F_m): 1.545
- M_corrected (F_m*(1-H_block)): 1.540 (H_block=0.004)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +25.4427%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7297562270191545, T_ticks=200
- mean_H_lock_norm=0.0035463402456161245, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0019 / 0.0002 / 0.0090

### tau_block_0012 (run_id=73)
- Partícula: tau, tier: level1, s2_state: latent
- match_score.d_total: 4.138
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.8181818181818183, 1.9090909090909094, 2.0, 2.090909090909091, 4.454545454545455]
- F_m (base): 1.818 GeV
- M_eff (base≈F_m): 1.818
- M_corrected (F_m*(1-H_block)): 1.799 (H_block=0.010)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +2.3256%
- H_block (lock_quality): 0.010
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8326674640915952, T_ticks=200
- mean_H_lock_norm=0.010043187750596873, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.7887 / 0.4386 / 0.9413

### eta_prime_block_0024 (run_id=181)
- Partícula: eta_prime, tier: level1, s2_state: latent
- match_score.d_total: 0.896
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.0476190476190477, 1.142857142857143, 2.0]
- F_m (base): 1.048 GeV
- M_eff (base≈F_m): 1.048
- M_corrected (F_m*(1-H_block)): 1.038 (H_block=0.010)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +9.3799%
- H_block (lock_quality): 0.010
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7054836519736484, T_ticks=200
- mean_H_lock_norm=0.009495402729296406, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0020 / 0.0002 / 0.0080

### eta_prime_block_0025 (run_id=4)
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

### delta_1232_block_0019 (run_id=193)
- Partícula: delta_1232, tier: none, s2_state: structural
- match_score.d_total: 8.107
- Bandas: count=1.0, s2_band_fraction=1.0
- band_energies_gev: [1.995145631067961, 1.9975728155339803, 2.0, 2.0024271844660193]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.991 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +61.9436%
- H_block (lock_quality): 0.002
- band_power_capture: 0.689656141400889
- chaos_mode=dynamic, PE_tick_norm=0.7167909837117966, T_ticks=200
- mean_H_lock_norm=0.0021537124341970025, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=1.0
- lock_S1_series (mean/min/max): 0.0002 / 0.0000 / 0.0003

### tau_block_0013 (run_id=50)
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

### deuteron_block_0025 (run_id=23)
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

### delta_1232_block_0020 (run_id=62)
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

### delta_1232_block_0021 (run_id=19)
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

### delta_1232_block_0022 (run_id=243)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.667
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9545454545454544, 1.9772727272727273, 2.0, 2.4318181818181817, 2.454545454545454, 2.477272727272727, 2.5, 2.522727272727273]
- F_m (base): 1.955 GeV
- M_eff (base≈F_m): 1.955
- M_corrected (F_m*(1-H_block)): 1.937 (H_block=0.009)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +58.6482%
- H_block (lock_quality): 0.009
- band_power_capture: 0.5456550019127121
- chaos_mode=dynamic, PE_tick_norm=0.485558741082517, T_ticks=200
- mean_H_lock_norm=0.008482856602908796, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0019 / 0.0002 / 0.0056

### deuteron_block_0026 (run_id=197)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 2.375
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8518518518518519, 1.9259259259259258, 2.0, 2.074074074074074]
- F_m (base): 1.852 GeV
- M_eff (base≈F_m): 1.852
- M_corrected (F_m*(1-H_block)): 1.849 (H_block=0.001)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -1.2667%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5835886979824053, T_ticks=200
- mean_H_lock_norm=0.0013718803824518783, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0018 / 0.0004 / 0.0039

### delta_1232_block_0023 (run_id=225)
- Partícula: delta_1232, tier: level1, s2_state: latent
- match_score.d_total: 3.511
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.6153846153846154, 1.6923076923076923, 2.0, 2.076923076923077, 2.153846153846154, 2.230769230769231]
- F_m (base): 1.615 GeV
- M_eff (base≈F_m): 1.615
- M_corrected (F_m*(1-H_block)): 1.593 (H_block=0.014)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +31.1189%
- H_block (lock_quality): 0.014
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6535826621492319, T_ticks=200
- mean_H_lock_norm=0.013917782949252262, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0014 / 0.0001 / 0.0055

### deuteron_block_0027 (run_id=237)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 0.463
- Bandas: count=7.0, s2_band_fraction=0.0
- band_energies_gev: [1.870967741935484, 1.9354838709677418, 2.0, 2.064516129032258, 2.7741935483870965, 2.838709677419355, 2.903225806451613]
- F_m (base): 1.871 GeV
- M_eff (base≈F_m): 1.871
- M_corrected (F_m*(1-H_block)): 1.857 (H_block=0.008)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.2475%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8360452641542858, T_ticks=200
- mean_H_lock_norm=0.007624887170313744, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.5163 / 0.0503 / 0.9527

### delta_1232_block_0024 (run_id=3)
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

### delta_1232_block_0025 (run_id=46)
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

### delta_1232_block_0026 (run_id=182)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.831
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9696969696969695, 1.9848484848484849, 2.0, 2.121212121212121, 2.1363636363636367, 2.1515151515151514]
- F_m (base): 1.970 GeV
- M_eff (base≈F_m): 1.970
- M_corrected (F_m*(1-H_block)): 1.965 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +59.8780%
- H_block (lock_quality): 0.002
- band_power_capture: 0.765098577248005
- chaos_mode=dynamic, PE_tick_norm=0.6971533765286346, T_ticks=200
- mean_H_lock_norm=0.0023272464843644646, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0001 / 0.0000 / 0.0001

### eta_prime_block_0026 (run_id=215)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.355
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.1935483870967742, 1.9677419354838708, 2.0, 2.032258064516129, 2.064516129032258]
- F_m (base): 1.194 GeV
- M_eff (base≈F_m): 1.194
- M_corrected (F_m*(1-H_block)): 1.184 (H_block=0.008)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +24.6161%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.74689959892522, T_ticks=200
- mean_H_lock_norm=0.007921591284349765, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0086 / 0.0007 / 0.0250

### deuteron_block_0028 (run_id=168)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.531
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.8909090909090907, 1.9999999999999998]
- F_m (base): 1.891 GeV
- M_eff (base≈F_m): 1.891
- M_corrected (F_m*(1-H_block)): 1.884 (H_block=0.004)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +0.8157%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6256952582329053, T_ticks=200
- mean_H_lock_norm=0.0036166229122250627, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0004 / 0.0000 / 0.0010

### deuteron_block_0029 (run_id=244)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.227
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.8333333333333335, 1.8750000000000002, 2.0, 2.041666666666667, 2.0833333333333335, 2.1250000000000004]
- F_m (base): 1.833 GeV
- M_eff (base≈F_m): 1.833
- M_corrected (F_m*(1-H_block)): 1.826 (H_block=0.004)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -2.2540%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6014626884368748, T_ticks=200
- mean_H_lock_norm=0.0040486220420290426, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0003 / 0.0000 / 0.0007

### eta_prime_block_0027 (run_id=32)
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

### tau_block_0014 (run_id=82)
- Partícula: tau, tier: level1, s2_state: latent
- match_score.d_total: 0.098
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.777777777777778, 1.888888888888889, 2.0, 2.111111111111111, 2.2222222222222223]
- F_m (base): 1.778 GeV
- M_eff (base≈F_m): 1.778
- M_corrected (F_m*(1-H_block)): 1.763 (H_block=0.008)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +0.0517%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7215479875770656, T_ticks=200
- mean_H_lock_norm=0.008086008822310708, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0012 / 0.0000 / 0.0085

### deuteron_block_0030 (run_id=255)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.353
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8620689655172413, 1.9310344827586206, 2.0, 2.068965517241379]
- F_m (base): 1.862 GeV
- M_eff (base≈F_m): 1.862
- M_corrected (F_m*(1-H_block)): 1.845 (H_block=0.009)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.7220%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6200673407565738, T_ticks=200
- mean_H_lock_norm=0.008959202439381643, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0065 / 0.0004 / 0.0220

### delta_1232_block_0027 (run_id=135)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.680
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [2.0]
- F_m (base): 2.000 GeV
- M_eff (base≈F_m): 2.000
- M_corrected (F_m*(1-H_block)): 1.993 (H_block=0.003)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +62.3377%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5765494229883202, T_ticks=200
- mean_H_lock_norm=0.003465026616285448, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0037 / 0.0003 / 0.0096

### deuteron_block_0031 (run_id=165)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 3.551
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.9111111111111112, 1.9555555555555557, 2.0]
- F_m (base): 1.911 GeV
- M_eff (base≈F_m): 1.911
- M_corrected (F_m*(1-H_block)): 1.909 (H_block=0.001)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.8928%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5809622376470293, T_ticks=200
- mean_H_lock_norm=0.000839047692196854, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0004 / 0.0000 / 0.0011

### delta_1232_block_0028 (run_id=189)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.680
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [2.0]
- F_m (base): 2.000 GeV
- M_eff (base≈F_m): 2.000
- M_corrected (F_m*(1-H_block)): 1.996 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +62.3377%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7679385029773054, T_ticks=200
- mean_H_lock_norm=0.002229852260410275, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0878 / 0.0008 / 0.6529

### deuteron_block_0032 (run_id=8)
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

### delta_1232_block_0029 (run_id=57)
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

### deuteron_block_0033 (run_id=44)
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

### deuteron_block_0034 (run_id=118)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 2.194
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.8536585365853657, 1.9512195121951217, 2.0, 2.048780487804878, 2.097560975609756]
- F_m (base): 1.854 GeV
- M_eff (base≈F_m): 1.854
- M_corrected (F_m*(1-H_block)): 1.846 (H_block=0.004)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -1.1704%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.755059477946527, T_ticks=200
- mean_H_lock_norm=0.003897857964452466, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0007 / 0.0000 / 0.0056

### deuteron_block_0035 (run_id=218)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 3.560
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.8399999999999996, 1.9999999999999998]
- F_m (base): 1.840 GeV
- M_eff (base≈F_m): 1.840
- M_corrected (F_m*(1-H_block)): 1.835 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -1.8986%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6218075562821846, T_ticks=200
- mean_H_lock_norm=0.0029576008599957863, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0004 / 0.0001 / 0.0008

### deuteron_block_0036 (run_id=227)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 8.518
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9607843137254901, 2.0]
- F_m (base): 1.961 GeV
- M_eff (base≈F_m): 1.961
- M_corrected (F_m*(1-H_block)): 1.943 (H_block=0.009)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +4.5412%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6316589488043959, T_ticks=200
- mean_H_lock_norm=0.008918399449536728, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0235 / 0.0016 / 0.0703

### delta_1232_block_0030 (run_id=236)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.709
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.5000000000000002, 1.9000000000000001, 2.0, 2.1, 2.2]
- F_m (base): 1.500 GeV
- M_eff (base≈F_m): 1.500
- M_corrected (F_m*(1-H_block)): 1.499 (H_block=0.001)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +21.7532%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.626112760541298, T_ticks=200
- mean_H_lock_norm=0.0008451076743096579, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0013 / 0.0002 / 0.0031

### tau_block_0015 (run_id=128)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 4.347
- Bandas: count=7.0, s2_band_fraction=0.0
- band_energies_gev: [1.7333333333333334, 1.8666666666666667, 1.9999999999999998, 2.1333333333333333, 2.533333333333333, 2.666666666666667, 2.8000000000000003]
- F_m (base): 1.733 GeV
- M_eff (base≈F_m): 1.733
- M_corrected (F_m*(1-H_block)): 1.723 (H_block=0.006)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -2.4496%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6601875087809711, T_ticks=200
- mean_H_lock_norm=0.005662268090300235, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.1443 / 0.0026 / 0.5605

### deuteron_block_0037 (run_id=63)
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

### delta_1232_block_0031 (run_id=90)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.992
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.4883720930232558, 1.5348837209302326, 2.0]
- F_m (base): 1.488 GeV
- M_eff (base≈F_m): 1.488
- M_corrected (F_m*(1-H_block)): 1.484 (H_block=0.003)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +20.8094%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8116340119953093, T_ticks=200
- mean_H_lock_norm=0.0028362117072123654, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0009 / 0.0001 / 0.0020

### delta_1232_block_0032 (run_id=61)
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

### delta_1232_block_0033 (run_id=109)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.982
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.5555555555555556, 1.9259259259259258, 2.0, 2.074074074074074, 2.148148148148148]
- F_m (base): 1.556 GeV
- M_eff (base≈F_m): 1.556
- M_corrected (F_m*(1-H_block)): 1.553 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +26.2626%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6253836640534036, T_ticks=200
- mean_H_lock_norm=0.0018545098548989336, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0012 / 0.0001 / 0.0029

### delta_1232_block_0034 (run_id=145)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.880
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.4666666666666666, 1.9733333333333332, 2.0, 2.026666666666667]
- F_m (base): 1.467 GeV
- M_eff (base≈F_m): 1.467
- M_corrected (F_m*(1-H_block)): 1.450 (H_block=0.011)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +19.0476%
- H_block (lock_quality): 0.011
- band_power_capture: 0.8040262754229885
- chaos_mode=dynamic, PE_tick_norm=0.7716611039833001, T_ticks=200
- mean_H_lock_norm=0.010872857153952836, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0048 / 0.0005 / 0.0130

### deuteron_block_0038 (run_id=205)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.597
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.9215686274509802, 1.9607843137254901, 2.0, 2.1176470588235294, 2.1568627450980395, 2.1960784313725488]
- F_m (base): 1.922 GeV
- M_eff (base≈F_m): 1.922
- M_corrected (F_m*(1-H_block)): 1.908 (H_block=0.007)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.4503%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5975445079891881, T_ticks=200
- mean_H_lock_norm=0.006789682548962269, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0005 / 0.0001 / 0.0011

### eta_prime_block_0028 (run_id=175)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 1.976
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.1555555555555557, 1.9555555555555557, 2.0, 2.0444444444444447]
- F_m (base): 1.156 GeV
- M_eff (base≈F_m): 1.156
- M_corrected (F_m*(1-H_block)): 1.146 (H_block=0.008)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +20.6494%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6525352830537613, T_ticks=200
- mean_H_lock_norm=0.007774533387407249, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0067 / 0.0004 / 0.0247

### deuteron_block_0039 (run_id=185)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 6.961
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9452054794520548, 1.972602739726027, 2.0, 2.4383561643835616]
- F_m (base): 1.945 GeV
- M_eff (base≈F_m): 1.945
- M_corrected (F_m*(1-H_block)): 1.933 (H_block=0.006)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.7106%
- H_block (lock_quality): 0.006
- band_power_capture: 0.7965635803089122
- chaos_mode=dynamic, PE_tick_norm=0.6586609331767411, T_ticks=200
- mean_H_lock_norm=0.006317503971190772, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0015 / 0.0001 / 0.0038

### delta_1232_block_0035 (run_id=106)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.047
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.5555555555555556, 1.6666666666666663, 2.0, 2.1111111111111107]
- F_m (base): 1.556 GeV
- M_eff (base≈F_m): 1.556
- M_corrected (F_m*(1-H_block)): 1.545 (H_block=0.007)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +26.2626%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8757977256248135, T_ticks=200
- mean_H_lock_norm=0.006974633465615904, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0085 / 0.0010 / 0.0477

### eta_prime_block_0029 (run_id=252)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.056
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [0.9523809523809524, 1.9047619047619049, 2.0, 2.095238095238095]
- F_m (base): 0.952 GeV
- M_eff (base≈F_m): 0.952
- M_corrected (F_m*(1-H_block)): 0.952 (H_block=0.001)
- sm_mass_gev: 0.958
- Δ_mass vs SM: -0.5637%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6362910825626833, T_ticks=200
- mean_H_lock_norm=0.0008773404458159743, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0035 / 0.0002 / 0.0472

### eta_prime_block_0030 (run_id=24)
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

### tau_block_0016 (run_id=13)
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

### tau_block_0017 (run_id=15)
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

### delta_1232_block_0036 (run_id=222)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.166
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.5238095238095237, 1.619047619047619, 1.9999999999999998, 2.095238095238095]
- F_m (base): 1.524 GeV
- M_eff (base≈F_m): 1.524
- M_corrected (F_m*(1-H_block)): 1.519 (H_block=0.003)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +23.6858%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7072390815932758, T_ticks=200
- mean_H_lock_norm=0.0029590294098205674, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0007 / 0.0001 / 0.0015

### deuteron_block_0040 (run_id=254)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 3.116
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.8444444444444443, 1.8666666666666667, 2.0]
- F_m (base): 1.844 GeV
- M_eff (base≈F_m): 1.844
- M_corrected (F_m*(1-H_block)): 1.831 (H_block=0.007)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -1.6616%
- H_block (lock_quality): 0.007
- band_power_capture: 0.8177054244792872
- chaos_mode=dynamic, PE_tick_norm=0.8228458180235744, T_ticks=200
- mean_H_lock_norm=0.007167661101023668, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0052 / 0.0000 / 0.0581

### tau_block_0018 (run_id=67)
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

### delta_1232_block_0037 (run_id=77)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.140
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.5483870967741937, 1.9354838709677418, 1.9999999999999998, 2.064516129032258, 2.1290322580645165]
- F_m (base): 1.548 GeV
- M_eff (base≈F_m): 1.548
- M_corrected (F_m*(1-H_block)): 1.546 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +25.6808%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6853738100768066, T_ticks=200
- mean_H_lock_norm=0.0016159560157570942, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0021 / 0.0001 / 0.0052

### deuteron_block_0041 (run_id=159)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 0.060
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.8750000000000002, 1.9375000000000004, 2.0, 2.0625, 2.125, 2.1875]
- F_m (base): 1.875 GeV
- M_eff (base≈F_m): 1.875
- M_corrected (F_m*(1-H_block)): 1.872 (H_block=0.001)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.0325%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6968768341249689, T_ticks=200
- mean_H_lock_norm=0.0013304357244589271, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0020 / 0.0001 / 0.0093

### delta_1232_block_0038 (run_id=116)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.851
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.5681818181818186, 1.590909090909091, 2.0, 2.022727272727273, 2.045454545454546, 2.0681818181818183, 2.0909090909090913]
- F_m (base): 1.568 GeV
- M_eff (base≈F_m): 1.568
- M_corrected (F_m*(1-H_block)): 1.553 (H_block=0.010)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +27.2875%
- H_block (lock_quality): 0.010
- band_power_capture: 0.6114489669109071
- chaos_mode=dynamic, PE_tick_norm=0.6077104155619911, T_ticks=200
- mean_H_lock_norm=0.00956663101420972, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0046 / 0.0010 / 0.0108

### deuteron_block_0042 (run_id=238)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 2.916
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.9047619047619047, 1.9523809523809523, 1.9999999999999998]
- F_m (base): 1.905 GeV
- M_eff (base≈F_m): 1.905
- M_corrected (F_m*(1-H_block)): 1.898 (H_block=0.004)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.5543%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6382853588760774, T_ticks=200
- mean_H_lock_norm=0.003622388934641022, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0009 / 0.0000 / 0.0017

### eta_prime_block_0031 (run_id=170)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.277
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.285714285714286, 1.4285714285714288, 2.0, 2.1428571428571432]
- F_m (base): 1.286 GeV
- M_eff (base≈F_m): 1.286
- M_corrected (F_m*(1-H_block)): 1.282 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +34.2390%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8087111756152723, T_ticks=200
- mean_H_lock_norm=0.003073253331429996, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.9551 / 0.8801 / 0.9907

### tau_block_0019 (run_id=99)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 0.098
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.7777777777777777, 1.9444444444444446, 2.0, 2.055555555555556, 2.111111111111111]
- F_m (base): 1.778 GeV
- M_eff (base≈F_m): 1.778
- M_corrected (F_m*(1-H_block)): 1.770 (H_block=0.005)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +0.0517%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6610575751073485, T_ticks=200
- mean_H_lock_norm=0.00458320094757158, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.1647 / 0.0077 / 0.5969

### tau_block_0020 (run_id=245)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 4.929
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8260869565217392, 1.9130434782608696, 2.0, 2.0869565217391304]
- F_m (base): 1.826 GeV
- M_eff (base≈F_m): 1.826
- M_corrected (F_m*(1-H_block)): 1.819 (H_block=0.004)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +2.7704%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7193526997331058, T_ticks=200
- mean_H_lock_norm=0.0038634333429519883, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0179 / 0.0003 / 0.2841

### deuteron_block_0043 (run_id=89)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 8.358
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9591836734693882, 2.0]
- F_m (base): 1.959 GeV
- M_eff (base≈F_m): 1.959
- M_corrected (F_m*(1-H_block)): 1.953 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +4.4558%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5833538589290748, T_ticks=200
- mean_H_lock_norm=0.0033655750707544917, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0048 / 0.0002 / 0.0132

### deuteron_block_0044 (run_id=139)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.440
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9200000000000002, 2.0]
- F_m (base): 1.920 GeV
- M_eff (base≈F_m): 1.920
- M_corrected (F_m*(1-H_block)): 1.909 (H_block=0.006)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.3667%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6662412605572863, T_ticks=200
- mean_H_lock_norm=0.005943973512145604, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0010 / 0.0002 / 0.0020

### tau_block_0021 (run_id=96)
- Partícula: tau, tier: level1, s2_state: latent
- match_score.d_total: 4.138
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.818181818181818, 1.9090909090909092, 2.0, 2.090909090909091, 2.181818181818182]
- F_m (base): 1.818 GeV
- M_eff (base≈F_m): 1.818
- M_corrected (F_m*(1-H_block)): 1.799 (H_block=0.011)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +2.3256%
- H_block (lock_quality): 0.011
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.9142998233959687, T_ticks=200
- mean_H_lock_norm=0.01079032398099015, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.8029 / 0.4672 / 0.9609

### deuteron_block_0045 (run_id=232)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.846
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8571428571428572, 1.9285714285714284, 2.0, 2.071428571428571]
- F_m (base): 1.857 GeV
- M_eff (base≈F_m): 1.857
- M_corrected (F_m*(1-H_block)): 1.845 (H_block=0.007)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.9846%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6982612032277608, T_ticks=200
- mean_H_lock_norm=0.006725581327980378, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0010 / 0.0002 / 0.0026

### delta_1232_block_0039 (run_id=166)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.498
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.6129032258064513, 1.9354838709677418, 2.0, 2.0645161290322576, 2.1290322580645156]
- F_m (base): 1.613 GeV
- M_eff (base≈F_m): 1.613
- M_corrected (F_m*(1-H_block)): 1.605 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +30.9175%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.843429114409622, T_ticks=200
- mean_H_lock_norm=0.004575142814647033, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.5074 / 0.0207 / 0.9559

### eta_prime_block_0032 (run_id=190)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.535
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.2115384615384615, 1.9807692307692306, 2.0, 2.0384615384615388]
- F_m (base): 1.212 GeV
- M_eff (base≈F_m): 1.212
- M_corrected (F_m*(1-H_block)): 1.200 (H_block=0.010)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +26.4944%
- H_block (lock_quality): 0.010
- band_power_capture: 0.9546000767502308
- chaos_mode=dynamic, PE_tick_norm=0.36599038438988296, T_ticks=200
- mean_H_lock_norm=0.009185168712119263, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0174 / 0.0015 / 0.0481

### delta_1232_block_0040 (run_id=239)
- Partícula: delta_1232, tier: none, s2_state: structural
- match_score.d_total: 8.110
- Bandas: count=1.0, s2_band_fraction=1.0
- band_energies_gev: [1.9954180985108816, 1.9977090492554406, 2.0, 2.002290950744559, 2.004581901489118, 2.006872852233677, 2.009163802978236, 2.011454753722795, 2.013745704467354, 2.016036655211913, 2.0183276059564714, 2.0206185567010304, 2.0229095074455894, 2.025200458190149, 2.027491408934708, 2.029782359679267, 2.0320733104238258, 2.0343642611683848, 2.0366552119129437, 2.0389461626575027, 2.0412371134020617, 2.0435280641466207, 2.0458190148911797, 2.0481099656357387, 2.050400916380298, 2.052691867124857, 2.0549828178694156, 2.0572737686139746, 2.0595647193585336, 2.0618556701030926]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.995 (H_block=0.000)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +61.9658%
- H_block (lock_quality): 0.000
- band_power_capture: 0.05773440203255442
- chaos_mode=dynamic, PE_tick_norm=0.7729323420625397, T_ticks=200
- mean_H_lock_norm=0.0003902535780989829, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=1.0
- lock_S1_series (mean/min/max): 0.0000 / 0.0000 / 0.0001

### deuteron_block_0046 (run_id=40)
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

### eta_prime_block_0033 (run_id=79)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 4.266
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.3846153846153846, 1.4230769230769234, 2.0]
- F_m (base): 1.385 GeV
- M_eff (base≈F_m): 1.385
- M_corrected (F_m*(1-H_block)): 1.378 (H_block=0.005)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +44.5651%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8258401180056061, T_ticks=200
- mean_H_lock_norm=0.004936947088510442, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0024 / 0.0002 / 0.0081

### delta_1232_block_0041 (run_id=88)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.031
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.6266666666666667, 2.0]
- F_m (base): 1.627 GeV
- M_eff (base≈F_m): 1.627
- M_corrected (F_m*(1-H_block)): 1.616 (H_block=0.006)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +32.0346%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7308358739488395, T_ticks=200
- mean_H_lock_norm=0.00646174053364839, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0009 / 0.0000 / 0.0020

### delta_1232_block_0042 (run_id=125)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.680
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [2.0]
- F_m (base): 2.000 GeV
- M_eff (base≈F_m): 2.000
- M_corrected (F_m*(1-H_block)): 1.994 (H_block=0.003)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +62.3377%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5684273134448731, T_ticks=200
- mean_H_lock_norm=0.0027963152288454146, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0014 / 0.0002 / 0.0035

### quark_s_const_block_0002 (run_id=241)
- Partícula: quark_s_const, tier: none, s2_state: none
- match_score.d_total: 0.751
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [0.5901639344262295, 1.9918032786885247, 2.0, 2.0081967213114753]
- F_m (base): 0.590 GeV
- M_eff (base≈F_m): 0.590
- M_corrected (F_m*(1-H_block)): 0.286 (H_block=0.515)
- sm_mass_gev: 0.510
- Δ_mass vs SM: +15.7184%
- H_block (lock_quality): 0.515
- band_power_capture: 0.9045061168090243
- chaos_mode=dynamic, PE_tick_norm=0.8686130673506475, T_ticks=200
- mean_H_lock_norm=0.008755501304259061, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.8112781244591328
- fraction_structured=0.75
- lock_S1_series (mean/min/max): 0.9224 / 0.7244 / 0.9925

### deuteron_block_0047 (run_id=21)
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

### eta_prime_block_0034 (run_id=249)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.420
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.2000000000000002, 1.2800000000000002, 2.0, 2.0800000000000005, 2.16]
- F_m (base): 1.200 GeV
- M_eff (base≈F_m): 1.200
- M_corrected (F_m*(1-H_block)): 1.192 (H_block=0.007)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +25.2897%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7785012251171014, T_ticks=200
- mean_H_lock_norm=0.006970536628603925, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0080 / 0.0002 / 0.0609

### eta_prime_block_0035 (run_id=14)
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

### deuteron_block_0048 (run_id=192)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 0.893
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.866666666666667, 1.9333333333333331, 2.0, 2.066666666666667]
- F_m (base): 1.867 GeV
- M_eff (base≈F_m): 1.867
- M_corrected (F_m*(1-H_block)): 1.861 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.4768%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7724856015128156, T_ticks=200
- mean_H_lock_norm=0.0031550017149411616, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0349 / 0.0005 / 0.2977

### deuteron_block_0049 (run_id=131)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.914
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.894736842105263, 1.9473684210526312, 2.0, 2.052631578947368]
- F_m (base): 1.895 GeV
- M_eff (base≈F_m): 1.895
- M_corrected (F_m*(1-H_block)): 1.885 (H_block=0.005)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.0198%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7230674669104049, T_ticks=200
- mean_H_lock_norm=0.0049897727418877, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0018 / 0.0001 / 0.0036

### eta_prime_block_0036 (run_id=114)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.420
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.0, 1.0769230769230769, 2.0]
- F_m (base): 1.000 GeV
- M_eff (base≈F_m): 1.000
- M_corrected (F_m*(1-H_block)): 0.995 (H_block=0.005)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +4.4081%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7696954409070286, T_ticks=200
- mean_H_lock_norm=0.004809229037336219, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0047 / 0.0004 / 0.0149

### tau_block_0022 (run_id=144)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 3.996
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.736842105263158, 1.7894736842105263, 2.0, 2.0526315789473686, 2.105263157894737]
- F_m (base): 1.737 GeV
- M_eff (base≈F_m): 1.737
- M_corrected (F_m*(1-H_block)): 1.723 (H_block=0.008)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -2.2522%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7226875063705405, T_ticks=200
- mean_H_lock_norm=0.007658465700587094, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0013 / 0.0003 / 0.0032

### eta_prime_block_0037 (run_id=229)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.591
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.3170731707317076, 1.9756097560975612, 2.0]
- F_m (base): 1.317 GeV
- M_eff (base≈F_m): 1.317
- M_corrected (F_m*(1-H_block)): 1.309 (H_block=0.006)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +37.5131%
- H_block (lock_quality): 0.006
- band_power_capture: 0.9530939139734953
- chaos_mode=dynamic, PE_tick_norm=0.5635510795244059, T_ticks=200
- mean_H_lock_norm=0.005830998608874396, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0087 / 0.0007 / 0.0228

### delta_1232_block_0043 (run_id=209)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.577
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.647058823529412, 1.8823529411764706, 2.0, 2.1176470588235294, 2.2352941176470584]
- F_m (base): 1.647 GeV
- M_eff (base≈F_m): 1.647
- M_corrected (F_m*(1-H_block)): 1.644 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +33.6898%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7452184549677, T_ticks=200
- mean_H_lock_norm=0.0020930106845684455, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0448 / 0.0002 / 0.4191

### eta_prime_block_0038 (run_id=68)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 4.266
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.3846153846153846, 1.4230769230769231, 2.0, 2.0384615384615388]
- F_m (base): 1.385 GeV
- M_eff (base≈F_m): 1.385
- M_corrected (F_m*(1-H_block)): 1.375 (H_block=0.007)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +44.5651%
- H_block (lock_quality): 0.007
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7415902618810624, T_ticks=200
- mean_H_lock_norm=0.0067693980691743184, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0048 / 0.0001 / 0.0130

### deuteron_block_0050 (run_id=184)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 3.551
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.9111111111111112, 1.9555555555555555, 2.0, 2.0444444444444443, 2.0888888888888886]
- F_m (base): 1.911 GeV
- M_eff (base≈F_m): 1.911
- M_corrected (F_m*(1-H_block)): 1.901 (H_block=0.005)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.8928%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.523470228301015, T_ticks=200
- mean_H_lock_norm=0.004982125465826354, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0564 / 0.0096 / 0.1620

### delta_1232_block_0044 (run_id=58)
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

### eta_prime_block_0039 (run_id=55)
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

### eta_prime_block_0040 (run_id=33)
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

### eta_prime_block_0041 (run_id=136)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.420
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.0, 2.0]
- F_m (base): 1.000 GeV
- M_eff (base≈F_m): 1.000
- M_corrected (F_m*(1-H_block)): 0.996 (H_block=0.004)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +4.4081%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8669401871474106, T_ticks=200
- mean_H_lock_norm=0.004241562609792021, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0461 / 0.0008 / 0.3225

### delta_1232_block_0045 (run_id=231)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 2.919
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.4285714285714286, 1.5714285714285716, 2.0]
- F_m (base): 1.429 GeV
- M_eff (base≈F_m): 1.429
- M_corrected (F_m*(1-H_block)): 1.425 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +15.9555%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8055342269868513, T_ticks=200
- mean_H_lock_norm=0.0021595832248923748, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0100 / 0.0005 / 0.0600

### eta_prime_block_0042 (run_id=121)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.634
- Bandas: count=7.0, s2_band_fraction=0.0
- band_energies_gev: [1.3214285714285716, 1.3571428571428572, 2.0, 2.035714285714286, 2.0714285714285716, 2.107142857142857, 2.1428571428571432]
- F_m (base): 1.321 GeV
- M_eff (base≈F_m): 1.321
- M_corrected (F_m*(1-H_block)): 1.317 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +37.9679%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7055012937532361, T_ticks=200
- mean_H_lock_norm=0.003109353778303185, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0040 / 0.0002 / 0.0109

### deuteron_block_0051 (run_id=148)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.545
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.921052631578947, 1.9999999999999998]
- F_m (base): 1.921 GeV
- M_eff (base≈F_m): 1.921
- M_corrected (F_m*(1-H_block)): 1.904 (H_block=0.009)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.4228%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.634361610993771, T_ticks=200
- mean_H_lock_norm=0.008822975347577436, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0020 / 0.0007 / 0.0037

### deuteron_block_0052 (run_id=206)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.440
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9200000000000002, 2.0]
- F_m (base): 1.920 GeV
- M_eff (base≈F_m): 1.920
- M_corrected (F_m*(1-H_block)): 1.913 (H_block=0.004)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.3667%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7546194612018869, T_ticks=200
- mean_H_lock_norm=0.0038634537324390705, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0038 / 0.0001 / 0.0293

### deuteron_block_0053 (run_id=112)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.329
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.8888888888888888, 1.9444444444444444, 2.0, 2.2777777777777777, 2.3333333333333335]
- F_m (base): 1.889 GeV
- M_eff (base≈F_m): 1.889
- M_corrected (F_m*(1-H_block)): 1.881 (H_block=0.004)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +0.7080%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7960075368834121, T_ticks=200
- mean_H_lock_norm=0.0039743455531513604, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0021 / 0.0001 / 0.0175

### delta_1232_block_0046 (run_id=35)
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

### eta_prime_block_0043 (run_id=162)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.489
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [0.9090909090909093, 1.9090909090909092, 2.0]
- F_m (base): 0.909 GeV
- M_eff (base≈F_m): 0.909
- M_corrected (F_m*(1-H_block)): 0.908 (H_block=0.001)
- sm_mass_gev: 0.958
- Δ_mass vs SM: -5.0835%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6668847761585183, T_ticks=200
- mean_H_lock_norm=0.0014571472714577538, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.2180 / 0.0022 / 0.8140

### delta_1232_block_0047 (run_id=71)
- Partícula: delta_1232, tier: none, s2_state: latent
- match_score.d_total: 8.051
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9899497487437183, 1.994974874371859, 2.0, 2.0050251256281406, 2.0100502512562812, 2.0150753768844223, 2.0201005025125625, 2.0251256281407035, 2.030150753768844, 2.0351758793969847, 2.040201005025126, 2.0452261306532664, 2.0502512562814066, 2.0552763819095476, 2.0603015075376883, 2.065326633165829]
- F_m (base): 1.990 GeV
- M_eff (base≈F_m): 1.990
- M_corrected (F_m*(1-H_block)): 1.936 (H_block=0.027)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +61.5219%
- H_block (lock_quality): 0.027
- band_power_capture: 0.1834993795011502
- chaos_mode=dynamic, PE_tick_norm=0.5074390851579673, T_ticks=200
- mean_H_lock_norm=0.02690789389079947, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=1.0
- lock_S1_series (mean/min/max): 0.9892 / 0.9699 / 0.9950

### delta_1232_block_0048 (run_id=164)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.680
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [2.0]
- F_m (base): 2.000 GeV
- M_eff (base≈F_m): 2.000
- M_corrected (F_m*(1-H_block)): 1.990 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +62.3377%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6641443229215116, T_ticks=200
- mean_H_lock_norm=0.0047904603093419556, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0010 / 0.0003 / 0.0042

### tau_block_0023 (run_id=120)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 3.272
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8095238095238095, 1.9047619047619044, 2.0, 2.0476190476190474]
- F_m (base): 1.810 GeV
- M_eff (base≈F_m): 1.810
- M_corrected (F_m*(1-H_block)): 1.807 (H_block=0.001)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +1.8383%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7364294596309424, T_ticks=200
- mean_H_lock_norm=0.001294245969023008, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0004 / 0.0000 / 0.0013

### delta_1232_block_0049 (run_id=80)
- Partícula: delta_1232, tier: level1, s2_state: latent
- match_score.d_total: 4.673
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.4583333333333333, 1.9583333333333333, 1.9999999999999998, 2.041666666666666, 2.083333333333333]
- F_m (base): 1.458 GeV
- M_eff (base≈F_m): 1.458
- M_corrected (F_m*(1-H_block)): 1.445 (H_block=0.009)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +18.3712%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.636797185058814, T_ticks=200
- mean_H_lock_norm=0.009189432387232379, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0034 / 0.0003 / 0.0080

### delta_1232_block_0050 (run_id=56)
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

### deuteron_block_0054 (run_id=60)
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

### delta_1232_block_0051 (run_id=137)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 5.004
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.6470588235294115, 1.9852941176470587, 1.9999999999999998, 2.014705882352941, 2.029411764705882]
- F_m (base): 1.647 GeV
- M_eff (base≈F_m): 1.647
- M_corrected (F_m*(1-H_block)): 1.629 (H_block=0.011)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +33.6898%
- H_block (lock_quality): 0.011
- band_power_capture: 0.6232428732443038
- chaos_mode=dynamic, PE_tick_norm=0.6275872817883091, T_ticks=200
- mean_H_lock_norm=0.010886916637553631, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0048 / 0.0009 / 0.0101

### eta_prime_block_0044 (run_id=138)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.991
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.357142857142857, 1.9642857142857142, 2.0, 2.0357142857142856, 2.071428571428571]
- F_m (base): 1.357 GeV
- M_eff (base≈F_m): 1.357
- M_corrected (F_m*(1-H_block)): 1.349 (H_block=0.006)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +41.6967%
- H_block (lock_quality): 0.006
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6112323286887673, T_ticks=200
- mean_H_lock_norm=0.0061485463956380965, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0059 / 0.0000 / 0.0245

### delta_1232_block_0052 (run_id=39)
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

### delta_1232_block_0053 (run_id=30)
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

### delta_1232_block_0054 (run_id=20)
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

### delta_1232_block_0055 (run_id=75)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 9.393
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9718309859154932, 2.0]
- F_m (base): 1.972 GeV
- M_eff (base≈F_m): 1.972
- M_corrected (F_m*(1-H_block)): 1.960 (H_block=0.006)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +60.0512%
- H_block (lock_quality): 0.006
- band_power_capture: 0.892069513121451
- chaos_mode=dynamic, PE_tick_norm=0.5500961438654721, T_ticks=200
- mean_H_lock_norm=0.006092841882836311, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0185 / 0.0010 / 0.0539

### delta_1232_block_0056 (run_id=151)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.680
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [2.0]
- F_m (base): 2.000 GeV
- M_eff (base≈F_m): 2.000
- M_corrected (F_m*(1-H_block)): 1.989 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +62.3377%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5754177544506838, T_ticks=200
- mean_H_lock_norm=0.005349484854006605, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0006 / 0.0004 / 0.0011

### delta_1232_block_0057 (run_id=38)
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

### delta_1232_block_0058 (run_id=27)
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

### delta_1232_block_0059 (run_id=81)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.416
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.5999999999999999, 1.9428571428571428, 2.0]
- F_m (base): 1.600 GeV
- M_eff (base≈F_m): 1.600
- M_corrected (F_m*(1-H_block)): 1.592 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +29.8701%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8999381676399578, T_ticks=200
- mean_H_lock_norm=0.004697998864776419, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.5677 / 0.2105 / 0.8958

### delta_1232_block_0060 (run_id=187)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.380
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.7017543859649125, 1.719298245614035, 2.0, 2.017543859649123, 2.0350877192982457, 2.0526315789473686, 2.0701754385964914, 2.0877192982456143, 2.105263157894737]
- F_m (base): 1.702 GeV
- M_eff (base≈F_m): 1.702
- M_corrected (F_m*(1-H_block)): 1.679 (H_block=0.013)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +38.1294%
- H_block (lock_quality): 0.013
- band_power_capture: 0.48607859131277475
- chaos_mode=dynamic, PE_tick_norm=0.60095276771695, T_ticks=200
- mean_H_lock_norm=0.01297597740072442, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0059 / 0.0011 / 0.0137

### eta_prime_block_0045 (run_id=92)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.563
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.2142857142857144, 1.2857142857142856, 2.0, 2.0714285714285716]
- F_m (base): 1.214 GeV
- M_eff (base≈F_m): 1.214
- M_corrected (F_m*(1-H_block)): 1.211 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +26.7813%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8583813335015505, T_ticks=200
- mean_H_lock_norm=0.002829201099517194, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.9657 / 0.9195 / 0.9879

### deuteron_block_0055 (run_id=11)
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

### eta_prime_block_0046 (run_id=199)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 1.753
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.1333333333333335, 1.2000000000000002, 2.0, 2.066666666666667, 2.1333333333333337, 2.2000000000000006]
- F_m (base): 1.133 GeV
- M_eff (base≈F_m): 1.133
- M_corrected (F_m*(1-H_block)): 1.130 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +18.3292%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.842909121148074, T_ticks=200
- mean_H_lock_norm=0.0031900838119680816, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0045 / 0.0007 / 0.0123

### delta_1232_block_0061 (run_id=129)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.773
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.964285714285714, 1.9821428571428568, 2.0, 2.142857142857143, 2.1607142857142856]
- F_m (base): 1.964 GeV
- M_eff (base≈F_m): 1.964
- M_corrected (F_m*(1-H_block)): 1.960 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +59.4388%
- H_block (lock_quality): 0.002
- band_power_capture: 0.8620919909197461
- chaos_mode=dynamic, PE_tick_norm=0.5165294787677888, T_ticks=200
- mean_H_lock_norm=0.0019269042414613354, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0017 / 0.0002 / 0.0044

### eta_prime_block_0047 (run_id=132)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.056
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [0.9523809523809526, 1.047619047619048, 2.0, 2.095238095238096]
- F_m (base): 0.952 GeV
- M_eff (base≈F_m): 0.952
- M_corrected (F_m*(1-H_block)): 0.947 (H_block=0.005)
- sm_mass_gev: 0.958
- Δ_mass vs SM: -0.5637%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6894442871437523, T_ticks=200
- mean_H_lock_norm=0.005032406883700206, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0106 / 0.0008 / 0.0404

### delta_1232_block_0062 (run_id=158)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.522
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.4588235294117646, 1.4823529411764704, 2.0, 2.023529411764706]
- F_m (base): 1.459 GeV
- M_eff (base≈F_m): 1.459
- M_corrected (F_m*(1-H_block)): 1.452 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +18.4110%
- H_block (lock_quality): 0.005
- band_power_capture: 0.8365054740152641
- chaos_mode=dynamic, PE_tick_norm=0.6774988800998379, T_ticks=200
- mean_H_lock_norm=0.004507967483662978, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0028 / 0.0003 / 0.0069

### tau_block_0024 (run_id=36)
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

### deuteron_block_0056 (run_id=150)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 7.312
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9487179487179487, 1.974358974358974, 2.0, 2.0256410256410255]
- F_m (base): 1.949 GeV
- M_eff (base≈F_m): 1.949
- M_corrected (F_m*(1-H_block)): 1.923 (H_block=0.013)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +3.8978%
- H_block (lock_quality): 0.013
- band_power_capture: 0.5639444128217946
- chaos_mode=dynamic, PE_tick_norm=0.5651075774125219, T_ticks=200
- mean_H_lock_norm=0.013031968191375483, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0282 / 0.0019 / 0.0949

### deuteron_block_0057 (run_id=176)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.581
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.8297872340425532, 1.957446808510638, 1.9999999999999998, 2.042553191489361, 2.085106382978723]
- F_m (base): 1.830 GeV
- M_eff (base≈F_m): 1.830
- M_corrected (F_m*(1-H_block)): 1.826 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -2.4431%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6264376030291636, T_ticks=200
- mean_H_lock_norm=0.0019743895233163425, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0023 / 0.0000 / 0.0183

### deuteron_block_0058 (run_id=149)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.846
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8571428571428574, 1.9285714285714286, 2.0, 2.0714285714285716]
- F_m (base): 1.857 GeV
- M_eff (base≈F_m): 1.857
- M_corrected (F_m*(1-H_block)): 1.854 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.9846%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6347146956561822, T_ticks=200
- mean_H_lock_norm=0.0015457373681573238, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0007 / 0.0000 / 0.0020

### tau_block_0025 (run_id=22)
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

### deuteron_block_0059 (run_id=34)
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

### quark_ud_const_block_0002 (run_id=83)
- Partícula: quark_ud_const, tier: level2, s2_state: none
- match_score.d_total: 1.716
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [0.1584158415841584, 0.3267326732673267, 1.9999999999999998]
- F_m (base): 0.158 GeV
- M_eff (base≈F_m): 0.158
- M_corrected (F_m*(1-H_block)): 0.066 (H_block=0.583)
- sm_mass_gev: 0.336
- Δ_mass vs SM: -52.8524%
- H_block (lock_quality): 0.583
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8736007982925788, T_ticks=200
- mean_H_lock_norm=0.005552483945731241, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.9182958340544894
- fraction_structured=0.3333333333333333
- lock_S1_series (mean/min/max): 0.9139 / 0.7524 / 0.9755

### delta_1232_block_0063 (run_id=152)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.821
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.647058823529412, 1.9411764705882355, 2.0, 2.058823529411765]
- F_m (base): 1.647 GeV
- M_eff (base≈F_m): 1.647
- M_corrected (F_m*(1-H_block)): 1.643 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +33.6898%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7723607109111666, T_ticks=200
- mean_H_lock_norm=0.0022558052492533368, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0993 / 0.0066 / 0.3489

### deuteron_block_0060 (run_id=103)
- Partícula: deuteron, tier: level1, s2_state: latent
- match_score.d_total: 4.107
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.9166666666666667, 1.958333333333333, 1.9999999999999998, 2.041666666666667]
- F_m (base): 1.917 GeV
- M_eff (base≈F_m): 1.917
- M_corrected (F_m*(1-H_block)): 1.894 (H_block=0.012)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.1890%
- H_block (lock_quality): 0.012
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6029389932376871, T_ticks=200
- mean_H_lock_norm=0.011389921703384407, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0005 / 0.0001 / 0.0009

### delta_1232_block_0064 (run_id=91)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.570
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.5666666666666664, 1.9666666666666663, 2.0]
- F_m (base): 1.567 GeV
- M_eff (base≈F_m): 1.567
- M_corrected (F_m*(1-H_block)): 1.554 (H_block=0.008)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +27.1645%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7931884935435697, T_ticks=200
- mean_H_lock_norm=0.00819980941096536, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0016 / 0.0001 / 0.0056

### tau_block_0026 (run_id=84)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 0.757
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.7692307692307694, 1.9487179487179487, 2.0, 2.025641025641026, 2.0512820512820515]
- F_m (base): 1.769 GeV
- M_eff (base≈F_m): 1.769
- M_corrected (F_m*(1-H_block)): 1.759 (H_block=0.006)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -0.4294%
- H_block (lock_quality): 0.006
- band_power_capture: 0.8080052667138579
- chaos_mode=dynamic, PE_tick_norm=0.6834034175105994, T_ticks=200
- mean_H_lock_norm=0.00568043971972673, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0001 / 0.0014

### tau_block_0027 (run_id=134)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 1.267
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.7894736842105263, 1.894736842105263, 2.0, 2.1052631578947367]
- F_m (base): 1.789 GeV
- M_eff (base≈F_m): 1.789
- M_corrected (F_m*(1-H_block)): 1.786 (H_block=0.002)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +0.7099%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6470288955254221, T_ticks=200
- mean_H_lock_norm=0.001836100049974687, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0088 / 0.0003 / 0.1434

### tau_block_0028 (run_id=160)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 0.098
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.777777777777778, 1.888888888888889, 2.0, 3.0000000000000004, 3.1111111111111116, 3.2222222222222223]
- F_m (base): 1.778 GeV
- M_eff (base≈F_m): 1.778
- M_corrected (F_m*(1-H_block)): 1.772 (H_block=0.003)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +0.0517%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8131666065149579, T_ticks=200
- mean_H_lock_norm=0.002996984931106464, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0030 / 0.0001 / 0.0212

### deuteron_block_0061 (run_id=169)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 0.463
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8709677419354838, 1.9354838709677418, 2.0, 2.064516129032258]
- F_m (base): 1.871 GeV
- M_eff (base≈F_m): 1.871
- M_corrected (F_m*(1-H_block)): 1.865 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.2475%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7645705836418598, T_ticks=200
- mean_H_lock_norm=0.003158536976911669, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0019 / 0.0000 / 0.0076

### eta_prime_block_0048 (run_id=111)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 4.266
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.3846153846153846, 1.9230769230769234, 2.0, 2.076923076923077, 2.153846153846154]
- F_m (base): 1.385 GeV
- M_eff (base≈F_m): 1.385
- M_corrected (F_m*(1-H_block)): 1.382 (H_block=0.002)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +44.5651%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8683299395850822, T_ticks=200
- mean_H_lock_norm=0.001681355052541125, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0012 / 0.0004 / 0.0027

### eta_prime_block_0049 (run_id=113)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.420
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.2, 1.2444444444444445, 1.9999999999999998, 2.0444444444444447]
- F_m (base): 1.200 GeV
- M_eff (base≈F_m): 1.200
- M_corrected (F_m*(1-H_block)): 1.196 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +25.2897%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7153142800069181, T_ticks=200
- mean_H_lock_norm=0.003286576357947978, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0051 / 0.0004 / 0.0124

### deuteron_block_0062 (run_id=53)
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

### eta_prime_block_0050 (run_id=155)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.898
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.347826086956522, 1.9565217391304348, 2.0]
- F_m (base): 1.348 GeV
- M_eff (base≈F_m): 1.348
- M_corrected (F_m*(1-H_block)): 1.335 (H_block=0.009)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +40.7240%
- H_block (lock_quality): 0.009
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6361146216970691, T_ticks=200
- mean_H_lock_norm=0.008953580817699184, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0097 / 0.0007 / 0.0267

### eta_prime_block_0051 (run_id=17)
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

### deuteron_block_0063 (run_id=41)
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

### tau_block_0029 (run_id=95)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 0.098
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.7777777777777777, 1.8888888888888888, 2.0, 2.1111111111111107, 2.7777777777777777, 2.888888888888889]
- F_m (base): 1.778 GeV
- M_eff (base≈F_m): 1.778
- M_corrected (F_m*(1-H_block)): 1.773 (H_block=0.003)
- sm_mass_gev: 1.777
- Δ_mass vs SM: +0.0517%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8943840592248049, T_ticks=200
- mean_H_lock_norm=0.002624244918637523, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0779 / 0.0001 / 0.6515

### deuteron_block_0064 (run_id=1)
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

### eta_prime_block_0052 (run_id=153)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 0.349
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [0.9230769230769231, 1.9230769230769234, 2.0, 2.076923076923077, 2.153846153846154]
- F_m (base): 0.923 GeV
- M_eff (base≈F_m): 0.923
- M_corrected (F_m*(1-H_block)): 0.919 (H_block=0.004)
- sm_mass_gev: 0.958
- Δ_mass vs SM: -3.6233%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8082795008500253, T_ticks=200
- mean_H_lock_norm=0.004271932021336069, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0282 / 0.0003 / 0.2888

### delta_1232_block_0065 (run_id=142)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.957
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.6923076923076925, 2.0]
- F_m (base): 1.692 GeV
- M_eff (base≈F_m): 1.692
- M_corrected (F_m*(1-H_block)): 1.687 (H_block=0.003)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +37.3626%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7969466216267501, T_ticks=200
- mean_H_lock_norm=0.003030601042146302, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0019 / 0.0000 / 0.0249

### eta_prime_block_0053 (run_id=161)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.728
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.2307692307692306, 1.9230769230769231, 2.0, 2.0769230769230766, 2.153846153846154]
- F_m (base): 1.231 GeV
- M_eff (base≈F_m): 1.231
- M_corrected (F_m*(1-H_block)): 1.229 (H_block=0.001)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +28.5023%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6421990367049716, T_ticks=200
- mean_H_lock_norm=0.001298618850129405, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.8407 / 0.5618 / 0.9537

### eta_prime_block_0054 (run_id=167)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 1.531
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.1111111111111112, 1.9999999999999998]
- F_m (base): 1.111 GeV
- M_eff (base≈F_m): 1.111
- M_corrected (F_m*(1-H_block)): 1.106 (H_block=0.005)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +16.0090%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6997529916345113, T_ticks=200
- mean_H_lock_norm=0.004650838174381675, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0057 / 0.0007 / 0.0156

### deuteron_block_0065 (run_id=196)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.329
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.8888888888888888, 1.9999999999999998]
- F_m (base): 1.889 GeV
- M_eff (base≈F_m): 1.889
- M_corrected (F_m*(1-H_block)): 1.881 (H_block=0.004)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +0.7080%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6233524317346811, T_ticks=200
- mean_H_lock_norm=0.003984288969934012, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.1375 / 0.0031 / 0.6099

### delta_1232_block_0066 (run_id=226)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 7.680
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [2.0]
- F_m (base): 2.000 GeV
- M_eff (base≈F_m): 2.000
- M_corrected (F_m*(1-H_block)): 1.984 (H_block=0.008)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +62.3377%
- H_block (lock_quality): 0.008
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7778653576544383, T_ticks=200
- mean_H_lock_norm=0.007805327127355067, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.2639 / 0.0557 / 0.5992

### eta_prime_block_0055 (run_id=85)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 4.020
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.36, 1.9200000000000004, 2.0, 2.08, 2.16]
- F_m (base): 1.360 GeV
- M_eff (base≈F_m): 1.360
- M_corrected (F_m*(1-H_block)): 1.359 (H_block=0.001)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +41.9950%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6852454212131542, T_ticks=200
- mean_H_lock_norm=0.0008230374615263317, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0017 / 0.0002 / 0.0217

### tau_block_0030 (run_id=115)
- Partícula: tau, tier: level1, s2_state: none
- match_score.d_total: 1.209
- Bandas: count=7.0, s2_band_fraction=0.0
- band_energies_gev: [1.7647058823529413, 1.8823529411764708, 2.0, 2.1176470588235294, 2.2352941176470593, 2.3529411764705888, 2.4705882352941178]
- F_m (base): 1.765 GeV
- M_eff (base≈F_m): 1.765
- M_corrected (F_m*(1-H_block)): 1.760 (H_block=0.003)
- sm_mass_gev: 1.777
- Δ_mass vs SM: -0.6840%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7915893828170005, T_ticks=200
- mean_H_lock_norm=0.002703536658176248, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0026 / 0.0001 / 0.0354

### delta_1232_block_0067 (run_id=108)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.629
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.411764705882353, 1.8823529411764706, 2.0]
- F_m (base): 1.412 GeV
- M_eff (base≈F_m): 1.412
- M_corrected (F_m*(1-H_block)): 1.408 (H_block=0.003)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +14.5913%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.733996993831966, T_ticks=200
- mean_H_lock_norm=0.0028669919079861994, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0839 / 0.0012 / 0.5634

### eta_prime_block_0056 (run_id=202)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 2.420
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.2, 1.9692307692307691, 2.0]
- F_m (base): 1.200 GeV
- M_eff (base≈F_m): 1.200
- M_corrected (F_m*(1-H_block)): 1.195 (H_block=0.004)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +25.2897%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5741908124518443, T_ticks=200
- mean_H_lock_norm=0.004051942001265126, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0129 / 0.0006 / 0.0353

### delta_1232_block_0068 (run_id=9)
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

### tau_block_0031 (run_id=31)
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

### delta_1232_block_0069 (run_id=43)
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

### delta_1232_block_0070 (run_id=117)
- Partícula: delta_1232, tier: level1, s2_state: latent
- match_score.d_total: 3.959
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.5, 1.9166666666666667, 2.0]
- F_m (base): 1.500 GeV
- M_eff (base≈F_m): 1.500
- M_corrected (F_m*(1-H_block)): 1.485 (H_block=0.010)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +21.7532%
- H_block (lock_quality): 0.010
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7601677002771074, T_ticks=200
- mean_H_lock_norm=0.010127207121819453, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.1247 / 0.0064 / 0.4732

### delta_1232_block_0071 (run_id=78)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.546
- Bandas: count=6.0, s2_band_fraction=0.0
- band_energies_gev: [1.6666666666666667, 1.8333333333333335, 2.0, 2.166666666666667, 2.833333333333334, 3.0000000000000004]
- F_m (base): 1.667 GeV
- M_eff (base≈F_m): 1.667
- M_corrected (F_m*(1-H_block)): 1.664 (H_block=0.002)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +35.2814%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6365018920052963, T_ticks=200
- mean_H_lock_norm=0.0016343678080832655, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0005 / 0.0000 / 0.0014

### deuteron_block_0066 (run_id=240)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.107
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9166666666666667, 2.0]
- F_m (base): 1.917 GeV
- M_eff (base≈F_m): 1.917
- M_corrected (F_m*(1-H_block)): 1.913 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.1890%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.738954555052548, T_ticks=200
- mean_H_lock_norm=0.0017475926660290558, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0041 / 0.0001 / 0.0551

### tau_block_0032 (run_id=48)
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

### tau_block_0033 (run_id=7)
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

### delta_1232_block_0072 (run_id=127)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.549
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.5384615384615385, 2.0]
- F_m (base): 1.538 GeV
- M_eff (base≈F_m): 1.538
- M_corrected (F_m*(1-H_block)): 1.534 (H_block=0.003)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +24.8751%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5729303349820796, T_ticks=200
- mean_H_lock_norm=0.0030793126759103935, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0010 / 0.0001 / 0.0024

### deuteron_block_0067 (run_id=64)
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

### delta_1232_block_0073 (run_id=107)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 9.594
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.984496124031008, 2.0]
- F_m (base): 1.984 GeV
- M_eff (base≈F_m): 1.984
- M_corrected (F_m*(1-H_block)): 1.982 (H_block=0.001)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +61.0792%
- H_block (lock_quality): 0.001
- band_power_capture: 0.9518002800035833
- chaos_mode=dynamic, PE_tick_norm=0.7481704270436974, T_ticks=200
- mean_H_lock_norm=0.0010954720074248334, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.1249 / 0.0204 / 0.3234

### deuteron_block_0068 (run_id=163)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 1.353
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.8620689655172413, 1.9655172413793103, 2.0, 2.03448275862069, 2.0689655172413794]
- F_m (base): 1.862 GeV
- M_eff (base≈F_m): 1.862
- M_corrected (F_m*(1-H_block)): 1.856 (H_block=0.003)
- sm_mass_gev: 1.876
- Δ_mass vs SM: -0.7220%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8507942482386295, T_ticks=200
- mean_H_lock_norm=0.002986707104903375, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0273 / 0.0001 / 0.1243

### deuteron_block_0069 (run_id=126)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 0.195
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.8775510204081634, 1.9591836734693882, 2.0, 2.0408163265306123]
- F_m (base): 1.878 GeV
- M_eff (base≈F_m): 1.878
- M_corrected (F_m*(1-H_block)): 1.875 (H_block=0.001)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +0.1035%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6360963005376482, T_ticks=200
- mean_H_lock_norm=0.0012600234497850433, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.1091 / 0.0042 / 0.4289

### deuteron_block_0070 (run_id=230)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 8.273
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9583333333333333, 2.0]
- F_m (base): 1.958 GeV
- M_eff (base≈F_m): 1.958
- M_corrected (F_m*(1-H_block)): 1.956 (H_block=0.001)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +4.4105%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6894164732839239, T_ticks=200
- mean_H_lock_norm=0.001171174949327384, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0845 / 0.0081 / 0.2621

### quark_ud_const_block_0003 (run_id=59)
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

### eta_prime_block_0057 (run_id=146)
- Partícula: eta_prime, tier: level1, s2_state: latent
- match_score.d_total: 0.349
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [0.9230769230769229, 1.923076923076923, 2.0]
- F_m (base): 0.923 GeV
- M_eff (base≈F_m): 0.923
- M_corrected (F_m*(1-H_block)): 0.913 (H_block=0.011)
- sm_mass_gev: 0.958
- Δ_mass vs SM: -3.6233%
- H_block (lock_quality): 0.011
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7315990689076389, T_ticks=200
- mean_H_lock_norm=0.010553317952193149, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0032 / 0.0002 / 0.0145

### eta_prime_block_0058 (run_id=105)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.343
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.2923076923076924, 1.9692307692307693, 1.9999999999999998]
- F_m (base): 1.292 GeV
- M_eff (base≈F_m): 1.292
- M_corrected (F_m*(1-H_block)): 1.289 (H_block=0.002)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +34.9274%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5680315698996088, T_ticks=200
- mean_H_lock_norm=0.002438294220188139, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0040 / 0.0003 / 0.0095

### delta_1232_block_0074 (run_id=198)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 5.358
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.7142857142857144, 1.9285714285714286, 1.9999999999999998, 2.0714285714285716, 2.142857142857143]
- F_m (base): 1.714 GeV
- M_eff (base≈F_m): 1.714
- M_corrected (F_m*(1-H_block)): 1.706 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +39.1466%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8263509455824013, T_ticks=200
- mean_H_lock_norm=0.00489048765784248, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0202 / 0.0001 / 0.3512

### deuteron_block_0071 (run_id=101)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.440
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.9200000000000004, 1.96, 2.0, 2.12, 2.16]
- F_m (base): 1.920 GeV
- M_eff (base≈F_m): 1.920
- M_corrected (F_m*(1-H_block)): 1.911 (H_block=0.005)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.3667%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5573575739004205, T_ticks=200
- mean_H_lock_norm=0.004523323683728131, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0005 / 0.0000 / 0.0012

### delta_1232_block_0075 (run_id=234)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.136
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.4615384615384617, 1.9230769230769231, 2.0]
- F_m (base): 1.462 GeV
- M_eff (base≈F_m): 1.462
- M_corrected (F_m*(1-H_block)): 1.459 (H_block=0.001)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +18.6314%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7955835939695948, T_ticks=200
- mean_H_lock_norm=0.001489998080606561, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0023 / 0.0000 / 0.0104

### delta_1232_block_0076 (run_id=29)
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

### quark_ud_const_block_0004 (run_id=213)
- Partícula: quark_ud_const, tier: level2, s2_state: none
- match_score.d_total: 1.704
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [0.15962441314553988, 0.30985915492957744, 2.0]
- F_m (base): 0.160 GeV
- M_eff (base≈F_m): 0.160
- M_corrected (F_m*(1-H_block)): 0.067 (H_block=0.583)
- sm_mass_gev: 0.336
- Δ_mass vs SM: -52.4927%
- H_block (lock_quality): 0.583
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7616976472621363, T_ticks=200
- mean_H_lock_norm=0.0059563917847537985, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.9182958340544894
- fraction_structured=0.3333333333333333
- lock_S1_series (mean/min/max): 0.7860 / 0.2646 / 0.9861

### delta_1232_block_0077 (run_id=235)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.325
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.5999999999999996, 1.68, 1.9999999999999998, 2.0799999999999996]
- F_m (base): 1.600 GeV
- M_eff (base≈F_m): 1.600
- M_corrected (F_m*(1-H_block)): 1.599 (H_block=0.001)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +29.8701%
- H_block (lock_quality): 0.001
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7672237889861704, T_ticks=200
- mean_H_lock_norm=0.0006588418755930364, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0012 / 0.0000 / 0.0034

### deuteron_block_0072 (run_id=171)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 4.107
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.9166666666666663, 1.9583333333333328, 1.9999999999999998]
- F_m (base): 1.917 GeV
- M_eff (base≈F_m): 1.917
- M_corrected (F_m*(1-H_block)): 1.913 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +2.1890%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.5168077157696864, T_ticks=200
- mean_H_lock_norm=0.00198276116698634, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0010 / 0.0001 / 0.0022

### delta_1232_block_0078 (run_id=247)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.276
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.4838709677419355, 1.935483870967742, 2.0]
- F_m (base): 1.484 GeV
- M_eff (base≈F_m): 1.484
- M_corrected (F_m*(1-H_block)): 1.476 (H_block=0.005)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +20.4441%
- H_block (lock_quality): 0.005
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.8975580948152466, T_ticks=200
- mean_H_lock_norm=0.005370732909016864, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0036 / 0.0004 / 0.0355

### delta_1232_block_0079 (run_id=220)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 4.136
- Bandas: count=4.0, s2_band_fraction=0.0
- band_energies_gev: [1.461538461538462, 1.9230769230769234, 2.0, 2.0769230769230775]
- F_m (base): 1.462 GeV
- M_eff (base≈F_m): 1.462
- M_corrected (F_m*(1-H_block)): 1.455 (H_block=0.004)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +18.6314%
- H_block (lock_quality): 0.004
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.7410999537372297, T_ticks=200
- mean_H_lock_norm=0.004218594303561729, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0007 / 0.0001 / 0.0012

### deuteron_block_0073 (run_id=76)
- Partícula: deuteron, tier: level1, s2_state: none
- match_score.d_total: 2.440
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9000000000000001, 2.0]
- F_m (base): 1.900 GeV
- M_eff (base≈F_m): 1.900
- M_corrected (F_m*(1-H_block)): 1.896 (H_block=0.002)
- sm_mass_gev: 1.876
- Δ_mass vs SM: +1.3004%
- H_block (lock_quality): 0.002
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6447125119711401, T_ticks=200
- mean_H_lock_norm=0.0020719674544174287, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0015 / 0.0004 / 0.0026

### eta_prime_block_0059 (run_id=180)
- Partícula: eta_prime, tier: level1, s2_state: none
- match_score.d_total: 3.753
- Bandas: count=5.0, s2_band_fraction=0.0
- band_energies_gev: [1.3333333333333333, 1.9047619047619049, 2.0, 2.0952380952380953, 2.1904761904761902]
- F_m (base): 1.333 GeV
- M_eff (base≈F_m): 1.333
- M_corrected (F_m*(1-H_block)): 1.330 (H_block=0.003)
- sm_mass_gev: 0.958
- Δ_mass vs SM: +39.2108%
- H_block (lock_quality): 0.003
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.6855762626578235, T_ticks=200
- mean_H_lock_norm=0.002698275664525395, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0014 / 0.0006 / 0.0085

### quark_ud_const_block_0005 (run_id=2)
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

### quark_ud_const_block_0006 (run_id=253)
- Partícula: quark_ud_const, tier: none, s2_state: none
- match_score.d_total: 0.481
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [0.37810945273631835, 0.4875621890547263, 2.0, 2.0099502487562186, 2.0199004975124373]
- F_m (base): 0.378 GeV
- M_eff (base≈F_m): 0.378
- M_corrected (F_m*(1-H_block)): 0.146 (H_block=0.614)
- sm_mass_gev: 0.336
- Δ_mass vs SM: +12.5326%
- H_block (lock_quality): 0.614
- band_power_capture: 0.8275107572002547
- chaos_mode=dynamic, PE_tick_norm=0.8665662353701378, T_ticks=200
- mean_H_lock_norm=0.006096679756631346, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.9709505944546688
- fraction_structured=0.6
- lock_S1_series (mean/min/max): 0.9854 / 0.9622 / 0.9982

### delta_1232_block_0080 (run_id=210)
- Partícula: delta_1232, tier: level1, s2_state: none
- match_score.d_total: 3.867
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.597014925373134, 1.6119402985074625, 2.0]
- F_m (base): 1.597 GeV
- M_eff (base≈F_m): 1.597
- M_corrected (F_m*(1-H_block)): 1.585 (H_block=0.007)
- sm_mass_gev: 1.232
- Δ_mass vs SM: +29.6278%
- H_block (lock_quality): 0.007
- band_power_capture: 0.9364194983182048
- chaos_mode=dynamic, PE_tick_norm=0.6513916947755737, T_ticks=200
- mean_H_lock_norm=0.007033472160805926, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0068 / 0.0008 / 0.0163
