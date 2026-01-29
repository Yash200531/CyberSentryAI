"""Train the lightweight local image classifier used by `image_app.py`.

The script consumes validated feedback samples (real/fake image reports) and
fits a small logistic regression model on top of byte-level statistics. Running
this gives you an on-device fallback whenever Hugging Face inference is
unavailable.
"""
from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split

from feedback_db import FeedbackDB
from image_model import FEATURE_NAMES, LocalImageModel, extract_image_features

IMAGE_STORAGE_DIR = Path("feedback_data/image_samples")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "image_deepfake_model.pkl"
METRICS_PATH = MODEL_DIR / "image_model_metrics.json"


def resolve_reference(image_id: str, reference: Optional[Union[str, Path]]) -> Optional[Path]:
    if not image_id:
        return None
    if reference and isinstance(reference, (str, Path)):
        path = Path(reference)
        if path.exists():
            return path
    if not IMAGE_STORAGE_DIR.exists():
        return None
    matches = list(IMAGE_STORAGE_DIR.glob(f"{image_id}.*"))
    return matches[0] if matches else None


def gather_samples(db: FeedbackDB, min_reports: int) -> List[Dict]:
    samples: List[Dict] = []
    validated = db.get_validated_image_data()

    def _append_row(image_id: str, reference: Optional[Union[str, Path]], label: str):
        path = resolve_reference(image_id, reference)
        if not path or not path.exists():
            return
        try:
            payload = path.read_bytes()
        except OSError:
            return
        label_norm = label.strip().lower()
        if label_norm not in {"real", "fake"}:
            return
        samples.append({
            "bytes": payload,
            "label": 1 if label_norm == "fake" else 0,
            "image_id": image_id,
            "reference": str(path),
        })

    if not validated.empty:
        for row in validated.itertuples(index=False):
            _append_row(row.image_id, row.reference, row.label)
    else:
        raw_entries = db.get_feedback_data("image")
        for entry in raw_entries:
            votes: Dict[str, int] = {}
            for report in entry.get("user_reports", []):
                label = (report.get("label") or "").strip().lower()
                if label in {"real", "fake"}:
                    votes[label] = votes.get(label, 0) + 1
            if not votes:
                continue
            best_label, count = max(votes.items(), key=lambda item: item[1])
            if count < min_reports:
                continue
            _append_row(entry.get("image_id", ""), entry.get("reference"), best_label)

    return samples


def train_local_model(samples: List[Dict], test_size: float, random_state: int):
    X = np.vstack([extract_image_features(item["bytes"]) for item in samples])
    y = np.array([item["label"] for item in samples], dtype=np.int64)

    if len(np.unique(y)) < 2:
        raise ValueError("Need at least one REAL and one FAKE sample to train the classifier.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    clf = LogisticRegression(max_iter=4000, class_weight="balanced")
    clf.fit(X_train, y_train)

    model = LocalImageModel(clf, feature_names=FEATURE_NAMES)

    y_prob = clf.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "feature_names": FEATURE_NAMES,
    }

    return model, metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the local image deepfake detector.")
    parser.add_argument("--min-reports", type=int, default=2, help="Minimum consistent votes to trust a pending sample.")
    parser.add_argument("--min-samples", type=int, default=6, help="Minimum total labeled samples required before training.")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split ratio for validation metrics.")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed for reproducibility.")
    args = parser.parse_args()

    db = FeedbackDB()
    samples = gather_samples(db, min_reports=args.min_reports)

    if len(samples) < args.min_samples:
        raise SystemExit(
            f"Not enough labeled images ({len(samples)}) to train. Add more validated reports or lower --min-samples."
        )

    model, metrics = train_local_model(samples, test_size=args.test_size, random_state=args.random_state)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved local image model to {MODEL_PATH}")
    print(f"Metrics written to {METRICS_PATH}")


if __name__ == "__main__":
    main()
