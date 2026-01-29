"""Utility helpers for lightweight on-device image classification.

This module extracts simple statistical features directly from the raw image
bytes (without requiring heavy dependencies such as Pillow or OpenCV) and wraps
an arbitrary scikit-learn style estimator so it can be used inside the
`image_app` Flask service.
"""
from __future__ import annotations

import math
from typing import Iterable, List

import numpy as np

FEATURE_NAMES: List[str] = [
    "log_length",
    "mean",
    "std",
    "min",
    "max",
    "ratio_high",
    "ratio_low",
    "unique_ratio",
    "entropy",
    "header_png",
    "header_jpg",
    "first_chunk_mean",
    "last_chunk_mean",
    "zero_ratio",
    "energy",
]


def _safe_array(image_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    if arr.size == 0:
        return np.zeros(1, dtype=np.uint8)
    return arr


def extract_image_features(image_bytes: bytes) -> np.ndarray:
    """Convert raw bytes into a deterministic feature vector."""
    arr = _safe_array(image_bytes)
    length = arr.size
    log_length = math.log1p(length)
    mean = float(arr.mean())
    std = float(arr.std())
    min_val = float(arr.min())
    max_val = float(arr.max())
    ratio_high = float((arr > 200).mean())
    ratio_low = float((arr < 55).mean())
    unique_ratio = float(len(np.unique(arr)) / 256.0)
    hist = np.bincount(arr, minlength=256).astype(np.float64)
    prob = hist / hist.sum()
    entropy = float(-(prob * np.log2(prob + 1e-12)).sum())
    header_png = 1.0 if image_bytes.startswith(b"\x89PNG") else 0.0
    header_jpg = 1.0 if image_bytes.startswith(b"\xff\xd8\xff") else 0.0
    chunk = min(2048, length)
    first_chunk_mean = float(arr[:chunk].mean())
    last_chunk_mean = float(arr[-chunk:].mean())
    zero_ratio = float((arr == 0).mean())
    energy = float((np.square(arr).mean()) / (255.0 ** 2))

    return np.array(
        [
            log_length,
            mean,
            std,
            min_val,
            max_val,
            ratio_high,
            ratio_low,
            unique_ratio,
            entropy,
            header_png,
            header_jpg,
            first_chunk_mean,
            last_chunk_mean,
            zero_ratio,
            energy,
        ],
        dtype=np.float32,
    )


class LocalImageModel:
    """Thin wrapper exposing `predict`/`predict_proba` on raw bytes."""

    def __init__(self, estimator, feature_names: Iterable[str] | None = None):
        self.estimator = estimator
        self.feature_names = list(feature_names or FEATURE_NAMES)

    def _vectorize(self, images: Iterable[bytes]) -> np.ndarray:
        return np.vstack([extract_image_features(img) for img in images])

    def predict(self, images: Iterable[bytes]):
        vectors = self._vectorize(images)
        return self.estimator.predict(vectors)

    def predict_proba(self, images: Iterable[bytes]):
        vectors = self._vectorize(images)
        if hasattr(self.estimator, "predict_proba"):
            return self.estimator.predict_proba(vectors)

        # Convert decision scores to pseudo probabilities when estimator lacks it.
        if hasattr(self.estimator, "decision_function"):
            scores = self.estimator.decision_function(vectors)
            scores = np.array(scores, dtype=np.float64).reshape(-1)
            probs = 1.0 / (1.0 + np.exp(-scores))
            probs = probs.reshape(-1, 1)
            return np.hstack([1.0 - probs, probs])

        preds = self.estimator.predict(vectors)
        preds = np.array(preds, dtype=np.float64).reshape(-1, 1)
        return np.hstack([1.0 - preds, preds])

    def decision_function(self, images: Iterable[bytes]):
        vectors = self._vectorize(images)
        if hasattr(self.estimator, "decision_function"):
            return self.estimator.decision_function(vectors)
        proba = self.predict_proba(images)
        return proba[:, 1]
