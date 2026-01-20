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
    ratings_csv: Optional[str | Path] = None,
    items_csv: Optional[str | Path] = None,
    sample_inputs_json: Optional[str | Path] = None,
) -> RecDataset:
    """
    Priority:
      1) ratings_csv (+optional items_csv)
      2) sample_inputs_json (expects a 'ratings' list inside)
    """

    if ratings_csv:
        ratings = load_ratings_csv(ratings_csv)
        items = load_items_csv(items_csv) if items_csv else None
        return RecDataset(ratings=ratings, items=items)

    if sample_inputs_json:
        obj = load_sample_inputs_json(sample_inputs_json)

        # Expect: {"ratings": [{"user_id":..,"item_id":..,"rating":..,"timestamp":..}, ...], "items":[...]}
        if "ratings" not in obj or not isinstance(obj["ratings"], list):
            raise ValueError("sample_inputs.json must include a list field: ratings")

        ratings = pd.DataFrame(obj["ratings"])
        for col in ["user_id", "item_id", "rating"]:
            if col not in ratings.columns:
                raise ValueError(f"sample_inputs.json ratings missing '{col}'")
        if "timestamp" not in ratings.columns:
            ratings["timestamp"] = 0

        items = None
        if "items" in obj and isinstance(obj["items"], list) and len(obj["items"]) > 0:
            items = pd.DataFrame(obj["items"])
            if "item_id" not in items.columns:
                items = None
            else:
                if "title" not in items.columns:
                    items["title"] = items["item_id"].astype(str)
                items = items[["item_id", "title"]].copy()

        return RecDataset(ratings=ratings[["user_id", "item_id", "rating", "timestamp"]].copy(), items=items)

    raise ValueError("Provide either ratings_csv or sample_inputs_json")