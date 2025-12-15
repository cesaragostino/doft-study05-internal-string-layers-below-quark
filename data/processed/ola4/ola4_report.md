# Ola3 – Reporte de Entropía / Caos / Masa
## Cómo se calcula la masa

Energía de enlace en Ola3 (motor Ola2 reloaded):
- $E_{bind} = \gamma \cdot (\sum M_{iniciales}) \cdot R_{final} \cdot Q_{lock}$
- $M_{final} = \sum M_{iniciales} - E_{bind}$
Nota: $\gamma$ según la config de Ola3; $Q_{lock}$ es la calidad media del lock.

## Termómetro cósmico (Ola1 → Ola3)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola3 (éxitos) | Δ (Ola3 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.702 | 0.853 | +0.151 |
| Entropía (H_lock) | 0.0053 | -0.0000 | -0.0053 |
| Dynamic Strain (1-R_final) | n/a | 0.0129 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| magnesium_synthesis | 10000 | 9009 | 90.1% | 0 | 991 | 0 |
| oxygen_hybrid_synthesis | 10000 | 4571 | 45.7% | 0 | 5429 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| magnesium_synthesis | 22.305 | 22.152 | 0.1534 | 0.0767 |
| oxygen_hybrid_synthesis | 14.071 | 13.974 | 0.0970 | 0.0485 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| magnesium_synthesis_run_8196 | magnesium_synthesis | 22.739 | 22.580 | 0.1589 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_6369 | magnesium_synthesis | 22.682 | 22.523 | 0.1583 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_3448 | magnesium_synthesis | 22.626 | 22.468 | 0.1583 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_3406 | magnesium_synthesis | 22.704 | 22.546 | 0.1581 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_5731 | magnesium_synthesis | 22.601 | 22.443 | 0.1579 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_5852 | magnesium_synthesis | 22.594 | 22.436 | 0.1578 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_2670 | magnesium_synthesis | 22.620 | 22.462 | 0.1578 | 2 | carbon12, carbon12 |
| oxygen_hybrid_synthesis_run_8103 | oxygen_hybrid_synthesis | 22.560 | 22.403 | 0.1578 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_3786 | magnesium_synthesis | 22.625 | 22.467 | 0.1578 | 2 | carbon12, carbon12 |
| magnesium_synthesis_run_5492 | magnesium_synthesis | 22.606 | 22.448 | 0.1578 | 2 | carbon12, carbon12 |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| magnesium_synthesis | 0.6395 | 0.0146 | 1.000 |
| oxygen_hybrid_synthesis | 0.6207 | 0.0096 | 1.000 |

## Compuestos aceptados (detalle)
### magnesium_synthesis
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 1 | 22.525 | 22.368 | 0.1560 | 0.996 | 0.994 | 0.836 | -0.0000 | carbon12, carbon12 |
| 2 | 22.289 | 22.138 | 0.1502 | 0.969 | 0.994 | 0.852 | -0.0000 | carbon12, carbon12 |
| 3 | 22.280 | 22.128 | 0.1517 | 0.974 | 0.999 | 0.840 | -0.0000 | carbon12, carbon12 |
| 4 | 22.346 | 22.191 | 0.1549 | 0.994 | 0.996 | 0.882 | -0.0000 | carbon12, carbon12 |
| 5 | 22.236 | 22.087 | 0.1486 | 0.957 | 0.998 | 0.836 | -0.0000 | carbon12, carbon12 |
| 6 | 22.341 | 22.185 | 0.1552 | 0.995 | 0.998 | 0.869 | -0.0000 | carbon12, carbon12 |
| 7 | 22.438 | 22.290 | 0.1482 | 0.946 | 0.997 | 0.833 | -0.0000 | carbon12, carbon12 |
| 8 | 22.157 | 22.005 | 0.1518 | 0.980 | 0.999 | 0.858 | -0.0000 | carbon12, carbon12 |
| 9 | 22.270 | 22.115 | 0.1556 | 1.000 | 0.998 | 0.821 | -0.0000 | carbon12, carbon12 |
| 10 | 22.230 | 22.077 | 0.1537 | 0.990 | 0.998 | 0.846 | -0.0000 | carbon12, carbon12 |
| 11 | 22.235 | 22.083 | 0.1516 | 0.978 | 0.995 | 0.825 | -0.0000 | carbon12, carbon12 |
| 12 | 22.299 | 22.144 | 0.1547 | 1.000 | 0.991 | 0.836 | -0.0000 | carbon12, carbon12 |
| 13 | 22.336 | 22.180 | 0.1556 | 0.997 | 0.998 | 0.855 | -0.0000 | carbon12, carbon12 |
| 14 | 22.359 | 22.203 | 0.1553 | 0.994 | 0.999 | 0.849 | -0.0000 | carbon12, carbon12 |
| 15 | 22.434 | 22.278 | 0.1563 | 0.999 | 0.997 | 0.871 | -0.0000 | carbon12, carbon12 |
| 16 | 22.299 | 22.144 | 0.1547 | 0.996 | 0.996 | 0.850 | -0.0000 | carbon12, carbon12 |
| 17 | 22.168 | 22.014 | 0.1542 | 0.995 | 0.998 | 0.856 | -0.0000 | carbon12, carbon12 |
| 19 | 22.222 | 22.072 | 0.1502 | 0.969 | 0.997 | 0.858 | -0.0000 | carbon12, carbon12 |
| 20 | 22.237 | 22.087 | 0.1497 | 0.964 | 0.997 | 0.841 | -0.0000 | carbon12, carbon12 |
| 22 | 22.285 | 22.133 | 0.1525 | 0.982 | 0.995 | 0.825 | -0.0000 | carbon12, carbon12 |
_(8989 más…)_

