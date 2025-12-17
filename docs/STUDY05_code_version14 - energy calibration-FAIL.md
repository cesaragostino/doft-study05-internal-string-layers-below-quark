# 1. What we will call “energy calibration” in DOFT

In the mechanical wave1/wave2 scheme:

DOFT has a well-defined internal energy:

```math
E_\text{DOFT} =
\sum_{\text{modes}} \left(\tfrac{1}{2} m v^2 + \tfrac{1}{2} m \omega_\text{eff}^2 x^2 \right)
\;+\;
\sum_{\text{mem}} \tfrac{1}{2} \kappa z^2
```

This is in internal units (dimensionless for the engine).

What is missing is how that unit is translated into GeV.

The calibration you want is:

- Choose a wave1 block that already matches a Standard Model particle very well.
- Use its internal energy as a “reference” and require that this configuration has the experimental mass of its SM particle.
- This fixes a global factor \(K\) such that

```math
E_\text{physical} = K \cdot E_\text{DOFT}.
```

From that point on, all DOFT masses and energies are read in GeV with the same rule, in all waves.

---

# 2. Automatic choice of the reference block in wave1

With the data you uploaded, if I look at `simple_blocks.json`, the block that currently has the best global match is:

- `block_id`: `eta_prime_block_0065`  
- `particle_name`: `"eta_prime"`  
- `family`: `"eta_prime_like"`  
- `grade`: `"A"`  
- `match_score.d_total`: ≈ 0.02  
- `match_score.has_enough_levels_full`: `True`  

That is: wave1 has already constructed a block that looks very much like the SM \(\eta'\) (eta-prime).

In `sm_universe.json` the entry for that particle is:

```text
{
  "name": "eta_prime",
  "family": "eta_prime_like",
  "type": "meson",
  "sm_mass_gev": 0.95778,
  "masses_gev": [0.958],
  ...
}
```

In design terms:

**Reference block selection criterion:**

- Use only blocks with `grade == "A"`,
- `has_enough_levels_full == True`,
- choose the one with the smallest `d_total` among those.

The `particle_name` of that block tells you which entry of `sm_universe` to use.

The experimental reference mass is `sm_mass_gev` from that entry.

In the current repo state, this gives exactly the block `eta_prime_block_0065` with SM mass ≈ 0.958 GeV. But the logic is general: if tomorrow there is another grade A block with better `d_total`, the reference changes automatically.

---

# 3. How to define the internal energy of each block

To be able to define \(K\), each wave1 block needs a scalar number
\(E_\text{DOFT}(i)\) representing its internal energy.

I propose something consistent with the mechanics and not with the “third peak” trick:

For each wave1 run:

- The engine is already computing \(E_\text{DOFT}(t)\) at each step
  (because it uses it for stability, layers, etc.).
- It is enough to store a time average over a window where the lock is already stable:

```math
\bar{E}_\text{DOFT} =
\frac{1}{T} \int_{t_0}^{t_0 + T} E_\text{DOFT}(t)\, dt
```

or, in discrete form, an average over the last \(N\) steps.

This \(\bar{E}_\text{DOFT}\) is the “energy level of the attractor” for that run.

When that run is promoted to a `simple_block`, that value is copied (or recomputed) and stored as, for example,
`internal_energy` or `E_doft`.

From a code point of view:

- The natural place to introduce this calculation is wave1 post-processing
  (where proxies are computed today and runs are decorated for `simple_blocks`).
- `Ola1_3-2-5_all_runs_proxies.csv` can have a new column, for instance `E_internal`, with that mean.
- `simple_blocks.json` adds a field `internal_energy` copied from there.

Theoretically this is clean: that energy comes directly from the oscillator + memory Hamiltonian, without any rescaling.

---

# 4. Definition of the calibration constant \(K\)

Once:

- You already have `internal_energy` for each wave1 block,
- You have chosen the reference block \(B_\text{ref}\) (by the criterion of best `d_total` and grade A),
- And you know the experimental mass `sm_mass_gev` of its associated SM particle,

the calibration is:

**Internal energy of the reference block:**

```math
E_\text{DOFT}(\text{ref}) = \text{internal\_energy}(B_\text{ref})
```

**Physical reference mass:**

```math
m_\text{ref} = \text{sm\_mass\_gev}(\text{particle\_name}(B_\text{ref}))
```

**Global constant:**

```math
K = \frac{m_\text{ref}}{E_\text{DOFT}(\text{ref})}
```

For any block (or mechanical wave2 compound) with internal energy \(E_\text{DOFT}(i)\), the physical mass is:

```math
m_i^\text{(phys)} = K \cdot E_\text{DOFT}(i)
```

This can be implemented as a small module that:

- Reads `simple_blocks.json` + `sm_universe.json`,
- Finds the reference block,
- Computes \(K\),
- And writes it into some global config, for example a JSON like:

```text
{
  "energy_calibration": {
    "reference_block_id": "eta_prime_block_0065",
    "reference_particle": "eta_prime",
    "E_internal_ref": 0.XXX,
    "m_ref_gev": 0.95778,
    "scale_K": 0.95778 / 0.XXX
  }
}
```

and optionally:

- Iterates again over `simple_blocks.json` and adds a property
  `mass_gev = K * internal_energy` to each block.

From then on, mechanical wave2 can read `mass_gev` directly from the blocks without inventing anything.

---

# 5. How this “propagates” to mechanical wave2

With this calibration in wave1:

Each wave1 brick carries:

- Its `internal_energy` (DOFT units),
- Its `mass_gev = K * internal_energy`.

Mechanical wave2, when building a structure (compound):

- Knows the mass of each input block in GeV,
- Simulates the large oscillator system (blocks + couplings),
- Also computes its global internal energy \(E_\text{internal, compound}\) with exactly the same formula as wave1 (time average of the Hamiltonian),
- Converts to mass:

```math
m_\text{compound}^\text{(phys)} =
K \cdot E_\text{DOFT}(\text{compound})
```

The binding energy is simply:

```math
E_\text{bind} =
\left( \sum m_\text{blocks}^\text{(phys)} \right)
- m_\text{compound}^\text{(phys)}
```

without inventing new formulas.

There is no more “magic peak”, no more “2 GeV per run”, no
\(\gamma \sum M R_\text{final}\): everything rests on ONE definition
of internal energy + ONE calibration in wave1.

---

# 6. What is explicit for the programmer

Summarized as a design (not as a task list):

- The single source of truth for energy is always the mechanical + memory energy
  that is already computed in wave1.
- Wave1 must expose, for each run, a scalar energy `internal_energy`
  (time average over the stationary regime).
- `simple_blocks.json` must include that value for each block.
- A small calibration module on top of wave1:
  - Inspects `simple_blocks.json`,
  - Chooses the reference block with best `grade == "A"` and smallest `d_total`,
  - Gets from `sm_universe.json` the `sm_mass_gev` corresponding to its `particle_name`,
  - Computes the global constant \(K\),
  - Stores it (and, if desired, writes `mass_gev` into each block).
- Mechanical wave2 uses the same internal energy formula and the same constant \(K\)
  to derive physical masses and binding energies.

With this:

- Calibration stays localized in wave1, as you wanted,
- It is anchored to the particle you are currently generating with best quality
  (currently `eta_prime_block_0065`),
- And it can be propagated to the rest of the architecture without adding
  a new “magic parameter” in each wave.
