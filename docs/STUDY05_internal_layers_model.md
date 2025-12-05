# Study05 – Internal Side Layer Model

## 1. Model Layers in Study05 (Internal Side)

We fix a reference level:

- **Q level**: quark/hadron scale.

Order of magnitude:

- Energy:  
  \(E_Q \sim 1\,\text{GeV}\)
- Frequency:  
  \(f_Q \sim 2 \times 10^{23}\,\text{Hz}\)

For the model:

- \(f_Q \in [10^{23}, 10^{24}]\,\text{Hz}\)

You can keep this as a tunable parameter, but with this range as default.

**Internal layers** (deeper ⇒ HIGHER frequency):

- **S1**: string-like, just below the quark level.
- **S2**: deeper string-like layer.
- **S3**: optional, even deeper layer.

---

### 1.1. Compression Range per Layer

We define the compression ratio between a deeper and a shallower layer:

\[
R_{\text{layer}} = \frac{f_{\text{deep}}}{f_{\text{shallow}}}
\]

and constrain it to:

\[
10^2 \le R_{\text{layer}} \le 10^4
\]

This is the “golden rule” of Study05:  
**a single layer cannot change the frequency scale by more than 2–4 orders of magnitude.**

---

### 1.2. Case A – 2 Internal Layers (S1, S2)

Relations:

\[
f_{S1} = R_{S1\to Q} \cdot f_Q, 
\qquad
f_{S2} = R_{S2\to S1} \cdot f_{S1}
\]

with

\[
R_{S1\to Q},\; R_{S2\to S1} \in [10^2, 10^4]
\]

Then:

\[
f_{S1} \in [10^2, 10^4] \cdot f_Q
\]

\[
f_{S2} \in [10^4, 10^8] \cdot f_Q
\]

Using \(f_Q \sim 10^{23}–10^{24}\,\text{Hz}\), you get:

- \(f_{S1} \sim 10^{25}–10^{28}\,\text{Hz}\)
- \(f_{S2} \sim 10^{27}–10^{32}\,\text{Hz}\)

---

### 1.3. Case B – 3 Internal Layers (S1, S2, S3)

Relations:

\[
f_{S1} = R_{S1\to Q} \cdot f_Q, 
\qquad
f_{S2} = R_{S2\to S1} \cdot f_{S1},
\qquad
f_{S3} = R_{S3\to S2} \cdot f_{S2}
\]

with each \(R \in [10^2, 10^4]\).

Then:

\[
f_{S3} \in [10^6, 10^{12}] \cdot f_Q
\]

With \(f_Q \sim 10^{23}–10^{24}\,\text{Hz}\):

- \(f_{S1} \sim 10^{25}–10^{28}\,\text{Hz}\)
- \(f_{S2} \sim 10^{27}–10^{32}\,\text{Hz}\)
- \(f_{S3} \sim 10^{29}–10^{36}\,\text{Hz}\)

This is still well below the **Planck frequency** (~\(10^{42}\,\text{Hz}\)), so you are not violating anything “obvious”.

---

## 2. Mathematical Core of the Model (Oscillators + Memory)

### 2.1. Base Equation for Each Mode

A mode \(x_{L,i}(t)\) in layer  
\(L \in \{S3, S2, S1, Q\}\) obeys:

\[
m_{L,i} \, \ddot x_{L,i}
+ 2\gamma_{L,i} \, \dot x_{L,i}
+ \omega_{L,i}^2 \, x_{L,i}
+ \sum_j K_{L,ij} (x_{L,i} - x_{L,j})
+ \sum_{L' < L} \sum_k C_{L \leftarrow L'}(i,k)\, x_{L',k}(t - \tau_{L'L})
= 0
\]

where:

- \(\omega_{L,i} \sim 2\pi f_{L,i}\) is centered on the frequency scale of layer \(L\)  
  (base frequency of the layer + small shifts),
