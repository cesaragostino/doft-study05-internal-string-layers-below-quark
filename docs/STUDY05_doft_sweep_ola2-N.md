# DOFT Sweep Ola2–N

**S1.0 Premisas (BOLD)**

- SWEEP sigue siendo motor diferencial (ola1-like) + acople por edges.
- S1 NO implementa el motor diferencial todavía.
- S1 solo garantiza que cada evaluación (sweep) puede “hidratar” una entity a los insumos numéricos mínimos que el motor diferencial va a necesitar en S2.
- DOF-only, cero SM.

## S1.1 Objetivo concreto

Dado un `entity_candidate` (edges + assignment + parent_ids + engine_params_bin_id), construir un objeto **HydratedEntity** con:

- topology (N, edges)
- node_inputs DOF por nodo, derivado desde Ola1 exports (sin SM)
- lineage/provenance completo (para trazabilidad)

Y dejarlo listo para que en S2 el motor diferencial consuma:

```
simulate_differential(hydrated_entity, engine_params, seed)
```

## S1.2 Inputs exactos (ya cableados en S0)

En config de sweep (`inputs`), deben existir y resolverse:

- blocks_json (default: `data/processed/ola1/simple_blocks.json`)
- dof_dna_catalog_csv (default: `data/processed/ola1/dof_dna_catalog.csv`)

En S1 sí los leemos (a diferencia del hook de S0).

## S1.3 Load blocks + DNA y preparar lookup tables

### S1.3.1 Regla

Si los archivos de Ola1 no contienen todas las columnas/campos que necesitamos, NO se parchea el Sweep con “fallbacks” raros:

- se crea/ajusta un exportador ola1 (tipo `ola1_export_dna_block_id` / `ola1_export_sweep_inputs`) que deje un set estable.

### S1.3.2 Implementación (S1)

- Cargar `blocks_json` una vez.
- Cargar `dof_dna_catalog_csv` una vez.
- Join estricto por `block_id`:
  - si falta DNA y require_dna=true → error
- Construir mapas:
  - `block_by_id[block_id]`
  - `dna_by_block_id[block_id]`

### S1.3.3 Inputs DOF necesarios (CORREGIDO)

Desde `blocks_json`, por bloque:

- block_id
- omega_ref (float)
- theta_internal (object) — REQUIRED  
  Hard rule: si falta → error (no se inventa nada)
- provenance/origin_run_id si existe (trazabilidad)

Desde `dof_dna_catalog_csv`:

- dof_grade
- dof_family_id
- genes_min si existe (o {})

Regla dura: Sweep/S2 no inventa estructura interna.  
Si no viaja theta_internal, se rompe el modelo diferencial.

## S1.4 NodeInputV1 schema (CORREGIDO)

Para cada nodo i de la entidad (orden canónico):

- node_index: int
- block_id: str
- omega_ref: float
- theta_internal: object (REQUIRED)
- dof_grade: str
- dof_family_id: str
- genes_min: object

### S1.4.1 Validación hard de theta_internal (no interpretativa)

En S1 validar:

- schema_version == "theta_internal_v1"
- modes existe y no es vacio
- es JSON-serializable
- no vacío (para evitar basura)

Contrato: theta_internal contiene solo parametros (no estado inicial).

## S1.5 Hydrate entity

Input: candidato con `assignment.block_ids` + `edges` + `canonical_node_order`.

Output: **HydratedEntityV1**:

- entity_id, ola, template_name, edges, canonical_node_order, assignment, parent_ids
- nodes: List[NodeInputV1] (incluye theta_internal)
- engine_params_bin_id (desde candidato)
- seed (desde candidato)
- provenance (hashes)
- theta_internal_digest:
  - `sha256(canonical_json(list_of_theta_internal_in_canonical_order))`

## S1.6 Write evaluation record (append-only)

Por cada candidato hidratado:

escribir una línea en `evaluations.jsonl` con:

- schema_version
- run_session_id
- timestamp_utc
- ola
- role="sweep"
- entity_id
- eval_id (regla ya fijada)
- engine_params_bin_id
- seed
- hydration resumen:
  - N
  - missing_blocks=0
  - missing_dna=0
  - theta_internal_present=true
  - theta_internal_digest=...
- structure (template_name/edges/assignment/canonical_node_order)
- nodes (hidración explícita)
- provenance

## S2.0 Objetivo

Dado un **HydratedEntityV1** (salido de S1) con:

- N nodos (cada uno con theta_internal, omega_ref, etc.)
- edges
- engine_params (incluye dt, T_ticks, W, K_global, tau_field, etc.)

ejecutar un motor diferencial tipo Ola1 por nodo + acople de red solo en S1 con retardo `tau_field`, y producir solo métricas escalares en `evaluations.jsonl`.

## S2.1 Inputs exactos (lo que S2 consume)

Por evaluación (entity_id, seed, engine_params_bin_id):

### 1) Estructura

- N
- edges: List[Tuple[int,int]] (índices 0..N-1)

### 2) Nodos (orden canónico)

Para cada nodo i:

- theta_internal (required, blob completo de parámetros/estado inicial del oscilador Ola1)
- omega_ref (float)
- metadata DOF (grade/family/genes) solo para trazabilidad (no para dinámica)

### 3) Parámetros de engine (mínimos para S2)

Desde config (o reconstruidos desde bin en Sweep):

- dt: float
- T_ticks: int
- W: int
- K_global: float (acople inter-nodo)
- tau_field: float (retardo real, en tiempo continuo)

Cualquier parámetro interno requerido por el oscilador Ola1 NO se inventa: viene en theta_internal.

## S2.3 Acople inter-nodo (F_inter, ecuacion exacta)

El acople se aplica solo en la capa S1.

Para cada nodo i:

F_inter_i(t) = (K_global / N_neighbors(i)) * sum_{j in N(i)} sin(theta_j,S1(t - tau_field) - theta_i,S1(t))

Donde:

- N(i) = vecinos de i en edges
- N_neighbors(i) = |N(i)|

Si N_neighbors(i) = 0 => F_inter_i(t) = 0

Implementacion exacta:

- se consulta el buffer para theta_j,S1(t - tau_field)
- se usa theta_i,S1(t) actual del tick

## S2.4 Motor por nodo (Ola1-core)

Cada nodo i es una instancia del oscilador diferencial Ola1 inicializada con theta_internal.

En cada tick:

- calcular dinamica interna por nodo (Ola1) => update de estados
- debe producir (directo o derivable) la fase theta_i,S1(t)
- y debe producir observables de energia por capa o equivalentes:
  E_Q(t), E_S1(t), E_S2(t) >= 0

Aplicar el termino inter-nodo como fuerza/drive adicional sobre la ecuacion de S1
(segun como este escrita Ola1 internamente).

Regla: el unico agregado de red es F_inter,i(t) en S1.
Importante: no se redisenia la fisica base; solo se agrega ese termino.

## S2.5 Que series se calculan (en memoria)

Durante el run se calculan en memoria (no se escriben a JSONL):

- E_Q[t], E_S1[t], E_S2[t] agregadas a nivel red (sum o mean por tick)
- pQ[t], pS1[t], pS2[t] (fracciones)
- theta_S1[i,t] (solo si debug; si no, no guardar array completo)
- R_network_S1[t] (parametro de orden)

Definiciones:

p_i(t) = E_i(t) / (E_Q(t) + E_S1(t) + E_S2(t) + eps)

R_network_S1(t) = |(1/N) * sum_j exp(i * theta_j,S1(t))|

## S2.6 Metricas canonicas (lo que se escribe en evaluations.jsonl)

Se reportan escalares sobre ventana final W ticks (ultimos W):

### Participacion por capas (entropia composicional)

H_part(t) = -sum_i p_i(t) * log(p_i(t) + eps)

H_part_norm(t) = H_part(t) / log(3)

Guardar:

- H_part_norm_mean
- H_part_norm_std
- pQ_mean, pS1_mean, pS2_mean (en ventana W)

### Complejidad temporal (Permutation Entropy)

Serie canonica:

x(t) = p_S1(t)

Compute:

PE_lockS1_norm = permutation_entropy(x(t), m=5, tau=1)

(sobre ventana W, V1)

Guardar metadata:

- PE_m=5
- PE_tau=1
- PE_len=W

### Sincronizacion de red

Guardar:

- R_network_S1_mean_lastW
- R_network_S1_std_lastW
- R_network_S1_final

## S2.7 Politica de storage (anti-explosion)

### S2.7.1 En evaluations.jsonl

- NO se guardan arrays. Solo escalares.

### S2.7.2 Debug traces

Unico flag permitido:

- debug_traces: bool (por defecto false)

Si debug_traces=true:

- guardar .npz externo por evaluacion
- el JSONL guarda:
  - trace_path
  - trace_sha256

Y listo.

## S2.8 Entregable de codigo (lo que el programador implementa)

Archivo nuevo (clean-room):

- src/olar/differential_engine.py

Clase: DifferentialNetwork

### Constructor

Recibe: nodes_theta_internal, omega_ref, edges, engine_params, seed.

Inicializa N osciladores Ola1 (instancias internas).

Inicializa HistoryBuffer para theta_S1 con delay_steps.

### HistoryBuffer

- circular: buffer[delay_steps+1, N]
- push(theta_S1_vector)
- get_delayed() devuelve theta_S1_vector de hace delay_steps

### step()

- obtener theta_S1_delayed = buffer.get_delayed()
- calcular F_inter[i] con ecuacion exacta
- para cada nodo i:
  - osc[i].step(dt, drive_s1=F_inter[i]) (interfaz interna)
  - leer theta_S1[i] actualizado
- buffer.push(theta_S1_current)
- acumular energias y R_network_S1(t)

### run()

Loop por T_ticks.

Devuelve solo los agregados necesarios para calcular metricas:

(ideal) acumuladores de ventana W ya "online" para no guardar todo.

## S2.9 Output de S2 hacia Sweep

S2 retorna a sweep.py un dict metrics_raw con:

- H_part_norm_mean
- H_part_norm_std
- pQ_mean, pS1_mean, pS2_mean
- PE_lockS1_norm, PE_m, PE_tau, PE_len
- R_network_S1_mean_lastW, R_network_S1_std_lastW, R_network_S1_final

y debug_trace_ref solo si debug_traces.

## S3 — Sweep Orchestrator + Evaluations Log (V1, DOFT-only)

## S3.0 Objetivo

Ejecutar Sweep sobre los candidatos de Explorer para delinear robustez local:

- por seeds deterministas
- por vecindario de parametros (bins vecinos)
- con early-stop para ahorrar computo
- guardando solo metricas escalares por evaluacion en evaluations.jsonl (append-only, dedupe por eval_id)

Prohibido: SM, formatos legacy, arrays gigantes en JSONL.

## S3.1 Inputs exactos

### S3.1.1 Archivos

Desde olaX_sweep.json + doft_run_inputs_v4.json (wiring):

- entities_candidates_jsonl (salida del Explorer, schema olar_entity_candidate_v1)
- blocks_json (para hidratacion, mismo que Explorer)
- dof_dna_catalog_csv (para hidratacion, mismo que Explorer)
- templates_json (para validar/firmar topologias si aplica)

### S3.1.2 Campos minimos por candidato

Cada linea candidata debe traer (top-level):

- entity_id
- build_plan (dict, con edges, template_name, canonical_node_order, assignment.block_ids, assignment.block_key_used)
- engine_params_bin_id (del attempt ganador)
- seed (del attempt ganador; sirve como hint, no reemplaza seeds del sweep)
- metrics_summary (solo para ranking/seleccion)
- provenance

## S3.2 Candidate selection (quien entra al sweep)

El Sweep hace un filtro determinista "barato" solo con lo que viene del Explorer, antes de simular:

Reglas desde candidate_source.filter:

- require_quality_lock_ok
- require_memory_non_negative
- min_quality_lock
- min_R_mean_lastW (si el Explorer ya la calcula)
- max_phase_var_lastW
- top_k_by
- top_k

Salida de este paso:

- lista ordenada de entity_id a procesar (maximo top_k)

Nota practica: si el ranking usa campos que no existen en metrics_summary, eso es error de config (fail-fast).

Implementacion V1 (loop + budget):

- lectura streaming de entities_candidates.jsonl
- filtros se aplican antes de cualquier simulacion
- top_k se mantiene con heap si top_k es grande
- budget por entidad via budgets.max_evals_per_entity (no cuenta dedupe)
- al final se imprime un resumen: evaluations_written, entities_processed, entities_skipped_by_filter, dedupe_skips

## S3.3 Hidratacion (usa S1 como modulo, no se re-inventa aca)

Para cada candidato seleccionado, se construye **HydratedEntityV1** llamando al modulo de S1 (ya cerrado).

Para cada nodo del assignment.block_ids:

- block_id
- omega_ref
- theta_internal (REQUIRED)
- DOF genes minimos (grade/family/etc.) para trazabilidad

Regla: si falta theta_internal en el bloque => error (no defaults inventados).

