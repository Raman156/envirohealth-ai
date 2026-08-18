import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.base import get_db
from app.models.user import User
from app.models.health_report import HealthReport
from app.models.sensor import Sensor, SensorStatus
from app.models.environmental_reading import EnvironmentalReading
from app.models.alert import Alert
from app.schemas.sensor import SensorResponse
from app.schemas.alert import AlertResponse
from app.api.dependencies import require_admin
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def admin_stats(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_reports = (await db.execute(select(func.count(HealthReport.id)))).scalar() or 0
    total_sensors = (await db.execute(select(func.count(Sensor.id)))).scalar() or 0
    online_sensors = (await db.execute(
        select(func.count(Sensor.id)).where(Sensor.status == SensorStatus.ONLINE)
    )).scalar() or 0
    offline_sensors = (await db.execute(
        select(func.count(Sensor.id)).where(Sensor.status == SensorStatus.OFFLINE)
    )).scalar() or 0
    total_readings = (await db.execute(select(func.count(EnvironmentalReading.id)))).scalar() or 0
    active_alerts = (await db.execute(
        select(func.count(Alert.id)).where(Alert.is_active == True)
    )).scalar() or 0

    return {
        "total_users": total_users,
        "total_health_reports": total_reports,
        "total_sensors": total_sensors,
        "online_sensors": online_sensors,
        "offline_sensors": offline_sensors,
        "total_env_readings": total_readings,
        "active_alerts": active_alerts,
    }


@router.get("/sensors", response_model=List[SensorResponse])
async def admin_sensors(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Sensor).order_by(Sensor.status))
    return list(result.scalars().all())


@router.get("/alerts", response_model=List[AlertResponse])
async def admin_alerts(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Alert).order_by(Alert.created_at.desc()).limit(50))
    return list(result.scalars().all())


@router.patch("/sensors/{sensor_id}/deactivate")
async def deactivate_sensor(sensor_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    sensor.is_active = "false"
    sensor.status = SensorStatus.OFFLINE
    await db.commit()
    return {"message": "Sensor deactivated"}
