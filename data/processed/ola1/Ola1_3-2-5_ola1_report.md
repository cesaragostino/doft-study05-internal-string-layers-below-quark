# Informe Ola1 – Ola1_3-2-5

## Semáforo de salud
- Runs totales: 18
- Runs aceptados: 18 (100.0%)
- Alertas: ninguna

## Entropía / Caos (nuevo)
- Fuente de datos: partial_runs
- Runs con entropy_chaos: 18
- chaos_mode: dynamic=18, ensemble=0
- PE_tick_norm (mean/med/min/max): 0.686 / 0.684 / 0.466 / 0.893
- T_ticks (mean/med/min/max): 201.0 / 201.0 / 201 / 201
- mean_H_lock_norm (mean/med): 0.004 / 0.003
- mixture_entropy_blocks_norm (mean/med): 0.000 / -0.000
- structure_mix_norm (mean/med): 0.000 / 0.000
- fraction_structured (mean/med): 0.000 / 0.000

## Energía interna (E_internal)
- Runs con E_internal: 18 / 18
- E_internal runs (mean/med/min/max): 0.00086681 / 5.26846e-05 / 7.47904e-11 / 0.0110075
- Bloques con internal_energy: 18 / 18
- internal_energy bloques (mean/med/min/max): 0.00086681 / 5.26846e-05 / 7.47904e-11 / 0.0110075
- mass_sim_gev bloques (mean/med/min/max): 2.51678 / 2.36698 / 1.81815 / 3.71135

## Proxies de masa/lock (unidades internas)
| run | particle | family | omega_ref | M_spec | M1 | M2 | M3 |
|-----|----------|--------|-----------|--------|----|----|----|
| 0 | meson_d_star_zero | charmed_meson | 1.232e+01 | 1.232e+01 | 1.100e+01 | 1.356e+02 | 7.224e+01 |
| 1 | meson_d_star_zero | charmed_meson | 6.904e+00 | 6.904e+00 | 1.101e+01 | 7.603e+01 | 2.990e+01 |
| 3 | meson_d_star_zero | charmed_meson | 1.015e+01 | 1.015e+01 | 1.201e+01 | 1.219e+02 | 4.920e+01 |
| 4 | meson_d_star_zero | charmed_meson | 1.143e+01 | 1.143e+01 | 1.200e+01 | 1.372e+02 | 6.616e+01 |
| 5 | meson_d_star_zero | charmed_meson | 9.820e+00 | 9.820e+00 | 1.100e+01 | 1.081e+02 | 4.192e+01 |
| 6 | meson_d_star_zero | charmed_meson | 9.813e+00 | 9.813e+00 | 1.800e+01 | 1.767e+02 | 5.622e+01 |
| 7 | meson_d_star_zero | charmed_meson | 6.642e+00 | 6.642e+00 | 2.300e+01 | 1.528e+02 | 4.303e+01 |
| 8 | meson_d_star_zero | charmed_meson | 6.532e+00 | 6.532e+00 | 1.100e+01 | 7.186e+01 | 9.508e+00 |
| 11 | meson_d_star_zero | charmed_meson | 8.864e+00 | 8.864e+00 | 1.500e+01 | 1.330e+02 | 5.079e+01 |
| 12 | meson_d_star_zero | charmed_meson | 6.991e+00 | 6.991e+00 | 2.802e+01 | 1.959e+02 | 2.657e+01 |
| 14 | meson_d_star_zero | charmed_meson | 9.253e+00 | 9.253e+00 | 1.702e+01 | 1.575e+02 | 8.314e+01 |
| 15 | meson_d_star_zero | charmed_meson | 7.159e+00 | 7.159e+00 | 1.401e+01 | 1.003e+02 | 3.056e+01 |
| 16 | meson_d_star_zero | charmed_meson | 9.656e+00 | 9.656e+00 | 1.100e+01 | 1.063e+02 | 3.935e+01 |
| 17 | meson_d_star_zero | charmed_meson | 6.348e+00 | 6.348e+00 | 2.301e+01 | 1.461e+02 | 2.949e+01 |
| 2 | meson_ds | charmed_meson | 6.154e+00 | 6.154e+00 | 1.200e+01 | 7.387e+01 | 7.860e+00 |
| 9 | meson_ds | charmed_meson | 6.281e+00 | 6.281e+00 | 2.301e+01 | 1.445e+02 | 2.250e+01 |
| 10 | meson_ds | charmed_meson | 1.256e+01 | 1.256e+01 | 1.700e+01 | 2.136e+02 | 4.035e+01 |
| 13 | meson_ds | charmed_meson | 6.445e+00 | 6.445e+00 | 2.500e+01 | 1.612e+02 | 5.035e+01 |

