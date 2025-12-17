
# 0. Objective

Define in Ola1 a family of derived parameters that approximate:

- Lock volume  
- Static lock density (Q/S1/S2 structure)  
- Dynamic lock density (order/chaos in time)

3 “mass” proxies based on these:

- `M_spec` (spectral baseline)  
- `M1` (volume × static density)  
- `M2` (ω_base × volume × static density)  
- `M3` (ω_base × volume × total structural+dynamic density)

All of this is computed per run in Ola1 and written to:

- `Ola1_..._all_runs_proxies.csv`  
- and optionally to `simple_blocks.json` when promoting blocks.

---

## 1. Available inputs in Ola1

Per run, the engine already produces / can produce:

### Layer structure

- `participation_entropy` (call it `H_layers`): participation entropy over {Q, S1, S2}, already present.  
- Average `layer_energy_fraction` (JSON or vector with {Q, S1, S2}) → already calculated and can be persisted in blocks.

### Frequency spectrum

- List of unscaled frequency peaks (`omega_peaks_raw` or equivalent).  
- If today only `band_energies_gev` (already rescaled) is stored, we need to keep the list of ω before rescaling, per run.  
- `band_count` = number of significant bands (already exists in proxies).

### Dynamic entropy/chaos in Ola1

- `entropy_chaos.mean_H_lock_norm` (0–1): normalized lock entropy (over the lock_S1 series), already calculated.  
- `entropy_chaos.PE_tick_norm` (0–1): permutation entropy over `lock_S1_series` (m=5, τ=1), already calculated.

Reminder:

- Ola1: PE over S1(t) fraction (energy lock).  
- Ola2: PE over R(t) (Kuramoto order parameter). We **do not** try to replicate R(t) in Ola1; we use PE over S1 as a proxy.

We do **not** touch the internal computation of `entropy_chaos`: we only use `mean_H_lock_norm` and `PE_tick_norm`.

---

## 2. Derived parameters per run

### 2.1. Lock volume (pure structure)

Let:

- `H_layers` = participation_entropy of the run.  
- `H_layers_max = log(3)` (three layers Q, S1, S2).

Define:

```text
Effective number of active layers (discrete version of participation ratio):

V_layers = exp(H_layers)        # range ~ [1, 3]

Effective lock volume:

V_lock = V_layers * band_count
```

Interpretation:

- If only Q dominates and there is 1 band: `H_layers ≈ 0 → V_layers ≈ 1 → V_lock ≈ 1`.  
- If Q/S1/S2 have comparable weights and there are several bands: `H_layers` is high → `V_layers` approaches 3 → `V_lock` grows.

This `V_lock` is your “how many structural springs are really resonating”.

---

### 2.2. Static lock density (Q/S1/S2 structure)

Normalize layer entropy to `[0,1]`:

```text
H_layers_norm = H_layers / H_layers_max          # [0,1]
D_stat = 1.0 - H_layers_norm                     # [0,1]
```

- `D_stat ≈ 1` → energy very concentrated in a single layer (statically sharp lock).  
- `D_stat ≈ 0` → energy distributed among Q/S1/S2 (statically diffuse lock).

This needs nothing beyond `participation_entropy` already computed.

---

### 2.3. Dynamic lock density (ordered chaos)

We use the `entropy_chaos` fields in Ola1, computed over the `lock_S1_series`:

- `mean_H_lock_norm ∈ [0,1]`, already normalized.  
- `PE_tick_norm ∈ [0,1]`, normalized permutation entropy.

We build a dynamic coherence factor:

```text
D_dyn = (1.0 - mean_H_lock_norm) * (1.0 - PE_tick_norm)
```

- High `mean_H_lock_norm` → lock changing / diffuse over time.  
- High `PE_tick_norm` → `lock_S1_series` is chaotic.

- `D_dyn ≈ 1` ⇒ energy lock very ordered and stable in time.  
- `D_dyn ≈ 0` ⇒ energy lock diffuse and/or chaotic.

