# Ola2 – Reporte de Entropía / Caos / Masa
## Termómetro cósmico (Ola1 → Ola2)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola2 (éxitos) | Δ (Ola2 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.699 | 0.859 | +0.160 |
| Entropía (H_lock) | 0.0053 | 0.0046 | -0.0007 |
| Dynamic Strain (1-R_final) | n/a | 0.0034 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| deuteron_refinery | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| helium_from_deuterons | 10000 | 9884 | 98.8% | 0 | 116 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| deuteron_refinery | nan | nan | nan | nan |
| helium_from_deuterons | 3.770 | 3.744 | 0.0263 | 0.0131 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| helium_from_deuterons_run_0824 | helium_from_deuterons | 3.917 | 3.889 | 0.0274 | 2 | deuteron, deuteron |
| helium_from_deuterons_run_5041 | helium_from_deuterons | 3.917 | 3.889 | 0.0274 | 2 | deuteron, deuteron |
| helium_from_deuterons_run_8742 | helium_from_deuterons | 3.919 | 3.892 | 0.0274 | 2 | deuteron, deuteron |
| helium_from_deuterons_run_1951 | helium_from_deuterons | 3.914 | 3.887 | 0.0274 | 2 | deuteron, deuteron |
| helium_from_deuterons_run_5078 | helium_from_deuterons | 3.914 | 3.887 | 0.0274 | 2 | deuteron, deuteron |
| helium_from_deuterons_run_2785 | helium_from_deuterons | 3.917 | 3.890 | 0.0273 | 2 | deuteron, deuteron |
| helium_from_deuterons_run_1128 | helium_from_deuterons | 3.909 | 3.882 | 0.0273 | 2 | deuteron, deuteron |
| helium_from_deuterons_run_4865 | helium_from_deuterons | 3.912 | 3.885 | 0.0273 | 2 | deuteron, deuteron |
| helium_from_deuterons_run_4783 | helium_from_deuterons | 3.915 | 3.887 | 0.0273 | 2 | deuteron, deuteron |
| helium_from_deuterons_run_5935 | helium_from_deuterons | 3.908 | 3.881 | 0.0273 | 2 | deuteron, deuteron |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| deuteron_refinery | nan | nan | nan |
| helium_from_deuterons | 0.5902 | 0.0034 | 1.000 |
