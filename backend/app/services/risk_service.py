import json
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.risk_score import RiskScore
from app.services.health_report_service import get_symptom_counts_for_location
from app.services.environment_service import get_latest_env_by_parameter
from app.ml.predictor import predict_risk
from app.analytics.trend_detector import calculate_trend


async def calculate_and_store_risk(db: AsyncSession, location_id) -> RiskScore:
    now = datetime.utcnow()
    since_24h = now - timedelta(hours=24)
    since_7d = now - timedelta(days=7)
    since_prev_7d = now - timedelta(days=14)

    symptom_counts = await get_symptom_counts_for_location(db, location_id, since_7d)
    env_readings = await get_latest_env_by_parameter(db, location_id, since_24h)
    historical_avg = await get_historical_avg_score(db, location_id, since_7d)

    prev_counts = await get_symptom_counts_for_location(db, location_id, since_prev_7d)
    symptom_trends = {}
    for symptom in set(list(symptom_counts.keys()) + list(prev_counts.keys())):
        curr = symptom_counts.get(symptom, 0)
        prev = prev_counts.get(symptom, 0)
        change, _ = calculate_trend(curr, prev)
        symptom_trends[symptom] = change

    prediction = predict_risk(location_id, env_readings, symptom_counts, symptom_trends, historical_avg)

    from app.services.location_service import get_location_by_id
    location = await get_location_by_id(db, location_id)

    score = RiskScore(
        location_id=str(location_id),
        grid_id=location.grid_id if location else None,
        overall_score=prediction["risk_score"],
        risk_level=prediction["risk_level"],
        health_score=prediction.get("health_score"),
        air_score=prediction.get("air_score"),
        water_score=prediction.get("water_score"),
        weather_score=prediction.get("weather_score"),
        historical_score=prediction.get("historical_score"),
        trend=prediction.get("trend"),
        explanation=json.dumps(prediction.get("explanation", [])),
        model_version=prediction.get("model_version", "rule_based_v1"),
        confidence=prediction.get("confidence", 0.7),
        calculated_at=now,
    )
    db.add(score)
    await db.commit()
    await db.refresh(score)
    return score


async def get_latest_risk_score(db: AsyncSession, location_id) -> Optional[RiskScore]:
    result = await db.execute(
        select(RiskScore)
        .where(RiskScore.location_id == str(location_id))
        .order_by(RiskScore.calculated_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_historical_avg_score(db: AsyncSession, location_id, since: datetime) -> float:
    result = await db.execute(
        select(RiskScore)
        .where(RiskScore.location_id == str(location_id), RiskScore.calculated_at >= since)
        .order_by(RiskScore.calculated_at.desc())
        .limit(10)
    )
    scores = result.scalars().all()
    if not scores:
        return 30.0
    return sum(s.overall_score for s in scores) / len(scores)


async def get_all_latest_risk_scores(db: AsyncSession) -> List[dict]:
    from app.services.location_service import get_all_locations
    locations = await get_all_locations(db)
    result = []
    for loc in locations:
        score = await get_latest_risk_score(db, loc.id)
        result.append({"location": loc, "score": score})
    return result
