
# 1. Theoretical Framework of Physical Observables in DOFT

## 1.1. Internal Energy \(E_{\text{DOFT}}\)

In DOFT, what is “real” at the micro level is a system of coupled oscillators with memory. The internal energy of the system is defined as:

$$
E_{\text{DOFT}}(t)
=
\sum_{\text{modes}}
\left(
\tfrac{1}{2} m v^2
+
\tfrac{1}{2} m \omega_{\text{eff}}^2 x^2
\right)
+
\sum_{\text{mem}}
\tfrac{1}{2} \kappa z^2
$$

where:

- \(x, v\): position and velocity of the mode,  
- \(m\): effective mass of the mode (normalized),  
- \(\omega_{\text{eff}}^2 = \omega_0^2 (1 + \varepsilon_\omega b_{\text{layer}})\): effective frequency with layer corrections,  
- \(z\): auxiliary memory variables with stiffness \(\kappa\).

This holds both for Wave 1 and for a future mechanical Wave 2: the Hamiltonian is the same, only the system size changes (more modes, more couplings).

What is used as a physical observable is the energy of the final attractor, not of the transient:

$$
E_{\text{internal}}
=
\langle
E_{\text{DOFT}}(t)
\rangle_{\text{late window}}
$$

That is, the time average of \(E_{\text{DOFT}}(t)\) over the tail of the simulation (when the lock has already stabilized).

## 1.2. Physical Mass \(m_{\text{phys}}\) and Calibration

The oscillator theory gives energy in internal units. To compare it with experimental physics (GeV) we only need a single global calibration:

1. Choose a Wave 1 block that already matches a Standard Model (SM) particle very well (reference block).  
2. Take its internal energy \(E_{\text{DOFT}}^{(\text{ref})}\).  
3. Require that this configuration represents the experimental mass \(m_{\text{ref}}\) (for example, the \(\eta'\) or another particle with grade A match).

This defines a global factor:

$$
K
=
\frac{m_{\text{ref}}}{E_{\text{DOFT}}^{(\text{ref})}}.
$$

From that point on:

- Physical mass of any block / compound:

$$
m_{\text{phys}} = K \cdot E_{\text{DOFT}}.
$$

The empirical energy that is compared with SM / nuclear data is always this \(m_{\text{phys}}\).

Internal energy and physical mass thus become:

- \(E_{\text{DOFT}}\): the “natural” magnitude of the engine.  
- \(m_{\text{phys}}\): the same magnitude converted to GeV with a single constant \(K\) fixed in Wave 1.

## 1.3. Size / Structural Dimension

Since there is no explicit space, “size” is represented by:

**Wave 1 blocks (bricks):**

- How many layers / modes are active (Q, S1, S2).  
- How the energy is distributed among layers → `participation_entropy`, `layer_energy_fraction`.  

This gives a measure of the internal complexity of the block.

**Wave 2 compounds (nuclei / clusters):**

- Number of blocks \(N\) in the cluster.  
- Graph structure (template): diameter in block hops, average degree.  

This gives a measure of topological size (how “large” the object is in terms of how many bricks it has and how they are connected).

These parameters act as an analogue of “radius” / “dimension” without introducing explicit spatial coordinates.

## 1.4. Order, Chaos, and “Age”

DOFT treats “time” as a sequence of changes toward more ordered lock patterns, up to the point where the system can no longer sustain the lock (it “gets tired” and falls).

The order/chaos observables are:

### In Wave 1 (blocks)

- **`participation_entropy`**: participation entropy of layers/modes (how much energy is distributed among Q/S1/S2).  
  - Low → concentrated lock, more order.  
  - High → distributed lock, more “structural chaos”.

- **`layer_energy_fraction`** → lets you reconstruct directly the Q/S1/S2 mixture.

### In Wave 2 (Kuramoto)

All entropy/chaos is measured on the phase dynamics \(\theta_i(t)\) via \(R(t)\):

$$
R(t)
=
\left|
\frac{1}{N}
\sum_j e^{i \theta_j(t)}
\right|
$$

(global phase coherence).

From this series \(R(t)\), we define:

- **`PE_tick_norm`**: permutation entropy of the series \(R(t)\) (\(m = 5, \tau = 1\)).  
  → Measures temporal chaos of global order:
  - low PE → regular \(R(t)\) (simple attractor),  
  - high PE → irregular \(R(t)\) (more chaotic dynamics).

- **`phase_var_lastW`**: mean variance of \(\Delta\theta_{ij}\) in the last window \(W\) (\(W \approx 20\) ticks).  
  → Phase dispersion in the final state:
  - low variance → phases well aligned (strong lock),  
  - high variance → poor synchrony.

- **`R_mean_lastW`, `R_final`**:  
  → Mean and final coherence. \(R \approx 1\) indicates a well-defined global lock.

- **`H_lock_mean` / `entropy_quality`**:  
  - `H_lock_mean`: normalized entropy of the Q/S1/S2 proportions at block level (average over blocks).  
  - `entropy_quality = 1 - H_lock_mean`:
    - close to 1 → energy well concentrated in few layers → “structured” lock.  
    - close to 0 → energy spread out → “diffuse” lock.

- **`memory_score_k10`**:  

  $$
  \text{memory\_score\_k10}
  = 1 - \frac{\text{MSE of } R(t) \text{ at 1 tick}}{\text{MSE at 10 ticks}}
  $$

  A persistence heuristic: how much the order dynamics “remembers” its recent state.

**Current Wave 2 success criterion:**

- enough ticks,  
- \(R_{\text{mean\_lastW}} > 0.85\),  
- \(\text{phase\_var\_lastW} < 0.02\),  
- and \(R_{\text{final}} > 0.90\).

If not, the compound is classified as `no_lock` or `insufficient_ticks`.

These observables are the third physical axis: at equal mass and size, a state can be “younger/more ordered” or “older/more chaotic” depending on its structural and dynamical entropy.

## 2. Technical Summary for Implementation

### 2.1. Wave 1 – Internal Energy and Mass

#### Internal Energy of a Run

In the Wave 1 integrator (`engine_core3`) we have \(E_{\text{DOFT}}(t)\) per step (already used for stability).

Define:

- \(t_{\max}\): total run time (from the engine).

Averaging window: \([0.75\, t_{\max},\, t_{\max}]\).

In discrete form: the last ~25% of steps.

Accumulate:

- `sum_E_internal_window` and `n_E_internal_window`  
  starting when \(t \ge 0.75\, t_{\max}\).

At the end of the run:

$$
E_{\text{internal}} = \frac{\text{sum\_E\_internal\_window}}{\text{n\_E\_internal\_window}}.
$$

This value is written to `Ola1_3-2-5_all_runs_proxies.csv` as column `E_internal` (internal units).

#### Promotion to Blocks (`simple_blocks.json`)

Each block keeps its `origin_run_id`.

When promoting, we copy:

```json
"internal_energy": E_internal  // DOFT units
```

from the corresponding run.

#### Calibration with the SM

- Read `simple_blocks.json` and `sm_universe.json`.  
- Build the candidate set for the reference block:

  1. First, blocks with `grade == "A"` and `has_enough_levels_full == true`.  
  2. If empty, downgrade to `grade == "B"` with the same condition.  
  3. If still empty → calibration error.

- Among the candidates:

  - pick the one with smallest `match_score.d_total`,  
  - break ties by `block_id` (lexicographic order).

For the reference block:

- `E_internal_ref = internal_energy`.  
- `particle_name_ref = particle_name` of the block.

In `sm_universe`:

- If it has `sm_mass_gev`, use that as `m_ref_gev`.  
- If it has no `sm_mass_gev` but has `masses_gev`, take the average of `masses_gev`.  
- If it has neither → error.

Define the global constant:

$$
K = \frac{m_{\text{ref\_gev}}}{E_{\text{internal\_ref}}}.
$$

Generate a calibration JSON, e.g. `data/processed/ola1-chaos/energy_calibration.json`, with:

```json
{
  "reference_block_id": "...",
  "reference_particle_name": "...",
  "E_internal_ref": ...,
  "m_ref_gev": ...,
  "scale_K": ...,
  "metadata": {
    "criteria": "...",
    "timestamp": "...",
    "sm_universe_source": "..."
  }
}
```

#### Propagation to Blocks

Optionally, enrich `simple_blocks.json` by adding:

```json
"mass_gev": K * internal_energy
```

`mass_gev` is the value that Wave 2 and the matching code should use as the default physical mass.

### 2.2. Size / Structural Observables

#### Wave 1 Blocks

Continue using the existing fields:

- `layer_energy_fraction` (Q/S1/S2),  
- `participation_entropy`.

These are the standard measure of internal structural complexity of the block.

#### Wave 2 Compounds

From the graph (template + edges):

- `node_count`: number of blocks in the compound.  
- `graph_diameter`: maximum length (in block hops) of the shortest path between two nodes.  
- `mean_degree`: average node degree.

These three fields, added to `compounds.json`, summarize the topological size of the compound.

### 2.3. Order/Chaos Observables (Wave 1 + Wave 2)

#### Wave 1 (Blocks)

- `participation_entropy` is already computed and stored in `simple_blocks.json`.  
- It is considered the basic structural entropy of the block (how distributed the energy is among layers).

#### Wave 2 (Kuramoto Phase Simulator)

On the integration of \(\theta_i(t)\):

- At each tick compute:

$$
R(t) =
\left|
\frac{1}{N}
\sum_j e^{i \theta_j(t)}
\right|.
$$

Series and metrics:

- `PE_tick_norm`: permutation entropy of the series \(R(t)\) with parameters (\(m = 5, \tau = 1\)).  
  → Main metric of “temporal chaos”.

- `phase_var_lastW`: mean variance of \(\Delta\theta_{ij}\) in the last window \(W\) (default \(W = 20\) ticks).  
  → Phase dispersion at the end.

- `R_mean_lastW`: average of \(R(t)\) in the last window \(W\).  
- `R_final`: final value of \(R(t)\).

- `QualityLock`: average `lock_quality.Q` of the blocks used (if available).  

- `H_lock_mean`: normalized entropy of the Q/S1/S2 mixture per block;  
  `entropy_quality = 1 - H_lock_mean`.

- `memory_score_k10`: as defined above.

#### Current “Successful Lock” Condition in Wave 2

We use as success condition:

- enough ticks,  
- `R_mean_lastW > 0.85`,  
- `phase_var_lastW < 0.02`,  
- and `R_final > 0.90`.

If these are not satisfied, the compound is labeled `no_lock` or `insufficient_ticks` and is not considered a stable state.

These fields are already being computed and written to `compounds.json`; in the theoretical framework they are fixed as the standard order/chaos observables for DOFT in the Kuramoto phase.

---

With this, the foundations of physical variables are fixed:

- A unique internal energy (oscillator + memory Hamiltonian).  
- Physical mass via a single global calibration in Wave 1.  
- Structural size via internal block complexity + cluster topology.  
- Order/chaos via structural entropy (Wave 1) and \(R(t)\)/permutation-entropy metrics (Wave 2).
