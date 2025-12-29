"""Fit a simple logistic regression boundary for S2 dominance in proxy space."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List

import numpy as np


def parse_float(v: str) -> float:
    try:
        return float(v)
    except Exception:
        return float("nan")


def read_proxies_csv(path: Path) -> Dict[str, np.ndarray]:
    rows: List[Dict] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: parse_float(v) for k, v in row.items()})
    arr = lambda key: np.array([r.get(key, np.nan) for r in rows], dtype=float)
    return {
        "first_energy": arr("first_energy"),
        "spacing_mean": arr("spacing_mean"),
        "d_spacing": arr("Nucleon_like_d_spacing"),
        "y": np.array([r.get("has_s2_dominant", 0) for r in rows], dtype=int),
    }


def main():
    parser = argparse.ArgumentParser(description="Fit logistic regression for S2 dominance.")
    parser.add_argument("--proxies-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, roc_auc_score
    except ImportError as e:
        raise SystemExit("scikit-learn is required for fit_s2_logit") from e

    data = read_proxies_csv(args.proxies_csv)
    X = np.vstack([data["first_energy"], data["spacing_mean"], data["d_spacing"]]).T
    y = data["y"]

    mask = np.isfinite(X).all(axis=1)
    X = X[mask]
    y = y[mask]
    if X.shape[0] == 0:
        raise SystemExit("No valid rows to fit.")

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    prob = model.predict_proba(X)[:, 1]
    auc = roc_auc_score(y, prob)
    acc = accuracy_score(y, model.predict(X))

    out_dir = args.output
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "coefficients": {
            "intercept": float(model.intercept_[0]),
            "first_energy": float(model.coef_[0][0]),
            "spacing_mean": float(model.coef_[0][1]),
            "nucleon_like_d_spacing": float(model.coef_[0][2]),
        },
        "metrics": {"auc": float(auc), "accuracy": float(acc)},
    }
    (out_dir / "s2_logit_summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