## Energía calibrada por bloque
- No se pudo construir la tabla (falta internal_energy, mass_gev o sm_mass_gev).

## Error de mass_sim_used vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| meson_d_star_zero | +28.1772% | -6.5396% | +81.4365% | 14 |
| meson_ds | +17.9862% | -7.6305% | +88.5513% | 4 |

## Masa por frecuencia (mass_sim_used_gev)
| run | particle | family | omega_ref_raw | omega_ref_used | mass_sim_used_gev | rel_err_vs_SM | guard |
|-----|----------|--------|--------------|----------------|------------------|---------------|-------|
| 0 | meson_d_star_zero | charmed_meson | 12.324 | 12.324 | 3.64116 | +0.8144 | no |
| 1 | meson_d_star_zero | charmed_meson | 6.90368 | 6.90368 | 2.03972 | +0.0164 | no |
| 3 | meson_d_star_zero | charmed_meson | 10.1511 | 10.1511 | 2.99918 | +0.4945 | no |
| 4 | meson_d_star_zero | charmed_meson | 11.4315 | 11.4315 | 3.37747 | +0.6830 | no |
| 5 | meson_d_star_zero | charmed_meson | 9.8201 | 9.8201 | 2.90139 | +0.4457 | no |
| 6 | meson_d_star_zero | charmed_meson | 9.81299 | 9.81299 | 2.89929 | +0.4447 | no |
| 7 | meson_d_star_zero | charmed_meson | 6.64221 | 6.64221 | 1.96247 | -0.0221 | no |
| 8 | meson_d_star_zero | charmed_meson | 6.53184 | 6.53184 | 1.92986 | -0.0384 | no |
| 11 | meson_d_star_zero | charmed_meson | 8.86384 | 8.86384 | 2.61885 | +0.3050 | no |
| 12 | meson_d_star_zero | charmed_meson | 6.9907 | 6.9907 | 2.06543 | +0.0292 | no |
| 14 | meson_d_star_zero | charmed_meson | 9.25347 | 9.25347 | 2.73397 | +0.3623 | no |
| 15 | meson_d_star_zero | charmed_meson | 7.15886 | 7.15886 | 2.11511 | +0.0539 | no |
| 16 | meson_d_star_zero | charmed_meson | 9.65644 | 9.65644 | 2.85303 | +0.4216 | no |
| 17 | meson_d_star_zero | charmed_meson | 6.34823 | 6.34823 | 1.87561 | -0.0654 | no |
| 2 | meson_ds | charmed_meson | 6.15377 | 6.15377 | 1.81815 | -0.0763 | no |
| 9 | meson_ds | charmed_meson | 6.28106 | 6.28106 | 1.85576 | -0.0572 | no |
| 10 | meson_ds | charmed_meson | 12.5615 | 12.5615 | 3.71135 | +0.8855 | no |
| 13 | meson_ds | charmed_meson | 6.44519 | 6.44519 | 1.90426 | -0.0326 | no |

* = harmonic-guard aplicado

## Harmonic Structure vs SM Quantum Numbers (v1 proxy)
Proceed with v1 using only the stored main FFT peak (plus km1/kp1 if frequency is available) and band_energies anchor. Evidence is score-based (not power-based).
dominant_k, dominant_parity, sector_confidence_v1 computed from k-matching scores (k_tol=0.07, k in 1..5). odd/even evidence fractions are sums of scores.

### By family
| family | count | odd_frac_mean | even_frac_mean | odd_dominant_frac |
|--------|-------|---------------|----------------|-------------------|
| charmed_meson | 18 | 0.874 | 0.126 | 0.889 |

### By J^PC
| jpc | count | odd_frac_mean | even_frac_mean | odd_dominant_frac |
|-----|-------|---------------|----------------|-------------------|
| 0- | 4 | 1.000 | 0.000 | 1.000 |
| 1- | 14 | 0.839 | 0.161 | 0.857 |