## S3.4 Vecindario de parametros (bins vecinos)

Modo V1: neighborhood.mode = "param_bin_neighbors"

Inputs:

- base_bin = candidate.engine_params_bin_id
- max_neighbor_bins = config.neighborhood.max_neighbor_bins

Definicion:

Interpretar engine_variation.bins como edges por dimension:

- K_local_edges
- kappa_edges
- tau_field_edges
- sigma0_edges
- sigma_tc_edges

engine_params_bin_id es el indice por dimension (ej: K2_k1_tau0_s00_stc0)

Generacion de vecinos:

- vecinos a distancia Manhattan <= max_neighbor_bins en el espacio discreto de indices
- siempre incluye el bin base
- bins fuera de rango se descartan

Salida:

- lista determinista de engine_params_bin_id a evaluar por entidad

## S3.5 Resolucion determinista de engine_params desde engine_params_bin_id

Como entities_candidates.jsonl ya no trae engine_params, el Sweep debe reconstruirlos asi:

- engine_params = engine_defaults (desde olaX_sweep.json o desde el mismo set que Explorer)
- para cada dimension del bin:
  - tomar el intervalo (edge_low, edge_high) y elegir un valor determinista dentro del bin
  - regla V1 cerrada: midpoint del bin
    v = (edge_k + edge_{k+1}) / 2

Parametros no binned quedan iguales a defaults (dt, T_ticks, W, sigma_theta_init, etc.).

Resultado:

- no hay floats en el hash del eval_id, pero si se guardan floats en engine_params (para reproducibilidad)

## S3.6 Seeds deterministas del Sweep (la regla manda)

Desde config:

- seeds = N
- salt = "sweep_v1"

Regla cerrada:

seed_i = u32(hash(entity_id, i, salt))

Donde u32 fuerza rango 0..2^32-1.

## S3.7 Ejecucion diferencial (llama S2)

Por cada entidad, por cada engine_params_bin_id, por cada seed:

- llamar DifferentialNetwork.run(...) de S2 con:
  - HydratedEntityV1
  - edges
  - engine_params reconstruidos
  - seed

S2 devuelve metrics_raw (escalares) incluyendo:

- H_part_norm_mean/std, pQ_mean/pS1_mean/pS2_mean
- PE_lockS1_norm, PE_m, PE_tau, PE_len
- R_network_S1_mean_lastW, R_network_S1_std_lastW, R_network_S1_final

## S3.8 Early-stop (ahorro de computo, sin ambiguedad)

Se implementa exactamente como dice config (budgets.early_stop), pero la metrica de corte para diferencial queda cerrada asi:

usar R_network_S1_mean_lastW como “la sincronizacion de red” para el corte.

Regla:

despues de after_seeds seeds evaluados para un bin:

si R_network_S1_mean_lastW < fail_threshold => cortar el resto de seeds para ese bin.

## S3.9 Output: evaluations.jsonl (append-only + dedupe)

Archivo:

- data/processed/olaN/raw/evaluations.jsonl

Cada evaluacion escribe 1 linea con schema olar_evaluation_v1 (o el que ya se usa en sweep), con top-level minimo consistente:

Campos requeridos:

- schema_version
- run_session_id
- timestamp_utc
- ola
- role: "sweep"
- entity_id
- eval_id (dedupe key)
- seed
- engine_params_bin_id
- engine_params (floats completos)
- metrics_raw (escalares)
- tags_raw (si existen; si no, {})
- reasons_raw (si existen; si no, [])
- provenance (hashes + machine, igual patron Explorer)

Regla de eval_id (mandatoria):

eval_id = hash(entity_id, seed, engine_params_bin_id, role="sweep", schema_version)

Sin floats en el hash.

### Dedupe / Resume

Al iniciar:

- escanear evaluations.jsonl y armar seen_eval_ids

En loop:

- si eval_id ya existe => skip antes de correr S2

## S0.0 Premisas

- SWEEP = motor diferencial (ola1-like) + acople por edges.
- NO Kuramoto en Sweep.
- NO SM en Sweep.
- Sweep consume solo lo que produce Explorer (candidatos) + configs.
- Todo output del Sweep es append-only JSONL y resume-safe.

## S0.1 Inputs exactos del Sweep (archivos)

### 1) Candidates (obligatorio)

`entities_candidates.jsonl` con schema `olar_entity_candidate_v1` (versión nueva, sin legacy).

Campos requeridos (top-level):

