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