### Top 10 particles by odd evidence
| particle | odd_evidence_frac | even_evidence_frac |
|----------|-------------------|--------------------|
| meson_ds | 1.000 | 0.000 |
| meson_d_star_zero | 0.839 | 0.161 |

### Top 10 particles by even evidence
| particle | odd_evidence_frac | even_evidence_frac |
|----------|-------------------|--------------------|
| meson_d_star_zero | 0.839 | 0.161 |
| meson_ds | 1.000 | 0.000 |

## Promedio cósmico (Ola1)
- cosmic_chaos_temp (PE avg): 0.6864
- cosmic_disorder (H_mean avg): 0.0044

## Caos/desorden por run
| Run ID | PE_tick_norm | mean_H_lock_norm |
|--------|--------------|------------------|
| 0 | 0.4655 | 0.0032 |
| 1 | 0.6017 | 0.0126 |
| 2 | 0.8933 | 0.0028 |
| 3 | 0.5931 | 0.0083 |
| 4 | 0.5163 | 0.0032 |
| 5 | 0.6103 | 0.0045 |
| 6 | 0.6812 | 0.0019 |
| 7 | 0.7181 | 0.0010 |
| 8 | 0.8675 | 0.0014 |
| 9 | 0.8435 | 0.0057 |
| 10 | 0.8107 | 0.0019 |
| 11 | 0.6178 | 0.0007 |
| 12 | 0.8633 | 0.0075 |
| 13 | 0.6870 | 0.0018 |
| 14 | 0.4657 | 0.0120 |
| 15 | 0.6938 | 0.0047 |
| 16 | 0.6285 | 0.0031 |
| 17 | 0.7975 | 0.0029 |

## Inventario (cosecha)
| Partícula | Cantidad | Mejor d_total | Promedio d_total |
|-----------|----------|---------------|------------------|
| meson_d_star_zero | 14 | 0.298 | 0.442 |
| meson_ds | 4 | 0.447 | 0.571 |

## Detalle por partícula (d_total y conteos)
| Partícula | Count | d_min | d_med | d_max | Tiers | S2 states |
|-----------|-------|-------|-------|-------|-------|-----------|
| meson_d_star_zero | 14 | 0.298 | 0.415 | 0.573 | level1:14 | latent:2, none:12 |
| meson_ds | 4 | 0.447 | 0.604 | 0.630 | level1:4 | none:4 |

## Radar del Zoo (d_total < 5.0) no aceptados
Sin candidatos cercanos fuera de la selección.

## Harmonic Policy Rejects (tagger)
Sin rechazos por política armónica.

## Pareto de rechazos (causas en selección)
No hay registros de rechazo (o no se encontró el log).

## Bloques aceptados con métricas de entropía/caos
### meson_ds_block_0001 (run_id=9)
- Partícula: meson_ds, tier: level1, s2_state: none
- match_score.d_total: 0.447
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9813953488372098, 1.990697674418605, 2.0, 2.0093023255813955, 2.018604651162791, 2.0279069767441866, 2.0372093023255817, 2.046511627906977, 2.7441860465116283, 2.7534883720930234, 2.7627906976744194, 2.7720930232558145, 2.7813953488372096, 2.790697674418605, 2.8000000000000003, 2.8093023255813954, 2.8186046511627914, 2.8279069767441865, 2.8372093023255816, 2.8465116279069775, 2.8558139534883726, 2.865116279069768, 2.8744186046511633]
- F_m (base): 1.981 GeV
- M_eff (base≈F_m): 1.981
- M_corrected (F_m*(1-H_block)): 1.970 (H_block=0.006)
- sm_mass_gev: 1.968
- mass_sim_raw_gev: 1.85576
- omega_ref_raw: 6.28106
- first_energy: 1.9814
- harmonic_ratio: 0.937
- err_raw_vs_sm: 0.057
- err_fix_vs_sm: 0.007
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: -5.7199%
- H_block (lock_quality): 0.006
- band_power_capture: 0.14160160168823227
- chaos_mode=dynamic, PE_tick_norm=0.843478555034114, T_ticks=201
- mean_H_lock_norm=0.005673895645962608, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0012 / 0.0000 / 0.0031

