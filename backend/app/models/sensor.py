import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Enum, ForeignKey, Text
from app.db.base import Base
from app.db.types import UUIDType


class SensorType(str, enum.Enum):
    AIR = "AIR"
    WATER = "WATER"
    WEATHER = "WEATHER"
    MULTI_SENSOR = "MULTI_SENSOR"


class SensorStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    WARNING = "WARNING"


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    sensor_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(SensorType), nullable=False)
    location_id = Column(UUIDType, ForeignKey("locations.id"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(Enum(SensorStatus), default=SensorStatus.ONLINE)
    last_seen = Column(DateTime, nullable=True)
    metadata_ = Column("metadata", Text, nullable=True)  # JSON stored as text
    is_active = Column(String(10), default="true")
    created_at = Column(DateTime, default=datetime.utcnow)
