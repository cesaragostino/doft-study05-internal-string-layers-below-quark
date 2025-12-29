# Informe Ola1 – Ola1_3-2-5

## Semáforo de salud
- Runs totales: 10
- Runs aceptados: 10 (100.0%)
- Alertas: ninguna

## Entropía / Caos (nuevo)
- Fuente de datos: sweep_results
- Runs con entropy_chaos: 10
- chaos_mode: dynamic=10, ensemble=0
- PE_tick_norm (mean/med/min/max): 0.699 / 0.652 / 0.561 / 0.898
- T_ticks (mean/med/min/max): 201.0 / 201.0 / 201 / 201
- mean_H_lock_norm (mean/med): 0.007 / 0.006
- mixture_entropy_blocks_norm (mean/med): 0.000 / -0.000
- structure_mix_norm (mean/med): 0.000 / 0.000
- fraction_structured (mean/med): 0.000 / 0.000

## Energía interna (E_internal)
- Runs con E_internal: 10 / 10
- E_internal runs (mean/med/min/max): 0.00151775 / 9.86014e-05 / 9.73308e-08 / 0.0120762
- Bloques con internal_energy: 10 / 10
- internal_energy bloques (mean/med/min/max): 0.00151775 / 9.86014e-05 / 9.73308e-08 / 0.0120762
- mass_sim_gev bloques (mean/med/min/max): 2.40909 / 2.19369 / 1.99849 / 3.33011

## Error de mass_sim_used vs SM
| Partícula | Δ_mean% | Δ_min% | Δ_max% | n |
|-----------|---------|--------|--------|---|
| lambda_c | -1.1872% | -1.1872% | -1.1872% | 1 |
| meson_d_star_zero | -0.2083% | -0.4167% | +0.0000% | 2 |
| meson_ds1_2460 | +0.0921% | +0.0921% | +0.0921% | 1 |
| meson_ds_star | +0.1997% | -0.3519% | +0.7513% | 2 |
| meson_ds_star_2090_DOF | -2.0182% | -2.0182% | -2.0182% | 1 |

## Proxies de masa/lock (unidades internas)
| run | particle | family | omega_ref | M_spec | M1 | M2 | M3 |
|-----|----------|--------|-----------|--------|----|----|----|
| 4 | lambda_c | charmed_baryon | 6.922e+00 | 6.922e+00 | 1.201e+01 | 8.312e+01 | 3.429e+01 |
| 0 | meson_d_star_zero | charmed_meson | 6.148e+00 | 6.148e+00 | 2.901e+01 | 1.784e+02 | 1.990e+01 |
| 3 | meson_d_star_zero | charmed_meson | 6.123e+00 | 6.123e+00 | 1.901e+01 | 1.164e+02 | 4.821e+01 |
| 8 | meson_ds1_2460 | charmed_meson | 7.542e+00 | 7.542e+00 | 1.100e+01 | 8.299e+01 | 3.626e+01 |
| 6 | meson_ds_star | charmed_meson | 6.448e+00 | 6.448e+00 | 1.101e+01 | 7.099e+01 | 1.559e+01 |
| 7 | meson_ds_star | charmed_meson | 6.519e+00 | 6.519e+00 | 1.900e+01 | 1.239e+02 | 1.263e+01 |
| 9 | meson_ds_star_2090_DOF | charmed_meson | 6.274e+00 | 6.274e+00 | 1.101e+01 | 6.909e+01 | 1.138e+01 |
| 1 | unknown | unknown | 9.606e+00 | 9.606e+00 | 1.601e+01 | 1.538e+02 | 6.602e+01 |
| 2 | unknown | unknown | 1.020e+01 | 1.020e+01 | 1.201e+01 | 1.226e+02 | 3.392e+01 |
| 5 | unknown | unknown | 8.021e+00 | 8.021e+00 | 1.100e+01 | 8.827e+01 | 3.769e+01 |

## Energía calibrada por bloque
- No se pudo construir la tabla (falta internal_energy, mass_gev o sm_mass_gev).

