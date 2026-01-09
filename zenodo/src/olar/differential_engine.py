"""Differential engine helpers (S2 scaffolding, DOF-only)."""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np

from core.ids.hashing import hash_text
from olar.physics_core import (
    Layer,
    Coupling,
    InterLayerCoupling,
    MemoryKernel,
    Mode,
    SimulationParams,
    SimulationState,
    _layer_order,
    _numeric_intra,
    _state_add,
    compute_layer_energies,
    derivatives,
    init_state,
    init_structural_params,
    make_index_map,
)
SERIES_EPS = 1e-12


def compute_inter_coupling(
    theta_s1_now: np.ndarray,
    theta_s1_delayed: np.ndarray,
    edges: Iterable[Tuple[int, int]],
    k_global: float,
    n_nodes: int,
) -> np.ndarray:
    """Compute inter-node coupling for S1 layer only.

    F_inter,i(t) = (K_global / N_neighbors(i)) * sum_{j in N(i)} sin(theta_j(t - tau) - theta_i(t))
    """
    neighbors: List[List[int]] = [[] for _ in range(n_nodes)]
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            continue
        i, j = int(edge[0]), int(edge[1])
        if i < 0 or j < 0 or i >= n_nodes or j >= n_nodes or i == j:
            continue
        neighbors[i].append(j)
        neighbors[j].append(i)

    f_inter = np.zeros(n_nodes, dtype=float)
    for i in range(n_nodes):
        neigh = neighbors[i]
        if not neigh:
            continue
        theta_i = theta_s1_now[i]
        theta_j = theta_s1_delayed[neigh]
        f_inter[i] = (k_global / float(len(neigh))) * float(np.sum(np.sin(theta_j - theta_i)))
    return f_inter


class HistoryBuffer:
    """Fixed-size ring buffer for delayed theta_S1 vectors."""

    def __init__(self, delay_steps: int, n_nodes: int, initial: np.ndarray) -> None:
        if delay_steps < 0:
            raise ValueError("delay_steps must be >= 0")
        self.delay_steps = int(delay_steps)
        self.size = self.delay_steps + 1
        self.buffer = np.zeros((self.size, n_nodes), dtype=float)
        self.head_idx = 0
        for idx in range(self.size):
            self.buffer[idx, :] = initial

    def push(self, theta_s1: np.ndarray) -> None:
        self.head_idx = (self.head_idx + 1) % self.size
        self.buffer[self.head_idx, :] = theta_s1

    def get_delayed(self, frac: float = 0.0) -> np.ndarray:
        if self.size == 1:
            return self.buffer[self.head_idx].copy()
        idx0 = (self.head_idx - self.delay_steps) % self.size
        idx1 = (idx0 + 1) % self.size
        if frac <= 0.0:
            return self.buffer[idx0].copy()
        if frac >= 1.0:
            return self.buffer[idx1].copy()
        return (1.0 - frac) * self.buffer[idx0] + frac * self.buffer[idx1]

    def get_delayed_steps(self, steps_ago: float) -> np.ndarray:
        if self.size == 1 or steps_ago <= 0.0:
            return self.buffer[self.head_idx].copy()
        base = int(math.floor(steps_ago))
        frac = steps_ago - base
        idx0 = (self.head_idx - base) % self.size
        if frac <= 0.0:
            return self.buffer[idx0].copy()
        idx1 = (idx0 - 1) % self.size
        return (1.0 - frac) * self.buffer[idx0] + frac * self.buffer[idx1]


class NodeOscillator:
    def __init__(self, theta_internal: dict, rng: np.random.Generator, sim_params: SimulationParams) -> None:
        self.modes = _parse_modes(theta_internal)
        if not self.modes:
            raise RuntimeError("theta_internal missing modes for differential_engine")
        self.intra_couplings = _parse_intra(theta_internal)
        self.inter_couplings = _parse_inter(theta_internal)
        self.index_map = make_index_map(self.modes)
        self.struct_params = init_structural_params(_layer_order([m.layer for m in self.modes]), rng)
        self.state, self.layer_to_idx, self.mem_arch, self.direct_links, self.layer_indices = init_state(
            self.modes, self.inter_couplings, self.struct_params, rng
        )
        self.intra_pairs = _numeric_intra(self.intra_couplings, self.index_map)
        self.sim_params = sim_params

    def derivatives(self, state: SimulationState, drive_s1: float) -> SimulationState:
        return derivatives(
            self.modes,
            self.intra_pairs,
            self.mem_arch,
            self.direct_links,
            self.struct_params,
            self.layer_to_idx,
            self.layer_indices,
            state,
            self.sim_params,
            drive_s1=drive_s1,
        )

    def theta_s1_from_state(self, state: SimulationState) -> float:
        indices = self.layer_indices.get(Layer.S1, [])
        if not indices:
            return 0.0
        phases = []
        for idx in indices:
            omega = self.modes[idx].omega0
            phases.append(math.atan2(state.v[idx] / max(omega, 1e-9), state.x[idx]))
        return float(np.mean(phases))

    def energies(self, state: SimulationState) -> Dict[Layer, float]:
        mem_energy_by_layer: Dict[Layer, float] = {}
        for (layer, k), idx_z in self.mem_arch.mem_index.items():
            params = self.mem_arch.layer_mem.get(layer)
            if params is None:
                continue
            mem_energy_by_layer[layer] = mem_energy_by_layer.get(layer, 0.0) + 0.5 * params.kappa[k] * state.z[
                idx_z
            ] ** 2
        return compute_layer_energies(
            self.modes, state, self.layer_to_idx, self.sim_params.eps_omega, mem_energy_by_layer=mem_energy_by_layer
        )


