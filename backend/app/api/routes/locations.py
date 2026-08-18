from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.location import LocationResponse
from app.services.location_service import get_all_locations, get_nearby_locations, get_location_by_id

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("", response_model=List[LocationResponse])
async def list_locations(db: AsyncSession = Depends(get_db)):
    return await get_all_locations(db)


@router.get("/nearby", response_model=List[LocationResponse])
async def nearby_locations(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius: float = Query(default=5.0, ge=0.1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await get_nearby_locations(db, lat, lng, radius)


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(location_id: str, db: AsyncSession = Depends(get_db)):
    from uuid import UUID
    try:
        loc = await get_location_by_id(db, UUID(location_id))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid location ID")
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc
