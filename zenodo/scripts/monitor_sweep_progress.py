#!/usr/bin/env python3
"""Report ola2 sweep progress across shards."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from core.ids.engine_bins import neighbor_engine_params_bin_ids
from core.ids.hashing import hash_text


def _load_json(path: Path) -> Dict:
    return json.loads(path.read_text())


def _resolve_path(path_str: str, base_dir: Path) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    if path_str.startswith("."):
        return base_dir / path
    if path_str.startswith(("data/", "src/", "docs/", "scripts/")):
        return path
    return base_dir / path


def _iter_entities(path: Path):
    if not path.exists():
        return []
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("entity_id"):
                tags = rec.get("tags_raw") or {}
                if tags.get("candidate") is True:
                    rows.append(rec)
    return rows


def _expected_evals_per_entity(cfg: Dict, entity: Dict) -> int:
    seed_policy = cfg.get("seed_policy", {})
    seeds = int(seed_policy.get("seeds", 1))
    max_evals_per_entity = int((cfg.get("budgets", {}) or {}).get("max_evals_per_entity", 0) or 0)
    engine_variation = cfg.get("engine_variation", {}) or {}
    neighbor = cfg.get("neighborhood", {}) or {}
    max_neighbor_bins = int(neighbor.get("max_neighbor_bins", 0) or 0)
    mode = str(neighbor.get("mode", "param_bin_neighbors"))
    base_bin_id = entity.get("engine_params_bin_id")
    if not base_bin_id:
        return 0
    if mode == "param_bin_neighbors":
        bin_ids = neighbor_engine_params_bin_ids(base_bin_id, engine_variation.get("bins") or {}, max_neighbor_bins)
    else:
        bin_ids = [base_bin_id]
    expected = len(bin_ids) * seeds
    if max_evals_per_entity:
        expected = min(expected, max_evals_per_entity)
    return expected


def _parse_timestamp(raw: str) -> float | None:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor sweep progress across shards.")
    parser.add_argument(
        "--sweep-config",
        default="config/ola2_paper/ola2_sweep.json",
        help="Base sweep config (for seeds/bins expectations).",
    )
    parser.add_argument(
        "--entities",
        default=None,
        help="entities_candidates.jsonl path (defaults to sweep config inputs).",
    )
    parser.add_argument(
        "--shards-root",
        default="data/processed/ola2/sweep_shards",
        help="Root directory containing shard_XX/raw or worker_XX/raw evaluations.jsonl",
    )
    parser.add_argument(
        "--shard-count",
        type=int,
        default=0,
        help="Shard count for assignment stats (hash-based).",
    )
    args = parser.parse_args()

    sweep_cfg_path = Path(args.sweep_config)
    cfg = _load_json(sweep_cfg_path)
    inputs = cfg.get("inputs", {}) or {}
    cfg_entities = inputs.get("entities_candidates_jsonl")
    if args.entities:
        entities_path = Path(args.entities)
    elif isinstance(cfg_entities, str) and cfg_entities:
        entities_path = _resolve_path(cfg_entities, sweep_cfg_path.parent)
    else:
        entities_path = Path("data/processed/ola2/raw/entities_candidates.jsonl")
    entities = _iter_entities(entities_path)
    expected_per_entity = {
        rec["entity_id"]: _expected_evals_per_entity(cfg, rec) for rec in entities if rec.get("entity_id")
    }

    counts = Counter()
    last_ts_by_entity: Dict[str, float] = {}
    shard_counts: Dict[str, int] = {}
    shard_last_ts: Dict[str, float] = {}
    all_ts: list[float] = []
    shards_root = Path(args.shards_root)
    patterns = ["shard_*/raw/evaluations.jsonl", "worker_*/raw/evaluations.jsonl"]
    paths = []
    for pattern in patterns:
        paths.extend(sorted(shards_root.glob(pattern)))
    is_worker_mode = any("worker_" in str(path) for path in paths)
    for path in paths:
        shard_name = path.parent.parent.name
        shard_counts[shard_name] = 0
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                eid = rec.get("entity_id")
                if eid:
                    counts[eid] += 1
                ts = _parse_timestamp(rec.get("timestamp_utc") or "")
                if ts is not None:
                    all_ts.append(ts)
                    if eid and ts > last_ts_by_entity.get(eid, 0.0):
                        last_ts_by_entity[eid] = ts
                    if ts > shard_last_ts.get(shard_name, 0.0):
                        shard_last_ts[shard_name] = ts
                shard_counts[shard_name] += 1

    total_candidates = len(expected_per_entity)
    processed_any = sum(1 for eid in expected_per_entity if counts.get(eid, 0) > 0)
    completed = 0
    for eid, expected in expected_per_entity.items():
        got = counts.get(eid, 0)
        if got >= expected and expected > 0:
            completed += 1

    print(f"total_candidates {total_candidates} (entities in input)")
    print(f"processed_any {processed_any} (entities with at least 1 eval)")
    print(f"completed {completed} (progress=1.000)")
    print(f"completed_ratio {completed}/{total_candidates}")

    total_expected = sum(expected_per_entity.values())
    total_done = sum(counts.values())
    eta_hours = None
    if total_done > 0 and all_ts:
        first_ts = min(all_ts)
        last_ts = max(all_ts)
        elapsed = max(last_ts - first_ts, 1.0)
        rate = total_done / elapsed
        remaining = max(total_expected - total_done, 0)
        eta_hours = remaining / rate / 3600 if rate > 0 else None
    if eta_hours is not None:
        print(f"eta_hours {eta_hours:.2f}")
    else:
        print("eta_hours n/a")

    # Top entities by progress (got/expected)
    progress_rows = []
    for eid, expected in expected_per_entity.items():
        got = counts.get(eid, 0)
        if expected <= 0:
            continue
        progress = got / float(expected)
        progress_rows.append((progress, got, expected, eid))
    progress_rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    print("")
    # shard assignment stats (hash-based)
    shard_count = int(args.shard_count or 0)
    shard_id_map: Dict[str, int] = {}
    shard_assigned: Dict[int, int] = {}
    if shard_count > 0:
        for eid in expected_per_entity:
            sid = int(hash_text(str(eid))[:8], 16) % shard_count
            shard_id_map[eid] = sid
            shard_assigned[sid] = shard_assigned.get(sid, 0) + 1
        print("shard_assignment:")
        for sid in range(shard_count):
            assigned = shard_assigned.get(sid, 0)
            done = 0
            for eid, exp in expected_per_entity.items():
                if shard_id_map.get(eid) != sid:
                    continue
                if counts.get(eid, 0) >= exp and exp > 0:
                    done += 1
            print(f"- shard_{sid:02d} done={done} of {assigned}")
        print("")
    elif is_worker_mode:
        print("worker_assignment: disabled (dynamic scheduling)")
        print("")

    print("bottom_progress:")
    for progress, got, expected, eid in progress_rows[:5]:
        status = "not_started" if got == 0 else ("complete" if progress >= 1.0 else "in_process")
        print(f"- {eid} status={status} got={got} expected={expected} progress={progress:.3f}")
    print("")
    print("top_progress:")
    for progress, got, expected, eid in progress_rows[-5:]:
        status = "not_started" if got == 0 else ("complete" if progress >= 1.0 else "in_process")
        print(f"- {eid} status={status} got={got} expected={expected} progress={progress:.3f}")

    # Shard activity summary
    print("")
    activity_label = "worker_activity" if is_worker_mode else "shard_activity"
    print(f"{activity_label}:")
    for shard_name in sorted(shard_counts):
        count = shard_counts.get(shard_name, 0)
        last_ts = shard_last_ts.get(shard_name)
        last_str = (
            datetime.fromtimestamp(last_ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if last_ts
            else "n/a"
        )
        print(f"- {shard_name} evals={count} last_eval_utc={last_str}")


if __name__ == "__main__":
    main()
