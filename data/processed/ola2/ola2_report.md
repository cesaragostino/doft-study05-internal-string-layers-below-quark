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
| Entropía (H_lock) | nan | 0.0809 | +nan |
| Dynamic Strain (1-R_final) | n/a | 0.0017 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| alpha_synthesis_pure | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| deuteron_synthesis_strict | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| open_cluster_scan | 10000 | 9950 | 99.5% | 0 | 50 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| alpha_synthesis_pure | nan | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan | nan |
| open_cluster_scan | 3.501 | 3.478 | 0.0230 | 0.0066 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| open_cluster_scan_run_3380 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | tau, tau, deuteron, tau |
| open_cluster_scan_run_9938 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | eta_prime, deuteron, deuteron, deuteron |
| open_cluster_scan_run_2259 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | eta_prime, eta_prime, deuteron, deuteron |
| open_cluster_scan_run_9950 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | deuteron, eta_prime, eta_prime, deuteron |
| open_cluster_scan_run_9392 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | deuteron, deuteron, eta_prime, deuteron |
| open_cluster_scan_run_6592 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | eta_prime, eta_prime, tau, deuteron |
| open_cluster_scan_run_0519 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | deuteron, tau, tau, deuteron |
| open_cluster_scan_run_4801 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | deuteron, deuteron, deuteron, eta_prime |
| open_cluster_scan_run_7048 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | deuteron, deuteron, eta_prime, tau |
| open_cluster_scan_run_9012 | open_cluster_scan | 4.000 | 3.972 | 0.0280 | 4 | eta_prime, eta_prime, deuteron, eta_prime |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| alpha_synthesis_pure | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan |
| open_cluster_scan | 0.8051 | 0.0017 | 2.169 |

## Compuestos aceptados (detalle)
### open_cluster_scan
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 3.000 | 2.979 | 0.0210 | 0.999 | 0.999 | 0.850 | 0.0046 | eta_prime, delta_1232, eta_prime |
| 1 | 3.000 | 2.979 | 0.0209 | 0.998 | 1.000 | 0.844 | 0.0032 | eta_prime, eta_prime, eta_prime |
| 2 | 4.000 | 3.972 | 0.0279 | 0.999 | 0.999 | 0.827 | 0.0051 | deuteron, tau, deuteron, eta_prime |
| 3 | 3.000 | 2.983 | 0.0175 | 0.998 | 0.833 | 0.881 | 0.2126 | eta_prime, quark_ud_const, eta_prime |
| 4 | 4.000 | 3.972 | 0.0280 | 0.999 | 1.000 | 0.827 | 0.0040 | eta_prime, eta_prime, eta_prime, delta_1232 |
| 5 | 4.000 | 3.976 | 0.0244 | 0.998 | 0.874 | 0.775 | 0.1626 | eta_prime, eta_prime, quark_ud_const, deuteron |
| 6 | 3.000 | 2.979 | 0.0209 | 0.995 | 0.999 | 0.853 | 0.0042 | delta_1232, eta_prime, deuteron |
| 7 | 4.000 | 3.972 | 0.0279 | 0.999 | 0.999 | 0.845 | 0.0082 | eta_prime, tau, eta_prime, deuteron |
| 8 | 3.000 | 2.979 | 0.0210 | 0.999 | 1.000 | 0.884 | 0.0023 | eta_prime, eta_prime, eta_prime |
| 9 | 4.000 | 3.972 | 0.0279 | 0.999 | 0.999 | 0.846 | 0.0067 | eta_prime, eta_prime, eta_prime, deuteron |
| 10 | 4.000 | 3.976 | 0.0244 | 0.997 | 0.875 | 0.835 | 0.1608 | eta_prime, delta_1232, quark_ud_const, eta_prime |
| 11 | 3.000 | 2.983 | 0.0175 | 1.000 | 0.833 | 0.832 | 0.2130 | deuteron, delta_1232, quark_ud_const |
| 12 | 4.000 | 3.972 | 0.0279 | 0.999 | 1.000 | 0.804 | 0.0034 | deuteron, tau, eta_prime, eta_prime |
| 13 | 4.000 | 3.976 | 0.0245 | 0.999 | 0.875 | 0.848 | 0.1602 | eta_prime, quark_ud_const, delta_1232, eta_prime |
| 14 | 3.000 | 2.983 | 0.0174 | 0.997 | 0.833 | 0.840 | 0.2137 | eta_prime, quark_ud_const, tau |
| 15 | 4.000 | 3.972 | 0.0280 | 0.999 | 1.000 | 0.844 | 0.0016 | deuteron, deuteron, eta_prime, deuteron |
| 16 | 4.000 | 3.979 | 0.0210 | 0.998 | 0.750 | 0.859 | 0.3165 | deuteron, eta_prime, quark_ud_const, quark_ud_const |
| 17 | 3.000 | 2.979 | 0.0210 | 1.000 | 1.000 | 0.805 | 0.0037 | delta_1232, eta_prime, tau |
| 18 | 4.000 | 3.972 | 0.0280 | 0.999 | 1.000 | 0.852 | 0.0034 | eta_prime, tau, deuteron, eta_prime |
| 19 | 3.000 | 2.979 | 0.0210 | 1.000 | 1.000 | 0.840 | 0.0027 | deuteron, eta_prime, deuteron |
_(9930 más…)_
