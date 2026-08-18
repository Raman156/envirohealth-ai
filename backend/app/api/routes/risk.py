import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.risk import RiskPredictionResponse
from app.services.risk_service import calculate_and_store_risk, get_latest_risk_score

router = APIRouter(prefix="/risk", tags=["Risk"])


def _parse_explanation(score) -> list:
    if not score.explanation:
        return []
    if isinstance(score.explanation, list):
        return score.explanation
    try:
        return json.loads(score.explanation)
    except Exception:
        return [str(score.explanation)]


@router.get("/{location_id}", response_model=RiskPredictionResponse)
async def get_risk(location_id: str, db: AsyncSession = Depends(get_db)):
    score = await get_latest_risk_score(db, location_id)
    if not score:
        score = await calculate_and_store_risk(db, location_id)
    return RiskPredictionResponse(
        location_id=score.location_id,
        risk_type="general",
        risk_score=score.overall_score,
        risk_level=score.risk_level,
        confidence=score.confidence,
        trend=score.trend or "STABLE",
        explanation=_parse_explanation(score),
        model_version=score.model_version,
        calculated_at=score.calculated_at,
    )


@router.post("/{location_id}/recalculate", response_model=RiskPredictionResponse)
async def recalculate_risk(location_id: str, db: AsyncSession = Depends(get_db)):
    score = await calculate_and_store_risk(db, location_id)
    return RiskPredictionResponse(
        location_id=score.location_id,
        risk_type="general",
        risk_score=score.overall_score,
        risk_level=score.risk_level,
        confidence=score.confidence,
        trend=score.trend or "STABLE",
        explanation=_parse_explanation(score),
        model_version=score.model_version,
        calculated_at=score.calculated_at,
    )
