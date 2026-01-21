from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


@dataclass
class EmotionDataset:
    texts: List[str]
    labels: List[str]


def _load_samples(sample_json_path: str | Path) -> EmotionDataset:
    p = Path(sample_json_path)
    obj = json.loads(p.read_text(encoding="utf-8"))

    # allow either {"samples":[...]} or direct list
    if isinstance(obj, dict) and "samples" in obj:
        samples = obj["samples"]
    elif isinstance(obj, list):
        samples = obj
    else:
        raise ValueError("sample_inputs.json must contain 'samples' list or be a list of samples")

    if not isinstance(samples, list) or len(samples) == 0:
        raise ValueError("'samples' must be a non-empty list")

    texts: List[str] = []
    labels: List[str] = []
    for i, s in enumerate(samples):
        if not isinstance(s, dict):
            raise ValueError(f"sample {i} is not an object")
        if "text" not in s or "label" not in s:
            raise ValueError(f"sample {i} must have 'text' and 'label'")
        texts.append(str(s["text"]))
        labels.append(str(s["label"]))

    return EmotionDataset(texts=texts, labels=labels)


def train_emotion_model(texts: List[str], labels: List[str]) -> Pipeline:
    """
    Simple NLP classifier:
    TF-IDF (word ngrams) + Logistic Regression
    """
    clf = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("lr", LogisticRegression(max_iter=1000)),
        ]
    )
    clf.fit(texts, labels)
    return clf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True, help="Path to sample_inputs.json (must include samples list)")
    ap.add_argument("--out", required=True, help="Output folder, e.g. models/emotion/latest")
    args = ap.parse_args()

    ds = _load_samples(args.sample)

    model = train_emotion_model(ds.texts, ds.labels)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save model
    joblib.dump(model, out_dir / "model.joblib")

    # Save label mapping (string->int) for UI/debug
    uniq = sorted(set(ds.labels))
    mapping = {lab: i for i, lab in enumerate(uniq)}
    (out_dir / "label_mapping.json").write_text(json.dumps(mapping, indent=2), encoding="utf-8")

    print(f"✅ Emotion model saved to: {out_dir / 'model.joblib'}")
    print(f"✅ Label mapping saved to: {out_dir / 'label_mapping.json'}")
    print(f"Classes: {uniq}")


if __name__ == "__main__":
    main()