### meson_d_star_zero_block_0001 (run_id=12)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.298
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9980601357904946, 1.9990300678952473, 1.9999999999999998, 2.0009699321047525, 2.0019398642095054, 2.002909796314258, 2.0038797284190104, 2.004849660523763, 2.005819592628516, 2.0067895247332688, 2.0077594568380213, 2.0087293889427738, 2.0096993210475267, 2.074684772065955, 2.0756547041707076, 2.0766246362754606, 2.077594568380213, 2.078564500484966, 2.0795344325897185, 2.0805043646944714, 2.0814742967992244, 2.082444228903977, 2.0834141610087293, 2.084384093113482, 2.0853540252182348, 2.0863239573229873, 2.0872938894277397, 2.0882638215324927]
- F_m (base): 1.998 GeV
- M_eff (base≈F_m): 1.998
- M_corrected (F_m*(1-H_block)): 1.983 (H_block=0.008)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.06543
- omega_ref_raw: 6.9907
- first_energy: 1.99806
- harmonic_ratio: 1.034
- err_raw_vs_sm: 0.029
- err_fix_vs_sm: 0.004
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +2.9190%
- H_block (lock_quality): 0.008
- band_power_capture: 0.14245067689810562
- chaos_mode=dynamic, PE_tick_norm=0.8633172870474974, T_ticks=201
- mean_H_lock_norm=0.007505366094030249, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0015 / 0.0003 / 0.0031

### meson_d_star_zero_block_0002 (run_id=16)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.495
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.992156862745098, 1.9960784313725493, 2.0, 2.003921568627451, 2.0078431372549024, 2.011764705882353, 2.0156862745098043, 2.019607843137255, 2.0235294117647062, 2.027450980392157, 2.0313725490196077]
- F_m (base): 1.992 GeV
- M_eff (base≈F_m): 1.992
- M_corrected (F_m*(1-H_block)): 1.986 (H_block=0.003)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.85303
- omega_ref_raw: 9.65644
- first_energy: 1.99216
- harmonic_ratio: 1.432
- err_raw_vs_sm: 0.422
- err_fix_vs_sm: 0.007
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +42.1647%
- H_block (lock_quality): 0.003
- band_power_capture: 0.16744446121769366
- chaos_mode=dynamic, PE_tick_norm=0.6285185052551079, T_ticks=201
- mean_H_lock_norm=0.0031138035296883384, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0016 / 0.0005 / 0.0036

### meson_d_star_zero_block_0003 (run_id=1)
- Partícula: meson_d_star_zero, tier: level1, s2_state: latent
- match_score.d_total: 0.385
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9954389965792474, 1.9977194982896243, 2.0, 2.002280501710376, 2.0045610034207524, 2.0068415051311295, 2.0091220068415057, 2.0114025085518814, 2.013683010262258, 2.0159635119726342, 2.0182440136830104]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.970 (H_block=0.013)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.03972
- omega_ref_raw: 6.90368
- first_energy: 1.99544
- harmonic_ratio: 1.022
- err_raw_vs_sm: 0.016
- err_fix_vs_sm: 0.006
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +1.6378%
- H_block (lock_quality): 0.013
- band_power_capture: 0.1683220935751636
- chaos_mode=dynamic, PE_tick_norm=0.6017195977935832, T_ticks=201
- mean_H_lock_norm=0.012613196227817923, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0009 / 0.0006 / 0.0011

### meson_d_star_zero_block_0004 (run_id=6)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.563
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9901234567901234, 1.9950617283950614, 2.0, 2.0049382716049386, 2.0098765432098764, 2.0148148148148146, 2.019753086419753, 2.0246913580246915, 2.0296296296296297, 2.034567901234568, 2.039506172839506, 2.0444444444444443, 2.0493827160493825, 2.0543209876543207, 2.0592592592592593, 2.0641975308641975, 2.0691358024691358, 2.074074074074074]
- F_m (base): 1.990 GeV
- M_eff (base≈F_m): 1.990
- M_corrected (F_m*(1-H_block)): 1.986 (H_block=0.002)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.89929
- omega_ref_raw: 9.81299
- first_energy: 1.99012
- harmonic_ratio: 1.457
- err_raw_vs_sm: 0.445
- err_fix_vs_sm: 0.008
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +44.4695%
- H_block (lock_quality): 0.002
- band_power_capture: 0.15088810495145621
- chaos_mode=dynamic, PE_tick_norm=0.6811822862387781, T_ticks=201
- mean_H_lock_norm=0.0018928565944374277, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0022 / 0.0003 / 0.0052

