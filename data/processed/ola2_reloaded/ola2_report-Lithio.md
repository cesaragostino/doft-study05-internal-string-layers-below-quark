# Ola2 – Reporte de Entropía / Caos / Masa
## Cómo se calcula la masa

Energía de enlace aplicada en el engine Ola2:
- $E_{bind} = \gamma \cdot (\sum M_{iniciales}) \cdot R_{final} \cdot Q_{lock}$
- $M_{final} = \sum M_{iniciales} - E_{bind}$
Nota: $\gamma$ es el acople configurado en Ola2 (p.ej. 0.007); $Q_{lock}$ es la calidad de lock media.

## Termómetro cósmico (Ola1 → Ola2)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola2 (éxitos) | Δ (Ola2 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.700 | 0.850 | +0.150 |
| Entropía (H_lock) | 0.0052 | 0.0046 | -0.0007 |
| Dynamic Strain (1-R_final) | n/a | 0.0054 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| deuteron_refinery | 10000 | 0 | 0.0% | 0 | 0 | 10000 |
| helium_from_deuterons | 10000 | 9895 | 99.0% | 0 | 105 | 0 |
| lithium_triad_test | 10000 | 9924 | 99.2% | 0 | 76 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| deuteron_refinery | nan | nan | nan | nan |
| helium_from_deuterons | 3.770 | 3.744 | 0.0263 | 0.0131 |
| lithium_triad_test | 5.655 | 5.616 | 0.0393 | 0.0131 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| lithium_triad_test_run_1189 | lithium_triad_test | 5.832 | 5.791 | 0.0408 | 3 | deuteron, deuteron, deuteron |
| lithium_triad_test_run_0041 | lithium_triad_test | 5.838 | 5.798 | 0.0407 | 3 | deuteron, deuteron, deuteron |
| lithium_triad_test_run_6521 | lithium_triad_test | 5.831 | 5.790 | 0.0407 | 3 | deuteron, deuteron, deuteron |
| lithium_triad_test_run_7749 | lithium_triad_test | 5.840 | 5.800 | 0.0407 | 3 | deuteron, deuteron, deuteron |
| lithium_triad_test_run_3684 | lithium_triad_test | 5.840 | 5.799 | 0.0407 | 3 | deuteron, deuteron, deuteron |
| lithium_triad_test_run_3521 | lithium_triad_test | 5.825 | 5.785 | 0.0407 | 3 | deuteron, deuteron, deuteron |
| lithium_triad_test_run_5154 | lithium_triad_test | 5.826 | 5.786 | 0.0407 | 3 | deuteron, deuteron, deuteron |
| lithium_triad_test_run_2682 | lithium_triad_test | 5.818 | 5.777 | 0.0407 | 3 | deuteron, deuteron, deuteron |
| lithium_triad_test_run_8810 | lithium_triad_test | 5.823 | 5.782 | 0.0407 | 3 | deuteron, deuteron, deuteron |
| lithium_triad_test_run_2800 | lithium_triad_test | 5.824 | 5.784 | 0.0406 | 3 | deuteron, deuteron, deuteron |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| deuteron_refinery | nan | nan | nan |
| helium_from_deuterons | 0.5839 | 0.0033 | 1.000 |
| lithium_triad_test | 0.7813 | 0.0075 | 2.000 |

## Compuestos aceptados (detalle)
### helium_from_deuterons
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 3.811 | 3.784 | 0.0266 | 1.000 | 0.999 | 0.858 | 0.0057 | deuteron, deuteron |
| 1 | 3.753 | 3.726 | 0.0263 | 1.000 | 1.000 | 0.878 | 0.0016 | deuteron, deuteron |
| 2 | 3.839 | 3.812 | 0.0268 | 0.998 | 1.000 | 0.817 | 0.0032 | deuteron, deuteron |
| 4 | 3.735 | 3.709 | 0.0259 | 0.991 | 1.000 | 0.846 | 0.0033 | deuteron, deuteron |
| 5 | 3.784 | 3.757 | 0.0263 | 0.994 | 0.999 | 0.877 | 0.0096 | deuteron, deuteron |
| 6 | 3.854 | 3.827 | 0.0269 | 0.996 | 1.000 | 0.849 | 0.0024 | deuteron, deuteron |
| 7 | 3.831 | 3.804 | 0.0268 | 0.998 | 0.999 | 0.846 | 0.0055 | deuteron, deuteron |
| 8 | 3.826 | 3.799 | 0.0265 | 0.989 | 1.000 | 0.836 | 0.0033 | deuteron, deuteron |
| 9 | 3.719 | 3.693 | 0.0260 | 1.000 | 1.000 | 0.846 | 0.0023 | deuteron, deuteron |
| 10 | 3.758 | 3.731 | 0.0263 | 0.999 | 1.000 | 0.893 | 0.0033 | deuteron, deuteron |
| 11 | 3.790 | 3.763 | 0.0265 | 1.000 | 1.000 | 0.849 | 0.0033 | deuteron, deuteron |
| 12 | 3.817 | 3.790 | 0.0267 | 1.000 | 1.000 | 0.848 | 0.0023 | deuteron, deuteron |
| 13 | 3.838 | 3.811 | 0.0267 | 0.996 | 0.999 | 0.862 | 0.0093 | deuteron, deuteron |
| 14 | 3.733 | 3.707 | 0.0261 | 1.000 | 0.999 | 0.869 | 0.0047 | deuteron, deuteron |
| 15 | 3.709 | 3.683 | 0.0258 | 0.995 | 0.999 | 0.884 | 0.0056 | deuteron, deuteron |
| 16 | 3.690 | 3.665 | 0.0258 | 0.999 | 0.999 | 0.842 | 0.0044 | deuteron, deuteron |
| 17 | 3.752 | 3.726 | 0.0261 | 0.994 | 1.000 | 0.866 | 0.0017 | deuteron, deuteron |
| 18 | 3.787 | 3.760 | 0.0265 | 0.998 | 1.000 | 0.879 | 0.0011 | deuteron, deuteron |
| 19 | 3.778 | 3.751 | 0.0264 | 0.999 | 1.000 | 0.842 | 0.0017 | deuteron, deuteron |
| 20 | 3.789 | 3.763 | 0.0263 | 0.992 | 1.000 | 0.838 | 0.0025 | deuteron, deuteron |
_(9875 más…)_

