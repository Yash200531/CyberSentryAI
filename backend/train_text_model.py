import json
import pickle
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

DATASETS_DIR = Path("../datasets")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"https?://\S+|www\.\S+", " <URL> ", text)
    text = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", " <EMAIL> ", text)
    text = re.sub(r"\b\+?\d[\d\s\-().]{7,}\b", " <PHONE> ", text)
    text = re.sub(r"\b\d+(?:[.,]\d+)?\b", " <NUM> ", text)
    text = re.sub(r"[$₹€£]", " <CUR> ", text)
    text = re.sub(r"[^\w\s<>]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_dataset(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding="latin-1")
    col_map = {c.lower(): c for c in df.columns}

    if {"v1", "v2"}.issubset(col_map):
        df = df.rename(columns={col_map["v1"]: "label", col_map["v2"]: "text"})
    elif {"label", "text"}.issubset(col_map):
        df = df.rename(columns={col_map["label"]: "label", col_map["text"]: "text"})
    elif {"category", "message"}.issubset(col_map):
        df = df.rename(columns={col_map["category"]: "label", col_map["message"]: "text"})
    else:
        return pd.DataFrame(columns=["label", "text"])

    df = df[["label", "text"]].dropna()
    df["text"] = df["text"].astype(str).str.strip().map(normalize_text)
    df["label"] = df["label"].astype(str).str.strip().str.lower()
    return df


def load_all_datasets() -> pd.DataFrame:
    csv_files = sorted(DATASETS_DIR.glob("*.csv"))
    data_frames = []

    for csv_path in csv_files:
        if "url" in csv_path.name.lower():
            continue
        df = load_dataset(csv_path)
        if not df.empty:
            df["source"] = csv_path.name
            data_frames.append(df)

    if not data_frames:
        raise FileNotFoundError("No compatible text datasets found in datasets folder.")

    data = pd.concat(data_frames, ignore_index=True)
    data = data.dropna(subset=["label", "text"]).reset_index(drop=True)
    return data


data = load_all_datasets()

X = data["text"]
y = data["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

pipeline = Pipeline(
    steps=[
        ("tfidf", TfidfVectorizer(stop_words="english")),
        ("svm", LinearSVC(class_weight="balanced")),
    ]
)

param_grid = {
    "tfidf__ngram_range": [(1, 2), (1, 3)],
    "tfidf__min_df": [1, 2, 3],
    "tfidf__max_df": [0.9, 1.0],
    "tfidf__sublinear_tf": [True, False],
    "svm__C": [0.5, 1.0, 2.0],
}

grid = GridSearchCV(
    pipeline,
    param_grid=param_grid,
    scoring="f1_macro",
    n_jobs=-1,
    cv=5,
    verbose=1,
)

grid.fit(X_train, y_train)
best_pipeline = grid.best_estimator_
print("Best Params:", grid.best_params_)

best_vectorizer = best_pipeline.named_steps["tfidf"]
best_svm = best_pipeline.named_steps["svm"]

X_train_vec = best_vectorizer.transform(X_train)
X_test_vec = best_vectorizer.transform(X_test)

model = CalibratedClassifierCV(best_svm, method="sigmoid", cv=5)
model.fit(X_train_vec, y_train)

classes = list(model.classes_)
pos_label = "spam" if "spam" in classes else classes[-1]
pos_index = classes.index(pos_label)

y_prob = model.predict_proba(X_test_vec)[:, pos_index]
y_true = (y_test == pos_label).astype(int).values

precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
f1_scores = (2 * precision * recall) / np.clip(precision + recall, 1e-9, None)
best_idx = int(np.argmax(f1_scores))
best_threshold = thresholds[max(best_idx - 1, 0)] if len(thresholds) else 0.5

y_pred = np.where(y_prob >= best_threshold, pos_label, [c for c in classes if c != pos_label][0])

acc = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
report = classification_report(y_test, y_pred, output_dict=True)
roc_auc = roc_auc_score(y_true, y_prob)

print("Model Accuracy:", acc)
print("Best Threshold:", best_threshold)
print("Confusion Matrix:\n", conf_matrix)
print("Classification Report:\n", classification_report(y_test, y_pred))
print("ROC-AUC:", roc_auc)

metrics = {
    "best_params": grid.best_params_,
    "best_threshold": float(best_threshold),
    "accuracy": float(acc),
    "roc_auc": float(roc_auc),
    "confusion_matrix": conf_matrix.tolist(),
    "classification_report": report,
    "classes": classes,
    "train_samples": int(len(X_train)),
    "test_samples": int(len(X_test)),
}

with open(MODEL_DIR / "text_model_metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

with open(MODEL_DIR / "text_scam_model.pkl", "wb") as f:
    pickle.dump((model, best_vectorizer), f)

print("SVM Model saved successfully!")
