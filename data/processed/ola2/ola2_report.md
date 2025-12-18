# Ola2 – Reporte de Entropía / Caos / Masa
## Cómo se calcula la masa

Energía de enlace aplicada en el engine Ola2:
- $E_{bind} = \gamma \cdot (\sum M_{iniciales}) \cdot R_{final} \cdot Q_{lock}$
- $M_{final} = \sum M_{iniciales} - E_{bind}$
Nota: $\gamma$ es el acople configurado en Ola2 (p.ej. 0.007); $Q_{lock}$ es la calidad de lock media.

## Termómetro cósmico (Ola1 → Ola2)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola2 (éxitos) | Δ (Ola2 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.701 | 0.842 | +0.141 |
| Entropía (H_lock) | 0.0052 | 0.0070 | +0.0018 |
| Dynamic Strain (1-R_final) | n/a | 0.0017 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| alpha_synthesis_pure | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| boron11_synthesis | 10000 | 236 | 2.4% | 0 | 1 | 9763 |
| carbon12_triple_alpha | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| deuteron_synthesis_strict | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| magnesium24_fusion | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| magnesium24_synthesis | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| open_cluster_scan | 10000 | 9959 | 99.6% | 0 | 41 | 0 |
| oxygen16_from_deuterons_fc6 | 10000 | 23 | 0.2% | 0 | 0 | 9977 |
| oxygen16_from_deuterons_fc8 | 10000 | 7 | 0.1% | 0 | 0 | 9993 |
| oxygen16_from_deuterons_ring8 | 10000 | 5 | 0.1% | 0 | 0 | 9995 |
| oxygen16_tetra_alpha | 10000 | 0 | 0.0% | 0 | 0 | 10000 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| alpha_synthesis_pure | nan | nan | nan | nan |
| boron11_synthesis | 3.000 | 2.981 | 0.0190 | 0.0063 |
| carbon12_triple_alpha | nan | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan | nan |
| magnesium24_fusion | nan | nan | nan | nan |
| magnesium24_synthesis | nan | nan | nan | nan |
| open_cluster_scan | 3.511 | 3.487 | 0.0240 | 0.0068 |
| oxygen16_from_deuterons_fc6 | 6.000 | 5.958 | 0.0419 | 0.0070 |
| oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0558 | 0.0070 |
| oxygen16_from_deuterons_ring8 | 8.000 | 7.944 | 0.0556 | 0.0070 |
| oxygen16_tetra_alpha | nan | nan | nan | nan |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| oxygen16_from_deuterons_fc8_run_6843 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0559 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_ring8_run_2737 | oxygen16_from_deuterons_ring8 | 8.000 | 7.944 | 0.0559 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_1647 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0559 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_2579 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0558 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_8872 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0558 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_8663 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0558 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_1934 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0558 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_ring8_run_2359 | oxygen16_from_deuterons_ring8 | 8.000 | 7.944 | 0.0557 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_5561 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0556 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_ring8_run_8707 | oxygen16_from_deuterons_ring8 | 8.000 | 7.944 | 0.0556 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| alpha_synthesis_pure | nan | nan | nan |
| boron11_synthesis | 0.8091 | 0.0013 | 2.000 |
| carbon12_triple_alpha | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan |
| magnesium24_fusion | nan | nan | nan |
| magnesium24_synthesis | nan | nan | nan |
| open_cluster_scan | 0.8056 | 0.0017 | 2.184 |
| oxygen16_from_deuterons_fc6 | 0.8907 | 0.0021 | 5.000 |
| oxygen16_from_deuterons_fc8 | 0.9478 | 0.0031 | 7.000 |
| oxygen16_from_deuterons_ring8 | 0.9286 | 0.0062 | 2.000 |
| oxygen16_tetra_alpha | nan | nan | nan |