### oxygen_hybrid_synthesis
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 7.359 | 7.308 | 0.0512 | 0.995 | 1.000 | 0.884 | -0.0000 | alpha, alpha |
| 1 | 22.379 | 22.223 | 0.1558 | 1.000 | 0.995 | 0.866 | -0.0000 | carbon12, carbon12 |
| 2 | 7.405 | 7.353 | 0.0518 | 0.999 | 1.000 | 0.854 | -0.0000 | alpha, alpha |
| 3 | 22.319 | 22.167 | 0.1524 | 0.979 | 0.996 | 0.855 | -0.0000 | carbon12, carbon12 |
| 4 | 7.457 | 7.405 | 0.0519 | 0.999 | 0.996 | 0.829 | -0.0000 | alpha, alpha |
| 5 | 7.390 | 7.338 | 0.0516 | 0.999 | 0.999 | 0.873 | -0.0000 | alpha, alpha |
| 7 | 7.504 | 7.452 | 0.0525 | 0.999 | 0.999 | 0.835 | -0.0000 | alpha, alpha |
| 10 | 7.577 | 7.525 | 0.0517 | 0.977 | 0.997 | 0.877 | -0.0000 | alpha, alpha |
| 11 | 22.207 | 22.056 | 0.1513 | 0.978 | 0.996 | 0.808 | -0.0000 | carbon12, carbon12 |
| 13 | 7.466 | 7.414 | 0.0519 | 0.998 | 0.996 | 0.845 | -0.0000 | alpha, alpha |
| 14 | 7.513 | 7.461 | 0.0513 | 0.977 | 0.999 | 0.834 | -0.0000 | alpha, alpha |
| 18 | 22.128 | 21.974 | 0.1539 | 0.994 | 0.999 | 0.845 | -0.0000 | carbon12, carbon12 |
| 20 | 22.365 | 22.209 | 0.1557 | 0.999 | 0.996 | 0.863 | -0.0000 | carbon12, carbon12 |
| 22 | 22.234 | 22.078 | 0.1553 | 1.000 | 0.998 | 0.875 | -0.0000 | carbon12, carbon12 |
| 23 | 7.508 | 7.457 | 0.0507 | 0.978 | 0.986 | 0.847 | -0.0000 | alpha, alpha |
| 24 | 7.505 | 7.452 | 0.0524 | 0.999 | 0.998 | 0.865 | -0.0000 | alpha, alpha |
| 25 | 7.468 | 7.415 | 0.0522 | 0.999 | 1.000 | 0.865 | -0.0000 | alpha, alpha |
| 26 | 22.301 | 22.145 | 0.1551 | 0.997 | 0.996 | 0.837 | -0.0000 | carbon12, carbon12 |
| 27 | 7.565 | 7.514 | 0.0517 | 0.977 | 0.999 | 0.801 | -0.0000 | alpha, alpha |
| 28 | 7.393 | 7.342 | 0.0515 | 1.000 | 0.996 | 0.879 | -0.0000 | alpha, alpha |
_(4551 más…)_