## DNA Catalog (DOF Individuals)
### DOF Grade A (Excellent)
| run_id | dof_grade | dof_family_id | dof_family_friendly | R_S1_Q | R_S2_S1 | dominant_parity | band_count | rho_lock | lock_quality_Q | participation_entropy |
| ------ | --------- | ------------- | ------------------- | ------ | ------- | --------------- | ---------- | -------- | -------------- | --------------------- |
| 1 | A | FCF8D | LOCKED_lowEnt_hiBands_S1Q_bin8_S2S1_bin3 | 8.06998003734204 | 2.4229239895937384 |  | 16 | 0.4272014186023219 | 0.9993918692610073 | 0.005523440728558385 |
| 3 | A | FCF8D | LOCKED_lowEnt_hiBands_S1Q_bin8_S2S1_bin3 | 8.537385536554327 | 4.379811544999278 |  | 19 | 0.4111545650529822 | 0.9990946489639224 | 0.00785564235296725 |
| 4 | A | F667F | LOCKED_lowEnt_midBands_S1Q_bin7_S2S1_bin3 | 5.683793152998649 | 2.519670993680853 |  | 12 | 0.4092455290197302 | 0.9989037908723102 | 0.00873001903656019 |
| 5 | A | FDDA9 | LOCKED_lowEnt_midBands_S1Q_bin8_S2S1_bin3 | 6.23314918428547 | 3.138620286585992 |  | 11 | 0.42518597320016027 | 0.9994784881725536 | 0.004734831727829694 |
| 6 | A | FCB61 | LOCKED_lowEnt_midBands_S1Q_bin1_S2S1_bin3 | 2.219272028926855 | 5.282108509024324 |  | 11 | 0.2176355838565897 | 0.9987944102751173 | 0.009783453408940268 |
| 8 | A | F2447 | LOCKED_lowEnt_midBands_S1Q_bin4_S2S1_bin3 | 3.642509238140948 | 8.54967796989017 |  | 11 | 0.43513872247040125 | 0.9995387644832996 | 0.004319279788733105 |

### DOF Grade B (Acceptable)
| run_id | dof_grade | dof_family_id | dof_family_friendly | R_S1_Q | R_S2_S1 | dominant_parity | band_count | rho_lock | lock_quality_Q | participation_entropy |
| ------ | --------- | ------------- | ------------------- | ------ | ------- | --------------- | ---------- | -------- | -------------- | --------------------- |
| 0 | B | F7BDC | LOCKED_lowEnt_maxBands_S1Q_bin7_S2S1_bin3 | 5.662711178644751 | 5.809106220501207 |  | 29 | 0.11106278245728635 | 0.9994715245262064 | 0.004881478874489564 |
| 2 | B | FD61F | LOCKED_midEnt_midBands_S1Q_bin8_S2S1_bin3 | 8.136334519334525 | 9.768361934584561 |  | 12 | 0.2736870184649259 | 0.998446934209868 | 0.012367017566833099 |
| 7 | B | F844C | LOCKED_lowEnt_hiBands_S1Q_bin6_S2S1_bin3 | 4.6566075611075455 | 4.727636006907037 |  | 19 | 0.10164880582630735 | 0.9997158123866279 | 0.0028007234777223614 |
| 9 | B | F1D18 | LOCKED_midEnt_midBands_S1Q_bin2_S2S1_bin3 | 2.6479506213477944 | 5.622823456736802 |  | 11 | 0.16258668178683924 | 0.9981224139681497 | 0.013971758497137436 |

### DOF Grade C (Noise/Ghosts)
| run_id | dof_grade | dof_family_id | dof_family_friendly | R_S1_Q | R_S2_S1 | dominant_parity | band_count | rho_lock | lock_quality_Q | participation_entropy |
| ------ | --------- | ------------- | ------------------- | ------ | ------- | --------------- | ---------- | -------- | -------------- | --------------------- |