class DifferentialNetwork:
    """S2 differential network runner (clean-room scaffolding)."""

    def __init__(
        self,
        nodes_theta_internal: List[dict],
        omega_ref: List[float],
        edges: Iterable[Tuple[int, int]],
        engine_params: dict,
        seed: int,
    ) -> None:
        self.nodes = list(nodes_theta_internal)
        self.omega_ref = np.array(omega_ref, dtype=float)
        self.edges = list(edges)
        self.engine_params = dict(engine_params)
        self.seed = int(seed)

        self.dt = float(self.engine_params.get("dt", 1.0))
        self.t_ticks = int(self.engine_params.get("T_ticks", 0))
        self.window_w = int(self.engine_params.get("W", 1))
        self.k_global = float(self.engine_params.get("K_global", 0.0))
        self.tau_field = float(self.engine_params.get("tau_field", 0.0))
        self.tau_steps = (self.tau_field / self.dt) if self.dt > 0 else 0.0
        delay_steps = int(math.ceil(self.tau_steps)) if self.tau_steps > 0 else 0
        self.sim_params = SimulationParams(
            dt=self.dt,
            total_steps=self.t_ticks,
        )
        self.oscillators: List[NodeOscillator] = []
        for idx, theta_internal in enumerate(self.nodes):
            node_seed = _node_seed(self.seed, idx)
            rng = np.random.default_rng(node_seed)
            self.oscillators.append(NodeOscillator(theta_internal, rng, self.sim_params))
        theta_s1_init = np.array([osc.theta_s1_from_state(osc.state) for osc in self.oscillators], dtype=float)
        self.history = HistoryBuffer(delay_steps, len(self.oscillators), theta_s1_init)

    def step(self) -> Tuple[np.ndarray, np.ndarray]:
        n_nodes = len(self.oscillators)
        states0 = [osc.state for osc in self.oscillators]
        theta0 = np.array([osc.theta_s1_from_state(state) for osc, state in zip(self.oscillators, states0)])
        steps_ago0 = self.tau_steps - 0.0
        delayed0 = theta0 if steps_ago0 <= 0.0 else self.history.get_delayed_steps(steps_ago0)
        f_inter0 = compute_inter_coupling(theta0, delayed0, self.edges, self.k_global, n_nodes)
        k1 = [osc.derivatives(state, f_inter0[idx]) for idx, (osc, state) in enumerate(zip(self.oscillators, states0))]
        states1 = [_state_add(state, k, self.dt * 0.5) for state, k in zip(states0, k1)]

        theta1 = np.array([osc.theta_s1_from_state(state) for osc, state in zip(self.oscillators, states1)])
        steps_ago1 = self.tau_steps - 0.5
        delayed1 = theta1 if steps_ago1 <= 0.0 else self.history.get_delayed_steps(steps_ago1)
        f_inter1 = compute_inter_coupling(theta1, delayed1, self.edges, self.k_global, n_nodes)
        k2 = [osc.derivatives(state, f_inter1[idx]) for idx, (osc, state) in enumerate(zip(self.oscillators, states1))]
        states2 = [_state_add(state, k, self.dt * 0.5) for state, k in zip(states0, k2)]

        theta2 = np.array([osc.theta_s1_from_state(state) for osc, state in zip(self.oscillators, states2)])
        steps_ago2 = self.tau_steps - 0.5
        delayed2 = theta2 if steps_ago2 <= 0.0 else self.history.get_delayed_steps(steps_ago2)
        f_inter2 = compute_inter_coupling(theta2, delayed2, self.edges, self.k_global, n_nodes)
        k3 = [osc.derivatives(state, f_inter2[idx]) for idx, (osc, state) in enumerate(zip(self.oscillators, states2))]
        states3 = [_state_add(state, k, self.dt) for state, k in zip(states0, k3)]

        theta3 = np.array([osc.theta_s1_from_state(state) for osc, state in zip(self.oscillators, states3)])
        steps_ago3 = self.tau_steps - 1.0
        delayed3 = theta3 if steps_ago3 <= 0.0 else self.history.get_delayed_steps(steps_ago3)
        f_inter3 = compute_inter_coupling(theta3, delayed3, self.edges, self.k_global, n_nodes)
        k4 = [osc.derivatives(state, f_inter3[idx]) for idx, (osc, state) in enumerate(zip(self.oscillators, states3))]

        eq = np.zeros(n_nodes, dtype=float)
        es1 = np.zeros(n_nodes, dtype=float)
        es2 = np.zeros(n_nodes, dtype=float)
        theta_next = np.zeros(n_nodes, dtype=float)
        for idx, osc in enumerate(self.oscillators):
            state = states0[idx]
            new_state = SimulationState(
                x=state.x + self.dt / 6.0 * (k1[idx].x + 2 * k2[idx].x + 2 * k3[idx].x + k4[idx].x),
                v=state.v + self.dt / 6.0 * (k1[idx].v + 2 * k2[idx].v + 2 * k3[idx].v + k4[idx].v),
                z=state.z + self.dt / 6.0 * (k1[idx].z + 2 * k2[idx].z + 2 * k3[idx].z + k4[idx].z),
                b=state.b + self.dt / 6.0 * (k1[idx].b + 2 * k2[idx].b + 2 * k3[idx].b + k4[idx].b),
                e=state.e + self.dt / 6.0 * (k1[idx].e + 2 * k2[idx].e + 2 * k3[idx].e + k4[idx].e),
            )
            osc.state = new_state
            theta_next[idx] = osc.theta_s1_from_state(new_state)
            energy = osc.energies(new_state)
            eq[idx] = float(energy.get(Layer.Q, 0.0))
            es1[idx] = float(energy.get(Layer.S1, 0.0))
            es2[idx] = float(energy.get(Layer.S2, 0.0))
        self.history.push(theta_next)
        return theta_next, np.vstack([eq, es1, es2])

    def run(self) -> dict:
        series_eq: List[float] = []
        series_es1: List[float] = []
        series_es2: List[float] = []
        series_r: List[float] = []
        for _ in range(self.t_ticks):
            theta_s1, energies = self.step()
            series_eq.append(float(np.sum(energies[0])))
            series_es1.append(float(np.sum(energies[1])))
            series_es2.append(float(np.sum(energies[2])))
            series_r.append(compute_r_network_s1(theta_s1))
        eq = np.array(series_eq, dtype=float)
        es1 = np.array(series_es1, dtype=float)
        es2 = np.array(series_es2, dtype=float)
        r_series = np.array(series_r, dtype=float)
        return build_metrics_raw(eq, es1, es2, r_series, self.window_w)


