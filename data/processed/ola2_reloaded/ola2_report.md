# Ola2 – Reporte de Entropía / Caos / Masa
## Termómetro cósmico (Ola1 → Ola2)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola2 (éxitos) | Δ (Ola2 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.699 | 0.843 | +0.144 |
| Entropía (H_lock) | 0.0053 | 0.0113 | +0.0060 |
| Dynamic Strain (1-R_final) | n/a | 0.0249 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| alpha_synthesis | 2000 | 91 | 4.5% | 0 | 1909 | 0 |
| deuteron_synthesis | 2000 | 691 | 34.5% | 0 | 1309 | 0 |
| open_cluster_scan | 2000 | 163 | 8.2% | 0 | 1837 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| alpha_synthesis | 7.220 | 7.172 | 0.0480 | 0.0120 |
| deuteron_synthesis | 3.295 | 3.273 | 0.0223 | 0.0111 |
| open_cluster_scan | 5.796 | 5.757 | 0.0383 | 0.0117 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| alpha_synthesis_run_1424 | alpha_synthesis | 7.655 | 7.601 | 0.0532 | 4 | deuteron, deuteron, deuteron, deuteron |
| alpha_synthesis_run_0986 | alpha_synthesis | 7.650 | 7.598 | 0.0526 | 4 | deuteron, deuteron, deuteron, deuteron |
| open_cluster_scan_run_0569 | open_cluster_scan | 7.675 | 7.623 | 0.0526 | 4 | delta_1232, deuteron, deuteron, deuteron |
| alpha_synthesis_run_1101 | alpha_synthesis | 7.554 | 7.501 | 0.0525 | 4 | deuteron, deuteron, deuteron, deuteron |
| alpha_synthesis_run_0924 | alpha_synthesis | 7.526 | 7.473 | 0.0524 | 4 | deuteron, deuteron, deuteron, deuteron |
| alpha_synthesis_run_0274 | alpha_synthesis | 7.490 | 7.438 | 0.0523 | 4 | deuteron, deuteron, deuteron, deuteron |
| alpha_synthesis_run_1663 | alpha_synthesis | 7.587 | 7.535 | 0.0523 | 4 | deuteron, deuteron, deuteron, deuteron |
| alpha_synthesis_run_1629 | alpha_synthesis | 7.487 | 7.435 | 0.0523 | 4 | deuteron, deuteron, deuteron, deuteron |
| open_cluster_scan_run_0124 | open_cluster_scan | 7.634 | 7.582 | 0.0523 | 4 | deuteron, deuteron, deuteron, delta_1232 |
| alpha_synthesis_run_0092 | alpha_synthesis | 7.488 | 7.435 | 0.0522 | 4 | deuteron, deuteron, deuteron, deuteron |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| alpha_synthesis | 0.8409 | 0.0438 | 3.000 |
| deuteron_synthesis | 0.6446 | 0.0192 | 1.000 |
| open_cluster_scan | 0.8295 | 0.0386 | 1.814 |