Optional clipping:

```text
D_dyn = max(0.0, min(1.0, D_dyn))
```

---

### 2.4. Total lock density

Combine static + dynamic structure:

```text
rho_lock = D_stat * D_dyn    # [0,1]
```

Interpretation:

- Increases when:
  - energy is concentrated in few layers (`D_stat` high), and  
  - the lock is stable/ordered in time (`D_dyn` high).
- Decreases if either of those breaks.

---

### 2.5. Reference frequency ω_ref

We need a base frequency per run as a spectral reference.

Assume the engine exposes `omega_peaks_raw` as an ascending list (after noise filtering). Define:

```text
omega_ref = min(omega_peaks_raw)      # lowest significant frequency band
```

If the code already marks a “main” band, you can use that; otherwise, the lowest one is the simple option and consistent with “softest mode” ~ base mass.

---

### 2.6. Lock mass/energy proxies

With all the above:

**Spectral baseline (no lock):**

```text
M_spec = omega_ref
```

**Geometric static mass (“volume × density”):**

```text
M1 = V_lock * D_stat
```

**Spectral + static structure:**

```text
S_lock = V_lock * D_stat        # pure structural factor
M2 = omega_ref * S_lock
```

**Spectral + structural + dynamic (full):**

```text
rho_lock = D_stat * D_dyn
M3 = omega_ref * V_lock * rho_lock
```

So per run we define 4 numbers:

```text
M_spec, M1, M2, M3
```

All in internal units (not GeV).  
If later you want to rescale any of them to GeV, you can apply a global spectral `K`, but that is another layer.

---

## 3. Persistence of these parameters

### 3.1. In `Ola1_..._all_runs_proxies.csv`

Add per-run columns:

Inputs that may not yet be in the CSV but are in the JSON:

- `mean_H_lock_norm`  
- `PE_tick_norm`

Structural derived quantities:

- `H_layers` (participation_entropy already there)  
- `V_layers`  
- `V_lock`  
- `D_stat`

Dynamic:

- `D_dyn`  
- `rho_lock`

Spectral:

- `omega_ref`

Mass proxies:

- `M_spec`  
- `M1`  
- `M2`  
- `M3`

With this, any downstream analysis (zoo, matching, plots) can use these fields without going back to the raw JSON.

---

### 3.2. In `simple_blocks.json`

When promoting blocks, in addition to what is already copied:

For the corresponding `origin_run_id`, copy:

- `omega_ref`  
- `V_lock`  
- `D_stat`  
- `D_dyn`  
- `rho_lock`  
- `M_spec`, `M1`, `M2`, `M3`

These fields are added to each block as extra attributes.  
They do not break anything existing (purely additive).

---

## 4. Explicit note on PE in Ola1 vs Ola2

In the documentation (comments / docstrings), make it clear:

- In Ola2, `PE_tick_norm` is computed over the Kuramoto global order parameter series:

  ```text
  R(t) = |⟨e^{iθ}⟩|
  ```

- In Ola1, `PE_tick_norm` is computed over `lock_S1_series =` energy fraction in S1(t) (energy lock), **not** over an R(t) of phases.

Therefore:

- `D_dyn` and `rho_lock` in Ola1 are metrics of **dynamic coherence of the energy lock**,  
- They are **not** numerically comparable directly to Ola2 PE values, but they play the same conceptual role (chaos/order of the pattern over time).

With this spec the programmer can:

- Without touching the core math of the engine,  
- Simply plug in: read `participation_entropy`, `entropy_chaos.mean_H_lock_norm`, `entropy_chaos.PE_tick_norm`, `omega_peaks_raw`, `band_count`,  
- Compute these derived quantities,  
- Save them into proxies and blocks.

From there, you can inspect in Ola1 how `M_spec`, `M1`, `M2`, `M3` distribute by family, without falling back into the pit of `E_internal`.