### meson_d_star_zero_block_0005 (run_id=11)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.514
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.991578947368421, 1.9957894736842108, 2.0, 2.004210526315789, 2.0168421052631578, 2.0210526315789474, 2.025263157894737, 2.0294736842105263, 2.033684210526316, 2.0378947368421056, 2.042105263157895, 2.046315789473684, 2.0505263157894733, 2.0547368421052634, 2.0589473684210526]
- F_m (base): 1.992 GeV
- M_eff (base≈F_m): 1.992
- M_corrected (F_m*(1-H_block)): 1.990 (H_block=0.001)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.61885
- omega_ref_raw: 8.86384
- first_energy: 1.99158
- harmonic_ratio: 1.315
- err_raw_vs_sm: 0.305
- err_fix_vs_sm: 0.008
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +30.4958%
- H_block (lock_quality): 0.001
- band_power_capture: 0.1605462067865705
- chaos_mode=dynamic, PE_tick_norm=0.6177777102636764, T_ticks=201
- mean_H_lock_norm=0.0007107685954658795, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0007 / 0.0001 / 0.0016

### meson_ds_block_0002 (run_id=2)
- Partícula: meson_ds, tier: level1, s2_state: none
- match_score.d_total: 0.604
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9861111111111112, 1.9930555555555556, 1.9999999999999998, 2.006944444444444, 2.013888888888889, 2.020833333333333, 2.0277777777777777, 3.333333333333333, 3.3402777777777777, 3.347222222222222, 3.3541666666666665, 3.3611111111111107]
- F_m (base): 1.986 GeV
- M_eff (base≈F_m): 1.986
- M_corrected (F_m*(1-H_block)): 1.981 (H_block=0.003)
- sm_mass_gev: 1.968
- mass_sim_raw_gev: 1.81815
- omega_ref_raw: 6.15377
- first_energy: 1.98611
- harmonic_ratio: 0.915
- err_raw_vs_sm: 0.076
- err_fix_vs_sm: 0.009
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: -7.6305%
- H_block (lock_quality): 0.003
- band_power_capture: 0.20428979189290092
- chaos_mode=dynamic, PE_tick_norm=0.8933003893794171, T_ticks=201
- mean_H_lock_norm=0.002766425889241407, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.9907 / 0.9660 / 0.9977

### meson_d_star_zero_block_0006 (run_id=17)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.573
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9898218829516543, 1.994910941475827, 2.0, 2.005089058524173, 2.0101781170483464, 2.015267175572519, 2.0203562340966923, 2.0254452926208653, 2.030534351145038, 2.035623409669211, 2.0407124681933846, 2.9720101781170483, 2.9770992366412217, 2.9821882951653946, 2.9872773536895676, 2.9923664122137406, 2.9974554707379135, 3.002544529262087, 3.00763358778626, 3.012722646310433, 3.017811704834606, 3.0229007633587788, 3.027989821882952]
- F_m (base): 1.990 GeV
- M_eff (base≈F_m): 1.990
- M_corrected (F_m*(1-H_block)): 1.984 (H_block=0.003)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 1.87561
- omega_ref_raw: 6.34823
- first_energy: 1.98982
- harmonic_ratio: 0.943
- err_raw_vs_sm: 0.065
- err_fix_vs_sm: 0.008
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: -6.5396%
- H_block (lock_quality): 0.003
- band_power_capture: 0.16236906575443363
- chaos_mode=dynamic, PE_tick_norm=0.7974805272696648, T_ticks=201
- mean_H_lock_norm=0.0029454429407879484, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0031 / 0.0002 / 0.0072

