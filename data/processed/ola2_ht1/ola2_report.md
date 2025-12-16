# Ola2 – Reporte de Entropía / Caos / Masa
## Cómo se calcula la masa

Energía de enlace aplicada en el engine Ola2:
- $E_{bind} = \gamma \cdot (\sum M_{iniciales}) \cdot R_{final} \cdot Q_{lock}$
- $M_{final} = \sum M_{iniciales} - E_{bind}$
Nota: $\gamma$ es el acople configurado en Ola2 (p.ej. 0.007); $Q_{lock}$ es la calidad de lock media.

## Termómetro cósmico (Ola1 → Ola2)
| Métrica | Promedio Ola1 (inputs) | Promedio Ola2 (éxitos) | Δ (Ola2 - Ola1) |
|---------|------------------------|------------------------|-----------------|
| Caos dinámico (PE) | 0.702 | 0.807 | +0.106 |
| Entropía (H_lock) | 0.0053 | 0.0047 | -0.0006 |
| Dynamic Strain (1-R_final) | n/a | 0.0216 | n/a |

## Rendimiento del reactor
| Target | Runs | Éxitos | Éxito % | geometry_mismatch | no_lock | otros |
|--------|------|--------|---------|-------------------|---------|-------|
| oxygen16_from_deuterons_fc6 | 10000 | 9987 | 99.9% | 0 | 13 | 0 |
| oxygen16_from_deuterons_fc8 | 10000 | 9995 | 100.0% | 0 | 5 | 0 |
| oxygen16_from_deuterons_ring8 | 10000 | 7399 | 74.0% | 0 | 2601 | 0 |

## Tabla de fusión (defecto de masa)
| Target | ⟨Σm⟩ | ⟨M_final⟩ | ⟨E_b⟩ | ⟨E_b⟩/nodo |
|--------|------|-----------|-------|------------|
| oxygen16_from_deuterons_fc6 | 11.313 | 11.235 | 0.0781 | 0.0130 |
| oxygen16_from_deuterons_fc8 | 15.084 | 14.980 | 0.1039 | 0.0130 |
| oxygen16_from_deuterons_ring8 | 15.079 | 14.978 | 0.1012 | 0.0126 |

### Top binding (mayor E_b)
| Compound | Target | Σm | M_final | E_b | Nodos | Partículas |
|----------|--------|----|---------|-----|-------|------------|
| oxygen16_from_deuterons_fc8_run_9687 | oxygen16_from_deuterons_fc8 | 15.349 | 15.242 | 0.1068 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_5406 | oxygen16_from_deuterons_fc8 | 15.365 | 15.258 | 0.1067 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_7257 | oxygen16_from_deuterons_fc8 | 15.324 | 15.218 | 0.1066 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_9428 | oxygen16_from_deuterons_fc8 | 15.346 | 15.239 | 0.1066 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_ring8_run_1015 | oxygen16_from_deuterons_ring8 | 15.348 | 15.241 | 0.1066 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_0022 | oxygen16_from_deuterons_fc8 | 15.403 | 15.297 | 0.1066 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_5959 | oxygen16_from_deuterons_fc8 | 15.308 | 15.202 | 0.1066 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_6597 | oxygen16_from_deuterons_fc8 | 15.338 | 15.232 | 0.1065 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_8816 | oxygen16_from_deuterons_fc8 | 15.406 | 15.299 | 0.1065 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| oxygen16_from_deuterons_fc8_run_5725 | oxygen16_from_deuterons_fc8 | 15.365 | 15.258 | 0.1064 | 8 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |

## Dinámica de memoria y topología
| Target | ⟨memory_score_k10⟩ | ⟨Dynamic Strain⟩ | ⟨grado efectivo⟩ |
|--------|--------------------|-------------------|------------------|
| oxygen16_from_deuterons_fc6 | 0.9022 | 0.0134 | 5.000 |
| oxygen16_from_deuterons_fc8 | 0.9256 | 0.0154 | 7.000 |
| oxygen16_from_deuterons_ring8 | 0.9111 | 0.0410 | 2.000 |