## Compuestos aceptados (detalle)
### boron11_synthesis
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 190 | 3.000 | 2.979 | 0.0210 | 1.000 | 0.999 | 0.833 | 0.0066 | triton, triton, triton |
| 221 | 3.000 | 2.986 | 0.0140 | 0.997 | 0.667 | 0.841 | 0.0056 | triton, triton, triton |
| 253 | 3.000 | 2.986 | 0.0140 | 0.997 | 0.667 | 0.870 | 0.0048 | triton, triton, triton |
| 304 | 3.000 | 2.979 | 0.0210 | 0.999 | 0.999 | 0.873 | 0.0061 | triton, triton, triton |
| 452 | 3.000 | 2.979 | 0.0210 | 0.999 | 1.000 | 0.832 | 0.0035 | triton, triton, triton |
| 453 | 3.000 | 2.979 | 0.0210 | 0.999 | 1.000 | 0.851 | 0.0014 | triton, triton, triton |
| 476 | 3.000 | 2.979 | 0.0210 | 1.000 | 1.000 | 0.853 | 0.0025 | triton, triton, triton |
| 503 | 3.000 | 2.986 | 0.0140 | 0.998 | 0.666 | 0.806 | 0.0065 | triton, triton, triton |
| 584 | 3.000 | 2.979 | 0.0210 | 1.000 | 1.000 | 0.836 | 0.0023 | triton, triton, triton |
| 624 | 3.000 | 2.979 | 0.0209 | 0.996 | 0.999 | 0.838 | 0.0046 | triton, triton, triton |
| 638 | 3.000 | 2.979 | 0.0209 | 0.997 | 0.999 | 0.878 | 0.0042 | triton, triton, triton |
| 659 | 3.000 | 2.979 | 0.0210 | 0.999 | 1.000 | 0.855 | 0.0029 | triton, triton, triton |
| 716 | 3.000 | 2.993 | 0.0070 | 0.999 | 0.334 | 0.834 | 0.0072 | triton, triton, triton |
| 719 | 3.000 | 2.986 | 0.0140 | 0.999 | 0.667 | 0.852 | 0.0050 | triton, triton, triton |
| 774 | 3.000 | 2.986 | 0.0140 | 0.999 | 0.667 | 0.851 | 0.0051 | triton, triton, triton |
| 778 | 3.000 | 2.979 | 0.0210 | 0.999 | 1.000 | 0.867 | 0.0011 | triton, triton, triton |
| 789 | 3.000 | 2.979 | 0.0210 | 1.000 | 0.999 | 0.874 | 0.0050 | triton, triton, triton |
| 809 | 3.000 | 2.979 | 0.0209 | 0.996 | 0.999 | 0.813 | 0.0061 | triton, triton, triton |
| 833 | 3.000 | 2.986 | 0.0140 | 1.000 | 0.667 | 0.843 | 0.0036 | triton, triton, triton |
| 834 | 3.000 | 2.986 | 0.0140 | 0.999 | 0.667 | 0.870 | 0.0045 | triton, triton, triton |
_(216 más…)_

### open_cluster_scan
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 4.000 | 3.972 | 0.0279 | 0.997 | 0.999 | 0.821 | 0.0068 | sigma_1775, sigma_1775, delta_1900, sigma_1775 |
| 1 | 4.000 | 3.972 | 0.0279 | 0.998 | 0.999 | 0.827 | 0.0076 | lambda_c, delta_1900, eta_c, j_psi |
| 2 | 3.000 | 2.979 | 0.0210 | 1.000 | 1.000 | 0.819 | 0.0039 | deuteron, j_psi, sigma_1775 |
| 3 | 4.000 | 3.972 | 0.0280 | 0.999 | 1.000 | 0.843 | 0.0034 | delta_1900, deuteron, meson_ds, meson_d_plus |
| 4 | 3.000 | 2.979 | 0.0210 | 1.000 | 1.000 | 0.867 | 0.0031 | triton, j_psi, lambda_c |
| 5 | 4.000 | 3.972 | 0.0280 | 0.999 | 0.999 | 0.848 | 0.0049 | delta_1900, delta_1900, meson_ds_star, delta_1900 |
| 6 | 3.000 | 2.979 | 0.0210 | 0.998 | 1.000 | 0.878 | 0.0032 | deuteron, meson_ds, meson_d_plus |
| 7 | 4.000 | 3.972 | 0.0279 | 0.997 | 0.999 | 0.829 | 0.0047 | delta_1900, delta_1900, sigma_c, meson_ds |
| 8 | 4.000 | 3.972 | 0.0279 | 0.998 | 1.000 | 0.849 | 0.0035 | delta_1900, triton, sigma_1775, sigma_1775 |
| 9 | 3.000 | 2.979 | 0.0210 | 0.999 | 0.999 | 0.861 | 0.0060 | helium3, delta_1900, delta_1900 |
| 10 | 4.000 | 3.972 | 0.0279 | 0.997 | 0.999 | 0.805 | 0.0057 | meson_d_plus, chi_c0, delta_1900, delta_1900 |
| 11 | 3.000 | 2.979 | 0.0209 | 0.996 | 0.999 | 0.853 | 0.0078 | meson_d_plus, helium3, psi_2s |
| 12 | 4.000 | 3.972 | 0.0280 | 0.999 | 1.000 | 0.849 | 0.0026 | delta_1900, sigma_1775, meson_ds, delta_1900 |
| 13 | 4.000 | 3.972 | 0.0279 | 0.999 | 0.999 | 0.843 | 0.0059 | sigma_1775, helium3, meson_d_plus, meson_d_plus |
| 14 | 4.000 | 3.972 | 0.0279 | 0.999 | 0.999 | 0.830 | 0.0081 | meson_d_star_zero, lambda_c, meson_d_star_zero, delta_1900 |
| 15 | 3.000 | 2.979 | 0.0209 | 0.995 | 0.999 | 0.868 | 0.0068 | lambda_c, deuteron, deuteron |
| 16 | 4.000 | 3.972 | 0.0279 | 0.998 | 0.999 | 0.835 | 0.0042 | helium3, delta_1900, delta_1900, sigma_c |
| 17 | 3.000 | 2.986 | 0.0140 | 0.998 | 0.666 | 0.856 | 0.0018 | delta_1900, omega_baryon, meson_ds_star |
| 18 | 4.000 | 3.972 | 0.0279 | 0.999 | 0.999 | 0.820 | 0.0054 | sigma_1775, chi_c2, helium3, sigma_1775 |
| 19 | 4.000 | 3.972 | 0.0279 | 0.998 | 0.999 | 0.845 | 0.0076 | delta_1900, deuteron, meson_d_plus, meson_d_star_plus |
_(9939 más…)_

