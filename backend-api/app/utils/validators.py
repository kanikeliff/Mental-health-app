def mood_score_guard(score: int) -> int:
    """
    I validate moodScore because I don't want random bad values in Firestore.
    The iOS app uses 1..5 so I enforce the same rule.
    """
    try:
        score_int = int(score)
    except Exception:
        raise ValueError("moodScore must be an integer")

    if score_int < 1 or score_int > 5:
        raise ValueError("moodScore must be between 1 and 5")

    return score_int
