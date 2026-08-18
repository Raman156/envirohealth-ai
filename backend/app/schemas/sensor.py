from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models.sensor import SensorType, SensorStatus


class SensorCreate(BaseModel):
    sensor_code: str
    name: str
    type: SensorType
    location_id: Optional[UUID] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    metadata: Optional[Dict[str, Any]] = None


class SensorStatusUpdate(BaseModel):
    status: SensorStatus


class SensorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sensor_code: str
    name: str
    type: str
    latitude: float
    longitude: float
    status: str
    last_seen: Optional[datetime] = None
    location_id: Optional[UUID] = None
