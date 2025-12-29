"""Hard gate for JSONL schema + no-fat evaluation payloads."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

from core.io.jsonl import iter_jsonl
from core.io.schema_validation import validate_attempt, validate_entity_candidate, validate_evaluation


_PROHIBITED_TOP_KEYS = {
    "edges",
    "nodes",
    "theta_internal",
    "hydrated_entity",
    "structure",
    "assignment",
    "build_plan",
    "canonical_node_order",
    "parent_ids",
    "source",
}
_PROHIBITED_KEY_PATTERNS = (
    re.compile(r".*_series$", re.IGNORECASE),
    re.compile(r".*history.*", re.IGNORECASE),
    re.compile(r"^buffer_.*", re.IGNORECASE),
    re.compile(r"^trace_.*", re.IGNORECASE),
)


def _is_short_str_list(val: Any, max_items: int = 32, max_len: int = 64) -> bool:
    if not isinstance(val, list) or len(val) > max_items:
        return False
    return all(isinstance(item, str) and len(item) <= max_len for item in val)


def _check_no_fat(value: Any, path: str = "") -> None:
    if isinstance(value, list):
        if not _is_short_str_list(value):
            raise ValueError(f"prohibited list at {path}")
        return
    if isinstance(value, dict):
        for key, val in value.items():
            key_path = f"{path}.{key}" if path else str(key)
            if key in _PROHIBITED_TOP_KEYS:
                raise ValueError(f"prohibited key {key_path}")
            for pattern in _PROHIBITED_KEY_PATTERNS:
                if pattern.match(str(key)):
                    raise ValueError(f"prohibited key {key_path}")
            _check_no_fat(val, key_path)


def _validate_attempts(path: Path) -> None:
    for row in iter_jsonl(path):
        schema = row.get("schema_version")
        if schema != "olar_attempt_v1":
            raise ValueError(f"attempt schema_version mismatch: {schema}")
        validate_attempt(row)


def _validate_candidates(path: Path) -> None:
    for row in iter_jsonl(path):
        schema = row.get("schema_version")
        if schema != "olar_entity_candidate_v1":
            raise ValueError(f"candidate schema_version mismatch: {schema}")
        validate_entity_candidate(row)


def _validate_evaluations(path: Path) -> None:
    for row in iter_jsonl(path):
        schema = row.get("schema_version")
        if schema != "olar_evaluation_v1":
            raise ValueError(f"evaluation schema_version mismatch: {schema}")
        validate_evaluation(row)
        _check_no_fat(row)


def main() -> None:
    parser = argparse.ArgumentParser(description="JSONL gate: schema + no-fat evaluation payloads.")
    parser.add_argument("--attempts", type=Path, help="attempts.jsonl path")
    parser.add_argument("--candidates", type=Path, help="entities_candidates.jsonl path")
    parser.add_argument("--evaluations", type=Path, help="evaluations.jsonl path")
    args = parser.parse_args()

    if args.attempts:
        _validate_attempts(args.attempts)
    if args.candidates:
        _validate_candidates(args.candidates)
    if args.evaluations:
        _validate_evaluations(args.evaluations)

    print("[jsonl_gate] ok")


if __name__ == "__main__":
    main()
