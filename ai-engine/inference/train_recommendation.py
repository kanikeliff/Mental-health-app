# training/train_recommendation.py
from __future__ import annotations

import argparse
import time
from pathlib import Path

from training.dataset_loader import load_recommendation_dataset
from inference.recommendation_logic import IBCFRecommender


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratings", default="", help="Path to ratings.csv (user_id,item_id,rating,timestamp?)")
    ap.add_argument("--items", default="", help="Optional items.csv (item_id,title)")
    ap.add_argument("--sample", default="data/sample_inputs.json", help="Fallback sample_inputs.json")
    ap.add_argument("--out", default="models/recommendation/latest", help="Output dir")
    args = ap.parse_args()

    ratings_path = args.ratings.strip() or None
    items_path = args.items.strip() or None
    sample_path = args.sample.strip() or None

    ds = load_recommendation_dataset(
        ratings_csv=ratings_path,
        items_csv=items_path,
        sample_inputs_json=sample_path,
    )

    model = IBCFRecommender()
    model.fit(ds.ratings, ds.items)

    meta = {
        "model_type": "IBCF-cosine-user-mean",
        "trained_at": int(time.time()),
        "num_users": int(ds.ratings["user_id"].nunique()),
        "num_items": int(ds.ratings["item_id"].nunique()),
        "num_ratings": int(len(ds.ratings)),
    }

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    model.save(out_dir, meta=meta)

    print(f"[OK] Recommendation model saved to: {out_dir}")


if __name__ == "__main__":
    main()