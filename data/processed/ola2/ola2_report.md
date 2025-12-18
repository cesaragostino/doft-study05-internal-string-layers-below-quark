# Ola2 – Reporte de Entropía / Caos / Masa
## Cómo se calcula la masa

Energía de enlace aplicada en el engine Ola2:
- $E_{bind} = \gamma \cdot (\sum M_{iniciales}) \cdot R_{final} \cdot Q_{lock}$
- $M_{final} = \sum M_{iniciales} - E_{bind}$
Nota: $\gamma$ es el acople configurado en Ola2 (p.ej. 0.007); $Q_{lock}$ es la calidad de lock media.

## Termómetro cósmico (Ola1 → Ola2)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola2 (éxitos) | Δ (Ola2 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | nan | 0.842 | +nan |
| Entropía (H_lock) | nan | 0.0071 | +nan |
| Dynamic Strain (1-R_final) | n/a | 0.0017 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| alpha_synthesis_pure | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| deuteron_synthesis_strict | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| open_cluster_scan | 10000 | 9959 | 99.6% | 0 | 41 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| alpha_synthesis_pure | nan | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan | nan |
| open_cluster_scan | 3.511 | 3.487 | 0.0240 | 0.0068 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| open_cluster_scan_run_7126 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | delta_1900, sigma_1775, lambda_c, helium3 |
| open_cluster_scan_run_7039 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | sigma_1775, sigma_c, triton, meson_ds |
| open_cluster_scan_run_5766 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | delta_1900, meson_ds, triton, triton |
| open_cluster_scan_run_4166 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | sigma_1775, meson_ds, chi_c0, meson_ds_star |
| open_cluster_scan_run_3551 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | sigma_c, psi_2s, meson_d_star_zero, delta_1900 |
| open_cluster_scan_run_9632 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | meson_ds, delta_1900, psi_2s, meson_ds |
| open_cluster_scan_run_5129 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | sigma_c, meson_ds, meson_ds, triton |
| open_cluster_scan_run_8120 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | delta_1900, psi_2s, lambda_c, delta_1900 |
| open_cluster_scan_run_3871 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | sigma_1775, meson_d0, delta_1900, meson_ds |
| open_cluster_scan_run_8267 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | delta_1900, sigma_1775, helium3, meson_ds |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| alpha_synthesis_pure | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan |
| open_cluster_scan | 0.8056 | 0.0017 | 2.184 |

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
