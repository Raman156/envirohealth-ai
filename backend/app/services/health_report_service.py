import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.health_report import HealthReport
from app.schemas.health_report import HealthReportCreate
from app.services.location_service import find_nearest_location


async def submit_health_report(db: AsyncSession, data: HealthReportCreate, anonymous_id: str) -> HealthReport:
    location = await find_nearest_location(db, data.latitude, data.longitude)
    if not location:
        raise ValueError("No location found near the provided coordinates")

    report = HealthReport(
        anonymous_user_id=anonymous_id,
        location_id=str(location.id),
        severity=data.severity,
        age_group=data.age_group,
        source="COMMUNITY",
        timestamp=datetime.utcnow(),
    )
    report.symptoms = [s.value for s in data.symptoms]
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def get_reports_for_location(
    db: AsyncSession, location_id, since: datetime, until: Optional[datetime] = None
) -> List[HealthReport]:
    until = until or datetime.utcnow()
    result = await db.execute(
        select(HealthReport).where(
            HealthReport.location_id == str(location_id),
            HealthReport.timestamp >= since,
            HealthReport.timestamp <= until,
        )
    )
    return list(result.scalars().all())


async def get_symptom_counts_for_location(db: AsyncSession, location_id, since: datetime) -> dict:
    reports = await get_reports_for_location(db, location_id, since)
    counts: dict = {}
    for report in reports:
        for symptom in (report.symptoms or []):
            counts[symptom] = counts.get(symptom, 0) + 1
    return counts
