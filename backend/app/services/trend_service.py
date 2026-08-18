from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.health_report_service import get_symptom_counts_for_location
from app.analytics.trend_detector import build_symptom_trends
from app.schemas.trend import TrendsResponse, TrendItem as SchemaTrendItem


async def get_trends_for_location(db: AsyncSession, location_id: UUID, period_days: int = 7) -> TrendsResponse:
    now = datetime.utcnow()
    current_start = now - timedelta(days=period_days)
    previous_start = now - timedelta(days=period_days * 2)
    previous_end = current_start

    current_counts = await get_symptom_counts_for_location(db, location_id, current_start)

    from app.services.health_report_service import get_reports_for_location
    prev_reports = await get_reports_for_location(db, location_id, previous_start, previous_end)
    prev_only: dict = {}
    for r in prev_reports:
        for s in (r.symptoms or []):
            prev_only[s] = prev_only.get(s, 0) + 1

    raw_trends = build_symptom_trends(current_counts, prev_only)

    # Convert dataclass TrendItems to Pydantic schema TrendItems
    schema_trends = [
        SchemaTrendItem(
            condition=t.condition,
            current=t.current,
            previous=t.previous,
            change_percent=t.change_percent,
            direction=t.direction,
        )
        for t in raw_trends
    ]

    return TrendsResponse(
        location_id=str(location_id),
        period_days=period_days,
        trends=schema_trends,
    )
