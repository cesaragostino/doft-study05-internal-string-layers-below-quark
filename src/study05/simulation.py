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
    dt: float = 0.01
    total_steps: int = 6000
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


def _layer_order(layers: Sequence[Layer]) -> List[Layer]:
    ordered = []
    for l in (Layer.Q, Layer.S1, Layer.S2, Layer.S3):
        if l in layers and l not in ordered:
            ordered.append(l)
    return ordered


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
) -> Tuple[SimulationState, Dict[Layer, int], List[MemoryLink], List[DirectLink]]:
    index_map = make_index_map(modes)
    layers_present = _layer_order([m.layer for m in modes])
    layer_to_idx = {layer: i for i, layer in enumerate(layers_present)}
    mem_links, direct_links = build_links(inter_couplings, index_map)

    x0 = rng.normal(scale=1e-3, size=len(modes))
    v0 = rng.normal(scale=1e-3, size=len(modes))
    z0 = np.zeros(len(mem_links))
    b0 = np.zeros(len(layers_present))
    e0 = np.zeros(len(layers_present))

    state = SimulationState(x=x0, v=v0, z=z0, b=b0, e=e0)
    energies = compute_layer_energies(modes, state, layer_to_idx, eps_omega=0.1)
    for layer, val in energies.items():
        idx = layer_to_idx[layer]
        state.e[idx] = val
        struct_params.e_ref[layer] = val
    return state, layer_to_idx, mem_links, direct_links


def compute_layer_energies(
    modes: List[Mode],
    state: SimulationState,
    layer_to_idx: Dict[Layer, int],
    eps_omega: float,
) -> Dict[Layer, float]:
    energies: Dict[Layer, float] = {layer: 0.0 for layer in layer_to_idx}
    for p, m in enumerate(modes):
        layer = m.layer
        b_idx = layer_to_idx[layer]
        bL = state.b[b_idx]
        omega_eff2 = m.omega0**2 * (1.0 + eps_omega * bL)
        energies[layer] += 0.5 * m.mass * state.v[p] ** 2 + 0.5 * m.mass * omega_eff2 * state.x[p] ** 2
    return energies


def _numeric_intra(intra_couplings: List[Coupling], index_map: Dict[Tuple[Layer, int], int]):
    pairs = []
    for c in intra_couplings:
        pairs.append((index_map[c.i], index_map[c.j], c.k_ij0, c.i[0]))
    return pairs


def derivatives(
    modes: List[Mode],
    intra_pairs: List[Tuple[int, int, float, Layer]],
    mem_links: List[MemoryLink],
    direct_links: List[DirectLink],
    struct_params: StructuralParams,
    layer_to_idx: Dict[Layer, int],
    state: SimulationState,
    eps_omega: float,
    eps_k: float,
    eps_tau: float,
    eps_amp: float,
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
        omega_eff2 = m.omega0**2 * (1.0 + eps_omega * bL)
        dv[p] += -omega_eff2 * state.x[p] - m.gamma * state.v[p]

    # intra-layer springs
    for i_idx, j_idx, k0, layer in intra_pairs:
        b_idx = layer_to_idx[layer]
        bL = state.b[b_idx]
        k_eff = k0 * (1.0 + eps_k * bL)
        dv[i_idx] += -k_eff * (state.x[i_idx] - state.x[j_idx]) / modes[i_idx].mass
        dv[j_idx] += -k_eff * (state.x[j_idx] - state.x[i_idx]) / modes[j_idx].mass

    # direct inter-layer coupling (spring-like)
    for link in direct_links:
        b_idx = layer_to_idx[link.shallow_layer]
        bL = state.b[b_idx]
        g_eff = link.g0 * (1.0 + eps_k * bL)
        dv[link.shallow_idx] += -g_eff * (state.x[link.shallow_idx] - state.x[link.deep_idx]) / modes[
            link.shallow_idx
        ].mass
        dv[link.deep_idx] += -g_eff * (state.x[link.deep_idx] - state.x[link.shallow_idx]) / modes[
            link.deep_idx
        ].mass

    # memory contributions
    for idx, link in enumerate(mem_links):
        b_tau_idx = layer_to_idx[link.deep_layer]
        b_amp_idx = layer_to_idx[link.shallow_layer]
        tau_eff = link.tau0 * (1.0 + eps_tau * state.b[b_tau_idx])
        amp_eff = link.amp0 * (1.0 + eps_amp * state.b[b_amp_idx])
        dz[idx] = -state.z[idx] / tau_eff + state.x[link.deep_idx]
        dv[link.shallow_idx] += -link.g0 * amp_eff * state.z[idx] / modes[link.shallow_idx].mass

    # structural updates
    inst_energy = compute_layer_energies(modes, state, layer_to_idx, eps_omega)
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
):
    index_map = make_index_map(modes)
    struct_params = init_structural_params(_layer_order([m.layer for m in modes]), rng)
    state, layer_to_idx, mem_links, direct_links = init_state(modes, inter_couplings, struct_params, rng)
    intra_pairs = _numeric_intra(intra_couplings, index_map)

    omega_max = max(m.omega0 for m in modes) if modes else 1.0
    dt = min(sim_params.dt, 0.05 / omega_max)
    total_steps = sim_params.total_steps
    transient_steps = int(sim_params.transient_frac * total_steps)

    samples_x = []
    samples_time = []
    samples_b = []

    def deriv(current_state: SimulationState) -> SimulationState:
        return derivatives(
            modes,
            intra_pairs,
            mem_links,
            direct_links,
            struct_params,
            layer_to_idx,
            current_state,
            sim_params.eps_omega,
            sim_params.eps_k,
            sim_params.eps_tau,
            sim_params.eps_amp,
        )

    for step in range(total_steps):
        state = rk4_step(state, deriv, dt)

        # stability checks
        if not (np.isfinite(state.x).all() and np.isfinite(state.v).all() and np.isfinite(state.z).all()):
            raise FloatingPointError("non-finite state")
        if np.any(np.abs(state.x) > sim_params.max_x) or np.any(np.abs(state.v) > sim_params.max_v):
            raise FloatingPointError("state blow-up")
        inst_energy = compute_layer_energies(modes, state, layer_to_idx, sim_params.eps_omega)
        if any(val > sim_params.max_energy for val in inst_energy.values()):
            raise FloatingPointError("energy blow-up")

        if step >= transient_steps and (step - transient_steps) % sim_params.sample_stride == 0:
            samples_time.append((step + 1) * dt)
            samples_x.append(state.x.copy())
            samples_b.append(state.b.copy())

    samples_x = np.array(samples_x)  # shape (T, N)
    samples_b = np.array(samples_b) if samples_b else np.empty((0, len(state.b)))
    times = np.array(samples_time)

    spectrum = compute_fft_spectrum(samples_x, dt * sim_params.sample_stride)

    # downsample traces for storage
    if samples_b.shape[0] > 300:
        stride = max(1, samples_b.shape[0] // 200)
        samples_b = samples_b[::stride]
        times = times[::stride]

    return {
        "times": times,
        "b_series": samples_b,
        "spectrum": spectrum,
        "layer_to_idx": layer_to_idx,
        "dt_used": dt,
    }


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
