# 3. Tuning the Model for Better Low-Energy Structure

## 3.1. Increasing Mode Density in 0–3 GeV

**Goal:**  
Per run, have several modes in the band (at least 3–4) so that it actually makes sense to talk about spacings and locks.

Three direct changes:

### 3.1.1. Always Rescale the Hamiltonian *A Posteriori*

**Current behavior (likely):**  
You calibrate the scale so that one Q-mode lands near ~2 GeV.

**Simple proposal:**

1. Build the full dynamical matrix (no band cuts).
2. Compute all positive eigenvalues → \(\{E_i\}\).
3. Choose a reference index \(k\) (e.g. the softest nonzero mode or the median of the lowest 3 modes).
4. Compute
   \[
   s = \frac{E_{\text{target}}}{E_k}, \quad E_{\text{target}} \approx 2.0~\text{GeV}.
   \]
5. Rescale the stiffness (or equivalent) as:
   - \(K \to K \cdot (E_{\text{target}} / E_k)^2\)  
     (or the equivalent operation in your code).

This forces one specific mode to sit around 2 GeV, but leaves freedom for other modes to fall into \([0, 3]\) GeV if the topology allows it.

---

### 3.1.2. Narrow the Ranges of \(R_{S1\_Q}\) and \(R_{S2\_S1}\)

Right now they are in \(10^2\)–\(10^4\), which is extremely large.

To see structure, I would try something like:

- \(R_{S1\_Q} \in [5, 50]\)
- \(R_{S2\_S1} \in [5, 50]\)

This is still hierarchical (internal layers are faster) but not so extreme that it flattens all the modes.

---

### 3.1.3. Temporarily Increase `band-max` in the Exploration Phase

Set, temporarily:

- `--band-max` = 5.0 or even 10.0.

First, look at **how many modes in total** fall below 10 GeV per run.

Once you see that you already have 3–5 soft modes per run, then you can refocus on the [0, 3] GeV window.

---

## 3.2. Forcing Real Mixing Across Layers (DOFT Locks)

**Goal:**  
Make sure soft modes are not “pure Q”, but actual combinations of Q + S1 (+ S2).

### 3.2.1. Reduce Internal Stiffness of S1/S2

In your current construction, the natural frequencies of S1 and S2 probably end up enormous because of those large \(R\) factors.

Redefine something like this (in dimensionless units):

- \(\omega_Q = \omega_0\)
- \(\omega_{S1} = \omega_0 \cdot \alpha^{-1}\) with \(\alpha \approx 2–5\)
- \(\omega_{S2} = \omega_0 \cdot \beta^{-1}\) with \(\beta \approx 5–20\)

This keeps the internal layers at higher frequencies than Q, but not absurdly high.

---

### 3.2.2. Couplings Between Layers of the Same Order as Diagonals

Make sure coupling terms \(K_{Q\,S1}\), \(K_{S1\,S2}\) are **\(\mathcal{O}(\omega^2)\)**, not \(\mathcal{O}(10^4 \omega^2)\).

If you work with a global coupling parameter `g_couple`, I would start with:

- \(g_{\text{couple}} \in [0.2, 3]\).

---

### 3.2.3. Add Mild Disorder Within Each Layer

If each node in Q is identical and each node in S1 is identical, the matrix has a lot of symmetry → degeneracies.

Break that with a 1–5% multiplicative jitter in:

- the diagonal terms, and
- the intra-layer couplings.

This should:

- Spread out the eigenvalues.
- Turn the histogram of \(\Delta E\) from “a spike at 0” into something more **Wigner–Dyson–like** (level repulsion).

---

### 3.2.4. Check Layer Participation per Energy Bin

You already have the layer–mode heatmap.

Use it to look, in bins of e.g. 0.2 GeV, at the **average weight per layer**. The target pattern is:

- In the 1–3 GeV band, non-trivial weights in Q + S1 (+ S2).

If all the S1/S2 weight always sits in modes above 10 GeV, the system is still too stiff.

---

## 3.3. Delays / Memory: Next Level

What you have now (`memory_terms = 6`) already gives a polynomial in \(\omega\) that distorts the modes, but it doesn’t seem to generate interesting locks; with this parametrization everything flows into hard modes except one.

The version “faithful to DOFT” would be:

For each physical oscillator \(x_i\), add memory variables \(y_i^{(k)}\) with equations like:

\[
m \, \ddot x
+ k_x x
+ \sum_k c_k (x - y_k)
+ \sum_j K_{ij} (x - x_j)
= 0
\]

\[
\tau_k \, \dot y_k + y_k = x
\]

In frequency space, this introduces a self-energy with memory:

\[
\Sigma(\omega) \propto \sum_k \frac{c_k}{1 + i\,\omega\,\tau_k}.
\]

**Practically, right now:**

I would use memory to **further soften** the hard modes:

- Choose \(\tau_k\) so that they introduce secondary resonance peaks in the 1–10 GeV region.

But I wouldn’t touch this until you first achieve:

1. At least one soft mode per run.
2. Non-trivial S1 weight in the 0–3 GeV band.
