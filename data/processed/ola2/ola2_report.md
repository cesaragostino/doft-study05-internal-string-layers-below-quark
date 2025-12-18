# Ola2 – Reporte de Entropía / Caos / Masa
## Cómo se calcula la masa

Energía de enlace aplicada en el engine Ola2:
- $E_{bind} = \gamma \cdot (\sum M_{iniciales}) \cdot R_{final} \cdot Q_{lock}$
- $M_{final} = \sum M_{iniciales} - E_{bind}$
Nota: $\gamma$ es el acople configurado en Ola2 (p.ej. 0.007); $Q_{lock}$ es la calidad de lock media.

## Termómetro cósmico (Ola1 → Ola2)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola2 (éxitos) | Δ (Ola2 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.698 | 0.842 | +0.144 |
| Entropía (H_lock) | 0.0054 | 0.0070 | +0.0017 |
| Dynamic Strain (1-R_final) | n/a | 0.0017 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| alpha_synthesis_pure | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| deuteron_synthesis_strict | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| open_cluster_scan | 10000 | 9959 | 99.6% | 0 | 41 | 0 |
| oxygen16_from_deuterons_fc6 | 10000 | 45 | 0.5% | 0 | 0 | 9955 |
| oxygen16_from_deuterons_fc8 | 10000 | 12 | 0.1% | 0 | 0 | 9988 |
| oxygen16_from_deuterons_ring8 | 10000 | 8 | 0.1% | 0 | 1 | 9991 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| alpha_synthesis_pure | nan | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan | nan |
| open_cluster_scan | 3.511 | 3.487 | 0.0240 | 0.0068 |
| oxygen16_from_deuterons_fc6 | 6.000 | 5.958 | 0.0419 | 0.0070 |
| oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0558 | 0.0070 |
| oxygen16_from_deuterons_ring8 | 8.000 | 7.944 | 0.0557 | 0.0070 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| oxygen16_from_deuterons_fc8_run_8874 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0559 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_0872 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0559 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_7622 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0559 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_ring8_run_6176 | oxygen16_from_deuterons_ring8 | 8.000 | 7.944 | 0.0559 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_9336 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0559 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_5941 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0559 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_ring8_run_5166 | oxygen16_from_deuterons_ring8 | 8.000 | 7.944 | 0.0558 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_0767 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0558 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_4105 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0558 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_1936 | oxygen16_from_deuterons_fc8 | 8.000 | 7.944 | 0.0558 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| alpha_synthesis_pure | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan |
| open_cluster_scan | 0.8056 | 0.0017 | 2.184 |
| oxygen16_from_deuterons_fc6 | 0.9012 | 0.0023 | 5.000 |
| oxygen16_from_deuterons_fc8 | 0.9364 | 0.0023 | 7.000 |
| oxygen16_from_deuterons_ring8 | 0.9050 | 0.0051 | 2.000 |

