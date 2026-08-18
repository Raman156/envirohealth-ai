from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.base import get_db
from app.schemas.history import HistoryResponse
from app.services.history_service import get_location_history

router = APIRouter(prefix="/history", tags=["History"])

VALID_PERIODS = {"24h", "7d", "30d", "90d", "180d", "1y"}


@router.get("/{location_id}", response_model=HistoryResponse)
async def get_history(
    location_id: str,
    period: str = Query(default="30d", pattern="^(24h|7d|30d|90d|180d|1y)$"),
    db: AsyncSession = Depends(get_db),
):
    try:
        lid = UUID(location_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid location ID")
    try:
        return await get_location_history(db, lid, period)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