### DNA Pareto (R1/R2 agrupados a 2 decimales)
| R_S1_Q_2dp | R_S2_S1_2dp | n | grade_A | grade_B | grade_C |
|-----------|------------|---|---------|---------|---------|
| 2.22 | 5.28 | 1 | 1 | 0 | 0 |
| 2.65 | 5.62 | 1 | 0 | 1 | 0 |
| 3.64 | 8.55 | 1 | 1 | 0 | 0 |
| 4.66 | 4.73 | 1 | 0 | 1 | 0 |
| 5.66 | 5.81 | 1 | 0 | 1 | 0 |
| 5.68 | 2.52 | 1 | 1 | 0 | 0 |
| 6.23 | 3.14 | 1 | 1 | 0 | 0 |
| 8.07 | 2.42 | 1 | 1 | 0 | 0 |
| 8.14 | 9.77 | 1 | 0 | 1 | 0 |
| 8.54 | 4.38 | 1 | 1 | 0 | 0 |

## Masa por frecuencia (mass_sim_used_gev)
| run | particle | family | omega_ref_raw | omega_ref_used | mass_sim_used_gev | rel_err_vs_SM | guard |
|-----|----------|--------|--------------|----------------|------------------|---------------|-------|
| 4 | lambda_c | charmed_baryon | 6.92157 | 6.92157 | 2.25932 | -0.0119 | no |
| 0 | meson_d_star_zero | charmed_meson | 6.14812 | 6.14812 | 2.00685 | +0.0000 | no |
| 3 | meson_d_star_zero | charmed_meson | 6.1225 | 6.1225 | 1.99849 | -0.0042 | no |
| 8 | meson_ds1_2460 | charmed_meson | 7.54178 | 7.54178 | 2.46176 | +0.0009 | no |
| 6 | meson_ds_star | charmed_meson | 6.4481 | 6.4481 | 2.10477 | -0.0035 | no |
| 7 | meson_ds_star | charmed_meson | 6.51949 | 6.51949 | 2.12807 | +0.0075 | no |
| 9 | meson_ds_star_2090_DOF | charmed_meson | 6.27364 | 6.27364 | 2.04782 | -0.0202 | no |
| 1 | unknown | unknown | 9.60566 | 9.60566 | 3.13545 | n/d | no |
| 2 | unknown | unknown | 10.202 | 10.202 | 3.33011 | n/d | no |
| 5 | unknown | unknown | 8.02115 | 8.02115 | 2.61824 | n/d | no |

* = harmonic-guard aplicado

## Harmonic Structure vs SM Quantum Numbers (v1 proxy)
Proceed with v1 using only the stored main FFT peak (plus km1/kp1 if frequency is available) and band_energies anchor. Evidence is score-based (not power-based).
dominant_k, dominant_parity, sector_confidence_v1 computed from k-matching scores (k_tol=0.07, k in 1..5). odd/even evidence fractions are sums of scores.

### By family
| family | count | odd_frac_mean | even_frac_mean | odd_dominant_frac |
|--------|-------|---------------|----------------|-------------------|
| charmed_baryon | 1 | 1.000 | 0.000 | 1.000 |
| charmed_meson | 6 | 1.000 | 0.000 | 1.000 |
| unknown | 3 | 0.333 | 0.667 | 0.333 |

### By J^PC
| jpc | count | odd_frac_mean | even_frac_mean | odd_dominant_frac |
|-----|-------|---------------|----------------|-------------------|
| 1+ | 1 | 1.000 | 0.000 | 1.000 |
| 1- | 5 | 1.000 | 0.000 | 1.000 |
| 1/2+ | 1 | 1.000 | 0.000 | 1.000 |
| unknown | 3 | 0.333 | 0.667 | 0.333 |

### Top 10 particles by odd evidence
| particle | odd_evidence_frac | even_evidence_frac |
|----------|-------------------|--------------------|
| meson_ds1_2460 | 1.000 | 0.000 |
| lambda_c | 1.000 | 0.000 |
| meson_ds_star_2090_DOF | 1.000 | 0.000 |
| meson_d_star_zero | 1.000 | 0.000 |
| meson_ds_star | 1.000 | 0.000 |
| unknown | 0.333 | 0.667 |

