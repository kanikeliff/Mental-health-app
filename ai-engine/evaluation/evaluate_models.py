# evaluation/evaluate_models.py
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from training.dataset_loader import load_recommendation_dataset
from inference.recommendation_logic import IBCFRecommender


def hit_rate_at_k(model: IBCFRecommender, test_rows, k: int) -> float:
    hits = 0
    total = 0
    for (u, true_item) in test_rows:
        recs = model.recommend(u, k=k)
        rec_items = [r.item_id for r in recs]
        hits += int(true_item in rec_items)
        total += 1
    return hits / max(total, 1)


def mrr_at_k(model: IBCFRecommender, test_rows, k: int) -> float:
    rr = []
    for (u, true_item) in test_rows:
        recs = model.recommend(u, k=k)
        rec_items = [r.item_id for r in recs]
        if true_item in rec_items:
            rank = rec_items.index(true_item) + 1
            rr.append(1.0 / rank)
        else:
            rr.append(0.0)
    return float(np.mean(rr)) if rr else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratings", default="")
    ap.add_argument("--items", default="")
    ap.add_argument("--sample", default="data/sample_inputs.json")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--out", default="evaluation/results.json")
    args = ap.parse_args()

    ds = load_recommendation_dataset(
        ratings_csv=args.ratings.strip() or None,
        items_csv=args.items.strip() or None,
        sample_inputs_json=args.sample.strip() or None,
    )

    # leave-one-out: last rating per user as test
    df = ds.ratings.copy()
    df["timestamp"] = df["timestamp"].astype(float)
    df = df.sort_values(["user_id", "timestamp"], ascending=[True, True])

    test_rows = []
    train_parts = []
    for u, g in df.groupby("user_id"):
        if len(g) < 2:
            train_parts.append(g)
            continue
        test = g.iloc[-1]
        train = g.iloc[:-1]
        test_rows.append((str(test["user_id"]), str(test["item_id"])))
        train_parts.append(train)

    train_df = np.concatenate([t.values for t in train_parts], axis=0)
    train_df = ds.ratings.iloc[:0].append(  # preserve columns
        [dict(zip(ds.ratings.columns, row)) for row in train_df],
        ignore_index=True
    )

    model = IBCFRecommender()
    model.fit(train_df, ds.items)

    results = {
        "k": args.k,
        "num_users": int(ds.ratings["user_id"].nunique()),
        "num_items": int(ds.ratings["item_id"].nunique()),
        "num_test": int(len(test_rows)),
        "HitRate@k": float(hit_rate_at_k(model, test_rows, args.k)),
        "MRR@k": float(mrr_at_k(model, test_rows, args.k)),
    }

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"[OK] Wrote: {outp}")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()