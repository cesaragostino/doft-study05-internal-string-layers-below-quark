# DOFT Wave 3 (Ola3) – Compound Synthesis Report

## 1. Executive Summary: The Combinatorial Wall

### Main Finding
Evaluation of DOFT engine's capacity to sustain phase coherence in compound structures from $N=2$ to $N=12$ nodes reveals:

- ✅ **Robust coherence emerges for $N \le 4$** (Dimer, Trimer, Tetrahedron)
- ⚠️ **Abrupt combinatorial wall at $N=12$** (Icosahedron - flat assembly)

### Critical Verdict
The model scales physically (binding energy grows with complexity), but synthesis of heavy structures requires **Hierarchical Modularity (Alpha-Clusters)** rather than combinatorial brute force.

## 2. Synthesis Targets & Success Rates

| Target | N (Nodes) | Runs | Success (%) | QualityLock (Avg) | Phase Var ($\sigma^2$) | Notes |
|--------|-----------|------|-------------|-------------------|------------------------|-------|
| **Dimer** | 2 | 1,000 | **74.50%** | 0.936 | 0.000321 | |
| **Trimer** | 3 | 2,000 | **44.15%** | 0.935 | 0.000354 | |
| **Tetrahedron** | 4 | 2,000 | **24.55%** | 0.939 | 0.000373 | |
| **Icosahedron** | 12 | 5,000 | **0.22%** | 0.930 | 0.000478 | |

### Decay Law Discovery

$${\text{Success}}(N) = \exp(0.92 -0.59N), \quad R^2 = 1.000$$

## 3. Emergent Observables: Mass & Binding Energy

| Structure | Mass/Node (GeV) | Binding (% of total) | Notes |
|-----------|-----------------|----------------------|-------|
| **Dimer** | 0.390 | 0.64% | |
| **Trimer** | 0.388 | 0.63% | |
| **Tetrahedron** | 0.396 | 0.63% | |
| **Icosahedron** | 0.398 | 0.60% | |

## 4. Kuramoto Signatures: Universal Phase Coherence

| Metric | Dimer | Trimer | Tetra | Icosahedron |
|--------|-------|--------|-------|-------------|
| Phase Var < 0.001 | 100.0% | 100.0% | 100.0% | 100.0% |
| R > 0.95 | 85.9% | 66.4% | 52.7% | 9.1% |
| R > 0.98 | 61.5% | 33.6% | 16.1% | 0.0% |

## 5. Memory Score Analysis & Bug Discovery

| Structure | Pre-Fix | Post-Fix | Change |
|-----------|---------|----------|--------|
| Dimer | n/a | 0.289 | n/a |
| Trimer | n/a | 0.579 | n/a |
| Tetrahedron | n/a | 0.659 | n/a |
| Icosahedron | n/a | 0.835 | n/a |

## 6. Dynamical Health Check: Chaos vs Order

- **Dimer** zombies: 33.20%
- **Trimer** zombies: 38.95%
- **Tetrahedron** zombies: 52.80%
- **Icosahedron** zombies: 59.54%