### oxygen16_from_deuterons_fc6
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 594 | 6.000 | 5.958 | 0.0419 | 0.997 | 0.999 | 0.781 | 0.0063 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 744 | 6.000 | 5.958 | 0.0419 | 0.999 | 0.999 | 0.838 | 0.0058 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 770 | 6.000 | 5.958 | 0.0419 | 0.998 | 0.999 | 0.857 | 0.0051 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 1902 | 6.000 | 5.958 | 0.0418 | 0.996 | 0.999 | 0.840 | 0.0062 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2153 | 6.000 | 5.958 | 0.0419 | 0.999 | 0.999 | 0.850 | 0.0048 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2212 | 6.000 | 5.958 | 0.0419 | 0.998 | 0.999 | 0.843 | 0.0066 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2748 | 6.000 | 5.958 | 0.0418 | 0.996 | 0.999 | 0.828 | 0.0063 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3129 | 6.000 | 5.958 | 0.0419 | 0.998 | 1.000 | 0.816 | 0.0028 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3384 | 6.000 | 5.958 | 0.0419 | 0.997 | 0.999 | 0.866 | 0.0042 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3728 | 6.000 | 5.958 | 0.0418 | 0.997 | 0.999 | 0.813 | 0.0057 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4584 | 6.000 | 5.958 | 0.0418 | 0.996 | 0.999 | 0.800 | 0.0046 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4988 | 6.000 | 5.958 | 0.0419 | 0.999 | 0.999 | 0.825 | 0.0073 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 5168 | 6.000 | 5.958 | 0.0419 | 0.998 | 0.999 | 0.827 | 0.0043 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 5212 | 6.000 | 5.958 | 0.0418 | 0.996 | 0.999 | 0.808 | 0.0065 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 5988 | 6.000 | 5.958 | 0.0419 | 0.999 | 0.999 | 0.817 | 0.0058 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 6065 | 6.000 | 5.958 | 0.0419 | 0.999 | 0.999 | 0.817 | 0.0073 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 6216 | 6.000 | 5.958 | 0.0419 | 0.998 | 0.999 | 0.843 | 0.0057 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 6457 | 6.000 | 5.958 | 0.0419 | 0.998 | 0.999 | 0.836 | 0.0047 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 7146 | 6.000 | 5.958 | 0.0419 | 0.998 | 0.999 | 0.842 | 0.0043 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 7294 | 6.000 | 5.958 | 0.0419 | 0.999 | 1.000 | 0.816 | 0.0041 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
_(3 más…)_

### oxygen16_from_deuterons_fc8
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 1647 | 8.000 | 7.944 | 0.0559 | 0.998 | 0.999 | 0.792 | 0.0062 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 1934 | 8.000 | 7.944 | 0.0558 | 0.996 | 0.999 | 0.875 | 0.0054 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2579 | 8.000 | 7.944 | 0.0558 | 0.997 | 1.000 | 0.854 | 0.0039 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 5561 | 8.000 | 7.944 | 0.0556 | 0.994 | 0.999 | 0.849 | 0.0052 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 6843 | 8.000 | 7.944 | 0.0559 | 0.999 | 1.000 | 0.791 | 0.0035 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 8663 | 8.000 | 7.944 | 0.0558 | 0.996 | 1.000 | 0.786 | 0.0035 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 8872 | 8.000 | 7.944 | 0.0558 | 0.998 | 0.999 | 0.839 | 0.0066 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |

### oxygen16_from_deuterons_ring8
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 2359 | 8.000 | 7.944 | 0.0557 | 0.995 | 1.000 | 0.844 | 0.0039 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2737 | 8.000 | 7.944 | 0.0559 | 0.998 | 0.999 | 0.841 | 0.0043 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 7721 | 8.000 | 7.945 | 0.0553 | 0.989 | 0.999 | 0.828 | 0.0075 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 8670 | 8.000 | 7.944 | 0.0555 | 0.992 | 0.999 | 0.801 | 0.0053 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 8707 | 8.000 | 7.944 | 0.0556 | 0.994 | 0.999 | 0.770 | 0.0047 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
