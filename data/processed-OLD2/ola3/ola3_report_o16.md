# Ola3 – Reporte de Entropía / Caos / Masa
## Cómo se calcula la masa

Energía de enlace en Ola3 (motor Ola2 reloaded):
- $E_{bind} = \gamma \cdot (\sum M_{iniciales}) \cdot R_{final} \cdot Q_{lock}$
- $M_{final} = \sum M_{iniciales} - E_{bind}$
Nota: $\gamma$ según la config de Ola3; $Q_{lock}$ es la calidad media del lock.

## Termómetro cósmico (Ola1 → Ola3)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola3 (éxitos) | Δ (Ola3 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.700 | 0.833 | +0.133 |
| Entropía (H_lock) | 0.0053 | -0.0000 | -0.0053 |
| Dynamic Strain (1-R_final) | n/a | 0.0163 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| carbon_triple_alpha | 10000 | 9041 | 90.4% | 0 | 959 | 0 |
| oxygen_tetra_alpha | 10000 | 8766 | 87.7% | 0 | 1234 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| carbon_triple_alpha | 11.231 | 11.154 | 0.0773 | 0.0258 |
| oxygen_tetra_alpha | 14.974 | 14.872 | 0.1025 | 0.0256 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| oxygen_tetra_alpha_run_4414 | oxygen_tetra_alpha | 15.283 | 15.177 | 0.1061 | 4 | alpha, alpha, alpha, alpha |
| oxygen_tetra_alpha_run_6199 | oxygen_tetra_alpha | 15.246 | 15.140 | 0.1060 | 4 | alpha, alpha, alpha, alpha |
| oxygen_tetra_alpha_run_7630 | oxygen_tetra_alpha | 15.207 | 15.101 | 0.1060 | 4 | alpha, alpha, alpha, alpha |
| oxygen_tetra_alpha_run_0908 | oxygen_tetra_alpha | 15.161 | 15.055 | 0.1059 | 4 | alpha, alpha, alpha, alpha |
| oxygen_tetra_alpha_run_9098 | oxygen_tetra_alpha | 15.189 | 15.084 | 0.1059 | 4 | alpha, alpha, alpha, alpha |
| oxygen_tetra_alpha_run_6637 | oxygen_tetra_alpha | 15.273 | 15.167 | 0.1059 | 4 | alpha, alpha, alpha, alpha |
| oxygen_tetra_alpha_run_7991 | oxygen_tetra_alpha | 15.262 | 15.156 | 0.1058 | 4 | alpha, alpha, alpha, alpha |
| oxygen_tetra_alpha_run_9967 | oxygen_tetra_alpha | 15.231 | 15.126 | 0.1058 | 4 | alpha, alpha, alpha, alpha |
| oxygen_tetra_alpha_run_0026 | oxygen_tetra_alpha | 15.169 | 15.063 | 0.1057 | 4 | alpha, alpha, alpha, alpha |
| oxygen_tetra_alpha_run_1041 | oxygen_tetra_alpha | 15.322 | 15.216 | 0.1057 | 4 | alpha, alpha, alpha, alpha |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| carbon_triple_alpha | 0.7871 | 0.0136 | 2.000 |
| oxygen_tetra_alpha | 0.8506 | 0.0190 | 3.000 |

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

### oxygen_tetra_alpha
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 15.025 | 14.922 | 0.1033 | 0.985 | 0.997 | 0.815 | -0.0000 | alpha, alpha, alpha, alpha |
| 3 | 14.961 | 14.858 | 0.1030 | 0.987 | 0.997 | 0.838 | -0.0000 | alpha, alpha, alpha, alpha |
| 4 | 14.943 | 14.842 | 0.1008 | 0.964 | 0.999 | 0.803 | -0.0000 | alpha, alpha, alpha, alpha |
| 5 | 14.981 | 14.877 | 0.1032 | 0.986 | 0.998 | 0.817 | -0.0000 | alpha, alpha, alpha, alpha |
| 6 | 14.964 | 14.861 | 0.1035 | 0.990 | 0.997 | 0.847 | -0.0000 | alpha, alpha, alpha, alpha |
| 7 | 14.799 | 14.696 | 0.1027 | 0.992 | 1.000 | 0.817 | -0.0000 | alpha, alpha, alpha, alpha |
| 8 | 14.894 | 14.791 | 0.1028 | 0.990 | 0.996 | 0.840 | -0.0000 | alpha, alpha, alpha, alpha |
| 9 | 15.024 | 14.922 | 0.1027 | 0.979 | 0.997 | 0.797 | -0.0000 | alpha, alpha, alpha, alpha |
| 10 | 15.048 | 14.945 | 0.1026 | 0.976 | 0.998 | 0.802 | -0.0000 | alpha, alpha, alpha, alpha |
| 11 | 14.909 | 14.808 | 0.1009 | 0.970 | 0.997 | 0.833 | -0.0000 | alpha, alpha, alpha, alpha |
| 12 | 14.951 | 14.850 | 0.1009 | 0.967 | 0.996 | 0.830 | -0.0000 | alpha, alpha, alpha, alpha |
| 13 | 14.832 | 14.733 | 0.0991 | 0.957 | 0.997 | 0.866 | -0.0000 | alpha, alpha, alpha, alpha |
| 14 | 14.966 | 14.863 | 0.1030 | 0.989 | 0.994 | 0.811 | -0.0000 | alpha, alpha, alpha, alpha |
| 15 | 14.920 | 14.818 | 0.1021 | 0.979 | 0.999 | 0.826 | -0.0000 | alpha, alpha, alpha, alpha |
| 16 | 15.098 | 14.994 | 0.1037 | 0.992 | 0.989 | 0.855 | -0.0000 | alpha, alpha, alpha, alpha |
| 17 | 14.904 | 14.801 | 0.1030 | 0.996 | 0.991 | 0.870 | -0.0000 | alpha, alpha, alpha, alpha |
| 18 | 14.917 | 14.814 | 0.1028 | 0.987 | 0.998 | 0.796 | -0.0000 | alpha, alpha, alpha, alpha |
| 19 | 15.022 | 14.923 | 0.0988 | 0.942 | 0.998 | 0.822 | -0.0000 | alpha, alpha, alpha, alpha |
| 20 | 14.944 | 14.845 | 0.0986 | 0.949 | 0.994 | 0.817 | -0.0000 | alpha, alpha, alpha, alpha |
| 21 | 15.141 | 15.038 | 0.1026 | 0.972 | 0.997 | 0.813 | -0.0000 | alpha, alpha, alpha, alpha |
_(8746 más…)_