## Compuestos aceptados (detalle)
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
| 82 | 6.000 | 5.958 | 0.0419 | 0.999 | 0.999 | 0.833 | 0.0064 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 286 | 6.000 | 5.958 | 0.0419 | 0.997 | 0.999 | 0.795 | 0.0062 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 401 | 6.000 | 5.958 | 0.0419 | 0.999 | 0.999 | 0.835 | 0.0067 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 670 | 6.000 | 5.958 | 0.0419 | 0.999 | 0.999 | 0.820 | 0.0048 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 1079 | 6.000 | 5.958 | 0.0419 | 0.998 | 0.999 | 0.799 | 0.0071 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 1156 | 6.000 | 5.958 | 0.0419 | 0.998 | 0.999 | 0.841 | 0.0063 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 1397 | 6.000 | 5.958 | 0.0416 | 0.993 | 0.999 | 0.795 | 0.0085 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 1465 | 6.000 | 5.958 | 0.0417 | 0.995 | 0.999 | 0.784 | 0.0062 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 1955 | 6.000 | 5.958 | 0.0418 | 0.996 | 0.999 | 0.833 | 0.0063 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2027 | 6.000 | 5.958 | 0.0419 | 0.998 | 0.999 | 0.827 | 0.0044 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2616 | 6.000 | 5.958 | 0.0419 | 0.997 | 0.999 | 0.803 | 0.0054 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2958 | 6.000 | 5.958 | 0.0419 | 0.999 | 0.999 | 0.830 | 0.0047 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3096 | 6.000 | 5.958 | 0.0419 | 0.999 | 0.999 | 0.824 | 0.0072 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3277 | 6.000 | 5.958 | 0.0418 | 0.996 | 0.999 | 0.861 | 0.0060 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3569 | 6.000 | 5.958 | 0.0418 | 0.997 | 0.999 | 0.825 | 0.0057 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4201 | 6.000 | 5.958 | 0.0419 | 0.997 | 0.999 | 0.846 | 0.0051 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4428 | 6.000 | 5.958 | 0.0418 | 0.996 | 0.999 | 0.793 | 0.0068 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4739 | 6.000 | 5.958 | 0.0419 | 1.000 | 0.999 | 0.807 | 0.0085 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4864 | 6.000 | 5.958 | 0.0419 | 0.998 | 0.999 | 0.791 | 0.0042 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4923 | 6.000 | 5.958 | 0.0419 | 0.999 | 1.000 | 0.835 | 0.0032 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
_(25 más…)_

### oxygen16_from_deuterons_fc8
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 767 | 8.000 | 7.944 | 0.0558 | 0.998 | 0.999 | 0.817 | 0.0049 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 872 | 8.000 | 7.944 | 0.0559 | 0.999 | 0.999 | 0.770 | 0.0062 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 1936 | 8.000 | 7.944 | 0.0558 | 0.998 | 0.999 | 0.783 | 0.0075 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3738 | 8.000 | 7.944 | 0.0557 | 0.996 | 0.999 | 0.854 | 0.0063 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3781 | 8.000 | 7.944 | 0.0558 | 0.997 | 0.999 | 0.833 | 0.0071 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4105 | 8.000 | 7.944 | 0.0558 | 0.997 | 0.999 | 0.833 | 0.0056 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 5941 | 8.000 | 7.944 | 0.0559 | 0.999 | 0.999 | 0.804 | 0.0070 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 7622 | 8.000 | 7.944 | 0.0559 | 0.999 | 0.999 | 0.798 | 0.0049 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 7819 | 8.000 | 7.944 | 0.0557 | 0.996 | 0.999 | 0.852 | 0.0065 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 8874 | 8.000 | 7.944 | 0.0559 | 0.999 | 0.999 | 0.803 | 0.0053 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 9336 | 8.000 | 7.944 | 0.0559 | 0.999 | 0.999 | 0.813 | 0.0067 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 9450 | 8.000 | 7.944 | 0.0557 | 0.996 | 0.999 | 0.781 | 0.0062 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |

### oxygen16_from_deuterons_ring8
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 2903 | 8.000 | 7.944 | 0.0558 | 0.997 | 0.999 | 0.730 | 0.0070 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2925 | 8.000 | 7.944 | 0.0557 | 0.995 | 0.999 | 0.827 | 0.0067 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4058 | 8.000 | 7.944 | 0.0555 | 0.992 | 0.999 | 0.827 | 0.0067 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4170 | 8.000 | 7.944 | 0.0557 | 0.996 | 0.999 | 0.811 | 0.0059 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4390 | 8.000 | 7.945 | 0.0554 | 0.990 | 0.999 | 0.801 | 0.0057 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 5166 | 8.000 | 7.944 | 0.0558 | 0.998 | 0.999 | 0.803 | 0.0058 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 6176 | 8.000 | 7.944 | 0.0559 | 0.999 | 0.999 | 0.796 | 0.0065 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 8952 | 8.000 | 7.944 | 0.0555 | 0.993 | 0.999 | 0.801 | 0.0065 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
