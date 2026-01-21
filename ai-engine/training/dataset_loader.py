# training/dataset_loader.py
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class RecDataset:
    ratings: pd.DataFrame   # columns: user_id, item_id, rating, timestamp(optional)
    items: Optional[pd.DataFrame] = None  # columns: item_id, title(optional)


def load_ratings_csv(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    df = pd.read_csv(p)

    # normalize column names
    df.columns = [c.strip() for c in df.columns]

    required = {"user_id", "item_id", "rating"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"ratings.csv missing columns: {sorted(missing)}. Need {sorted(required)}")

    # timestamp is optional
    if "timestamp" not in df.columns:
        df["timestamp"] = 0

    return df[["user_id", "item_id", "rating", "timestamp"]].copy()


def load_items_csv(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    df = pd.read_csv(p)
    df.columns = [c.strip() for c in df.columns]
    if "item_id" not in df.columns:
        raise ValueError("items.csv must contain item_id")
    if "title" not in df.columns:
        df["title"] = df["item_id"].astype(str)
    return df[["item_id", "title"]].copy()


def load_sample_inputs_json(path: str | Path) -> dict:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_recommendation_dataset(
    *,
    ratings_csv: str | Path | None = None,
    items_csv: str | Path | None = None,
    sample_inputs_json: str | Path | None = None,
) -> RecDataset:
    """
    Loads recommendation dataset from either:
    - CSVs: ratings_csv (+ optional items_csv)
    - or a JSON sample file: sample_inputs_json
    JSON can be:
      1) a dict with "ratings": [...]
      2) a dict with any list that contains user_id,item_id,rating
      3) directly a list of dicts: [{user_id,item_id,rating,...}, ...]
    """

    # ✅ Priority: sample JSON (demo mode)
    if sample_inputs_json:
        obj = load_sample_inputs_json(sample_inputs_json)

        # CASE 1: file is directly a list of dicts
        if isinstance(obj, list):
            ratings = pd.DataFrame(obj)

        # CASE 2: dict with ratings-like list somewhere
        elif isinstance(obj, dict):
            candidate = None

            # Standard key
            if "ratings" in obj and isinstance(obj["ratings"], list):
                candidate = obj["ratings"]
            else:
                # Search any list of dicts that looks like ratings
                for k, v in obj.items():
                    if isinstance(v, list) and v and isinstance(v[0], dict):
                        keys = set(v[0].keys())
                        if {"user_id", "item_id", "rating"}.issubset(keys):
                            candidate = v
                            break

            if candidate is None:
                raise ValueError(
                    "sample_inputs.json does not contain a ratings-like list. "
                    "Expected a list of dicts containing user_id,item_id,rating."
                )

            ratings = pd.DataFrame(candidate)

        else:
            raise ValueError("sample_inputs.json must be a dict or a list")

        # Validate required columns
        for col in ["user_id", "item_id", "rating"]:
            if col not in ratings.columns:
                raise ValueError(f"sample_inputs.json ratings missing '{col}'")

        # timestamp optional
        if "timestamp" not in ratings.columns:
            ratings["timestamp"] = 0

        # Optional items list
        items = None
        if isinstance(obj, dict) and "items" in obj and isinstance(obj["items"], list) and obj["items"]:
            tmp = pd.DataFrame(obj["items"])
            if "item_id" in tmp.columns:
                if "title" not in tmp.columns:
                    tmp["title"] = tmp["item_id"].astype(str)
                items = tmp[["item_id", "title"]].copy()

        return RecDataset(
            ratings=ratings[["user_id", "item_id", "rating", "timestamp"]].copy(),
            items=items,
        )

    # ✅ Otherwise: CSV mode
    if not ratings_csv:
        raise ValueError("You must provide either sample_inputs_json or ratings_csv")

    ratings = load_ratings_csv(ratings_csv)
    items = load_items_csv(items_csv) if items_csv else None
    return RecDataset(ratings=ratings, items=items)
