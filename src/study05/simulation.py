"""Dynamic simulator with structural breathing, memory, and FFT-based spectra."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple
import math

import numpy as np

from .couplings import Coupling, InterLayerCoupling
from .layers import Layer, Mode, make_index_map


@dataclass
class StructuralParams:
    tau_e: Dict[Layer, float]
    tau_b: Dict[Layer, float]
    alpha_b: Dict[Layer, float]
    e_ref: Dict[Layer, float]


@dataclass
class SimulationState:
    x: np.ndarray
    v: np.ndarray
    z: np.ndarray
    b: np.ndarray  # per-layer
    e: np.ndarray  # per-layer


@dataclass
class LayerMemoryParams:
    tau0: np.ndarray
    beta_tau: np.ndarray
    a: np.ndarray
    beta: np.ndarray
    g: np.ndarray
    kappa: np.ndarray


@dataclass
class MemoryArchitecture:
    layer_order: List[Layer]
    layer_mem: Dict[Layer, LayerMemoryParams]
    W: np.ndarray  # shape (L, L) aligned with layer_order
    mem_index: Dict[Tuple[Layer, int], int]  # (layer, k) -> global z index


@dataclass
class AdaptiveLockPair:
    name: str
    i_idx: int
    j_idx: int
    p: int
    q: int
    weight: float
    omega_i_init: float = 0.0
    omega_j_init: float = 0.0
    k_adapt: float = 0.0
    sum_cos: float = 0.0
    sum_sin: float = 0.0
    n_samples: int = 0
    L_last: float = 0.0
    L_sin_last: float = 0.0
    phi_last: float = 0.0
    omega_updates: int = 0
    omega_update_applied: bool = False
    delta_omega_i_last: float = 0.0
    delta_omega_j_last: float = 0.0
    omega_i_before: float = 0.0
    omega_j_before: float = 0.0
    omega_i_after: float = 0.0
    omega_j_after: float = 0.0
    clamp_i: str = "none"
    clamp_j: str = "none"


@dataclass
class AdaptiveLockConfig:
    enabled: bool
    window_cycles: float
    ref_layer: Layer
    ref_mode: int
    epsilon_K: float
    lambda_K: float
    L0: float
    K_min: float
    K_max: float
    K_gate: float
    epsilon_omega: float
    omega_min: float
    omega_max: float
    lock_threshold_L: float
    lock_ratio_tol: float
    pairs: List[AdaptiveLockPair]


@dataclass
class MemoryLink:
    deep_idx: int
    shallow_idx: int
    tau0: float
    amp0: float
    g0: float
    deep_layer: Layer
    shallow_layer: Layer


@dataclass
class DirectLink:
    deep_idx: int
    shallow_idx: int
    g0: float
    deep_layer: Layer
    shallow_layer: Layer


@dataclass
class SimulationParams:
    dt: float = 0.0025
    total_steps: int = 12000
    transient_frac: float = 0.3
    sample_stride: int = 5
    eps_omega: float = 0.1
    eps_k: float = 0.1
    eps_tau: float = 0.1
    eps_amp: float = 0.1
    peak_threshold: float = 0.05
    max_peaks: int = 30
    structural_peak_cap: int = 12
    max_x: float = 1e3
    max_v: float = 1e3
    max_energy: float = 1e6
    max_abs_z: float = 1e6
    energy_blowup_factor: float = 1e8
    clamp_tanh_arg: float = 5.0


def _layer_order(layers: Sequence[Layer]) -> List[Layer]:
    ordered = []
    for l in (Layer.Q, Layer.S1, Layer.S2, Layer.S3):
        if l in layers and l not in ordered:
            ordered.append(l)
    return ordered


def _layer_indices(modes: List[Mode]) -> Dict[Layer, List[int]]:
    idx: Dict[Layer, List[int]] = {}
    for i, m in enumerate(modes):
        idx.setdefault(m.layer, []).append(i)
    return idx


def _layer_ref_omega(modes: List[Mode], layer: Layer) -> float:
    omegas = [m.omega0 for m in modes if m.layer == layer]
    if not omegas:
        return 1.0
    return float(np.median(omegas))


def _build_memory_architecture(
    modes: List[Mode],
    rng: np.random.Generator,
    memory_cfg: Dict[str, object] | None = None,
) -> MemoryArchitecture:
    """Construct per-layer memory parameters following v2 spec (4/3/4 modes and mixing W).

    memory_cfg overrides defaults when provided. Supported keys:
      - modes_per_layer: {"Q": int, "S1": int, "S2": int}
      - tau0: {"Q": [...], "S1": [...], "S2": [...]}  # in units of 1/omega_Q
      - beta_tau: {"Q": [min, max], ...}
      - beta: {"Q": [min, max], ...}
      - a: {"Q": [...], ...}
      - g_xi: {"Q": [min, max], ...}  # scaling of m*omega^2
      - mixing_ranges: {"S2<-Q": [lo, hi], ...}
    """
    memory_cfg = memory_cfg or {}
    layers_present = _layer_order([m.layer for m in modes if m.layer in (Layer.Q, Layer.S1, Layer.S2)])
    layer_mem: Dict[Layer, LayerMemoryParams] = {}
    mem_index: Dict[Tuple[Layer, int], int] = {}

    base_tau_default = {
        Layer.Q: [0.02, 0.05, 0.2, 1.0],
        Layer.S1: [0.05, 0.2, 1.0],
        Layer.S2: [0.1, 0.5, 2.0, 8.0],
    }
    base_a_default = [0.9, 0.7, 0.5, 0.35]
    beta_tau_ranges_default = {Layer.Q: (0.05, 0.1), Layer.S1: (0.05, 0.1), Layer.S2: (0.2, 0.3)}
    beta_ranges_default = {Layer.Q: (2.0, 3.0), Layer.S1: (2.0, 3.0), Layer.S2: (1.0, 2.0)}
    xi_ranges_default = {Layer.Q: (0.1, 0.3), Layer.S1: (0.1, 0.3), Layer.S2: (0.1, 0.5)}

    modes_per_layer_cfg = memory_cfg.get("modes_per_layer", {})
    tau0_cfg = memory_cfg.get("tau0", {})
    beta_tau_cfg = memory_cfg.get("beta_tau", {})
    beta_cfg = memory_cfg.get("beta", {})
    a_cfg = memory_cfg.get("a", {})
    g_xi_cfg = memory_cfg.get("g_xi", {})

    omega_q_ref = _layer_ref_omega(modes, Layer.Q)
    z_counter = 0
    for layer in layers_present:
        if layer.name in tau0_cfg:
            taus_base = tau0_cfg[layer.name]
        elif layer in tau0_cfg:
            taus_base = tau0_cfg[layer]
        else:
            taus_base = base_tau_default.get(layer, [])
            n_override = None
            if layer.name in modes_per_layer_cfg:
                n_override = modes_per_layer_cfg[layer.name]
            elif layer in modes_per_layer_cfg:
                n_override = modes_per_layer_cfg[layer]
            if n_override is not None:
                n_override = int(n_override)
                if n_override < len(taus_base):
                    taus_base = taus_base[:n_override]
                elif n_override > len(taus_base):
                    if taus_base:
                        taus_base = taus_base + [taus_base[-1]] * (n_override - len(taus_base))
                    else:
                        taus_base = [0.1] * n_override
        n_mem = len(taus_base)
        if n_mem == 0:
            continue
        tau0 = np.array([t / max(omega_q_ref, 1e-6) for t in taus_base])
        if layer.name in beta_tau_cfg:
            beta_tau_lo, beta_tau_hi = beta_tau_cfg[layer.name]
        elif layer in beta_tau_cfg:
            beta_tau_lo, beta_tau_hi = beta_tau_cfg[layer]
        else:
            beta_tau_lo, beta_tau_hi = beta_tau_ranges_default.get(layer, (0.05, 0.1))
        beta_tau = rng.uniform(beta_tau_lo, beta_tau_hi, size=n_mem)
        if layer.name in beta_cfg:
            beta_lo, beta_hi = beta_cfg[layer.name]
        elif layer in beta_cfg:
            beta_lo, beta_hi = beta_cfg[layer]
        else:
            beta_lo, beta_hi = beta_ranges_default.get(layer, (2.0, 3.0))
        beta = rng.uniform(beta_lo, beta_hi, size=n_mem)
        if layer.name in a_cfg:
            a_list = a_cfg[layer.name]
        elif layer in a_cfg:
            a_list = a_cfg[layer]
        else:
            a_list = base_a_default
        a = np.array(a_list[:n_mem] + [a_list[-1]] * max(0, n_mem - len(a_list)))
        if layer.name in g_xi_cfg:
            xi_lo, xi_hi = g_xi_cfg[layer.name]
        elif layer in g_xi_cfg:
            xi_lo, xi_hi = g_xi_cfg[layer]
        else:
            xi_lo, xi_hi = xi_ranges_default.get(layer, (0.1, 0.3))
        omega_ref = _layer_ref_omega(modes, layer)
        mass_ref = np.mean([m.mass for m in modes if m.layer == layer]) if any(m.layer == layer for m in modes) else 1.0
        g = rng.uniform(xi_lo, xi_hi, size=n_mem) * mass_ref * (omega_ref**2)
        kappa = g / np.maximum(a, 1e-12)

        for k in range(n_mem):
            mem_index[(layer, k)] = z_counter
            z_counter += 1
        layer_mem[layer] = LayerMemoryParams(
            tau0=tau0, beta_tau=beta_tau, a=a, beta=beta, g=g, kappa=kappa
        )

    ranges_default = {
        (Layer.S2, Layer.Q): (0.2, 0.4),
        (Layer.S2, Layer.S1): (0.2, 0.4),
        (Layer.S1, Layer.Q): (0.1, 0.3),
        (Layer.Q, Layer.S1): (0.05, 0.15),
        (Layer.Q, Layer.S2): (0.05, 0.1),
        (Layer.S1, Layer.S2): (0.1, 0.2),
    }
    mixing_cfg = memory_cfg.get("mixing_ranges", {})
    L = len(layers_present)
    W = np.eye(L)
    for i, layer_i in enumerate(layers_present):
        for j, layer_j in enumerate(layers_present):
            if i == j:
                continue
            key = f"{layer_i.name}<-{layer_j.name}"
            if key in mixing_cfg:
                lo, hi = mixing_cfg[key]
            elif (layer_i, layer_j) in ranges_default:
                lo, hi = ranges_default[(layer_i, layer_j)]
            else:
                lo = hi = None
            if lo is None or hi is None:
                W[i, j] = 0.0
            else:
                W[i, j] = rng.uniform(lo, hi)

    return MemoryArchitecture(layer_order=layers_present, layer_mem=layer_mem, W=W, mem_index=mem_index)


def _build_adaptive_lock_config(
    modes: List[Mode],
    index_map: Dict[Tuple[Layer, int], int],
    cfg: Dict[str, object] | None,
) -> AdaptiveLockConfig | None:
    if not cfg or not cfg.get("enabled", False):
        return None
    try:
        ref_layer = Layer[cfg.get("ref_frequency_layer", "Q")]
    except Exception:
        ref_layer = Layer.Q
    ref_mode = int(cfg.get("ref_mode_index", 0))
    pairs_cfg = cfg.get("lock_pairs", [])
    pairs: List[AdaptiveLockPair] = []
    for pc in pairs_cfg:
        try:
            li = Layer[pc.get("layer_i")]
            lj = Layer[pc.get("layer_j")]
        except Exception:
            continue
        mi = int(pc.get("mode_i", 0))
        mj = int(pc.get("mode_j", 0))
        name = pc.get("name", f"{li.name}_{lj.name}_{mi}_{mj}")
        p = int(pc.get("p", 1))
        q = int(pc.get("q", 1))
        weight = float(pc.get("weight", 1.0))
        if (li, mi) not in index_map or (lj, mj) not in index_map:
            continue
        pairs.append(
            AdaptiveLockPair(
                name=name,
                i_idx=index_map[(li, mi)],
                j_idx=index_map[(lj, mj)],
                p=p,
                q=q,
                weight=weight,
                k_adapt=0.0,
                omega_i_init=modes[index_map[(li, mi)]].omega0,
                omega_j_init=modes[index_map[(lj, mj)]].omega0,
            )
        )
    return AdaptiveLockConfig(
        enabled=True,
        window_cycles=float(cfg.get("window_cycles", 20.0)),
        ref_layer=ref_layer,
        ref_mode=ref_mode,
        epsilon_K=float(cfg.get("epsilon_K", 1e-3)),
        lambda_K=float(cfg.get("lambda_K", 1e-3)),
        L0=float(cfg.get("L0", 0.2)),
        K_min=float(cfg.get("K_min", 0.0)),
        K_max=float(cfg.get("K_max", 5.0)),
        K_gate=float(cfg.get("K_gate", 1e-2)),
        epsilon_omega=float(cfg.get("epsilon_omega", 1e-4)),
        omega_min=float(cfg.get("omega_min", 0.1)),
        omega_max=float(cfg.get("omega_max", 5.0)),
        lock_threshold_L=float(cfg.get("lock_threshold_L", 0.8)),
        lock_ratio_tol=float(cfg.get("lock_ratio_tol", 0.1)),
        pairs=pairs,
    )


def build_links(
    inter_couplings: List[InterLayerCoupling],
    index_map: Dict[Tuple[Layer, int], int],
) -> Tuple[List[MemoryLink], List[DirectLink]]:
    mem_links: List[MemoryLink] = []
    direct_links: List[DirectLink] = []
    for ic in inter_couplings:
        for (i_deep, j_sh), kernel in ic.links.items():
            deep_idx = index_map[(ic.deep_layer, i_deep)]
            sh_idx = index_map[(ic.shallow_layer, j_sh)]
            direct_links.append(
                DirectLink(
                    deep_idx=deep_idx,
                    shallow_idx=sh_idx,
                    g0=ic.g0,
                    deep_layer=ic.deep_layer,
                    shallow_layer=ic.shallow_layer,
                )
            )
            for tau0, amp0 in zip(kernel.taus0, kernel.amps0):
                mem_links.append(
                    MemoryLink(
                        deep_idx=deep_idx,
                        shallow_idx=sh_idx,
                        tau0=tau0,
                        amp0=amp0,
                        g0=ic.g0,
                        deep_layer=ic.deep_layer,
                        shallow_layer=ic.shallow_layer,
                    )
                )
    return mem_links, direct_links


def init_structural_params(layers: List[Layer], rng: np.random.Generator) -> StructuralParams:
    tau_e = {}
    tau_b = {}
    alpha_b = {}
    e_ref = {}
    for layer in layers:
        tau_e[layer] = float(rng.uniform(50.0, 200.0))
        tau_b[layer] = float(rng.uniform(200.0, 800.0))
        alpha_b[layer] = float(rng.uniform(0.01, 0.1))
        e_ref[layer] = 0.0
    return StructuralParams(tau_e=tau_e, tau_b=tau_b, alpha_b=alpha_b, e_ref=e_ref)


def init_state(
    modes: List[Mode],
    inter_couplings: List[InterLayerCoupling],
    struct_params: StructuralParams,
    rng: np.random.Generator,
    memory_cfg: Dict[str, object] | None = None,
) -> Tuple[SimulationState, Dict[Layer, int], MemoryArchitecture, List[DirectLink], Dict[Layer, List[int]]]:
    index_map = make_index_map(modes)
    layers_present = _layer_order([m.layer for m in modes])
    layer_to_idx = {layer: i for i, layer in enumerate(layers_present)}
    mem_arch = _build_memory_architecture(modes, rng, memory_cfg=memory_cfg)
    _, direct_links = build_links(inter_couplings, index_map)

    x0 = rng.normal(scale=1e-3, size=len(modes))
    v0 = rng.normal(scale=1e-3, size=len(modes))
    z0 = np.zeros(len(mem_arch.mem_index))
    b0 = np.zeros(len(layers_present))
    e0 = np.zeros(len(layers_present))

    state = SimulationState(x=x0, v=v0, z=z0, b=b0, e=e0)
    energies = compute_layer_energies(modes, state, layer_to_idx, eps_omega=0.1)
    for layer, val in energies.items():
        idx = layer_to_idx[layer]
        state.e[idx] = val
        struct_params.e_ref[layer] = val
    layer_indices = _layer_indices(modes)
    return state, layer_to_idx, mem_arch, direct_links, layer_indices


def compute_layer_energies(
    modes: List[Mode],
    state: SimulationState,
    layer_to_idx: Dict[Layer, int],
    eps_omega: float,
    mem_energy_by_layer: Dict[Layer, float] | None = None,
) -> Dict[Layer, float]:
    energies: Dict[Layer, float] = {layer: 0.0 for layer in layer_to_idx}
    for p, m in enumerate(modes):
        layer = m.layer
        b_idx = layer_to_idx[layer]
        bL = state.b[b_idx]
        omega_eff2 = m.omega0**2 * (1.0 + eps_omega * bL)
        energies[layer] += 0.5 * m.mass * state.v[p] ** 2 + 0.5 * m.mass * omega_eff2 * state.x[p] ** 2
    if mem_energy_by_layer:
        for layer, e_mem in mem_energy_by_layer.items():
            if layer in energies:
                energies[layer] += e_mem
    return energies


def _numeric_intra(intra_couplings: List[Coupling], index_map: Dict[Tuple[Layer, int], int]):
    pairs = []
    for c in intra_couplings:
        pairs.append((index_map[c.i], index_map[c.j], c.k_ij0, c.i[0]))
    return pairs


def derivatives(
    modes: List[Mode],
    intra_pairs: List[Tuple[int, int, float, Layer]],
    mem_arch: MemoryArchitecture,
    direct_links: List[DirectLink],
    struct_params: StructuralParams,
    layer_to_idx: Dict[Layer, int],
    layer_indices: Dict[Layer, List[int]],
    state: SimulationState,
    sim_params: SimulationParams,
    adapt_pairs: List[AdaptiveLockPair] | None = None,
) -> SimulationState:
    dx = np.zeros_like(state.x)
    dv = np.zeros_like(state.v)
    dz = np.zeros_like(state.z)
    db = np.zeros_like(state.b)
    de = np.zeros_like(state.e)

    dx[:] = state.v

    # base frequency/damping forces
    for p, m in enumerate(modes):
        b_idx = layer_to_idx[m.layer]
        bL = state.b[b_idx]
        omega_eff2 = m.omega0**2 * (1.0 + sim_params.eps_omega * bL)
        dv[p] += -omega_eff2 * state.x[p] - m.gamma * state.v[p]

    # intra-layer springs
    for i_idx, j_idx, k0, layer in intra_pairs:
        b_idx = layer_to_idx[layer]
        bL = state.b[b_idx]
        k_eff = k0 * (1.0 + sim_params.eps_k * bL)
        dv[i_idx] += -k_eff * (state.x[i_idx] - state.x[j_idx]) / modes[i_idx].mass
        dv[j_idx] += -k_eff * (state.x[j_idx] - state.x[i_idx]) / modes[j_idx].mass

    # direct inter-layer coupling (spring-like)
    for link in direct_links:
        b_idx = layer_to_idx[link.shallow_layer]
        bL = state.b[b_idx]
        g_eff = link.g0 * (1.0 + sim_params.eps_k * bL)
        dv[link.shallow_idx] += -g_eff * (state.x[link.shallow_idx] - state.x[link.deep_idx]) / modes[
            link.shallow_idx
        ].mass
        dv[link.deep_idx] += -g_eff * (state.x[link.deep_idx] - state.x[link.shallow_idx]) / modes[
            link.deep_idx
        ].mass

    # adaptive springs
    if adapt_pairs:
        for pair in adapt_pairs:
            k_adapt = pair.k_adapt
            if k_adapt == 0.0:
                continue
            i = pair.i_idx
            j = pair.j_idx
            dv[i] += -k_adapt * (state.x[i] - state.x[j]) / modes[i].mass
            dv[j] += -k_adapt * (state.x[j] - state.x[i]) / modes[j].mass

    # memory contributions per layer
    mem_energy_by_layer: Dict[Layer, float] = {}
    for (layer, k), idx_z in mem_arch.mem_index.items():
        params = mem_arch.layer_mem.get(layer)
        if params is None:
            continue
        mem_energy_by_layer[layer] = mem_energy_by_layer.get(layer, 0.0) + 0.5 * params.kappa[k] * state.z[idx_z] ** 2

    inst_energy = compute_layer_energies(
        modes, state, layer_to_idx, sim_params.eps_omega, mem_energy_by_layer=mem_energy_by_layer
    )

    # layer signals and inputs
    signals = {layer: float(np.mean([state.x[i] for i in layer_indices.get(layer, [])])) for layer in layer_indices}
    signals_vec = np.array([signals.get(layer, 0.0) for layer in mem_arch.layer_order])
    input_vec = mem_arch.W @ signals_vec if signals_vec.size else np.array([])
    input_by_layer = {layer: input_vec[i] for i, layer in enumerate(mem_arch.layer_order)} if input_vec.size else {}

    mem_force: Dict[Layer, float] = {}
    for layer, params in mem_arch.layer_mem.items():
        if layer not in layer_indices:
            continue
        energy_layer = inst_energy.get(layer, 0.0)
        input_layer = input_by_layer.get(layer, 0.0)
        for k in range(len(params.tau0)):
            idx_z = mem_arch.mem_index[(layer, k)]
            tau_eff = params.tau0[k] * (1.0 + params.beta_tau[k] * energy_layer)
            tau_eff = max(tau_eff, 1e-9)
            u = params.beta[k] * input_layer
            u_clamped = float(np.clip(u, -sim_params.clamp_tanh_arg, sim_params.clamp_tanh_arg))
            dz[idx_z] = -state.z[idx_z] / tau_eff + params.a[k] * np.tanh(u_clamped)
            mem_force[layer] = mem_force.get(layer, 0.0) + params.g[k] * state.z[idx_z]

    for layer, force in mem_force.items():
        for idx in layer_indices.get(layer, []):
            dv[idx] += -force / modes[idx].mass

    # structural updates
    for layer, idx in layer_to_idx.items():
        tau_e = struct_params.tau_e[layer]
        tau_b = struct_params.tau_b[layer]
        alpha_b = struct_params.alpha_b[layer]
        e_ref = struct_params.e_ref[layer]
        de[idx] = (inst_energy[layer] - state.e[idx]) / tau_e
        db[idx] = (-state.b[idx] + alpha_b * (state.e[idx] - e_ref)) / tau_b

    return SimulationState(x=dx, v=dv, z=dz, b=db, e=de)


def rk4_step(
    state: SimulationState,
    deriv_fn,
    dt: float,
) -> SimulationState:
    k1 = deriv_fn(state)
    k2 = deriv_fn(_state_add(state, k1, dt * 0.5))
    k3 = deriv_fn(_state_add(state, k2, dt * 0.5))
    k4 = deriv_fn(_state_add(state, k3, dt))

    new_x = state.x + dt / 6.0 * (k1.x + 2 * k2.x + 2 * k3.x + k4.x)
    new_v = state.v + dt / 6.0 * (k1.v + 2 * k2.v + 2 * k3.v + k4.v)
    new_z = state.z + dt / 6.0 * (k1.z + 2 * k2.z + 2 * k3.z + k4.z)
    new_b = state.b + dt / 6.0 * (k1.b + 2 * k2.b + 2 * k3.b + k4.b)
    new_e = state.e + dt / 6.0 * (k1.e + 2 * k2.e + 2 * k3.e + k4.e)

    return SimulationState(x=new_x, v=new_v, z=new_z, b=new_b, e=new_e)


def _state_add(base: SimulationState, delta: SimulationState, scale: float) -> SimulationState:
    return SimulationState(
        x=base.x + scale * delta.x,
        v=base.v + scale * delta.v,
        z=base.z + scale * delta.z,
        b=base.b + scale * delta.b,
        e=base.e + scale * delta.e,
    )


def simulate(
    modes: List[Mode],
    intra_couplings: List[Coupling],
    inter_couplings: List[InterLayerCoupling],
    sim_params: SimulationParams,
    rng: np.random.Generator,
    debug: bool = False,
    memory_cfg: Dict[str, object] | None = None,
    adaptive_cfg: Dict[str, object] | None = None,
):
    if memory_cfg:
        clamp_val = memory_cfg.get("clamp_tanh_arg")
        if clamp_val is not None:
            sim_params.clamp_tanh_arg = float(clamp_val)
        max_abs_z = memory_cfg.get("max_abs_z")
        if max_abs_z is not None:
            sim_params.max_abs_z = float(max_abs_z)
        energy_blowup = memory_cfg.get("energy_blowup_factor")
        if energy_blowup is not None:
            sim_params.energy_blowup_factor = float(energy_blowup)

    index_map = make_index_map(modes)
    struct_params = init_structural_params(_layer_order([m.layer for m in modes]), rng)
    state, layer_to_idx, mem_arch, direct_links, layer_indices = init_state(
        modes, inter_couplings, struct_params, rng, memory_cfg=memory_cfg
    )
    adaptive_conf = _build_adaptive_lock_config(modes, index_map, adaptive_cfg)
    intra_pairs = _numeric_intra(intra_couplings, index_map)

    omega_max = max(m.omega0 for m in modes) if modes else 1.0
    dt = min(sim_params.dt, 0.05 / omega_max)
    total_steps = sim_params.total_steps
    transient_steps = int(sim_params.transient_frac * total_steps)

    samples_x = []
    samples_time = []
    samples_b = []
    samples_e = []
    debug_inputs = []
    debug_tau = []
    debug_z = []

    # reference energy for blow-up detection
    def _mem_energy():
        mem_energy_by_layer: Dict[Layer, float] = {}
        for (layer, k), idx_z in mem_arch.mem_index.items():
            params = mem_arch.layer_mem.get(layer)
            if params is None:
                continue
            mem_energy_by_layer[layer] = mem_energy_by_layer.get(layer, 0.0) + 0.5 * params.kappa[k] * state.z[idx_z] ** 2
        return mem_energy_by_layer

    init_mem_energy = _mem_energy()
    init_energy = compute_layer_energies(modes, state, layer_to_idx, sim_params.eps_omega, mem_energy_by_layer=init_mem_energy)
    energy_ref_total = sum(init_energy.values()) if init_energy else 1.0

    adapt_pairs = adaptive_conf.pairs if adaptive_conf and adaptive_conf.enabled else None

    def deriv(current_state: SimulationState) -> SimulationState:
        return derivatives(
            modes,
            intra_pairs,
            mem_arch,
            direct_links,
            struct_params,
            layer_to_idx,
            layer_indices,
            current_state,
            sim_params,
            adapt_pairs=adapt_pairs,
        )

    # adaptive lock runtime
    if adaptive_conf and adaptive_conf.enabled:
        ref_idx = index_map.get((adaptive_conf.ref_layer, adaptive_conf.ref_mode), 0)
        omega_ref = modes[ref_idx].omega0 if ref_idx < len(modes) else 1.0
        window_duration = adaptive_conf.window_cycles * (2 * np.pi) / max(omega_ref, 1e-8)
        window_start = 0.0
    else:
        ref_idx = 0
        window_duration = float("inf")
        window_start = 0.0

    for step in range(total_steps):
        state = rk4_step(state, deriv, dt)

        # adaptive lock accumulation
        if adapt_pairs:
            for pair in adapt_pairs:
                x_i = state.x[pair.i_idx]
                v_i = state.v[pair.i_idx]
                omega_i = modes[pair.i_idx].omega0
                x_j = state.x[pair.j_idx]
                v_j = state.v[pair.j_idx]
                omega_j = modes[pair.j_idx].omega0
                phi_i = math.atan2(v_i / max(omega_i, 1e-9), x_i)
                phi_j = math.atan2(v_j / max(omega_j, 1e-9), x_j)
                theta = pair.p * phi_j - pair.q * phi_i
                pair.sum_cos += math.cos(theta)
                pair.sum_sin += math.sin(theta)
                pair.n_samples += 1

        # stability checks
        if not (np.isfinite(state.x).all() and np.isfinite(state.v).all() and np.isfinite(state.z).all()):
            raise FloatingPointError("non-finite state")
        if np.any(np.abs(state.x) > sim_params.max_x) or np.any(np.abs(state.v) > sim_params.max_v):
            raise FloatingPointError("state blow-up")
        if np.any(np.abs(state.z) > sim_params.max_abs_z):
            raise FloatingPointError("memory blow-up")

        mem_energy = _mem_energy()
        inst_energy = compute_layer_energies(
            modes, state, layer_to_idx, sim_params.eps_omega, mem_energy_by_layer=mem_energy
        )
        if any(val > sim_params.max_energy for val in inst_energy.values()):
            raise FloatingPointError("energy blow-up")
        total_e = sum(inst_energy.values())
        if total_e > sim_params.energy_blowup_factor * max(energy_ref_total, 1e-12):
            raise FloatingPointError("energy runaway")

        if step >= transient_steps and (step - transient_steps) % sim_params.sample_stride == 0:
            samples_time.append((step + 1) * dt)
            samples_x.append(state.x.copy())
            samples_b.append(state.b.copy())
            # keep per-layer energies for entropy/chaos metrics
            energy_vec = [inst_energy.get(layer, 0.0) for layer in layer_to_idx.keys()]
            samples_e.append(energy_vec)
            if debug:
                signals = {layer: float(np.mean([state.x[i] for i in layer_indices.get(layer, [])])) for layer in layer_indices}
                sig_vec = np.array([signals.get(layer, 0.0) for layer in mem_arch.layer_order])
                inp_vec = mem_arch.W @ sig_vec if sig_vec.size else np.array([])
                debug_inputs.append(inp_vec.copy())
                tau_snapshot = []
                for layer in mem_arch.layer_order:
                    params = mem_arch.layer_mem.get(layer)
                    if params is None:
                        continue
                    energy_layer = inst_energy.get(layer, 0.0)
                    tau_layer = params.tau0 * (1.0 + params.beta_tau * energy_layer)
                    tau_snapshot.append(tau_layer)
                debug_tau.append(tau_snapshot)
                debug_z.append(state.z.copy())

        # window update for adaptive lock
        current_time = (step + 1) * dt
        if adapt_pairs and (current_time - window_start) >= window_duration:
            # compute averages and update K and omega
            avg_sin_by_mode: Dict[int, float] = {}
            for pair in adapt_pairs:
                pair.omega_update_applied = False
                pair.delta_omega_i_last = 0.0
                pair.delta_omega_j_last = 0.0
                if pair.n_samples > 0:
                    L_cos = pair.sum_cos / pair.n_samples
                    L_sin = pair.sum_sin / pair.n_samples
                else:
                    L_cos = 0.0
                    L_sin = 0.0
                L_mag = math.sqrt(L_cos * L_cos + L_sin * L_sin)
                pair.L_last = L_mag
                pair.L_sin_last = L_sin
                pair.phi_last = math.atan2(L_sin, L_cos)
                dK = adaptive_conf.epsilon_K * (L_mag - adaptive_conf.L0) - adaptive_conf.lambda_K * pair.k_adapt
                pair.k_adapt = float(np.clip(pair.k_adapt + dK, adaptive_conf.K_min, adaptive_conf.K_max))
                # accumulate omega adjustments only if there is meaningful lock and coupling developed
                if L_mag > adaptive_conf.L0 and pair.k_adapt > adaptive_conf.K_gate:
                    delta_i = -adaptive_conf.epsilon_omega * pair.weight * L_sin * pair.q
                    delta_j = adaptive_conf.epsilon_omega * pair.weight * L_sin * pair.p
                    avg_sin_by_mode[pair.i_idx] = avg_sin_by_mode.get(pair.i_idx, 0.0) + delta_i
                    avg_sin_by_mode[pair.j_idx] = avg_sin_by_mode.get(pair.j_idx, 0.0) + delta_j
                    pair.delta_omega_i_last = delta_i
                    pair.delta_omega_j_last = delta_j
                else:
                    pair.omega_update_applied = False
                    continue
                # reset accumulators
                pair.sum_cos = 0.0
                pair.sum_sin = 0.0
                pair.n_samples = 0

            for idx, delta in avg_sin_by_mode.items():
                base_omega = modes[idx].omega0
                delta_cap = 0.05 * max(abs(base_omega), 1e-6)
                delta = float(np.clip(delta, -delta_cap, delta_cap))
                raw_omega = base_omega + delta
                new_omega = float(np.clip(raw_omega, adaptive_conf.omega_min, adaptive_conf.omega_max))
                modes[idx].omega0 = new_omega
                clamp_flag = "none"
                if new_omega <= adaptive_conf.omega_min + 1e-12:
                    clamp_flag = "min"
                elif new_omega >= adaptive_conf.omega_max - 1e-12:
                    clamp_flag = "max"
                # mark updates for pairs involving this mode
                for pair in adapt_pairs:
                    if pair.i_idx == idx or pair.j_idx == idx:
                        pair.omega_updates += 1
                        pair.omega_update_applied = True
                        if pair.i_idx == idx:
                            pair.omega_i_before = base_omega
                            pair.omega_i_after = new_omega
                            pair.delta_omega_i_last = delta
                            pair.clamp_i = clamp_flag
                        if pair.j_idx == idx:
                            pair.omega_j_before = base_omega
                            pair.omega_j_after = new_omega
                            pair.delta_omega_j_last = delta
                            pair.clamp_j = clamp_flag

            # recompute window based on current ref omega
            omega_ref = modes[ref_idx].omega0 if ref_idx < len(modes) else 1.0
            window_duration = adaptive_conf.window_cycles * (2 * np.pi) / max(omega_ref, 1e-8)
            window_start = current_time

    samples_x = np.array(samples_x)  # shape (T, N)
    samples_b = np.array(samples_b) if samples_b else np.empty((0, len(state.b)))
    samples_e = np.array(samples_e) if samples_e else np.empty((0, len(state.b)))
    times = np.array(samples_time)

    spectrum = compute_fft_spectrum(samples_x, dt * sim_params.sample_stride)

    # downsample traces for storage
    if samples_b.shape[0] > 300:
        stride = max(1, samples_b.shape[0] // 200)
        samples_b = samples_b[::stride]
        samples_e = samples_e[::stride] if samples_e.size else samples_e
        times = times[::stride]

    result = {
        "times": times,
        "b_series": samples_b,
        "energies_series": samples_e,
        "spectrum": spectrum,
        "layer_to_idx": layer_to_idx,
        "dt_used": dt,
    }
    if adapt_pairs:
        pairs_out = []
        for pair in adapt_pairs:
            omega_i_raw = modes[pair.i_idx].omega0
            omega_j_raw = modes[pair.j_idx].omega0
            omega_i = float(np.clip(omega_i_raw, adaptive_conf.omega_min, adaptive_conf.omega_max))
            omega_j = float(np.clip(omega_j_raw, adaptive_conf.omega_min, adaptive_conf.omega_max))
            ratio = omega_i / omega_j if omega_j != 0 else float("inf")
            target_ratio = pair.p / pair.q if pair.q != 0 else float("inf")
            hit_min = (omega_i <= adaptive_conf.omega_min + 1e-12) or (omega_j <= adaptive_conf.omega_min + 1e-12)
            hit_max = (omega_i >= adaptive_conf.omega_max - 1e-12) or (omega_j >= adaptive_conf.omega_max - 1e-12)
            locked = bool(
                (pair.L_last > adaptive_conf.lock_threshold_L)
                and (abs(ratio - target_ratio) < adaptive_conf.lock_ratio_tol)
            )
            drift_without_update = False
            if pair.omega_updates == 0:
                tol_i = 0.05 * max(abs(pair.omega_i_init), 1e-6)
                tol_j = 0.05 * max(abs(pair.omega_j_init), 1e-6)
                if abs(omega_i - pair.omega_i_init) > tol_i or abs(omega_j - pair.omega_j_init) > tol_j:
                    drift_without_update = True
            pairs_out.append(
                {
                    "name": pair.name,
                    "L_mean": pair.L_last,
                    "L_mag_used": pair.L_last,
                    "L_sin": pair.L_sin_last,
                    "phi_mean": pair.phi_last,
                    "K_final": pair.k_adapt,
                    "K_used": pair.k_adapt,
                    "omega_i_raw_final": omega_i_raw,
                    "omega_j_raw_final": omega_j_raw,
                    "omega_i_final": omega_i,
                    "omega_j_final": omega_j,
                    "delta_omega_i_last": pair.delta_omega_i_last,
                    "delta_omega_j_last": pair.delta_omega_j_last,
                    "omega_i_before": pair.omega_i_before,
                    "omega_i_after": pair.omega_i_after,
                    "omega_j_before": pair.omega_j_before,
                    "omega_j_after": pair.omega_j_after,
                    "clamp_i": pair.clamp_i,
                    "clamp_j": pair.clamp_j,
                    "ratio_eff": ratio,
                    "target_ratio": target_ratio,
                    "p": pair.p,
                    "q": pair.q,
                    "locked": locked,
                    "hit_omega_min": hit_min,
                    "hit_omega_max": hit_max,
                    "omega_update_applied": pair.omega_update_applied,
                    "omega_update_count": pair.omega_updates,
                    "omega_drift_without_update": drift_without_update,
                }
            )
        result["adaptive_lock"] = {"pairs": pairs_out}
    if debug:
        result["debug_traces"] = {
            "inputs": np.array(debug_inputs),
            "tau_eff": debug_tau,
            "z": np.array(debug_z),
        }
    return result


def compute_fft_spectrum(samples_x: np.ndarray, dt_sample: float):
    """Compute FFT and per-frequency power."""
    if samples_x.size == 0:
        return {"freqs": np.array([]), "omega": np.array([]), "power_total": np.array([]), "per_mode": np.array([])}
    X = np.fft.rfft(samples_x, axis=0)
    freqs = np.fft.rfftfreq(samples_x.shape[0], d=dt_sample)
    omega = 2 * np.pi * freqs
    power_per_mode = np.abs(X) ** 2
    power_total = np.sum(power_per_mode, axis=1)
    return {"freqs": freqs, "omega": omega, "power_total": power_total, "per_mode": power_per_mode}


def pick_peaks(
    spectrum: Dict[str, np.ndarray],
    modes: List[Mode],
    layer_to_idx: Dict[Layer, int],
    sim_params: SimulationParams,
):
    omega = spectrum["omega"]
    power_total = spectrum["power_total"]
    if omega.size == 0:
        return [], [], []
    mask = power_total > sim_params.peak_threshold * np.max(power_total)
    idxs = np.where(mask)[0]
    idxs = idxs[idxs > 0]  # drop DC
    idxs = np.sort(idxs)
    if idxs.size > sim_params.max_peaks:
        idxs = idxs[: sim_params.max_peaks]

    weights_per_peak: List[Dict[str, float]] = []
    power_per_mode = spectrum["per_mode"]
    peak_powers: List[float] = []
    for idx in idxs:
        weights = {}
        peak_powers.append(float(power_total[idx]))
        total = float(np.sum(power_per_mode[idx]))
        if total <= 0:
            weights_per_peak.append({})
            continue
        for layer in layer_to_idx:
            layer_indices = [i for i, m in enumerate(modes) if m.layer == layer]
            layer_power = float(np.sum(power_per_mode[idx, layer_indices]))
            weights[layer.name] = layer_power / total
        weights_per_peak.append(weights)
    return omega[idxs], weights_per_peak, peak_powers
