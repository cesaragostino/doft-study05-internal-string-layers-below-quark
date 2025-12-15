# Ola3 – Reporte de Entropía / Caos / Masa
## Cómo se calcula la masa

Energía de enlace en Ola3 (motor Ola2 reloaded):
- $E_{bind} = \gamma \cdot (\sum M_{iniciales}) \cdot R_{final} \cdot Q_{lock}$
- $M_{final} = \sum M_{iniciales} - E_{bind}$
Nota: $\gamma$ según la config de Ola3; $Q_{lock}$ es la calidad media del lock.

## Termómetro cósmico (Ola1 → Ola3)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola3 (éxitos) | Δ (Ola3 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.704 | 0.851 | +0.147 |
| Entropía (H_lock) | 0.0053 | -0.0000 | -0.0053 |
| Dynamic Strain (1-R_final) | n/a | 0.0146 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| magnesium_synthesis | 10000 | 9033 | 90.3% | 0 | 967 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| magnesium_synthesis | 22.306 | 22.152 | 0.1534 | 0.0767 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| magnesium_synthesis_run_2086 | magnesium_synthesis | 22.701 | 22.543 | 0.1585 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_5812 | magnesium_synthesis | 22.705 | 22.546 | 0.1581 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_5665 | magnesium_synthesis | 22.629 | 22.471 | 0.1581 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_3342 | magnesium_synthesis | 22.648 | 22.490 | 0.1580 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_5569 | magnesium_synthesis | 22.572 | 22.414 | 0.1579 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_6530 | magnesium_synthesis | 22.629 | 22.471 | 0.1579 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_6162 | magnesium_synthesis | 22.583 | 22.426 | 0.1577 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_9179 | magnesium_synthesis | 22.594 | 22.436 | 0.1577 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_1003 | magnesium_synthesis | 22.575 | 22.417 | 0.1577 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_4018 | magnesium_synthesis | 22.588 | 22.431 | 0.1577 | 2 | carbon12, carbon12 |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| magnesium_synthesis | 0.6341 | 0.0146 | 1.000 |

## Compuestos aceptados (detalle)
### magnesium_synthesis
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 22.296 | 22.141 | 0.1546 | 0.994 | 0.996 | 0.852 | -0.0000 | carbon12, carbon12 |
| 1 | 22.307 | 22.151 | 0.1553 | 1.000 | 0.994 | 0.798 | -0.0000 | carbon12, carbon12 |
| 2 | 22.481 | 22.325 | 0.1561 | 0.994 | 0.998 | 0.811 | -0.0000 | carbon12, carbon12 |
| 3 | 22.270 | 22.116 | 0.1547 | 0.995 | 0.997 | 0.831 | -0.0000 | carbon12, carbon12 |
| 4 | 22.252 | 22.097 | 0.1549 | 0.997 | 0.997 | 0.843 | -0.0000 | carbon12, carbon12 |
| 5 | 22.392 | 22.237 | 0.1547 | 0.989 | 0.997 | 0.862 | -0.0000 | carbon12, carbon12 |
| 6 | 22.327 | 22.173 | 0.1544 | 0.988 | 0.999 | 0.846 | -0.0000 | carbon12, carbon12 |
| 7 | 22.365 | 22.213 | 0.1511 | 0.969 | 0.997 | 0.823 | -0.0000 | carbon12, carbon12 |
| 8 | 22.427 | 22.276 | 0.1509 | 0.964 | 0.997 | 0.817 | -0.0000 | carbon12, carbon12 |
| 9 | 22.206 | 22.053 | 0.1529 | 0.986 | 0.998 | 0.851 | -0.0000 | carbon12, carbon12 |
| 10 | 22.357 | 22.201 | 0.1557 | 0.999 | 0.996 | 0.855 | -0.0000 | carbon12, carbon12 |
| 11 | 22.318 | 22.170 | 0.1471 | 0.945 | 0.997 | 0.812 | -0.0000 | carbon12, carbon12 |
| 12 | 22.474 | 22.325 | 0.1489 | 0.949 | 0.997 | 0.847 | -0.0000 | carbon12, carbon12 |
| 14 | 22.480 | 22.324 | 0.1564 | 0.999 | 0.995 | 0.887 | -0.0000 | carbon12, carbon12 |
| 15 | 22.469 | 22.314 | 0.1548 | 0.990 | 0.994 | 0.859 | -0.0000 | carbon12, carbon12 |
| 16 | 22.475 | 22.319 | 0.1566 | 0.999 | 0.996 | 0.859 | -0.0000 | carbon12, carbon12 |
| 17 | 22.362 | 22.207 | 0.1554 | 0.994 | 0.998 | 0.849 | -0.0000 | carbon12, carbon12 |
| 18 | 22.419 | 22.265 | 0.1544 | 0.989 | 0.995 | 0.835 | -0.0000 | carbon12, carbon12 |
| 19 | 22.286 | 22.131 | 0.1555 | 0.999 | 0.998 | 0.837 | -0.0000 | carbon12, carbon12 |
| 20 | 22.391 | 22.235 | 0.1564 | 1.000 | 0.998 | 0.891 | -0.0000 | carbon12, carbon12 |
_(9013 más…)_
