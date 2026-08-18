from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.health_report_service import get_reports_for_location
from app.services.environment_service import get_latest_readings_for_location
from app.services.location_service import get_location_by_id
from app.analytics.aggregation import aggregate_symptoms, aggregate_env_readings, get_period_bounds
from app.schemas.history import HistoryResponse, HistoryDataPoint
from collections import defaultdict


PERIOD_MAP = {
    "24h": "24h", "7d": "7d", "30d": "30d",
    "90d": "90d", "180d": "180d", "1y": "1y",
}


async def get_location_history(
    db: AsyncSession,
    location_id: UUID,
    period: str = "30d",
) -> HistoryResponse:
    location = await get_location_by_id(db, location_id)
    if not location:
        raise ValueError("Location not found")

    period_key = PERIOD_MAP.get(period, "30d")
    start, end = get_period_bounds(period_key)

    reports = await get_reports_for_location(db, location_id, start, end)
    env_readings = await get_latest_readings_for_location(db, location_id, start)

    health_summary = aggregate_symptoms(reports)
    env_summary = aggregate_env_readings(env_readings)

    # Build time series — bucket by day
    health_series = _build_health_series(reports, start, end)
    env_series = _build_env_series(env_readings, start, end)

    return HistoryResponse(
        location=location.name,
        location_id=str(location_id),
        period=period,
        health=health_summary,
        environment={
            "average_aqi": round(env_summary.get("aqi", 0), 1),
            "average_temperature": round(env_summary.get("temperature", 0), 1),
            "average_humidity": round(env_summary.get("humidity", 0), 1),
            "average_pm25": round(env_summary.get("pm25", 0), 1),
            "average_water_ph": round(env_summary.get("water_ph", 0), 1),
        },
        health_series=health_series,
        environment_series=env_series,
    )


def _build_health_series(reports, start, end):
    """Group symptom reports by day."""
    daily = defaultdict(lambda: defaultdict(int))
    for r in reports:
        day = r.timestamp.strftime("%Y-%m-%d")
        for s in (r.symptoms or []):
            daily[day][s] += 1

    series = defaultdict(list)
    for day in sorted(daily.keys()):
        for symptom, count in daily[day].items():
            series[symptom].append(HistoryDataPoint(timestamp=day, value=count))
    return dict(series)


def _build_env_series(readings, start, end):
    """Group env readings by day, averaged per parameter."""
    daily = defaultdict(lambda: defaultdict(list))
    for r in readings:
        day = r.timestamp.strftime("%Y-%m-%d")
        daily[day][r.parameter].append(r.value)

    series = defaultdict(list)
    for day in sorted(daily.keys()):
        for param, values in daily[day].items():
            avg = sum(values) / len(values)
            series[param].append(HistoryDataPoint(timestamp=day, value=round(avg, 2)))
    return dict(series)
