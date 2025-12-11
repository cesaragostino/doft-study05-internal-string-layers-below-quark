"""Dynamic simulator with structural breathing, memory, and FFT-based spectra."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

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
    intra_pairs = _numeric_intra(intra_couplings, index_map)

    omega_max = max(m.omega0 for m in modes) if modes else 1.0
    dt = min(sim_params.dt, 0.05 / omega_max)
    total_steps = sim_params.total_steps
    transient_steps = int(sim_params.transient_frac * total_steps)

    samples_x = []
    samples_time = []
    samples_b = []
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
        )

    for step in range(total_steps):
        state = rk4_step(state, deriv, dt)

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

    samples_x = np.array(samples_x)  # shape (T, N)
    samples_b = np.array(samples_b) if samples_b else np.empty((0, len(state.b)))
    times = np.array(samples_time)

    spectrum = compute_fft_spectrum(samples_x, dt * sim_params.sample_stride)

    # downsample traces for storage
    if samples_b.shape[0] > 300:
        stride = max(1, samples_b.shape[0] // 200)
        samples_b = samples_b[::stride]
        times = times[::stride]

    result = {
        "times": times,
        "b_series": samples_b,
        "spectrum": spectrum,
        "layer_to_idx": layer_to_idx,
        "dt_used": dt,
    }
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
        return [], []
    mask = power_total > sim_params.peak_threshold * np.max(power_total)
    idxs = np.where(mask)[0]
    idxs = idxs[idxs > 0]  # drop DC
    idxs = np.sort(idxs)
    if idxs.size > sim_params.max_peaks:
        idxs = idxs[: sim_params.max_peaks]

    weights_per_peak: List[Dict[str, float]] = []
    power_per_mode = spectrum["per_mode"]
    for idx in idxs:
        weights = {}
        total = float(np.sum(power_per_mode[idx]))
        if total <= 0:
            weights_per_peak.append({})
            continue
        for layer in layer_to_idx:
            layer_indices = [i for i, m in enumerate(modes) if m.layer == layer]
            layer_power = float(np.sum(power_per_mode[idx, layer_indices]))
            weights[layer.name] = layer_power / total
        weights_per_peak.append(weights)
    return omega[idxs], weights_per_peak
