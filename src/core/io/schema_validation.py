"""Schema validation helpers (hard required fields, V1)."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from olar.schemas import (
    ATTEMPT_REQUIRED_FIELDS,
    ATTEMPT_REQUIRED_NESTED,
    ENTITY_REQUIRED_FIELDS,
    ENTITY_REQUIRED_NESTED,
    EVALUATION_REQUIRED_FIELDS,
    EVALUATION_REQUIRED_NESTED,
    GENOME_LAYER_REQUIRED_FIELDS,
    BLOCK_REQUIRED_FIELDS,
    EVALUATION_OPTIONAL_FIELDS,
    THETA_INTERNAL_REQUIRED_FIELDS,
    assert_required,
)


def _is_str(val: Any) -> bool:
    return isinstance(val, str) and val != ""


def _is_number(val: Any) -> bool:
    return isinstance(val, (int, float))


def _is_bool(val: Any) -> bool:
    return isinstance(val, bool)


def _is_scalar(val: Any) -> bool:
    return val is None or isinstance(val, (str, int, float, bool))


def _is_short_str_list(val: Any, max_items: int = 32, max_len: int = 64) -> bool:
    if not isinstance(val, list) or len(val) > max_items:
        return False
    for item in val:
        if not isinstance(item, str) or len(item) > max_len:
            return False
    return True


def _is_shallow_scalar_dict(val: Any) -> bool:
    if not isinstance(val, dict):
        return False
    for v in val.values():
        if not _is_scalar(v):
            return False
    return True


def _is_edge_list(val: Any) -> bool:
    if not isinstance(val, list):
        return False
    for edge in val:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            return False
        if not all(isinstance(x, (int, float)) for x in edge):
            return False
    return True


def _ensure_type(cond: bool, label: str, missing: List[str]) -> None:
    if not cond:
        missing.append(label)


def validate_attempt(record: Dict[str, Any]) -> None:
    assert_required(record, ATTEMPT_REQUIRED_FIELDS, ATTEMPT_REQUIRED_NESTED)
    missing: List[str] = []
    _ensure_type(record.get("schema_version") == "olar_attempt_v1", "schema_version", missing)
    _ensure_type(_is_str(record.get("entity_id")), "entity_id", missing)
    _ensure_type(_is_str(record.get("eval_id")), "eval_id", missing)
    _ensure_type(_is_str(record.get("role")), "role", missing)
    _ensure_type(_is_number(record.get("seed")), "seed", missing)
    _ensure_type(_is_str(record.get("engine_params_bin_id")), "engine_params_bin_id", missing)
    _ensure_type(isinstance(record.get("engine_params"), dict), "engine_params", missing)
    _ensure_type(isinstance(record.get("build_plan"), dict), "build_plan", missing)
    _ensure_type(isinstance(record.get("canonical_node_order"), list), "canonical_node_order", missing)
    _ensure_type(isinstance(record.get("edges"), list), "edges", missing)
    if missing:
        raise ValueError(f"Attempt validation failed: {missing}")


def validate_entity_candidate(record: Dict[str, Any]) -> None:
    assert_required(record, ENTITY_REQUIRED_FIELDS, ENTITY_REQUIRED_NESTED)
    missing: List[str] = []
    _ensure_type(record.get("schema_version") == "olar_entity_candidate_v1", "schema_version", missing)
    _ensure_type(_is_str(record.get("entity_id")), "entity_id", missing)
    _ensure_type(_is_str(record.get("source_eval_id")), "source_eval_id", missing)
    _ensure_type(_is_number(record.get("seed")), "seed", missing)
    _ensure_type(_is_str(record.get("engine_params_bin_id")), "engine_params_bin_id", missing)
    _ensure_type(isinstance(record.get("metrics_summary"), dict), "metrics_summary", missing)
    _ensure_type(isinstance(record.get("tags_raw"), dict), "tags_raw", missing)
    _ensure_type(isinstance(record.get("reasons_raw"), list), "reasons_raw", missing)
    _ensure_type(isinstance(record.get("build_plan"), dict), "build_plan", missing)
    _ensure_type(_is_str(record.get("template_name")), "template_name", missing)
    _ensure_type(_is_edge_list(record.get("edges")), "edges", missing)
    _ensure_type(isinstance(record.get("canonical_node_order"), list), "canonical_node_order", missing)
    _ensure_type(isinstance(record.get("parent_ids"), list), "parent_ids", missing)
    if missing:
        raise ValueError(f"Entity candidate validation failed: {missing}")


def validate_evaluation(record: Dict[str, Any]) -> None:
    assert_required(record, EVALUATION_REQUIRED_FIELDS, EVALUATION_REQUIRED_NESTED)
    missing: List[str] = []
    _ensure_type(record.get("schema_version") == "olar_evaluation_v1", "schema_version", missing)
    _ensure_type(_is_str(record.get("run_session_id")), "run_session_id", missing)
    _ensure_type(_is_str(record.get("timestamp_utc")), "timestamp_utc", missing)
    _ensure_type(_is_number(record.get("ola")), "ola", missing)
    _ensure_type(_is_str(record.get("entity_id")), "entity_id", missing)
    _ensure_type(_is_str(record.get("eval_id")), "eval_id", missing)
    _ensure_type(record.get("role") == "sweep", "role", missing)
    _ensure_type(_is_number(record.get("seed")), "seed", missing)
    _ensure_type(_is_str(record.get("engine_params_bin_id")), "engine_params_bin_id", missing)
    _ensure_type(isinstance(record.get("engine_params"), dict), "engine_params", missing)
    _ensure_type(isinstance(record.get("metrics_raw"), dict), "metrics_raw", missing)
    _ensure_type(isinstance(record.get("tags_raw"), dict), "tags_raw", missing)
    _ensure_type(isinstance(record.get("reasons_raw"), list), "reasons_raw", missing)
    _ensure_type(isinstance(record.get("provenance"), dict), "provenance", missing)
    metrics_raw = record.get("metrics_raw") if isinstance(record.get("metrics_raw"), dict) else {}
    for key, val in metrics_raw.items():
        if not _is_scalar(val):
            missing.append(f"metrics_raw.{key}.scalar")
    tags_raw = record.get("tags_raw") if isinstance(record.get("tags_raw"), dict) else {}
    for key, val in tags_raw.items():
        if _is_scalar(val):
            continue
        if _is_short_str_list(val):
            continue
        missing.append(f"tags_raw.{key}.scalar_or_short_list")
    reasons_raw = record.get("reasons_raw")
    if not _is_short_str_list(reasons_raw):
        missing.append("reasons_raw.short_list")
    provenance = record.get("provenance") if isinstance(record.get("provenance"), dict) else {}
    for key, val in provenance.items():
        if _is_scalar(val):
            continue
        if _is_shallow_scalar_dict(val):
            continue
        missing.append(f"provenance.{key}.scalar_or_shallow_dict")
    allowed_keys = set(EVALUATION_REQUIRED_FIELDS) | set(EVALUATION_OPTIONAL_FIELDS)
    extra_keys = sorted(k for k in record.keys() if k not in allowed_keys)
    if extra_keys:
        missing.append(f"unexpected_keys:{extra_keys}")
    optional_types = {
        "status": _is_str,
        "seed_index": _is_number,
        "seed_u32": _is_number,
        "runtime_sec": _is_number,
        "is_finite_primary": _is_bool,
        "nan_primary_count": _is_number,
        "sweep_passed": _is_bool,
    }
    for opt_key in EVALUATION_OPTIONAL_FIELDS:
        if opt_key not in record:
            continue
        val = record.get(opt_key)
        check = optional_types.get(opt_key)
        if check is None:
            continue
        _ensure_type(val is None or check(val), opt_key, missing)
    if missing:
        raise ValueError(f"Evaluation validation failed: {missing}")


def validate_genome_layer(row: Dict[str, Any]) -> None:
    missing = [k for k in GENOME_LAYER_REQUIRED_FIELDS if k not in row]
    if missing:
        raise ValueError(f"Genome layer validation failed: {missing}")


def validate_block(row: Dict[str, Any]) -> None:
    missing = [k for k in BLOCK_REQUIRED_FIELDS if k not in row]
    if missing:
        raise ValueError(f"Block validation failed: {missing}")
    if not _is_str(row.get("block_id")):
        raise ValueError("Block validation failed: block_id")
    if not _is_number(row.get("omega_ref")):
        raise ValueError("Block validation failed: omega_ref")


def validate_theta_internal(theta_internal: Dict[str, Any]) -> None:
    missing = [k for k in THETA_INTERNAL_REQUIRED_FIELDS if k not in theta_internal]
    if missing:
        raise ValueError(f"theta_internal validation failed: {missing}")
    if theta_internal.get("schema_version") != "theta_internal_v1":
        raise ValueError("theta_internal validation failed: schema_version")
    modes = theta_internal.get("modes")
    if not isinstance(modes, list) or not modes:
        raise ValueError(
            "Missing theta_internal.modes (legacy blocks not supported). Regenerate via ola1 exporter."
        )
