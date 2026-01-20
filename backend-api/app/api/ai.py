from __future__ import annotations

from fastapi import APIRouter, Query
from app.services.ai_bridge import get_recommendations, ai_engine_healthcheck

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/recommend")
def recommend(
    user_id: str = Query(...),
    k: int = Query(10, ge=1, le=50),
):
    return get_recommendations(user_id=user_id, k=k)

@router.get("/health")
def ai_health():
    return ai_engine_healthcheck()