### meson_d_star_zero_block_0007 (run_id=7)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.520
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9913978494623659, 1.9956989247311827, 2.0, 2.004301075268817, 2.0086021505376346, 2.0129032258064514, 2.0172043010752687, 2.021505376344086, 2.0258064516129033, 2.03010752688172, 2.034408602150538, 2.0387096774193547, 2.0774193548387094, 2.081720430107527, 2.086021505376344, 2.0903225806451613, 2.094623655913978, 2.098924731182796, 2.1032258064516127, 2.10752688172043, 2.1118279569892473, 2.1161290322580646, 2.1204301075268814]
- F_m (base): 1.991 GeV
- M_eff (base≈F_m): 1.991
- M_corrected (F_m*(1-H_block)): 1.989 (H_block=0.001)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 1.96247
- omega_ref_raw: 6.64221
- first_energy: 1.9914
- harmonic_ratio: 0.985
- err_raw_vs_sm: 0.022
- err_fix_vs_sm: 0.008
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: -2.2116%
- H_block (lock_quality): 0.001
- band_power_capture: 0.16672777833047478
- chaos_mode=dynamic, PE_tick_norm=0.7180793315600255, T_ticks=201
- mean_H_lock_norm=0.0010178606855118105, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.4830 / 0.0727 / 0.9014

### meson_d_star_zero_block_0008 (run_id=8)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.399
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9950372208436724, 1.9975186104218363, 2.0, 2.002481389578164, 2.004962779156328, 2.0074441687344917, 2.009925558312655, 2.012406947890819, 2.014888337468983, 2.0173697270471465, 2.0198511166253104]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.992 (H_block=0.001)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 1.92986
- omega_ref_raw: 6.53184
- first_energy: 1.99504
- harmonic_ratio: 0.967
- err_raw_vs_sm: 0.038
- err_fix_vs_sm: 0.006
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: -3.8365%
- H_block (lock_quality): 0.001
- band_power_capture: 0.16723455529927272
- chaos_mode=dynamic, PE_tick_norm=0.8675016565408591, T_ticks=201
- mean_H_lock_norm=0.0014079620816907948, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0019 / 0.0001 / 0.0054

### meson_d_star_zero_block_0009 (run_id=14)
- Partícula: meson_d_star_zero, tier: level1, s2_state: latent
- match_score.d_total: 0.317
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9974968710888612, 1.9987484355444303, 2.0, 2.0012515644555697, 2.002503128911139, 2.0037546933667083, 2.0050062578222776, 2.0062578222778473, 2.007509386733417, 2.0087609511889863, 2.0100125156445556, 2.011264080100125, 2.0125156445556946, 2.013767209011264, 2.0150187734668337, 2.0162703379224034, 2.0175219023779722]
- F_m (base): 1.997 GeV
- M_eff (base≈F_m): 1.997
- M_corrected (F_m*(1-H_block)): 1.973 (H_block=0.012)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.73397
- omega_ref_raw: 9.25347
- first_energy: 1.9975
- harmonic_ratio: 1.369
- err_raw_vs_sm: 0.362
- err_fix_vs_sm: 0.005
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +36.2321%
- H_block (lock_quality): 0.012
- band_power_capture: 0.1021468231068432
- chaos_mode=dynamic, PE_tick_norm=0.46565145758292276, T_ticks=201
- mean_H_lock_norm=0.011999274348205784, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0035 / 0.0009 / 0.0089

### meson_ds_block_0003 (run_id=10)
- Partícula: meson_ds, tier: level1, s2_state: none
- match_score.d_total: 0.604
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9861111111111112, 1.9930555555555556, 2.0, 2.0069444444444446, 2.013888888888889, 4.020833333333333, 4.027777777777778, 4.034722222222222, 4.041666666666667, 4.048611111111111, 4.055555555555555, 4.0625, 4.069444444444444, 4.076388888888889, 4.083333333333334, 4.090277777777779, 4.097222222222222]
- F_m (base): 1.986 GeV
- M_eff (base≈F_m): 1.986
- M_corrected (F_m*(1-H_block)): 1.982 (H_block=0.002)
- sm_mass_gev: 1.968
- mass_sim_raw_gev: 3.71135
- omega_ref_raw: 12.5615
- first_energy: 1.98611
- harmonic_ratio: 1.869
- err_raw_vs_sm: 0.886
- err_fix_vs_sm: 0.009
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +88.5513%
- H_block (lock_quality): 0.002
- band_power_capture: 0.16667252732331841
- chaos_mode=dynamic, PE_tick_norm=0.8107174387034924, T_ticks=201
- mean_H_lock_norm=0.0019097880444193444, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0036 / 0.0005 / 0.0091

