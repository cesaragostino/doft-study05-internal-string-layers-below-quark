# Study05 – DOFT Internal Layers Simulator

Pequeño simulador de osciladores acoplados con capas internas (S1, S2, opcional S3) y una capa efectiva Q, siguiendo `docs/STUDY05_code_header_and_structures.md`.

## Estructura
- Código: `src/study05/`
- Datos de entrada/sorteos: `data/raw/`
- Resultados procesados y gráficas: `data/processed/`

## Requisitos
- Python 3.8+ con `numpy` y `matplotlib` disponibles (matplotlib solo si quieres gráficas).

## Workflow completo (generar datos)
Desde la raíz del repo:
```bash
PYTHONPATH=src python3 -m study05.run_sweep \
  --case CaseA_2layers \
  --runs 50 \
  --seed 123 \
  --band-min 0.0 \
  --band-max 3.0
```
Esto:
- Guarda parámetros en `data/raw/study05_sweep_params.json`.
- Guarda resultados en `data/processed/study05_sweep_results.json`.
- Si no usas `--no-plots`, también crea gráficos en `data/processed/`.

Cambios útiles:
- Usa `--case CaseB_3layers` para incluir S3.
- Ajusta `--n-*` para modos por capa y `--max-complexity` para forzar `C <= 8–10`.
