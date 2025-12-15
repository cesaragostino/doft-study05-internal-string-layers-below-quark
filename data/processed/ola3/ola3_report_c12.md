# Ola3 – Reporte de Entropía / Caos / Masa
## Cómo se calcula la masa

Energía de enlace en Ola3 (motor Ola2 reloaded):
- $E_{bind} = \gamma \cdot (\sum M_{iniciales}) \cdot R_{final} \cdot Q_{lock}$
- $M_{final} = \sum M_{iniciales} - E_{bind}$
Nota: $\gamma$ según la config de Ola3; $Q_{lock}$ es la calidad media del lock.

## Termómetro cósmico (Ola1 → Ola3)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola3 (éxitos) | Δ (Ola3 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.700 | 0.838 | +0.138 |
| Entropía (H_lock) | 0.0053 | -0.0000 | -0.0053 |
| Dynamic Strain (1-R_final) | n/a | 0.0136 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| carbon_triple_alpha | 10000 | 9041 | 90.4% | 0 | 959 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| carbon_triple_alpha | 11.231 | 11.154 | 0.0773 | 0.0258 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| carbon_triple_alpha_run_0318 | carbon_triple_alpha | 11.492 | 11.412 | 0.0801 | 3 | alpha, alpha, alpha |
| carbon_triple_alpha_run_0143 | carbon_triple_alpha | 11.453 | 11.373 | 0.0801 | 3 | alpha, alpha, alpha |
| carbon_triple_alpha_run_8740 | carbon_triple_alpha | 11.434 | 11.354 | 0.0798 | 3 | alpha, alpha, alpha |
| carbon_triple_alpha_run_2571 | carbon_triple_alpha | 11.404 | 11.325 | 0.0798 | 3 | alpha, alpha, alpha |
| carbon_triple_alpha_run_0328 | carbon_triple_alpha | 11.430 | 11.351 | 0.0797 | 3 | alpha, alpha, alpha |
| carbon_triple_alpha_run_2666 | carbon_triple_alpha | 11.479 | 11.399 | 0.0797 | 3 | alpha, alpha, alpha |
| carbon_triple_alpha_run_3746 | carbon_triple_alpha | 11.454 | 11.374 | 0.0797 | 3 | alpha, alpha, alpha |
| carbon_triple_alpha_run_0633 | carbon_triple_alpha | 11.434 | 11.354 | 0.0797 | 3 | alpha, alpha, alpha |
| carbon_triple_alpha_run_9769 | carbon_triple_alpha | 11.471 | 11.391 | 0.0797 | 3 | alpha, alpha, alpha |
| carbon_triple_alpha_run_0414 | carbon_triple_alpha | 11.451 | 11.371 | 0.0797 | 3 | alpha, alpha, alpha |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| carbon_triple_alpha | 0.7871 | 0.0136 | 2.000 |

## Compuestos aceptados (detalle)
### carbon_triple_alpha
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 11.224 | 11.146 | 0.0779 | 0.993 | 0.999 | 0.862 | -0.0000 | alpha, alpha, alpha |
| 1 | 11.253 | 11.176 | 0.0775 | 0.994 | 0.990 | 0.852 | -0.0000 | alpha, alpha, alpha |
| 2 | 11.124 | 11.046 | 0.0775 | 1.000 | 0.996 | 0.868 | -0.0000 | alpha, alpha, alpha |
| 3 | 11.385 | 11.306 | 0.0787 | 0.990 | 0.997 | 0.845 | -0.0000 | alpha, alpha, alpha |
| 4 | 11.283 | 11.204 | 0.0782 | 0.994 | 0.996 | 0.834 | -0.0000 | alpha, alpha, alpha |
| 5 | 11.246 | 11.173 | 0.0740 | 0.943 | 0.997 | 0.834 | -0.0000 | alpha, alpha, alpha |
| 6 | 11.236 | 11.158 | 0.0781 | 0.997 | 0.996 | 0.855 | -0.0000 | alpha, alpha, alpha |
| 7 | 11.291 | 11.213 | 0.0781 | 0.990 | 0.998 | 0.787 | -0.0000 | alpha, alpha, alpha |
| 8 | 11.160 | 11.084 | 0.0768 | 0.986 | 0.997 | 0.869 | -0.0000 | alpha, alpha, alpha |
| 9 | 11.220 | 11.142 | 0.0782 | 0.997 | 0.998 | 0.841 | -0.0000 | alpha, alpha, alpha |
| 10 | 11.157 | 11.079 | 0.0778 | 0.997 | 0.999 | 0.843 | -0.0000 | alpha, alpha, alpha |
| 11 | 11.369 | 11.290 | 0.0787 | 0.998 | 0.992 | 0.832 | -0.0000 | alpha, alpha, alpha |
| 12 | 11.364 | 11.285 | 0.0787 | 0.998 | 0.991 | 0.858 | -0.0000 | alpha, alpha, alpha |
| 13 | 11.276 | 11.198 | 0.0780 | 0.992 | 0.996 | 0.843 | -0.0000 | alpha, alpha, alpha |
| 14 | 11.266 | 11.188 | 0.0780 | 0.989 | 1.000 | 0.852 | -0.0000 | alpha, alpha, alpha |
| 15 | 11.203 | 11.125 | 0.0777 | 0.993 | 0.999 | 0.837 | -0.0000 | alpha, alpha, alpha |
| 16 | 11.230 | 11.152 | 0.0783 | 0.999 | 0.996 | 0.837 | -0.0000 | alpha, alpha, alpha |
| 18 | 11.234 | 11.156 | 0.0782 | 0.995 | 0.999 | 0.853 | -0.0000 | alpha, alpha, alpha |
| 19 | 11.212 | 11.134 | 0.0778 | 0.992 | 1.000 | 0.867 | -0.0000 | alpha, alpha, alpha |
| 20 | 11.338 | 11.260 | 0.0774 | 0.979 | 0.996 | 0.837 | -0.0000 | alpha, alpha, alpha |
_(9021 más…)_
