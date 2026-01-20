from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple

ASSESS_DIR = Path(__file__).resolve().parents[1] / "data" / "assessments"

SUPPORTED = {
    "phq9": "phq9.json",
    "who5": "who5.json",
    "scl90_short": "scl90_short.json",
}

def load_assessment(name: str) -> Dict[str, Any]:
    if name not in SUPPORTED:
        raise ValueError(f"Unknown assessment: {name}")
    path = ASSESS_DIR / SUPPORTED[name]
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def validate_answers(assessment: Dict[str, Any], answers: Dict[str, int]) -> Tuple[bool, List[str]]:
    missing = []
    qids = [q["id"] for q in assessment["questions"]]
    for qid in qids:
        if qid not in answers:
            missing.append(qid)

    mn = int(assessment["scale"]["min"])
    mx = int(assessment["scale"]["max"])
    bad = [k for k, v in answers.items() if not isinstance(v, int) or v < mn or v > mx]

    errors = []
    if missing:
        errors.append(f"Missing answers for: {missing[:5]}{'...' if len(missing)>5 else ''}")
    if bad:
        errors.append(f"Out-of-range answers: {bad[:5]}{'...' if len(bad)>5 else ''}")
    return (len(errors) == 0), errors

def score_assessment(name: str, answers: Dict[str, int]) -> Dict[str, Any]:
    a = load_assessment(name)
    ok, errors = validate_answers(a, answers)
    if not ok:
        return {"ok": False, "errors": errors}

    total = sum(int(v) for v in answers.values())
    result: Dict[str, Any] = {"ok": True, "name": name, "total_score": total}

    # Simple interpretations (demo-safe, NOT diagnosis)
    if name == "phq9":
        # PHQ-9 total 0-27
        if total <= 4: level = "minimal"
        elif total <= 9: level = "mild"
        elif total <= 14: level = "moderate"
        elif total <= 19: level = "moderately_severe"
        else: level = "severe"
        result["level"] = level
        # Q9 self-harm signal (not diagnosis, just flag)
        q9 = int(answers.get("phq9_q9", 0))
        result["safety_flag"] = q9 >= 1
        result["note"] = "This is a screening score, not a diagnosis."
    elif name == "who5":
        # WHO-5 raw 0-25; common to scale *4 to 0-100
        result["score_0_100"] = total * 4
        result["note"] = "Higher scores indicate better well-being (screening, not diagnosis)."
    else:
        # scl90_short
        result["avg_item_score"] = round(total / max(len(answers), 1), 3)
        result["note"] = "Demo short form (not clinical)."

    result["ts"] = int(time.time())
    return result
