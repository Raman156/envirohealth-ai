from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.sensor import Sensor, SensorStatus
from app.models.environmental_reading import EnvironmentalReading
from app.schemas.sensor import SensorCreate
from app.schemas.environmental import SensorReadingIngest

PARAMETER_UNITS = {
    "pm25": "µg/m³", "pm10": "µg/m³", "aqi": "AQI",
    "co": "ppm", "no2": "µg/m³", "so2": "µg/m³", "o3": "µg/m³",
    "temperature": "°C", "humidity": "%", "rainfall": "mm",
    "wind_speed": "km/h", "wind_direction": "°",
    "water_ph": "pH", "water_turbidity": "NTU",
    "water_tds": "mg/L", "water_temperature": "°C",
    "uv_index": "UV", "pressure": "hPa",
}


async def get_sensor_by_code(db: AsyncSession, sensor_code: str) -> Optional[Sensor]:
    result = await db.execute(select(Sensor).where(Sensor.sensor_code == sensor_code))
    return result.scalar_one_or_none()


async def get_all_sensors(db: AsyncSession) -> List[Sensor]:
    result = await db.execute(select(Sensor))
    return list(result.scalars().all())


async def create_sensor(db: AsyncSession, data: SensorCreate) -> Sensor:
    sensor = Sensor(
        sensor_code=data.sensor_code,
        name=data.name,
        type=data.type,
        location_id=str(data.location_id) if data.location_id else None,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    db.add(sensor)
    await db.commit()
    await db.refresh(sensor)
    return sensor


async def ingest_sensor_reading(db: AsyncSession, data: SensorReadingIngest) -> List[EnvironmentalReading]:
    sensor = await get_sensor_by_code(db, data.sensor_code)
    if not sensor:
        raise ValueError(f"Sensor '{data.sensor_code}' not found")
    if sensor.is_active != "true":
        raise ValueError(f"Sensor '{data.sensor_code}' is not active")

    sensor.last_seen = datetime.utcnow()
    sensor.status = SensorStatus.ONLINE

    stored = []
    for param, value in data.readings.items():
        param_lower = param.lower()
        unit = PARAMETER_UNITS.get(param_lower, "unknown")
        reading = EnvironmentalReading(
            location_id=str(sensor.location_id) if sensor.location_id else None,
            sensor_id=str(sensor.id),
            parameter=param_lower,
            value=value,
            unit=unit,
            source=data.sensor_code,
            source_type="SENSOR",
            timestamp=data.timestamp,
            quality_score=1.0,
        )
        db.add(reading)
        stored.append(reading)

    await db.commit()
    return stored


async def check_and_update_sensor_status(db: AsyncSession):
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(minutes=15)
    result = await db.execute(
        select(Sensor).where(
            and_(Sensor.last_seen < cutoff, Sensor.status == SensorStatus.ONLINE)
        )
    )
    for sensor in result.scalars().all():
        sensor.status = SensorStatus.OFFLINE
    await db.commit()