### Top 10 particles by even evidence
| particle | odd_evidence_frac | even_evidence_frac |
|----------|-------------------|--------------------|
| unknown | 0.333 | 0.667 |
| meson_ds1_2460 | 1.000 | 0.000 |
| lambda_c | 1.000 | 0.000 |
| meson_ds_star | 1.000 | 0.000 |
| meson_ds_star_2090_DOF | 1.000 | 0.000 |
| meson_d_star_zero | 1.000 | 0.000 |

## Promedio cósmico (Ola1)
- cosmic_chaos_temp (PE avg): 0.6986
- cosmic_disorder (H_mean avg): 0.0068

## Caos/desorden por run
| Run ID | PE_tick_norm | mean_H_lock_norm |
|--------|--------------|------------------|
| 0 | 0.8880 | 0.0044 |
| 1 | 0.5685 | 0.0050 |
| 2 | 0.7200 | 0.0113 |
| 3 | 0.5830 | 0.0070 |
| 4 | 0.5842 | 0.0079 |
| 5 | 0.5711 | 0.0043 |
| 6 | 0.7784 | 0.0089 |
| 7 | 0.8978 | 0.0025 |
| 8 | 0.5614 | 0.0039 |
| 9 | 0.8332 | 0.0127 |

## Inventario (cosecha)
| Partícula | Cantidad | Mejor d_total | Promedio d_total |
|-----------|----------|---------------|------------------|
| lambda_c | 1 | 1.357 | 1.357 |
| meson_d_star_zero | 2 | 0.000 | 0.147 |
| meson_ds1_2460 | 1 | 0.353 | 0.353 |
| meson_ds_star | 2 | 0.241 | 0.388 |
| meson_ds_star_2090_DOF | 1 | 1.205 | 1.205 |
| unknown | 3 | 0.193 | 0.353 |

## Detalle por partícula (d_total y conteos)
| Partícula | Count | d_min | d_med | d_max | Tiers | S2 states |
|-----------|-------|-------|-------|-------|-------|-----------|
| lambda_c | 1 | 1.357 | 1.357 | 1.357 | level1:1 | latent:1 |
| meson_d_star_zero | 2 | 0.000 | 0.147 | 0.294 | level1:2 | none:2 |
| meson_ds1_2460 | 1 | 0.353 | 0.353 | 0.353 | level1:1 | none:1 |
| meson_ds_star | 2 | 0.241 | 0.388 | 0.536 | level1:2 | latent:1, none:1 |
| meson_ds_star_2090_DOF | 1 | 1.205 | 1.205 | 1.205 | level1:1 | latent:1 |
| unknown | 3 | 0.193 | 0.215 | 0.651 | level1:3 | latent:1, none:2 |

## Radar del Zoo (d_total < 5.0) no aceptados
| Partícula | Cantidad | Mejor d_total |
|-----------|----------|---------------|
| unknown | 57 | 0.000 |

## Harmonic Policy Rejects (tagger)
- run_id=0.0 candidate jpc=0- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=0- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=1- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=1- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=0- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=1- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=1/2- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=3/2- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=5/2- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=0- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=1- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=0- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=0- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=0- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=1- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=1- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=5/2- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=1- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=1/2- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)
- run_id=0.0 candidate jpc=3/2- -> policy even/[1, 2, 4] | run parity=odd, k=1, conf=1.0 -> REJECT (parity_mismatch)

## Pareto de rechazos (causas en selección)
| Razón | Cuenta |
|-------|--------|
| dof_grade_not_a | 4 |
| policy_rejected | 3 |