def _node_seed(seed: int, idx: int) -> int:
    return int(hash_text(f"{seed}|node|{idx}")[:8], 16) & 0xFFFFFFFF


def _parse_modes(theta_internal: Dict[str, Any]) -> List[Mode]:
    modes = []
    for raw in theta_internal.get("modes", []) or []:
        layer_name = raw.get("layer")
        if not layer_name:
            continue
        try:
            layer = Layer[layer_name]
        except Exception:
            continue
        if layer not in (Layer.Q, Layer.S1, Layer.S2):
            continue
        modes.append(
            Mode(
                layer=layer,
                index=int(raw.get("index", 0)),
                omega0=float(raw.get("omega0", 0.0)),
                mass=float(raw.get("mass", 1.0)),
                gamma=float(raw.get("gamma", 0.0)),
            )
        )
    return modes


def _parse_intra(theta_internal: Dict[str, Any]) -> List[Coupling]:
    intra = []
    for raw in theta_internal.get("intra_couplings", []) or []:
        i_raw = raw.get("i") or {}
        j_raw = raw.get("j") or {}
        try:
            i_layer = Layer[i_raw.get("layer")]
            j_layer = Layer[j_raw.get("layer")]
        except Exception:
            continue
        if i_layer not in (Layer.Q, Layer.S1, Layer.S2) or j_layer not in (Layer.Q, Layer.S1, Layer.S2):
            continue
        intra.append(
            Coupling(
                i=(i_layer, int(i_raw.get("index", 0))),
                j=(j_layer, int(j_raw.get("index", 0))),
                k_ij0=float(raw.get("k_ij0", 0.0)),
            )
        )
    return intra


