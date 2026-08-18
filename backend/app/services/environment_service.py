from typing import List, Optional, Dict
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.environmental_reading import EnvironmentalReading


async def normalize_and_store_reading(db: AsyncSession, reading: EnvironmentalReading) -> EnvironmentalReading:
    """Validate and store an environmental reading after normalization."""
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading


async def get_latest_readings_for_location(
    db: AsyncSession,
    location_id: UUID,
    since: datetime,
) -> List[EnvironmentalReading]:
    result = await db.execute(
        select(EnvironmentalReading)
        .where(
            EnvironmentalReading.location_id == location_id,
            EnvironmentalReading.timestamp >= since,
        )
        .order_by(EnvironmentalReading.timestamp.desc())
    )
    return result.scalars().all()


async def get_latest_env_by_parameter(
    db: AsyncSession,
    location_id: UUID,
    since: datetime,
) -> Dict[str, float]:
    """Return latest value per parameter."""
    readings = await get_latest_readings_for_location(db, location_id, since)
    latest = {}
    for r in readings:
        if r.parameter not in latest:
            latest[r.parameter] = r.value
    return latest


async def get_all_recent_readings(db: AsyncSession, since: datetime) -> List[EnvironmentalReading]:
    result = await db.execute(
        select(EnvironmentalReading)
        .where(EnvironmentalReading.timestamp >= since)
        .order_by(EnvironmentalReading.timestamp.desc())
    )
    return result.scalars().all()