## Bloques aceptados con métricas de entropía/caos
### meson_ds1_2460_block_0001 (run_id=8)
- Partícula: meson_ds1_2460, tier: level1, s2_state: none
- match_score.d_total: 0.353
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9944827586206897, 1.9972413793103447, 2.0, 2.002758620689655, 2.0055172413793105, 2.0082758620689654, 2.0110344827586206, 2.013793103448276, 2.016551724137931, 2.019310344827586, 2.0220689655172417]
- F_m (base): 1.994 GeV
- M_eff (base≈F_m): 1.994
- M_corrected (F_m*(1-H_block)): 1.987 (H_block=0.004)
- sm_mass_gev: 2.459
- mass_sim_raw_gev: 2.46176
- mass_sim_used_gev: 2.46176
- Δ_mass_sim vs SM: +0.0921%
- H_block (lock_quality): 0.004
- band_power_capture: 0.1683142630548654
- chaos_mode=dynamic, PE_tick_norm=0.5614194305724906, T_ticks=201
- mean_H_lock_norm=0.003931575347196229, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0019 / 0.0004 / 0.0041

### lambda_c_block_0001 (run_id=4)
- Partícula: lambda_c, tier: level1, s2_state: latent
- match_score.d_total: 1.357
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9974126778783956, 1.9987063389391977, 2.0, 2.001293661060802, 2.002587322121604, 2.003880983182406, 2.0051746442432083, 2.00646830530401, 2.0077619663648125, 2.009055627425614, 2.0103492884864167, 2.0116429495472183]
- F_m (base): 1.997 GeV
- M_eff (base≈F_m): 1.997
- M_corrected (F_m*(1-H_block)): 1.982 (H_block=0.008)
- sm_mass_gev: 2.286
- mass_sim_raw_gev: 2.25932
- mass_sim_used_gev: 2.25932
- Δ_mass_sim vs SM: -1.1872%
- H_block (lock_quality): 0.008
- band_power_capture: 0.16040093273058495
- chaos_mode=dynamic, PE_tick_norm=0.5841720533939703, T_ticks=201
- mean_H_lock_norm=0.007946405776206828, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0013 / 0.0005 / 0.0021

### meson_ds_star_2090_DOF_block_0001 (run_id=9)
- Partícula: meson_ds_star_2090_DOF, tier: level1, s2_state: latent
- match_score.d_total: 1.205
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9967948717948718, 1.998397435897436, 1.9999999999999998, 2.001602564102564, 2.0032051282051277, 2.004807692307692, 2.0064102564102564, 2.0080128205128203, 2.0096153846153846, 2.011217948717949, 2.0128205128205128]
- F_m (base): 1.997 GeV
- M_eff (base≈F_m): 1.997
- M_corrected (F_m*(1-H_block)): 1.971 (H_block=0.013)
- sm_mass_gev: 2.090
- mass_sim_raw_gev: 2.04782
- mass_sim_used_gev: 2.04782
- Δ_mass_sim vs SM: -2.0182%
- H_block (lock_quality): 0.013
- band_power_capture: 0.16723133178874688
- chaos_mode=dynamic, PE_tick_norm=0.8331976307161386, T_ticks=201
- mean_H_lock_norm=0.01271764264889772, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0005 / 0.0000 / 0.0035

### meson_d_star_zero_block_0001 (run_id=3)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.294
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.991951710261569, 1.9959758551307845, 1.9999999999999998, 2.004024144869215, 2.0080482897384306, 2.0120724346076457, 2.016096579476861, 2.0201207243460764, 4.3903420523138825, 4.394366197183099, 4.398390342052314, 4.402414486921529, 4.406438631790744, 4.410462776659959, 4.414486921529175, 4.41851106639839, 4.422535211267605, 4.426559356136821, 4.430583501006036]
- F_m (base): 1.992 GeV
- M_eff (base≈F_m): 1.992
- M_corrected (F_m*(1-H_block)): 1.978 (H_block=0.007)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 1.99849
- mass_sim_used_gev: 1.99849
- Δ_mass_sim vs SM: -0.4167%
- H_block (lock_quality): 0.007
- band_power_capture: 0.16870635061416958
- chaos_mode=dynamic, PE_tick_norm=0.5829595183930155, T_ticks=201
- mean_H_lock_norm=0.007013171647375131, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0098 / 0.0007 / 0.0342