- \(K_{L,ij}\): couplings **within the same layer** (string-like),
- \(C_{L \leftarrow L'}(i,k)\): coupling **between layers** (from deeper \(L'\) to more shallow \(L\)),
- \(\tau_{L'L}\): typical delay between those layers.

---

### 2.2. Memory / Kernel Representation

Instead of writing memory explicitly as an integral, we represent it via **additional internal modes** (approximating the kernel as a sum of exponentials).  
For each inter-layer coupling \(L' \to L\):

\[
\text{response} \sim 
\sum_{a=1}^{M_{L'L}} 
A_{L'L}(a) \, e^{-t / \tau_{L'L}(a)}
\]

Each pair \((A, \tau)\) counts as **one memory degree of freedom**.

---

## 3. Complexity Index \(C\)

We define:

\[
C = 
\underbrace{\sum_L N_L}_{\text{explicit modes}}
+
\underbrace{\sum_{L',L} M_{L'L}}_{\text{memory modes}}
\]

Study05 design rule:

\[
C \le 8 \quad (\text{or at most } 10)
\]

Examples:

- **Simple case**:

  - \(N_{S1} = 3,\; N_{S2} = 2,\; N_Q = 1\), no S3,
  - total memory modes \(M_\text{mem} = 2\).

  Then:

  \[
  C = 3 + 2 + 1 + 2 = 8 \quad \Rightarrow \text{valid}
  \]

- **Overly complex case** (\(C > 10\)) → discarded in the search.

This directly encodes your requirement of “few effective degrees of freedom” into the engine.

---

## 4. Structure: String-Like per Internal Layer

For each internal layer \(S_k\):

- Assume a **1D discrete string** of \(N_{S_k}\) modes:

  - \(N_{S_k}\) between 3 and 7 (limits complexity),
  - connected only to neighbors (chain graph).

**Parameters:**

- \[
  \omega_{S_k, i} = \omega_{S_k} (1 + \delta_i)
  \]

  where \(\omega_{S_k}\) is the base frequency of the layer and \(|\delta_i| \le 0.1\) are small variations.

- \(K_{S_k}\): neighbor–neighbor coupling  
  (same value for the whole chain in v0.1).

Diagonalizing this yields a family of modes:

\[
\Omega_{S_k, n} \approx \Omega_{S_k} \cdot f(n, N_{S_k}, K_{S_k})
\]

These are your internal string-like harmonics.

---

### Lock Between Layers (Rational Condition)

Between layers, a pair of modes \((L', n')\) and \((L, n)\) is considered a **lock candidate** if:

\[
\left|
\frac{\Omega_{L', n'}}{\Omega_{L, n}} - \frac{p}{q}
\right|
< \varepsilon
\]

with:

- \(p, q \le 7\) (small primes 2, 3, 5, 7 and simple products),
- \(\varepsilon \sim 10^{-2}\) or \(10^{-3}\) (v0.1 tolerance).

This is where DOFT injects its “primes + integer/ fractional locks” without exploding the search space.

---

## 5. Scan (Search) – What the Simulator Actually Runs

### 5.1. Parameters to Scan

For each configuration (2 or 3 internal layers):

**Layers / base frequencies:**

- Choose \(f_Q\) (or a discrete range within \([10^{23}, 10^{24}]\,Hz\)).
- Choose \(R_{\text{layer}}\) for each jump (uniform in log-space over \([10^2, 10^4]\)).
- Derive \(f_{S1}, f_{S2}, f_{S3}\) according to Case A/B.

**Per-layer structure:**

- \(N_{S_k} \in \{3,4,5,6,7\}\).
- \(K_{S_k}\) in a reasonable range (e.g. in units such that \(0.1 \le K_{S_k}/m_{S_k} \le 10\)).
- Small offsets \(\delta_i\), e.g. uniform in \([-0.1, 0.1]\).

**Memory:**

For each deep→shallow coupling (S2→S1, S1→Q, S3→S2 if present):

- Choose \(M_{L'L} \in \{0,1,2\}\)  
  (controlled via the complexity \(C\)).
- Set \(\tau_{L'L}^{(a)} \sim \alpha/\omega_{L'}\) with \(\alpha \in [0.1, 10]\)  
  (order of \(1/\omega\) or its multiples).
- Amplitudes \(A_{L'L}^{(a)}\) in a small range (controls memory weight).

**Complexity filter:**

- If computed \(C > 8\) (or 10), discard the configuration **without simulating**.

---

### 5.2. What Each Run Produces

For each accepted configuration:

- Compute the **effective mode spectrum** at the Q level  
  (after coupling S1, S2, S3 + memory).

From that spectrum, extract:

- Dominant frequencies → effective masses (\(m = \hbar \omega / c^2\)).
- Number and spacing of resonances (for comparison with hadronic spectra).
- Pattern of mode **Q factors** (which modes have long lifetime vs die quickly).

---

## 6. Checks Against Physical Data (Q / Hadron Level)

In v0.1, without yet touching superconductors, Study05 checks could include:

1. **Resonance spacing**

   - You want Q-level modes separated in energy by ~0.5–1 GeV  
     (right order for light baryon/meson resonances).

2. **Number of relevant modes in a band**

   - In a given range (e.g. 0–3 GeV), how many modes with high Q appear?  
   - It should be of the same order as in the particle tables  
     (not 1, not 10⁶).

3. **Regge-like trajectories (optional v0.1)**

   - In an extended version, you can assign an “effective spin” to modes  
     (not detailed here),
   - and look for an approximately linear relation **J vs m²** for  
     modes connected along the string.

4. **Consistency with “no visible quark substructure”**

   - The effective size of the mode distribution at Q  
     (something like \(\Delta x\) of the dominant mode) must be  
     \(\le 10^{-19}\,\text{m}\) so as not to violate scattering constraints.
   - This gives a bound on how \(f_{S_k}\), couplings, and memory  
     can combine.

