# 1. DOFT axioms (v2)

## 1.1. Everything is oscillators with delays

The fundamental dynamics is described by coupled degrees of freedom \(x_i(t)\),  
with forces that depend on the present state and on its history.

## 1.2. Layered structure

For a “block” (proto-particle / proto-hadron) we use 3 effective internal layers:

- \(Q\): deep core (stiffest / most concentrated mode).
- \(S_1\): first structural mode (shape / density change at an intermediate scale).
- \(S_2\): internal collective mode (the “global lock” mode inside the block).

More layers (\(S_3\), etc.) are reserved for higher levels (atoms, nuclei).

## 1.3. Memory as a physical medium

The “vacuum” is NOT instantaneous or simple:

- it has multiple time scales (fast, medium, slow),
- it is nonlinear, and its response depends on the state of the system,
- it is coupled across layers (the history of \(Q\) affects \(S_2\), etc.).

## 1.4. Evolutionary waves

- **Wave 1 (Ola1):** forms simple blocks (effective mesons, constituent quarks, etc.).
- **Wave 2 (Ola2):** combines Wave-1 blocks into composite structures (baryons, light nuclei).

Between waves we apply a physical “natural selector” (locks, stability, spectral match).

---

# 2. State variables for a 3-layer block

Consider a block (one Ola1 unit). We define:

- Mechanical coordinates per layer:
  \[
  x_Q(t),\; x_{S1}(t),\; x_{S2}(t)
  \]

- Velocities:
  \[
  v_Q(t) = \dot{x}_Q(t),\quad
  v_{S1}(t) = \dot{x}_{S1}(t),\quad
  v_{S2}(t) = \dot{x}_{S2}(t)
  \]

- Mechanical parameters per layer \(\alpha \in \{Q, S1, S2\}\):

  - effective mass \(m_\alpha\),
  - bare frequency \(\omega_{0,\alpha}\),
  - local damping \(\gamma_\alpha\).

## 2.1. Multiscale memory

For each layer \(\alpha\) we introduce \(N_{\text{mem}}\) auxiliary variables
\(z_{\alpha,k}(t)\) that represent different memory scales \(\tau_{\alpha,k}\):

- index \(k \in \{1, \dots, N_{\text{mem}}\}\) (for example: fast, mid, slow).

Physical idea:

- \(z_{\alpha,1}\): fast memory (almost instantaneous response).
- \(z_{\alpha,2}\): intermediate memory.
- \(z_{\alpha,3}\): slow / long-tail memory.

---

# 3. Dynamics of a block – 3L DOFT with memory

## 3.1. Basic mechanical equations (without memory)

Before adding memory, the motion of each layer would be:

\[
m_\alpha \,\ddot{x}_\alpha(t)
+ m_\alpha \,\gamma_\alpha \,\dot{x}_\alpha(t)
+ m_\alpha \,\omega_{0,\alpha}^2 \,x_\alpha(t)
+ F_\alpha^{(\text{intra})}(t)
= 0
\]

where \(F_\alpha^{(\text{intra})}\) includes:

- couplings between layers (Q–S1, S1–S2, etc.) inside the block,
- small local nonlinear terms if we want them.

For example, a simple linear coupling:

\[
F_Q^{(\text{intra})}
= -k_{Q,S1}(x_Q - x_{S1})
\]

\[
F_{S1}^{(\text{intra})}
= -k_{Q,S1}(x_{S1} - x_Q)
  -k_{S1,S2}(x_{S1} - x_{S2})
\]

\[
F_{S2}^{(\text{intra})}
= -k_{S1,S2}(x_{S2} - x_{S1})
\]

This is the “skeleton” (no memory yet).

## 3.2. Memory architecture: multiscale + nonlinear + cross-coupled

### 3.2.1. Memory input per layer

The memory of a layer does not depend only on its own coordinate, but also on the other layers.
For each \(\alpha\) we define:

\[
\text{Input}_\alpha(t)
=
x_\alpha(t)
+ w_{\alpha\leftarrow Q}\, x_Q(t)
+ w_{\alpha\leftarrow S1}\, x_{S1}(t)
+ w_{\alpha\leftarrow S2}\, x_{S2}(t)
\]

The \(w_{\alpha\leftarrow\beta}\) are mixing coefficients (memory cross-couplings).