### unknown_block_0001 (run_id=2)
- Partícula: unknown, tier: level1, s2_state: latent
- match_score.d_total: 0.193
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9898218829516534, 1.9949109414758268, 2.0, 2.0050890585241725, 2.010178117048346, 2.015267175572519, 2.020356234096692, 2.0254452926208653, 2.0305343511450378, 2.0356234096692107, 2.040712468193384, 2.045801526717557]
- F_m (base): 1.990 GeV
- M_eff (base≈F_m): 1.990
- M_corrected (F_m*(1-H_block)): 1.967 (H_block=0.011)
- H_block (lock_quality): 0.011
- band_power_capture: 0.1632533390045388
- chaos_mode=dynamic, PE_tick_norm=0.720045598473932, T_ticks=201
- mean_H_lock_norm=0.011256930859287842, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0015 / 0.0001 / 0.0033

### unknown_block_0002 (run_id=5)
- Partícula: unknown, tier: level1, s2_state: none
- match_score.d_total: 0.651
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9968076616121309, 1.9984038308060657, 2.0, 2.001596169193935, 2.003192338387869, 2.0047885075818037, 2.0063846767757387, 2.007980845969673, 2.0095770151636074, 2.011173184357542, 2.0127693535514766]
- F_m (base): 1.997 GeV
- M_eff (base≈F_m): 1.997
- M_corrected (F_m*(1-H_block)): 1.988 (H_block=0.004)
- H_block (lock_quality): 0.004
- band_power_capture: 0.16810699964237438
- chaos_mode=dynamic, PE_tick_norm=0.5711252387448268, T_ticks=201
- mean_H_lock_norm=0.0043098295456069965, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0027 / 0.0004 / 0.0062

### unknown_block_0003 (run_id=1)
- Partícula: unknown, tier: level1, s2_state: none
- match_score.d_total: 0.215
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9973839110529759, 1.9986919555264877, 1.9999999999999998, 2.001308044473512, 2.002616088947024, 2.003924133420536, 2.0052321778940483, 2.00654022236756, 2.0078482668410724, 2.0091563113145847, 2.010464355788097, 2.0745585349901896, 2.075866579463702, 2.0771746239372137, 2.078482668410726, 2.079790712884238]
- F_m (base): 1.997 GeV
- M_eff (base≈F_m): 1.997
- M_corrected (F_m*(1-H_block)): 1.987 (H_block=0.005)
- H_block (lock_quality): 0.005
- band_power_capture: 0.1712623610546853
- chaos_mode=dynamic, PE_tick_norm=0.5684723587164301, T_ticks=201
- mean_H_lock_norm=0.005022967638712326, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0094 / 0.0005 / 0.0243

### meson_ds_star_block_0001 (run_id=7)
- Partícula: meson_ds_star, tier: level1, s2_state: none
- match_score.d_total: 0.536
- Bandas: count=2.0, s2_band_fraction=0.0
- band_energies_gev: [1.9954075774971296, 1.997703788748565, 2.0, 2.002296211251435, 2.0045924225028706, 2.0068886337543055, 2.009184845005741, 2.0114810562571757, 2.0137772675086105, 2.016073478760046, 2.018369690011481, 2.020665901262916, 2.700344431687715, 2.7026406429391505, 2.7049368541905854, 2.7072330654420207, 2.709529276693456, 2.711825487944891, 2.7141216991963257]
- F_m (base): 1.995 GeV
- M_eff (base≈F_m): 1.995
- M_corrected (F_m*(1-H_block)): 1.990 (H_block=0.003)
- sm_mass_gev: 2.112
- mass_sim_raw_gev: 2.12807
- mass_sim_used_gev: 2.12807
- Δ_mass_sim vs SM: +0.7513%
- H_block (lock_quality): 0.003
- band_power_capture: 0.16696904410569927
- chaos_mode=dynamic, PE_tick_norm=0.8978398444538839, T_ticks=201
- mean_H_lock_norm=0.002462322243705017, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0079 / 0.0001 / 0.0679

