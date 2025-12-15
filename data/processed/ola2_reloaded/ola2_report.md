# Ola2 – Reporte de Entropía / Caos / Masa
## Termómetro cósmico (Ola1 → Ola2)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola2 (éxitos) | Δ (Ola2 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.699 | 0.843 | +0.143 |
| Entropía (H_lock) | 0.0053 | 0.0101 | +0.0048 |
| Dynamic Strain (1-R_final) | n/a | 0.0258 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| alpha_synthesis | 10000 | 496 | 5.0% | 0 | 9504 | 0 |
| deuteron_synthesis | 10000 | 3722 | 37.2% | 0 | 6278 | 0 |
| open_cluster_scan | 10000 | 847 | 8.5% | 0 | 9153 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| alpha_synthesis | 7.235 | 7.187 | 0.0479 | 0.0120 |
| deuteron_synthesis | 3.306 | 3.284 | 0.0224 | 0.0112 |
| open_cluster_scan | 5.875 | 5.835 | 0.0393 | 0.0119 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| alpha_synthesis_run_7613 | alpha_synthesis | 7.693 | 7.640 | 0.0537 | 4 | deuteron, deuteron, deuteron, deuteron |
| alpha_synthesis_run_1186 | alpha_synthesis | 7.761 | 7.707 | 0.0536 | 4 | delta_1232, deuteron, deuteron, deuteron |
| alpha_synthesis_run_3730 | alpha_synthesis | 7.654 | 7.601 | 0.0533 | 4 | deuteron, deuteron, deuteron, deuteron |
| alpha_synthesis_run_9737 | alpha_synthesis | 7.647 | 7.594 | 0.0531 | 4 | deuteron, deuteron, deuteron, deuteron |
| open_cluster_scan_run_2204 | open_cluster_scan | 7.658 | 7.605 | 0.0531 | 4 | delta_1232, deuteron, deuteron, deuteron |
| open_cluster_scan_run_8625 | open_cluster_scan | 7.666 | 7.613 | 0.0531 | 4 | deuteron, delta_1232, deuteron, deuteron |
| alpha_synthesis_run_7640 | alpha_synthesis | 7.637 | 7.584 | 0.0530 | 4 | deuteron, deuteron, deuteron, deuteron |
| alpha_synthesis_run_9774 | alpha_synthesis | 7.620 | 7.567 | 0.0530 | 4 | deuteron, deuteron, deuteron, deuteron |
| alpha_synthesis_run_2802 | alpha_synthesis | 7.699 | 7.646 | 0.0530 | 4 | deuteron, deuteron, deuteron, deuteron |
| alpha_synthesis_run_1463 | alpha_synthesis | 7.782 | 7.729 | 0.0529 | 4 | deuteron, delta_1232, delta_1232, deuteron |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| alpha_synthesis | 0.8600 | 0.0428 | 3.000 |
| deuteron_synthesis | 0.6597 | 0.0207 | 1.000 |
| open_cluster_scan | 0.8273 | 0.0378 | 1.823 |