For example, for \(S2\):

\[
\text{Input}_{S2}
=
x_{S2}
+ w_{S2\leftarrow Q}\, x_Q
+ w_{S2\leftarrow S1}\, x_{S1}
\]

→ \(S2\) “feels” the history of Q and S1.

In compact form:

\[
\text{Input}(t) = W\,x(t)
\]

with \(W\) a \(3\times 3\) matrix.

### 3.2.2. Dynamics of memory modes \(z_{\alpha,k}\)

For each pair \((\alpha, k)\):

\[
\dot{z}_{\alpha,k}(t)
=
-\frac{1}{\tau_{\alpha,k}(E_\alpha)}\, z_{\alpha,k}(t)
+ a_{\alpha,k}\,\tanh\!\big(\beta_{\alpha,k}\,\text{Input}_\alpha(t)\big)
\]

where:

- \(\tau_{\alpha,k}(E_\alpha)\) is the memory time, which can depend on the local energy of the layer:

\[
E_\alpha(t)
=
\frac{1}{2} m_\alpha \dot{x}_\alpha^2
+
\frac{1}{2} m_\alpha \omega_{0,\alpha}^2 x_\alpha^2
+ \dots
\]

A simple and stable form is:

\[
\tau_{\alpha,k}(E_\alpha)
=
\tau_{\alpha,k}(0)\,\big(1 + \beta_{\alpha,k}^{(\tau)}\,E_\alpha\big),
\quad
\tau_{\alpha,k}(0) > 0,\;
\beta_{\alpha,k}^{(\tau)} \ge 0
\]

→ memory gets slower when the layer is highly excited (kind of “hardening”).

- \(a_{\alpha,k}\) controls how much of the signal enters the memory mode,
- \(\beta_{\alpha,k}\) controls the scale at which \(\tanh\) stops being linear.

Interpretation:

- For \(|\text{Input}|\) small: \(\tanh(\beta\,\text{Input}) \approx \beta\,\text{Input}\) → almost linear memory.
- For \(|\text{Input}|\) large: \(\tanh \to \pm 1\) → the medium saturates (maximum polarization capacity).

### 3.2.3. Memory force on each layer

We define the net memory force on \(\alpha\) as:

\[
F_\alpha^{(\text{mem})}(t)
=
\sum_{k=1}^{N_{\text{mem}}}
g_{\alpha,k}\, z_{\alpha,k}(t)
\]

The coefficients \(g_{\alpha,k}\) control how much each memory scale contributes to the effective force.

## 3.3. Full equation per layer (Ola1 block)

The dynamics of each layer \(\alpha \in \{Q, S1, S2\}\) of an Ola1 block is:

\[
m_\alpha \,\ddot{x}_\alpha(t)
+ m_\alpha \,\gamma_\alpha \,\dot{x}_\alpha(t)
+ m_\alpha \,\omega_{0,\alpha}^2 \,x_\alpha(t)
+ F_\alpha^{(\text{intra})}(t)
+ F_\alpha^{(\text{mem})}(t)
= 0
\]

with:

\[
F_\alpha^{(\text{mem})}(t)
=
\sum_k g_{\alpha,k}\, z_{\alpha,k}(t)
\]

and

\[
\dot{z}_{\alpha,k}(t)
=
-\frac{1}{\tau_{\alpha,k}(E_\alpha)}\, z_{\alpha,k}(t)
+ a_{\alpha,k}\,\tanh\!\big(\beta_{\alpha,k}\,\text{Input}_\alpha(t)\big)
\]

\[
\text{Input}_\alpha(t)
=
x_\alpha
+
\sum_\beta w_{\alpha\leftarrow\beta}\,x_\beta
\]

This is the DOFT v2 model for a 3-layer block with multiscale nonlinear memory and cross coupling.

---

# 4. Energy and “lock” per layer in Ola1

We want to measure “what percentage of the structure lives in Q, S1, S2”.

We define the energy per layer:

\[
E_\alpha(t)
=
E_\alpha^{(\text{mech})}(t)
+
E_\alpha^{(\text{mem})}(t)
\]

- Mechanical energy:

