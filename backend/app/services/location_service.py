import math
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.location import Location
from app.schemas.location import LocationCreate


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return distance in km between two lat/lng points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def get_location_by_id(db: AsyncSession, location_id) -> Optional[Location]:
    result = await db.execute(select(Location).where(Location.id == str(location_id)))
    return result.scalar_one_or_none()


async def get_all_locations(db: AsyncSession) -> List[Location]:
    result = await db.execute(select(Location))
    return list(result.scalars().all())


async def find_nearest_location(db: AsyncSession, lat: float, lng: float) -> Optional[Location]:
    locations = await get_all_locations(db)
    if not locations:
        return None
    return min(locations, key=lambda l: _haversine_km(lat, lng, l.latitude, l.longitude))


async def get_nearby_locations(db: AsyncSession, lat: float, lng: float, radius_km: float = 5.0) -> List[Location]:
    locations = await get_all_locations(db)
    nearby = [l for l in locations if _haversine_km(lat, lng, l.latitude, l.longitude) <= radius_km]
    nearby.sort(key=lambda l: _haversine_km(lat, lng, l.latitude, l.longitude))
    return nearby if nearby else locations  # fallback: return all if none within radius


async def create_location(db: AsyncSession, data: LocationCreate) -> Location:
    loc = Location(
        name=data.name, city=data.city, state=data.state, country=data.country,
        latitude=data.latitude, longitude=data.longitude, grid_id=data.grid_id,
    )
    db.add(loc)
    await db.commit()
    await db.refresh(loc)
    return loc