- schema_version
- run_session_id
- timestamp_utc
- ola
- entity_id
- source_eval_id
- build_plan (object)
- template_name
- edges
- canonical_node_order
- assignment (incluye block_ids y block_key_used)
- parent_ids
- seed (esto puede existir pero Sweep NO debe confiar en este seed para sweep-seeds; ver seed policy)
- engine_params_bin_id
- metrics_summary
- tags_raw
- reasons_raw
- provenance (con hashes y machine)

### 2) Sweep config (obligatorio)

`ola2_sweep.json` (schema `olar_sweep_config_v1`), y `run_sequence.json` si se usa pipeline.

Mínimos necesarios:

- seed_policy (deterministic, seeds, min_seeds_required, salt)
- neighborhood (modo + max_neighbor_bins)
- budgets (max_evals_per_entity, early_stop…)
- engine_defaults y engine_variation.bins (para derivar params desde bin_id)
- outputs.evaluations_jsonl

Nota: si hoy `ola2_sweep.json` no trae engine_defaults/variation, agregarlos ahora (porque Sweep no tendrá engine_params en candidates).

### 3) Optional “olar_inputs” (NO en S0)

No se implementa en S0. Solo se deja el “hook” (path reservado) para Etapa S1/S2.

## S0.3 ID Policy (hard)

### entity_id

- Se toma del candidato (ya determinista por build_plan canónico).
- Sweep NO recalcula entity_id.

### eval_id (hard, sin floats)

Debe ser exactamente:

```
eval_id = hash(entity_id, seed, engine_params_bin_id, role="sweep", schema_version="olar_evaluation_v1")
```

Reglas:

- NO incluir engine_params (floats).
- NO incluir config_hash/code_hash (eso va en provenance, no en eval_id).
- NO incluir metrics.

Dedup key: eval_id (solo eso).

## S0.4 Seed policy (hard)

En Sweep:

- Ignorar candidate.seed para sweep.
- Generar seeds deterministas:

```
seed_i = hash(entity_id, i, salt="sweep_v1")  para i = 0..seeds-1
```

Además:

- min_seeds_required se usa para clasificación posterior (ej: LOCKED requiere >=2 seeds robustas, etc.).
- En S0 solo se loguea.

## S0.5 engine_params derivation (hard)

Como candidates ya NO trae engine_params:

Sweep debe derivar engine_params solo desde:

- engine_defaults
- engine_variation.bins
- engine_params_bin_id

Implementar función única en core (para reutilizar en Explorer/Sweep/Catalog):

- `core/ids/engine_bins.py` (o similar)
- `parse_bin_id(engine_params_bin_id) -> indices`
- `resolve_engine_params(defaults, bins, engine_params_bin_id) -> engine_params(float)`

Formato de bin_id queda congelado:

```
K{idx}_k{idx}_tau{idx}_s0{idx}_stc{idx}
```

IMPORTANTÍSIMO: si cambian bins → cambia taxonomy_version/config, no el formato del bin_id.

## S0.6 Resume / append-only / dedupe (hard)

En el arranque del Sweep:

- Crear set `seen_eval_ids` escaneando `evaluations.jsonl` si existe.

En el loop, antes de ejecutar:

- calcular `seed_i`
- calcular `eval_id`
- si `eval_id` está en set → skip (log)

Solo si no existe:

- correr evaluación (en S0 puede ser stub, pero debe escribir línea completa igual)
- append JSONL
- flush periódico

No debe existir modo overwrite. Solo append.

## S0.7 Candidate selection (hard, mínimo)

Sweep no procesa todo sin filtro.

Input filter mínimo (desde config):

- require_candidate: true (usa tags_raw.candidate del candidato)
- top_k_by: "priority_score" o si no existe, por ahora R_mean_lastW (definido en config)
- top_k: N

Regla:

- No inventar scores: si no hay priority_score, se usa R_mean_lastW.

## S0.9 “Smoke test” obligatorio (para cerrar S0)

Comando:

- correr Sweep con:
  - candidates de tu run smoke
  - top_k=5
  - seeds=3
  - max_neighbor_bins=1
  - max_evals_per_entity=10 (aunque el engine sea stub al inicio)

Verificar:

- genera `evaluations.jsonl`
- rerun → dedupe skip y `evaluations_written` no crece
- `eval_id` cambia cuando cambia seed o bin_id
- `eval_id` NO cambia si el float de engine_params cambia por representación (porque no se hashea)
