# DOFT: Mass from Resonance Frequency – Technical Description and Programming Spec

## 1 Conceptual overview

In DOFT the fundamental entities (blocks) are not spheres with variable volume. Each block is a mode of an underlying delayed–oscillator system (a “lock”) with a characteristic resonance frequency ω. When a lock reaches a stable oscillatory regime (after adaptive tuning and memory), its spectrum contains several peaks corresponding to harmonics or sub‑modes. The lowest significant peak in the raw FFT represents the fundamental resonance of that block. The proposal is to derive the rest mass of a block directly from this frequency, analogous to the relationship \(E = h 
u\) in quantum mechanics.

**Physical analogy.** In field theory the mass of a particle is set by the frequency of a mode of a field. A large oscillation volume (many degrees of freedom in S1/S2) does not change the note being played; it only changes the amplitude or extension of the wave. Therefore volume/density metrics should be used as structural diagnostics, not as mass.

**Conversion constant.** Because the DOFT simulator uses arbitrary time units (ticks) and FFT bins, frequencies must be converted to GeV using a simulation‐specific constant. Fitting the known masses of high‑quality blocks yields

\[
\hbar_	ext{sim} pprox 0.2817~	ext{GeV cycle}^{-1}
\]

which plays the role of \(h / 2\pi\) in the simulated universe. A frequency of 1 cycle per simulation time unit corresponds to \(\sim 0.2817\) GeV of rest mass.

## 2 Source of error and correction

The FFT used to estimate the spectrum has finite resolution. With a run time \(T\) the bin width is

\[
\Delta \omega pprox rac{2\pi}{T}.
\]

If the true frequency lies between bins, selecting the maximum bin introduces an error that can be \(> 10\%\). To reduce this “pixelation” error:

1. **Record the raw FFT.** For each run, store the complex FFT values per mode or at least the power spectrum before any rescaling.
2. **Identify the peak bin** (\(k\)) and its immediate neighbours (\(k-1, k, k+1\)).
3. **Perform sub‑bin interpolation:** fit a parabola (or Gaussian in log‑magnitude) through the three bins and compute the offset \(\delta \in [-0.5, 0.5]\) of the true peak from the centre bin. The interpolated frequency is

\[
\omega_	ext{interp} = rac{2\pi}{T} (k + \delta).
\]

This technique, well known in spectral analysis (Quinn quadratic interpolation), reduces the mass error to \(\sim 1\%\) without lengthening the simulation.

## 3 Implementation specification

### 3.1 Simulation changes

1. **Preserve raw FFT.** In `study05/run_sweep.py` and the relevant engine, after computing the FFT on each run, store the power spectrum (or at least the magnitude of the first few bins around the fundamental) into the proxies CSV (`*_all_runs_proxies.csv`). Include the raw frequency bin width `delta_omega`.

2. **Compute interpolated frequency.**

   - Find `peak_index` as the index of the largest FFT magnitude in the low‑frequency region.
   - Take `X[k-1]`, `X[k]`, `X[k+1]`, compute log magnitudes if using Gaussian fit.
   - Calculate
     \[
     \delta = rac{1}{2} rac{X[k-1] - X[k+1]}{X[k-1] - 2X[k] + X[k+1]}
     \]
     (for quadratic interpolation). Constrain \(\delta\) to \([-0.5, 0.5]\).
   - Set `omega_ref = (peak_index + delta) * delta_omega`.

3. **Store `omega_ref`.** Save `omega_ref` in the proxies CSV and propagate it into `simple_blocks.json` (field `omega_ref`). This replaces the previous approach of taking the third lowest peak or using `band_energies_gev`.

4. **Calibrate and record \(\hbar_	ext{sim}\).**

   - Compute \(\hbar_	ext{sim}\) once per sweep by fitting
     \[
     	ext{sm\_mass\_gev} pprox \hbar_	ext{sim} \cdot \omega_	ext{ref}
     \]
     on all grade A/B blocks with reliable matches (e.g., using linear least squares).
   - Store the value and the regression details in a JSON file (e.g. `hbar_sim_calibration.json`) including the list of runs used.

5. **Use \(\hbar_	ext{sim}\) to compute mass.** For each block:

   \[
   	ext{mass\_sim\_gev} = \hbar_	ext{sim} \cdot \omega_	ext{ref}.
   \]

   Save `mass_sim_gev` in the proxies CSV and `simple_blocks.json` (field `mass_sim_gev`).

### 3.2 Downstream changes

1. **Update matching and selection.** In `study06/match_sm_ola1` use `mass_sim_gev` instead of any mass derived from `E_internal`. The distance metric `d_mass` should measure something like
   \[
   d_	ext{mass} = rac{|	ext{mass\_sim\_gev} - 	ext{sm\_mass\_gev}|}{	ext{tolerance}}.
   \]

2. **Deprecate `E_internal` for mass.** Remove any usage of `E_internal` in mass estimation. Keep internal energy for diagnostics (H_lock, participation entropy, memory load) but not for SM matching.

