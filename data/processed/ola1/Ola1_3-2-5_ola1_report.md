# Informe Ola1 – Ola1_3-2-5

## Semáforo de salud
- Runs totales: 20
- Runs aceptados: 20 (100.0%)
- Alertas: ninguna

## Entropía / Caos (nuevo)
- Fuente de datos: sweep_results
- Runs con entropy_chaos: 20
- chaos_mode: dynamic=20, ensemble=0
- PE_tick_norm (mean/med/min/max): 0.709 / 0.699 / 0.508 / 0.864
- T_ticks (mean/med/min/max): 200.0 / 200.0 / 200 / 200
- mean_H_lock_norm (mean/med): 0.005 / 0.003
- mixture_entropy_blocks_norm (mean/med): 0.000 / -0.000
- structure_mix_norm (mean/med): 0.050 / 0.000
- fraction_structured (mean/med): 0.025 / 0.000

## Energía interna (E_internal)
- Runs con E_internal: 20 / 20
- E_internal runs (mean/med/min/max): 0.000232373 / 6.76308e-05 / 3.71695e-06 / 0.00268174
- Bloques con internal_energy: 20 / 20
- internal_energy bloques (mean/med/min/max): 0.000232373 / 6.76308e-05 / 3.71695e-06 / 0.00268174
- mass_gev bloques (mean/med/min/max): 1.69485 / 0.493276 / 0.0271101 / 19.5597

## Error de masa vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| delta_1232 | +36.5645% | +21.7532% | +62.3377% | 4 |
| deuteron | +2.3346% | +1.0198% | +3.8978% | 5 |
| eta_prime | +22.4751% | +0.2318% | +36.5337% | 7 |
| quark_ud_const | -11.3475% | -11.3475% | -11.3475% | 1 |
| tau | +0.6272% | -2.4496% | +2.3256% | 3 |

## Promedio cósmico (Ola1)
- cosmic_chaos_temp (PE avg): 0.7095
- cosmic_disorder (H_mean avg): 0.0046

## Caos/desorden por run
| Run ID | PE_tick_norm | mean_H_lock_norm |
|--------|--------------|------------------|
| 0 | 0.5853 | 0.0029 |
| 1 | 0.6845 | 0.0145 |
| 2 | 0.8454 | 0.0026 |
| 3 | 0.6925 | 0.0087 |
| 4 | 0.7499 | 0.0041 |
| 5 | 0.8257 | 0.0044 |
| 6 | 0.6250 | 0.0015 |
| 7 | 0.7475 | 0.0009 |
| 8 | 0.6915 | 0.0014 |
| 9 | 0.8644 | 0.0051 |
| 10 | 0.6854 | 0.0020 |
| 11 | 0.7050 | 0.0009 |
| 12 | 0.5076 | 0.0069 |
| 13 | 0.7673 | 0.0020 |
| 14 | 0.7803 | 0.0152 |
| 15 | 0.6881 | 0.0066 |
| 16 | 0.7687 | 0.0036 |
| 17 | 0.6326 | 0.0025 |
| 18 | 0.7201 | 0.0021 |
| 19 | 0.6228 | 0.0049 |

## Inventario (cosecha)
| Partícula | Cantidad | Mejor d_total | Promedio d_total |
|-----------|----------|---------------|------------------|
| delta_1232 | 4 | 2.560 | 4.776 |
| deuteron | 5 | 1.914 | 4.380 |
| eta_prime | 7 | 0.020 | 2.150 |
| quark_ud_const | 1 | 0.321 | 0.321 |
| tau | 3 | 3.570 | 4.018 |

## Detalle por partícula (d_total y conteos)
| Partícula | Count | d_min | d_med | d_max | Tiers | S2 states |
|-----------|-------|-------|-------|-------|-------|-----------|
| delta_1232 | 4 | 2.560 | 4.432 | 7.680 | level1:4 | none:4 |
| deuteron | 5 | 1.914 | 3.349 | 7.312 | level1:5 | latent:1, none:4 |
| eta_prime | 7 | 0.020 | 2.773 | 3.497 | level1:7 | latent:1, none:6 |
| quark_ud_const | 1 | 0.321 | 0.321 | 0.321 | none:1 | none:1 |
| tau | 3 | 3.570 | 4.138 | 4.347 | level1:3 | none:3 |

## Radar del Zoo (d_total < 5.0) no aceptados
Sin candidatos cercanos fuera de la selección.

## Pareto de rechazos (causas en selección)
No hay registros de rechazo (o no se encontró el log).

## Bloques aceptados con métricas de entropía/caos
### delta_1232_block_0001 (run_id=12)
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

### eta_prime_block_0001 (run_id=5)
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
- H_block (lock_quality): 0.632
- band_power_capture: 1.0
- chaos_mode=dynamic, PE_tick_norm=0.845416153988296, T_ticks=200
- mean_H_lock_norm=0.0026361000375823467, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=1.0
- fraction_structured=0.5
- lock_S1_series (mean/min/max): 0.9960 / 0.9916 / 0.9987

### delta_1232_block_0002 (run_id=9)
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

### eta_prime_block_0003 (run_id=17)
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

### deuteron_block_0001 (run_id=8)
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

### deuteron_block_0002 (run_id=11)
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

### eta_prime_block_0004 (run_id=0)
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

### tau_block_0002 (run_id=15)
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

### deuteron_block_0003 (run_id=1)
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

### deuteron_block_0004 (run_id=18)
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

### eta_prime_block_0005 (run_id=10)
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

### tau_block_0003 (run_id=7)
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

### deuteron_block_0005 (run_id=6)
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

### delta_1232_block_0004 (run_id=3)
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

### eta_prime_block_0006 (run_id=14)
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

### eta_prime_block_0007 (run_id=4)
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