## Compuestos aceptados (detalle)
### oxygen16_from_deuterons_fc6
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 11.347 | 11.268 | 0.0788 | 0.992 | 1.000 | 0.827 | 0.0023 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 1 | 11.243 | 11.166 | 0.0777 | 0.988 | 0.999 | 0.834 | 0.0055 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2 | 11.238 | 11.159 | 0.0783 | 0.997 | 0.999 | 0.801 | 0.0056 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3 | 11.321 | 11.243 | 0.0776 | 0.980 | 0.999 | 0.797 | 0.0052 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4 | 11.302 | 11.224 | 0.0777 | 0.983 | 0.999 | 0.859 | 0.0041 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 5 | 11.260 | 11.182 | 0.0786 | 0.997 | 1.000 | 0.794 | 0.0032 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 6 | 11.214 | 11.136 | 0.0782 | 0.997 | 0.999 | 0.849 | 0.0058 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 7 | 11.346 | 11.268 | 0.0779 | 0.981 | 0.999 | 0.833 | 0.0045 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 8 | 11.259 | 11.183 | 0.0759 | 0.964 | 0.999 | 0.810 | 0.0064 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 9 | 11.284 | 11.206 | 0.0781 | 0.989 | 1.000 | 0.834 | 0.0028 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 10 | 11.397 | 11.318 | 0.0790 | 0.991 | 0.999 | 0.821 | 0.0062 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 11 | 11.343 | 11.265 | 0.0773 | 0.974 | 0.999 | 0.828 | 0.0074 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 12 | 11.343 | 11.265 | 0.0786 | 0.991 | 0.999 | 0.806 | 0.0050 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 13 | 11.322 | 11.244 | 0.0780 | 0.985 | 0.999 | 0.831 | 0.0056 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 14 | 11.218 | 11.140 | 0.0781 | 0.996 | 0.999 | 0.838 | 0.0043 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 15 | 11.242 | 11.164 | 0.0778 | 0.990 | 0.999 | 0.877 | 0.0065 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 16 | 11.315 | 11.236 | 0.0782 | 0.987 | 1.000 | 0.834 | 0.0033 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 17 | 11.282 | 11.205 | 0.0777 | 0.985 | 1.000 | 0.807 | 0.0038 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 18 | 11.187 | 11.109 | 0.0781 | 0.998 | 0.999 | 0.812 | 0.0052 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 19 | 11.246 | 11.169 | 0.0773 | 0.983 | 0.999 | 0.792 | 0.0060 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
_(9967 más…)_

### oxygen16_from_deuterons_fc8
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 15.047 | 14.944 | 0.1029 | 0.978 | 0.999 | 0.796 | 0.0065 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 1 | 15.121 | 15.019 | 0.1021 | 0.965 | 0.999 | 0.817 | 0.0049 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2 | 15.075 | 14.972 | 0.1037 | 0.983 | 1.000 | 0.816 | 0.0039 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3 | 14.980 | 14.875 | 0.1043 | 0.996 | 0.999 | 0.809 | 0.0051 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4 | 14.964 | 14.861 | 0.1032 | 0.986 | 0.999 | 0.729 | 0.0067 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 5 | 15.092 | 14.987 | 0.1043 | 0.988 | 0.999 | 0.805 | 0.0048 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 6 | 14.997 | 14.893 | 0.1041 | 0.992 | 0.999 | 0.821 | 0.0057 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 7 | 15.077 | 14.973 | 0.1043 | 0.988 | 0.999 | 0.810 | 0.0041 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 8 | 14.953 | 14.850 | 0.1037 | 0.992 | 1.000 | 0.833 | 0.0031 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 9 | 15.096 | 14.992 | 0.1049 | 0.993 | 0.999 | 0.845 | 0.0053 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 10 | 14.951 | 14.847 | 0.1036 | 0.991 | 0.999 | 0.815 | 0.0049 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 11 | 15.109 | 15.005 | 0.1044 | 0.988 | 0.999 | 0.805 | 0.0045 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 12 | 15.094 | 14.989 | 0.1048 | 0.992 | 1.000 | 0.815 | 0.0034 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 13 | 15.251 | 15.146 | 0.1051 | 0.986 | 0.999 | 0.805 | 0.0068 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 14 | 14.914 | 14.810 | 0.1041 | 0.998 | 1.000 | 0.825 | 0.0038 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 15 | 15.194 | 15.089 | 0.1052 | 0.990 | 0.999 | 0.824 | 0.0056 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 16 | 15.138 | 15.033 | 0.1047 | 0.989 | 0.999 | 0.793 | 0.0057 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 17 | 15.098 | 14.995 | 0.1035 | 0.980 | 1.000 | 0.837 | 0.0038 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 18 | 15.217 | 15.113 | 0.1038 | 0.975 | 0.999 | 0.816 | 0.0042 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 19 | 15.042 | 14.938 | 0.1040 | 0.988 | 1.000 | 0.819 | 0.0031 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
_(9975 más…)_