\[
E_\alpha^{(\text{mech})}
=
\frac{1}{2} m_\alpha \dot{x}_\alpha^2
+
\frac{1}{2} m_\alpha \omega_{0,\alpha}^2 x_\alpha^2
\]

(We can include intra-block coupling terms in the partition, but at the “lock” level this does not change the logic.)

- Memory-associated energy (optional and dependent on how you define it):

A simple effective form: proportional to \(z^2\):

\[
E_\alpha^{(\text{mem})}
=
\sum_k
\frac{1}{2}\,\kappa_{\alpha,k}\, z_{\alpha,k}^2
\]

Total structural energy of the block:

\[
E_{\text{struct}}
=
E_Q + E_{S1} + E_{S2}
\]

We define the fractions:

\[
R_Q
=
\frac{E_Q}{E_{\text{struct}}},\quad
R_{S1}
=
\frac{E_{S1}}{E_{\text{struct}}},\quad
R_{S2}
=
\frac{E_{S2}}{E_{\text{struct}}}
\]

And from there the lock qualities and layer states:

\[
\text{lock\_quality}_Q = R_Q,\quad \text{etc.}
\]

Structural “tier” classification (Ola1 block tier):

- **tier = none**: \(R_Q\) below the basic threshold.
- **tier = level1**: \(R_Q\) high, but \(R_{S1}, R_{S2}\) low.
- **tier = level2**: \(R_Q\) high, \(R_{S1}\) significant, \(R_{S2}\) still small.
- **tier = level3**: \(R_Q, R_{S1}, R_{S2}\) all above minimum thresholds → structurally “full” block.

State of S2 in Ola1:

- **none**: \(R_{S2} \approx 0\).
- **latent**: \(R_{S2}\) small but non-zero, and not dominant.
- **structural**: \(R_{S2}\) comparable to \(R_Q, R_{S1}\) and above a threshold.

This formalizes what you were already using, but now with memory included in the energy.

---

# 5. Ola2: compounds of 3L blocks

In Ola2, a compound (for example a baryon) is formed by combining \(N_B\) Ola1 blocks,
each with its own internal DOFT. Let:

- block index \(b = 1, \dots, N_B\),
- internal coordinates \(x_\alpha^{(b)}(t)\).

## 5.1. Couplings between blocks

In addition to the internal dynamics of each block, we introduce:

- “springs” between blocks, for example between \(S1\) layers or between effective “surfaces”:

\[
F_{\alpha,b}^{(\text{inter})}(t)
=
-\sum_{b' \ne b}
k_{b,b'}^{(\alpha)} \big( x_\alpha^{(b)} - x_\alpha^{(b')} \big)
\]

