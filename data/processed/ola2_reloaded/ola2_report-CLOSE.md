# Ola2 – Reporte de Entropía / Caos / Masa
## Termómetro cósmico (Ola1 → Ola2)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola2 (éxitos) | Δ (Ola2 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.699 | 0.828 | +0.129 |
| Entropía (H_lock) | 0.0053 | 0.0047 | -0.0006 |
| Dynamic Strain (1-R_final) | n/a | 0.0358 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| alpha_synthesis_pure | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| deuteron_synthesis_strict | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| open_cluster_scan | 10000 | 782 | 7.8% | 0 | 9218 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| alpha_synthesis_pure | nan | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan | nan |
| open_cluster_scan | 5.896 | 5.856 | 0.0394 | 0.0119 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| open_cluster_scan_run_0200 | open_cluster_scan | 7.822 | 7.768 | 0.0542 | 4 | delta_1232, deuteron, delta_1232, delta_1232 |
| open_cluster_scan_run_4379 | open_cluster_scan | 7.760 | 7.706 | 0.0537 | 4 | delta_1232, deuteron, deuteron, deuteron |
| open_cluster_scan_run_2997 | open_cluster_scan | 7.817 | 7.764 | 0.0535 | 4 | delta_1232, deuteron, deuteron, delta_1232 |
| open_cluster_scan_run_0323 | open_cluster_scan | 7.574 | 7.521 | 0.0529 | 4 | deuteron, deuteron, deuteron, deuteron |
| open_cluster_scan_run_3326 | open_cluster_scan | 7.672 | 7.619 | 0.0528 | 4 | deuteron, deuteron, deuteron, deuteron |
| open_cluster_scan_run_5516 | open_cluster_scan | 7.586 | 7.533 | 0.0528 | 4 | deuteron, deuteron, deuteron, deuteron |
| open_cluster_scan_run_9377 | open_cluster_scan | 7.633 | 7.581 | 0.0527 | 4 | deuteron, deuteron, deuteron, deuteron |
| open_cluster_scan_run_8329 | open_cluster_scan | 7.632 | 7.580 | 0.0526 | 4 | deuteron, deuteron, deuteron, deuteron |
| open_cluster_scan_run_8497 | open_cluster_scan | 7.596 | 7.543 | 0.0526 | 4 | deuteron, deuteron, deuteron, deuteron |
| open_cluster_scan_run_3632 | open_cluster_scan | 7.563 | 7.510 | 0.0526 | 4 | deuteron, deuteron, deuteron, deuteron |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| alpha_synthesis_pure | nan | nan | nan |
| deuteron_synthesis_strict | nan | nan | nan |
| open_cluster_scan | 0.8288 | 0.0358 | 1.847 |
