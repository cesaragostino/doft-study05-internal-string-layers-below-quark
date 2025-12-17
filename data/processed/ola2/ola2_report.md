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
| Entropía (H_lock) | nan | 0.0196 | +nan |
| Dynamic Strain (1-R_final) | n/a | 0.0017 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| alpha_synthesis_pure | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| deuteron_synthesis_strict | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| open_cluster_scan | 10000 | 9953 | 99.5% | 0 | 47 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| alpha_synthesis_pure | nan | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan | nan |
| open_cluster_scan | 3.499 | 3.476 | 0.0230 | 0.0066 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| open_cluster_scan_run_9710 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | deuteron, tau, deuteron, tau |
| open_cluster_scan_run_6972 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | delta_1232, deuteron, tau, deuteron |
| open_cluster_scan_run_9307 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | delta_1232, alpha, triton, delta_1232 |
| open_cluster_scan_run_4400 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | delta_1232, tau, helium3, alpha |
| open_cluster_scan_run_9640 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | deuteron, delta_1232, deuteron, deuteron |
| open_cluster_scan_run_1970 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | delta_1232, delta_1232, deuteron, deuteron |
| open_cluster_scan_run_4617 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | deuteron, tau, delta_1232, tau |
| open_cluster_scan_run_4347 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | helium3, tau, tau, tau |
| open_cluster_scan_run_4726 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | deuteron, tau, delta_1232, triton |
| open_cluster_scan_run_4124 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | delta_1232, delta_1232, triton, deuteron |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| alpha_synthesis_pure | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan |
| open_cluster_scan | 0.8072 | 0.0017 | 2.164 |

## Compuestos aceptados (detalle)
### open_cluster_scan
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 4.000 | 3.972 | 0.0278 | 0.995 | 0.999 | 0.819 | 0.0074 | deuteron, tau, delta_1232, delta_1232 |
| 1 | 3.000 | 2.979 | 0.0210 | 1.000 | 1.000 | 0.858 | 0.0026 | helium3, deuteron, triton |
| 2 | 4.000 | 3.972 | 0.0279 | 0.999 | 0.999 | 0.848 | 0.0060 | deuteron, delta_1232, tau, deuteron |
| 3 | 3.000 | 2.979 | 0.0210 | 0.999 | 0.999 | 0.875 | 0.0061 | tau, delta_1232, tau |
| 4 | 4.000 | 3.972 | 0.0280 | 1.000 | 1.000 | 0.825 | 0.0041 | tau, deuteron, helium3, delta_1232 |
| 5 | 3.000 | 2.979 | 0.0210 | 1.000 | 1.000 | 0.847 | 0.0032 | triton, helium3, delta_1232 |
| 6 | 3.000 | 2.979 | 0.0210 | 0.998 | 1.000 | 0.835 | 0.0040 | deuteron, deuteron, deuteron |
| 7 | 4.000 | 3.972 | 0.0280 | 1.000 | 0.999 | 0.792 | 0.0042 | alpha, deuteron, helium3, deuteron |
| 8 | 4.000 | 3.972 | 0.0280 | 0.999 | 0.999 | 0.849 | 0.0055 | delta_1232, delta_1232, delta_1232, deuteron |
| 9 | 4.000 | 3.972 | 0.0280 | 0.999 | 0.999 | 0.853 | 0.0042 | alpha, tau, helium3, deuteron |
| 10 | 3.000 | 2.979 | 0.0210 | 0.999 | 1.000 | 0.879 | 0.0023 | tau, tau, tau |
| 11 | 4.000 | 3.972 | 0.0280 | 1.000 | 1.000 | 0.882 | 0.0034 | deuteron, deuteron, helium3, delta_1232 |
| 12 | 3.000 | 2.979 | 0.0210 | 0.999 | 1.000 | 0.802 | 0.0031 | tau, delta_1232, alpha |
| 13 | 3.000 | 2.979 | 0.0210 | 0.999 | 0.999 | 0.827 | 0.0051 | deuteron, delta_1232, alpha |
| 14 | 4.000 | 3.972 | 0.0279 | 0.998 | 0.999 | 0.869 | 0.0059 | deuteron, deuteron, tau, deuteron |
| 15 | 4.000 | 3.972 | 0.0280 | 1.000 | 0.999 | 0.831 | 0.0061 | delta_1232, alpha, deuteron, delta_1232 |
| 16 | 3.000 | 2.979 | 0.0210 | 1.000 | 0.999 | 0.864 | 0.0047 | delta_1232, deuteron, deuteron |
| 17 | 4.000 | 3.978 | 0.0220 | 0.999 | 0.788 | 0.826 | 0.1011 | helium3, deuteron, tau, tau |
| 18 | 4.000 | 3.972 | 0.0279 | 0.998 | 1.000 | 0.840 | 0.0031 | delta_1232, deuteron, deuteron, deuteron |
| 19 | 3.000 | 2.979 | 0.0210 | 0.999 | 1.000 | 0.873 | 0.0019 | deuteron, tau, deuteron |
_(9933 más…)_
