# inference/predict.py
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from inference.recommendation_logic import IBCFRecommender
from inference.schemas import RecommendResponse, RecItem


DEFAULT_REC_MODEL_DIR = Path("models/recommendation/latest")


def recommend(user_id: str, k: int = 10, model_dir: str | Path = DEFAULT_REC_MODEL_DIR) -> RecommendResponse:
    model = IBCFRecommender.load(model_dir)
    recs = model.recommend(user_id=user_id, k=k)
    return RecommendResponse(
        user_id=user_id,
        results=[RecItem(item_id=r.item_id, score=r.score, explanation=r.explanation) for r in recs],
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="recommend", choices=["recommend"])
    ap.add_argument("--user", required=True)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--model", default=str(DEFAULT_REC_MODEL_DIR))
    args = ap.parse_args()

    if args.task == "recommend":
        out = recommend(args.user, args.k, args.model)
        print(out.model_dump_json(indent=2))


if __name__ == "__main__":
    main()