### meson_d_star_zero_block_0002 (run_id=0)
- Partícula: meson_d_star_zero, tier: level1, s2_state: none
- match_score.d_total: 0.000
- Bandas: count=3.0, s2_band_fraction=0.0
- band_energies_gev: [1.9927404718693285, 1.9963702359346642, 2.0, 2.003629764065336, 2.0072595281306715, 2.0108892921960075, 2.014519056261343, 2.0181488203266786, 2.0217785843920146, 2.7441016333938295, 2.747731397459165, 2.7513611615245006, 2.7549909255898366, 2.758620689655172, 2.762250453720508, 2.7658802177858437, 2.7695099818511797, 2.838475499092559, 2.8421052631578947, 2.8457350272232307, 2.8493647912885662, 2.8529945553539022, 2.8566243194192382, 2.8602540834845733, 2.863883847549909, 2.867513611615245, 2.8711433756805804, 2.8747731397459164, 2.8784029038112524]
- F_m (base): 1.993 GeV
- M_eff (base≈F_m): 1.993
- M_corrected (F_m*(1-H_block)): 1.984 (H_block=0.004)
- sm_mass_gev: 2.007
- mass_sim_raw_gev: 2.00685
- mass_sim_used_gev: 2.00685
- Δ_mass_sim vs SM: +0.0000%
- H_block (lock_quality): 0.004
- band_power_capture: 0.1662507818750888
- chaos_mode=dynamic, PE_tick_norm=0.8879520171985489, T_ticks=201
- mean_H_lock_norm=0.004368762937712295, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0013 / 0.0000 / 0.0055

### meson_ds_star_block_0002 (run_id=6)
- Partícula: meson_ds_star, tier: level1, s2_state: latent
- match_score.d_total: 0.241
- Bandas: count=1.0, s2_band_fraction=0.0
- band_energies_gev: [1.9975155279503103, 1.998757763975155, 1.9999999999999998, 2.0012422360248445, 2.0024844720496886, 2.0037267080745336, 2.0049689440993785, 2.006211180124223, 2.007453416149068, 2.0086956521739125, 2.0099378881987575]
- F_m (base): 1.998 GeV
- M_eff (base≈F_m): 1.998
- M_corrected (F_m*(1-H_block)): 1.980 (H_block=0.009)
- sm_mass_gev: 2.112
- mass_sim_raw_gev: 2.10477
- mass_sim_used_gev: 2.10477
- Δ_mass_sim vs SM: -0.3519%
- H_block (lock_quality): 0.009
- band_power_capture: 0.16722765536205134
- chaos_mode=dynamic, PE_tick_norm=0.7784358033081104, T_ticks=201
- mean_H_lock_norm=0.00890528306466911, mixture_entropy_blocks_norm=-0.0, structure_mix_norm=0.0
- fraction_structured=0.0
- lock_S1_series (mean/min/max): 0.0256 / 0.0044 / 0.0644

- M2 (omega_ref*V_lock*D_stat): 82.9912
- M3 (omega_ref*V_lock*rho_lock): 36.2552
- M2 (omega_ref*V_lock*D_stat): 83.1213
- M3 (omega_ref*V_lock*rho_lock): 34.2895
- M2 (omega_ref*V_lock*D_stat): 69.091
- M3 (omega_ref*V_lock*rho_lock): 11.378
- M2 (omega_ref*V_lock*D_stat): 116.407
- M3 (omega_ref*V_lock*rho_lock): 48.2058
- M2 (omega_ref*V_lock*D_stat): 122.552
- M3 (omega_ref*V_lock*rho_lock): 33.9229
- M2 (omega_ref*V_lock*D_stat): 88.2693
- M3 (omega_ref*V_lock*rho_lock): 37.6933
- M2 (omega_ref*V_lock*D_stat): 153.765
- M3 (omega_ref*V_lock*rho_lock): 66.0205
- M2 (omega_ref*V_lock*D_stat): 123.901
- M3 (omega_ref*V_lock*rho_lock): 12.6266
- M2 (omega_ref*V_lock*D_stat): 178.372
- M3 (omega_ref*V_lock*rho_lock): 19.8989
- M2 (omega_ref*V_lock*D_stat): 70.9886
- M3 (omega_ref*V_lock*rho_lock): 15.5885