### meson_d_star_zero_block_0010 (run_id=5)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.409
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.994729907773386, 1.997364953886693, 2.0, 2.0026350461133067, 2.005270092226614, 2.007905138339921, 2.010540184453228, 2.013175230566535, 2.015810276679842, 2.018445322793149, 2.021080368906456]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.986 (H_block=0.004)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.90139
- omega_ref_raw: 9.8201
- first_energy: 1.99473
- harmonic_ratio: 1.455
- err_raw_vs_sm: 0.446
- err_fix_vs_sm: 0.006
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +44.5742%
- H_block (lock_quality): 0.004
- band_power_capture: 0.16516101139845044
- chaos_mode=dynamic, PE_tick_norm=0.6103003305028971, T_ticks=201
- mean_H_lock_norm=0.004493286341759505, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0036 / 0.0011 / 0.0070

### meson_d_star_zero_block_0011 (run_id=0)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.399
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9950248756218902, 1.9975124378109448, 2.0, 2.0024875621890548, 2.004975124378109, 2.007462686567164, 2.0099502487562186, 2.0124378109452734, 2.014925373134328, 2.017412935323383, 2.0199004975124377]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.989 (H_block=0.003)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 3.64116
- omega_ref_raw: 12.324
- first_energy: 1.99502
- harmonic_ratio: 1.825
- err_raw_vs_sm: 0.814
- err_fix_vs_sm: 0.006
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +81.4365%
- H_block (lock_quality): 0.003
- band_power_capture: 0.16760328959879653
- chaos_mode=dynamic, PE_tick_norm=0.4655412777286469, T_ticks=201
- mean_H_lock_norm=0.0031920479875085493, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0079 / 0.0005 / 0.0213

### meson_ds_block_0004 (run_id=13)
- Partícula: meson_ds, tier: level1, s2_state: none
- match_score.d_total: 0.630
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9868852459016393, 1.9934426229508198, 2.0, 2.0065573770491802, 2.013114754098361, 2.019672131147541, 2.026229508196722, 2.0327868852459017, 2.039344262295082, 2.0459016393442626, 2.734426229508197, 2.740983606557377, 2.747540983606558, 2.754098360655738, 2.760655737704918, 2.7672131147540986, 2.773770491803279, 2.780327868852459, 2.7868852459016393, 2.79344262295082, 2.8000000000000003, 2.8065573770491805, 2.813114754098361, 2.8196721311475414, 2.8262295081967213]
- F_m (base): 1.987 GeV
- M_eff (base≈F_m): 1.987
- M_corrected (F_m*(1-H_block)): 1.983 (H_block=0.002)
- sm_mass_gev: 1.968
- mass_sim_raw_gev: 1.90426
- omega_ref_raw: 6.44519
- first_energy: 1.98689
- harmonic_ratio: 0.958
- err_raw_vs_sm: 0.033
- err_fix_vs_sm: 0.009
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: -3.2562%
- H_block (lock_quality): 0.002
- band_power_capture: 0.15415457705212188
- chaos_mode=dynamic, PE_tick_norm=0.6870098867025489, T_ticks=201
- mean_H_lock_norm=0.0018019725015719077, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0016 / 0.0001 / 0.0042

### meson_d_star_zero_block_0012 (run_id=4)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.548
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9905660377358492, 1.9952830188679247, 2.0, 2.0047169811320757, 2.0094339622641515, 2.014150943396227, 2.0188679245283025, 2.023584905660378, 2.028301886792453, 2.0330188679245285, 2.037735849056604, 2.0424528301886795]
- F_m (base): 1.991 GeV
- M_eff (base≈F_m): 1.991
- M_corrected (F_m*(1-H_block)): 1.984 (H_block=0.003)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 3.37747
- omega_ref_raw: 11.4315
- first_energy: 1.99057
- harmonic_ratio: 1.697
- err_raw_vs_sm: 0.683
- err_fix_vs_sm: 0.008
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +68.2971%
- H_block (lock_quality): 0.003
- band_power_capture: 0.16302040693834596
- chaos_mode=dynamic, PE_tick_norm=0.516348136180885, T_ticks=201
- mean_H_lock_norm=0.0031717388704359784, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0020 / 0.0007 / 0.0048