3. **Volume and density metrics.** Keep `V_lock`, `D_stat`, `rho_lock` (`M1`/`M2`/`M3`) as descriptors of the lock’s structure and coherence. They may be used in filters (e.g., require `rho_lock > 0.2` to ensure a well‑formed lock) but do *not* contribute to the mass.

4. **Recalibration conditions.** Refit \(\hbar_	ext{sim}\) only if changes occur in the integrator step `dt`, the FFT length, or the engine’s scaling. Otherwise a single global constant should suffice for all sweeps/olas.

### 3.3 Developer notes

- The quadratic interpolation formula is cheap to implement and sufficient. If the FFT uses a window (e.g., Hann), use the corresponding coefficient (Quinn’s formula). Provide unit tests verifying that a synthetic sinusoid at a non‑integer bin index yields a correct `omega_ref` within <1% error.
- Document the units clearly: `omega_ref` is in cycles per simulation time unit; `mass_sim_gev` is in GeV. Multiplying `omega_ref` by `hbar_sim` yields mass.
- Update any plotting/analysis scripts to refer to `mass_sim_gev` rather than `E_internal` if the goal is to compare to SM masses.
- The existing `M1`, `M2`, `M3` fields remain to describe structural properties and should not be used as masses.

## 4 Summary

The revised approach positions each DOFT block as a fundamental oscillator whose mass is simply

\[
M = \hbar_	ext{sim} \, \omega.
\]

A single conversion constant \(\hbar_	ext{sim} pprox 0.2817\) fixes the scale, and sub‑bin interpolation removes most discretization error. Energy internal to the lock (volume, density, memory) remains useful for characterizing stability and structure, but no longer conflates with mass. This yields a physically interpretable and stable mass metric for use in matching DOFT states to the Standard Model.


# AMENDMENT - RECALIBRATING wakko h

# Changes to Stabilize ℏ_sim and Avoid “Crazy ħ”

## A) Minimal Changes (Mandatory)

### Unify units: distinguish *f* vs *ω*

Store explicitly:

- `f_ref` (cycles per simulation time unit)
- `omega_ref` (rad / time) = `2 * pi * f_ref`

If you use:

- `M = hbar_sim * omega` → use `omega_ref`.
- `M = h_sim * f` → use `f_ref`.

Persist `freq_units` or separate fields to avoid confusion.

### Store `delta_f` / `delta_omega` explicitly

Persist:

- `dt_sample = dt * sample_stride`
- `n_samples`
- `T_obs = n_samples * dt_sample`
- `delta_f = 1 / T_obs`
- `delta_omega = 2 * pi * delta_f`

### Peak selection: robust fundamental (not “global maximum”)

Replace “maximum in low frequencies” with:

- Exclude DC (`k = 0` forbidden).
- Search for the first peak (lowest frequency) that satisfies:

  - `mag[k] >= peak_prominence_min` **or** `mag[k] / median(mag) >= SNR_min`
  - optionally: `mag[k] >= frac_of_max * max_mag` (e.g. ≥ 0.2)

If there are multiple channels (Q/S1/S2): define an “identity channel” (ideally Q) and always use that one.

---

## B) Reduce Spectral Error (Needed – discuss if not feasible)

### Sub-bin interpolation of the peak (parabolic)

If `1 <= k < len(mag) - 1`:

- Compute `delta` (parabolic) using `mag[k-1]`, `mag[k]`, `mag[k+1]`.
- `k_hat = k + delta`
- `f_ref = k_hat * delta_f`
- `omega_ref = 2 * pi * f_ref`

If there are no neighbours: use the raw bin.

Store debug fields:

- `peak_k`, `peak_delta`
- `mag_km1`, `mag_k`, `mag_kp1`

### FFT window + zero padding (optional)

- Apply a Hann window to reduce leakage.
- Zero-pad (e.g. 4×) to densify bins (improves interpolation).

---

## C) Robust Estimation of ℏ_sim (Key)

### Pre-filter by cluster: keep the lowest-frequency cloud

Goal: avoid harmonics dominating the calibration.

For each “calibratable” run (grade A/B + reliable match):

1. Compute `omega_ref` (interpolated).
2. Build clusters in `omega_ref` and choose the lowest-ω cluster as **fundamental**.

Simple and robust implementation:

- Build a 1D histogram / KDE of `omega_ref`.
- Find the first dominant mode (peak) in the low-frequency band.
- Keep runs within ±`tol_cluster` (e.g. ±10% or ±2× local IQR) of that mode.

Easy programmable alternative:

- Sort ω and group by gaps: split where the relative gap exceeds X (e.g. 20–30%).
- Take the first (lowest) group.

Only this subset (fundamental cluster) is used to calibrate `hbar_sim`.

### Calibration by weighted median

For each run in the fundamental cluster:

- `h_i = m_SM / omega_ref`

Define:

- `hbar_sim = weighted_median(h_i, weight = quality_weight)`

Example:

- `quality_weight = Q_lock / (1 + d_total)`

Additional outlier rejection:

- Clip `h_i` outside `[p5, p95]` **or**
- Drop points with `|rel_err| > 50%`.

### Automatic 2π–factor check

Compute `h_i` using ω and using f.

