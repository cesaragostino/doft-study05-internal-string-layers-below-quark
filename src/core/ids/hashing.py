"""Hash utilities for DOFT recursive stack (V1)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


def hash_text(text: str, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def hash_bytes(blob: bytes, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    h.update(blob)
    return h.hexdigest()


def hash_file(path: Path, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_provenance(config_hash: str, code_hash: str, inputs_hash: str, machine: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "config_hash": config_hash,
        "code_hash": code_hash,
        "inputs_hash": inputs_hash,
        "machine": machine,
    }


def stable_dumps(obj: Any, float_fmt: str = ".12g") -> str:
    """Serialize with stable float formatting and sorted keys."""

    def _normalize(val: Any) -> Any:
        if isinstance(val, float):
            return format(val, float_fmt)
        if isinstance(val, dict):
            return {str(k): _normalize(v) for k, v in sorted(val.items(), key=lambda kv: str(kv[0]))}
        if isinstance(val, (list, tuple)):
            return [_normalize(v) for v in val]
        return val

    return json.dumps(_normalize(obj), sort_keys=True, separators=(",", ":"))