### oxygen16_from_deuterons_ring8
| run_id | Σm | M_final | E_b | R_final | Q_lock | PE | H_block | Partículas |
|--------|----|---------|-----|---------|--------|----|---------|------------|
| 0 | 14.964 | 14.860 | 0.1034 | 0.988 | 0.999 | 0.796 | 0.0063 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 2 | 15.011 | 14.911 | 0.0996 | 0.949 | 0.999 | 0.793 | 0.0058 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 3 | 15.202 | 15.101 | 0.1009 | 0.949 | 0.999 | 0.769 | 0.0042 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 4 | 15.152 | 15.047 | 0.1053 | 0.993 | 0.999 | 0.819 | 0.0043 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 5 | 15.241 | 15.144 | 0.0977 | 0.916 | 0.999 | 0.787 | 0.0043 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 6 | 15.222 | 15.123 | 0.0992 | 0.931 | 1.000 | 0.782 | 0.0037 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 7 | 14.995 | 14.894 | 0.1013 | 0.966 | 0.999 | 0.857 | 0.0056 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 9 | 15.085 | 14.984 | 0.1014 | 0.961 | 0.999 | 0.812 | 0.0045 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 11 | 15.105 | 15.010 | 0.0954 | 0.903 | 0.999 | 0.796 | 0.0059 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 12 | 15.106 | 15.004 | 0.1013 | 0.959 | 0.999 | 0.773 | 0.0050 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 13 | 15.030 | 14.928 | 0.1022 | 0.972 | 0.999 | 0.802 | 0.0046 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 14 | 15.176 | 15.076 | 0.0999 | 0.941 | 0.999 | 0.810 | 0.0042 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 15 | 15.169 | 15.066 | 0.1036 | 0.977 | 0.999 | 0.804 | 0.0044 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 16 | 14.991 | 14.888 | 0.1025 | 0.977 | 0.999 | 0.801 | 0.0042 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 17 | 15.184 | 15.083 | 0.1007 | 0.948 | 0.999 | 0.779 | 0.0049 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 18 | 15.002 | 14.901 | 0.1010 | 0.962 | 0.999 | 0.840 | 0.0043 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 19 | 15.178 | 15.076 | 0.1021 | 0.961 | 0.999 | 0.767 | 0.0054 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 20 | 15.110 | 15.009 | 0.1009 | 0.954 | 1.000 | 0.847 | 0.0037 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 21 | 15.077 | 14.972 | 0.1045 | 0.990 | 0.999 | 0.836 | 0.0043 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
| 22 | 15.093 | 14.989 | 0.1044 | 0.988 | 1.000 | 0.790 | 0.0038 | deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron, deuteron |
_(7379 más…)_