### meson_d_star_zero_block_0013 (run_id=15)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.421
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9943741209563994, 1.9971870604782, 2.0, 2.002812939521801, 2.005625879043601, 2.008438818565401, 2.0112517580872016, 2.0140646976090015, 2.016877637130802, 2.0196905766526023, 2.0225035161744027, 2.0253164556962027, 2.028129395218003, 2.0309423347398035]
- F_m (base): 1.994 GeV
- M_eff (base≈F_m): 1.994
- M_corrected (F_m*(1-H_block)): 1.985 (H_block=0.005)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.11511
- omega_ref_raw: 7.15886
- first_energy: 1.99437
- harmonic_ratio: 1.061
- err_raw_vs_sm: 0.054
- err_fix_vs_sm: 0.006
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +5.3947%
- H_block (lock_quality): 0.005
- band_power_capture: 0.14531081188308628
- chaos_mode=dynamic, PE_tick_norm=0.6937950213463957, T_ticks=201
- mean_H_lock_norm=0.004682519288743721, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0008 / 0.0001 / 0.0017

### meson_d_star_zero_block_0014 (run_id=3)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.354
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9963898916967506, 1.9981949458483754, 2.0, 2.0018050541516246, 2.003610108303249, 2.0054151624548737, 2.007220216606498, 2.0090252707581224, 2.0108303249097474, 2.0126353790613716, 2.0144404332129966, 2.0162454873646207]
- F_m (base): 1.996 GeV
- M_eff (base≈F_m): 1.996
- M_corrected (F_m*(1-H_block)): 1.980 (H_block=0.008)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.99918
- omega_ref_raw: 10.1511
- first_energy: 1.99639
- harmonic_ratio: 1.502
- err_raw_vs_sm: 0.494
- err_fix_vs_sm: 0.005
- omega_ref_guard_applied: false
- Δ_mass_sim vs SM: +49.4470%
- H_block (lock_quality): 0.008
- band_power_capture: 0.16303090732763015
- chaos_mode=dynamic, PE_tick_norm=0.5930597289965321, T_ticks=201
- mean_H_lock_norm=0.008347151006301881, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0079 / 0.0007 / 0.0211

- M2 (omega_ref*V_lock*D_stat): 144.543
- M3 (omega_ref*V_lock*rho_lock): 22.4957
- M2 (omega_ref*V_lock*D_stat): 195.879
- M3 (omega_ref*V_lock*rho_lock): 26.5723
- M2 (omega_ref*V_lock*D_stat): 106.253
- M3 (omega_ref*V_lock*rho_lock): 39.3481
- M2 (omega_ref*V_lock*D_stat): 76.0289
- M3 (omega_ref*V_lock*rho_lock): 29.8989
- M2 (omega_ref*V_lock*D_stat): 176.667
- M3 (omega_ref*V_lock*rho_lock): 56.2178
- M2 (omega_ref*V_lock*D_stat): 132.967
- M3 (omega_ref*V_lock*rho_lock): 50.7868
- M2 (omega_ref*V_lock*D_stat): 73.8653
- M3 (omega_ref*V_lock*rho_lock): 7.8596
- M2 (omega_ref*V_lock*D_stat): 146.052
- M3 (omega_ref*V_lock*rho_lock): 29.4912
- M2 (omega_ref*V_lock*D_stat): 152.786
- M3 (omega_ref*V_lock*rho_lock): 43.0297
- M2 (omega_ref*V_lock*D_stat): 71.8601
- M3 (omega_ref*V_lock*rho_lock): 9.50794
- M2 (omega_ref*V_lock*D_stat): 157.484
- M3 (omega_ref*V_lock*rho_lock): 83.1418
- M2 (omega_ref*V_lock*D_stat): 213.586
- M3 (omega_ref*V_lock*rho_lock): 40.3509
- M2 (omega_ref*V_lock*D_stat): 108.068
- M3 (omega_ref*V_lock*rho_lock): 41.9248
- M2 (omega_ref*V_lock*D_stat): 135.605
- M3 (omega_ref*V_lock*rho_lock): 72.2442
- M2 (omega_ref*V_lock*D_stat): 161.158
- M3 (omega_ref*V_lock*rho_lock): 50.35
- M2 (omega_ref*V_lock*D_stat): 137.22
- M3 (omega_ref*V_lock*rho_lock): 66.1561
- M2 (omega_ref*V_lock*D_stat): 100.27
- M3 (omega_ref*V_lock*rho_lock): 30.5594
- M2 (omega_ref*V_lock*D_stat): 121.909
- M3 (omega_ref*V_lock*rho_lock): 49.1956