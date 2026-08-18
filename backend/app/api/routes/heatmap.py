from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.db.base import get_db
from app.schemas.heatmap import HeatmapResponse, HeatmapPoint
from app.services.risk_service import get_all_latest_risk_scores
from app.services.environment_service import get_latest_env_by_parameter
from app.analytics.risk_calculator import get_risk_level

router = APIRouter(prefix="/heatmap", tags=["Heatmap"])


@router.get("/risk", response_model=HeatmapResponse)
async def risk_heatmap(db: AsyncSession = Depends(get_db)):
    data = await get_all_latest_risk_scores(db)
    points = []
    for item in data:
        loc = item["location"]
        score = item["score"]
        points.append(HeatmapPoint(
            grid_id=loc.grid_id or str(loc.id)[:8],
            location_id=loc.id,
            location_name=loc.name,
            latitude=loc.latitude,
            longitude=loc.longitude,
            risk_score=score.overall_score if score else 0,
            risk_level=score.risk_level if score else "LOW",
            value=score.overall_score if score else 0,
        ))
    return HeatmapResponse(layer="risk", points=points)


@router.get("/air", response_model=HeatmapResponse)
async def air_heatmap(db: AsyncSession = Depends(get_db)):
    from app.services.location_service import get_all_locations
    locations = await get_all_locations(db)
    since = datetime.utcnow() - timedelta(hours=24)
    points = []
    for loc in locations:
        readings = await get_latest_env_by_parameter(db, loc.id, since)
        aqi = readings.get("aqi", 0)
        risk_score = min(aqi / 5.0, 100)
        points.append(HeatmapPoint(
            grid_id=loc.grid_id or str(loc.id)[:8],
            location_id=loc.id,
            location_name=loc.name,
            latitude=loc.latitude,
            longitude=loc.longitude,
            risk_score=risk_score,
            risk_level=get_risk_level(risk_score),
            value=aqi,
            label=f"AQI: {aqi:.0f}",
        ))
    return HeatmapResponse(layer="air", points=points)


@router.get("/water", response_model=HeatmapResponse)
async def water_heatmap(db: AsyncSession = Depends(get_db)):
    from app.services.location_service import get_all_locations
    from app.analytics.risk_calculator import calculate_water_risk_score
    locations = await get_all_locations(db)
    since = datetime.utcnow() - timedelta(hours=24)
    points = []
    for loc in locations:
        readings = await get_latest_env_by_parameter(db, loc.id, since)
        water_score = calculate_water_risk_score(readings)
        tds = readings.get("water_tds", 0)
        points.append(HeatmapPoint(
            grid_id=loc.grid_id or str(loc.id)[:8],
            location_id=loc.id,
            location_name=loc.name,
            latitude=loc.latitude,
            longitude=loc.longitude,
            risk_score=water_score,
            risk_level=get_risk_level(water_score),
            value=tds,
            label=f"TDS: {tds:.0f} mg/L",
        ))
    return HeatmapResponse(layer="water", points=points)