and, if desired, cross-block memory (optional but DOFT-consistent): variables
\(z_{(b,b'),k}^{(\text{inter})}\) that follow ODEs similar to the internal ones.

The equation for each layer \(\alpha\) in block \(b\) becomes:

\[
m_\alpha \,\ddot{x}_\alpha^{(b)}
+ m_\alpha \,\gamma_\alpha \,\dot{x}_\alpha^{(b)}
+ m_\alpha \,\omega_{0,\alpha}^2 x_\alpha^{(b)}
+ F_{\alpha,b}^{(\text{intra})}
+ F_{\alpha,b}^{(\text{mem})}
+ F_{\alpha,b}^{(\text{inter})}
= 0
\]

## 5.2. Compound energy and \(S2_{\text{compound}}\)

Total structural energy of the compound:

\[
E_{\text{struct}}^{(\text{comp})}
=
\sum_b \sum_{\alpha \in \{Q, S1, S2\}} E_\alpha^{(b)}
+ E^{(\text{inter})}
\]

where \(E^{(\text{inter})}\) contains the energy stored in inter-block links
(springs + cross-block memory if present).

We want to split this energy into three “bins” at compound level:

- \(E_Q^{(\text{comp})}\): energy associated with “hard internal” modes
  (fundamentally Q of each block).
- \(E_{S1}^{(\text{comp})}\): intermediate modes (internal shape changes and short-range
  block–block interactions).
- \(E_{S2}^{(\text{comp})}\): energy in truly collective modes:
  - oscillations where multiple blocks vibrate in correlated fashion,
  - more energy in “collective” links (inter-block) and in internal S2 layers.

A practical way to define this:

- Tag energy terms according to their role:
  - purely internal Q terms within each block → contribute to \(E_Q^{(\text{comp})}\),
  - intra-block Q–S1 and S1–S2 couplings → contribute to \(E_{S1}^{(\text{comp})}\),
  - inter-block couplings and inter-block memory → contribute to \(E_{S2}^{(\text{comp})}\).

Alternatively (more sophisticated):

- analyze normal modes of the compound and group them according to:
  - which coordinate combinations dominate,
  - what fraction of the total energy is localized in inter-block links.

Then define:

\[
R_Q^{(\text{comp})}
=
\frac{E_Q^{(\text{comp})}}{E_{\text{struct}}^{(\text{comp})}},\quad
R_{S1}^{(\text{comp})}
=
\frac{E_{S1}^{(\text{comp})}}{E_{\text{struct}}^{(\text{comp})}},\quad
R_{S2}^{(\text{comp})}
=
\frac{E_{S2}^{(\text{comp})}}{E_{\text{struct}}^{(\text{comp})}}
\]

And by analogy:

\[
\text{lock\_quality}_Q^{(\text{comp})} = R_Q^{(\text{comp})},\quad \text{etc.}
\]

- **tier\_compound**: none / level1 / level2 / level3 according to thresholds.

- **S2\_compound**:

  - none: \(R_{S2}^{(\text{comp})} \approx 0\).
  - latent: \(R_{S2}^{(\text{comp})}\) small but non-zero.
  - structural: \(R_{S2}^{(\text{comp})}\) above a threshold → the compound has a stable
    collective mode fed by the environment.

This formalizes exactly the idea:

- In Ola2, \(S2_{\text{compound}}\) is not a flag inherited from the blocks;
- it is a new collective mode that depends on how the blocks interact.

---

# 6. Spectral matching with the SM (Ola1 and Ola2)

For any of these systems (blocks or Ola2 compounds) we obtain an effective spectrum:

- peak energies \(E_i\) (in GeV),
- widths \(\Gamma_i\).

We define a match functional against an SM “target” (for example, pion, proton, etc.):

- target has levels \(\{ E_i^{(\text{exp})}, \Gamma_i^{(\text{exp})} \}\),
- the model yields levels \(\{ E_j^{(\text{mod})}, \Gamma_j^{(\text{mod})} \}\).

A distance of the form:

\[
d_{\text{spacing}}
=
\frac{1}{N_{\text{lev}}}
\sum_i
\big(\Delta E_i^{(\text{mod})} - \Delta E_i^{(\text{exp})}\big)^2
\]

\[
d_{\text{mass}}
=
\frac{1}{N_{\text{lev}}}
\sum_i
\big(E_i^{(\text{mod})} - E_i^{(\text{exp})}\big)^2
\]

\[
d_{\text{total}}
=
w_m\, d_{\text{mass}} + w_s\, d_{\text{spacing}}
\]

with physical / tunable thresholds:

- Ola1: \(d_{\text{total}} < d_{\text{meson}}\) → block is a candidate “effective meson”.
- Ola2: \(d_{\text{total}} < d_{\text{baryon}}\) → compound is a candidate baryon.

And labels of the form YES / POSSIBLE / NO according to \(d_{\text{total}}\) and tier\_compound.

---

# 7. Final physical reading

**Ola1 v2:**

- A 3L block (Q/S1/S2) with multiscale nonlinear memory and cross coupling.
- It can self-organize into pion-like, rho-like, quark-like states, etc.
- Internal S2 can be none / latent / structural depending on how the memory distributes energy.

**Ola2 v2:**

- Takes Ola1 blocks (a list of candidates with already-formed internal structure).
- Couples them via inter-block links (springs + extra memory if desired).
- Defines an \(S2_{\text{compound}}\) as a collective mode across blocks.
- Evaluates whether that compound:
  - has high tier\_compound (Q+S1+S2 lock),
  - and spectrally resembles an SM baryon / nucleus.

**Memory:**

- Represented by auxiliary variables \(z_{\alpha,k}\),
- multiscale (\(\tau_{\text{fast}}, \tau_{\text{mid}}, \tau_{\text{slow}}, \dots\)),
- nonlinear (\(\tanh\), \(\tau\) depending on energy),
- with mixing between layers (matrix \(W\)).
