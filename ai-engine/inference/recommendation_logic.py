# inference/recommendation_logic.py
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RecResult:
    item_id: str
    score: float
    explanation: Optional[str] = None


class IBCFRecommender:
    """
    Item-Based Collaborative Filtering (cosine similarity)
    with per-user mean normalization:
        r'_{u,i} = r_{u,i} - mean_u
    """

    def __init__(self):
        self.item_ids: List[str] = []
        self.user_ids: List[str] = []
        self.item_index: Dict[str, int] = {}
        self.user_index: Dict[str, int] = {}
        self.user_mean: np.ndarray | None = None

        self.sim: np.ndarray | None = None          # item-item similarity
        self.r_norm: np.ndarray | None = None       # user x item normalized ratings
        self.items_title: Dict[str, str] = {}       # optional

    def fit(self, ratings: pd.DataFrame, items: Optional[pd.DataFrame] = None) -> None:
        # ids
        self.user_ids = sorted(ratings["user_id"].astype(str).unique().tolist())
        self.item_ids = sorted(ratings["item_id"].astype(str).unique().tolist())
        self.user_index = {u: i for i, u in enumerate(self.user_ids)}
        self.item_index = {it: j for j, it in enumerate(self.item_ids)}

        n_users = len(self.user_ids)
        n_items = len(self.item_ids)

        # rating matrix
        R = np.zeros((n_users, n_items), dtype=np.float32)
        cnt = np.zeros((n_users, 1), dtype=np.float32)

        for row in ratings.itertuples(index=False):
            u = str(row.user_id)
            it = str(row.item_id)
            r = float(row.rating)
            ui = self.user_index[u]
            ij = self.item_index[it]
            R[ui, ij] = r
            cnt[ui, 0] += 1.0

        # user mean (avoid div by 0)
        sums = R.sum(axis=1, keepdims=True)
        denom = np.maximum(cnt, 1.0)
        self.user_mean = (sums / denom).astype(np.float32)

        # normalize only where rating exists
        mask = (R > 0).astype(np.float32)
        R_norm = (R - self.user_mean) * mask
        self.r_norm = R_norm

        # item vectors = columns (users x items)
        # similarity between item columns
        self.sim = cosine_similarity(R_norm.T)
        np.fill_diagonal(self.sim, 0.0)

        if items is not None:
            # items: item_id, title
            self.items_title = {str(r.item_id): str(r.title) for r in items.itertuples(index=False)}

    def recommend(self, user_id: str, k: int = 10) -> List[RecResult]:
        if self.sim is None or self.r_norm is None or self.user_mean is None:
            raise RuntimeError("Model not trained/loaded")

        u = str(user_id)
        if u not in self.user_index:
            # cold start: return top popular-ish = items with highest total similarity sum (cheap fallback)
            simsums = self.sim.sum(axis=1)
            top_idx = np.argsort(-simsums)[:k]
            return [RecResult(item_id=self.item_ids[j], score=float(simsums[j]), explanation="Cold start fallback.") for j in top_idx]

        ui = self.user_index[u]
        user_vec = self.r_norm[ui]  # normalized ratings

        rated_mask = (user_vec != 0)
        scores = np.zeros(len(self.item_ids), dtype=np.float32)

        # score(item j) = sum_{i rated} sim[j,i] * r_norm[u,i] / (sum |sim[j,i]| + eps)
        eps = 1e-8
        for j in range(len(self.item_ids)):
            if rated_mask[j]:
                scores[j] = -np.inf  # don't recommend already rated
                continue
            sims = self.sim[j]
            numer = np.sum(sims[rated_mask] * user_vec[rated_mask])
            denom = np.sum(np.abs(sims[rated_mask])) + eps
            scores[j] = numer / denom

        top = np.argsort(-scores)[:k]
        results: List[RecResult] = []
        for j in top:
            it = self.item_ids[j]
            expl = self._explain(u, it)
            results.append(RecResult(item_id=it, score=float(scores[j]), explanation=expl))
        return results

    def _explain(self, user_id: str, item_id: str) -> str:
        # simple explanation: top 2 similar-to-rated items
        ui = self.user_index.get(user_id)
        ij = self.item_index.get(item_id)
        if ui is None or ij is None:
            return "Recommended based on similar items."

        user_vec = self.r_norm[ui]
        rated_idx = np.where(user_vec != 0)[0]
        if len(rated_idx) == 0:
            return "Recommended based on similar items."

        sims = self.sim[ij, rated_idx]
        top2 = rated_idx[np.argsort(-sims)[:2]]

        def title(xid: str) -> str:
            return self.items_title.get(xid, xid)

        reasons = [title(self.item_ids[t]) for t in top2]
        return f"Because you liked items similar to: {', '.join(reasons)}."

    def save(self, out_dir: str | Path, meta: Optional[dict] = None) -> None:
        p = Path(out_dir)
        p.mkdir(parents=True, exist_ok=True)

        # np artifacts
        np.save(p / "sim.npy", self.sim)
        np.save(p / "r_norm.npy", self.r_norm)
        np.save(p / "user_mean.npy", self.user_mean)

        # json artifacts
        payload = {
            "user_ids": self.user_ids,
            "item_ids": self.item_ids,
            "items_title": self.items_title,
            "meta": meta or {},
        }
        with (p / "model.json").open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, model_dir: str | Path) -> "IBCFRecommender":
        p = Path(model_dir)

        obj = cls()
        with (p / "model.json").open("r", encoding="utf-8") as f:
            payload = json.load(f)

        obj.user_ids = payload["user_ids"]
        obj.item_ids = payload["item_ids"]
        obj.user_index = {u: i for i, u in enumerate(obj.user_ids)}
        obj.item_index = {it: j for j, it in enumerate(obj.item_ids)}
        obj.items_title = payload.get("items_title", {})

        obj.sim = np.load(p / "sim.npy")
        obj.r_norm = np.load(p / "r_norm.npy")
        obj.user_mean = np.load(p / "user_mean.npy")
        return obj