If `median(h_f) / median(h_omega) ~ 2 * pi` → raise a strong warning: **units mismatch**.

---

## D) Persistence / Artifacts

### New fields in proxies

Add:

- `f_ref`, `omega_ref`
- `delta_f`, `delta_omega`
- `peak_k`, `peak_delta`
- `mass_sim_gev = hbar_sim * omega_ref`
- (optional debug) `h_i` per run

### Store calibration

Write `data/processed/ola1/hbar_sim_calibration.json` with:

- `hbar_sim`, `units`, `n_used`, `n_rejected`
- percentiles of `h_i`
- criteria and parameters (`tol_cluster`, SNR, cutoffs, etc.)


----- NOTES:
Defaults propuestos
1) Corte/SNR del pico

Objetivo: elegir fundamental robusta sin meter heurística pesada.

omega_max_cutoff = 12.0 rad/s

skip_dc = True (siempre)

frac_of_max = 0.20 (20% del máximo dentro de la ventana baja)

SNR_min = 5.0 usando mag[k] / median(mag[1:K])

donde K es el índice del cutoff (bins hasta omega_max_cutoff), y median excluye DC.

peak_prominence_min: no lo implementes ahora (o setearlo None). Con SNR_min + frac_of_max alcanza y es más estable para este caso.

Regla práctica: en la banda baja 
0
<
𝜔
<
𝜔
𝑐
𝑢
𝑡
0<ω<ω
cut
	​

, elegís el primer pico que cumpla ambos:

mag[k] >= frac_of_max * max_mag_low

mag[k] / median_mag_low >= SNR_min

Si no hay ninguno, fallback al máximo en la banda baja (excepto DC).

2) Canal identidad (Q)

Sí: usar Q como canal identidad.

Si el FFT que guardás es per_mode: usar el canal que corresponde a la capa/modo Q (tu índice de Q).

Si por configuración no hay Q o no se registró ese canal:

fallback a power_total (o al canal con mayor energía en banda baja) pero manteniendo el filtro de baja frecuencia.

Esto evita que a veces uses un modo y otras veces otro (causa típica del “ħ loco”).

3) Ventana de búsqueda y DC

omega_max_cutoff = 12.0 rad/s explícito

skip_dc = True siempre (k=0 prohibido para selección e interpolación)

4) Cluster de ω para calibración

Te doy un método simple, determinista y con número:

Método preferido: “primer modo + ±10%”

Construís omega_ref de los runs calibrables.

Tomás omega0 = median del decile más bajo (p10) o directamente el mínimo robusto.

Te quedás con el cluster fundamental:

abs(omega_ref - omega0) / omega0 <= 0.10 (±10%)

Eso es mucho más fácil de implementar y menos frágil que “gap threshold”.

Si querés segunda opción por si no hay densidad:

gap grouping con gap_rel_threshold = 0.25 (25%) y tomás el primer grupo.

Pero yo iría con ±10% alrededor del primer modo.

5) Peso del weighted median

Sí, usá:

𝑞
𝑢
𝑎
𝑙
𝑖
𝑡
𝑦
_
𝑤
𝑒
𝑖
𝑔
ℎ
𝑡
=
𝑄
_
𝑙
𝑜
𝑐
𝑘
1
+
𝑑
_
𝑡
𝑜
𝑡
𝑎
𝑙
quality_weight=
1+d_total
Q_lock
	​


Q_lock = lock_quality.Q

d_total = distancia total del match (si no existe por run, poner 0 y queda solo Q)

Es razonable y suficientemente suave.

6) Outlier trimming

Preferencia:

Primero aplicar el cluster fundamental (esto ya elimina la mayoría de outliers “armónicos”).

Luego trimming suave:

clipear por percentiles: descartar h_i fuera de [p10, p90].

No usar el |rel_err|>50% como regla primaria porque depende de SM target; el trimming por percentiles es más “agnóstico” y no mete circularidad. Si querés una regla extra:

además descartar h_i <= 0.

7) Zero-padding / Hann

Mi recomendación: implementarlo ya, pero de manera simple:

Ventana: Hann

Zero-padding: 4×

No cambia nada aguas abajo y mejora la estabilidad del pico (menos leakage + mejor interpolación). Si te preocupa tocar demasiado, al menos Hann ya.

8) Persistencia de magnitudes vecinas

Guardar solo del canal seleccionado (Q) y solo lo necesario:

mag_km1, mag_k, mag_kp1

No hace falta por “canal”, solo por el canal identidad que usaste para omega_ref. Eso te da debug suficiente para ver si la interpolación está bien o si estás en borde.

Resumen de parámetros para hardcode

omega_max_cutoff = 12.0

skip_dc = True

frac_of_max = 0.20

SNR_min = 5.0 con median_mag_low = median(mag[1:K])

cluster_tol_rel = 0.10 (±10% alrededor de omega0)

quality_weight = Q_lock / (1 + d_total)

trim_percentiles = [10, 90]

FFT preproc: window = Hann, zero_pad_factor = 4

Persistir: mag_km1, mag_k, mag_kp1 (solo canal identidad)