def _parse_inter(theta_internal: Dict[str, Any]) -> List[InterLayerCoupling]:
    inter = []
    for raw in theta_internal.get("inter_couplings", []) or []:
        try:
            deep = Layer[raw.get("deep_layer")]
            shallow = Layer[raw.get("shallow_layer")]
        except Exception:
            continue
        if deep not in (Layer.Q, Layer.S1, Layer.S2) or shallow not in (Layer.Q, Layer.S1, Layer.S2):
            continue
        links = {}
        for link in raw.get("links", []) or []:
            i_deep = int(link.get("i_deep", 0))
            j_shallow = int(link.get("j_shallow", 0))
            taus0 = [float(x) for x in link.get("taus0", [])]
            amps0 = [float(x) for x in link.get("amps0", [])]
            links[(i_deep, j_shallow)] = MemoryKernel(taus0=taus0, amps0=amps0)
        inter.append(
            InterLayerCoupling(
                deep_layer=deep,
                shallow_layer=shallow,
                g0=float(raw.get("g0", 0.0)),
                links=links,
            )
        )
    return inter


def compute_energy_fractions(eq: float, es1: float, es2: float) -> Tuple[float, float, float]:
    total = float(eq + es1 + es2) + SERIES_EPS
    return float(eq / total), float(es1 / total), float(es2 / total)


def compute_r_network_s1(theta_s1: np.ndarray) -> float:
    return float(np.abs(np.mean(np.exp(1j * theta_s1))))


def compute_participation_entropy(
    pq: np.ndarray,
    ps1: np.ndarray,
    ps2: np.ndarray,
) -> Tuple[float, float, float, float, float]:
    p_stack = np.stack([pq, ps1, ps2], axis=1)
    h_part = -np.sum(p_stack * np.log(p_stack + SERIES_EPS), axis=1)
    h_part_norm = h_part / np.log(3.0)
    return (
        float(np.mean(h_part_norm)),
        float(np.std(h_part_norm)),
        float(np.mean(pq)),
        float(np.mean(ps1)),
        float(np.mean(ps2)),
    )


def permutation_entropy_v1_diff(series: np.ndarray, m: int = 5, tau: int = 1) -> float | None:
    x = np.asarray(series, dtype=float)
    t_len = x.size
    if t_len < m * tau + 1:
        return None
    patterns: Dict[Tuple[int, ...], int] = {}
    for t in range(t_len - (m - 1) * tau):
        window = x[t : t + m * tau : tau]
        order = tuple(np.argsort(window, kind="stable"))
        patterns[order] = patterns.get(order, 0) + 1
    total = sum(patterns.values())
    if total == 0:
        return None
    probs = np.array(list(patterns.values()), dtype=float) / total
    return float(-np.sum(probs * np.log(np.clip(probs, SERIES_EPS, 1.0))) / np.log(math.factorial(m)))


def compute_pe_lock_s1(ps1: np.ndarray, window_w: int) -> Tuple[float, int, int, int]:
    if ps1.size < window_w:
        return float("nan"), 5, 1, window_w
    series = ps1[-window_w:]
    pe = permutation_entropy_v1_diff(series, m=5, tau=1)
    if pe is None:
        return float("nan"), 5, 1, window_w
    return float(pe), 5, 1, window_w


def build_metrics_raw(
    eq_series: np.ndarray,
    es1_series: np.ndarray,
    es2_series: np.ndarray,
    r_network_s1: np.ndarray,
    window_w: int,
    debug_trace_ref: str | None = None,
) -> dict:
    if eq_series.size == 0 or es1_series.size == 0 or es2_series.size == 0:
        return {}
    pq = eq_series / (eq_series + es1_series + es2_series + SERIES_EPS)
    ps1 = es1_series / (eq_series + es1_series + es2_series + SERIES_EPS)
    ps2 = es2_series / (eq_series + es1_series + es2_series + SERIES_EPS)

    h_mean, h_std, pq_mean, ps1_mean, ps2_mean = compute_participation_entropy(pq, ps1, ps2)
    pe_val, pe_m, pe_tau, pe_len = compute_pe_lock_s1(ps1, window_w)
    if r_network_s1.size >= window_w:
        r_window = r_network_s1[-window_w:]
        r_mean = float(np.mean(r_window))
        r_std = float(np.std(r_window))
    else:
        r_mean = float("nan")
        r_std = float("nan")
    r_final = float(r_network_s1[-1]) if r_network_s1.size else float("nan")

    metrics = {
        "H_part_norm_mean_lastW": h_mean,
        "H_part_norm_std_lastW": h_std,
        "pQ_mean_lastW": pq_mean,
        "pS1_mean_lastW": ps1_mean,
        "pS2_mean_lastW": ps2_mean,
        "PE_lockS1_norm": pe_val,
        "PE_m": pe_m,
        "PE_tau": pe_tau,
        "PE_len": pe_len,
        "R_network_S1_mean_lastW": r_mean,
        "R_network_S1_std_lastW": r_std,
        "R_network_S1_final": r_final,
    }
    if debug_trace_ref:
        metrics["debug_trace_ref"] = debug_trace_ref
    return metrics