### lithium_triad_test
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 5.689 | 5.649 | 0.0398 | 0.999 | 0.999 | 0.835 | 0.0072 | deuteron, deuteron, deuteron |
| 1 | 5.648 | 5.609 | 0.0384 | 0.972 | 0.999 | 0.847 | 0.0079 | deuteron, deuteron, deuteron |
| 2 | 5.716 | 5.677 | 0.0396 | 0.989 | 0.999 | 0.869 | 0.0050 | deuteron, deuteron, deuteron |
| 3 | 5.627 | 5.587 | 0.0394 | 1.000 | 1.000 | 0.826 | 0.0036 | deuteron, deuteron, deuteron |
| 4 | 5.704 | 5.665 | 0.0396 | 0.991 | 1.000 | 0.832 | 0.0039 | deuteron, deuteron, deuteron |
| 5 | 5.680 | 5.641 | 0.0392 | 0.987 | 0.999 | 0.819 | 0.0076 | deuteron, deuteron, deuteron |
| 6 | 5.642 | 5.603 | 0.0394 | 0.998 | 0.999 | 0.856 | 0.0076 | deuteron, deuteron, deuteron |
| 7 | 5.621 | 5.582 | 0.0392 | 0.997 | 1.000 | 0.837 | 0.0025 | deuteron, deuteron, deuteron |
| 8 | 5.642 | 5.602 | 0.0395 | 1.000 | 1.000 | 0.849 | 0.0020 | deuteron, deuteron, deuteron |
| 9 | 5.636 | 5.597 | 0.0394 | 0.999 | 0.999 | 0.838 | 0.0071 | deuteron, deuteron, deuteron |
| 10 | 5.647 | 5.608 | 0.0390 | 0.988 | 0.999 | 0.801 | 0.0078 | deuteron, deuteron, deuteron |
| 11 | 5.706 | 5.666 | 0.0397 | 0.994 | 1.000 | 0.874 | 0.0040 | deuteron, deuteron, deuteron |
| 12 | 5.548 | 5.510 | 0.0387 | 0.998 | 1.000 | 0.866 | 0.0032 | deuteron, deuteron, deuteron |
| 13 | 5.599 | 5.560 | 0.0391 | 0.999 | 0.999 | 0.840 | 0.0058 | deuteron, deuteron, deuteron |
| 14 | 5.786 | 5.746 | 0.0401 | 0.992 | 0.999 | 0.871 | 0.0066 | deuteron, deuteron, deuteron |
| 15 | 5.642 | 5.602 | 0.0393 | 0.995 | 1.000 | 0.872 | 0.0021 | deuteron, deuteron, deuteron |
| 16 | 5.660 | 5.621 | 0.0390 | 0.985 | 0.999 | 0.852 | 0.0089 | deuteron, deuteron, deuteron |
| 17 | 5.723 | 5.684 | 0.0396 | 0.990 | 0.999 | 0.789 | 0.0084 | deuteron, deuteron, deuteron |
| 18 | 5.606 | 5.566 | 0.0392 | 0.998 | 1.000 | 0.838 | 0.0041 | deuteron, deuteron, deuteron |
| 19 | 5.675 | 5.635 | 0.0395 | 0.996 | 1.000 | 0.823 | 0.0018 | deuteron, deuteron, deuteron |
_(9904 más…)_
