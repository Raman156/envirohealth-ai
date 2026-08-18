from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.sensor import SensorCreate, SensorResponse
from app.schemas.environmental import SensorReadingIngest, EnvironmentalReadingResponse
from app.services.sensor_service import (
    create_sensor, get_all_sensors, ingest_sensor_reading, get_sensor_by_code
)
from app.api.dependencies import require_admin

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.get("", response_model=List[SensorResponse])
async def list_sensors(db: AsyncSession = Depends(get_db)):
    sensors = await get_all_sensors(db)
    return sensors


@router.post("", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
async def register_sensor(
    data: SensorCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin),
):
    existing = await get_sensor_by_code(db, data.sensor_code)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Sensor code already exists")
    return await create_sensor(db, data)


@router.post("/readings", status_code=status.HTTP_201_CREATED)
async def ingest_readings(data: SensorReadingIngest, db: AsyncSession = Depends(get_db)):
    """Endpoint for sensors to push readings (HTTP-based IoT ingestion)."""
    try:
        stored = await ingest_sensor_reading(db, data)
        return {"message": f"Stored {len(stored)} readings", "sensor_code": data.sensor_code}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Convenience typed endpoints for different sensor types
@router.post("/air", status_code=status.HTTP_201_CREATED)
async def ingest_air(data: SensorReadingIngest, db: AsyncSession = Depends(get_db)):
    return await ingest_readings(data, db)


@router.post("/water", status_code=status.HTTP_201_CREATED)
async def ingest_water(data: SensorReadingIngest, db: AsyncSession = Depends(get_db)):
    return await ingest_readings(data, db)


@router.post("/weather", status_code=status.HTTP_201_CREATED)
async def ingest_weather(data: SensorReadingIngest, db: AsyncSession = Depends(get_db)):
    return await ingest_readings(data, db)
