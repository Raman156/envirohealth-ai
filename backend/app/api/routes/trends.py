from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.base import get_db
from app.schemas.trend import TrendsResponse
from app.services.trend_service import get_trends_for_location

router = APIRouter(prefix="/trends", tags=["Trends"])


@router.get("/{location_id}", response_model=TrendsResponse)
async def get_trends(
    location_id: str,
    period_days: int = Query(default=7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    try:
        lid = UUID(location_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid location ID")
    return await get_trends_for_location(db, lid, period_days)
